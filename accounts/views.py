from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.translation import gettext_lazy as _

from .models import User, OTP
from .serializers import (
    UserSerializer, 
    PhoneNumberSerializer, 
    OTPVerificationSerializer,
    TelegramIDSerializer
)
from core.services.telegram import TelegramClient


class RequestOTPView(APIView):
    """
    View for requesting an OTP for login/registration.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            
            # Get or create user
            user, created = User.objects.get_or_create(phone_number=phone_number)
            
            # Generate OTP
            otp = OTP.generate_otp(user)
            
            # In a real application, send the OTP via SMS
            # For now, we'll just return it in the response (for development only)
            return Response({
                'message': _('OTP sent successfully'),
                'otp_code': otp.code,  # Remove this in production
                'is_new_user': created
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """
    View for verifying OTP and logging in/registering user.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                'message': _('OTP verified successfully'),
                'user': UserSerializer(serializer.validated_data['user']).data,
                'refresh': serializer.validated_data['refresh'],
                'access': serializer.validated_data['access'],
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating user profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


class UpdateTelegramIDView(APIView):
    """
    View for updating user's Telegram ID.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = TelegramIDSerializer(data=request.data)
        if serializer.is_valid():
            telegram_id = serializer.validated_data['telegram_id']
            
            # Verify the Telegram ID
            telegram_client = TelegramClient()
            is_valid = telegram_client.verify_telegram_id(telegram_id)
            
            if is_valid:
                # Update user's Telegram ID
                user = request.user
                user.telegram_id = telegram_id
                user.save()
                
                return Response({
                    'message': _('Telegram ID updated successfully'),
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': _('Invalid Telegram ID')
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

