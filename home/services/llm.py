import json
import logging
from urllib import error, request

from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_MODELS = (
    "qwen/qwen3.8-27b",
    "groq/compound-mini",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
)


def _candidate_models():
    preferred = getattr(settings, "GROQ_MODEL", "").strip()
    models = []
    if preferred:
        models.append(preferred)
    for model in DEFAULT_MODELS:
        if model not in models:
            models.append(model)
    return models


def chat_completion(messages, *, temperature=0.2, max_tokens=700):
    """Call Groq chat completions. Returns None if unavailable."""
    api_key = getattr(settings, "GROQ_API_KEY", "").strip()
    if not api_key:
        return None

    last_error = None
    for model in _candidate_models():
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        req = request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (compatible; MohitPortfolio/1.0)",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            content = (data["choices"][0]["message"].get("content") or "").strip()
            if content:
                return content
            last_error = f"empty content from {model}"
        except error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8")[:300]
            except Exception:
                body = str(exc)
            last_error = f"{exc} {body}"
            # Try next model on model_not_found / access issues
            if exc.code in {400, 404} and "model" in body.lower():
                logger.info("Groq model unavailable (%s), trying next", model)
                continue
            logger.warning("Groq chat failed for %s: %s", model, last_error)
            if exc.code in {401, 403}:
                continue
            return None
        except (error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            logger.warning("Groq chat failed for %s: %s", model, exc)
            continue

    if last_error:
        logger.warning("Groq chat unavailable: %s", last_error)
    return None
