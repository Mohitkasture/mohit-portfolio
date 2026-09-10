import json
import logging
from urllib import error, request

from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from home.models import GitHubRepoCache, SiteProfile

logger = logging.getLogger(__name__)


def _github_username():
    profile = SiteProfile.objects.first()
    if profile and profile.github_username:
        return profile.github_username
    return getattr(settings, "GITHUB_USERNAME", "Mohit-flowcreafter")


def fetch_repos(username=None):
    username = username or _github_username()
    url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "mohit-portfolio",
    }
    token = getattr(settings, "GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = request.Request(url, headers=headers)
    try:
        with request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning("GitHub fetch failed: %s", exc)
        return []


def sync_github_repos(username=None):
    username = username or _github_username()
    repos = fetch_repos(username=username)
    synced = 0
    seen_ids = []
    for item in repos:
        if not isinstance(item, dict) or item.get("private"):
            continue
        pushed = parse_datetime(item.get("pushed_at") or "") if item.get("pushed_at") else None
        if pushed and timezone.is_naive(pushed):
            pushed = timezone.make_aware(pushed, timezone.utc)
        GitHubRepoCache.objects.update_or_create(
            github_id=item["id"],
            defaults={
                "name": item.get("name") or "",
                "full_name": item.get("full_name") or "",
                "description": item.get("description") or "",
                "html_url": item.get("html_url") or "",
                "language": item.get("language") or "",
                "stars": item.get("stargazers_count") or 0,
                "forks": item.get("forks_count") or 0,
                "topics": item.get("topics") or [],
                "pushed_at": pushed,
                "is_fork": bool(item.get("fork")),
                "is_visible": True,
            },
        )
        seen_ids.append(item["id"])
        synced += 1
    # Hide repos that no longer belong to the configured profile
    if seen_ids:
        GitHubRepoCache.objects.exclude(github_id__in=seen_ids).update(is_visible=False)
    else:
        GitHubRepoCache.objects.update(is_visible=False)
    return synced
