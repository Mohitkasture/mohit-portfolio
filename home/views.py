import logging

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render

from home.mailer import send_contact_message

logger = logging.getLogger(__name__)


def _contact_page(request):
    return render(
        request,
        "home/index.html",
        {
            "contact_name": "Mohit Kasture",
            "contact_email": settings.CONTACT_EMAIL,
            "web3forms_access_key": settings.WEB3FORMS_ACCESS_KEY,
        },
    )


def index(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        body = request.POST.get("message", "").strip()
        if name and email and body:
            try:
                send_contact_message(name, email, body)
            except Exception as exc:
                logger.exception("Contact form email failed")
                if settings.DEBUG:
                    messages.error(request, f"Message could not be sent: {exc}")
                else:
                    messages.error(
                        request,
                        f"Message could not be sent. Please email {settings.CONTACT_EMAIL} directly.",
                    )
            else:
                messages.success(request, "Thanks — I got your message.")
        else:
            messages.error(request, "Please fill in all fields.")
        return redirect("/#contact")
    return _contact_page(request)
