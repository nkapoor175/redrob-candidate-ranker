# Redrob Candidate Ranker — AI-Powered Candidate Ranking System

**Team Catalyst** · Redrob Intelligent Candidate Discovery & Ranking Challenge

Given a job description and a pool of 100,000 candidates, this system ranks the
top-100 best-fit candidates the way a recruiter would — using skills, experience,
career growth, and behavioral signals rather than keyword matching — and returns
an explainable, spec-compliant shortlist.

- **Live demo (sandbox):** https://huggingface.co/spaces/navikakapoor/redrob-candidate-ranker
- **Ranking performance:** 100,000 candidates ranked in ~90 seconds, offline, CPU-only.

## Approach

A hybrid, explainable ranker:

- **JD understanding** — offline parsing (regex + a skills taxonomy + fuzzy
  matching) extracts required/preferred skills, an experience band, and role type.
- **Candidate understanding** — each profile is parsed into structured features;
  semantic embeddings (`sentence-transformers/all-MiniLM-L6-v2`) are pre-computed
  offline and looked up at rank time.
- **Hybrid scoring** — four signals combined as a weighted blend:
  skill match (0.40), experience relevance (0.25), growth index (0.20),
  behavioral score (0.15), then gated by a **title-fit** check so keyword-stuffed,
  off-target profiles cannot rank at the top. Semantic cosine similarity is blended
  in when embeddings are present.
- **Explainability** — every candidate ships with a fact-grounded reason generated
  from its own computed scores (no hallucination, no LLM calls in the ranking path).

## Project structure

```
redrob-candidate-ranker/
├── app/
│   ├── main.py            # FastAPI service (/rank, /rank/csv, /health)
│   ├── pipeline.py        # integration layer + data pipeline
│   ├── schemas.py         # shared data contracts
│   └── modules/
│       ├── jd_parser.py         # JD text  -> ParsedJD
│       ├── candidate_parser.py  # record   -> CandidateFeatures (+ embedding lookup)
│       ├── scoring.py           # hybrid scoring engine
│       └── reranker.py          # deterministic re-rank + explanation generation
├── precompute_embeddings.py     # offline, one-time embedding generation
├── rank.py                      # single-command CSV producer (Stage-3)
├── tests/test_submission_format.py  # local submission validator
├── requirements.txt
└── submission_metadata.yaml
```

## Reproduce the submission CSV

Recommended: Python 3.11 or 3.12.

```bash
python -m venv venv && venv\Scripts\activate      # Windows (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
```

**Step 1 — one-time offline pre-computation** (place the dataset at `data/candidates.jsonl` first):

```bash
python precompute_embeddings.py --candidates data/candidates.jsonl
```

This downloads the `all-MiniLM-L6-v2` model, saves the weights to
`data/models/` (so they load later with `local_files_only=True`, no internet),
batch-encodes candidates, quantizes to int8, and writes
`data/candidate_embeddings.npz`. Pre-computation may exceed 5 minutes — that is
allowed; only the ranking step is time-limited.

**Step 2 — produce the ranking (the single Stage-3 command):**

```bash
python rank.py --candidates ./data/candidates.jsonl --out ./outputs/submission.csv
```

Runs **offline, CPU-only**, and completes the ranking of 100K candidates in
~90 seconds — well within the 5-minute / 16 GB budget (submission_spec Section 3).
No hosted LLM calls occur during ranking.

**Step 3 — validate before submitting:**

```bash
python tests/test_submission_format.py outputs/submission.csv data/candidates.jsonl
```

Checks row count, ranks 1–100, unique IDs, non-increasing scores, and that every
ID exists in the dataset.

## Run the API / dashboard backend

```bash
uvicorn app.main:app --reload
```

Interactive API docs at `http://127.0.0.1:8000/docs`. The recruiter dashboard
(separate `frontend/` app) calls `POST /rank`.

## Pipeline

```
JD text ─────────────► jd_parser.parse_jd ─────────► ParsedJD
candidates.jsonl ──► candidate_parser.parse_candidate ─► CandidateFeatures (+ embedding)
(ParsedJD + features) ─► scoring.score_candidate ────► ScoredCandidate
top-K shortlist ──► reranker.rerank + build_reasoning ─► RankedCandidate[]
RankedCandidate[] ─► pipeline.write_submission_csv ──► submission.csv
```

## Notes on artifacts

The 100K `candidates.jsonl`, generated `candidate_embeddings.npz`, and downloaded
model weights are git-ignored; `precompute_embeddings.py` regenerates the
embeddings for any dataset. The model is fetched once and cached locally for
fully offline ranking.

## Team

| Member | Role |
|--------|------|
| Parthvi Mishra | Candidate Understanding & Embeddings |
| Jash Trehan | Job Understanding & Ranking |
| Navika Kapoor | Backend & Integration |
| Kaarthik Reddy | Frontend, Presentation & Documentation |
