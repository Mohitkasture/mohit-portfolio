import re

from home.services.llm import chat_completion

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{2,4}\)?[\s\-]?)?\d{3,4}[\s\-]?\d{3,4}"
)
GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w\-]+/?", re.I)
LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-/%]+/?", re.I)
TECH_RE = re.compile(
    r"\b(Python|Django|Flask|DRF|PostgreSQL|MySQL|Redis|Docker|Celery|"
    r"GitHub Actions|CI/CD|REST|JWT|React|JavaScript|TypeScript|SQL|"
    r"MongoDB|AWS|Nginx|Gunicorn|LLM|RAG|embeddings?|vector|Unity|C#)\b",
    re.I,
)

TARGET_BACKEND_KEYWORDS = {
    "python",
    "django",
    "django rest framework",
    "drf",
    "postgresql",
    "sql",
    "rest",
    "docker",
    "redis",
    "jwt",
    "ci/cd",
    "github actions",
    "celery",
    "api",
}


def extract_text_from_pdf(file_bytes):
    try:
        from io import BytesIO

        from pypdf import PdfReader

        reader = PdfReader(BytesIO(file_bytes))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts).strip()
    except Exception:
        return ""


def rule_based_extract(text):
    emails = EMAIL_RE.findall(text or "")
    phones = PHONE_RE.findall(text or "")
    github = GITHUB_RE.findall(text or "")
    linkedin = LINKEDIN_RE.findall(text or "")
    techs = sorted({m.group(0) for m in TECH_RE.finditer(text or "")}, key=str.lower)
    lower = (text or "").lower()
    present = sorted(k for k in TARGET_BACKEND_KEYWORDS if k in lower)
    missing = sorted(k for k in TARGET_BACKEND_KEYWORDS if k not in lower)
    return {
        "emails": emails[:3],
        "phones": [p.strip() for p in phones[:3] if len(re.sub(r"\D", "", p)) >= 10],
        "github": github[:2],
        "linkedin": linkedin[:2],
        "technologies": techs,
        "matched_keywords": present,
        "missing_keywords": missing[:12],
    }


def score_resume(text, extracted):
    """Deterministic ATS-style scoring from rules (not random LLM scores)."""
    length = len(text or "")
    length_score = min(25, length / 80)
    keyword_ratio = len(extracted["matched_keywords"]) / max(1, len(TARGET_BACKEND_KEYWORDS))
    keyword_score = keyword_ratio * 40
    contact_score = 0
    if extracted["emails"]:
        contact_score += 8
    if extracted["phones"]:
        contact_score += 7
    if extracted["github"] or extracted["linkedin"]:
        contact_score += 5
    project_score = (
        15 if re.search(r"\b(project|built|developed|implemented)\b", text or "", re.I) else 5
    )
    experience_score = (
        15
        if re.search(r"\b(experience|intern|developer|engineer)\b", text or "", re.I)
        else 5
    )
    total = round(
        min(
            100,
            length_score + keyword_score + contact_score + project_score + experience_score,
        )
    )
    return {
        "ats_score": total,
        "skills_match": round(keyword_ratio * 100),
        "experience": min(100, round(experience_score / 15 * 100)),
        "projects": min(100, round(project_score / 15 * 100)),
        "contact": min(100, round(contact_score / 20 * 100)),
    }


def analyze_resume(text):
    extracted = rule_based_extract(text)
    scores = score_resume(text, extracted)
    llm_suggestions = chat_completion(
        [
            {
                "role": "system",
                "content": (
                    "You are a resume coach for backend/Python roles. "
                    "Given extracted resume facts and scores, give 4 concrete improvement bullets. "
                    "Do not invent fake employers. Do not change the numeric scores."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Scores: {scores}\nExtracted: {extracted}\n"
                    f"Resume excerpt:\n{(text or '')[:3500]}"
                ),
            },
        ],
        max_tokens=450,
    )
    mode = "rules+llm"
    if not llm_suggestions:
        mode = "rules"
        missing = extracted["missing_keywords"][:5]
        llm_suggestions = (
            "- Add measurable impact (APIs shipped, latency, users).\n"
            "- List stack explicitly: Django, DRF, PostgreSQL, Docker.\n"
            f"- Consider adding missing keywords: {', '.join(missing) or 'CI/CD, Redis'}.\n"
            "- Link GitHub repos with short architecture notes."
        )
    return {
        "scores": scores,
        "extracted": extracted,
        "suggestions": llm_suggestions,
        "mode": mode,
    }
