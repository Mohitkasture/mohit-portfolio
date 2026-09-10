from django.utils import timezone

from home.models import EvaluationCase, EvaluationRun
from home.services.rag import answer_question


def _keyword_hit_rate(answer, keywords):
    if not keywords:
        return 1.0
    lower = (answer or "").lower()
    hits = sum(1 for kw in keywords if kw and kw.lower() in lower)
    return hits / len(keywords)


def run_evaluation():
    cases = list(EvaluationCase.objects.filter(is_active=True))
    run = EvaluationRun.objects.create(total=len(cases))
    details = []
    passed = 0
    grounded_scores = []
    hallucination_flags = 0

    for case in cases:
        result = answer_question(case.question)
        answer = result.get("answer", "")
        sources = result.get("sources") or []
        hit_rate = _keyword_hit_rate(answer, case.expected_keywords)
        grounded = 1.0 if sources else (0.4 if hit_rate >= 0.5 else 0.0)
        # Hallucination heuristic: claims strong match but no sources and weak keywords
        hallucinated = bool(not sources and hit_rate < 0.25 and len(answer) > 40)
        ok = hit_rate >= 0.5 and not hallucinated
        if ok:
            passed += 1
        if hallucinated:
            hallucination_flags += 1
        grounded_scores.append(grounded)
        details.append(
            {
                "question": case.question,
                "expected_keywords": case.expected_keywords,
                "answer": answer[:500],
                "hit_rate": round(hit_rate, 3),
                "grounded": grounded,
                "hallucinated": hallucinated,
                "passed": ok,
                "mode": result.get("mode"),
                "sources": sources,
            }
        )

    total = max(1, len(cases))
    run.passed = passed
    run.accuracy = passed / total
    run.groundedness = sum(grounded_scores) / total if grounded_scores else 0
    run.hallucination_rate = hallucination_flags / total
    run.details = details
    run.finished_at = timezone.now()
    run.save()
    return run
