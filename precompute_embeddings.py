#!/usr/bin/env python3
"""
Precompute Candidate Embeddings
===============================
This script runs offline batch-encoding for all candidate records.
It saves precomputed embedding vectors to a compressed NumPy archive.
Usage:
    python precompute_embeddings.py --candidates data/candidates.jsonl
"""

import argparse
import sys
import time
from pathlib import Path
import numpy as np

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.pipeline import iter_candidates
from app.modules.candidate_parser import build_text_for_embedding


def main():
    parser = argparse.ArgumentParser(description="Precompute candidate embeddings in batch.")
    parser.add_argument(
        "--candidates",
        required=True,
        help="Path to candidates.jsonl or candidates.jsonl.gz",
    )
    parser.add_argument(
        "--out",
        default="./data/candidate_embeddings.npz",
        help="Output path for precomputed numpy archive",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=256,
        help="Batch size for SentenceTransformer encoding",
    )
    args = parser.parse_args()

    candidates_path = Path(args.candidates)
    out_path = Path(args.out)

    if not candidates_path.exists():
        print(f"Error: Candidate file not found at {candidates_path}")
        sys.exit(1)

    print(f"Reading candidates from {candidates_path}...")
    t0 = time.time()
    records = list(iter_candidates(candidates_path))
    num_candidates = len(records)
    print(f"Loaded {num_candidates} candidates in {time.time() - t0:.2f}s")

    if num_candidates == 0:
        print("No candidates found.")
        sys.exit(0)

    print("Building texts for embedding...")
    t0 = time.time()
    texts = [build_text_for_embedding(rec) for rec in records]
    ids = [rec.get("candidate_id", "") for rec in records]
    print(f"Built texts in {time.time() - t0:.2f}s")

    print("Loading SentenceTransformer('all-MiniLM-L6-v2')...")
    t0 = time.time()
    from sentence_transformers import SentenceTransformer
    # We load without local_files_only=True so it can download/cache the model initially
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print(f"Model loaded in {time.time() - t0:.2f}s")

    local_model_path = Path(__file__).resolve().parent / "data" / "models" / "all-MiniLM-L6-v2"
    print(f"Saving model weights locally to {local_model_path}...")
    model.save(str(local_model_path))

    print(f"Encoding {num_candidates} texts (batch_size={args.batch_size})...")
    t0 = time.time()
    embeddings = model.encode(
        texts,
        batch_size=args.batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    duration = time.time() - t0
    print(f"Encoded {num_candidates} texts in {duration:.2f}s ({num_candidates / duration:.1f} cands/sec)")

    print("Quantizing embeddings to int8...")
    # Scale from [-1.0, 1.0] to [-127, 127] and cast to int8
    quantized_embeddings = np.round(embeddings * 127.0).astype(np.int8)

    print(f"Saving quantized embeddings to {out_path}...")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out_path,
        ids=np.array(ids, dtype=object),
        embeddings=quantized_embeddings,
    )
    print("Pre-computation completed successfully!")


if __name__ == "__main__":
    main()
