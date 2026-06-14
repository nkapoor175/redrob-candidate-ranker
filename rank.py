"""
Stage-3 reproducible entrypoint (submission_spec.md Section 10.3).

Single command that produces the submission CSV from the candidates file,
offline and CPU-only:

    python rank.py --candidates ./data/candidates.jsonl --out ./outputs/submission.csv

This is the command organizers run inside the sandboxed container. Keep it
self-contained and free of network calls.
"""
from __future__ import annotations
import argparse
import time
from pathlib import Path

from app import pipeline

DEFAULT_JD = Path(__file__).resolve().parent / "data" / "job_description.md"


def main():
    ap = argparse.ArgumentParser(description="Produce the top-100 ranking CSV.")
    ap.add_argument("--candidates", required=True, help="Path to candidates.jsonl or .jsonl.gz")
    ap.add_argument("--jd", default=str(DEFAULT_JD), help="Path to the job description text/markdown")
    ap.add_argument("--out", default="./outputs/submission.csv", help="Output CSV path")
    ap.add_argument("--top-k", type=int, default=100)
    args = ap.parse_args()

    jd_text = Path(args.jd).read_text(encoding="utf-8") if Path(args.jd).exists() else ""

    t0 = time.time()
    resp = pipeline.rank_candidates(jd_text, args.candidates, top_k=args.top_k)
    out = pipeline.write_submission_csv(resp, args.out)
    elapsed = time.time() - t0

    print(f"Ranked {resp.total_candidates} candidates -> top {len(resp.results)}")
    print(f"Wrote {out}")
    print(f"Ranking step took {elapsed:.1f}s (budget: 300s)")


if __name__ == "__main__":
    main()
