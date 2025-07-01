from django.shortcuts import render, redirect
from django.db.models import Q
from django.db import connection
from .models import Product, Category, Brand
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from .forms import ProductForm, ReviewForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from connection import get_mongo_connection # for mongo connection
from bson.objectid import ObjectId
from datetime import datetime, timezone
from django.http import HttpResponseForbidden

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
        cursor.execute("""
            SELECT s.*, c.name as category_name 
            FROM subcategory s 
            JOIN category c ON s.category_id = c.category_id 
            ORDER BY c.name, s.name
        """)
        subcategory_columns = [col[0] for col in cursor.description]
        subcategories = [dict(zip(subcategory_columns, row)) for row in cursor.fetchall()]

        # Fetch all suppliers and their supplies (with product info and cost price)
        cursor.execute("""
            SELECT s.supplier_id, s.name AS supplier_name, s.contact, 
                   p.product_id, p.name AS product_name, sp.cost_price, sp.supply_id, sp.supply_date
            FROM supplier s
            JOIN supplies sp ON s.supplier_id = sp.supplier_id
            JOIN product p ON sp.product_id = p.product_id
            ORDER BY s.name, p.name
        """)
        supplier_rows = cursor.fetchall()
        suppliers = {}
        for row in supplier_rows:
            supplier_id, supplier_name, contact, product_id, product_name, cost_price, supply_id, supply_date = row
            if supplier_id not in suppliers:
                suppliers[supplier_id] = {
                    'supplier_id': supplier_id,
                    'supplier_name': supplier_name,
                    'contact': contact,
                    'supplies': []
                }
            suppliers[supplier_id]['supplies'].append({
                'product_id': product_id,
                'product_name': product_name,
                'cost_price': cost_price,
                'supply_id': supply_id,
                'supply_date': supply_date
            })
        suppliers = list(suppliers.values())

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
        'suppliers': suppliers,
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
    
    # Get random testimonials from reviews
    db = get_mongo_connection()
    if db is not None:
        # Get 5 random reviews with customer names and product names, excluding admin reviews
        random_reviews = list(db.ProductReviews.aggregate([
            { "$sample": { "size": 10 } },  # Sample more to account for admin filtering
            { "$lookup": {
                "from": "ProductReviews",
                "localField": "product_id",
                "foreignField": "product_id",
                "as": "product_info"
            }}
        ]))
        
        # Get customer names and product names for these reviews
        if random_reviews:
            customer_ids = list(set([r["customer_id"] for r in random_reviews]))
            product_ids = list(set([r["product_id"] for r in random_reviews]))
            
            with connection.cursor() as cursor:
                # Get customer names, excluding admin users
                if customer_ids:
                    format_strings = ','.join(['%s'] * len(customer_ids))
                    cursor.execute(f"""
                        SELECT customer_id, name 
                        FROM customer 
                        WHERE customer_id IN ({format_strings}) AND (is_admin IS NULL OR is_admin = FALSE)
                    """, customer_ids)
                    customers = {row[0]: row[1] for row in cursor.fetchall()}
                else:
                    customers = {}
                
                # Get product names
                if product_ids:
                    format_strings = ','.join(['%s'] * len(product_ids))
                    cursor.execute(f"""
                        SELECT product_id, name 
                        FROM product 
                        WHERE product_id IN ({format_strings})
                    """, product_ids)
                    products_dict = {row[0]: row[1] for row in cursor.fetchall()}
                else:
                    products_dict = {}
            
            # Add customer names and product names to reviews, excluding admin reviews
            testimonials = []
            for review in random_reviews:
                # Only include reviews from non-admin customers
                if review['customer_id'] in customers:
                    testimonials.append({
                        'review': review.get('review', ''),
                        'customer_name': customers.get(review['customer_id'], 'Anonymous'),
                        'product_name': products_dict.get(review['product_id'], 'Product'),
                        'rating': review.get('rating', 0)
                    })
                    
                    # Stop when we have 5 testimonials
                    if len(testimonials) >= 5:
                        break
            
            context['testimonials'] = testimonials
        else:
            context['testimonials'] = []
    else:
        context['testimonials'] = []
    
    return render(request, 'home.html', context)

def category_products(request, category_id):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT p.*, b.name as brand_name, c.name as category_name
            FROM product p
            LEFT JOIN brand b ON p.brand_id = b.brand_id
            LEFT JOIN category c ON p.category_id = c.category_id
            WHERE p.category_id = %s
        ''', [category_id])
        columns = [col[0] for col in cursor.description]
        products = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.execute('SELECT * FROM category WHERE category_id = %s', [category_id])
        category_row = cursor.fetchone()
        category = dict(zip([col[0] for col in cursor.description], category_row)) if category_row else None

    context = {
        'products': products,
        'category': category,
    }
    return render(request, 'products/category_products.html', context)

def brand_products(request, brand_id):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT p.*, b.name as brand_name, c.name as category_name
            FROM product p
            LEFT JOIN brand b ON p.brand_id = b.brand_id
            LEFT JOIN category c ON p.category_id = c.category_id
            WHERE p.brand_id = %s
        ''', [brand_id])
        columns = [col[0] for col in cursor.description]
        products = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.execute('SELECT * FROM brand WHERE brand_id = %s', [brand_id])
        brand_row = cursor.fetchone()
        brand = dict(zip([col[0] for col in cursor.description], brand_row)) if brand_row else None

    context = {
        'products': products,
        'brand': brand,
    }
    return render(request, 'products/brand_products.html', context)

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
        category_id = request.POST.get('category_id', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Subcategory name is required.'}, status=400)
        if not category_id:
            return JsonResponse({'success': False, 'error': 'Category is required for subcategory.'}, status=400)
        with connection.cursor() as cursor:
            # Check for duplicate
            cursor.execute('SELECT subcategory_id FROM subcategory WHERE name = %s AND category_id = %s', [name, category_id])
            if cursor.fetchone():
                return JsonResponse({'success': False, 'error': 'Subcategory already exists in this category.'}, status=400)
            cursor.execute('INSERT INTO subcategory (name, category_id) VALUES (%s, %s) RETURNING subcategory_id', [name, category_id])
            subcategory_id = cursor.fetchone()[0]
        return JsonResponse({'success': True, 'subcategory': {'subcategory_id': subcategory_id, 'name': name, 'category_id': category_id}})
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
def get_subcategories_for_category(request, category_id):
    """Get all subcategories for a specific category"""
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        with connection.cursor() as cursor:
            cursor.execute('SELECT subcategory_id, name FROM subcategory WHERE category_id = %s ORDER BY name', [category_id])
            subcategories = [{'subcategory_id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        return JsonResponse({'success': True, 'subcategories': subcategories})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@admin_required
@csrf_exempt
def get_all_subcategories(request):
    """Get all subcategories with their category information"""
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT s.subcategory_id, s.name, s.category_id, c.name as category_name 
                FROM subcategory s 
                JOIN category c ON s.category_id = c.category_id 
                ORDER BY c.name, s.name
            ''')
            subcategories = [{'subcategory_id': row[0], 'name': row[1], 'category_id': row[2], 'category_name': row[3]} for row in cursor.fetchall()]
        return JsonResponse({'success': True, 'subcategories': subcategories})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@admin_required
@csrf_exempt
def update_subcategory_category(request, subcategory_id):
    """Update a subcategory's category"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        category_id = request.POST.get('category_id', '').strip()
        if not category_id:
            return JsonResponse({'success': False, 'error': 'Category ID is required.'}, status=400)
        
        with connection.cursor() as cursor:
            # Check if the subcategory exists
            cursor.execute('SELECT name FROM subcategory WHERE subcategory_id = %s', [subcategory_id])
            subcategory = cursor.fetchone()
            if not subcategory:
                return JsonResponse({'success': False, 'error': 'Subcategory not found.'}, status=400)
            
            # Check if the category exists
            cursor.execute('SELECT name FROM category WHERE category_id = %s', [category_id])
            category = cursor.fetchone()
            if not category:
                return JsonResponse({'success': False, 'error': 'Category not found.'}, status=400)
            
            # Check for duplicate subcategory name in the target category
            cursor.execute('SELECT subcategory_id FROM subcategory WHERE name = %s AND category_id = %s AND subcategory_id != %s', [subcategory[0], category_id, subcategory_id])
            if cursor.fetchone():
                return JsonResponse({'success': False, 'error': 'A subcategory with this name already exists in the target category.'}, status=400)
            
            # Update the subcategory's category
            cursor.execute('UPDATE subcategory SET category_id = %s WHERE subcategory_id = %s', [category_id, subcategory_id])
            
        return JsonResponse({'success': True, 'message': 'Subcategory linked successfully.'})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@admin_required
@csrf_exempt
def get_product(request, product_id):
    """Return product data as JSON for editing."""
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT product_id, name, description, brand_id, category_id, subcategory_id, market_price, sale_price, unit, stock_level, rating
                FROM product WHERE product_id = %s
            ''', [product_id])
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'success': False, 'error': 'Product not found.'}, status=404)
            columns = [col[0] for col in cursor.description]
            product = dict(zip(columns, row))
        return JsonResponse({'success': True, 'product': product})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@admin_required
@csrf_exempt
def update_product(request, product_id):
    """Update product data via AJAX POST."""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                with connection.cursor() as cursor:
                    cursor.execute('''
                        UPDATE product SET
                            name = %s,
                            description = %s,
                            brand_id = %s,
                            category_id = %s,
                            subcategory_id = %s,
                            market_price = %s,
                            sale_price = %s,
                            unit = %s,
                            stock_level = %s,
                            rating = %s
                        WHERE product_id = %s
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
                        product_id
                    ])
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

def product_detail(request, product_id):
    """
    A view to display the details of a single product using raw SQL.
    """
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT p.*, b.name as brand_name, c.name as category_name, s.name as subcategory_name
            FROM product p
            LEFT JOIN brand b ON p.brand_id = b.brand_id
            LEFT JOIN category c ON p.category_id = c.category_id
            LEFT JOIN subcategory s ON p.subcategory_id = s.subcategory_id
            WHERE p.product_id = %s
        ''', [product_id])
        row = cursor.fetchone()
        if not row:
            return render(request, '404.html', status=404)
        columns = [col[0] for col in cursor.description]
        product = dict(zip(columns, row))

    # mongo

    db = get_mongo_connection()
    product = Product.objects.get(pk=product_id)

    if request.method == "POST":
        if not request.session.get("customer_id"):
            return redirect("accounts:login")
        
        form = ReviewForm(request.POST)
        if form.is_valid():
            db.ProductReviews.insert_one({
                "product_id": int(product_id),
                "customer_id": int(request.session["customer_id"]),
                "rating": float(form.cleaned_data["rating"]),
                "review": form.cleaned_data["review"],
                "timestamp": datetime.now(timezone.utc),
                "votes": []
            })
            return redirect("products:product_detail", product_id=product_id)
    else:
        form = ReviewForm()
    
     #  Get sort option from query string (?sort=helpful)
    sort_option = request.GET.get("sort", "recent")
    
    #  Call helper function to get all sorted review categories
    customer_id = request.session.get("customer_id")
    sorted_reviews = get_sorted_reviews(product_id, customer_id)

    #  Choose which set of reviews to show based on the option
    if sort_option == "helpful":
        reviews_to_show = sorted_reviews["most_helpful"]
    elif sort_option == "lowest":
        reviews_to_show = sorted_reviews["lowest_rated"]
    elif sort_option == "recent":
        reviews_to_show = sorted_reviews["most_recent"]
    else:  # default is "all"
        reviews_to_show = sorted_reviews["all"]

    #  Add review_id for rendering buttons
    for r in reviews_to_show:
        r["review_id"] = str(r["_id"])

    #  Render with the selected review list
    return render(request, "products/product_detail.html", {
        "product": product,
        "reviews": reviews_to_show,
        "form": form,
        "sort": sort_option
    })


def edit_review(request, product_id, review_id):
    db = get_mongo_connection()
    review = db.ProductReviews.find_one({"_id": ObjectId(review_id)})

    if not review:
        return HttpResponseForbidden("Review not found.")
    
    if review["customer_id"] != request.session.get("customer_id"):
        return HttpResponseForbidden("You are not allowed to edit this review.")
    
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            db.ProductReviews.update_one(
                {"_id": ObjectId(review_id)},
                {"$set": {
                    "rating": float(form.cleaned_data["rating"]),
                    "review": form.cleaned_data["review"]
                }}
            )
            return redirect("products:product_detail", product_id=product_id)
    else:
        form = ReviewForm(initial={
            "rating": review["rating"],
            "review": review["review"]
        })
    return render(request, "products/edit_review.html", {"form": form, "product_id": product_id})

def delete_review(request, product_id, review_id):
    db = get_mongo_connection()
    review = db.ProductReviews.find_one({"_id": ObjectId(review_id)})

    if not review or review["customer_id"] != request.session.get("customer_id"):
        return HttpResponseForbidden("You are not allowed to delete this review.")
    
    db.ProductReviews.delete_one({"_id": ObjectId(review_id)})
    return redirect("products:product_detail", product_id=product_id)

def get_sorted_reviews(product_id, customer_id):
    db = get_mongo_connection()

    # Handle case when user is not logged in (customer_id is None)
    user_voted_condition = {}
    if customer_id is not None:
        user_voted_condition = {
            "user_voted": {
                "$in": [int(customer_id), { "$map": {
                    "input": "$votes",
                    "as": "v",
                    "in": "$$v.user_id"
                }}]
            }
        }

    base_pipeline = [
        { "$match": { "product_id": int(product_id) } },
        {
            "$addFields": {
                "vote_score": { "$sum": "$votes.value" },
                "upvotes": {
                    "$size": {
                        "$filter": {
                            "input": "$votes",
                            "as": "v",
                            "cond": { "$eq": ["$$v.value", 1] }
                        }
                    }
                },
                "downvotes": {
                    "$size": {
                        "$filter": {
                            "input": "$votes",
                            "as": "v",
                            "cond": { "$eq": ["$$v.value", -1] }
                        }
                    }
                },
                "user_voted": customer_id is not None and {
                    "$in": [int(customer_id), { "$map": {
                        "input": "$votes",
                        "as": "v",
                        "in": "$$v.user_id"
                    }}]
                } or False
            }
        }
    ]

    helpful = list(db.ProductReviews.aggregate(
        base_pipeline + [
            { "$match": { "vote_score": { "$gte": 1 } } },
            { "$sort": { "vote_score": -1 } },
            { "$limit": 3 }
        ]
    ))

    recent = list(db.ProductReviews.aggregate(
        base_pipeline + [
            { "$sort": { "timestamp": -1 } },
            { "$limit": 5 }
        ]
    ))

    lowest = list(db.ProductReviews.aggregate(
        base_pipeline + [
            { "$sort": { "rating": 1 } },
            { "$limit": 3 }
        ]
    ))

    all_reviews = list(db.ProductReviews.aggregate(
        base_pipeline + [
            { "$sort": { "timestamp": -1 } }
        ]
    ))
    
    # Get customer names for all reviews
    customer_ids = list(set([r["customer_id"] for r in helpful + recent + lowest + all_reviews]))
    
    # Get customer data from PostgreSQL
    with connection.cursor() as cursor:
        if customer_ids:
            format_strings = ','.join(['%s'] * len(customer_ids))
            cursor.execute(f"""
                SELECT customer_id, name 
                FROM customer 
                WHERE customer_id IN ({format_strings})
            """, customer_ids)
            customers = {row[0]: row[1] for row in cursor.fetchall()}
        else:
            customers = {}
    
    # Add customer names and review_id to all reviews
    for r in helpful + recent + lowest + all_reviews:
        r["review_id"] = str(r["_id"])
        r["customer_name"] = customers.get(r["customer_id"], "Anonymous")

    return {
        "most_helpful": helpful,
        "most_recent": recent,
        "lowest_rated": lowest,
        "all": all_reviews
    }

def vote_review(request, review_id):
    if not request.session.get("customer_id"):
        return redirect("accounts:login")
    
    db = get_mongo_connection()

    user_id = int(request.session["customer_id"])
    vote_value = int(request.POST.get("vote"))  # 1 or -1

    review = db.ProductReviews.find_one({"_id": ObjectId(review_id)})
    if not review:
        return redirect("products:product_detail", product_id=review["product_id"])

    product_id = review["product_id"]
    votes = review.get("votes", [])

    updated = False
    new_votes = []
    for v in votes:
        if v.get("user_id") == user_id:
            if v.get("value") != vote_value:
                # Change vote (e.g., from upvote to downvote)
                new_votes.append({"user_id": user_id, "value": vote_value})
            else:
                # Same vote again, skip adding (to prevent duplicate)
                new_votes.append(v)
            updated = True
        else:
            new_votes.append(v)

    if not updated:
        # User has not voted before → add new
        new_votes.append({"user_id": user_id, "value": vote_value})

    db.ProductReviews.update_one(
        {"_id": ObjectId(review_id)},
        {"$set": {"votes": new_votes}}
    )

    return redirect("products:product_detail", product_id=product_id)

@admin_required
@csrf_exempt
def add_supplier(request):
    if request.method == 'POST':
        supplier_name = request.POST.get('supplier_name', '').strip()
        contact = request.POST.get('contact', '').strip()
        product_id = request.POST.get('product_id', '').strip()
        cost_price = request.POST.get('cost_price', '').strip()
        supply_date = request.POST.get('supply_date', '').strip()
        errors = {}
        if not supplier_name:
            errors['supplier_name'] = 'Supplier name is required.'
        if not contact:
            errors['contact'] = 'Contact is required.'
        if not product_id:
            errors['product_id'] = 'Product is required.'
        if not cost_price:
            errors['cost_price'] = 'Cost price is required.'
        if not supply_date:
            errors['supply_date'] = 'Supply date is required.'
        if errors:
            # For AJAX, return JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'errors': errors}, status=400)
            # For normal POST, re-render page with errors (not typical for modal)
            messages.error(request, 'Please correct the errors in the form.')
            return redirect('products:manage_products')
        with connection.cursor() as cursor:
            # Enforce unique supplier name
            cursor.execute('SELECT supplier_id FROM supplier WHERE name = %s', [supplier_name])
            row = cursor.fetchone()
            if row:
                supplier_id = row[0]
            else:
                cursor.execute('INSERT INTO supplier (name, contact) VALUES (%s, %s) RETURNING supplier_id', [supplier_name, contact])
                supplier_id = cursor.fetchone()[0]
            # Insert into supplies
            cursor.execute('''
                INSERT INTO supplies (supplier_id, product_id, supply_date, cost_price)
                VALUES (%s, %s, %s, %s)
            ''', [supplier_id, product_id, supply_date, cost_price])
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('products:manage_products')
    else:
        return HttpResponseForbidden('Invalid request method.')

@admin_required
@csrf_exempt
def delete_supplier(request, supplier_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            # Delete all supplies for this supplier
            cursor.execute('DELETE FROM supplies WHERE supplier_id = %s', [supplier_id])
            # Delete the supplier
            cursor.execute('DELETE FROM supplier WHERE supplier_id = %s', [supplier_id])
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('products:manage_products')
    else:
        return HttpResponseForbidden('Invalid request method.')

@admin_required
@csrf_exempt
def edit_supplier(request, supplier_id):
    if request.method == 'POST':
        supplier_name = request.POST.get('supplier_name', '').strip()
        contact = request.POST.get('contact', '').strip()
        errors = {}
        if not supplier_name:
            errors['supplier_name'] = 'Supplier name is required.'
        if not contact:
            errors['contact'] = 'Contact is required.'
        if errors:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'errors': errors}, status=400)
            messages.error(request, 'Please correct the errors in the form.')
            return redirect('products:manage_products')
        with connection.cursor() as cursor:
            # Enforce unique supplier name (cannot change to a name that already exists for another supplier)
            cursor.execute('SELECT supplier_id FROM supplier WHERE name = %s AND supplier_id != %s', [supplier_name, supplier_id])
            if cursor.fetchone():
                errors['supplier_name'] = 'A supplier with this name already exists.'
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'errors': errors}, status=400)
                messages.error(request, 'A supplier with this name already exists.')
                return redirect('products:manage_products')
            cursor.execute('UPDATE supplier SET name = %s, contact = %s WHERE supplier_id = %s', [supplier_name, contact, supplier_id])
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('products:manage_products')
    else:
        return HttpResponseForbidden('Invalid request method.')

@admin_required
@csrf_exempt
def edit_supply(request, supply_id):
    if request.method == 'POST':
        cost_price = request.POST.get('cost_price', '').strip()
        supply_date = request.POST.get('supply_date', '').strip()
        errors = {}
        if not cost_price:
            errors['cost_price'] = 'Cost price is required.'
        if not supply_date:
            errors['supply_date'] = 'Supply date is required.'
        if errors:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'errors': errors}, status=400)
            messages.error(request, 'Please correct the errors in the form.')
            return redirect('products:manage_products')
        with connection.cursor() as cursor:
            cursor.execute('UPDATE supplies SET cost_price = %s, supply_date = %s WHERE supply_id = %s', [cost_price, supply_date, supply_id])
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('products:manage_products')
    else:
        return HttpResponseForbidden('Invalid request method.')

@admin_required
@csrf_exempt
def delete_supply(request, supply_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM supplies WHERE supply_id = %s', [supply_id])
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('products:manage_products')
    else:
        return HttpResponseForbidden('Invalid request method.')

@admin_required
@csrf_exempt
def add_supply(request):
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier_id', '').strip()
        product_id = request.POST.get('product_id', '').strip()
        cost_price = request.POST.get('cost_price', '').strip()
        supply_date = request.POST.get('supply_date', '').strip()
        errors = {}
        if not supplier_id:
            errors['supplier_id'] = 'Supplier is required.'
        if not product_id:
            errors['product_id'] = 'Product is required.'
        if not cost_price:
            errors['cost_price'] = 'Cost price is required.'
        if not supply_date:
            errors['supply_date'] = 'Supply date is required.'
        if errors:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'errors': errors}, status=400)
            messages.error(request, 'Please correct the errors in the form.')
            return redirect('products:manage_products')
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO supplies (supplier_id, product_id, supply_date, cost_price)
                VALUES (%s, %s, %s, %s)
            ''', [supplier_id, product_id, supply_date, cost_price])
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('products:manage_products')
    else:
        return HttpResponseForbidden('Invalid request method.')