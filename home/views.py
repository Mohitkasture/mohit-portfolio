import logging

from django.conf import settings
from django.shortcuts import redirect, render

from home.mailer import send_contact_message
from home.models import (
    Education,
    Experience,
    GitHubRepoCache,
    Project,
    SiteProfile,
    SkillCategory,
)
from home.services import analytics as analytics_service

logger = logging.getLogger(__name__)


def _first_name(name):
    parts = (name or "").split()
    return parts[0] if parts else ""


def _portfolio_context(request, form_error="", form_values=None):
    form_values = form_values or {}
    thanks_name = request.session.pop("contact_thanks_name", "")
    form_success = request.session.pop("contact_form_ok", False) or bool(thanks_name)
    profile = SiteProfile.objects.first()
    return {
        "profile": profile,
        "experiences": Experience.objects.filter(is_visible=True),
        "projects": Project.objects.filter(is_visible=True),
        "skill_categories": SkillCategory.objects.filter(is_visible=True).prefetch_related(
            "skills"
        ),
        "education_items": Education.objects.filter(is_visible=True),
        "github_repos": GitHubRepoCache.objects.filter(is_visible=True, is_fork=False)[:8],
        "contact_name": (profile.full_name if profile else "Mohit Kasture"),
        "contact_email": (
            profile.email if profile and profile.email else settings.CONTACT_EMAIL
        ),
        "site_url": settings.SITE_URL,
        "web3forms_access_key": settings.WEB3FORMS_ACCESS_KEY,
        "form_success": form_success,
        "thanks_name": thanks_name,
        "form_error": form_error,
        "form_name": form_values.get("name", ""),
        "form_email": form_values.get("email", ""),
        "form_message": form_values.get("message", ""),
    }


def index(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        body = request.POST.get("message", "").strip()
        form_values = {"name": name, "email": email, "message": body}
        if name and email and body:
            try:
                send_contact_message(name, email, body)
            except Exception as exc:
                logger.exception("Contact form email failed")
                if settings.DEBUG:
                    form_error = f"Message could not be sent: {exc}"
                else:
                    form_error = (
                        "Message could not be sent. Please try again, or email "
                        f"{settings.CONTACT_EMAIL} directly."
                    )
                return render(
                    request,
                    "home/index.html",
                    _portfolio_context(request, form_error=form_error, form_values=form_values),
                )
            if not request.session.session_key:
                request.session.create()
            analytics_service.track_event(
                "contact_submit",
                path="/",
                label=email[:160],
                session_key=request.session.session_key,
            )
            request.session["contact_thanks_name"] = _first_name(name)
            request.session["contact_form_ok"] = True
            return redirect("/#contact")
        return render(
            request,
            "home/index.html",
            _portfolio_context(
                request,
                form_error="Please fill in all fields.",
                form_values=form_values,
            ),
        )

    if not request.session.session_key:
        request.session.create()
    analytics_service.track_event(
        "page_view",
        path="/",
        label="home",
        session_key=request.session.session_key,
    )
    return render(request, "home/index.html", _portfolio_context(request))
