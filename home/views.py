import logging

from django.conf import settings
from django.shortcuts import redirect, render

from home.mailer import send_contact_message

logger = logging.getLogger(__name__)


def _first_name(name):
    parts = (name or "").split()
    return parts[0] if parts else ""


def _contact_page(request, form_error="", form_values=None):
    form_values = form_values or {}
    thanks_name = request.session.pop("contact_thanks_name", "")
    form_success = request.session.pop("contact_form_ok", False) or bool(thanks_name)
    return render(
        request,
        "home/index.html",
        {
            "contact_name": "Mohit Kasture",
            "contact_email": settings.CONTACT_EMAIL,
            "site_url": settings.SITE_URL,
            "web3forms_access_key": settings.WEB3FORMS_ACCESS_KEY,
            "form_success": form_success,
            "thanks_name": thanks_name,
            "form_error": form_error,
            "form_name": form_values.get("name", ""),
            "form_email": form_values.get("email", ""),
            "form_message": form_values.get("message", ""),
        },
    )


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
                return _contact_page(request, form_error=form_error, form_values=form_values)
            request.session["contact_thanks_name"] = _first_name(name)
            request.session["contact_form_ok"] = True
            return redirect("/#contact")
        return _contact_page(
            request,
            form_error="Please fill in all fields.",
            form_values=form_values,
        )
    return _contact_page(request)
