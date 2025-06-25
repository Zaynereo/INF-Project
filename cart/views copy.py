from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from .models import Cart, CartItem, Wishlist, Coupon, CouponUsage
from products.models import Product


class CartView(LoginRequiredMixin, ListView):
    """Display shopping cart"""
    model = CartItem
    template_name = 'cart/cart_detail.html'
    context_object_name = 'cart_items'
    
    def get_queryset(self):
        """Get items from user's active cart"""
        cart = Cart.objects.filter(user=self.request.user, is_active=True).first()
        if cart:
            return cart.items.all()
        return CartItem.objects.none()
    
    def get_context_data(self, **kwargs):
        """Add cart totals and coupon info"""
        context = super().get_context_data(**kwargs)
        cart = Cart.objects.filter(user=self.request.user, is_active=True).first()
        if cart:
            context['cart'] = cart
            context['total_amount'] = cart.total_amount
            context['item_count'] = cart.total_items
        return context


class AddToCartView(LoginRequiredMixin, CreateView):
    """Add product to cart"""
    model = CartItem
    fields = ['quantity']
    template_name = 'cart/add_to_cart.html'
    
    def form_valid(self, form):
        """Add product to cart"""
        product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        cart, created = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        
        # Check if product is already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': form.cleaned_data['quantity']}
        )
        
        if not created:
            cart_item.quantity += form.cleaned_data['quantity']
            cart_item.save()
        
        messages.success(self.request, f'{product.name} added to cart.')
        return redirect('cart:cart_detail')


class UpdateCartItemView(LoginRequiredMixin, UpdateView):
    """Update cart item quantity"""
    model = CartItem
    fields = ['quantity']
    template_name = 'cart/update_cart_item.html'
    success_url = reverse_lazy('cart:cart_detail')
    
    def get_queryset(self):
        """Only allow users to update their own cart items"""
        return CartItem.objects.filter(cart__user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Cart updated successfully.')
        return super().form_valid(form)


class RemoveFromCartView(LoginRequiredMixin, DeleteView):
    """Remove item from cart"""
    model = CartItem
    template_name = 'cart/remove_from_cart.html'
    success_url = reverse_lazy('cart:cart_detail')
    
    def get_queryset(self):
        """Only allow users to remove their own cart items"""
        return CartItem.objects.filter(cart__user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Item removed from cart.')
        return super().delete(request, *args, **kwargs)


class ClearCartView(LoginRequiredMixin, DeleteView):
    """Clear entire cart"""
    model = Cart
    template_name = 'cart/clear_cart.html'
    success_url = reverse_lazy('cart:cart_detail')
    
    def get_queryset(self):
        """Only allow users to clear their own cart"""
        return Cart.objects.filter(user=self.request.user, is_active=True)
    
    def delete(self, request, *args, **kwargs):
        cart = self.get_object()
        cart.clear()
        messages.success(request, 'Cart cleared successfully.')
        return redirect(self.success_url)


class WishlistView(LoginRequiredMixin, ListView):
    """Display user's wishlist"""
    model = Wishlist
    template_name = 'cart/wishlist.html'
    context_object_name = 'wishlist_items'
    paginate_by = 12
    
    def get_queryset(self):
        """Get wishlist items for current user"""
        return Wishlist.objects.filter(user=self.request.user).select_related('product')


class AddToWishlistView(LoginRequiredMixin, CreateView):
    """Add product to wishlist"""
    model = Wishlist
    fields = []
    template_name = 'cart/add_to_wishlist.html'
    
    def form_valid(self, form):
        """Add product to wishlist"""
        product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=self.request.user,
            product=product
        )
        
        if created:
            messages.success(self.request, f'{product.name} added to wishlist.')
        else:
            messages.info(self.request, f'{product.name} is already in your wishlist.')
        
        return redirect('cart:wishlist')


class RemoveFromWishlistView(LoginRequiredMixin, DeleteView):
    """Remove product from wishlist"""
    model = Wishlist
    template_name = 'cart/remove_from_wishlist.html'
    success_url = reverse_lazy('cart:wishlist')
    
    def get_queryset(self):
        """Only allow users to remove their own wishlist items"""
        return Wishlist.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Item removed from wishlist.')
        return super().delete(request, *args, **kwargs)


class ApplyCouponView(LoginRequiredMixin, CreateView):
    """Apply coupon to cart"""
    model = CouponUsage
    fields = []
    template_name = 'cart/apply_coupon.html'
    
    def form_valid(self, form):
        """Apply coupon to cart"""
        coupon_code = self.request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            
            if not coupon.is_valid:
                messages.error(self.request, 'This coupon has expired or is no longer valid.')
                return redirect('cart:cart_detail')
            
            cart = Cart.objects.filter(user=self.request.user, is_active=True).first()
            if not cart:
                messages.error(self.request, 'Your cart is empty.')
                return redirect('cart:cart_detail')
            
            if cart.total_amount < coupon.min_order_amount:
                messages.error(self.request, f'Minimum order amount of ${coupon.min_order_amount} required.')
                return redirect('cart:cart_detail')
            
            # Check if coupon already used by this user
            if CouponUsage.objects.filter(coupon=coupon, user=self.request.user).exists():
                messages.error(self.request, 'You have already used this coupon.')
                return redirect('cart:cart_detail')
            
            messages.success(self.request, f'Coupon "{coupon.code}" applied successfully!')
            return redirect('cart:cart_detail')
            
        except Coupon.DoesNotExist:
            messages.error(self.request, 'Invalid coupon code.')
            return redirect('cart:cart_detail')


class RemoveCouponView(LoginRequiredMixin, DeleteView):
    """Remove coupon from cart"""
    model = CouponUsage
    template_name = 'cart/remove_coupon.html'
    success_url = reverse_lazy('cart:cart_detail')
    
    def get_queryset(self):
        """Only allow users to remove their own coupon usages"""
        return CouponUsage.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Coupon removed from cart.')
        return super().delete(request, *args, **kwargs)


# AJAX views for dynamic functionality
def add_to_cart_ajax(request, product_id):
    """Add product to cart via AJAX"""
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            product = Product.objects.get(pk=product_id)
            quantity = int(request.POST.get('quantity', 1))
            
            cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart',
                'cart_count': cart.total_items,
                'cart_total': str(cart.total_amount)
            })
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid quantity'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def update_cart_item_ajax(request, item_id):
    """Update cart item quantity via AJAX"""
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(
                pk=item_id,
                cart__user=request.user,
                cart__is_active=True
            )
            quantity = int(request.POST.get('quantity', 1))
            
            if quantity <= 0:
                cart_item.delete()
                message = 'Item removed from cart'
            else:
                cart_item.quantity = quantity
                cart_item.save()
                message = 'Cart updated successfully'
            
            cart = cart_item.cart
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_count': cart.total_items,
                'cart_total': str(cart.total_amount),
                'item_total': str(cart_item.total_price)
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cart item not found'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid quantity'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def remove_from_cart_ajax(request, item_id):
    """Remove item from cart via AJAX"""
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(
                pk=item_id,
                cart__user=request.user,
                cart__is_active=True
            )
            cart = cart_item.cart
            cart_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Item removed from cart',
                'cart_count': cart.total_items,
                'cart_total': str(cart.total_amount)
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cart item not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def add_to_wishlist_ajax(request, product_id):
    """Add product to wishlist via AJAX"""
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            product = Product.objects.get(pk=product_id)
            wishlist_item, created = Wishlist.objects.get_or_create(
                user=request.user,
                product=product
            )
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': f'{product.name} added to wishlist'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Product already in wishlist'
                })
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def search_coupons_ajax(request):
    """Search for valid coupons via AJAX"""
    if request.method == 'GET' and request.user.is_authenticated:
        query = request.GET.get('q', '')
        if query:
            coupons = Coupon.objects.filter(
                Q(code__icontains=query) | Q(description__icontains=query),
                is_active=True
            )[:10]
            
            return JsonResponse({
                'success': True,
                'coupons': [
                    {
                        'code': coupon.code,
                        'description': coupon.description,
                        'value': str(coupon.value),
                        'type': coupon.coupon_type,
                        'min_order': str(coupon.min_order_amount)
                    } for coupon in coupons
                ]
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})
