import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel


class Category(TimeStampedModel):
    """
    Product category model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
    
    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    """
    Product model.
    """
    class ProductType(models.TextChoices):
        TELEGRAM_PREMIUM = 'telegram_premium', _('Telegram Premium')
        TELEGRAM_STARS = 'telegram_stars', _('Telegram Stars')
        SPOTIFY = 'spotify', _('Spotify')
        OTHER = 'other', _('Other')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    product_type = models.CharField(max_length=20, choices=ProductType.choices, default=ProductType.OTHER)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
    
    def __str__(self):
        return self.name
    
    @property
    def current_price(self):
        """
        Return the current price (discount_price if available, otherwise price).
        """
        return self.discount_price if self.discount_price else self.price


class ProductVariant(TimeStampedModel):
    """
    Product variant model (e.g., different durations for Telegram Premium).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration_months = models.PositiveIntegerField(default=1, help_text=_('Duration in months (for subscription products)'))
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('Product Variant')
        verbose_name_plural = _('Product Variants')
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    @property
    def current_price(self):
        """
        Return the current price (discount_price if available, otherwise price).
        """
        return self.discount_price if self.discount_price else self.price

