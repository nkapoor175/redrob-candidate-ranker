"""
Re-ranker + Explanation Generator  ---  OWNER: Jash (Member 2)

Two responsibilities:
  1. Re-rank the top-K shortlist (a smaller, more careful pass).
  2. Generate the 1-2 sentence `reasoning` string each row needs.

CONSTRAINT (submission_spec Section 3): the *ranking step that produces the CSV*
must be offline / CPU-only. So the baseline reasoning generator below is a
template over real profile facts (no network). If the team wants richer LLM
reasoning, do it as a SEPARATE offline pre-compute or a local model — never a
hosted API call inside rank.py.
"""
from __future__ import annotations
from typing import List
from app.schemas import ParsedJD, CandidateFeatures, ScoredCandidate


def build_reasoning(jd: ParsedJD, cand: CandidateFeatures, sc: ScoredCandidate) -> str:
    """Fact-grounded 1-2 sentence justification (Stage-4 review safe).

    Uses ONLY facts present in the candidate record (no hallucination), and
    surfaces an honest concern where one exists.
    """
    matched = [s for s in cand.skills
               if any(r.lower() in s.lower() or s.lower() in r.lower()
                      for r in jd.required_skills)]
    skill_str = ", ".join(matched[:4]) if matched else "adjacent skills only"

    sentence = (f"{cand.current_title or 'Candidate'} with "
                f"{cand.years_of_experience:.1f} yrs; matches on {skill_str}; "
                f"recruiter response rate {cand.recruiter_response_rate:.2f}.")

    concern = ""
    if sc.growth_index < 0.3:
        concern = " Concern: current title is outside the core engineering track."
    elif cand.last_active_days_ago and cand.last_active_days_ago > 60:
        concern = f" Concern: inactive for ~{cand.last_active_days_ago} days."
    elif cand.recruiter_response_rate < 0.2:
        concern = " Concern: low recruiter responsiveness may limit availability."
    return (sentence + concern).strip()


def rerank(jd: ParsedJD,
           shortlist: List[tuple[CandidateFeatures, ScoredCandidate]]
           ) -> List[tuple[CandidateFeatures, ScoredCandidate]]:
    """Offline re-rank pass. Baseline = stable sort by score desc, then
    candidate_id asc to break ties deterministically (spec Section 3).
    Jash can swap in a cross-encoder / local model here.
    """
    return sorted(shortlist, key=lambda x: (-x[1].score, x[0].candidate_id))
