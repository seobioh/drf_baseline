# accounts/views.py
app_name = 'accounts'

import random
import requests
import urllib.parse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.timezone import now

from .task import send_verification_email, send_verification_sms
from .utils import NaverResponse, KakaoResponse, GoogleResponse
from .models import User, Verification, UserSocialAccount
from .serializers import UserSerializer, SignUpSerializer, VerificationCheckSerializer, VerificationRequestSerializer, SocialSignUpSerializer
from .permissions import IsAuthenticated, AllowAny

# User
# <-------------------------------------------------------------------------------------------------------------------------------->
# Sign Up API
class SignUpAPIView(APIView):
    def post(self, request):
        request.data.get("verification_code")
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            response = AuthResponseBuilder(user).with_message("Register successful").build()
            return Response(response, status=status.HTTP_200_OK)
        
        else:
            response_error = {
                "code": 1,
                "message": "Signup failed",
                "errors": serializer.errors,
            }
            return Response(response_error, status=status.HTTP_400_BAD_REQUEST)


# Token Refresh API
class TokenRefreshAPIView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})

        try: 
            serializer.is_valid(raise_exception=True)
            access_token = serializer.validated_data["access"]
            access_token_lifetime = api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()

            token_obj = RefreshToken(refresh_token)
            user_id = token_obj["user_id"]
            user = User.objects.get(id=user_id)
            user.last_access = now()
            user.save(update_fields=["last_access"])
            
            response = {
                "code": 0,
                "access_token": access_token,
                "expires_in": access_token_lifetime
            }
            return Response(response, status=status.HTTP_200_OK)

        except TokenError as error:
            response_error = {
                "code": 1,
                "message": "Authentication failed",
                "errors": str(error),
            }
            return Response(response_error, status=status.HTTP_401_UNAUTHORIZED)
    

# Account Management API (Login, Fetch Info, Update, Delete)
class AccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # Override permission for POST (Sign-In) to allow all users
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return super().get_permissions()
    
    # Get Account Info (Authenticated Users Only)
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)

        # Update last access time
        user.last_access = now()
        user.save(update_fields=["last_access"])

        response = AuthResponseBuilder(user).with_message("Sign In successful").build()
        return Response(response, status=status.HTTP_200_OK)
        
    # Sign-In API (Issue JWT Token)
    def post(self, request):
        user = authenticate(email=request.data.get("email"), password=request.data.get("password"))
        if user is not None:
            serializer = UserSerializer(user)

            # Update last login time
            user.last_access = now()
            user.save(update_fields=["last_access"])

            response = AuthResponseBuilder(user).with_message("Sign In successful").build()
            return Response(response, status=status.HTTP_200_OK)
        
        else:
            response_error = {
                "code": 1,
                "message": "Invalid credentials. Please try again.",
                "errors": {"non_field_errors": ["Invalid email or password."]},
            }     
            return Response(response_error, status=status.HTTP_400_BAD_REQUEST)
        
    # Delete Account API
    def delete(self, request):
        user = request.user  # Authenticated user
        user.delete()

        response = {
            "code": 0,
            "message": "Account deleted successfully"
        }
        return Response(response, status=status.HTTP_202_ACCEPTED)
        
    # Update Account Info API
    def put(self, request):
        user = request.user  # Authenticated user
        serializer = UserSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(last_access=now())
            updated_user = serializer.data

            response = {
                "code": 0,
                "message": "User information updated successfully",
                "user": updated_user,
            }
            return Response(response, status=status.HTTP_200_OK)
        
        else:
            response_error = {
                "code": 1,
                "message": "Validation failed",
                "errors": serializer.errors,
            }     
            return Response(response_error, status=status.HTTP_400_BAD_REQUEST)


# Verification
# <-------------------------------------------------------------------------------------------------------------------------------->
# Send Verification Code API
class SendVerificationView(APIView):
    def post(self, request):
        serializer = VerificationRequestSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"code": 1, "message": "유효성 검사 실패", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        type = serializer.validated_data['type']
        target = serializer.validated_data['target']

        # 6 digits random code
        verification_code = f"{random.randint(0, 999999):06d}"

        # Update or create verification record
        verification, _ = Verification.objects.update_or_create(
            type=type,
            target=target,
            defaults={'verification_code': verification_code, 'created_at': now()}
        )

        # Send verification code
        if type == 'mobile':
            send_verification_sms(target, verification_code)     # send_verification_sms.delay(target, code) for celery
        else:
            send_verification_email(target, verification_code)   # send_verification_email.delay(target, code) for celery

        return Response({"code": 0, "message": "인증번호 발송 완료"}, status=status.HTTP_200_OK)


# Check Verification Code API
class CheckVerificationView(APIView):
    def post(self, request):
        serializer = VerificationCheckSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"code": 1, "message": "유효성 검사 실패", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        target = serializer.validated_data['target']
        code = serializer.validated_data['code']

        # Find verification record by target
        try:
            verification = Verification.objects.get(target=target, code=code)
        except Verification.DoesNotExist:
            return Response({"code": 1, "message": "인증번호 불일치"}, status=status.HTTP_400_BAD_REQUEST)

        if verification.is_expired():
            return Response({"code": 1, "message": "인증번호 만료"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"code": 0, "message": "인증 성공"}, status=status.HTTP_200_OK)
    

# Social API
# <-------------------------------------------------------------------------------------------------------------------------------->
# Naver API
class NaverAPIView(APIView):
    def post(self, request):
        code = request.data.get("code")
        state = request.data.get("state")

        # Code to access token request
        token_request = requests.get(f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={settings.NAVER_CLIENT_ID}&client_secret={settings.NAVER_CLIENT_SECRET}&code={code}&state={state}")
        token_response_json = token_request.json()

        # Error handling for token request
        error = token_response_json.get("error")
        if error:
            error_description = token_response_json.get("error_description", "An error occurred during token acquisition.")
            return Response({"error": error, "error_description": error_description}, status=status.HTTP_400_BAD_REQUEST)

        # Profile request
        naver_access_token = token_response_json.get("access_token")
        if not naver_access_token:
            return Response({"code": 1, "message": "Missing naver_access_token"}, status=status.HTTP_400_BAD_REQUEST)

        # Naver API
        naver_res = requests.post("https://openapi.naver.com/v1/nid/me", headers={"Authorization": f"Bearer {naver_access_token}"})
        if naver_res.status_code != 200:
            return Response({"code": 1, "message": "Failed to get profile from Naver"}, status=status.HTTP_400_BAD_REQUEST)

        naver_response = NaverResponse(naver_res.json())
        if not naver_response.is_valid:
            return Response({"code": 1, "message": "Invalid response from Naver"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 기존 소셜 계정으로 유저 찾기
        try:
            social_account = UserSocialAccount.objects.get(provider='naver', provider_user_id=naver_response.id)
            user = social_account.user
            user.last_access = now()
            user.save(update_fields=["last_access"])
            response = AuthResponseBuilder(user).with_message("Sign In successful").build()
            return Response(response, status=status.HTTP_200_OK)

        # 2. 없으면 회원가입 처리
        except UserSocialAccount.DoesNotExist:
            user_data = naver_response.to_user_data()
            serializer = SocialSignUpSerializer(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
                response = AuthResponseBuilder(user).with_message("Register & Sign In successful").build()
                return Response(response, status=status.HTTP_200_OK)

            else:
                response_error = {
                    "code": 1,
                    "message": "Social sign in failed",
                    "errors": serializer.errors,
                }
                return Response(response_error, status=status.HTTP_400_BAD_REQUEST)


# Google Sign In API
class GoogleAPIView(APIView):
    def post(self, request):
        code = request.data.get("code")
        code = urllib.parse.unquote(code)

        # Code to access token request
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.GOOGLE_CLIENT_KEY,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_CALLBACK_URI,
            'code': code
        }
        token_request = requests.post("https://oauth2.googleapis.com/token", data=token_data)
        token_response_json = token_request.json()

        # Error handling for token request
        error = token_response_json.get("error")
        if error:
            error_description = token_response_json.get("error_description", "An error occurred during token acquisition.")
            return Response({"error": error, "error_description": error_description}, status=status.HTTP_400_BAD_REQUEST)

        # Profile request
        google_access_token = token_response_json.get("access_token")
        if not google_access_token:
            return Response({"code": 1, "message": "Missing google_access_token"}, status=status.HTTP_400_BAD_REQUEST)

        # Google API
        google_res = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": f"Bearer {google_access_token}"})
        if google_res.status_code != 200:
            return Response({"code": 1, "message": "Failed to get profile from Google"}, status=status.HTTP_400_BAD_REQUEST)

        google_response = GoogleResponse(google_res.json())
        if not google_response.is_valid:
            return Response({"code": 1, "message": "Invalid response from Google"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 기존 소셜 계정으로 유저 찾기
        try:
            social_account = UserSocialAccount.objects.get(provider='google', provider_user_id=google_response.id)
            user = social_account.user
            user.last_access = now()
            user.save(update_fields=["last_access"])
            response = AuthResponseBuilder(user).with_message("Sign In successful").build()
            return Response(response, status=status.HTTP_200_OK)

        # 2. 없으면 회원가입처럼 처리
        except UserSocialAccount.DoesNotExist:
            user_data = google_response.to_user_data()
            serializer = SocialSignUpSerializer(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
                response = AuthResponseBuilder(user).with_message("Register & Sign In successful").build()
                return Response(response, status=status.HTTP_200_OK)

            else:
                response_error = {
                    "code": 1,
                    "message": "Social sign in failed",
                    "errors": serializer.errors,
                }
                return Response(response_error, status=status.HTTP_400_BAD_REQUEST)


# Kakao Sign In API
class KakaoAPIView(APIView):
    def post(self, request):
        code = request.data.get("code")

        # Code to access token request
        token_request = requests.get(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={settings.KAKAO_CLIENT_KEY}&redirect_uri={settings.KAKAO_CALLBACK_URI}&code={code}")
        token_response_json = token_request.json()

        # Error handling for token request
        error = token_response_json.get("error")
        if error:
            error_description = token_response_json.get("error_description", "An error occurred during token acquisition.")
            return Response({"error": error, "error_description": error_description}, status=status.HTTP_400_BAD_REQUEST)

        # Profile request
        kakao_access_token = token_response_json.get("access_token")
        if not kakao_access_token:
            return Response({"code": 1, "message": "Missing kakao_access_token"}, status=status.HTTP_400_BAD_REQUEST)

        # Kakao API
        kakao_res = requests.post("https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {kakao_access_token}"})
        if kakao_res.status_code != 200:
            return Response({"code": 1, "message": "Failed to get profile from Kakao"}, status=status.HTTP_400_BAD_REQUEST)

        kakao_response = KakaoResponse(kakao_res.json())
        if not kakao_response.is_valid:
            return Response({"code": 1, "message": "Invalid response from Kakao"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 기존 소셜 계정으로 유저 찾기
        try:
            social_account = UserSocialAccount.objects.get(provider='kakao', provider_user_id=kakao_response.id)
            user = social_account.user
            user.last_access = now()
            user.save(update_fields=["last_access"])
            response = AuthResponseBuilder(user).with_message("Sign In successful").build()
            return Response(response, status=status.HTTP_200_OK)

        # 2. 없으면 회원가입처럼 처리
        except UserSocialAccount.DoesNotExist:
            user_data = kakao_response.to_user_data()
            serializer = SocialSignUpSerializer(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
                response = AuthResponseBuilder(user).with_message("Register & Sign In successful").build()
                return Response(response, status=status.HTTP_200_OK)

            else:
                response_error = {
                    "code": 1,
                    "message": "Social sign in failed",
                    "errors": serializer.errors,
                }
                return Response(response_error, status=status.HTTP_400_BAD_REQUEST)



# Apple Sign In API
class AppleAPIView(APIView):
    def post(self, request):
        pass


# AuthResponse
# <-------------------------------------------------------------------------------------------------------------------------------->
class AuthResponseBuilder:
    def __init__(self, user):
        self.user = user
        self.message = "Success"
        self.code = 0

    def with_message(self, message: str):
        self.message = message
        return self

    def with_code(self, code: int):
        self.code = code
        return self

    def build(self) -> dict:
        token = TokenObtainPairSerializer.get_token(self.user)
        return {
            "code": self.code,
            "user": UserSerializer(self.user).data,
            "message": self.message,
            "token": {
                "access_token": str(token.access_token),
                "refresh_token": str(token),
                "expires_in": token.access_token.lifetime.total_seconds(),
            },
        }
