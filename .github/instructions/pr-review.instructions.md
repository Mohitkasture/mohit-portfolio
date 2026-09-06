---
applyTo: "**"
---

You are reviewing a GitHub pull request into `main`. Post the review on the pull request itself.

Required comment shape:

## Summary
What this PR changes.

## What to improve
| Severity | Location | Finding |
|---|---|---|
| High / Medium / Low | `path:line` | Short issue |

## Code suggestions
Concrete patched code for each High/Medium item.

## Merge advice
Safe to merge, or fix first.

Prefer inline comments on the exact lines when a finding is local. Always include one top-level summary comment as well.
