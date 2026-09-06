This is a personal Django 6.1 portfolio site (Python, HTML, CSS, a little JavaScript). Production deploys from the `main` branch on Render.

When you review a pull request on GitHub, always reply on the PR with all four of these:

1. **Summary** — 2–4 sentences in plain English: what changed and why.
2. **What to improve** — a markdown table with columns: Severity, Location (`file:line`), Finding. Sort highest severity first. Use High / Medium / Low.
3. **Code suggestions** — for each High or Medium finding, show the actual replacement code, not only advice.
4. **Merge advice** — one line: safe to merge, or fix first (list the blockers).

Review only the files in the PR diff. Focus on bugs, security (secrets, XSS, contact-form abuse), broken UX, and missing tests. Do not nitpick formatting or demand large refactors.

Key files: `home/views.py` (contact form), `home/mailer.py`, `home/templates/home/`, `home/static/home/`, `portfolio_site/settings.py`.
