# accounts/tasks.py
app_name = "accounts"

from django.tasks import task

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@task
def send_verification_email(email: str, code: str) -> bool:
    subject = "Your Verification Code"

    html_content = render_to_string("verification_email.html", {"code": code})

    # fallback text (메일 클라이언트가 HTML 지원 안할 때)
    text_content = f"Your verification code is: {code}"

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email="VAHANA <noreply@vahana.kr>",
        to=[email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=True)

    return True


@task
def send_verification_sms(mobile: str, code: str) -> bool:
    # TODO: Implement SMS verification provider logic (e.g. Aligo, CoolSMS, Twilio, etc.)
    return True
