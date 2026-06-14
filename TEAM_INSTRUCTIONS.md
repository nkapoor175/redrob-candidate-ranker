# Team Instructions & Integration Rules

**Project:** Redrob Candidate Ranker — AI-Powered Candidate Ranking System
**Repo:** https://github.com/nkapoor175/redrob-candidate-ranker
**Integration Lead:** Navika — all integration questions go to her.

---

## 0. The golden rule

**Everyone edits ONE file and never changes the function signatures.**

Every module talks to the others *only* through the data shapes defined in
`app/schemas.py`. If your function takes and returns the agreed types, your code
"just works" when merged. There is no big merge-it-all-at-the-end step.

| Person | Role | The ONLY file(s) you edit | Function(s) you implement | Must return |
|--------|------|---------------------------|---------------------------|-------------|
| Parthvi | Candidate Understanding | `app/modules/candidate_parser.py` | `parse_candidate(record)` | `CandidateFeatures` |
| Jash | Job Understanding & Ranking | `app/modules/jd_parser.py`, `scoring.py`, `reranker.py` | `parse_jd`, `score_candidate`, `rerank`, `build_reasoning` | `ParsedJD`, `ScoredCandidate`, list, str |
| Navika | Backend & Integration | `app/main.py`, `app/pipeline.py`, `app/schemas.py` | wiring + API | — |
| Kaarthik | Frontend / Docs / Demo | frontend (separate project) | calls the `/rank` API over HTTP | — |

Replace the **body** of your function. Keep the name, the arguments, and the
return type exactly as they are.

---

## 1. One-time setup (everyone)

```bash
git clone https://github.com/nkapoor175/redrob-candidate-ranker.git
cd redrob-candidate-ranker
python -m venv venv
# Windows: venv\Scripts\activate     Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
git checkout -b yourname        # e.g. git checkout -b parthvi
```

A small sample dataset and the job description are already in `data/` so you can
test immediately. The full 100K `candidates.jsonl` is NOT in the repo (too big) —
get it from the shared drive and drop it in `data/`.

---

## 2. Daily workflow (everyone)

```bash
git pull origin main            # get latest before you start
# ... edit your file ...
git add .
git commit -m "what you changed"
git push origin yourname        # push YOUR branch, not main
```

Then open a Pull Request on GitHub into `main`. Navika reviews that signatures
are unchanged and merges. **Commit small and often** — judges check git history
for real iteration; one giant final commit is a red flag at Stage 4.

---

## 3. The contract — `app/schemas.py` (READ BEFORE CODING)

These are the shared data shapes. **Do not change them yourself.** If you need a
new field, tell Navika and she changes it once for everyone.

- **ParsedJD** — `required_skills[]`, `preferred_skills[]`, `experience_required_min/max`, `role_type`, `notes`
- **CandidateFeatures** — `candidate_id`, `name`, `current_title`, `years_of_experience`, `skills[]`, `summary`, behavioral signals, `embedding[]`, `raw`
- **ScoredCandidate** — `candidate_id`, `score`, `skill_match`, `experience_relevance`, `growth_index`, `behavioral_score`
- **RankedCandidate** — `candidate_id`, `rank`, `score`, `reasoning`

Schema stability is the #1 thing that keeps integration painless. Lock it on the
first call; change it only through Navika after that.

---

## 4. Per-person briefs

### Parthvi — Candidate Understanding
You own `app/modules/candidate_parser.py`. Replace the body of
`parse_candidate(record)` with your real parsing + feature extraction +
embeddings — but it must still return a `CandidateFeatures` object, including
filling in the `embedding` field. Don't touch any other file.
**Critical:** embeddings for 100K candidates can't be generated during ranking
(5-min limit). Write a SEPARATE script that computes all embeddings once and
saves them to disk; the pipeline loads them at rank time.

### Jash — Job Understanding & Ranking
You own three files:
- `jd_parser.py` → `parse_jd(jd_text)` returns `ParsedJD`
- `scoring.py` → `score_candidate(jd, cand)` returns `ScoredCandidate`
- `reranker.py` → `rerank(...)` and `build_reasoning(...)`

Replace the bodies with your real hybrid model and explanation logic; keep the
names, arguments, and return types identical.
**Hard rule:** no hosted LLM API calls (OpenAI/Anthropic/etc.) anywhere in the
ranking path — it must run offline, CPU-only, under 5 minutes.

### Navika — Backend & Integration
You own `app/main.py`, `app/pipeline.py`, `app/schemas.py`, `rank.py`, tests.
You don't implement the ML — you wire the modules together, expose the API, and
produce the submission CSV. You own schema changes and PR merges.

### Kaarthik — Frontend / Presentation / Docs
You don't merge any Python. Your dashboard calls the backend API:
- Start the server: `uvicorn app.main:app --reload`
- Call `POST /rank` with `jd_text` + the candidate file; get back ranked
  candidates with scores and reasoning as JSON.
- Full endpoint details in `API_DOCS.md`; interactive docs at
  `http://127.0.0.1:8000/docs`.
You also own the PPT, demo video, and keeping the GitHub README current.

---

## 5. Smoke test (run after every merge — Navika)

```bash
python rank.py --candidates ./data/candidates.jsonl --out ./outputs/submission.csv
python tests/test_submission_format.py outputs/submission.csv data/candidates.jsonl
```

If both pass, integration is healthy. If not, the last merged PR is the culprit.

---

## 6. Hard constraints (do NOT break — from submission_spec.md)

- Ranking step must run **offline, CPU-only, ≤5 min, ≤16 GB**.
- **No hosted LLM API calls** inside `rank.py` / the ranking path.
- **Embeddings pre-computed once and saved to disk**, never generated at rank time.
- Output CSV: exactly 100 rows, ranks 1–100 each once, unique candidate_ids,
  scores non-increasing with rank, columns `candidate_id,rank,score,reasoning`.
- Never commit the full `candidates.jsonl` (it's git-ignored).

---

## 7. Branch & PR etiquette

- One branch per person, named after you.
- Pull `main` before starting each session.
- Small, frequent, descriptive commits.
- PR into `main`; Navika reviews + merges.
- Don't push directly to `main`.
