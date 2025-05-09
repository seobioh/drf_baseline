# accounts/serializers.py
app_name = "accounts"

from rest_framework import serializers
from .models import User, EmailVerification

class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):       # Verify data
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'user_name', 'birthday', 'gender', 'profile_img_url', 'password', 'last_login', 'created_at']
        extra_kwargs = {'password': {'write_only': True}, 'last_login': {'read_only': True}, 'created_at': {'read_only': True}}

class EmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerification
        fields = ['email', 'code']