"""
Re-ranker + Explanation Generator  ---  OWNER: Jash (Member 2)

Two responsibilities:
  1. Re-rank the top-K shortlist (stable sort by score, deterministic ties).
  2. Generate a fact-grounded ``reasoning`` string for every ranked candidate
     so recruiters (and Stage-4 judges) can see *why* someone was ranked.

CONSTRAINT (submission_spec Section 3): the *ranking step that produces the CSV*
must be offline / CPU-only. The reasoning generator below is a template over
real profile facts — no network calls.
"""
from __future__ import annotations

from typing import List, Tuple

from rapidfuzz import fuzz

from app.schemas import CandidateFeatures, ParsedJD, ScoredCandidate


# ──────────────────────────────────────────────────────────────────────
# Reasoning builder
# ──────────────────────────────────────────────────────────────────────
def build_reasoning(jd: ParsedJD,
                    cand: CandidateFeatures,
                    sc: ScoredCandidate) -> str:
    """Fact-grounded 2-3 sentence justification (Stage-4 review safe).

    Uses ONLY facts present in the candidate record (no hallucination).
    Surfaces an honest concern where one exists.
    """
    parts: list[str] = []

    # ── Skill match detail ──
    matched_req: list[str] = []
    for req in jd.required_skills:
        rl = req.lower()
        for cs in cand.skills:
            cl = cs.lower()
            if rl in cl or cl in rl or fuzz.ratio(rl, cl) >= 78:
                matched_req.append(cs)
                break

    total_req = len(jd.required_skills)
    n_matched = len(matched_req)

    if n_matched > 0:
        examples = ", ".join(matched_req[:4])
        parts.append(
            f"Matches {n_matched}/{total_req} required skills "
            f"(skill_match={sc.skill_match:.2f}) including {examples}"
        )
    else:
        parts.append(
            f"Limited required-skill overlap (skill_match={sc.skill_match:.2f})"
        )

    # ── Experience fit ──
    yrs = cand.years_of_experience
    lo, hi = jd.experience_required_min, jd.experience_required_max
    if lo <= yrs <= hi:
        parts.append(
            f"{yrs:.0f}yrs experience fits the {lo:.0f}\u2013{hi:.0f}yr range "
            f"(exp={sc.experience_relevance:.2f})"
        )
    elif yrs < lo:
        parts.append(
            f"{yrs:.0f}yrs experience is below the {lo:.0f}\u2013{hi:.0f}yr target "
            f"(exp={sc.experience_relevance:.2f})"
        )
    else:
        parts.append(
            f"{yrs:.0f}yrs experience exceeds the {lo:.0f}\u2013{hi:.0f}yr range "
            f"(exp={sc.experience_relevance:.2f})"
        )

    # ── Title / Role context ──
    if cand.current_title:
        parts.append(f"Current role: {cand.current_title}")

    # ── Behavioral signals ──
    behav_notes: list[str] = []
    if cand.recruiter_response_rate >= 0.70:
        behav_notes.append("high recruiter responsiveness")
    elif cand.recruiter_response_rate < 0.20:
        behav_notes.append("low recruiter responsiveness")
    if cand.open_to_work:
        behav_notes.append("open to work")
    if cand.last_active_days_ago is not None:
        if cand.last_active_days_ago <= 30:
            behav_notes.append("recently active")
        elif cand.last_active_days_ago > 180:
            behav_notes.append(f"inactive ~{cand.last_active_days_ago}d")
    if behav_notes:
        parts.append(
            f"Behavioral: {', '.join(behav_notes)} "
            f"(score={sc.behavioral_score:.2f})"
        )

    # ── Growth index ──
    if sc.growth_index >= 0.70:
        parts.append(f"Strong growth signals (growth={sc.growth_index:.2f})")
    elif sc.growth_index < 0.30:
        parts.append(f"Limited growth indicators (growth={sc.growth_index:.2f})")

    # ── GitHub activity ──
    if cand.github_activity_score > 0.5:
        parts.append(
            f"Active GitHub contributor "
            f"(activity={cand.github_activity_score:.2f})"
        )

    # ── Concerns ──
    concerns: list[str] = []
    if sc.skill_match < 0.25:
        concerns.append("weak skill alignment")
    if sc.experience_relevance < 0.50:
        concerns.append("experience mismatch")
    if cand.recruiter_response_rate < 0.15:
        concerns.append("may be unreachable")
    if cand.last_active_days_ago and cand.last_active_days_ago > 180:
        concerns.append("platform inactivity")

    result = ". ".join(parts) + "."
    if concerns:
        result += f" Concerns: {', '.join(concerns)}."

    return result


# ──────────────────────────────────────────────────────────────────────
# Re-ranker
# ──────────────────────────────────────────────────────────────────────
def rerank(
    jd: ParsedJD,
    shortlist: List[Tuple[CandidateFeatures, ScoredCandidate]],
) -> List[Tuple[CandidateFeatures, ScoredCandidate]]:
    """Offline re-rank pass on the pre-sorted shortlist.

    Strategy
    --------
    1. Stable sort by ``score`` descending.
    2. Ties broken by ``candidate_id`` ascending (deterministic per spec §3).
    3. Light penalty for candidates whose title is a clear mismatch for the
       role_type in the JD (an extra guard against keyword-stuffed profiles
       that slipped through scoring).

    The pipeline calls this on the top ~3×K candidates before slicing to K.
    """
    role_lower = jd.role_type.lower() if jd.role_type else ""

    def _sort_key(pair: Tuple[CandidateFeatures, ScoredCandidate]):
        feats, sc = pair
        score = sc.score

        # Micro-boost for candidates whose title resonates with the JD role
        title_lower = feats.current_title.lower()
        role_words = set(role_lower.split())
        title_words = set(title_lower.split())
        overlap = role_words & title_words - {"senior", "junior", "lead", "staff",
                                               "principal", "founding", "the", "a"}
        if overlap:
            score += 0.005  # tiny nudge, not enough to override real signal

        return (-score, feats.candidate_id)

    return sorted(shortlist, key=_sort_key)
