from collections import Counter
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from home.models import AnalyticsEvent, Project
from home.services.llm import chat_completion


def track_event(event_type, *, path="", label="", metadata=None, session_key=""):
    return AnalyticsEvent.objects.create(
        event_type=event_type,
        path=path or "",
        label=label or "",
        metadata=metadata or {},
        session_key=session_key or "",
    )


def summary(days=30):
    since = timezone.now() - timedelta(days=days)
    qs = AnalyticsEvent.objects.filter(created_at__gte=since)
    counts = dict(
        qs.values_list("event_type").annotate(c=Count("id")).values_list("event_type", "c")
    )
    top_projects = (
        qs.filter(event_type="project_view")
        .exclude(label="")
        .values("label")
        .annotate(c=Count("id"))
        .order_by("-c")[:5]
    )
    ai_labels = [
        e.label for e in qs.filter(event_type="ai_query").exclude(label="")[:200]
    ]
    topic_counter = Counter()
    for label in ai_labels:
        for token in label.lower().replace("?", " ").split():
            if len(token) > 3:
                topic_counter[token] += 1

    featured = Project.objects.filter(is_visible=True).order_by("-view_count", "order")[:3]
    return {
        "window_days": days,
        "totals": {
            "page_views": counts.get("page_view", 0),
            "project_views": counts.get("project_view", 0),
            "resume_downloads": counts.get("resume_download", 0),
            "github_clicks": counts.get("github_click", 0),
            "contact_requests": counts.get("contact_submit", 0),
            "ai_queries": counts.get("ai_query", 0),
            "resume_analyses": counts.get("resume_analyze", 0),
        },
        "top_projects": list(top_projects),
        "most_viewed_db": [{"title": p.title, "views": p.view_count} for p in featured],
        "frequent_ai_topics": topic_counter.most_common(8),
    }


def ai_insights(days=30):
    data = summary(days=days)
    totals = data["totals"]
    prompt = (
        "You are an analytics assistant for Mohit Kasture's portfolio. "
        "Write 3 short bullet insights from this JSON. Be specific and factual.\n\n"
        f"{data}"
    )
    text = chat_completion(
        [
            {"role": "system", "content": "Summarize portfolio analytics in 3 concise bullets."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=350,
    )
    if text:
        return {"insights": text, "summary": data}

    # Rule-based fallback
    lines = []
    pv = totals.get("project_views", 0)
    if pv:
        top = data["top_projects"][:1]
        if top:
            lines.append(f"Most viewed project label this period: {top[0]['label']} ({top[0]['c']} views).")
    if totals.get("ai_queries"):
        topics = ", ".join(t for t, _ in data["frequent_ai_topics"][:3]) or "general questions"
        lines.append(f"Visitors asked the AI about: {topics}.")
    lines.append(
        f"Engagement window ({days}d): {totals.get('page_views', 0)} page views, "
        f"{totals.get('resume_downloads', 0)} resume downloads, "
        f"{totals.get('ai_queries', 0)} AI queries."
    )
    return {"insights": "\n".join(f"- {line}" for line in lines), "summary": data}
