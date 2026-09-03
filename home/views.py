import smtplib

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render


def index(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        body = request.POST.get("message", "").strip()
        if name and email and body:
            mail = EmailMessage(
                subject=f"Portfolio message from {name}",
                body=f"From: {name} <{email}>\n\n{body}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_EMAIL],
                reply_to=[email],
            )
            try:
                mail.send(fail_silently=False)
            except (OSError, smtplib.SMTPException):
                messages.error(
                    request,
                    "Message could not be sent. Please email me directly.",
                )
            else:
                messages.success(request, "Thanks — I’ll get back to you.")
        else:
            messages.error(request, "Please fill in all fields.")
        return redirect("/#contact")
    return render(request, "home/index.html")
