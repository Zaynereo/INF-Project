from django.shortcuts import render
from django.db.models import Q
from django.db import connection
from .models import Product, Category, Brand

def home(request):
    """
    A view that retrieves all products, categories, and brands from the database
    and prepares them to be displayed on the homepage, with filtering and sorting.
    """
    # Get filter and sort parameters
    sort_by = request.GET.get('sort', 'name_asc')
    selected_brands = request.GET.getlist('brand')
    selected_categories = request.GET.getlist('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Base query
    query = """
        SELECT p.*, b.name as brand_name, c.name as category_name
        FROM product p
        LEFT JOIN brand b ON p.brand_id = b.brand_id
        LEFT JOIN category c ON p.category_id = c.category_id
    """
    params = []
    where_clauses = []

    # Brand filter
    if selected_brands:
        where_clauses.append(f"p.brand_id IN ({','.join(['%s'] * len(selected_brands))})")
        params.extend(selected_brands)

    # Category filter
    if selected_categories:
        where_clauses.append(f"p.category_id IN ({','.join(['%s'] * len(selected_categories))})")
        params.extend(selected_categories)

    # Price filter
    if min_price:
        where_clauses.append("p.sale_price >= %s")
        params.append(min_price)
    if max_price:
        where_clauses.append("p.sale_price <= %s")
        params.append(max_price)
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    # Sorting
    if sort_by == 'price_asc':
        query += " ORDER BY p.sale_price ASC"
    elif sort_by == 'price_desc':
        query += " ORDER BY p.sale_price DESC"
    elif sort_by == 'name_desc':
        query += " ORDER BY p.name DESC"
    else: # name_asc
        query += " ORDER BY p.name ASC"

    with connection.cursor() as cursor:
        # Fetch filtered products
        cursor.execute(query, params)
        product_columns = [col[0] for col in cursor.description]
        products = [dict(zip(product_columns, row)) for row in cursor.fetchall()]

        # Fetch all categories and brands for filter options
        cursor.execute("SELECT * FROM category ORDER BY name")
        category_columns = [col[0] for col in cursor.description]
        categories = [dict(zip(category_columns, row)) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM brand ORDER BY name")
        brand_columns = [col[0] for col in cursor.description]
        brands = [dict(zip(brand_columns, row)) for row in cursor.fetchall()]

    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'sort_by': sort_by,
        'selected_brands': [int(b) for b in selected_brands],
        'selected_categories': [int(c) for c in selected_categories],
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'home.html', context)

def category_products(request, category_id):
    """
    A view to display products belonging to a specific category.
    """
    category = Category.objects.get(pk=category_id)
    products = Product.objects.filter(category=category)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'category_products.html', context)

def brand_products(request, brand_id):
    """
    A view to display products belonging to a specific brand.
    """
    brand = Brand.objects.get(pk=brand_id)
    products = Product.objects.filter(brand=brand)
    
    context = {
        'brand': brand,
        'products': products,
    }
    return render(request, 'brand_products.html', context)

def product_detail(request, product_id):
    """
    A view to display the details of a single product.
    """
    product = Product.objects.get(pk=product_id)
    
    context = {
        'product': product,
    }
    return render(request, 'product_detail.html', context)

def product_search(request):
    """
    A view to search products by name, brand, category, and subcategory.
    """
    query = request.GET.get('q', '')
    products = []
    
    if query:
        # Use raw SQL to search across multiple tables
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT p.*, b.name as brand_name, c.name as category_name, s.name as subcategory_name
                FROM product p
                LEFT JOIN brand b ON p.brand_id = b.brand_id
                LEFT JOIN category c ON p.category_id = c.category_id
                LEFT JOIN subcategory s ON p.subcategory_id = s.subcategory_id
                WHERE p.name ILIKE %s 
                   OR b.name ILIKE %s 
                   OR c.name ILIKE %s 
                   OR s.name ILIKE %s
                ORDER BY p.name
            """, [f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'])
            
            columns = [col[0] for col in cursor.description]
            products = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    context = {
        'products': products,
        'query': query,
        'results_count': len(products) if products else 0,
    }
    return render(request, 'products/product_search.html', context)
