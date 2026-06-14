"""
Common data formats (Pydantic models) shared across all modules.

OWNER: Navika (Backend & Integration Lead)

These models are the *contract* between teammates' modules. Everyone codes
to these shapes so data flows cleanly through the pipeline:

    JD        -> ParsedJD        (Jash's JD parser produces this)
    candidate -> CandidateFeatures (Parthvi's parser/embedder produces this)
    (ParsedJD + CandidateFeatures) -> ScoredCandidate (Jash's scoring engine)
    top-K ScoredCandidate -> RankedCandidate (final output -> CSV / dashboard)
"""
from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


# ---------- Job Description ----------
class ParsedJD(BaseModel):
    """Output of the JD Parser (Jash)."""
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_required_min: float = 0
    experience_required_max: float = 99
    role_type: str = ""
    # free-form notes the LLM extracted (disqualifiers, "what we mean", etc.)
    notes: str = ""


# ---------- Candidate ----------
class CandidateFeatures(BaseModel):
    """
    Normalized candidate representation produced by the Candidate Parser
    + Feature/Embedding modules (Parthvi). Keeps only what the scorer needs.
    """
    candidate_id: str
    name: str = ""
    current_title: str = ""
    years_of_experience: float = 0
    skills: List[str] = Field(default_factory=list)
    summary: str = ""
    # behavioral signals (subset of redrob_signals used in scoring)
    recruiter_response_rate: float = 0
    last_active_days_ago: Optional[int] = None
    open_to_work: bool = False
    github_activity_score: float = -1
    # optional embedding vector (Parthvi)
    embedding: List[float] = Field(default_factory=list)
    # keep the raw record around for reasoning / inspection
    raw: Dict = Field(default_factory=dict)


# ---------- Scoring ----------
class ScoredCandidate(BaseModel):
    """Output of the Scoring Engine (Jash) before final ranking."""
    candidate_id: str
    score: float
    skill_match: float = 0
    experience_relevance: float = 0
    growth_index: float = 0
    behavioral_score: float = 0


# ---------- Final ranking output (-> CSV & dashboard) ----------
class RankedCandidate(BaseModel):
    candidate_id: str
    rank: int
    score: float
    reasoning: str = ""


class RankResponse(BaseModel):
    job_title: str = ""
    total_candidates: int = 0
    results: List[RankedCandidate] = Field(default_factory=list)
