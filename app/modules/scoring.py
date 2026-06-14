"""
Scoring Engine + Hybrid Ranking  ---  OWNER: Jash (Member 2)

Navika provides a transparent, offline, CPU-only baseline scorer so the whole
pipeline produces a valid submission today. Jash replaces `score_candidate`
with the real hybrid model (embeddings similarity + learning-to-rank, etc.).

IMPORTANT (submission_spec Section 3): the ranking step must run offline,
CPU-only, <=5 min, <=16 GB. No hosted LLM calls here.
"""
from __future__ import annotations
from app.schemas import ParsedJD, CandidateFeatures, ScoredCandidate

# Title signals from the JD: product-ML / engineering titles are a fit;
# the JD explicitly warns that a great skill list under a non-eng title is NOT.
_FIT_TITLE_HINTS = ["ai engineer", "ml engineer", "machine learning", "data scientist",
                    "software", "backend", "search", "nlp", "research engineer"]
_WEAK_TITLE_HINTS = ["marketing", "sales", "hr", "accountant", "graphic", "content",
                     "civil", "mechanical", "operations", "customer support", "project manager"]


def _skill_match(jd: ParsedJD, cand: CandidateFeatures) -> float:
    cand_skills = {s.lower() for s in cand.skills}
    req = [s.lower() for s in jd.required_skills]
    pref = [s.lower() for s in jd.preferred_skills]
    if not req:
        return 0.0
    req_hit = sum(any(r in cs or cs in r for cs in cand_skills) for r in req) / len(req)
    pref_hit = (sum(any(p in cs or cs in p for cs in cand_skills) for p in pref) / len(pref)
                if pref else 0.0)
    return 0.75 * req_hit + 0.25 * pref_hit


def _experience_relevance(jd: ParsedJD, cand: CandidateFeatures) -> float:
    yrs = cand.years_of_experience
    lo, hi = jd.experience_required_min, jd.experience_required_max
    if lo <= yrs <= hi:
        return 1.0
    # soft falloff outside the band
    dist = (lo - yrs) if yrs < lo else (yrs - hi)
    return max(0.0, 1.0 - 0.15 * dist)


def _title_fit(cand: CandidateFeatures) -> float:
    t = cand.current_title.lower()
    if any(h in t for h in _FIT_TITLE_HINTS):
        return 1.0
    if any(h in t for h in _WEAK_TITLE_HINTS):
        return 0.15
    return 0.5


def _behavioral(cand: CandidateFeatures) -> float:
    """Availability multiplier: responsive + recently active + open-to-work."""
    resp = cand.recruiter_response_rate
    active = 1.0
    if cand.last_active_days_ago is not None:
        active = 1.0 if cand.last_active_days_ago <= 30 else max(0.3, 1 - cand.last_active_days_ago / 365)
    otw = 1.0 if cand.open_to_work else 0.7
    return max(0.0, min(1.0, 0.5 * resp + 0.3 * active + 0.2 * otw))


def score_candidate(jd: ParsedJD, cand: CandidateFeatures) -> ScoredCandidate:
    skill = _skill_match(jd, cand)
    exp = _experience_relevance(jd, cand)
    title = _title_fit(cand)
    behav = _behavioral(cand)

    # Hybrid weights. Title fit gates skill match so keyword-stuffed
    # non-engineers don't float to the top (a documented trap).
    base = 0.45 * (skill * title) + 0.20 * exp + 0.15 * title
    final = base * (0.6 + 0.4 * behav)  # behavioral acts as a modifier

    return ScoredCandidate(
        candidate_id=cand.candidate_id,
        score=round(final, 6),
        skill_match=round(skill, 4),
        experience_relevance=round(exp, 4),
        growth_index=round(title, 4),
        behavioral_score=round(behav, 4),
    )
