from rest_framework import serializers

from .models import Category, Product, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'is_active']


class ProductVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductVariant model.
    """
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'name', 'description', 'price', 'discount_price', 
            'current_price', 'duration_months', 'is_active'
        ]


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    """
    category = CategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'discount_price', 
            'current_price', 'category', 'product_type', 'image', 'is_active', 'variants'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing products.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'current_price', 'category_name', 
            'product_type', 'image', 'is_active'
        ]

