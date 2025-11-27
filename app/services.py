# app/services.py
import os
import re
import json
import asyncio
from typing import Dict, Any
import httpx
from .config import settings

# Minimal prompt to force JSON-only output
EVAL_PROMPT = """
You are an expert hiring screener. Evaluate the candidate's short answer and RETURN STRICT JSON (no extra commentary).
Output EXACTLY three fields:
- score: integer 1-5 (5 best)
- summary: one-line concise summary (<= 20 words)
- improvement: one short suggestion (<= 25 words)

Candidate says:
\"\"\"{answer}\"\"\"

Use these heuristics:
5: Correct, complete, concise, shows depth or example.
4: Mostly correct, minor missing detail.
3: Partially correct or incomplete.
2: Poor, big gaps.
1: Incorrect/irrelevant.

Return JSON only.
"""

# -------------------------
# Fallback heuristic (works without API key)
# -------------------------
KEY_TERMS = [
    "design", "trade-off", "complexity", "edge", "optimize", "test",
    "security", "performance", "scalability", "consistency", "retry", "idempotent"
]

def fallback_score_and_text(answer: str) -> Dict[str, Any]:
    text = (answer or "").strip()
    if not text:
        return {"score": 1, "summary": "No answer provided.", "improvement": "Provide an answer with key ideas."}
    words = text.split()
    length = len(words)
    keywords = sum(1 for k in KEY_TERMS if re.search(r"\b" + re.escape(k) + r"\b", text, flags=re.I))

    if length >= 80 and keywords >= 2:
        score = 5
    elif length >= 50 and keywords >= 1:
        score = 4
    elif length >= 25:
        score = 3
    elif length >= 10:
        score = 2
    else:
        score = 1

    # summary = first sentence (≤ 20 words)
    first_sentence = re.split(r'(?<=[.!?])\s+', text, maxsplit=1)[0]
    s_words = first_sentence.split()
    summary = " ".join(s_words[:20]) + ("..." if len(s_words) > 20 else "")
    improvement = "Be more specific and mention trade-offs or testing." if score < 4 else "Add a concrete example or metrics."

    return {"score": score, "summary": summary, "improvement": improvement}

# -------------------------
# Helper: call OpenAI chat completions (via REST)
# -------------------------
async def call_openai_chat(prompt: str) -> str:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured")
    url = f"{settings.OPENAI_API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 300,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        # support typical structure: choices[0].message.content
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            # some models may return message.content or text
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
            if "text" in choice:
                return choice["text"]
        # fallback to raw string
        return json.dumps(data)

# -------------------------
# Robust JSON parsing from model output
# -------------------------
def parse_model_json(raw: str) -> Dict[str, Any]:
    """
    Extract the first {...} JSON block and parse.
    Raises ValueError on bad parse.
    """
    if not raw:
        raise ValueError("empty model output")
    # find first JSON object
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("no JSON object found in model output")
    candidate = raw[start:end+1]
    parsed = json.loads(candidate)
    # basic normalization & validation
    score = int(parsed.get("score", 1))
    score = max(1, min(5, score))
    summary = str(parsed.get("summary", "")).strip()
    improvement = str(parsed.get("improvement", "")).strip()
    if not summary:
        summary = ""
    if not improvement:
        improvement = ""
    return {"score": score, "summary": summary, "improvement": improvement}

# -------------------------
# Public evaluate function
# -------------------------
async def evaluate_text(answer: str) -> Dict[str, Any]:
    """
    Evaluate text using LLM if configured, otherwise fallback heuristic.
    Returns dict with keys: score, summary, improvement
    """
    # normalize "Candidate says: ..." prefix
    txt = (answer or "").strip()
    if txt.lower().startswith("candidate says:"):
        txt = txt.split(":", 1)[1].strip()

    if settings.USE_FALLBACK:
        return fallback_score_and_text(txt)

    prompt = EVAL_PROMPT.format(answer=txt)
    try:
        raw = await call_openai_chat(prompt)
        try:
            parsed = parse_model_json(raw)
            return parsed
        except Exception:
            # sometimes models add surrounding text — try to find JSON anywhere
            # last resort: fallback heuristic
            return fallback_score_and_text(txt)
    except Exception:
        # any HTTP/timeout error -> fallback
        return fallback_score_and_text(txt)

# -------------------------
# Bulk evaluation helper (concurrent)
# -------------------------
async def evaluate_bulk(items):
    # items: list of (id, text)
    tasks = [evaluate_text(text) for (_id, text) in items]
    results = await asyncio.gather(*tasks)
    # return list of dicts in same order
    return results
