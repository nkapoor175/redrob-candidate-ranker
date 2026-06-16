"""
JD Parser  ---  OWNER: Jash (Member 2)

Extracts structured requirements from raw job description text using
offline NLP: regex patterns, a comprehensive skills taxonomy, and
fuzzy string matching (rapidfuzz).  Splits the JD into logical sections
(required / preferred / exclusion) so skills land in the right bucket.

Runs entirely offline on CPU — no API calls.
"""
from __future__ import annotations

import re
from typing import List, Tuple

from rapidfuzz import fuzz

from app.schemas import ParsedJD

# ──────────────────────────────────────────────────────────────────────
# Comprehensive skills taxonomy (order doesn't matter; matched by fuzzy)
# ──────────────────────────────────────────────────────────────────────
_SKILLS_TAXONOMY: List[str] = [
    # --- Programming Languages ---
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang",
    "rust", "scala", "kotlin", "ruby", "r", "matlab", "julia", "swift",
    "php", "perl", "bash", "shell scripting", "sql", "nosql",
    # --- AI / ML Core ---
    "machine learning", "deep learning", "neural networks",
    "natural language processing", "nlp", "computer vision",
    "reinforcement learning", "generative ai", "transformers",
    "attention mechanism", "transfer learning",
    # --- Embeddings & Retrieval ---
    "embeddings", "sentence-transformers", "word2vec", "glove", "fasttext",
    "bert", "roberta", "gpt", "t5", "llama", "mistral",
    "retrieval", "information retrieval", "semantic search", "hybrid search",
    "dense retrieval", "sparse retrieval", "bm25", "tf-idf",
    "vector database", "pinecone", "weaviate", "qdrant", "milvus",
    "faiss", "elasticsearch", "opensearch", "chromadb", "pgvector",
    # --- LLM & Fine-tuning ---
    "large language models", "llm", "fine-tuning", "lora", "qlora", "peft",
    "prompt engineering", "rag", "retrieval augmented generation",
    "langchain", "llamaindex", "hugging face", "huggingface",
    # --- ML Frameworks ---
    "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn",
    "xgboost", "lightgbm", "catboost", "spacy", "nltk", "gensim",
    "jax", "onnx", "mlflow", "wandb", "weights and biases",
    # --- Ranking & Evaluation ---
    "ranking", "learning-to-rank", "recommendation systems",
    "collaborative filtering", "content-based filtering",
    "a/b testing", "evaluation", "ndcg", "mrr", "map",
    "precision", "recall", "f1", "offline evaluation", "online evaluation",
    # --- Data Engineering & Infra ---
    "data engineering", "etl", "data pipeline", "apache spark", "spark",
    "hadoop", "kafka", "airflow", "dbt", "snowflake", "databricks",
    "docker", "kubernetes", "k8s", "ci/cd", "mlops",
    "aws", "gcp", "azure", "cloud computing",
    "distributed systems", "microservices", "api design", "rest api",
    "graphql", "grpc", "redis", "mongodb", "postgresql", "mysql",
    # --- Data Science ---
    "data analysis", "statistics", "probability", "bayesian",
    "feature engineering", "dimensionality reduction", "pca",
    "clustering", "classification", "regression", "time series",
    "pandas", "numpy", "scipy", "matplotlib",
    # --- Web ---
    "react", "angular", "vue", "next.js", "node.js", "express",
    # --- Domain ---
    "hr-tech", "recruiting tech", "talent acquisition",
    "marketplace", "e-commerce", "fintech", "healthtech",
    # --- General Engineering ---
    "system design", "software architecture", "design patterns",
    "testing", "unit testing", "integration testing",
    "git", "code review", "production deployment",
    "monitoring", "observability", "performance optimization", "scalability",
    # --- Open Source ---
    "open-source", "open source contributions",
]

# ──────────────────────────────────────────────────────────────────────
# Section-detection patterns (compiled once)
# ──────────────────────────────────────────────────────────────────────
_REQUIRED_SECTION_RE = [
    re.compile(p, re.IGNORECASE) for p in [
        r"^(?:things?\s+you\s+)?absolutely\s+need\b",
        r"^requirements?\b",
        r"^essential\s+(?:skills?|qualifications?|experience)",
        r"^must[\s-]have\b",
        r"^what\s+(?:we|you)\s+need\b",
        r"^core\s+(?:skills?|competenc)",
        r"^minimum\s+(?:qualifications?|requirements?)",
        r"^key\s+(?:skills?|requirements?|qualifications?)",
    ]
]

_PREFERRED_SECTION_RE = [
    re.compile(p, re.IGNORECASE) for p in [
        r"(?:things?\s+we(?:'d)?\s+)?like\s+(?:you\s+to\s+have|to\s+see)",
        r"nice[\s-]to[\s-]have",
        r"prefer(?:red)?",
        r"bonus",
        r"desirable",
        r"good[\s-]to[\s-]have",
        r"additional\s+(?:skills?|qualifications?)",
        r"plus(?:es)?",
    ]
]

_EXCLUSION_SECTION_RE = [
    re.compile(p, re.IGNORECASE) for p in [
        r"(?:things?\s+we\s+)?(?:explicitly\s+)?(?:do\s+)?not\s+want",
        r"disqualif",
        r"not\s+(?:a\s+fit|looking\s+for)",
        r"red\s+flags?",
        r"deal[\s-]breakers?",
    ]
]

# ──────────────────────────────────────────────────────────────────────
# Role type detection
# ──────────────────────────────────────────────────────────────────────
_ROLE_KEYWORDS = {
    "AI Engineer":       ["ai engineer", "artificial intelligence engineer"],
    "ML Engineer":       ["ml engineer", "machine learning engineer"],
    "Data Scientist":    ["data scientist"],
    "Data Engineer":     ["data engineer"],
    "Backend Engineer":  ["backend engineer", "back-end engineer", "backend developer"],
    "Software Engineer": ["software engineer", "software developer", "swe"],
    "Full Stack Engineer": ["full stack", "fullstack"],
    "Frontend Engineer": ["frontend engineer", "front-end engineer"],
    "DevOps Engineer":   ["devops engineer", "devops"],
    "Product Manager":   ["product manager"],
    "Research Engineer":  ["research engineer"],
    "NLP Engineer":      ["nlp engineer"],
    "Search Engineer":   ["search engineer"],
    "Platform Engineer": ["platform engineer"],
}

_SENIORITY_RE = [
    (re.compile(r"\bsenior\b|\bsr\.?\b", re.I), "Senior"),
    (re.compile(r"\bstaff\b", re.I),             "Staff"),
    (re.compile(r"\bprincipal\b", re.I),          "Principal"),
    (re.compile(r"\blead\b|\btech\s*lead\b", re.I), "Lead"),
    (re.compile(r"\bjunior\b|\bjr\.?\b", re.I),   "Junior"),
    (re.compile(r"\bfounding\b", re.I),            "Founding"),
]


# ──────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────
def _extract_experience(text: str) -> Tuple[float, float]:
    """Extract min/max years of experience using multiple regex patterns."""
    lower = text.lower()

    # "5-9 years", "5–9 years", "5 to 9 years"
    m = re.search(r"(\d+)\s*[-–to]+\s*(\d+)\s*\+?\s*years?", lower)
    if m:
        return float(m.group(1)), float(m.group(2))

    # "5+ years"
    m = re.search(r"(\d+)\s*\+\s*years?", lower)
    if m:
        base = float(m.group(1))
        return base, base + 5

    # "minimum 5 years" / "at least 5 years"
    m = re.search(r"(?:minimum|at\s+least|min)\s*[:\s]*(\d+)\s*years?", lower)
    if m:
        base = float(m.group(1))
        return base, base + 5

    # "X years of experience" (generic)
    m = re.search(r"(\d+)\s*years?\s+(?:of\s+)?experience", lower)
    if m:
        base = float(m.group(1))
        return max(0, base - 1), base + 2

    return 0, 99  # could not determine — no filter


def _split_sections(text: str) -> dict[str, str]:
    """Split the JD into required / preferred / exclusion / general blocks."""
    buckets: dict[str, list[str]] = {
        "required": [], "preferred": [], "exclusion": [], "general": [],
    }
    current = "general"
    buffer: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip()
        lower = stripped.lower()

        # Only treat SHORT lines (< 120 chars, < 15 words) as potential
        # section headers.  Long prose sentences that happen to contain
        # "need" or "require" should not trigger a section change.
        is_header_candidate = len(stripped) < 120 and len(stripped.split()) < 15

        new_section = None
        if is_header_candidate:
            for rx in _REQUIRED_SECTION_RE:
                if rx.search(lower):
                    new_section = "required"
                    break
            if new_section is None:
                for rx in _PREFERRED_SECTION_RE:
                    if rx.search(lower):
                        new_section = "preferred"
                        break
            if new_section is None:
                for rx in _EXCLUSION_SECTION_RE:
                    if rx.search(lower):
                        new_section = "exclusion"
                        break

        if new_section and new_section != current:
            buckets[current].extend(buffer)
            buffer = []
            current = new_section

        buffer.append(stripped)

    buckets[current].extend(buffer)
    return {k: "\n".join(v) for k, v in buckets.items()}


def _fuzzy_match_skills(text: str, threshold: int = 80) -> List[str]:
    """Return taxonomy skills that appear in *text* (substring or fuzzy)."""
    lower = text.lower()
    # Pre-tokenise the text once for windowed fuzzy checks
    tokens = re.findall(r"\b[\w+#./-]+\b", lower)
    matched: list[str] = []

    for skill in _SKILLS_TAXONOMY:
        sk = skill.lower()

        # For very short skills (<=3 chars like "r", "go", "sql", "c++"),
        # require a word-boundary match to avoid false positives.
        if len(sk) <= 3:
            if re.search(r"\b" + re.escape(sk) + r"\b", lower):
                matched.append(skill)
            continue

        # ── fast path: substring ──
        if sk in lower:
            matched.append(skill)
            continue

        # multi-word: check all constituent words present as whole words
        parts = sk.split()
        if len(parts) > 1 and all(
            re.search(r"\b" + re.escape(p) + r"\b", lower) for p in parts
        ):
            matched.append(skill)
            continue

        # ── fuzzy path (only for skills >= 5 chars to avoid noise) ──
        if len(sk) < 5:
            continue
        for i, tok in enumerate(tokens):
            if fuzz.ratio(sk, tok) >= threshold:
                matched.append(skill)
                break
            # bigram window
            if i + 1 < len(tokens):
                bigram = f"{tok} {tokens[i + 1]}"
                if fuzz.ratio(sk, bigram) >= threshold:
                    matched.append(skill)
                    break
            # trigram window
            if i + 2 < len(tokens):
                trigram = f"{tok} {tokens[i + 1]} {tokens[i + 2]}"
                if fuzz.ratio(sk, trigram) >= threshold:
                    matched.append(skill)
                    break

    # deduplicate while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for s in matched:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(s)
    return deduped


def _extract_role_type(text: str) -> str:
    """Identify the role title from the JD text."""
    lower = text.lower()

    # Try an explicit title line near the top
    head = "\n".join(text.split("\n")[:12]).lower()
    m = re.search(
        r"(?:job\s+(?:title|description)|role|position)\s*[:：]\s*(.+?)(?:\n|$)",
        head,
    )
    if m:
        raw = m.group(1).strip().rstrip(".")
        if len(raw) < 80:
            return raw.title()

    # seniority prefix
    seniority = ""
    for rx, label in _SENIORITY_RE:
        if rx.search(lower):
            seniority = label
            break

    # match against known role keywords
    for role, keywords in _ROLE_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                return f"{seniority} {role}".strip() if seniority else role

    return f"{seniority} Software Engineer".strip() if seniority else "Software Engineer"


def _extract_notes(text: str, sections: dict[str, str]) -> str:
    """Pull out domain, location, work-mode, and disqualifier notes."""
    lower = text.lower()
    notes: list[str] = []

    # Location
    m = re.search(r"(?:location|based\s+in|office)\s*[:：]?\s*(.+?)(?:\n|$)", lower)
    if m:
        notes.append(f"Location: {m.group(1).strip()[:120]}")

    # Work mode
    if "remote" in lower and "hybrid" in lower:
        notes.append("Work mode: Hybrid/Remote")
    elif "remote" in lower:
        notes.append("Work mode: Remote")
    elif "hybrid" in lower:
        notes.append("Work mode: Hybrid")
    elif re.search(r"on[\s-]?site|in[\s-]office", lower):
        notes.append("Work mode: On-site")

    # Domain keywords
    domain_map = {
        "fintech": "Fintech", "hr-tech": "HR-Tech", "hrtech": "HR-Tech",
        "recruiting": "Recruiting/HR-Tech", "talent intelligence": "Talent/HR-Tech",
        "marketplace": "Marketplace", "e-commerce": "E-Commerce",
        "healthtech": "HealthTech", "edtech": "EdTech",
        "saas": "SaaS", "series a": "Series-A Startup", "startup": "Startup",
    }
    domains: list[str] = []
    seen_domains: set[str] = set()
    for kw, label in domain_map.items():
        if kw in lower and label not in seen_domains:
            seen_domains.add(label)
            domains.append(label)
    if domains:
        notes.append(f"Domain: {', '.join(domains[:4])}")

    # Warnings from the JD itself
    if "keyword stuff" in lower or "trap" in lower or "honeypot" in lower:
        notes.append("WARNING: JD warns against keyword-stuffed / honeypot profiles.")
    if "consulting" in lower or "services" in lower:
        notes.append("Down-weight pure consulting/services-only backgrounds.")
    if "production" in lower:
        notes.append("Strong emphasis on production deployment experience.")

    # Disqualifier summary (first 200 chars of exclusion section)
    excl = sections.get("exclusion", "").strip()
    if excl:
        notes.append(f"Disqualifiers: {excl[:200]}")

    return " | ".join(notes) if notes else ""


# ──────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────
def parse_jd(jd_text: str) -> ParsedJD:
    """Parse raw JD text into structured requirements.

    Uses regex for experience ranges, section-aware skill extraction with a
    comprehensive taxonomy + rapidfuzz fuzzy matching, pattern-based role-type
    detection, and keyword extraction for contextual notes.

    Fully offline — no API calls.
    """
    if not jd_text or not jd_text.strip():
        return ParsedJD()

    sections = _split_sections(jd_text)
    exp_min, exp_max = _extract_experience(jd_text)

    # ── Skill extraction ──
    req_text = sections.get("required", "")
    pref_text = sections.get("preferred", "")

    required_skills = _fuzzy_match_skills(req_text) if req_text.strip() else []
    preferred_skills = _fuzzy_match_skills(pref_text) if pref_text.strip() else []

    # If nothing landed in the required bucket, scan full text
    if not required_skills:
        required_skills = _fuzzy_match_skills(jd_text)

    # Remove duplicates across buckets (required wins)
    req_lower = {s.lower() for s in required_skills}
    preferred_skills = [s for s in preferred_skills if s.lower() not in req_lower]

    role_type = _extract_role_type(jd_text)
    notes = _extract_notes(jd_text, sections)

    return ParsedJD(
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        experience_required_min=exp_min,
        experience_required_max=exp_max,
        role_type=role_type,
        notes=notes,
    )
