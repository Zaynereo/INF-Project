from django.contrib import admin
from .models import Supplier, Order, OrderItem, Supply, OrderHistory


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact', 'email', 'phone']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


class OrderHistoryInline(admin.TabularInline):
    model = OrderHistory
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'payment_status', 'total_amount', 'item_count', 'order_date']
    list_filter = ['status', 'payment_status', 'order_date']
    search_fields = ['order_number', 'customer__username', 'customer__email', 'tracking_number']
    list_editable = ['status', 'payment_status']
    readonly_fields = ['order_number', 'order_date', 'updated_at', 'item_count']
    inlines = [OrderItemInline, OrderHistoryInline]
    ordering = ['-order_date']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'order_date')
        }),
        ('Financial Information', {
            'fields': ('total_amount', 'subtotal', 'tax_amount', 'shipping_amount', 'discount_amount')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'billing_address', 'tracking_number', 'estimated_delivery')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status')
        }),
        ('Additional Information', {
            'fields': ('notes', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'product__name']
    readonly_fields = ['total_price', 'created_at']
    ordering = ['-created_at']


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'product', 'supply_date', 'cost_price', 'quantity', 'total_cost']
    list_filter = ['supplier', 'supply_date']
    search_fields = ['supplier__name', 'product__name']
    readonly_fields = ['total_cost', 'created_at', 'updated_at']
    ordering = ['-supply_date']


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'created_by__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
