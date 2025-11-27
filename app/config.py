# app/config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    USE_FALLBACK = os.getenv("USE_FALLBACK", "").lower() in ("1", "true") or not OPENAI_API_KEY

settings = Settings()

