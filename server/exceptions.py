# server/exceptions.py

from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied, ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied

from .utils import ErrorResponseBuilder


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        # DRF 예외가 처리된 경우
        error_data = response.data
        
        # 에러 타입에 따른 메시지 설정
        if isinstance(exc, AuthenticationFailed):
            message = "Authentication failed."
            error_code = 401
        elif isinstance(exc, NotAuthenticated):
            message = "Authentication required."
            error_code = 401
        elif isinstance(exc, PermissionDenied):
            message = "Permission denied."
            error_code = 403
        elif isinstance(exc, ValidationError):
            message = "Invalid input data."
            error_code = 400
        elif isinstance(exc, Http404):
            message = "Resource not found."
            error_code = 404
        elif isinstance(exc, (InvalidToken, TokenError)):
            message = "Token is invalid or expired."
            error_code = 401
        else:
            message = "Server error occurred."
            error_code = response.status_code
        
        # ErrorResponseBuilder로 응답 생성
        error_response = ErrorResponseBuilder() \
            .with_code(error_code) \
            .with_message(message) \
            .with_errors(error_data) \
            .build()
        
        return Response(error_response, status=response.status_code)
    
    # Django 예외 처리
    if isinstance(exc, DjangoPermissionDenied):
        error_response = ErrorResponseBuilder() \
            .with_code(403) \
            .with_message("Permission denied.") \
            .build()
        return Response(error_response, status=403)
    
    if isinstance(exc, DjangoValidationError):
        error_response = ErrorResponseBuilder() \
            .with_code(400) \
            .with_message("Invalid input data.") \
            .with_errors(exc.message_dict if hasattr(exc, 'message_dict') else str(exc)) \
            .build()
        return Response(error_response, status=400)
    
    # 기타 예외 처리
    if isinstance(exc, Exception):
        error_response = ErrorResponseBuilder() \
            .with_code(500) \
            .with_message("Internal server error.") \
            .build()
        return Response(error_response, status=500)
    
    return response