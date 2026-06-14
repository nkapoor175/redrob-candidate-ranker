"""
Candidate Parser / Feature Extraction  ---  OWNER: Parthvi (Member 1)

Navika provides this STUB + baseline that turns a raw candidate record (the
redrob schema in candidates.jsonl) into a normalized CandidateFeatures object.
Parthvi replaces the body with the real parser + embedding generation.
Keep the signature and return type (CandidateFeatures) stable.
"""
from __future__ import annotations
from datetime import date, datetime
from app.schemas import CandidateFeatures


def _days_since(date_str: str) -> int | None:
    if not date_str:
        return None
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (date.today() - d).days
    except Exception:
        return None


def parse_candidate(record: dict) -> CandidateFeatures:
    """Normalize one raw candidate record into CandidateFeatures.

    Baseline: pull the fields the scorer needs out of the redrob schema.
    Parthvi adds: real skill extraction, project parsing, and `embedding`.
    """
    profile = record.get("profile", {})
    signals = record.get("redrob_signals", {})
    skills = [s.get("name", "") for s in record.get("skills", []) if s.get("name")]

    return CandidateFeatures(
        candidate_id=record.get("candidate_id", ""),
        name=profile.get("anonymized_name", ""),
        current_title=profile.get("current_title", ""),
        years_of_experience=float(profile.get("years_of_experience", 0) or 0),
        skills=skills,
        summary=profile.get("summary", ""),
        recruiter_response_rate=float(signals.get("recruiter_response_rate", 0) or 0),
        last_active_days_ago=_days_since(signals.get("last_active_date", "")),
        open_to_work=bool(signals.get("open_to_work_flag", False)),
        github_activity_score=float(signals.get("github_activity_score", -1) or -1),
        embedding=[],  # Parthvi fills this in
        raw=record,
    )
