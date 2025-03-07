from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Payment, Order
from core.services.telegram import TelegramPremiumService


@receiver(post_save, sender=Payment)
def handle_payment_status_change(sender, instance, created, **kwargs):
    """
    Handle payment status changes.
    """
    if not created and instance.status == Payment.PaymentStatus.COMPLETED:
        # Update order status
        order = instance.order
        order.status = Order.OrderStatus.PAID
        order.save()
        
        # Process the order based on product type
        process_order(order)


def process_order(order):
    """
    Process the order based on product type.
    """
    # Check if all items are processed
    all_processed = True
    
    for item in order.items.all():
        product = item.product
        
        if product.product_type == 'telegram_premium':
            # Process Telegram Premium purchase
            telegram_id = order.telegram_id
            duration_months = item.variant.duration_months if item.variant else 1
            
            try:
                # Purchase Telegram Premium
                result = TelegramPremiumService.purchase_premium(
                    telegram_id=telegram_id,
                    months=duration_months
                )
                
                if result.get('success'):
                    # Update order with transaction details
                    order.notes += f"\nTelegram Premium purchase successful: {result.get('transaction_id')}"
                else:
                    all_processed = False
                    order.notes += f"\nTelegram Premium purchase failed: {result.get('message')}"
            except Exception as e:
                all_processed = False
                order.notes += f"\nError processing Telegram Premium purchase: {str(e)}"
    
    # Update order status
    if all_processed:
        order.status = Order.OrderStatus.COMPLETED
    else:
        order.status = Order.OrderStatus.PROCESSING
    
    order.save()

