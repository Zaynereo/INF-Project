from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('list/', views.order_list_view, name='order_list'),
    path('detail/<int:order_id>/', views.order_detail_view, name='order_detail'),
] 