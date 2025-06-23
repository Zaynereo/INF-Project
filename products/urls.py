from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.product_search, name='product_search'),
    path('manage/', views.manage_products, name='manage_products'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('brand/<int:brand_id>/', views.brand_products, name='brand_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('add/', views.add_product, name='add_product'),
    path('add_brand/', views.add_brand, name='add_brand'),
    path('delete_brand/<int:brand_id>/', views.delete_brand, name='delete_brand'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('delete_subcategory/<int:subcategory_id>/', views.delete_subcategory, name='delete_subcategory'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_subcategory/', views.add_subcategory, name='add_subcategory'),
]