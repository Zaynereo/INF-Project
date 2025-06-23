from django.contrib import admin
from .models import Category, SubCategory, Brand, Product, Supplier, Supply, ProductImage, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'name', 'description']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['subcategory_id', 'name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'category__name']
    ordering = ['category', 'name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['brand_id', 'name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'category', 'subcategory', 'brand', 'market_price', 'sale_price', 'stock_level', 'rating']
    list_filter = ['category', 'subcategory', 'brand', 'rating']
    search_fields = ['name', 'description', 'category__name', 'brand__name']
    list_editable = ['market_price', 'sale_price', 'stock_level']
    ordering = ['name']
    readonly_fields = ['product_id']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_id', 'name', 'contact']
    search_fields = ['name', 'contact']
    ordering = ['name']


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ['supply_id', 'supplier', 'product', 'supply_date', 'cost_price']
    list_filter = ['supplier', 'supply_date']
    search_fields = ['supplier__name', 'product__name']
    ordering = ['-supply_date']
    readonly_fields = ['supply_id']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'alt_text', 'is_primary']
    list_filter = ['is_primary', 'product']
    search_fields = ['product__name', 'alt_text']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'rating', 'title', 'is_approved']
    list_filter = ['rating', 'is_approved', 'product']
    search_fields = ['product__name', 'user__username', 'title']
    list_editable = ['is_approved']
