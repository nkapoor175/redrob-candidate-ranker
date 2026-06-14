"""
FastAPI Backend  ---  OWNER: Navika (Member 3 - Backend & Integration Lead)

Endpoints that expose the pipeline to the frontend dashboard (Kaarthik) and
let recruiters upload a JD + candidate file and get a ranked shortlist back.

Run locally:
    uvicorn app.main:app --reload
Interactive API docs (auto-generated) at:  http://127.0.0.1:8000/docs
"""
from __future__ import annotations
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import RankResponse
from app import pipeline

app = FastAPI(
    title="Redrob Candidate Ranking API",
    description="Backend for the AI-Powered Candidate Ranking System "
                "(India Runs Hackathon). Connects JD parsing, candidate "
                "parsing, scoring, and re-ranking into one service.",
    version="0.1.0",
)

# allow the frontend dashboard (Kaarthik) to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# default dataset location (drop candidates.jsonl or .jsonl.gz in /data)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@app.get("/health")
def health():
    """Liveness check for the dashboard / sandbox."""
    return {"status": "ok"}


@app.post("/rank", response_model=RankResponse)
async def rank(
    jd_text: str = Form(..., description="Raw job description text"),
    top_k: int = Form(100, description="How many candidates to return"),
    candidates_file: UploadFile | None = File(
        None, description="candidates.jsonl or .jsonl.gz. "
                          "If omitted, uses data/candidates.jsonl."),
):
    """Main endpoint: rank candidates for a JD.

    Accepts an uploaded candidate file OR falls back to the bundled dataset,
    runs the full pipeline, and returns the ranked shortlist as JSON.
    """
    if candidates_file is not None:
        suffix = ".jsonl.gz" if candidates_file.filename.endswith(".gz") else ".jsonl"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(await candidates_file.read())
        tmp.close()
        path = tmp.name
    else:
        path = DATA_DIR / "candidates.jsonl"
        if not path.exists():
            path = DATA_DIR / "candidates.jsonl.gz"
        if not path.exists():
            raise HTTPException(
                status_code=400,
                detail="No candidate file uploaded and no dataset found in /data.",
            )

    try:
        return pipeline.rank_candidates(jd_text, path, top_k=top_k)
    except Exception as e:  # surface pipeline errors cleanly to the dashboard
        raise HTTPException(status_code=500, detail=f"Ranking failed: {e}")


@app.post("/rank/csv")
async def rank_csv(
    jd_text: str = Form(...),
    top_k: int = Form(100),
    candidates_file: UploadFile | None = File(None),
):
    """Same as /rank but writes the spec-compliant submission CSV to /outputs
    and returns the path. Handy for generating the actual hackathon submission.
    """
    resp = await rank(jd_text=jd_text, top_k=top_k, candidates_file=candidates_file)
    out = pipeline.write_submission_csv(
        resp, Path(__file__).resolve().parent.parent / "outputs" / "submission.csv")
    return {"rows": len(resp.results), "csv_path": str(out)}
