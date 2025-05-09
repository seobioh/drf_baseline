# accounts/urls.py
app_name = 'accounts'

from django.contrib import admin
from django.urls import path

from .views import *

urlpatterns = [
    path("", AccountAPIView.as_view()),
    path("signup", SignUpAPIView.as_view()),
    path("refresh", TokenRefreshAPIView.as_view()),
    path("send-code", SendVerificationCodeAPIView.as_view()),
    path("verify-code", VerifyCodeAPIView.as_view()),
]
