from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductViewSet, ProductVariantViewSet

app_name = 'products'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<slug:product_slug>/variants/', ProductVariantViewSet.as_view({'get': 'list'}), name='product-variants'),
]

