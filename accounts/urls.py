# accounts/urls.py
app_name = 'accounts'

from django.contrib import admin
from django.urls import path

from .views import AccountAPIView, SignUpAPIView, TokenRefreshAPIView, SendVerificationView, CheckVerificationView
from .social import NaverSignUpAPIView, GoogleSignUpAPIView, KakaoSignUpAPIView, AppleSignUpAPIView, NaverSignInAPIView, GoogleSignInAPIView, KakaoSignInAPIView, AppleSignInAPIView

urlpatterns = [
    path("", AccountAPIView.as_view()),
    path("/signup", SignUpAPIView.as_view()),
    path("/refresh", TokenRefreshAPIView.as_view()),
    path("/send-code", SendVerificationView.as_view()),
    path("/verify-code", CheckVerificationView.as_view()),

    path("/naver/signup", NaverSignUpAPIView.as_view()),
    path("/google/signup", GoogleSignUpAPIView.as_view()),
    path("/kakao/signup", KakaoSignUpAPIView.as_view()),
    path("/apple/signup", AppleSignUpAPIView.as_view()),

    path("/naver/signin", NaverSignInAPIView.as_view()),
    path("/google/signin", GoogleSignInAPIView.as_view()),
    path("/kakao/signin", KakaoSignInAPIView.as_view()),
    path("/apple/signin", AppleSignInAPIView.as_view()),
]
