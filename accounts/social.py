# accounts/social.py
app_name = 'accounts'

import random

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from django.contrib.auth import authenticate
from django.utils.timezone import now

# Social SignUp API
# <-------------------------------------------------------------------------------------------------------------------------------->
# Naver SignUp API
class NaverSignUpAPIView(APIView):
    def post(self, request):
        pass


# Google SignUp API
class GoogleSignUpAPIView(APIView):
    def post(self, request):
        pass


# Kakao SignUp API
class KakaoSignUpAPIView(APIView):
    def post(self, request):
        pass


# Apple SignUp API
class AppleSignUpAPIView(APIView):
    def post(self, request):
        pass



# Social SignIn API
# <-------------------------------------------------------------------------------------------------------------------------------->
# Naver SignIn API
class NaverSignInAPIView(APIView):
    def post(self, request):
        pass


# Google SignIn API
class GoogleSignInAPIView(APIView):
    def post(self, request):
        pass


# Kakao SignIn API
class KakaoSignInAPIView(APIView):
    def post(self, request):
        pass


# Apple SignIn API
class AppleSignInAPIView(APIView):
    def post(self, request):
        pass


