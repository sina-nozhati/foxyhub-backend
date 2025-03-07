from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Product, ProductVariant
from .serializers import (
    CategorySerializer, 
    ProductSerializer, 
    ProductListSerializer,
    ProductVariantSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing categories.
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing products.
    """
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'product_type']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'created_at']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer


class ProductVariantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing product variants.
    """
    serializer_class = ProductVariantSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return ProductVariant.objects.filter(
            is_active=True,
            product__slug=self.kwargs.get('product_slug')
        )

