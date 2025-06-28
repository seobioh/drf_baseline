# accounts/task.py
app_name = "accounts"

from celery import shared_task

from django.core.mail import send_mail

@shared_task
def send_verification_email(email, code):
    send_mail(
        subject='Your Verification Code',
        message=f'Your verification code is: {code}',
        from_email='your_email@gmail.com',
        recipient_list=[email],
        fail_silently=True,
    )    
    return True
