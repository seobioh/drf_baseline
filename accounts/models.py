# accounts/models.py
app_name = "accounts"

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager # Django's user model
from django.utils import timezone
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, name, user_name, birthday=None, gender=None, profile_img_url=None, password=None):
        if not email:
            raise ValueError("Email can't be blank.")
        if not name:
            raise ValueError("Name field can't be blank.")
        if not user_name:
            raise ValueError("user_name field can't be blank.")
        user = self.model(
            email = email,
            name = name,
            user_name = user_name,
            birthday = birthday,
            gender = gender,
            profile_img_url = profile_img_url
        )
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_superuser(self, email, name, user_name, password=None, **extra_fields):
        user = self.create_user(
            email = email,
            name = name,
            user_name = user_name,
            password = password,
            **extra_fields
        )
        user.is_business = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self.db)
        return user

        
class User(AbstractBaseUser):  # Custom user model
    # Required fields
    id = models.AutoField(primary_key=True) # Primary Key
    email = models.EmailField(null=False, blank=False,  unique=True)   # Unique = True
    name = models.CharField(null=False, blank=False, max_length=24)
    user_name = models.CharField(null=False, blank=False, max_length=24)

    # Optional fields
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(null=True, blank=True, max_length=6)
    profile_img_url = models.TextField(null=True, blank=True)

    # Auto fields
    created_at = models.DateTimeField(auto_now_add=True)

    # Required fields
    is_active = models.BooleanField(default=True)
    is_business = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    # User's username field is set to email.
    USERNAME_FIELD = 'email'

    # Required fields
    REQUIRED_FIELDS = ['name', 'user_name']

    class Meta:
        db_table = "User"  # DB 테이블에 표시되는 이름
        
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