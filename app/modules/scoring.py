"""
Scoring Engine + Hybrid Ranking  ---  OWNER: Jash (Member 2)

Produces a ``ScoredCandidate`` for every (ParsedJD, CandidateFeatures) pair.

Sub-scores
----------
* **skill_match** (weight 0.40)  — rapidfuzz fuzzy matching of candidate
  skills vs required/preferred JD skills.
* **experience_relevance** (weight 0.25) — Gaussian-ish curve centred on the
  JD experience band with soft falloff outside it.
* **growth_index** (weight 0.20) — career trajectory signals: GitHub activity,
  certifications, projects, experience breadth, education level.
* **behavioral_score** (weight 0.15) — platform engagement: recruiter response
  rate, recency of activity, open-to-work flag.

A **title-fit gate** prevents keyword-stuffed non-engineer profiles from
floating to the top (the JD explicitly warns about this trap).

Optionally blends in **semantic similarity** (sentence-transformers
``all-MiniLM-L6-v2``) when candidate embeddings are available.  The JD
embedding is computed once and cached at module level.

Runs entirely offline on CPU — no API calls.

IMPORTANT (submission_spec Section 3): the ranking step must run offline,
CPU-only, <=5 min, <=16 GB. No hosted LLM calls here.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
from rapidfuzz import fuzz

from app.schemas import CandidateFeatures, ParsedJD, ScoredCandidate

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────
# Weights
# ──────────────────────────────────────────────────────────────────────
W_SKILL = 0.40
W_EXP   = 0.25
W_GROW  = 0.20
W_BEHAV = 0.15

# Blend ratio when semantic embeddings are available
SEMANTIC_BLEND = 0.35  # final = (1-α)*weighted + α*cos_sim

# ──────────────────────────────────────────────────────────────────────
# Title-fit hints (gate keyword-stuffed profiles per JD warning)
# ──────────────────────────────────────────────────────────────────────
_FIT_TITLE_HINTS = [
    "ai engineer", "ml engineer", "machine learning", "data scientist",
    "software", "backend", "search", "nlp", "research engineer",
    "data engineer", "platform engineer", "full stack", "devops",
    "deep learning", "applied scientist", "sde", "developer",
]
_WEAK_TITLE_HINTS = [
    "marketing", "sales", "hr ", "human resource", "accountant", "graphic",
    "content", "civil", "mechanical", "operations", "customer support",
    "project manager", "business analyst", "recruiter", "admin",
]

# ──────────────────────────────────────────────────────────────────────
# Module-level caches  (computed once, reused for all 100 K candidates)
# ──────────────────────────────────────────────────────────────────────
_jd_skill_cache: Dict[int, dict] = {}       # id(jd) → normalised skill lists
_jd_embedding_cache: Dict[int, object] = {}  # id → np.ndarray | None
_st_model: object = None                     # SentenceTransformer (lazy)
_st_model_loaded: bool = False


def _get_st_model():
    """Lazily load the SentenceTransformer model (only when embeddings exist)."""
    global _st_model, _st_model_loaded
    if _st_model_loaded:
        return _st_model
    try:
        from sentence_transformers import SentenceTransformer
        _st_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Loaded sentence-transformers model all-MiniLM-L6-v2")
    except Exception as exc:                     # noqa: BLE001
        logger.warning("sentence-transformers unavailable (%s); "
                       "semantic scoring disabled.", exc)
        _st_model = None
    _st_model_loaded = True
    return _st_model


def _normalise_skills(jd: ParsedJD) -> dict:
    """Cache-friendly normalisation of JD skill lists."""
    key = id(jd)
    if key in _jd_skill_cache:
        return _jd_skill_cache[key]
    data = {
        "required": [s.lower().strip() for s in jd.required_skills if s.strip()],
        "preferred": [s.lower().strip() for s in jd.preferred_skills if s.strip()],
    }
    _jd_skill_cache[key] = data
    return data


def _ensure_jd_embedding(jd: ParsedJD) -> Optional[np.ndarray]:
    """Compute (and cache) a dense embedding for the parsed JD."""
    key = id(jd)
    if key in _jd_embedding_cache:
        return _jd_embedding_cache[key]

    model = _get_st_model()
    if model is None:
        _jd_embedding_cache[key] = None
        return None

    # Build a concise text representation of the JD
    jd_text = (
        f"{jd.role_type}. "
        f"Required skills: {', '.join(jd.required_skills)}. "
        f"Preferred skills: {', '.join(jd.preferred_skills)}. "
        f"Experience: {jd.experience_required_min}-"
        f"{jd.experience_required_max} years. "
        f"{jd.notes}"
    )
    emb = model.encode(jd_text, normalize_embeddings=True)
    arr = np.asarray(emb, dtype=np.float32)
    _jd_embedding_cache[key] = arr
    return arr


# ──────────────────────────────────────────────────────────────────────
# Sub-score functions
# ──────────────────────────────────────────────────────────────────────
def _skill_match(jd: ParsedJD, cand: CandidateFeatures) -> float:
    """Fuzzy-match candidate skills against JD required + preferred lists.

    Uses rapidfuzz so "ReactJS" ≈ "React.js", "scikit-learn" ≈ "sklearn", etc.
    Formula: 0.70 × (req_matched / req_total) + 0.30 × (pref_matched / pref_total)
    """
    norm = _normalise_skills(jd)
    req_skills = norm["required"]
    pref_skills = norm["preferred"]
    cand_skills = [s.lower().strip() for s in cand.skills if s.strip()]

    if not req_skills and not pref_skills:
        return 0.0

    def _count(jd_list: List[str]) -> Tuple[int, int]:
        if not jd_list:
            return 0, 0
        hits = 0
        for jsk in jd_list:
            for cs in cand_skills:
                # fast substring check
                if jsk in cs or cs in jsk:
                    hits += 1
                    break
                # fuzzy check
                if fuzz.ratio(jsk, cs) >= 78 or fuzz.partial_ratio(jsk, cs) >= 85:
                    hits += 1
                    break
        return hits, len(jd_list)

    req_hit, req_tot = _count(req_skills)
    pref_hit, pref_tot = _count(pref_skills)

    req_score  = (req_hit  / req_tot)  if req_tot  else 0.0
    pref_score = (pref_hit / pref_tot) if pref_tot else 0.0

    return 0.70 * req_score + 0.30 * pref_score


def _experience_relevance(jd: ParsedJD, cand: CandidateFeatures) -> float:
    """Score how well candidate experience fits the JD band.

    Within range → near 1.0 (slight boost for mid-range).
    Under → linear decay (0.20 per year below).
    Over  → gentle decay (0.08 per year above — overqualified is ok-ish).
    """
    yrs = cand.years_of_experience
    lo  = jd.experience_required_min
    hi  = jd.experience_required_max

    if lo <= yrs <= hi:
        # Slight bonus for centred candidates
        mid = (lo + hi) / 2.0
        half = max((hi - lo) / 2.0, 1.0)
        return 0.92 + 0.08 * (1.0 - abs(yrs - mid) / half)

    if yrs < lo:
        deficit = lo - yrs
        return max(0.0, 1.0 - 0.20 * deficit)

    # over-experienced
    excess = yrs - hi
    return max(0.30, 1.0 - 0.08 * excess)


def _title_fit(cand: CandidateFeatures) -> float:
    """Gate score: engineering titles → 1.0; clearly non-eng titles → low."""
    t = cand.current_title.lower()
    if any(h in t for h in _FIT_TITLE_HINTS):
        return 1.0
    if any(h in t for h in _WEAK_TITLE_HINTS):
        return 0.15
    return 0.50  # ambiguous title


def _growth_index(cand: CandidateFeatures) -> float:
    """Career trajectory / growth signals derived from raw candidate data.

    Checks: GitHub activity, certifications, projects, experience breadth,
    education level, and any explicit growth fields in the raw record.
    """
    signals: list[float] = []
    raw = cand.raw

    # GitHub activity (field on CandidateFeatures)
    if cand.github_activity_score >= 0:
        signals.append(min(1.0, cand.github_activity_score))

    # Explicit growth fields that may be present in the raw record
    for key in ("career_progression", "activity_score", "growth_score"):
        if key in raw:
            try:
                signals.append(min(1.0, max(0.0, float(raw[key]))))
            except (TypeError, ValueError):
                pass

    # Experience breadth (more positions → more growth, capped at 5)
    experience = raw.get("experience", [])
    if isinstance(experience, list) and experience:
        signals.append(min(1.0, len(experience) / 5.0))

    # Certifications
    certs = raw.get("certifications", [])
    if isinstance(certs, list) and certs:
        signals.append(min(1.0, len(certs) / 3.0))

    # Side projects / open-source
    projects = raw.get("projects", [])
    if isinstance(projects, list) and projects:
        signals.append(min(1.0, len(projects) / 3.0))

    # Education level
    education = raw.get("education", [])
    if isinstance(education, list):
        best_edu = 0.0
        for edu in education:
            if isinstance(edu, dict):
                deg = str(edu.get("degree", "")).lower()
                if "phd" in deg or "doctorate" in deg:
                    best_edu = max(best_edu, 0.9)
                elif any(k in deg for k in ("master", "m.s.", "m.tech", "mba", "m.e.")):
                    best_edu = max(best_edu, 0.7)
                elif any(k in deg for k in ("bachelor", "b.tech", "b.s.", "b.e.", "b.sc")):
                    best_edu = max(best_edu, 0.5)
        if best_edu > 0:
            signals.append(best_edu)

    # Skills count as a proxy for breadth (cap at 15 for full score)
    if cand.skills:
        signals.append(min(1.0, len(cand.skills) / 15.0))

    return (sum(signals) / len(signals)) if signals else 0.50


def _behavioral_score(cand: CandidateFeatures) -> float:
    """Platform engagement: responsiveness, recency, open-to-work."""
    parts: list[float] = []

    # Recruiter response rate (0-1 already)
    parts.append(cand.recruiter_response_rate)

    # Recency of platform activity
    if cand.last_active_days_ago is not None:
        if cand.last_active_days_ago <= 7:
            parts.append(1.0)
        elif cand.last_active_days_ago <= 30:
            parts.append(0.90)
        elif cand.last_active_days_ago <= 90:
            parts.append(0.70)
        elif cand.last_active_days_ago <= 180:
            parts.append(0.40)
        else:
            parts.append(max(0.10, 1.0 - cand.last_active_days_ago / 365.0))
    else:
        parts.append(0.50)  # unknown → neutral

    # Open-to-work flag
    parts.append(1.0 if cand.open_to_work else 0.60)

    return sum(parts) / len(parts) if parts else 0.50


def _cosine_similarity(a: np.ndarray, b) -> float:
    """Cosine similarity between two vectors, safe for zero-length/zero-norm."""
    b_arr = np.asarray(b, dtype=np.float32)
    if a.shape != b_arr.shape:
        return 0.0
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b_arr)
    if norm_a < 1e-9 or norm_b < 1e-9:
        return 0.0
    return float(np.dot(a, b_arr) / (norm_a * norm_b))


# ──────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────
def score_candidate(jd: ParsedJD, cand: CandidateFeatures) -> ScoredCandidate:
    """Score a single candidate against a parsed JD.

    Returns a ``ScoredCandidate`` with four sub-scores and a blended final
    score.  When the candidate carries a pre-computed embedding, semantic
    cosine similarity with the JD is blended in.

    The JD embedding is computed exactly once and cached at module level so
    it is **not** re-computed per candidate.
    """
    skill = _skill_match(jd, cand)
    exp   = _experience_relevance(jd, cand)
    growth = _growth_index(cand)
    behav = _behavioral_score(cand)
    title = _title_fit(cand)

    # Weighted combination of the four sub-scores
    weighted = (W_SKILL * skill
                + W_EXP * exp
                + W_GROW * growth
                + W_BEHAV * behav)

    # Title-fit gate: scales the weighted score down for non-eng titles
    # so keyword-stuffed profiles from non-engineering roles don't rank high.
    weighted = weighted * (0.50 + 0.50 * title)

    # ── Semantic similarity (only when candidate embedding is available) ──
    cand_emb = cand.embedding
    if cand_emb and len(cand_emb) > 0:
        jd_emb = _ensure_jd_embedding(jd)
        if jd_emb is not None:
            cos_sim = _cosine_similarity(jd_emb, cand_emb)
            cos_norm = (cos_sim + 1.0) / 2.0  # map [-1,1] → [0,1]
            final = (1.0 - SEMANTIC_BLEND) * weighted + SEMANTIC_BLEND * cos_norm
        else:
            final = weighted
    else:
        final = weighted

    final = max(0.0, min(1.0, final))

    return ScoredCandidate(
        candidate_id=cand.candidate_id,
        score=round(final, 6),
        skill_match=round(skill, 4),
        experience_relevance=round(exp, 4),
        growth_index=round(growth, 4),
        behavioral_score=round(behav, 4),
    )
