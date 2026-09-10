# Mohit Kasture — Portfolio

Python / Django portfolio with CMS-backed content, REST APIs, RAG assistant, GitHub sync, analytics, resume analyzer, AI evaluation, and an AI game NPC.

## Quick start

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
# set SECRET_KEY / DATABASE_URL / GROQ_API_KEY in .env
python manage.py migrate
python manage.py seed_portfolio
python manage.py sync_github   # optional
python manage.py runserver
```

Admin: `/admin/` · API: `/api/` · JWT login: `POST /api/auth/login/`

## Docker

```bash
docker compose up --build
```

## Key commands

```bash
python manage.py rebuild_knowledge
python manage.py run_ai_eval
python manage.py test
```

## Features

1. Django CMS models + admin for projects, skills, experience, education
2. DRF APIs + JWT for protected writes
3. RAG “Ask Mohit AI” over portfolio knowledge (+ Groq when configured)
4. Semantic project search
5. GitHub repo sync
6. Analytics tracking + admin insights endpoints
7. Resume analyzer (regex rules + LLM suggestions)
8. AI evaluation pipeline (`run_ai_eval`)
9. AI game NPC (Asha)
10. Docker + GitHub Actions CI
