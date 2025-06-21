from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Product, Category, Brand, ProductReview
from .forms import ProductReviewForm


class ProductListView(ListView):
    """Display all products with pagination"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        """Filter active products only"""
        return Product.objects.filter(is_active=True).select_related('category', 'brand')
    
    def get_context_data(self, **kwargs):
        """Add categories and brands to context"""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        return context


class CategoryProductListView(ListView):
    """Display products filtered by category"""
    model = Product
    template_name = 'products/category_products.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        """Filter products by category"""
        category_slug = self.kwargs['category_slug']
        return Product.objects.filter(
            category__name__iexact=category_slug.replace('-', ' '),
            is_active=True
        ).select_related('category', 'brand')
    
    def get_context_data(self, **kwargs):
        """Add category info to context"""
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category_slug']
        context['category'] = get_object_or_404(Category, name__iexact=category_slug.replace('-', ' '))
        return context


class BrandProductListView(ListView):
    """Display products filtered by brand"""
    model = Product
    template_name = 'products/brand_products.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        """Filter products by brand"""
        brand_slug = self.kwargs['brand_slug']
        return Product.objects.filter(
            brand__name__iexact=brand_slug.replace('-', ' '),
            is_active=True
        ).select_related('category', 'brand')
    
    def get_context_data(self, **kwargs):
        """Add brand info to context"""
        context = super().get_context_data(**kwargs)
        brand_slug = self.kwargs['brand_slug']
        context['brand'] = get_object_or_404(Brand, name__iexact=brand_slug.replace('-', ' '))
        return context


class ProductDetailView(DetailView):
    """Display detailed product information"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        """Include related data"""
        return Product.objects.filter(is_active=True).select_related('category', 'brand')
    
    def get_context_data(self, **kwargs):
        """Add reviews and related products to context"""
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['reviews'] = product.reviews.filter(is_approved=True).select_related('user')
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(pk=product.pk)[:4]
        context['review_form'] = ProductReviewForm()
        return context


class ProductSearchView(ListView):
    """Search products by name, description, or category"""
    model = Product
    template_name = 'products/product_search.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        """Filter products based on search query"""
        query = self.request.GET.get('q', '')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query) |
                Q(brand__name__icontains=query),
                is_active=True
            ).select_related('category', 'brand')
        return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        """Add search query to context"""
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class ProductFilterView(ListView):
    """Filter products by various criteria"""
    model = Product
    template_name = 'products/product_filter.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        """Apply filters based on request parameters"""
        queryset = Product.objects.filter(is_active=True).select_related('category', 'brand')
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__name=category)
        
        # Brand filter
        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(brand__name=brand)
        
        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Sort by
        sort_by = self.request.GET.get('sort')
        if sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add filter options to context"""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        context['filters'] = self.request.GET
        return context


class ProductReviewView(LoginRequiredMixin, CreateView):
    """Add a review to a product"""
    model = ProductReview
    form_class = ProductReviewForm
    template_name = 'products/product_review.html'
    
    def form_valid(self, form):
        """Set the product and user for the review"""
        form.instance.product = get_object_or_404(Product, pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        messages.success(self.request, 'Your review has been submitted and is pending approval.')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to product detail page"""
        return reverse_lazy('products:product_detail', kwargs={'pk': self.kwargs['pk']})


# Admin views for staff users
class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user is staff"""
    def test_func(self):
        return self.request.user.is_staff


class ProductCreateView(StaffRequiredMixin, CreateView):
    """Create a new product (staff only)"""
    model = Product
    template_name = 'products/product_form.html'
    fields = ['name', 'category', 'sub_category', 'brand', 'price', 'unit', 'stock_level', 'description', 'image', 'is_active']
    success_url = reverse_lazy('products:product_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product created successfully.')
        return super().form_valid(form)


class ProductUpdateView(StaffRequiredMixin, UpdateView):
    """Update an existing product (staff only)"""
    model = Product
    template_name = 'products/product_form.html'
    fields = ['name', 'category', 'sub_category', 'brand', 'price', 'unit', 'stock_level', 'description', 'image', 'is_active']
    
    def get_success_url(self):
        return reverse_lazy('products:product_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully.')
        return super().form_valid(form)


class ProductDeleteView(StaffRequiredMixin, DeleteView):
    """Delete a product (staff only)"""
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Product deleted successfully.')
        return super().delete(request, *args, **kwargs)


# AJAX views for dynamic functionality
def add_to_cart_ajax(request, product_id):
    """Add product to cart via AJAX"""
    if request.method == 'POST' and request.user.is_authenticated:
        product = get_object_or_404(Product, pk=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        # Get or create cart for user
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
        
        # Add or update cart item
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
            'cart_count': cart.total_items
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def add_to_wishlist_ajax(request, product_id):
    """Add product to wishlist via AJAX"""
    if request.method == 'POST' and request.user.is_authenticated:
        product = get_object_or_404(Product, pk=product_id)
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
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})
