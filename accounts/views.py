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
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.timezone import now
from django.db import IntegrityError

from server.utils import ErrorResponseBuilder

from .task import send_verification_email, send_verification_sms
from .utils import NaverResponse, KakaoResponse, GoogleResponse, PassRequest, PassResponse, PortOneResponse
from .models import User, Verification, UserSocialAccount, PassVerification
from .serializers import UserSerializer, SignUpSerializer, VerificationCheckSerializer, VerificationRequestSerializer, SocialSignUpSerializer
from .permissions import IsAuthenticated, AllowAny

# User
# <-------------------------------------------------------------------------------------------------------------------------------->
# Sign Up API
class SignUpAPIView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():                
            user = serializer.save()

            identity_code = request.data.get("identity_code")
            if identity_code is not None:
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
                    response = ErrorResponseBuilder().with_message("User Verification failed").with_errors({"error": str(error)}).build()
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

            response = AuthResponseBuilder(user).with_message("Register successful").build()
            return Response(response, status=status.HTTP_200_OK)
        
        else:
            response = ErrorResponseBuilder().with_message("Signup failed").with_errors(serializer.errors).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Check Email API
class CheckEmailAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if User.objects.filter(email=email).exists():
            response = ErrorResponseBuilder().with_message("이미 가입된 이메일입니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"code": 0, "message": "사용 가능한 이메일입니다."}, status=status.HTTP_200_OK)


# Reset Password API
class ResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = VerificationCheckSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("유효성 검사 실패").with_errors(serializer.errors).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        target = serializer.validated_data['target']
        verification_code = serializer.validated_data['verification_code']

        # Find verification record by target
        try:
            verification = Verification.objects.get(target=target, verification_code=verification_code)
        except Verification.DoesNotExist:
            response = ErrorResponseBuilder().with_message("인증번호 불일치").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if verification.is_expired():
            response = ErrorResponseBuilder().with_message("인증번호 만료").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if verification.type == 'mobile':
            user = User.objects.get(mobile=verification.target)
        else:
            user = User.objects.get(email=verification.target)

        verification.delete()
        response = AuthResponseBuilder(user).with_message("Verification successful").build()
        return Response(response, status=status.HTTP_200_OK)


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
            response = ErrorResponseBuilder().with_message("Authentication failed").with_errors({"token_error": str(error)}).build()
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
            response = ErrorResponseBuilder().with_message("Invalid credentials. Please try again.").with_errors({"non_field_errors": ["Invalid email or password."]}).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
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
            response = ErrorResponseBuilder().with_message("Validation failed").with_errors(serializer.errors).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Verification
# <-------------------------------------------------------------------------------------------------------------------------------->
# Send Verification Code API
class SendVerificationView(APIView):
    def post(self, request):
        serializer = VerificationRequestSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("유효성 검사 실패").with_errors(serializer.errors).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        type = serializer.validated_data['type']
        target = serializer.validated_data['target']
        check_unique = request.data.get('check_unique')

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
            if check_unique:
                if User.objects.filter(mobile=target).exists():
                    response = ErrorResponseBuilder().with_message("이미 가입된 전화번호입니다.").build()
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

            send_verification_sms(target, verification_code)     # send_verification_sms.delay(target, verification_code) for celery

        else:
            if check_unique:
                if User.objects.filter(email=target).exists():
                    response = ErrorResponseBuilder().with_message("이미 가입된 이메일입니다.").build()
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

            send_verification_email(target, verification_code)   # send_verification_email.delay(target, verification_code) for celery

        return Response({"code": 0, "message": "인증번호 발송 완료"}, status=status.HTTP_200_OK)


# Check Verification Code API
class CheckVerificationView(APIView):
    def post(self, request):
        serializer = VerificationCheckSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            response = ErrorResponseBuilder().with_message("유효성 검사 실패").with_errors(serializer.errors).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        target = serializer.validated_data['target']
        verification_code = serializer.validated_data['verification_code']

        # Find verification record by target
        try:
            verification = Verification.objects.get(target=target, verification_code=verification_code)
        except Verification.DoesNotExist:
            response = ErrorResponseBuilder().with_message("인증번호 불일치").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if verification.is_expired():
            response = ErrorResponseBuilder().with_message("인증번호 만료").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        return Response({"code": 0, "message": "인증 성공"}, status=status.HTTP_200_OK)
    

# Social API
# <-------------------------------------------------------------------------------------------------------------------------------->
# Naver API
class NaverAPIView(APIView):
    def post(self, request):
        code = request.data.get("code")
        state = request.data.get("state")
        
        try:
            # NaverResponse 객체를 통해 네이버 인증 처리
            naver_response = NaverResponse.create_from_code(code, state, settings.NAVER_CLIENT_ID, settings.NAVER_CLIENT_SECRET)
            
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
                    response = ErrorResponseBuilder().with_message("Social sign in failed").with_errors(serializer.errors).build()
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError as error:
            response = ErrorResponseBuilder().with_message("네이버 로그인 실패").with_errors({"error": str(error)}).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Google Sign In API
class GoogleAPIView(APIView):
    def post(self, request):
        code = request.data.get("code")
        
        try:
            # GoogleResponse 객체를 통해 구글 인증 처리
            google_response = GoogleResponse.create_from_code(code, settings.GOOGLE_CLIENT_KEY, settings.GOOGLE_CLIENT_SECRET, settings.GOOGLE_CALLBACK_URI)
            
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
                    response = ErrorResponseBuilder().with_message("Social sign in failed").with_errors(serializer.errors).build()
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError as error:
            response = ErrorResponseBuilder().with_message("구글 로그인 실패").with_errors({"error": str(error)}).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Kakao Sign In API
class KakaoAPIView(APIView):
    def post(self, request):
        code = request.data.get("code")
        
        try:
            # KakaoResponse 객체를 통해 카카오 인증 처리
            kakao_response = KakaoResponse.create_from_code(code, settings.KAKAO_CLIENT_KEY, settings.KAKAO_CALLBACK_URI)
            
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
                    response = ErrorResponseBuilder().with_message("Social sign in failed").with_errors(serializer.errors).build()
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError as error:
            response = ErrorResponseBuilder().with_message("카카오 로그인 실패").with_errors({"error": str(error)}).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Apple Sign In API
class AppleAPIView(APIView):
    def post(self, request):
        pass


# Authentication API
# <-------------------------------------------------------------------------------------------------------------------------------->
# PASS Authentication API
class PassRequestAPIView(APIView):
    def get(self, request):
        try:
            pass_response = PassRequest.create_from_nice_api(settings.NICE_ACCESS_TOKEN, settings.NICE_CLIENT_ID, settings.NICE_PRODUCT_ID, settings.NICE_SERVER_URI)
            
            if not pass_response.is_valid:
                response = ErrorResponseBuilder().with_message("NICE API 응답이 유효하지 않습니다.").build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            # DB에 인증 데이터 저장, 기존 데이터가 있으면 삭제 (req_no는 unique)
            PassVerification.objects.filter(req_no=pass_response.req_no).delete()
            PassVerification.objects.create(
                req_no=pass_response.req_no,
                token_version_id=pass_response.token_version_id,
                key=pass_response.key,
                iv=pass_response.iv,
                hmac_key=pass_response.hmac_key
            )
            
            # 프론트엔드에 전달할 데이터
            frontend_data = pass_response.to_frontend_data()
            
            return Response({
                'code': 0,
                'message': '본인인증 데이터가 생성되었습니다.',
                'data': frontend_data
            }, status=status.HTTP_200_OK)
            
        except Exception as error:
            response = ErrorResponseBuilder().with_message('본인인증 데이터 생성 중 오류가 발생했습니다').with_errors({"error": str(error)}).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# PASS CI API
class PassAPIView(APIView):
    def post(self, request):
        try:
            req_no = request.data.get('req_no')
            token_version_id = request.data.get('token_version_id')
            enc_data = request.data.get('enc_data')
            integrity_value = request.data.get('integrity_value')
            
            if not all([req_no, token_version_id, enc_data, integrity_value]):
                response = ErrorResponseBuilder().with_message("필수 파라미터가 누락되었습니다.").with_errors({
                    "missing_fields": ["req_no", "token_version_id", "enc_data", "integrity_value"]
                }).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            # DB에서 인증 세션 데이터 조회
            try:
                pass_verification = PassVerification.objects.get(
                    req_no=req_no,
                    token_version_id=token_version_id
                )
            except PassVerification.DoesNotExist:
                response = ErrorResponseBuilder().with_message("유효하지 않은 인증 요청입니다.").build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            # 만료 확인 (30분)
            if pass_verification.is_expired():
                response = ErrorResponseBuilder().with_message("인증 요청이 만료되었습니다.").build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            # 이미 인증 완료된 경우
            if pass_verification.is_verified:
                response = ErrorResponseBuilder().with_message("이미 인증이 완료된 요청입니다.").build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            # 무결성 검증 (HMAC)
            h = hmac.new(
                key=pass_verification.hmac_key.encode(),
                msg=enc_data.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()
            calculated_integrity = base64.b64encode(h).decode('utf-8')
            
            if calculated_integrity != integrity_value:
                response = ErrorResponseBuilder().with_message("무결성 검증에 실패했습니다.").build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            # PassResponse 객체 생성 및 사용자 데이터 파싱
            try:
                pass_response = PassResponse.create_from_request_data(
                    req_no=req_no,
                    token_version_id=token_version_id,
                    enc_data=enc_data,
                    integrity_value=integrity_value
                )
                
                # 사용자 데이터 파싱
                user_data = pass_response.parse_user_data(
                    key=pass_verification.key,
                    iv=pass_verification.iv
                )
            except Exception as error:
                response = ErrorResponseBuilder().with_message("사용자 데이터 파싱에 실패했습니다.").with_errors({"error": str(error)}).build()
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            # 인증 완료로 표시
            pass_verification.mark_as_verified()
            
            return Response({
                'code': 0,
                'message': '본인인증이 완료되었습니다.',
                'data': {
                    'req_no': req_no,
                    'user_data': user_data
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as error:
            response = ErrorResponseBuilder().with_message('본인인증 처리 중 오류가 발생했습니다').with_errors({"error": str(error)}).build()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# PortOne API
class PortOneAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        identity_code = request.data.get("identity_code")

        if not identity_code:
            response = ErrorResponseBuilder().with_message("identity_code is required").build()
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

            response = AuthResponseBuilder(user).with_message("본인인증 완료").build()
            return Response(response, status=status.HTTP_200_OK)

        except IntegrityError:
            response = ErrorResponseBuilder().with_message("이미 본인인증된 아이디가 존재합니다.").build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            response = ErrorResponseBuilder().with_message("포트원 인증 실패").with_errors({"error": str(error)}).build()
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Auth Response Builder
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