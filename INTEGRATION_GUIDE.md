# Integration Guide (read this before you write code)

Owner: Navika (Backend & Integration Lead). Questions about integration → me.

## The one rule that makes integration painless

**Everyone edits ONE file and never changes the function signatures.**
All modules talk to each other only through the data shapes in `app/schemas.py`.
If your function takes and returns the agreed types, your code "just works" when
merged — there is no big integration step at the end.

| Person | The ONLY file you edit | The function you implement | Must return |
|--------|------------------------|----------------------------|-------------|
| Parthvi | `app/modules/candidate_parser.py` | `parse_candidate(record) ` | `CandidateFeatures` |
| Jash | `app/modules/jd_parser.py` | `parse_jd(jd_text)` | `ParsedJD` |
| Jash | `app/modules/scoring.py` | `score_candidate(jd, cand)` | `ScoredCandidate` |
| Jash | `app/modules/reranker.py` | `rerank(...)`, `build_reasoning(...)` | reranked list / string |
| Navika | `app/pipeline.py`, `app/main.py`, `app/schemas.py` | wiring + API | — |
| Kaarthik | frontend (separate) | calls the `/rank` API over HTTP | — |

Replace the *body* of your function. Keep the name, arguments, and return type.

## Step-by-step plan

1. **Navika** creates the GitHub repo and pushes this scaffold (first commit).
2. **Whole team, one short call:** walk through `app/schemas.py` and agree on the
   fields. After this call, schemas are frozen. Need a new field later? Tell
   Navika — schema changes go through one person only.
3. Everyone clones, makes a branch named after themselves (`git checkout -b parthvi`).
4. Build inside your file. Test locally with the sample dataset already in `data/`.
5. Open a Pull Request into `main`. Navika reviews that the signature is unchanged,
   then merges.
6. After every merge, Navika runs the smoke test (below). Green = still integrated.
7. Once embeddings are real, Parthvi adds a pre-compute script (see note below).
8. Final dry run on the full 100k dataset, validate, then submit.

## Smoke test (run after every merge)

```bash
python rank.py --candidates ./data/candidates.jsonl --out ./outputs/submission.csv
python tests/test_submission_format.py outputs/submission.csv data/candidates.jsonl
```

If both pass, integration is healthy. If not, the last merged PR is the culprit.

## Critical constraints (do not break these)

- **Ranking step must run offline, CPU-only, ≤5 min, ≤16 GB** (submission_spec §3).
- **No hosted LLM API calls inside `rank.py`** (no OpenAI/Anthropic/etc. at rank time).
- **Embeddings are pre-computed once and saved to disk**, then loaded at rank time —
  never generate 100k embeddings inside the ranking step.

## Branch / PR etiquette

- One branch per person, named after you.
- Small, frequent commits (the judges check git history for real iteration — a
  single giant "final dump" commit is a red flag at Stage 4).
- PR title = what you changed. Navika merges.
- Never commit the full `candidates.jsonl` (it's git-ignored) — too big.
