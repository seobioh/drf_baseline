# accounts/serializers.py
app_name = "accounts"

from rest_framework import serializers
from .models import User, EmailVerification

class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'mobile', 'name', 'username',
            'birthday', 'gender', 'profile_image',
            'password', 'last_access', 'created_at', 'modified_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'last_access': {'read_only': True},
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
        }

class EmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerification
        fields = ['email', 'code']