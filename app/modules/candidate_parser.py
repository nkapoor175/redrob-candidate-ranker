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


# Lazy load precomputed embeddings
_EMBEDDINGS_CACHE: dict[str, list[float]] = {}
_EMBEDDINGS_LOADED = False


def _load_precomputed_embeddings() -> None:
    global _EMBEDDINGS_CACHE, _EMBEDDINGS_LOADED
    if _EMBEDDINGS_LOADED:
        return
    import numpy as np
    from pathlib import Path
    npz_path = Path(__file__).resolve().parent.parent.parent / "data" / "candidate_embeddings.npz"
    if npz_path.exists():
        try:
            data = np.load(npz_path, allow_pickle=True)
            ids = data["ids"]
            embs = data["embeddings"]
            # Dequantize from int8 to float32
            dequantized = embs.astype(np.float32) / 127.0
            _EMBEDDINGS_CACHE = {str(i): e.tolist() for i, e in zip(ids, dequantized)}
        except Exception:
            pass
    _EMBEDDINGS_LOADED = True


def _days_since(date_str: str) -> int | None:
    if not date_str:
        return None

    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (date.today() - d).days
    except Exception:
        return None


def _build_candidate_text(
    profile: dict,
    skills: list[str],
    career_text: str,
    education_text: str,
    cert_text: str,
) -> str:
    return f"""
Headline:
{profile.get("headline", "")}

Summary:
{profile.get("summary", "")}

Current Title:
{profile.get("current_title", "")}

Skills:
{' '.join(skills)}

Education:
{education_text}

Career History:
{career_text}

Certifications:
{cert_text}
"""


def build_text_for_embedding(record: dict) -> str:
    """Public helper to construct the same candidate text representation used in precomputation."""
    profile = record.get("profile", {})
    skills = [
        s.get("name", "")
        for s in record.get("skills", [])
        if s.get("name")
    ]
    career_text = " ".join(
        job.get("description", "")
        for job in record.get("career_history", [])
    )
    education_text = " ".join(
        f"{e.get('degree', '')} {e.get('field_of_study', '')}"
        for e in record.get("education", [])
    )
    cert_text = " ".join(
        cert.get("name", "")
        for cert in record.get("certifications", [])
    )
    return _build_candidate_text(
        profile=profile,
        skills=skills,
        career_text=career_text,
        education_text=education_text,
        cert_text=cert_text,
    )


def parse_candidate(record: dict) -> CandidateFeatures:
    """
    Normalize one raw candidate record into CandidateFeatures.

    Enhanced version:
    - Extracts skills
    - Includes career descriptions
    - Includes education
    - Includes certifications
    - Looks up precomputed semantic embedding from disk
    """

    profile = record.get("profile", {})
    signals = record.get("redrob_signals", {})

    skills = [
        s.get("name", "")
        for s in record.get("skills", [])
        if s.get("name")
    ]

    _load_precomputed_embeddings()
    candidate_id = record.get("candidate_id", "")
    embedding = _EMBEDDINGS_CACHE.get(candidate_id, [])

    return CandidateFeatures(
        candidate_id=candidate_id,
        name=profile.get("anonymized_name", ""),
        current_title=profile.get("current_title", ""),
        years_of_experience=float(
            profile.get("years_of_experience", 0) or 0
        ),
        skills=skills,
        summary=profile.get("summary", ""),
        recruiter_response_rate=float(
            signals.get("recruiter_response_rate", 0) or 0
        ),
        last_active_days_ago=_days_since(
            signals.get("last_active_date", "")
        ),
        open_to_work=bool(
            signals.get("open_to_work_flag", False)
        ),
        github_activity_score=float(
            signals.get("github_activity_score", -1) or -1
        ),
        embedding=embedding,
        raw=record,
    )