# accounts/views.py
app_name = 'accounts'

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings

from django.contrib.auth import authenticate

from .models import User
from .serializers import UserSerializer
from .permissions import IsAuthenticated, AllowAny

# Sign Up API
class SignUpAPIView(APIView):
    def post(self, request):
        # Check if the email is already registered
        if User.objects.filter(email=request.data["email"]).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save user data
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            expires_in = token.access_token.lifetime.total_seconds()
            
            return Response(
                {
                    "user": serializer.data,
                    "message": "Register successful",
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expires_in": expires_in,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Token Refresh API
class TokenRefreshAPIView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})

        try: 
            serializer.is_valid(raise_exception=True)
        except TokenError as error:
            return Response({"error": str(error)}, status=status.HTTP_401_UNAUTHORIZED)
        
        access_token = serializer.validated_data["access"]
        access_token_lifetime = api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()

        return Response(
            {
                "access_token": access_token,
                "expires_in": access_token_lifetime
            },
            status=status.HTTP_200_OK
        )

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

        return Response(
            {
                "user": serializer.data,
                "message": "Login successful",
                "token": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": expires_in,
                },
            },
            status=status.HTTP_200_OK,
        )
        
    # Sign-In API (Issue JWT Token)
    def post(self, request):
        user = authenticate(email=request.data.get("email"), password=request.data.get("password"))
        if user is not None:
            serializer = UserSerializer(user)
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            expires_in = token.access_token.lifetime.total_seconds()
            
            return Response(
                {
                    "user": serializer.data,
                    "message": "Login successful",
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expires_in": expires_in,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"message": "Invalid credentials. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
        
    # Delete Account API
    def delete(self, request):
        user = request.user  # Authenticated user
        user.delete()
        return Response({
            "message": "Account deleted successfully"
        }, status=status.HTTP_202_ACCEPTED)
        
    # Update Account Info API
    def put(self, request):
        user = request.user  # Authenticated user
        serializer = UserSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            updated_user = serializer.data

            return Response(
                {
                    "message": "User information updated successfully",
                    "user": updated_user,
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
