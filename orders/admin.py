from django.contrib import admin

from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'telegram_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__phone_number', 'telegram_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [OrderItemInline, PaymentInline]
    date_hierarchy = 'created_at'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('payment_method', 'status', 'created_at')
    search_fields = ('order__user__phone_number', 'transaction_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

