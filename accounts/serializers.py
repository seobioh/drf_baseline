# accounts/serializers.py
app_name = "accounts"

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):       # Verify data
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'nickname', 'birthday', 'gender', 'profile_img', 'password']
        extra_kwargs = {'password': {'write_only': True}}