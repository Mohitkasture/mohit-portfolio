import math
import re
from collections import Counter

from home.models import Education, Experience, KnowledgeChunk, Project, SiteProfile, Skill
from home.services.llm import chat_completion

TOKEN_RE = re.compile(r"[a-z0-9+#.]{2,}", re.I)
STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "for",
    "is",
    "are",
    "was",
    "were",
    "be",
    "as",
    "at",
    "by",
    "from",
    "with",
    "about",
    "into",
    "his",
    "her",
    "their",
    "my",
    "your",
    "me",
    "you",
    "he",
    "she",
    "it",
    "this",
    "that",
    "what",
    "which",
    "who",
    "whom",
    "tell",
    "please",
    "does",
    "do",
    "did",
    "has",
    "have",
    "had",
}


def tokenize(text):
    return [t.lower() for t in TOKEN_RE.findall(text or "") if t.lower() not in STOPWORDS]


def _vector(text):
    return Counter(tokenize(text))


def _cosine(a, b):
    if not a or not b:
        return 0.0
    keys = set(a) | set(b)
    dot = sum(a[k] * b[k] for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if not na or not nb:
        return 0.0
    return dot / (na * nb)


INTENT_SOURCE_TYPES = {
    "projects": {"project"},
    "skills": {"skill", "profile"},
    "experience": {"experience", "profile"},
    "education": {"education", "profile"},
    "location": {"profile", "experience"},
    "about": {"profile", "experience"},
    "general": set(),
}


def retrieve(question, *, top_k=5, intent=None):
    qvec = _vector(question)
    q_lower = (question or "").lower()
    preferred = INTENT_SOURCE_TYPES.get(intent or "", set())
    scored = []
    for chunk in KnowledgeChunk.objects.filter(is_active=True):
        blob = f"{chunk.title} {chunk.content} {' '.join(chunk.keywords or [])}"
        score = _cosine(qvec, _vector(blob))
        for kw in chunk.keywords or []:
            if kw and kw.lower() in q_lower:
                score += 0.15
        if preferred:
            if chunk.source_type in preferred:
                score += 0.25
            else:
                score *= 0.45
        # Meta/custom engineering notes should not dominate normal Q&A
        if chunk.source_type == "custom":
            if not any(w in q_lower for w in ("rag", "assistant", "portfolio platform", "evaluation")):
                score *= 0.35
        if score > 0.08:
            scored.append((score, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    if not scored:
        return []
    top_score = scored[0][0]
    # Keep only sources that actually helped answer the question
    relevant = [(s, c) for s, c in scored if s >= max(0.12, top_score * 0.55)]
    return relevant[:top_k]


SYSTEM_PROMPT = """You are "Ask Mohit AI" on Mohit Kasture's developer portfolio.
Speak like a friendly, sharp human — short and natural, not corporate or robotic.
Answer ONLY from the provided portfolio knowledge context.
Use 1-4 short sentences, or a brief bullet list when listing items.
Never say "knowledge base", "virtual assistant", or dump engineering/meta notes about how this chat works.
For greetings or "what's your name": reply warmly in one short line, say you are Ask Mohit AI, then invite a question about Mohit's projects, skills, or experience.
If the context lacks the answer, say you do not have that information.
Stay factual. Do not invent employers, projects, or skills.
"""


def _intent(question):
    q = (question or "").lower().strip()
    if _is_smalltalk(q):
        return "smalltalk"
    if any(w in q for w in ("project", "built", "flowcreator", "meditation", "portfolio platform")):
        return "projects"
    if any(w in q for w in ("skill", "technolog", "stack", "django", "python", "know")):
        return "skills"
    if any(
        w in q
        for w in (
            "experience",
            "work",
            "job",
            "appunik",
            "intern",
            "company",
            "role",
            "roll",
            "current",
            "employer",
        )
    ):
        return "experience"
    if any(w in q for w in ("educat", "degree", "mca", "college", "university")):
        return "education"
    if any(w in q for w in ("where", "location", "city", "based", "live", "ahmedabad")):
        return "location"
    if any(w in q for w in ("who", "about", "mohit", "yourself", "bio")):
        return "about"
    return "general"


def _is_smalltalk(question):
    q = (question or "").lower().strip()
    if not q:
        return False
    greetings = ("hi", "hello", "hey", "yo", "hola", "namaste", "good morning", "good evening")
    identity = (
        "your name",
        "who are you",
        "what are you",
        "what's your name",
        "whats your name",
    )
    if any(phrase in q for phrase in identity):
        return True
    # Pure greeting, or greeting + short chitchat ("hi what is your name" already covered)
    tokens = tokenize(q)
    if len(tokens) <= 4 and any(q == g or q.startswith(g + " ") or q.startswith(g + "!") for g in greetings):
        return True
    if q.rstrip("!?.") in greetings:
        return True
    return False


def _smalltalk_reply(question):
    q = (question or "").lower()
    if any(p in q for p in ("your name", "who are you", "what are you")):
        return (
            "Hey — I'm Ask Mohit AI. I can walk you through Mohit Kasture's projects, "
            "skills, and experience. What do you want to know?"
        )
    return (
        "Hey! I'm Ask Mohit AI. Ask me anything about Mohit's projects, skills, "
        "or experience."
    )


def synthesize_answer(question):
    """Deterministic natural-language answer from CMS when LLM is unavailable."""
    profile = SiteProfile.objects.first()
    intent = _intent(question)
    name = profile.full_name if profile else "Mohit Kasture"

    if intent == "smalltalk":
        return _smalltalk_reply(question)

    if intent == "about" or intent == "location":
        parts = [f"{name} is a Python & Django backend developer."]
        if profile:
            if profile.location:
                parts.append(f"He is based in {profile.location}.")
            if profile.current_role:
                parts.append(profile.current_role)
            if profile.focus_line:
                parts.append(f"Focus: {profile.focus_line}.")
        return " ".join(parts)

    if intent == "skills":
        skills = list(
            Skill.objects.filter(is_visible=True, category__is_visible=True)
            .select_related("category")
            .order_by("category__order", "order")
        )
        if not skills:
            return f"{name} works with Python, Django, Django REST Framework, and PostgreSQL."
        by_cat = {}
        for skill in skills:
            by_cat.setdefault(skill.category.name, []).append(skill.name)
        lines = [f"{name}'s core skills include:"]
        for cat, names in by_cat.items():
            lines.append(f"• {cat}: {', '.join(names)}")
        return "\n".join(lines)

    if intent == "experience":
        experiences = list(Experience.objects.filter(is_visible=True)[:4])
        if not experiences:
            return f"{name} currently works as a Python Developer at AppUnik in Ahmedabad."
        lines = [f"{name}'s experience:"]
        for exp in experiences:
            lines.append(f"• {exp.title} at {exp.company} ({exp.period})")
        return "\n".join(lines)

    if intent == "education":
        items = list(Education.objects.filter(is_visible=True)[:4])
        if not items:
            return f"{name} completed an MCA and a BSc in Bhopal."
        lines = [f"{name}'s education:"]
        for edu in items:
            lines.append(f"• {edu.degree} — {edu.institution} ({edu.period})")
        return "\n".join(lines)

    if intent == "projects":
        projects = list(Project.objects.filter(is_visible=True)[:5])
        q = (question or "").lower()
        focused = [p for p in projects if p.title.lower() in q or p.slug.replace("-", " ") in q]
        chosen = focused or projects
        if not chosen:
            return "No projects are published in the portfolio yet."
        lines = []
        for project in chosen[:3]:
            stack = ", ".join((project.tech_stack or [])[:6])
            blurb = project.tagline or project.overview or project.contribution
            lines.append(f"• {project.title}: {blurb}")
            if stack:
                lines.append(f"  Stack: {stack}")
        header = f"{name} has built these projects:" if not focused else f"About {chosen[0].title}:"
        return header + "\n" + "\n".join(lines)

    # general: mix of profile + top projects
    projects = list(Project.objects.filter(is_visible=True)[:3])
    titles = ", ".join(p.title for p in projects) if projects else "backend and AI projects"
    location = profile.location if profile and profile.location else "Ahmedabad"
    role = profile.current_role if profile and profile.current_role else "Python/Django developer"
    return (
        f"{name} is a {role.rstrip('.')}. Based in {location}. "
        f"Highlighted work includes {titles}. "
        "Ask about his skills, experience, or a specific project for more detail."
    )


def answer_question(question):
    if _is_smalltalk(question):
        return {
            "answer": _smalltalk_reply(question),
            "sources": [],
            "mode": "smalltalk",
        }

    intent = _intent(question)
    hits = retrieve(question, top_k=3, intent=intent)
    context_parts = []
    sources = []
    for score, chunk in hits:
        context_parts.append(f"### {chunk.title}\n{chunk.content}")
        sources.append(
            {
                "title": chunk.title,
                "source_type": chunk.source_type,
                "score": round(score, 3),
            }
        )
    context = "\n\n".join(context_parts) if context_parts else "No relevant portfolio context found."

    llm_answer = chat_completion(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Portfolio knowledge:\n{context}\n\n"
                    f"Visitor question: {question}\n\n"
                    "Give a direct helpful answer. Do not mention knowledge base or retrieval."
                ),
            },
        ]
    )

    if llm_answer:
        return {
            "answer": llm_answer,
            "sources": sources,
            "mode": "rag+llm",
        }

    synthesized = synthesize_answer(question)
    return {
        "answer": synthesized,
        "sources": sources,
        "mode": "rag-fallback",
    }


def semantic_project_search(query):
    qvec = _vector(query)
    results = []
    for project in Project.objects.filter(is_visible=True):
        blob = " ".join(
            [
                project.title,
                project.tagline,
                project.overview,
                project.contribution,
                project.technical,
                " ".join(project.tech_stack or []),
                " ".join(project.bullets or []),
            ]
        )
        score = _cosine(qvec, _vector(blob))
        q_lower = query.lower()
        for tech in project.tech_stack or []:
            if tech.lower() in q_lower:
                score += 0.2
        if score > 0.08:
            results.append((score, project))
    results.sort(key=lambda item: item[0], reverse=True)
    return results
