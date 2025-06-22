from django.shortcuts import render
from .models import Product, Category

def home(request):
    """
    A view that retrieves all products and categories from the database
    and prepares them to be displayed on the homepage.
    """
    products = Product.objects.all()
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'home.html', context)
