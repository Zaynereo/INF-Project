from django.shortcuts import render, redirect
from django.db.models import Q
from django.db import connection
from .models import Product, Category, Brand
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from .forms import ProductForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Decorator to check for admin status
def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            messages.error(request, "You do not have permission to access this page.")
            return redirect('products:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@admin_required
def manage_products(request):
    """
    A view for admins to see all products with extra details, sorting, and search.
    """
    sort_by = request.GET.get('sort', 'name_asc')
    search_query = request.GET.get('q', '')
    params = []
    query = """
        SELECT p.*, b.name as brand_name, c.name as category_name
        FROM product p
        LEFT JOIN brand b ON p.brand_id = b.brand_id
        LEFT JOIN category c ON p.category_id = c.category_id
        WHERE p.is_active = TRUE
    """
    if search_query:
        query += " AND (p.name ILIKE %s OR b.name ILIKE %s OR c.name ILIKE %s)"
        params.extend([f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'])
    # Sorting
    if sort_by == 'stock_asc':
        query += " ORDER BY p.stock_level ASC"
    elif sort_by == 'stock_desc':
        query += " ORDER BY p.stock_level DESC"
    elif sort_by == 'price_asc':
        query += " ORDER BY p.sale_price ASC"
    elif sort_by == 'price_desc':
        query += " ORDER BY p.sale_price DESC"
    elif sort_by == 'name_desc':
        query += " ORDER BY p.name DESC"
    else:  # name_asc
        query += " ORDER BY p.name ASC"
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        products = [dict(zip(columns, row)) for row in cursor.fetchall()]
        # Fetch all categories and brands for the add product modal
        cursor.execute("SELECT * FROM category ORDER BY name")
        category_columns = [col[0] for col in cursor.description]
        categories = [dict(zip(category_columns, row)) for row in cursor.fetchall()]
        cursor.execute("SELECT * FROM brand ORDER BY name")
        brand_columns = [col[0] for col in cursor.description]
        brands = [dict(zip(brand_columns, row)) for row in cursor.fetchall()]
        cursor.execute("SELECT * FROM subcategory ORDER BY name")
        subcategory_columns = [col[0] for col in cursor.description]
        subcategories = [dict(zip(subcategory_columns, row)) for row in cursor.fetchall()]

    # --- Order History Section ---
    # Filters
    order_customer = request.GET.get('order_customer', '')
    order_product = request.GET.get('order_product', '')
    order_start = request.GET.get('order_start', '')
    order_end = request.GET.get('order_end', '')
    order_page = int(request.GET.get('order_page', 1))
    ORDERS_PER_PAGE = 10
    order_params = []
    order_where = []
    order_query = '''
        SELECT ot.order_id, ot.order_date, cu.name as customer_name, ot.total_amount
        FROM ordertable ot
        JOIN customer cu ON ot.customer_id = cu.customer_id
    '''
    if order_customer:
        order_where.append('cu.name ILIKE %s')
        order_params.append(f'%{order_customer}%')
    if order_start:
        order_where.append('ot.order_date >= %s')
        order_params.append(order_start)
    if order_end:
        order_where.append('ot.order_date <= %s')
        order_params.append(order_end)
    if order_product:
        order_query += ' JOIN orderitem oi ON ot.order_id = oi.order_id JOIN product p2 ON oi.product_id = p2.product_id'
        order_where.append('p2.name ILIKE %s')
        order_params.append(f'%{order_product}%')
    if order_where:
        order_query += ' WHERE ' + ' AND '.join(order_where)
    order_query += ' ORDER BY ot.order_date DESC'
    # Pagination
    order_query_count = f'SELECT COUNT(*) FROM ({order_query}) as sub'
    order_query += f' LIMIT {ORDERS_PER_PAGE} OFFSET {(order_page-1)*ORDERS_PER_PAGE}'
    with connection.cursor() as cursor:
        # Get total count for pagination
        cursor.execute(order_query_count, order_params)
        total_orders = cursor.fetchone()[0]
        total_pages = (total_orders + ORDERS_PER_PAGE - 1) // ORDERS_PER_PAGE
        # Get paginated orders
        cursor.execute(order_query, order_params)
        order_columns = [col[0] for col in cursor.description]
        orders = [dict(zip(order_columns, row)) for row in cursor.fetchall()]
        # Get order details for all orders on this page
        order_ids = [o['order_id'] for o in orders]
        order_details = {}
        if order_ids:
            format_strings = ','.join(['%s'] * len(order_ids))
            cursor.execute(f'''
                SELECT oi.order_id, p.name as product_name, oi.quantity, p.sale_price
                FROM orderitem oi
                JOIN product p ON oi.product_id = p.product_id
                WHERE oi.order_id IN ({format_strings})
            ''', order_ids)
            for row in cursor.fetchall():
                order_id, product_name, quantity, sale_price = row
                order_details.setdefault(order_id, []).append({
                    'product_name': product_name,
                    'quantity': quantity,
                    'sale_price': sale_price,
                })
    context = {
        'products': products,
        'sort_by': sort_by,
        'search_query': search_query,
        'brands': brands,
        'categories': categories,
        'subcategories': subcategories,
        'orders': orders,
        'order_details': order_details,
        'order_page': order_page,
        'total_order_pages': total_pages,
        'order_customer': order_customer,
        'order_product': order_product,
        'order_start': order_start,
        'order_end': order_end,
    }
    return render(request, 'products/manage_products.html', context)

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
        WHERE p.is_active = TRUE
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
        query += " AND " + " AND ".join(where_clauses)

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

@admin_required
def delete_product(request, product_id):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute('UPDATE product SET is_active = FALSE WHERE product_id = %s', [product_id])
            messages.success(request, 'Product archived (soft deleted) successfully.')
        except Exception as e:
            messages.error(request, f'Error archiving product: {e}')
    return redirect('products:manage_products')

@admin_required
def add_product(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            with connection.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO product (name, description, brand_id, category_id, subcategory_id, market_price, sale_price, unit, stock_level, rating, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                    RETURNING product_id
                ''', [
                    data['name'],
                    data['description'],
                    data['brand'].brand_id if data['brand'] else None,
                    data['category'].category_id if data['category'] else None,
                    data['subcategory'].subcategory_id if data['subcategory'] else None,
                    data['market_price'],
                    data['sale_price'],
                    data['unit'],
                    data['stock_level'],
                    data['rating'],
                ])
                product_id = cursor.fetchone()[0]
            return JsonResponse({'success': True, 'product_id': product_id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@admin_required
@csrf_exempt
def add_brand(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get('name', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Brand name is required.'}, status=400)
        with connection.cursor() as cursor:
            # Check for duplicate
            cursor.execute('SELECT brand_id FROM brand WHERE name = %s', [name])
            if cursor.fetchone():
                return JsonResponse({'success': False, 'error': 'Brand already exists.'}, status=400)
            cursor.execute('INSERT INTO brand (name) VALUES (%s) RETURNING brand_id', [name])
            brand_id = cursor.fetchone()[0]
        return JsonResponse({'success': True, 'brand': {'brand_id': brand_id, 'name': name}})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@admin_required
@csrf_exempt
def delete_brand(request, brand_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        with connection.cursor() as cursor:
            # Check if brand is referenced by any product
            cursor.execute('SELECT COUNT(*) FROM product WHERE brand_id = %s', [brand_id])
            if cursor.fetchone()[0] > 0:
                return JsonResponse({'success': False, 'error': 'Cannot delete: This brand is used by one or more products.'}, status=400)
            cursor.execute('DELETE FROM brand WHERE brand_id = %s', [brand_id])
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@admin_required
@csrf_exempt
def delete_category(request, category_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        with connection.cursor() as cursor:
            # Check if category is referenced by any product
            cursor.execute('SELECT COUNT(*) FROM product WHERE category_id = %s', [category_id])
            if cursor.fetchone()[0] > 0:
                return JsonResponse({'success': False, 'error': 'Cannot delete: This category is used by one or more products.'}, status=400)
            cursor.execute('DELETE FROM category WHERE category_id = %s', [category_id])
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@admin_required
@csrf_exempt
def delete_subcategory(request, subcategory_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        with connection.cursor() as cursor:
            # Check if subcategory is referenced by any product
            cursor.execute('SELECT COUNT(*) FROM product WHERE subcategory_id = %s', [subcategory_id])
            if cursor.fetchone()[0] > 0:
                return JsonResponse({'success': False, 'error': 'Cannot delete: This subcategory is used by one or more products.'}, status=400)
            cursor.execute('DELETE FROM subcategory WHERE subcategory_id = %s', [subcategory_id])
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@admin_required
@csrf_exempt
def add_category(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get('name', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Category name is required.'}, status=400)
        with connection.cursor() as cursor:
            # Check for duplicate
            cursor.execute('SELECT category_id FROM category WHERE name = %s', [name])
            if cursor.fetchone():
                return JsonResponse({'success': False, 'error': 'Category already exists.'}, status=400)
            cursor.execute('INSERT INTO category (name) VALUES (%s) RETURNING category_id', [name])
            category_id = cursor.fetchone()[0]
        return JsonResponse({'success': True, 'category': {'category_id': category_id, 'name': name}})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@admin_required
@csrf_exempt
def add_subcategory(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category_id')
        if not name:
            return JsonResponse({'success': False, 'error': 'Subcategory name is required.'}, status=400)
        if not category_id:
            return JsonResponse({'success': False, 'error': 'Category is required for subcategory.'}, status=400)
        with connection.cursor() as cursor:
            # Check for duplicate
            cursor.execute('SELECT subcategory_id FROM subcategory WHERE name = %s AND category_id = %s', [name, category_id])
            if cursor.fetchone():
                return JsonResponse({'success': False, 'error': 'Subcategory already exists for this category.'}, status=400)
            cursor.execute('INSERT INTO subcategory (name, category_id) VALUES (%s, %s) RETURNING subcategory_id', [name, category_id])
            subcategory_id = cursor.fetchone()[0]
        return JsonResponse({'success': True, 'subcategory': {'subcategory_id': subcategory_id, 'name': name, 'category_id': category_id}})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)
