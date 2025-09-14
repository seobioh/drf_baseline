# accounts/urls.py
app_name = 'accounts'

from django.contrib import admin
from django.urls import path

from .views import AccountAPIView, SignUpAPIView, CheckEmailAPIView, ResetPasswordAPIView, TokenRefreshAPIView, SendVerificationView, CheckVerificationView
from .views import NaverAPIView, GoogleAPIView, KakaoAPIView, AppleAPIView, PortOneAPIView

urlpatterns = [
    path("", AccountAPIView.as_view()),
    path("/signup", SignUpAPIView.as_view()),
    path("/check-email", CheckEmailAPIView.as_view()),
    path("/reset-password", ResetPasswordAPIView.as_view()),
    path("/refresh", TokenRefreshAPIView.as_view()),
    path("/send-code", SendVerificationView.as_view()),
    path("/verify-code", CheckVerificationView.as_view()),

    path("/naver", NaverAPIView.as_view()),
    path("/google", GoogleAPIView.as_view()),
    path("/kakao", KakaoAPIView.as_view()),
    path("/apple", AppleAPIView.as_view()),

    path("/portone", PortOneAPIView.as_view()),
]