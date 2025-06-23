from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from .models import Order, OrderItem, OrderHistory
from cart.models import Cart, CartItem
from accounts.models import Address


class CheckoutView(CreateView):
    """Checkout process"""
    model = Order
    template_name = 'orders/checkout.html'
    fields = ['shipping_address', 'billing_address', 'payment_method', 'notes']
    
    def get_context_data(self, **kwargs):
        """Add cart and addresses to context"""
        context = super().get_context_data(**kwargs)
        cart = Cart.objects.filter(user=self.request.user, is_active=True).first()
        if cart:
            context['cart'] = cart
            context['cart_items'] = cart.items.all()
            context['total_amount'] = cart.total_amount
        context['addresses'] = Address.objects.filter(customer=self.request.user.customer_profile)
        return context
    
    def form_valid(self, form):
        """Process the order"""
        cart = Cart.objects.filter(user=self.request.user, is_active=True).first()
        if not cart or not cart.items.exists():
            messages.error(self.request, 'Your cart is empty.')
            return redirect('cart:cart_detail')
        
        # Create order
        form.instance.customer = self.request.user
        form.instance.total_amount = cart.total_amount
        form.instance.subtotal = cart.total_amount
        order = form.save()
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
                total_price=cart_item.total_price
            )
        
        # Clear cart
        cart.clear()
        
        # Create order history
        OrderHistory.objects.create(
            order=order,
            status='pending',
            created_by=self.request.user
        )
        
        messages.success(self.request, f'Order #{order.order_number} created successfully!')
        return redirect('orders:order_detail', pk=order.pk)


class OrderDetailView(DetailView):
    """Display order details"""
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        """Only allow users to view their own orders"""
        return Order.objects.filter(customer=self.request.user)


class OrderCancelView(UpdateView):
    """Cancel an order"""
    model = Order
    fields = []
    template_name = 'orders/order_cancel.html'
    
    def get_queryset(self):
        """Only allow users to cancel their own orders"""
        return Order.objects.filter(customer=self.request.user, status='pending')
    
    def form_valid(self, form):
        """Cancel the order"""
        order = form.instance
        order.status = 'cancelled'
        order.save()
        
        # Create order history
        OrderHistory.objects.create(
            order=order,
            status='cancelled',
            created_by=self.request.user,
            notes='Order cancelled by customer'
        )
        
        messages.success(self.request, f'Order #{order.order_number} has been cancelled.')
        return redirect('orders:order_detail', pk=order.pk)


class OrderTrackView(DetailView):
    """Track order by order number"""
    model = Order
    template_name = 'orders/order_track.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_context_data(self, **kwargs):
        """Add order history to context"""
        context = super().get_context_data(**kwargs)
        context['order_history'] = self.object.history.all().order_by('-created_at')
        return context


class PaymentView(DetailView):
    """Payment processing page"""
    model = Order
    template_name = 'orders/payment.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        """Only allow users to pay for their own orders"""
        return Order.objects.filter(customer=self.request.user, payment_status='pending')


class PaymentSuccessView(UpdateView):
    """Handle successful payment"""
    model = Order
    fields = []
    template_name = 'orders/payment_success.html'
    
    def get_queryset(self):
        """Only allow users to update their own orders"""
        return Order.objects.filter(customer=self.request.user)
    
    def form_valid(self, form):
        """Update payment status"""
        order = form.instance
        order.payment_status = 'paid'
        order.status = 'confirmed'
        order.save()
        
        # Create order history
        OrderHistory.objects.create(
            order=order,
            status='confirmed',
            created_by=self.request.user,
            notes='Payment received'
        )
        
        messages.success(self.request, f'Payment for order #{order.order_number} was successful!')
        return redirect('orders:order_detail', pk=order.pk)


class PaymentCancelView(DetailView):
    """Handle cancelled payment"""
    model = Order
    template_name = 'orders/payment_cancel.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        """Only allow users to view their own orders"""
        return Order.objects.filter(customer=self.request.user)


# AJAX views for real-time updates
def update_order_status_ajax(request, order_id):
    """Update order status via AJAX (admin only)"""
    if request.method == 'POST' and request.user.is_staff:
        order = get_object_or_404(Order, pk=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.ORDER_STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            # Create order history
            OrderHistory.objects.create(
                order=order,
                status=new_status,
                created_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Order status updated to {new_status}',
                'new_status': new_status
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def get_order_tracking_ajax(request, order_number):
    """Get order tracking info via AJAX"""
    if request.method == 'GET':
        try:
            order = Order.objects.get(order_number=order_number)
            history = order.history.all().order_by('-created_at')
            
            return JsonResponse({
                'success': True,
                'order': {
                    'number': order.order_number,
                    'status': order.status,
                    'total_amount': str(order.total_amount),
                    'order_date': order.order_date.isoformat(),
                },
                'history': [
                    {
                        'status': h.status,
                        'notes': h.notes,
                        'created_at': h.created_at.isoformat(),
                    } for h in history
                ]
            })
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})
