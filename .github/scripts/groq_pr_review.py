#!/usr/bin/env python3
"""Post a Groq AI review comment on a GitHub pull request."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODELS = (
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
)
UNAVAILABLE_MODELS = {
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "mixtral-8x7b-32768",
    "llama-2-70b-chat",
}
# Keep well under the 8000 TPM free-tier cap (~4 chars/token).
MAX_DIFF_CHARS = 9000
SHORT_PROMPT = (
    "You review a GitHub pull request into main. Be concise. "
    "Reply with Markdown headings: ## Summary, ## What to improve "
    "(table: Severity | Location | Finding), ## Code suggestions "
    "(only High/Medium, short snippets), ## Merge advice (one line). "
    "Focus on bugs, security, and broken UX. Skip formatting nits."
)
GITHUB_API = "https://api.github.com"


def http_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict | None = None,
    payload: dict | None = None,
    accept: str = "application/json",
    timeout: int = 90,
) -> tuple[int, str]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Accept": accept,
            "User-Agent": "mohit-portfolio-groq-review",
            **({"Content-Type": "application/json"} if payload is not None else {}),
            **(headers or {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def message_text(message: dict) -> str:
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
            elif isinstance(item, str):
                parts.append(item)
        joined = "".join(parts).strip()
        if joined:
            return joined
    reasoning = message.get("reasoning")
    if isinstance(reasoning, str) and reasoning.strip():
        return reasoning.strip()
    return ""


def github_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def fetch_pr_diff(repo: str, pr_number: str, token: str) -> str:
    status, text = http_json(
        f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}",
        headers=github_headers(token),
        accept="application/vnd.github.diff",
    )
    if status >= 400:
        raise RuntimeError(f"Could not read PR diff ({status}): {text[:500]}")
    return text


def post_pr_comment(repo: str, pr_number: str, token: str, body: str) -> None:
    status, text = http_json(
        f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments",
        method="POST",
        headers=github_headers(token),
        payload={"body": body},
    )
    if status >= 400:
        raise RuntimeError(f"Could not comment on PR ({status}): {text[:500]}")


def groq_review(api_key: str, model: str, prompt: str, diff: str) -> str:
    payload = {
        "model": model,
        "max_completion_tokens": 1200,
        "messages": [
            {
                "role": "user",
                "content": f"{prompt}\n\n```diff\n{diff}\n```",
            }
        ],
    }
    status, text = http_json(
        GROQ_URL,
        method="POST",
        headers={"Authorization": f"Bearer {api_key}"},
        payload=payload,
    )
    if status >= 400:
        raise RuntimeError(f"Groq error for {model} ({status}): {text[:800]}")
    data = json.loads(text)
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"Groq returned no choices: {text[:800]}")
    body = message_text(choices[0].get("message") or {})
    if not body:
        raise RuntimeError(f"Groq returned empty content: {text[:800]}")
    return body


def load_prompt() -> str:
    return SHORT_PROMPT


def model_list(requested: str) -> list[str]:
    models = []
    if requested and requested not in UNAVAILABLE_MODELS:
        models.append(requested)
    for model in DEFAULT_MODELS:
        if model not in models:
            models.append(model)
    return models


def main() -> int:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    pr_number = os.environ.get("PR_NUMBER", "").strip()
    requested_model = os.environ.get("GROQ_MODEL", "").strip()

    if not pr_number or not repo or not token:
        print("PR_NUMBER, GITHUB_REPOSITORY, or GITHUB_TOKEN is missing.", file=sys.stderr)
        return 1

    if not api_key:
        message = (
            "## AI review (Groq)\n\n"
            "Review did not run: GitHub secret `GROQ_API_KEY` is missing.\n\n"
            "Add it under **Settings → Secrets and variables → Actions** "
            "(`GROQ_API_KEY`), then push a new commit to this PR.\n"
        )
        try:
            post_pr_comment(repo, pr_number, token, message)
        except Exception as exc:
            print(exc, file=sys.stderr)
        print("GROQ_API_KEY is not set.", file=sys.stderr)
        return 1

    try:
        diff = fetch_pr_diff(repo, pr_number, token)
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1

    if not diff.strip():
        post_pr_comment(
            repo,
            pr_number,
            token,
            "## AI review (Groq)\n\nNo file diff was found on this pull request.\n",
        )
        return 0

    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n\n[diff truncated to fit Groq token limit]"

    models = model_list(requested_model)
    last_error = None
    review = None
    used_model = models[0]
    for model in models:
        try:
            print(f"Trying Groq model {model}")
            review = groq_review(api_key, model, load_prompt(), diff)
            used_model = model
            break
        except Exception as exc:
            last_error = exc
            print(exc, file=sys.stderr)

    if not review:
        error_text = str(last_error or "Unknown Groq error")
        post_pr_comment(
            repo,
            pr_number,
            token,
            "## AI review (Groq)\n\n"
            "The review job ran, but Groq did not return a review.\n\n"
            f"```\n{error_text[:1500]}\n```\n",
        )
        print(error_text, file=sys.stderr)
        return 1

    comment = (
        "## AI review (Groq)\n\n"
        f"{review}\n\n"
        "---\n"
        f"_Automatic review for pull requests into `main` · model `{used_model}`._\n"
    )
    post_pr_comment(repo, pr_number, token, comment)
    print("Posted Groq review comment on the pull request.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"Unhandled error: {exc}", file=sys.stderr)
        sys.exit(1)
