#!/usr/bin/env python3
"""Post a Groq AI review on a GitHub pull request (Critical / Major / Minor)."""

from __future__ import annotations

import json
import os
import subprocess
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
MAX_DIFF_CHARS = 8000
GITHUB_API = "https://api.github.com"
SHORT_PROMPT = """
You are a GitHub pull-request reviewer. Review ONLY the diff. Be specific.

Reply in Markdown using EXACTLY these headings:

## Summary
3 short bullets: what this PR changes.

## Critical
Blocking bugs, security, or broken behavior.
If none, write: None.
For each issue:
- **Issue:** one sentence
- **File:** `path`
- **Suggested fix:** a fenced code block with the corrected code (required)

## Major
Important quality/bugs that should be fixed before merge.
If none, write: None.
For each issue:
- **Issue:** one sentence
- **File:** `path`
- **Suggested fix:** a fenced code block with the corrected code (required)

## Minor
Small nits. Bullets only. No code unless one line.

## Merge advice
One line: Safe to merge, or Fix Critical/Major first.

Do not invent files that are not in the diff. Do not use High/Medium/Low.
""".strip()


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


def wrap_review(raw: str, model: str) -> str:
    body = raw.strip()
    if "## Summary" not in body:
        body = "## Summary\n\n" + body
    return (
        "## AI review (Groq)\n\n"
        "Issues are grouped as **Critical**, **Major**, and **Minor**.\n"
        "For **Critical** and **Major**, copy the **suggested fix** into the PR "
        "(or use GitHub Copilot **Fix with AI** on that snippet).\n\n"
        f"{body}\n\n"
        "---\n"
        f"_Automatic review for PRs into `main` · `{model}`._\n"
    )


def write_review_file(body: str) -> str:
    path = os.path.abspath("groq-review.md")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(body)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(body)
            handle.write("\n")
    return path


def post_via_gh(pr_number: str, body_path: str) -> None:
    env = os.environ.copy()
    if not env.get("GH_TOKEN") and env.get("GITHUB_TOKEN"):
        env["GH_TOKEN"] = env["GITHUB_TOKEN"]
    subprocess.check_call(
        ["gh", "pr", "comment", pr_number, "--body-file", body_path],
        env=env,
    )


def post_issue_comment(repo: str, pr_number: str, token: str, body: str) -> None:
    status, text = http_json(
        f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments",
        method="POST",
        headers=github_headers(token),
        payload={"body": body},
    )
    if status >= 400:
        raise RuntimeError(f"Could not comment on PR ({status}): {text[:800]}")


def post_pr_review(
    repo: str,
    pr_number: str,
    token: str,
    body: str,
    commit_id: str,
) -> None:
    payload = {"body": body, "event": "COMMENT"}
    if commit_id:
        payload["commit_id"] = commit_id
    status, text = http_json(
        f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/reviews",
        method="POST",
        headers=github_headers(token),
        payload=payload,
    )
    if status >= 400:
        raise RuntimeError(f"Could not create PR review ({status}): {text[:800]}")


def groq_review(api_key: str, model: str, prompt: str, diff: str) -> str:
    payload = {
        "model": model,
        "max_completion_tokens": 1600,
        "messages": [
            {
                "role": "user",
                "content": f"{prompt}\n\nPR diff:\n```diff\n{diff}\n```",
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


def model_list(requested: str) -> list[str]:
    models = []
    if requested and requested not in UNAVAILABLE_MODELS:
        models.append(requested)
    for model in DEFAULT_MODELS:
        if model not in models:
            models.append(model)
    return models


def publish(repo: str, pr_number: str, token: str, commit_id: str, body: str) -> None:
    path = write_review_file(body)
    errors = []
    try:
        post_via_gh(pr_number, path)
        print("Posted PR conversation comment with gh.")
    except Exception as exc:
        errors.append(f"gh pr comment: {exc}")
        print(exc, file=sys.stderr)
    try:
        post_pr_review(repo, pr_number, token, body, commit_id)
        print("Posted GitHub pull request review.")
    except Exception as exc:
        errors.append(f"reviews API: {exc}")
        print(exc, file=sys.stderr)
    try:
        post_issue_comment(repo, pr_number, token, body)
        print("Posted GitHub issues comment.")
    except Exception as exc:
        errors.append(f"issues API: {exc}")
        print(exc, file=sys.stderr)
    if len(errors) == 3:
        raise RuntimeError("Failed to post review to GitHub:\n" + "\n".join(errors))


def main() -> int:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    pr_number = os.environ.get("PR_NUMBER", "").strip()
    commit_id = os.environ.get("HEAD_SHA", "").strip()
    requested_model = os.environ.get("GROQ_MODEL", "").strip()

    if not pr_number or not repo or not token:
        print("PR_NUMBER, GITHUB_REPOSITORY, or GITHUB_TOKEN is missing.", file=sys.stderr)
        return 1

    if not api_key:
        publish(
            repo,
            pr_number,
            token,
            commit_id,
            "## AI review (Groq)\n\n"
            "Review did not run: GitHub secret `GROQ_API_KEY` is missing.\n\n"
            "Add it under **Settings → Secrets and variables → Actions**.\n",
        )
        print("GROQ_API_KEY is not set.", file=sys.stderr)
        return 1

    try:
        diff = fetch_pr_diff(repo, pr_number, token)
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1

    if not diff.strip():
        publish(
            repo,
            pr_number,
            token,
            commit_id,
            "## AI review (Groq)\n\nNo file diff was found on this pull request.\n",
        )
        return 0

    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n\n[diff truncated to fit Groq token limit]"

    last_error = None
    review = None
    used_model = model_list(requested_model)[0]
    for model in model_list(requested_model):
        try:
            print(f"Trying Groq model {model}")
            review = groq_review(api_key, model, SHORT_PROMPT, diff)
            used_model = model
            break
        except Exception as exc:
            last_error = exc
            print(exc, file=sys.stderr)

    if not review:
        error_text = str(last_error or "Unknown Groq error")
        publish(
            repo,
            pr_number,
            token,
            commit_id,
            "## AI review (Groq)\n\n"
            "The review job ran, but Groq did not return a review.\n\n"
            f"```\n{error_text[:1500]}\n```\n",
        )
        print(error_text, file=sys.stderr)
        return 1

    body = wrap_review(review, used_model)
    print(body[:1500])
    publish(repo, pr_number, token, commit_id, body)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"Unhandled error: {exc}", file=sys.stderr)
        sys.exit(1)
