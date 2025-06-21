from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Order management
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('order/<int:pk>/cancel/', views.OrderCancelView.as_view(), name='order_cancel'),
    
    # Order tracking
    path('track/<str:order_number>/', views.OrderTrackView.as_view(), name='order_track'),
    
    # Payment
    path('payment/<int:order_id>/', views.PaymentView.as_view(), name='payment'),
    path('payment/success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/cancel/', views.PaymentCancelView.as_view(), name='payment_cancel'),
] 