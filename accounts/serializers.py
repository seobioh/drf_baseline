# accounts/serializers.py
app_name = "accounts"

from rest_framework import serializers

from .models import User, UserSocialAccount, Verification

# User
# <-------------------------------------------------------------------------------------------------------------------------------->
class UserSerializer(serializers.ModelSerializer):
    ci_verified = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'mobile', 'name', 'username',
            'ci_verified', 'birthday', 'gender', 'profile_image', 'referral_code',
            'password', 'last_access', 'created_at', 'modified_at'
        ]
        extra_kwargs = {
            'email': {'read_only': True},
            'ci_verified': {'read_only': True},
            'referral_code': {'read_only': True},
            'password': {'write_only': True},
            'last_access': {'read_only': True},
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        # password가 포함되어 있으면 별도로 처리
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # mobile, name, birthday가 변경되면 ci와 ci_hash 초기화 (변경사항이 있으면 무조건)
        name = validated_data.get('name')
        mobile = validated_data.get('mobile')
        birthday = validated_data.get('birthday')
        
        if ('name' in validated_data and name != instance.name) or \
           ('mobile' in validated_data and mobile != instance.mobile) or \
           ('birthday' in validated_data and birthday != instance.birthday):
            instance.ci = None
            instance.ci_hash = None
        
        # 나머지 필드들 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

    def get_ci_verified(self, obj):
        return obj.ci_hash is not None

    def validate_mobile(self, value):
        if hasattr(self, 'instance') and self.instance and self.instance.mobile == value:
            return value
        
        if value and value.strip() and User.objects.filter(mobile=value).exists():
            raise serializers.ValidationError("Mobile number already exists.")
        return value


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'mobile', 'name', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_mobile(self, value):
        if value and value.strip() and User.objects.filter(mobile=value).exists():
            raise serializers.ValidationError("Mobile number already exists.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


# Verification
# <-------------------------------------------------------------------------------------------------------------------------------->
class VerificationRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=Verification.TYPE_CHOICES)
    target = serializers.CharField(max_length=255)


class VerificationCheckSerializer(serializers.Serializer):
    target = serializers.CharField(max_length=255)
    verification_code = serializers.CharField(max_length=6)


# Social User
# <-------------------------------------------------------------------------------------------------------------------------------->
class SocialSignUpSerializer(SignUpSerializer):
    provider = serializers.ChoiceField(choices=UserSocialAccount.PROVIDER_CHOICES)
    provider_user_id = serializers.CharField(max_length=255)

    class Meta(SignUpSerializer.Meta):
        fields = SignUpSerializer.Meta.fields + ['provider', 'provider_user_id']

    def create(self, validated_data):
        provider = validated_data.pop('provider')
        provider_user_id = validated_data.pop('provider_user_id')

        user = super().create(validated_data)

        UserSocialAccount.objects.create(
            user=user,
            provider=provider,
            provider_user_id=provider_user_id
        )

        return user