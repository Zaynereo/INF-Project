from django.contrib import admin
from .models import CustomerProfile, Address


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'email', 'phone', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at', 'country']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'is_verified')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Additional Information', {
            'fields': ('date_of_birth', 'profile_picture')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'address_type', 'first_name', 'last_name', 'city', 'state', 'is_default']
    list_filter = ['address_type', 'is_default', 'country', 'created_at']
    search_fields = ['customer__user__username', 'first_name', 'last_name', 'city', 'state']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-is_default', '-created_at']
    
    fieldsets = (
        ('Customer & Type', {
            'fields': ('customer', 'address_type', 'is_default')
        }),
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'company', 'phone')
        }),
        ('Address Information', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'zip_code', 'country')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
