from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, PaymentWebhookView

app_name = 'orders'

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
]

