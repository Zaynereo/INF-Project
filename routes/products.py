from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, abort, current_app
from flask_login import login_required, current_user
from models import db
from models.sql_models import Product, CartItem
from sqlalchemy import or_
import os

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
def list_products():
    # Get query parameters for filtering
    category = request.args.get('category')
    search = request.args.get('search')
    sort_by = request.args.get('sort_by', 'name')  # Default sort by name
    sort_order = request.args.get('sort_order', 'asc')  # Default ascending
    
    # Start with base query
    query = Product.query
    
    # Apply filters
    if category:
        query = query.filter_by(category=category)
        
    if search:
        search = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search),
                Product.description.ilike(search),
                Product.brand.ilike(search)
            )
        )
    
    # Apply sorting
    if sort_by == 'price':
        if sort_order == 'desc':
            query = query.order_by(Product.price.desc())
        else:
            query = query.order_by(Product.price.asc())
    else:  # Default sort by name
        if sort_order == 'desc':
            query = query.order_by(Product.name.desc())
        else:
            query = query.order_by(Product.name.asc())
    
    # Get unique categories for filter dropdown
    with current_app.app_context():
        categories = [cat[0] for cat in db.session.query(Product.category).distinct()]
    
    # Get paginated results
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Items per page
    products = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        'products/list.html',
        products=products,
        categories=categories,
        current_category=category,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

@products_bp.route('/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('products/detail.html', product=product)

@products_bp.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    if quantity < 1:
        flash('Quantity must be at least 1', 'danger')
        return redirect(url_for('products.product_detail', product_id=product_id))
    
    # Check if product already in cart
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    if cart_item:
        # Update quantity if already in cart
        cart_item.quantity += quantity
    else:
        # Add new item to cart
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'Added {quantity} {product.name} to your cart', 'success')
    return redirect(request.referrer or url_for('products.list_products'))

# API endpoints for AJAX requests
@products_bp.route('/api')
def api_products():
    # Get query parameters
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    # Build query
    query = Product.query
    
    if search:
        search = f"%{search}%"
        query = query.filter(Product.name.ilike(search))
    
    if category:
        query = query.filter_by(category=category)
    
    # Execute query and format results
    products = query.limit(10).all()
    return jsonify([{
        'id': p.product_id,
        'name': p.name,
        'category': p.category,
        'price': p.price,
        'image': url_for('static', filename=f'images/products/{p.product_id}.jpg')
    } for p in products])

# Admin routes for product management
@products_bp.route('/admin')
@login_required
def admin_list():
    if not current_user.is_admin:
        abort(403)  # Forbidden
    
    products = Product.query.all()
    return render_template('admin/products/list.html', products=products)

@products_bp.route('/admin/create', methods=['GET', 'POST'])
@login_required
def admin_create():
    if not current_user.is_admin:
        abort(403)
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        category = request.form.get('category')
        sub_category = request.form.get('sub_category')
        brand = request.form.get('brand')
        price = float(request.form.get('price', 0))
        unit = request.form.get('unit')
        stock_level = int(request.form.get('stock_level', 0))
        
        # Create new product
        product = Product(
            name=name,
            category=category,
            sub_category=sub_category,
            brand=brand,
            price=price,
            unit=unit,
            stock_level=stock_level
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Handle image upload if present
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Ensure upload directory exists
                os.makedirs('static/images/products', exist_ok=True)
                # Save image with product ID as filename
                image.save(f'static/images/products/{product.product_id}.jpg')
        
        flash('Product created successfully!', 'success')
        return redirect(url_for('products.admin_list'))
    
    return render_template('admin/products/create.html')

@products_bp.route('/admin/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit(product_id):
    if not current_user.is_admin:
        abort(403)
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        # Update product details
        product.name = request.form.get('name', product.name)
        product.category = request.form.get('category', product.category)
        product.sub_category = request.form.get('sub_category', product.sub_category)
        product.brand = request.form.get('brand', product.brand)
        product.price = float(request.form.get('price', product.price))
        product.unit = request.form.get('unit', product.unit)
        product.stock_level = int(request.form.get('stock_level', product.stock_level))
        
        # Handle image upload if present
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Ensure upload directory exists
                os.makedirs('static/images/products', exist_ok=True)
                # Save image with product ID as filename
                image.save(f'static/images/products/{product.product_id}.jpg')
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products.admin_list'))
    
    return render_template('admin/products/edit.html', product=product)

@products_bp.route('/admin/delete/<int:product_id>', methods=['POST'])
@login_required
def admin_delete(product_id):
    if not current_user.is_admin:
        abort(403)
    
    product = Product.query.get_or_404(product_id)
    
    # Delete associated image if exists
    image_path = f'static/images/products/{product_id}.jpg'
    if os.path.exists(image_path):
        os.remove(image_path)
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products.admin_list'))
