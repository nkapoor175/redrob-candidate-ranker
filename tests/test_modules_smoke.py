"""Quick smoke test for the three Jash modules (no candidates.jsonl needed)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
from app.modules.jd_parser import parse_jd
from app.modules.scoring import score_candidate
from app.modules.reranker import rerank, build_reasoning
from app.schemas import CandidateFeatures, ParsedJD

# ── 1. JD Parser ──
jd_path = Path(__file__).resolve().parent.parent / "data" / "job_description.md"
jd_text = jd_path.read_text(encoding="utf-8")
parsed = parse_jd(jd_text)

print("=" * 60)
print("PARSED JD")
print("=" * 60)
print(f"  role_type           : {parsed.role_type}")
print(f"  experience_range    : {parsed.experience_required_min}-{parsed.experience_required_max}")
print(f"  required_skills ({len(parsed.required_skills):2d}) : {parsed.required_skills[:8]}...")
print(f"  preferred_skills({len(parsed.preferred_skills):2d}) : {parsed.preferred_skills[:6]}...")
print(f"  notes               : {parsed.notes[:120]}...")
print()

# ── 2. Scoring (synthetic candidates) ──
good_candidate = CandidateFeatures(
    candidate_id="CAND-GOOD-001",
    name="Alice Engineer",
    current_title="Senior ML Engineer",
    years_of_experience=7.0,
    skills=["Python", "Embeddings", "Retrieval", "Vector Database",
            "Hybrid Search", "NDCG", "MRR", "PyTorch", "FAISS", "Ranking"],
    summary="ML engineer with 7 years building search and ranking systems.",
    recruiter_response_rate=0.85,
    last_active_days_ago=5,
    open_to_work=True,
    github_activity_score=0.8,
    embedding=[],
    raw={"experience": [{"title": "ML Engineer"}, {"title": "Data Scientist"}],
         "certifications": [{"name": "AWS ML Specialty"}],
         "projects": [{"name": "open-source retrieval lib"}]},
)

bad_candidate = CandidateFeatures(
    candidate_id="CAND-BAD-002",
    name="Bob Marketer",
    current_title="Marketing Manager",
    years_of_experience=2.0,
    skills=["Python", "SQL", "Excel", "Marketing Analytics"],
    summary="Marketing professional.",
    recruiter_response_rate=0.10,
    last_active_days_ago=200,
    open_to_work=False,
    github_activity_score=-1,
    embedding=[],
    raw={},
)

sc_good = score_candidate(parsed, good_candidate)
sc_bad  = score_candidate(parsed, bad_candidate)

print("=" * 60)
print("SCORING")
print("=" * 60)
print(f"  Good candidate  : score={sc_good.score:.4f}  skill={sc_good.skill_match:.3f}  "
      f"exp={sc_good.experience_relevance:.3f}  growth={sc_good.growth_index:.3f}  "
      f"behav={sc_good.behavioral_score:.3f}")
print(f"  Bad  candidate  : score={sc_bad.score:.4f}  skill={sc_bad.skill_match:.3f}  "
      f"exp={sc_bad.experience_relevance:.3f}  growth={sc_bad.growth_index:.3f}  "
      f"behav={sc_bad.behavioral_score:.3f}")

assert sc_good.score > sc_bad.score, \
    f"Good candidate should outscore bad! {sc_good.score} vs {sc_bad.score}"
print("  [OK] Good > Bad")
print()

# ── 3. Reranker + reasoning ──
shortlist = [(good_candidate, sc_good), (bad_candidate, sc_bad)]
reranked = rerank(parsed, shortlist)

print("=" * 60)
print("RERANKING + REASONING")
print("=" * 60)
for i, (feats, sc) in enumerate(reranked, 1):
    reasoning = build_reasoning(parsed, feats, sc)
    print(f"  Rank {i}: {feats.name} (score={sc.score:.4f})")
    print(f"    Reasoning: {reasoning[:200]}")
    print()

assert reranked[0][1].score >= reranked[1][1].score, "Rerank order wrong"
print("  [OK] Rerank order correct")
print()

print("ALL SMOKE TESTS PASSED [OK]")
