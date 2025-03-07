from rest_framework import serializers
from django.db import transaction

from .models import Order, OrderItem, Payment
from products.models import Product, ProductVariant
from products.serializers import ProductSerializer, ProductVariantSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model.
    """
    product_details = ProductSerializer(source='product', read_only=True)
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_details', 'variant', 'variant_details',
            'quantity', 'price', 'total_price'
        ]
        read_only_fields = ['id', 'price', 'total_price']


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Payment model.
    """
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'payment_method', 'status', 
            'transaction_id', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'total_amount', 'telegram_id',
            'notes', 'created_at', 'updated_at', 'items', 'payments'
        ]
        read_only_fields = ['id', 'user', 'status', 'total_amount', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new order.
    """
    telegram_id = serializers.CharField(max_length=20, required=True)
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            allow_empty=False
        ),
        allow_empty=False
    )
    
    def validate_items(self, items):
        """
        Validate the items in the order.
        """
        validated_items = []
        
        for item in items:
            product_id = item.get('product_id')
            variant_id = item.get('variant_id')
            quantity = int(item.get('quantity', 1))
            
            if not product_id:
                raise serializers.ValidationError("Product ID is required for each item")
            
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {product_id} does not exist or is not active")
            
            variant = None
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id, product=product, is_active=True)
                except ProductVariant.DoesNotExist:
                    raise serializers.ValidationError(f"Variant with ID {variant_id} does not exist or is not active")
            
            if quantity < 1:
                raise serializers.ValidationError("Quantity must be at least 1")
            
            price = variant.current_price if variant else product.current_price
            
            validated_items.append({
                'product': product,
                'variant': variant,
                'quantity': quantity,
                'price': price
            })
        
        return validated_items
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new order with the validated data.
        """
        user = self.context['request'].user
        telegram_id = validated_data.get('telegram_id')
        items = validated_data.get('items')
        
        # Calculate total amount
        total_amount = sum(item['price'] * item['quantity'] for item in items)
        
        # Create order
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            telegram_id=telegram_id
        )
        
        # Create order items
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                variant=item['variant'],
                quantity=item['quantity'],
                price=item['price']
            )
        
        return order

