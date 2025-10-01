# accounts/views.py
app_name = 'accounts'

import random
import hmac
import hashlib
import base64

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.timezone import now
from django.db import IntegrityError

from drf_spectacular.utils import extend_schema

from users.utils import ReferralHandler
from server.utils import SuccessResponseBuilder, ErrorResponseBuilder

from .task import send_verification_email, send_verification_sms
from .utils import AuthResponseBuilder, NaverResponse, KakaoResponse, GoogleResponse, PortOneResponse
from .models import User, Verification, UserSocialAccount
from .serializers import UserSerializer, SignUpSerializer, VerificationCheckSerializer, VerificationRequestSerializer, SocialSignUpSerializer
from .permissions import IsAuthenticated, AllowAny
from .schemas import AccountSchema

# User
# <-------------------------------------------------------------------------------------------------------------------------------->
# Sign Up API
class SignUpAPIView(APIView):
    @extend_schema(**AccountSchema.signup())
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():                
            user = serializer.save()

            identity_code = request.data.get("identity_code")
            if identity_code:
                try:
                    port_one_response = PortOneResponse.create_from_code(identity_code, settings.PORTONE_API_SECRET)
                    user.ci = port_one_response.ci
                    user.name = port_one_response.name
                    user.mobile = port_one_response.mobile
                    user.birthday = port_one_response.birthday
                    user.gender = port_one_response.gender
                    user.save()

                except IntegrityError:
                    response = ErrorResponseBuilder().with_message("이미 본인인증된 아이디가 존재합니다.").build()
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

                except Exception as error:
                    user.delete()
                    response = ErrorResponseBuilder().with_message("사용자 인증에 실패했습니다.").with_errors({"error": str(error)}).build()
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

            referral_code = request.data.get("referral_code")
            if referral_code:
                referree = User.objects.filter(referral_code=referral_code).first()
                if referree:
                    referral_handler = ReferralHandler(user, referree)
                    referral_handler.create()

            response = AuthResponseBuilder(user).with_message("회원가입 성공").build()
            return Response(response, status=status.HTTP_200_OK)
        
        else:
            response = ErrorResponseBuilder().with_message("회원가입에 실패했습니다.").with_errors(serializer.errors).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Check Email API
class CheckEmailAPIView(APIView):
    @extend_schema(**AccountSchema.check_email())
    def post(self, request):
        email = request.data.get("email")
        if User.objects.filter(email=email).exists():
            response = ErrorResponseBuilder().with_message("이미 가입된 이메일입니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = SuccessResponseBuilder().with_message("사용 가능한 이메일입니다.").build()
            return Response(response, status=status.HTTP_200_OK)


# Reset Password API
class ResetPasswordAPIView(APIView):
    @extend_schema(**AccountSchema.reset_password())
    def post(self, request):
        try:    
            identity_code = request.data.get("identity_code")
            if identity_code is not None:
                port_one_response = PortOneResponse.create_from_code(identity_code, settings.PORTONE_API_SECRET)
                ci_hash = hashlib.sha256(port_one_response.ci.encode('utf-8')).hexdigest()
                user = User.objects.get(ci_hash=ci_hash)

            else:
                serializer = VerificationCheckSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                target = serializer.validated_data['target']
                verification_code = serializer.validated_data['verification_code']
                verification = Verification.objects.get(target=target, verification_code=verification_code)

                if verification.is_expired():
                    response = ErrorResponseBuilder().with_message("인증번호가 만료되었습니다.").build()
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

                if verification.type == 'mobile':
                    user = User.objects.get(mobile=verification.target)

                else:
                    user = User.objects.get(email=verification.target)

                verification.delete()

            response = AuthResponseBuilder(user).with_message("임시 토큰 발급 성공").build()
            return Response(response, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            response = ErrorResponseBuilder().with_message("사용자를 찾을 수 없습니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Verification.DoesNotExist:
            response = ErrorResponseBuilder().with_message("인증번호가 일치하지 않습니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("처리 중 오류가 발생했습니다.").with_errors({"error": str(e)}).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Token Refresh API
class TokenRefreshAPIView(APIView):
    @extend_schema(**AccountSchema.token_refresh())
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
            
            response = SuccessResponseBuilder().with_message("토큰 갱신 성공").with_data({
                "token": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": access_token_lifetime
                }
            }).build()
            return Response(response, status=status.HTTP_200_OK)

        except TokenError as error:
            response = ErrorResponseBuilder().with_message("토큰 갱신에 실패했습니다.").with_errors({"token_error": str(error)}).build()
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
    

# Account Management API (Login, Fetch Info, Update, Delete)
class AccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # Override permission for POST (Sign-In) to allow all users
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return super().get_permissions()
    
    # Get Account Info (Authenticated Users Only)
    @extend_schema(**AccountSchema.get_account_info())
    def get(self, request):
        user = request.user
        user.last_access = now()
        user.save(update_fields=["last_access"])
        response = AuthResponseBuilder(user).with_message("로그인 성공").build()
        return Response(response, status=status.HTTP_200_OK)
        
    # Sign-In API (Issue JWT Token)
    @extend_schema(**AccountSchema.signin())
    def post(self, request):
        user = authenticate(email=request.data.get("email"), password=request.data.get("password"))
        if user is not None:
            user.last_access = now()
            user.save(update_fields=["last_access"])
            response = AuthResponseBuilder(user).with_message("로그인 성공").build()
            return Response(response, status=status.HTTP_200_OK)
        
        else:
            response = ErrorResponseBuilder().with_message("잘못된 인증 정보입니다. 다시 시도해주세요.").with_errors({"non_field_errors": ["잘못된 이메일 또는 비밀번호입니다."]}).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
    # Delete Account API
    @extend_schema(**AccountSchema.delete_account())
    def delete(self, request):
        user = request.user  # Authenticated user
        user.delete()

        response = SuccessResponseBuilder().with_message("계정 삭제 성공").build()
        return Response(response, status=status.HTTP_202_ACCEPTED)
        
    # Update Account Info API
    @extend_schema(**AccountSchema.update_account())
    def put(self, request):
        user = request.user  # Authenticated user
        serializer = UserSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(last_access=now())
            updated_user = serializer.data

            response = SuccessResponseBuilder().with_message("사용자 정보 수정 성공").with_data({"user": updated_user}).build()
            return Response(response, status=status.HTTP_200_OK)
        
        else:
            response = ErrorResponseBuilder().with_message("사용자 정보 수정에 실패했습니다.").with_errors(serializer.errors).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Verification
# <-------------------------------------------------------------------------------------------------------------------------------->
# Send Verification Code API
class SendVerificationView(APIView):
    @extend_schema(**AccountSchema.request_verification())
    def post(self, request):
        serializer = VerificationRequestSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)

        except Exception as e:
            response = ErrorResponseBuilder().with_message("인증번호 요청에 실패했습니다.").with_errors(serializer.errors).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        type = serializer.validated_data['type']
        target = serializer.validated_data['target']
        check_unique = request.data.get('check_unique')

        # Send verification code
        if type == 'mobile':
            if check_unique:
                if User.objects.filter(mobile=target).exists():
                    response = ErrorResponseBuilder().with_message("이미 가입된 전화번호입니다.").build()
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                if not User.objects.filter(mobile=target).exists():
                    response = ErrorResponseBuilder().with_message("가입되지 않은 전화번호입니다.").build()
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

            # Update or create verification record
            verification_code = f"{random.randint(0, 999999):06d}"
            Verification.objects.update_or_create(
                type=type,
                target=target,
                defaults={'verification_code': verification_code, 'created_at': now()}
            )
            send_verification_sms(target, verification_code)     # send_verification_sms.delay(target, verification_code) for celery

        else:
            if check_unique:
                if User.objects.filter(email=target).exists():
                    response = ErrorResponseBuilder().with_message("이미 가입된 이메일입니다.").build()
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

            else:
                if not User.objects.filter(email=target).exists():
                    response = ErrorResponseBuilder().with_message("가입되지 않은 이메일입니다.").build()
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

            # Update or create verification record
            verification_code = f"{random.randint(0, 999999):06d}"
            Verification.objects.update_or_create(
                type=type,
                target=target,
                defaults={'verification_code': verification_code, 'created_at': now()}
            )
            send_verification_email(target, verification_code)   # send_verification_email.delay(target, verification_code) for celery

        response = SuccessResponseBuilder().with_message("인증번호 발송 완료").build()
        return Response(response, status=status.HTTP_200_OK)


# Check Verification Code API
class CheckVerificationView(APIView):
    @extend_schema(**AccountSchema.check_verification())
    def post(self, request):
        serializer = VerificationCheckSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("인증번호 확인에 실패했습니다.").with_errors(serializer.errors).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        target = serializer.validated_data['target']
        verification_code = serializer.validated_data['verification_code']

        # Find verification record by target
        try:
            verification = Verification.objects.get(target=target, verification_code=verification_code)
        except Verification.DoesNotExist:
            response = ErrorResponseBuilder().with_message("인증번호가 일치하지 않습니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if verification.is_expired():
            response = ErrorResponseBuilder().with_message("인증번호가 만료되었습니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        response = SuccessResponseBuilder().with_message("인증 성공").build()
        return Response(response, status=status.HTTP_200_OK)
    

# Social API
# <-------------------------------------------------------------------------------------------------------------------------------->
# Naver API
class NaverAPIView(APIView):
    @extend_schema(**AccountSchema.naver_auth())
    def post(self, request):
        code = request.data.get("code")
        state = request.data.get("state")
        
        try:
            # NaverResponse 객체를 통해 네이버 인증 처리
            naver_response = NaverResponse.create_from_code(code, state, settings.NAVER_CLIENT_ID, settings.NAVER_CLIENT_SECRET)
            
            # 1. 기존 소셜 계정으로 유저 찾기
            social_account = UserSocialAccount.objects.get(provider='naver', provider_user_id=naver_response.id)
            user = social_account.user
            user.last_access = now()
            user.save(update_fields=["last_access"])
            response = AuthResponseBuilder(user).with_message("네이버 로그인 성공").build()
            return Response(response, status=status.HTTP_200_OK)

        # 2. 없으면 회원가입 처리
        except UserSocialAccount.DoesNotExist:
            user_data = naver_response.to_user_data()
            serializer = SocialSignUpSerializer(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
                response = AuthResponseBuilder(user).with_message("회원가입 성공").build()
                return Response(response, status=status.HTTP_200_OK)

            else:
                response = ErrorResponseBuilder().with_message("네이버 회원가입에 실패했습니다.").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError as error:
            response = ErrorResponseBuilder().with_message("네이버 로그인에 실패했습니다.").with_errors({"error": str(error)}).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Google Sign In API
class GoogleAPIView(APIView):
    @extend_schema(**AccountSchema.google_auth())
    def post(self, request):
        code = request.data.get("code")
        
        try:
            # GoogleResponse 객체를 통해 구글 인증 처리
            google_response = GoogleResponse.create_from_code(code, settings.GOOGLE_CLIENT_KEY, settings.GOOGLE_CLIENT_SECRET, settings.GOOGLE_CALLBACK_URI)
            
            # 1. 기존 소셜 계정으로 유저 찾기
            social_account = UserSocialAccount.objects.get(provider='google', provider_user_id=google_response.id)
            user = social_account.user
            user.last_access = now()
            user.save(update_fields=["last_access"])
            response = AuthResponseBuilder(user).with_message("구글 로그인 성공").build()
            return Response(response, status=status.HTTP_200_OK)

        # 2. 없으면 회원가입처럼 처리
        except UserSocialAccount.DoesNotExist:
            user_data = google_response.to_user_data()
            serializer = SocialSignUpSerializer(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
                response = AuthResponseBuilder(user).with_message("회원가입 성공").build()
                return Response(response, status=status.HTTP_200_OK)

            else:
                response = ErrorResponseBuilder().with_message("구글 회원가입에 실패했습니다.").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError as error:
            response = ErrorResponseBuilder().with_message("구글 로그인에 실패했습니다.").with_errors({"error": str(error)}).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Kakao Sign In API
class KakaoAPIView(APIView):
    @extend_schema(**AccountSchema.kakao_auth())
    def post(self, request):
        code = request.data.get("code")
        
        try:
            # KakaoResponse 객체를 통해 카카오 인증 처리
            kakao_response = KakaoResponse.create_from_code(code, settings.KAKAO_CLIENT_KEY, settings.KAKAO_CALLBACK_URI)
            
            # 1. 기존 소셜 계정으로 유저 찾기
            social_account = UserSocialAccount.objects.get(provider='kakao', provider_user_id=kakao_response.id)
            user = social_account.user
            user.last_access = now()
            user.save(update_fields=["last_access"])
            response = AuthResponseBuilder(user).with_message("카카오 로그인 성공").build()
            return Response(response, status=status.HTTP_200_OK)

        # 2. 없으면 회원가입처럼 처리
        except UserSocialAccount.DoesNotExist:
            user_data = kakao_response.to_user_data()
            serializer = SocialSignUpSerializer(data=user_data)
            if serializer.is_valid():
                user = serializer.save()
                response = AuthResponseBuilder(user).with_message("회원가입 성공").build()
                return Response(response, status=status.HTTP_200_OK)

            else:
                response = ErrorResponseBuilder().with_message("카카오 회원가입에 실패했습니다.").with_errors(serializer.errors).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError as error:
            response = ErrorResponseBuilder().with_message("카카오 로그인에 실패했습니다.").with_errors({"error": str(error)}).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Apple Sign In API
class AppleAPIView(APIView):
    @extend_schema(**AccountSchema.apple_auth())
    def post(self, request):
        pass


# Authentication API
# <-------------------------------------------------------------------------------------------------------------------------------->
# PortOne API
class PortOneAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**AccountSchema.portone_verification())
    def post(self, request):
        identity_code = request.data.get("identity_code")

        if not identity_code:
            response = ErrorResponseBuilder().with_message("identity_code가 필요합니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user

            if user.ci:
                response = ErrorResponseBuilder().with_message("이미 본인인증이 완료된 유저입니다.").build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            port_one_response = PortOneResponse.create_from_code(identity_code, settings.PORTONE_API_SECRET)

            user.ci = port_one_response.ci
            user.name = port_one_response.name
            user.mobile = port_one_response.mobile
            user.birthday = port_one_response.birthday
            user.gender = port_one_response.gender
            user.save()

            response = AuthResponseBuilder(user).with_message("본인인증 성공").build()
            return Response(response, status=status.HTTP_200_OK)

        except IntegrityError:
            response = ErrorResponseBuilder().with_message("이미 본인인증된 아이디가 존재합니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            response = ErrorResponseBuilder().with_message("본인인증에 실패했습니다.").with_errors({"error": str(error)}).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)