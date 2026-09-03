import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

logger = logging.getLogger(__name__)


def _contact_page(request):
    return render(
        request,
        "home/index.html",
        {
            "contact_name": "Mohit Kasture",
            "contact_email": settings.CONTACT_EMAIL,
        },
    )


def index(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        body = request.POST.get("message", "").strip()
        if name and email and body:
            smtp_ready = bool(settings.SMTP_USER and settings.SMTP_PASSWORD)
            if not smtp_ready:
                logger.error("Contact form submitted but SMTP is not configured")
                messages.error(
                    request,
                    f"Message could not be delivered right now. Please email {settings.CONTACT_EMAIL} directly.",
                )
            else:
                mail = EmailMessage(
                    subject=f"Portfolio message from {name}",
                    body=f"From: {name} <{email}>\n\n{body}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.CONTACT_EMAIL],
                    reply_to=[email],
                )
                try:
                    mail.send(fail_silently=False)
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
                    messages.success(
                        request,
                        f"Your message was sent to Mohit Kasture at {settings.CONTACT_EMAIL}. I’ll reply to you soon.",
                    )
        else:
            messages.error(request, "Please fill in all fields.")
        return redirect("/#contact")
    return _contact_page(request)
