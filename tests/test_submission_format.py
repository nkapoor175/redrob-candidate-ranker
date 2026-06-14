"""
Local submission-format validator (submission_spec.md Sections 3 & 6).
Run this before uploading so you never get auto-rejected at Stage 1.

    python tests/test_submission_format.py outputs/submission.csv data/candidates.jsonl

The second arg (candidates file) is optional; if given, every candidate_id is
checked to exist in the dataset.
"""
from __future__ import annotations
import csv
import gzip
import json
import sys
from pathlib import Path


def load_valid_ids(path):
    ids = set()
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                ids.add(json.loads(line)["candidate_id"])
    return ids


def validate(csv_path, candidates_path=None):
    errors = []
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))

    # column order
    header = list(rows[0].keys()) if rows else []
    if header != ["candidate_id", "rank", "score", "reasoning"]:
        errors.append(f"Header must be candidate_id,rank,score,reasoning (got {header})")

    if len(rows) != 100:
        errors.append(f"Must be exactly 100 rows (got {len(rows)})")

    ranks = [int(r["rank"]) for r in rows]
    if sorted(ranks) != list(range(1, 101)):
        errors.append("Ranks must be each integer 1..100 exactly once")

    ids = [r["candidate_id"] for r in rows]
    if len(set(ids)) != len(ids):
        errors.append("Duplicate candidate_id values found")

    scores = [float(r["score"]) for r in rows]
    ordered = [s for _, s in sorted(zip(ranks, scores))]
    if any(ordered[i] < ordered[i + 1] for i in range(len(ordered) - 1)):
        errors.append("Score must be non-increasing as rank increases")
    if len(set(scores)) == 1:
        errors.append("All scores identical - model isn't differentiating")

    if candidates_path:
        valid = load_valid_ids(candidates_path)
        missing = [i for i in ids if i not in valid]
        if missing:
            errors.append(f"{len(missing)} candidate_id(s) not in dataset, e.g. {missing[:3]}")

    return errors


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/submission.csv"
    cand_path = sys.argv[2] if len(sys.argv) > 2 else None
    errs = validate(csv_path, cand_path)
    if errs:
        print("INVALID submission:")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    print(f"VALID: {csv_path} passes all format checks.")
