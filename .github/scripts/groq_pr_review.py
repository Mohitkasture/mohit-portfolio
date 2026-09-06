#!/usr/bin/env python3
"""Post a Groq AI review comment on a GitHub pull request."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-120b"
MAX_DIFF_CHARS = 80_000


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace")


def message_text(message: dict) -> str:
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(item.get("text") or item.get("content") or "")
            elif isinstance(item, str):
                parts.append(item)
        joined = "".join(parts).strip()
        if joined:
            return joined
    reasoning = message.get("reasoning")
    if isinstance(reasoning, str) and reasoning.strip():
        return reasoning.strip()
    return ""


def main() -> int:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    pr_number = os.environ.get("PR_NUMBER", "").strip()
    if not pr_number:
        print("PR_NUMBER is missing", file=sys.stderr)
        return 1
    if not api_key:
        print("GROQ_API_KEY is not set. Add it in GitHub → Settings → Secrets and variables → Actions.")
        return 0

    diff = run(["gh", "pr", "diff", pr_number])
    if not diff.strip():
        print("No diff to review.")
        return 0
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n\n[diff truncated for the model context window]"

    extra = ""
    prompt_file = os.path.join(".github", "copilot-instructions.md")
    if os.path.isfile(prompt_file):
        extra = open(prompt_file, encoding="utf-8").read().strip()

    system = extra or (
        "You are reviewing a GitHub pull request into main. "
        "Reply with Summary, What to improve (table), Code suggestions, and Merge advice."
    )
    user = (
        "Review this pull request diff. Base branch is main. "
        "Write the review in Markdown for a GitHub PR comment.\n\n"
        f"```diff\n{diff}\n```"
    )

    payload = {
        "model": os.environ.get("GROQ_MODEL", "").strip() or DEFAULT_MODEL,
        "temperature": 0.2,
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    request = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(detail, file=sys.stderr)
        return 1

    choices = data.get("choices") or []
    if not choices:
        print(json.dumps(data)[:2000], file=sys.stderr)
        return 1
    body = message_text(choices[0].get("message") or {})
    if not body:
        print(json.dumps(data)[:2000], file=sys.stderr)
        return 1

    comment = (
        "## AI review (Groq)\n\n"
        f"{body}\n\n"
        "---\n"
        "_Automatic review for pull requests into `main`._\n"
    )
    review_path = "groq-review.md"
    with open(review_path, "w", encoding="utf-8") as handle:
        handle.write(comment)
    subprocess.check_call(["gh", "pr", "comment", pr_number, "--body-file", review_path])
    print("Posted Groq review comment on the pull request.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
