from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Cart management
    path('', views.CartView.as_view(), name='cart_detail'),
    path('add/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('update/<int:item_id>/', views.UpdateCartItemView.as_view(), name='update_cart_item'),
    path('remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('clear/', views.ClearCartView.as_view(), name='clear_cart'),
    
    # AJAX endpoints
    path('ajax/add/<int:product_id>/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('ajax/update/<int:item_id>/', views.update_cart_item_ajax, name='update_cart_item_ajax'),
    path('ajax/remove/<int:item_id>/', views.remove_from_cart_ajax, name='remove_from_cart_ajax'),
    
    # Wishlist
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    
    # Coupons
    path('coupon/apply/', views.ApplyCouponView.as_view(), name='apply_coupon'),
    path('coupon/remove/', views.RemoveCouponView.as_view(), name='remove_coupon'),
] 