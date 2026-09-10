#!/usr/bin/env bash
set -o errexit
python manage.py migrate --no-input
python manage.py seed_portfolio
python manage.py collectstatic --no-input
exec gunicorn portfolio_site.wsgi:application --bind 0.0.0.0:${PORT:-8000}
