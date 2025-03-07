import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel
from accounts.models import User
from products.models import Product, ProductVariant


class Order(TimeStampedModel):
    """
    Order model.
    """
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PAID = 'paid', _('Paid')
        PROCESSING = 'processing', _('Processing')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        CANCELLED = 'cancelled', _('Cancelled')
        REFUNDED = 'refunded', _('Refunded')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    telegram_id = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.id} - {self.user.phone_number}"


class OrderItem(TimeStampedModel):
    """
    Order item model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity}) - Order {self.order.id}"
    
    @property
    def total_price(self):
        return self.price * self.quantity


class Payment(TimeStampedModel):
    """
    Payment model.
    """
    class PaymentMethod(models.TextChoices):
        CRYPTO = 'crypto', _('Cryptocurrency')
        CARD = 'card', _('Credit/Debit Card')
        OTHER = 'other', _('Other')
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        REFUNDED = 'refunded', _('Refunded')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
    
    def __str__(self):
        return f"Payment {self.id} - Order {self.order.id}"

