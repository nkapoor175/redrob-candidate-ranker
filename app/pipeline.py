"""
Integration Layer + Data Processing Pipeline
==============================================
OWNER: Navika (Member 3 - Backend & Integration Lead)

This is YOUR core deliverable. It connects all four modules into one flow:

    JD text ---------> jd_parser.parse_jd ---------> ParsedJD
    candidates.jsonl -> candidate_parser.parse_candidate -> CandidateFeatures
    (ParsedJD + CandidateFeatures) -> scoring.score_candidate -> ScoredCandidate
    top-K shortlist -> reranker.rerank + build_reasoning -> RankedCandidate[]
    RankedCandidate[] -> CSV (submission) + JSON (dashboard)

It reads gzipped or plain JSONL, streams to stay under the 16 GB limit, and
writes a submission CSV that matches submission_spec.md exactly.
"""
from __future__ import annotations
import csv
import gzip
import json
import io
from pathlib import Path
from typing import Iterator, List

from app.schemas import ParsedJD, RankedCandidate, RankResponse
from app.modules import jd_parser, candidate_parser, scoring, reranker


# ---------- data loading ----------
def iter_candidates(path: str | Path) -> Iterator[dict]:
    """Stream candidate records from .jsonl or .jsonl.gz one at a time."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


# ---------- the pipeline ----------
def rank_candidates(jd_text: str,
                    candidates_path: str | Path,
                    top_k: int = 100) -> RankResponse:
    """Run the full pipeline and return the top-K ranked candidates."""
    jd: ParsedJD = jd_parser.parse_jd(jd_text)

    scored = []  # list[(CandidateFeatures, ScoredCandidate)]
    total = 0
    for record in iter_candidates(candidates_path):
        total += 1
        feats = candidate_parser.parse_candidate(record)
        sc = scoring.score_candidate(jd, feats)
        scored.append((feats, sc))

    # keep an over-sized shortlist, then do the careful re-rank pass on it
    scored.sort(key=lambda x: (-x[1].score, x[0].candidate_id))
    shortlist = scored[: max(top_k * 3, top_k)]
    reranked = reranker.rerank(jd, shortlist)[:top_k]

    results: List[RankedCandidate] = []
    for i, (feats, sc) in enumerate(reranked, start=1):
        results.append(RankedCandidate(
            candidate_id=feats.candidate_id,
            rank=i,
            score=sc.score,
            reasoning=reranker.build_reasoning(jd, feats, sc),
        ))

    return RankResponse(job_title=jd.role_type, total_candidates=total, results=results)


# ---------- submission output ----------
def write_submission_csv(resp: RankResponse, out_path: str | Path) -> Path:
    """Write the spec-compliant CSV: candidate_id,rank,score,reasoning."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["candidate_id", "rank", "score", "reasoning"])
        for r in resp.results:
            w.writerow([r.candidate_id, r.rank, f"{r.score:.4f}", r.reasoning])
    return out_path
