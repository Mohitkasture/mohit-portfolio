from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render


def index(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        body = request.POST.get("message", "").strip()
        if name and email and body:
            send_mail(
                subject=f"Portfolio message from {name}",
                message=f"From: {name} <{email}>\n\n{body}",
                from_email=None,
                recipient_list=["mkymohitkumaryadav0@gmail.com"],
                fail_silently=True,
            )
            messages.success(request, "Thanks — I’ll get back to you.")
        else:
            messages.error(request, "Please fill in all fields.")
        return redirect("/#contact")
    return render(request, "home/index.html")
