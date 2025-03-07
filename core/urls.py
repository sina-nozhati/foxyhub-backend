from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import HealthCheckView

app_name = 'core'

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]

