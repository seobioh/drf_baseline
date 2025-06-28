# accounts/views.py
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

from .task import send_verification_email
from .models import User, EmailVerification
from .serializers import UserSerializer, EmailVerificationSerializer
from .permissions import IsAuthenticated, AllowAny


# Sign Up API
class SignUpAPIView(APIView):
    def post(self, request):
        # Check if the email is already registered
        if User.objects.filter(email=request.data.get("email")).exists():
            response_error = {
                "code": 1,
                "message": "Email already exists.",
            }
            return Response(response_error, status=status.HTTP_400_BAD_REQUEST)

        # Check if the mobile number is already registered
        if User.objects.filter(mobile=request.data.get("mobile")).exists():
            response_error = {
                "code": 1,
                "message": "Mobile number already exists.",
            }
            return Response(response_error, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save user data
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            expires_in = token.access_token.lifetime.total_seconds()

            response = {
                "code": 0,
                "user": serializer.data,
                "message": "Register successful",
                "token": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": expires_in,
                },
            }
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
        user = request.user  # Authenticated user
        serializer = UserSerializer(user)
        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)
        expires_in = token.access_token.lifetime.total_seconds()

        # Update last access time
        user.last_access = now()
        user.save(update_fields=["last_access"])

        response = {
            "code": 0,
            "user": serializer.data,
            "message": "Register successful",
            "token": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": expires_in,
            },
        }
        return Response(response, status=status.HTTP_200_OK)
        
    # Sign-In API (Issue JWT Token)
    def post(self, request):
        user = authenticate(email=request.data.get("email"), password=request.data.get("password"))
        if user is not None:
            serializer = UserSerializer(user)
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            expires_in = token.access_token.lifetime.total_seconds()

            # Update last login time
            user.last_access = now()
            user.save(update_fields=["last_access"])

            response = {
                "code": 0,
                "user": serializer.data,
                "message": "Register successful",
                "token": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": expires_in,
                },
            }
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


# Verification Code API
class SendVerificationCodeAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            response_error = {
                "code": 1,
                "message": "Email is required."
            }
            return Response(response_error, status=status.HTTP_400_BAD_REQUEST)

        # Check if email already belongs to a registered user
        if User.objects.filter(email=email).exists():
            response_error = {
                "code": 1,
                "message": "Email already registered."
            }
            return Response(response_error, status=status.HTTP_400_BAD_REQUEST)

        # Generate 6-digit code
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        # Check if a record already exists for the email
        EmailVerification.objects.update_or_create(
            email=email,
            defaults={'code': code, 'created_at': now()}
        )

        send_verification_email(email, code)

        response = {
            "code": 0,
            "message": "Verification code sent to your email."
        }
        return Response(response, status=status.HTTP_200_OK)
    

# Verification Code API
class VerifyCodeAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            response_error = {
                "code": 1,
                "message": "Email is required."
            }
            return Response(response_error, status=status.HTTP_400_BAD_REQUEST)
        
        code = request.data.get("code")
        try:
            record = EmailVerification.objects.get(email=email, code=code)

        except EmailVerification.DoesNotExist:
            response_error = {
                "code": 2,
                "message": "Invalid verification code."
            }
            return Response(response_error, status.HTTP_400_BAD_REQUEST)

        if record.is_expired():
            response = {
                "code": 3,
                "message": "Verification code expired."
            }
            record.delete()
            return Response(response, status.HTTP_400_BAD_REQUEST)

        response = {
            "code": 0,
            "message": "Verification successful."
        }
        record.delete()
        return Response(response, status=status.HTTP_200_OK)