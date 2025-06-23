from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.product_search, name='product_search'),
    path('manage/', views.manage_products, name='manage_products'), # <--- ADD THIS LINE
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('brand/<int:brand_id>/', views.brand_products, name='brand_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
]