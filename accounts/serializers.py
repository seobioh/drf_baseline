# accounts/serializers.py
app_name = "accounts"

from rest_framework import serializers
from .models import User, Verification

class UserSerializer(serializers.ModelSerializer):
    ci_verified = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'mobile', 'name', 'username',
            'ci_verified', 'birthday', 'gender', 'profile_image',
            'password', 'last_access', 'created_at', 'modified_at'
        ]
        extra_kwargs = {
            'ci_verified': {'read_only': True},
            'password': {'write_only': True},
            'last_access': {'read_only': True},
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def get_ci_verified(self, obj):
        return obj.ci_hash is not None


class VerificationRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=Verification.TYPE_CHOICES)
    target = serializers.CharField(max_length=255)


class VerificationCheckSerializer(serializers.Serializer):
    target = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=6)
