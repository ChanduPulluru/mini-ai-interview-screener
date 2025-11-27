# app/main.py
import asyncio
from fastapi import FastAPI, HTTPException
from typing import List
from .schemas import (
    EvaluateRequest, EvaluateResponse,
    CandidateIn, RankRequest, RankResponse, RankedCandidate
)
from .services import evaluate_text, evaluate_bulk
from .config import settings

app = FastAPI(title="Mini AI Interview Screener (backend)")

@app.get("/")
async def root():
    return {"ok": True, "provider": "fallback" if settings.USE_FALLBACK else "openai"}

@app.post("/evaluate-answer", response_model=EvaluateResponse)
async def evaluate_answer(req: EvaluateRequest):
    """
    Accepts text input. Example:
      {"text": "Candidate says: I would shard the DB and use queues ..."}
    Returns JSON:
      {"score":1-5, "summary":"...", "improvement":"..."}
    """
    result = await evaluate_text(req.text)
    return EvaluateResponse(**result)

@app.post("/rank-candidates", response_model=RankResponse)
async def rank_candidates(req: RankRequest):
    """
    Input:
    {
      "candidates": [
        {"id": "c1", "text": "Candidate says: ..."},
        {"id": "c2", "text": "Candidate says: ..."}
      ]
    }
    Output: ranked list (highest score first)
    """
    if not req.candidates:
        raise HTTPException(status_code=400, detail="No candidates provided")

    # Prepare items preserving id and original text
    items = [(c.id, c.text) for c in req.candidates]

    # Evaluate concurrently
    results = await evaluate_bulk(items)  # list of dicts corresponding to items

    # Build ranked candidates
    ranked_objs = []
    for (item, res) in zip(items, results):
        cid, text = item
        ranked_objs.append(RankedCandidate(
            id=cid,
            text=text,
            score=int(res["score"]),
            summary=res["summary"],
            improvement=res["improvement"]
        ))

    # Sort by score desc, tie-breaker by longer summary (arbitrary)
    ranked_sorted = sorted(ranked_objs, key=lambda x: (-x.score, -len(x.summary)))

    return RankResponse(ranked=ranked_sorted)
