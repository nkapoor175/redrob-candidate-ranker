# India Runs Hackathon — AI-Powered Candidate Ranking System

Team project for the **Redrob Intelligent Candidate Discovery & Ranking Challenge**.
Given a Job Description and a pool of 100,000 candidates, the system ranks the
top-100 best-fit candidates with explainable reasoning.

## Team

| Member | Role | Owns |
|--------|------|------|
| Parthvi | AI & Candidate Understanding | `app/modules/candidate_parser.py` (parsing, features, embeddings) |
| Jash | Job Understanding & Ranking | `app/modules/jd_parser.py`, `scoring.py`, `reranker.py` |
| **Navika** | **Backend & Integration** | **`app/main.py`, `app/pipeline.py`, `app/schemas.py`, `rank.py`, tests** |
| Kaarthik | Frontend, Presentation & Docs | dashboard (consumes this API), PPT, demo video |

## What this backend does (Navika's part)

It is the glue layer. It defines the shared data contracts (`schemas.py`), wires
all four modules into one pipeline (`pipeline.py`), exposes them over a FastAPI
service (`main.py`), and produces the spec-compliant submission CSV (`rank.py`).
The teammates' modules currently contain working **baseline stubs** so the whole
thing runs today; each module keeps a fixed signature so Parthvi and Jash can
drop in their real implementations without breaking integration.

## Project structure

```
India-Runs-Hackathon/
├── app/
│   ├── main.py            # FastAPI app + endpoints      (Navika)
│   ├── pipeline.py        # integration layer + pipeline  (Navika)
│   ├── schemas.py         # shared data formats           (Navika)
│   └── modules/
│       ├── jd_parser.py        # JD -> ParsedJD           (Jash)
│       ├── candidate_parser.py # record -> features       (Parthvi)
│       ├── scoring.py          # hybrid scoring engine     (Jash)
│       └── reranker.py         # re-rank + reasoning       (Jash)
├── rank.py                # CLI: produces submission CSV (Stage-3 command)
├── tests/test_submission_format.py  # local format validator
├── data/                  # put candidates.jsonl(.gz) + job_description.md here
├── outputs/               # submission.csv lands here
├── requirements.txt
├── submission_metadata.yaml
└── API_DOCS.md
```

## Setup

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Precomputing Embeddings (Offline Setup)

To support offline ranking and avoid network queries at runtime, candidate embeddings must be precomputed. This one-time step downloads the SentenceTransformer model weights, saves them locally, and generates the embedding cache.

1. Ensure the raw candidates file is at `data/candidates.jsonl`.
2. Run the offline precomputation script:
   ```bash
   python precompute_embeddings.py --candidates data/candidates.jsonl
   ```

This script will:
- Download the `all-MiniLM-L6-v2` SentenceTransformer model (if not already cached locally).
- Save the model weights to `data/models/all-MiniLM-L6-v2/` so they can be loaded later with `local_files_only=True` without internet access.
- Batch-encode candidates in `data/candidates.jsonl`, quantize the embeddings to `int8`, and write them to `data/candidate_embeddings.npz` (which the candidate parser reads).

Both `data/models/` and `data/candidate_embeddings.npz` are added to `.gitignore` so they won't bloat the repository.

## Run the API server

```bash
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs** for interactive (Swagger) API docs.
The frontend dashboard calls these endpoints.

## Produce a submission CSV (Stage-3 reproducible command)

Once the embeddings have been precomputed, run:

```bash
python rank.py --candidates ./data/candidates.jsonl --out ./outputs/submission.csv
```

This runs **offline, CPU-only** and stays well inside the 5-minute / 16 GB budget
required by `submission_spec.md` Section 3. No hosted LLM calls happen during
ranking.

## Validate before submitting

```bash
python tests/test_submission_format.py outputs/submission.csv data/candidates.jsonl
```

Catches every common rejection (wrong row count, ranks not 1–100, duplicate IDs,
non-decreasing scores, IDs missing from the dataset) before you upload.

## How the modules connect

```
JD text ───────────────► jd_parser.parse_jd ─────────► ParsedJD
candidates.jsonl ──► candidate_parser.parse_candidate ─► CandidateFeatures
(ParsedJD + features) ─► scoring.score_candidate ──────► ScoredCandidate
top-K shortlist ──► reranker.rerank + build_reasoning ─► RankedCandidate[]
RankedCandidate[] ─► pipeline.write_submission_csv ────► submission.csv
```

## Notes for teammates

- Keep the function signatures in `app/modules/*` unchanged — the integration
  layer depends on them. Replace the bodies, not the interfaces.
- The ranking step (`rank.py`) must stay offline. If you want LLM-quality
  reasoning, generate it as a separate pre-compute step, not inside `rank.py`.
- A real dataset isn't committed; drop `candidates.jsonl(.gz)` into `data/`.
