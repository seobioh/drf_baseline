# accounts/schemas.py
app_name = "accounts"

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from drf_spectacular.utils import OpenApiExample

from server.schemas import SuccessResponseSerializer, ErrorResponseSerializer


# Wrapper Serializers
# <-------------------------------------------------------------------------------------------------------------------------------->
# Auth Response Serializer
class AuthResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=0, help_text="Success code")
    message = serializers.CharField(help_text="Success message")
    data = serializers.DictField(help_text="Response data containing user info and tokens")
    
    class Meta:
        ref_name = "AuthResponse"


# Request Serializers
class SignUpRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="이메일 주소")
    mobile = serializers.CharField(help_text="휴대폰 번호")
    name = serializers.CharField(help_text="이름")
    username = serializers.CharField(help_text="사용자명")
    password = serializers.CharField(write_only=True, help_text="비밀번호")
    identity_code = serializers.CharField(required=False, help_text="본인인증 코드")
    referral_code = serializers.CharField(required=False, help_text="추천 코드")


class SignInRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="이메일 주소")
    password = serializers.CharField(write_only=True, help_text="비밀번호")


class UpdateAccountRequestSerializer(serializers.Serializer):
    mobile = serializers.CharField(required=False, help_text="휴대폰 번호")
    name = serializers.CharField(required=False, help_text="이름")
    username = serializers.CharField(required=False, help_text="사용자명")
    birthday = serializers.DateField(required=False, help_text="생년월일")
    gender = serializers.ChoiceField(choices=[('M', '남성'), ('F', '여성')], required=False, help_text="성별")
    profile_image = serializers.URLField(required=False, help_text="프로필 이미지 URL")
    password = serializers.CharField(write_only=True, required=False, help_text="새 비밀번호")


class CheckEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="확인할 이메일 주소")


class VerificationRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=[('email', '이메일'), ('sms', 'SMS')], help_text="인증 타입")
    target = serializers.CharField(help_text="인증 대상 (이메일 주소 또는 전화번호)")


class VerificationCheckRequestSerializer(serializers.Serializer):
    target = serializers.CharField(help_text="인증 대상 (이메일 주소 또는 전화번호)")
    verification_code = serializers.CharField(max_length=6, help_text="인증번호 (6자리)")


class ResetPasswordRequestSerializer(serializers.Serializer):
    target = serializers.CharField(required=False, help_text="인증 대상 (이메일 주소 또는 전화번호)")
    verification_code = serializers.CharField(required=False, max_length=6, help_text="인증번호 (6자리)")
    identity_code = serializers.CharField(required=False, help_text="본인인증 코드")


class NaverAuthRequestSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="네이버 OAuth authorization code")
    state = serializers.CharField(help_text="네이버 OAuth state parameter")


class GoogleAuthRequestSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="구글 OAuth authorization code")


class KakaoAuthRequestSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="카카오 OAuth authorization code")


class AppleAuthRequestSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="애플 OAuth authorization code")
    id_token = serializers.CharField(help_text="애플 ID token")


class PortoneVerificationRequestSerializer(serializers.Serializer):
    identity_code = serializers.CharField(help_text="포트원 본인인증 코드")  


# Common Examples
# <-------------------------------------------------------------------------------------------------------------------------------->
class CommonExamples:
    @staticmethod
    def auth_success_example(message="인증이 완료되었습니다.", include_token=True):
        """인증 성공 응답 예시"""
        user_data = {
            "id": 1,
            "email": "user@example.com",
            "mobile": "010-1234-5678",
            "name": "홍길동",
            "username": "honggildong",
            "ci_verified": True,
            "birthday": "1990-01-01",
            "gender": "M",
            "profile_image": "https://example.com/profile.jpg",
            "referral_code": "ABC123",
            "point": 1000,
            "last_access": "2024-01-01T12:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "modified_at": "2024-01-01T12:00:00Z"
        }        
        data = {"user": user_data}

        if include_token:
            data["token"] = {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "expires_in": 3600
            }
        
        return OpenApiExample(
            "Success Response",
            summary="성공",
            description="요청이 성공적으로 처리된 경우의 응답",
            value={
                "code": 0,
                "message": message,
                "data": data
            },
            response_only=True,
            status_codes=['200']
        )
    
    @staticmethod
    def auth_error_example(message="인증에 실패했습니다.", errors=None):
        """인증 실패 응답 예시"""
        if errors is None:
            errors = {"detail": "자격 증명이 제공되지 않았습니다."}
        
        return OpenApiExample(
            "Error Response",
            summary="실패",
            description="요청 처리 중 오류가 발생한 경우의 응답",
            value={
                "code": 1,
                "message": message,
                "errors": errors
            },
            response_only=True,
            status_codes=['400', '401']
        )
    
    @staticmethod
    def success_example(message="요청이 성공적으로 처리되었습니다.", data=None):
        """일반 성공 응답 예시"""
        if data is None:
            data = {"result": "success"}
        
        return OpenApiExample(
            "Success Response",
            summary="성공",
            description="요청이 성공적으로 처리된 경우의 응답",
            value={
                "code": 0,
                "message": message,
                "data": data
            },
            response_only=True,
            status_codes=['200']
        )
    
    @staticmethod
    def error_example(message="요청 처리 중 오류가 발생했습니다.", errors=None):
        """일반 오류 응답 예시"""
        if errors is None:
            errors = {"detail": "요청을 처리할 수 없습니다."}
        
        return OpenApiExample(
            "Error Response",
            summary="실패",
            description="요청 처리 중 오류가 발생한 경우의 응답",
            value={
                "code": 1,
                "message": message,
                "errors": errors
            },
            response_only=True,
            status_codes=['400', '500']
        )


# Account Schema
# <-------------------------------------------------------------------------------------------------------------------------------->
class AccountSchema:
    @staticmethod
    def signup():
        return {
            'summary': "회원가입",
            'description': "새로운 사용자 계정을 생성합니다.",
            'request': SignUpRequestSerializer,
            'responses': {
                200: AuthResponseSerializer,
                400: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.auth_success_example(
                    message="회원가입 성공",
                ),
                CommonExamples.auth_error_example(
                    message="이메일 중복",
                    errors={"email": ["이미 가입된 이메일입니다."]}
                )
            ]
        }

    @staticmethod
    def token_refresh():
        return {
            'summary': "토큰 갱신",
            'description': "리프레시 토큰을 사용하여 액세스 토큰을 갱신합니다.",
            'request': TokenRefreshSerializer,
            'responses': {
                200: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="토큰 갱신 성공",
                    data={
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "expires_in": 3600
                    }
                ),
                CommonExamples.auth_error_example(
                    message="토큰 갱신에 실패했습니다.",
                    errors={"token_error": ["유효하지 않은 토큰입니다."]}
                )
            ]
        }

    @staticmethod
    def get_account_info():
        return {
            'summary': "계정 정보 조회",
            'description': "인증된 사용자의 계정 정보를 조회합니다.",
            'responses': {
                200: AuthResponseSerializer,
                401: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.auth_success_example(
                    message="로그인 성공",
                    include_token=False
                ),
                CommonExamples.auth_error_example(
                    message="인증에 실패했습니다."
                )
            ]
        }

    @staticmethod
    def signin():
        return {
            'summary': "로그인",
            'description': "이메일과 비밀번호로 로그인합니다.",
            'request': SignInRequestSerializer,
            'responses': {
                200: AuthResponseSerializer,
                400: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.auth_success_example(
                    message="로그인 성공"
                ),
                CommonExamples.auth_error_example(
                    message="로그인에 실패했습니다.",
                    errors={"non_field_errors": ["잘못된 이메일 또는 비밀번호입니다."]}
                )
            ]
        }

    @staticmethod
    def update_account():
        return {
            'summary': "계정 정보 수정",
            'description': "인증된 사용자의 계정 정보를 수정합니다.",
            'request': UpdateAccountRequestSerializer,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="사용자 정보 수정 성공",
                ),
                CommonExamples.error_example(
                    message="사용자 정보 수정에 실패했습니다.",
                    errors={
                        "mobile": ["이미 가입된 전화번호입니다."],
                        "username": ["이미 사용 중인 사용자명입니다."]
                    }
                )
            ]
        }

    @staticmethod
    def delete_account():
        return {
            'summary': "계정 삭제",
            'description': "인증된 사용자의 계정을 삭제합니다.",
            'responses': {
                202: SuccessResponseSerializer,
                401: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="계정 삭제 성공",
                    data={"deleted": True}
                ),
                CommonExamples.auth_error_example(
                    message="인증 실패"
                )
            ]
        }

    @staticmethod
    def check_email():
        return {
            'summary': "이메일 중복 확인",
            'description': "이메일 중복 여부를 확인합니다.",
            'request': CheckEmailRequestSerializer,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="이메일 사용 가능",
                    data={
                        "available": True,
                        "email": "newuser@example.com"
                    }
                ),
                CommonExamples.success_example(
                    message="이메일 중복",
                    data={
                        "available": False,
                        "email": "existing@example.com"
                    }
                ),
                CommonExamples.error_example(
                    message="이메일 중복 확인에 실패했습니다.",
                    errors={
                        "email": ["유효하지 않은 이메일 형식입니다."]
                    }
                )
            ]
        }

    @staticmethod
    def request_verification():
        return {
            'summary': "인증번호 발송",
            'description': "이메일 또는 전화번호로 인증번호를 발송합니다.",
            'request': VerificationRequestSerializer,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="인증번호 발송 완료",
                    data={
                        "type": "email",
                        "target": "user@example.com",
                        "expires_in": 300
                    }
                ),
                CommonExamples.success_example(
                    message="인증번호 발송 완료",
                    data={
                        "type": "sms",
                        "target": "010-1234-5678",
                        "expires_in": 300
                    }
                ),
                CommonExamples.error_example(
                    message="인증번호 요청에 실패했습니다.",
                    errors={
                        "target": ["유효하지 않은 전화번호 형식입니다."]
                    }
                )
            ]
        }

    @staticmethod
    def check_verification():
        return {
            'summary': "인증번호 확인",
            'description': "발송된 인증번호를 확인합니다.",
            'request': VerificationCheckRequestSerializer,
            'responses': {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.success_example(
                    message="인증 성공",
                    data={"verified": True, "target": "user@example.com"}
                ),
                CommonExamples.error_example(
                    message="인증번호가 일치하지 않습니다.",
                    errors={"verification_code": ["인증번호 불일치"]}
                )
            ]
        }

    @staticmethod
    def reset_password():
        return {
            'summary': "비밀번호 재설정",
            'description': "인증번호 또는 본인인증을 통해 비밀번호 재설정에 필요한 토큰을 발급합니다.",
            'request': ResetPasswordRequestSerializer,
            'responses': {
                200: AuthResponseSerializer,
                400: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.auth_success_example(
                    message="임시 토큰이 발급되었습니다."
                ),
                CommonExamples.error_example(
                    message="인증번호가 일치하지 않습니다.",
                    errors={"verification_code": ["인증번호 불일치"]}
                ),
                CommonExamples.error_example(
                    message="처리 중 오류가 발생했습니다.",
                    errors={"error": "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}
                )
            ]
        }

    @staticmethod
    def naver_auth():
        return {
            'summary': "네이버 로그인",
            'description': "네이버 OAuth를 통한 로그인/회원가입",
            'request': NaverAuthRequestSerializer,
            'responses': {
                200: AuthResponseSerializer,
                400: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.auth_success_example(
                    message="로그인 성공"
                ),
                CommonExamples.auth_error_example(
                    message="네이버 로그인에 실패했습니다.",
                    errors={"error": ["네이버 로그인 실패"]}
                )
            ]
        }

    @staticmethod
    def google_auth():
        return {
            'summary': "구글 로그인",
            'description': "구글 OAuth를 통한 로그인/회원가입",
            'request': GoogleAuthRequestSerializer,
            'responses': {
                200: AuthResponseSerializer,
                400: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.auth_success_example(
                    message="로그인 성공"
                ),
                CommonExamples.auth_error_example(
                    message="구글 로그인에 실패했습니다.",
                    errors={"error": ["구글 로그인 실패"]}
                )
            ]
        }

    @staticmethod
    def kakao_auth():
        return {
            'summary': "카카오 로그인",
            'description': "카카오 OAuth를 통한 로그인/회원가입",
            'request': KakaoAuthRequestSerializer,
            'responses': {
                200: AuthResponseSerializer,
                400: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.auth_success_example(
                    message="로그인 성공"
                ),
                CommonExamples.auth_error_example(
                    message="카카오 로그인에 실패했습니다.",
                    errors={"error": ["카카오 로그인 실패"]}
                )
            ]
        }

    @staticmethod
    def apple_auth():
        return {
            'summary': "애플 로그인",
            'description': "애플 OAuth를 통한 로그인/회원가입",
            'request': AppleAuthRequestSerializer,
            'responses': {
                200: AuthResponseSerializer,
                400: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.auth_success_example(
                    message="로그인 성공"
                ),
                CommonExamples.auth_error_example(
                    message="애플 로그인에 실패했습니다.",
                    errors={"error": ["애플 로그인 실패"]}
                )
            ]
        }

    @staticmethod
    def portone_verification():
        return {
            'summary': "포트원 본인인증",
            'description': "포트원을 통한 본인인증을 처리합니다.",
            'request': PortoneVerificationRequestSerializer,
            'responses': {
                200: AuthResponseSerializer,
                400: ErrorResponseSerializer,
            },
            'examples': [
                CommonExamples.auth_success_example(
                    message="본인인증 성공"
                ),
                CommonExamples.auth_error_example(
                    message="본인인증에 실패했습니다.",
                    errors={"error": ["포트원 인증 실패"]}
                )
            ]
        }