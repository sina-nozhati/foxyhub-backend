from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, OTP


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'email', 'telegram_id', 'first_name', 'last_name', 'is_verified']
        read_only_fields = ['id', 'is_verified']


class PhoneNumberSerializer(serializers.Serializer):
    """
    Serializer for phone number validation.
    """
    phone_number = serializers.CharField(max_length=15)


class OTPVerificationSerializer(serializers.Serializer):
    """
    Serializer for OTP verification.
    """
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        otp_code = attrs.get('otp_code')
        
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("User with this phone number does not exist."))
        
        # Get the latest OTP for the user
        latest_otp = OTP.objects.filter(user=user).order_by('-created_at').first()
        
        if not latest_otp:
            raise serializers.ValidationError(_("No OTP found for this user."))
        
        if not latest_otp.is_valid():
            raise serializers.ValidationError(_("OTP has expired or already been used."))
        
        if latest_otp.code != otp_code:
            raise serializers.ValidationError(_("Invalid OTP code."))
        
        # Mark OTP as used
        latest_otp.is_used = True
        latest_otp.save()
        
        # Mark user as verified if not already
        if not user.is_verified:
            user.is_verified = True
            user.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class TelegramIDSerializer(serializers.Serializer):
    """
    Serializer for updating Telegram ID.
    """
    telegram_id = serializers.CharField(max_length=20)

