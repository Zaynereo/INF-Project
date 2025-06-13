from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.sql_models import db, User, Product, Order, Supplier, Supply, OrderItem
from sqlalchemy import func, extract, desc
from datetime import datetime, timedelta
from functools import wraps

# Create admin blueprint
admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to ensure user is an admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    # Get statistics for the dashboard
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_customers = User.query.filter_by(is_admin=False).count()
    
    # Calculate total revenue
    total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
    
    # Get recent orders
    recent_orders = Order.query.order_by(desc(Order.order_date)).limit(5).all()
    
    # Get sales data for the last 7 days
    today = datetime.utcnow()
    week_ago = today - timedelta(days=7)
    
    daily_sales = db.session.query(
        func.date(Order.order_date).label('date'),
        func.sum(Order.total_amount).label('total')
    ).filter(
        Order.order_date >= week_ago,
        Order.status != 'cancelled'
    ).group_by(
        func.date(Order.order_date)
    ).order_by(
        'date'
    ).all()
    
    # Format data for chart
    sales_dates = [sale.date.strftime('%Y-%m-%d') for sale in daily_sales]
    sales_totals = [float(sale.total or 0) for sale in daily_sales]
    
    # Get top selling products
    top_products = db.session.query(
        Product,
        func.sum(OrderItem.quantity).label('total_quantity')
    ).join(
        OrderItem,
        Product.product_id == OrderItem.product_id
    ).join(
        Order,
        OrderItem.order_id == Order.id
    ).filter(
        Order.status != 'cancelled',
        Order.order_date >= week_ago
    ).group_by(
        Product.product_id
    ).order_by(
        desc('total_quantity')
    ).limit(5).all()
    
    # Get low stock products
    low_stock_products = Product.query.filter(
        Product.stock_level <= 10  # Threshold for low stock
    ).order_by(
        Product.stock_level
    ).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        total_products=total_products,
        total_orders=total_orders,
        total_customers=total_customers,
        total_revenue=total_revenue,
        recent_orders=recent_orders,
        sales_dates=sales_dates,
        sales_totals=sales_totals,
        top_products=top_products,
        low_stock_products=low_stock_products
    )

# Customer management
@admin_bp.route('/customers')
@login_required
@admin_required
def manage_customers():
    # Get all non-admin users
    customers = User.query.filter_by(is_admin=False).all()
    return render_template('admin/customers/list.html', customers=customers)

@admin_bp.route('/customers/<int:user_id>')
@login_required
@admin_required
def view_customer(user_id):
    customer = User.query.get_or_404(user_id)
    
    # Get customer's orders
    orders = Order.query.filter_by(user_id=user_id).order_by(desc(Order.order_date)).all()
    
    return render_template('admin/customers/detail.html', customer=customer, orders=orders)

# Supplier management
@admin_bp.route('/suppliers')
@login_required
@admin_required
def manage_suppliers():
    suppliers = Supplier.query.all()
    return render_template('admin/suppliers/list.html', suppliers=suppliers)

@admin_bp.route('/suppliers/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_supplier():
    if request.method == 'POST':
        # Create new supplier
        supplier = Supplier(
            name=request.form.get('name'),
            contact_person=request.form.get('contact_person'),
            contact_number=request.form.get('contact_number'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            country=request.form.get('country')
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        flash('Supplier created successfully!', 'success')
        return redirect(url_for('admin.manage_suppliers'))
    
    return render_template('admin/suppliers/create.html')

@admin_bp.route('/suppliers/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    
    if request.method == 'POST':
        # Update supplier details
        supplier.name = request.form.get('name', supplier.name)
        supplier.contact_person = request.form.get('contact_person', supplier.contact_person)
        supplier.contact_number = request.form.get('contact_number', supplier.contact_number)
        supplier.email = request.form.get('email', supplier.email)
        supplier.address = request.form.get('address', supplier.address)
        supplier.city = request.form.get('city', supplier.city)
        supplier.country = request.form.get('country', supplier.country)
        
        db.session.commit()
        
        flash('Supplier updated successfully!', 'success')
        return redirect(url_for('admin.manage_suppliers'))
    
    return render_template('admin/suppliers/edit.html', supplier=supplier)

@admin_bp.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
@login_required
@admin_required
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # Check if supplier has any supplies
    if supplier.supplies:
        flash('Cannot delete supplier with associated supplies', 'danger')
        return redirect(url_for('admin.manage_suppliers'))
    
    db.session.delete(supplier)
    db.session.commit()
    
    flash('Supplier deleted successfully!', 'success')
    return redirect(url_for('admin.manage_suppliers'))

# Inventory management
@admin_bp.route('/inventory')
@login_required
@admin_required
def manage_inventory():
    # Get all products with their current stock levels
    products = Product.query.order_by(Product.name).all()
    
    # Get low stock products
    low_stock = Product.query.filter(Product.stock_level <= 10).order_by(Product.stock_level).all()
    
    # Get out of stock products
    out_of_stock = Product.query.filter(Product.stock_level == 0).all()
    
    return render_template(
        'admin/inventory/list.html',
        products=products,
        low_stock=low_stock,
        out_of_stock=out_of_stock
    )

@admin_bp.route('/inventory/report')
@login_required
@admin_required
def inventory_report():
    # Get inventory report data
    products = Product.query.order_by(Product.category, Product.name).all()
    
    # Calculate total inventory value
    total_value = sum(p.price * p.stock_level for p in products)
    
    # Get inventory by category
    categories = db.session.query(
        Product.category,
        func.sum(Product.stock_level).label('total_quantity'),
        func.sum(Product.price * Product.stock_level).label('total_value')
    ).group_by(Product.category).all()
    
    return render_template(
        'admin/inventory/report.html',
        products=products,
        categories=categories,
        total_value=total_value
    )

# Reports
@admin_bp.route('/reports/sales')
@login_required
@admin_required
def sales_report():
    # Get date range from query params or default to last 30 days
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        end_date = datetime.utcnow().strftime('%Y-%m-%d')
        start_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Convert string dates to datetime objects
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get sales data for the selected period
    sales_data = db.session.query(
        func.date(Order.order_date).label('date'),
        func.count(Order.id).label('order_count'),
        func.sum(Order.total_amount).label('total_sales')
    ).filter(
        Order.order_date.between(start_dt, end_dt + timedelta(days=1)),
        Order.status != 'cancelled'
    ).group_by(
        func.date(Order.order_date)
    ).order_by('date').all()
    
    # Get top selling products
    top_products = db.session.query(
        Product,
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.quantity * OrderItem.item_price).label('total_revenue')
    ).join(
        OrderItem,
        Product.product_id == OrderItem.product_id
    ).join(
        Order,
        OrderItem.order_id == Order.id
    ).filter(
        Order.order_date.between(start_dt, end_dt + timedelta(days=1)),
        Order.status != 'cancelled'
    ).group_by(
        Product.product_id
    ).order_by(
        desc('total_quantity')
    ).limit(10).all()
    
    # Calculate total sales and orders
    total_sales = sum(float(sale.total_sales or 0) for sale in sales_data)
    total_orders = sum(sale.order_count for sale in sales_data)
    
    # Format data for chart
    dates = [sale.date.strftime('%Y-%m-%d') for sale in sales_data]
    sales = [float(sale.total_sales or 0) for sale in sales_data]
    
    return render_template(
        'admin/reports/sales.html',
        start_date=start_date,
        end_date=end_date,
        dates=dates,
        sales=sales,
        total_sales=total_sales,
        total_orders=total_orders,
        top_products=top_products
    )
