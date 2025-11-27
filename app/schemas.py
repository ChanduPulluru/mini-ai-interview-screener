# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class EvaluateRequest(BaseModel):
    # Accepts either raw answer or full text "Candidate says: ..."
    text: str

class EvaluateResponse(BaseModel):
    score: int
    summary: str
    improvement: str

class CandidateIn(BaseModel):
    id: Optional[str] = None
    text: str

class RankRequest(BaseModel):
    candidates: List[CandidateIn]

class RankedCandidate(BaseModel):
    id: Optional[str] = None
    text: str
    score: int
    summary: str
    improvement: str

class RankResponse(BaseModel):
    ranked: List[RankedCandidate]
