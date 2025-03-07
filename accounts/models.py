import uuid
import random
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.conf import settings

from core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """
    Custom user manager for the User model.
    """
    
    def create_user(self, phone_number, password=None, **extra_fields):
        """
        Create and save a regular user with the given phone number and password.
        """
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, password=None, **extra_fields):
        """
        Create and save a superuser with the given phone number and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser, TimeStampedModel):
    """
    Custom user model that uses phone number for authentication.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None  # Remove username field
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    telegram_id = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return self.phone_number


class OTP(TimeStampedModel):
    """
    One-time password model for user verification.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    class Meta:
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
    
    def __str__(self):
        return f"{self.user.phone_number} - {self.code}"
    
    @classmethod
    def generate_otp(cls, user):
        """
        Generate a new OTP for the given user.
        """
        # Generate a 6-digit code
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Set expiry time
        expires_at = timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        
        # Create and return the OTP
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
    
    def is_valid(self):
        """
        Check if the OTP is still valid.
        """
        return not self.is_used and self.expires_at > timezone.now()

