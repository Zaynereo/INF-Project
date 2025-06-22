from django.contrib import admin
from .models import Order, OrderItem, OrderHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer', 'total_amount', 'order_date']
    list_filter = ['order_date']
    search_fields = ['order_id', 'customer__username']
    readonly_fields = ['order_id', 'order_date']
    inlines = [OrderItemInline]
    ordering = ['-order_date']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order_item_id', 'order', 'product', 'quantity']
    search_fields = ['order__order_id', 'product__name']
    readonly_fields = ['order_item_id']


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_id', 'created_by__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
