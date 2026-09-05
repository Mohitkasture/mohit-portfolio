import json
import logging
import os
import urllib.error
import urllib.request

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)

WEB3FORMS_URL = "https://api.web3forms.com/submit"
RESEND_URL = "https://api.resend.com/emails"


def send_contact_message(name, email, body):
    """Send via HTTPS first (Render blocks Gmail SMTP), then local SMTP."""
    if settings.WEB3FORMS_ACCESS_KEY:
        _send_web3forms(name, email, body)
        return
    if settings.RESEND_API_KEY:
        _send_resend(name, email, body)
        return
    if settings.SMTP_USER and settings.SMTP_PASSWORD and not os.environ.get("RENDER"):
        _send_smtp(name, email, body)
        return
    raise RuntimeError("No HTTPS mail provider is configured")


def _post_json(url, payload, headers=None, timeout=12):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(detail or str(exc)) from exc
    return json.loads(raw) if raw else {}


def _send_web3forms(name, email, body):
    result = _post_json(
        WEB3FORMS_URL,
        {
            "access_key": settings.WEB3FORMS_ACCESS_KEY,
            "name": name,
            "email": email,
            "message": body,
            "subject": f"Portfolio message from {name}",
            "from_name": "Mohit Kasture Portfolio",
            "replyto": email,
        },
    )
    if not result.get("success"):
        raise RuntimeError(result.get("message") or "Web3Forms rejected the message")


def _send_resend(name, email, body):
    from_email = settings.DEFAULT_FROM_EMAIL
    if not from_email or from_email.endswith("@localhost"):
        from_email = "Portfolio <onboarding@resend.dev>"
    result = _post_json(
        RESEND_URL,
        {
            "from": from_email,
            "to": [settings.CONTACT_EMAIL],
            "subject": f"Portfolio message from {name}",
            "text": f"From: {name} <{email}>\n\n{body}",
            "reply_to": email,
        },
        headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
    )
    if not result.get("id"):
        raise RuntimeError(result.get("message") or "Resend rejected the message")


def _send_smtp(name, email, body):
    mail = EmailMessage(
        subject=f"Portfolio message from {name}",
        body=f"From: {name} <{email}>\n\n{body}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_EMAIL],
        reply_to=[email],
    )
    mail.send(fail_silently=False)
