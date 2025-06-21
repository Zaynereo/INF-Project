from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Home page and product listing
    path('', views.ProductListView.as_view(), name='product_list'),
    path('category/<slug:category_slug>/', views.CategoryProductListView.as_view(), name='category_products'),
    path('brand/<slug:brand_slug>/', views.BrandProductListView.as_view(), name='brand_products'),
    
    # Product details
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/review/', views.ProductReviewView.as_view(), name='product_review'),
    
    # Search and filtering
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    path('filter/', views.ProductFilterView.as_view(), name='product_filter'),
    
    # Admin product management (for staff users)
    path('admin/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('admin/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('admin/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
] 