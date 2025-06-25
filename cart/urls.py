from django.urls import path
from .views import CartView, AddToCartView, UpdateCartItemView, RemoveFromCartView, ClearCartView

app_name = 'cart'

urlpatterns = [
    path('', CartView.as_view(), name='cart_detail'),
    path('add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('update/<str:product_id>/', UpdateCartItemView.as_view(), name='update_cart_item'),
    path('remove/<str:product_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('clear/', ClearCartView.as_view(), name='clear_cart'),
]
