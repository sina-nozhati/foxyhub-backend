from django.urls import path

from .views import (
    RequestOTPView,
    VerifyOTPView,
    UserProfileView,
    UpdateTelegramIDView
)

app_name = 'accounts'

urlpatterns = [
    path('request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('update-telegram-id/', UpdateTelegramIDView.as_view(), name='update-telegram-id'),
]

