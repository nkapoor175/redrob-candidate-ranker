"""
JD Parser  ---  OWNER: Jash (Member 2)

Navika provides this STUB interface + a simple offline baseline so the pipeline
runs end to end today. Jash replaces the body of `parse_jd` with the real
LLM-based extraction. Keep the function signature and return type (ParsedJD)
the same so nothing downstream breaks.
"""
from __future__ import annotations
import re
from app.schemas import ParsedJD

# Baseline keyword lists derived from the released JD. Jash will replace this
# with LLM extraction; the integration layer doesn't care how it's produced.
_REQUIRED = [
    "embeddings", "retrieval", "vector database", "hybrid search", "python",
    "ranking", "evaluation", "ndcg", "mrr", "map",
]
_PREFERRED = [
    "llm fine-tuning", "lora", "qlora", "peft", "learning-to-rank",
    "xgboost", "hr-tech", "distributed systems", "open-source",
]


def parse_jd(jd_text: str) -> ParsedJD:
    """Parse raw JD text into structured requirements.

    Baseline implementation: keyword presence + a regex for the experience band.
    Replace with LLM extraction (Jash).
    """
    lower = jd_text.lower()
    exp_min, exp_max = 5, 9
    m = re.search(r"(\d+)\s*[-–to]+\s*(\d+)\s*year", lower)
    if m:
        exp_min, exp_max = float(m.group(1)), float(m.group(2))

    required = [s for s in _REQUIRED if s in lower] or _REQUIRED
    preferred = [s for s in _PREFERRED if s in lower] or _PREFERRED

    return ParsedJD(
        required_skills=required,
        preferred_skills=preferred,
        experience_required_min=exp_min,
        experience_required_max=exp_max,
        role_type="Senior AI Engineer",
        notes=("Down-weight pure-research, consulting-only, and inactive "
               "candidates. Keyword stuffers and honeypots are traps."),
    )
