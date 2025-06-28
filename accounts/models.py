# accounts/models.py
app_name = "accounts"

import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager # Django's user model
from django.utils import timezone
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, mobile, name, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        if not mobile:
            raise ValueError("Mobile number is required.")
        if not name:
            raise ValueError("Name is required.")        
        if not username:
            username = f"오리무새{uuid.uuid4().hex[:8]}"

        email = self.normalize_email(email)
        mobile = self.normalize_email(mobile)

        user = self.model(
            email = email,
            mobile = mobile,
            name = name,
            username = username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, mobile, name, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_business', True)
        extra_fields.setdefault('is_active', True)

        email = self.normalize_email(email)
        mobile = self.normalize_email(mobile)

        user = self.create_user(
            email = email,
            mobile = mobile,
            name = name,
            username = username,
            password = password,
            **extra_fields
        )
        return user

        
class User(AbstractBaseUser):  # Custom user model
    # Required fields
    id = models.AutoField(primary_key=True)                 # Primary Key
    email = models.EmailField(unique=True)                  # Unique = True
    mobile = models.CharField(max_length=15, unique=True)   # Unique = True
    name = models.CharField(max_length=24)
    username = models.CharField(max_length=24, unique=True, blank=True)

    # Optional fields
    profile_image = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=6, null=True, blank=True)

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
    REQUIRED_FIELDS = ['mobile', 'name']

    class Meta:
        db_table = "User"
        verbose_name = "User"
        verbose_name_plural = "Users"
        
    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin 
    
    def has_module_perms(self, app_label):
        return self.is_admin
    

class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f'{self.email} - {self.code}'