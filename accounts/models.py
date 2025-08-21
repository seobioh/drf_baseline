# accounts/models.py
app_name = "accounts"

import uuid
import hashlib

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager # Django's user model
from django.db import models
from django.utils import timezone
from django_cryptography.fields import encrypt

class UserManager(BaseUserManager):
    def create_user(self, email, name, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        if not name:
            raise ValueError("Name is required.")

        uuid8 = uuid.uuid4().hex[:8]
        if not username:
            username = f"오리무새{uuid8}"

        referral_code = uuid8
        email = self.normalize_email(email)

        user = self.model(
            email = email,
            name = name,
            username = username,
            referral_code = referral_code,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_business', True)
        extra_fields.setdefault('is_active', True)

        user = self.create_user(
            email = email,
            name = name,
            username = username,
            password = password,
            **extra_fields
        )
        return user

        
class User(AbstractBaseUser):
    # Required fields
    id = models.AutoField(primary_key=True)                 # Primary Key
    email = models.EmailField(unique=True)                  # Unique = True
    mobile = models.CharField(max_length=15, unique=True, blank=True, null=True)   # Unique = True, blank = True, null = True
    name = models.CharField(max_length=24)
    username = models.CharField(max_length=24, unique=True, blank=True)

    # Optional fields
    ci = encrypt(models.CharField(max_length=100, null=True, blank=True))
    ci_hash = models.CharField(max_length=64, unique=True, null=True, blank=True)
    profile_image = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=6, null=True, blank=True)
    referral_code = models.CharField(max_length=10,  unique=True, null=True, blank=True)

    # Auto fields
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    last_access = models.DateTimeField(null=True, blank=True)

    # Required fields
    is_active = models.BooleanField(default=True)
    is_business = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    # User's username field is set to email.
    USERNAME_FIELD = 'email'

    # Required fields
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = "User"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        if self.ci:
            self.ci_hash = hashlib.sha256(self.ci.encode('utf-8')).hexdigest()      # Create SHA256 hash if ci exists
        else:
            self.ci_hash = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin 
    
    def has_module_perms(self, app_label):
        return self.is_admin


class UserSocialAccount(models.Model):
    PROVIDER_CHOICES = (
        ('google', 'Google'),
        ('kakao', 'Kakao'),
        ('naver', 'Naver'),
        ('apple', 'Apple'),
    )

    user = models.ForeignKey(User, related_name='social_accounts', on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_user_id = models.CharField(max_length=255)  # 소셜 고유 ID
    connected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Social Account"
        verbose_name_plural = "User Social Accounts"
        unique_together = ('provider', 'provider_user_id')  # 같은 소셜에서 중복 방지

    def __str__(self):
        return f"{self.user.email} - {self.provider}"


class Verification(models.Model):
    TYPE_CHOICES = (
        ('mobile', 'Mobile'),
        ('email', 'Email'),
    )

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    target = models.CharField(max_length=255)  # 전화번호 또는 이메일
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('type', 'target')

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f"{self.type} - {self.target}"


class PassVerification(models.Model):
    req_no = models.CharField(max_length=50, unique=True)  # 요청 고유번호
    token_version_id = models.CharField(max_length=50)     # 토큰 버전 ID
    key = encrypt(models.CharField(max_length=100))        # 암호화 키
    iv = encrypt(models.CharField(max_length=100))         # 초기화 벡터
    hmac_key = encrypt(models.CharField(max_length=100))   # HMAC 키
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)       # 인증 완료 여부
    verified_at = models.DateTimeField(null=True, blank=True)  # 인증 완료 시간
    
    class Meta:
        db_table = "PassVerification"
        verbose_name = "Pass Verification"
        verbose_name_plural = "Pass Verifications"
        indexes = [
            models.Index(fields=['req_no']),
            models.Index(fields=['token_version_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"PassVerification(req_no={self.req_no}, verified={self.is_verified})"
    
    def is_expired(self):
        """30분 후 만료"""
        return timezone.now() > self.created_at + timezone.timedelta(minutes=30)
    
    def mark_as_verified(self):
        """인증 완료로 표시"""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=['is_verified', 'verified_at'])