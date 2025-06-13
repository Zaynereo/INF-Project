from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.sql_models import db, Order, OrderItem, CartItem, Product
from datetime import datetime
from sqlalchemy import desc

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders')
@login_required
def list_orders():
    """Display a list of the current user's orders"""
    orders = Order.query.filter_by(user_id=current_user.id).order_by(desc(Order.order_date)).all()
    return render_template('orders/list.html', orders=orders)

@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # Get cart items with product details
    cart_items = db.session.query(
        CartItem,
        Product
    ).join(
        Product,
        CartItem.product_id == Product.product_id
    ).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('products.list_products'))
    
    # Calculate total
    total = sum(item.Product.price * item.CartItem.quantity for item in cart_items)
    
    if request.method == 'POST':
        # Create new order
        order = Order(
            user_id=current_user.id,
            shipping_address=request.form.get('shipping_address'),
            payment_method=request.form.get('payment_method'),
            total_amount=total,
            status='pending',
            payment_status='pending'
        )
        
        db.session.add(order)
        
        # Add order items
        for item in cart_items:
            order_item = OrderItem(
                product_id=item.Product.product_id,
                quantity=item.CartItem.quantity,
                item_price=item.Product.price
            )
            order.items.append(order_item)
            
            # Update product stock
            item.Product.stock_level -= item.CartItem.quantity
            
            # Remove item from cart
            db.session.delete(item.CartItem)
        
        db.session.commit()
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('orders.order_detail', order_id=order.id))
    
    return render_template('orders/checkout.html', cart_items=cart_items, total=total)

@orders_bp.route('/')
@login_required
def order_history():
    # Get user's orders
    orders = Order.query.filter_by(user_id=current_user.id).order_by(desc(Order.order_date)).all()
    return render_template('orders/history.html', orders=orders)

@orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    # Get order with items
    order = Order.query.get_or_404(order_id)
    
    # Ensure the order belongs to the current user (unless admin)
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this order', 'danger')
        return redirect(url_for('orders.order_history'))
    
    # Get order items with product details
    order_items = db.session.query(
        OrderItem,
        Product
    ).join(
        Product,
        OrderItem.product_id == Product.product_id
    ).filter(
        OrderItem.order_id == order_id
    ).all()
    
    return render_template('orders/detail.html', order=order, order_items=order_items)

@orders_bp.route('/cancel/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Check if order belongs to user
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to cancel this order', 'danger')
        return redirect(url_for('orders.order_history'))
    
    # Only allow cancelling pending orders
    if order.status != 'pending':
        flash('Only pending orders can be cancelled', 'warning')
        return redirect(url_for('orders.order_detail', order_id=order_id))
    
    # Update order status
    order.status = 'cancelled'
    
    # Return items to stock
    for item in order.items:
        product = Product.query.get(item.product_id)
        if product:
            product.stock_level += item.quantity
    
    db.session.commit()
    
    flash('Order has been cancelled', 'info')
    return redirect(url_for('orders.order_detail', order_id=order_id))

# Admin order management
@orders_bp.route('/admin')
@login_required
def admin_orders():
    if not current_user.is_admin:
        abort(403)  # Forbidden
    
    # Get query parameters for filtering
    status = request.args.get('status')
    
    # Build query
    query = Order.query
    
    if status:
        query = query.filter_by(status=status)
    
    orders = query.order_by(desc(Order.order_date)).all()
    return render_template('admin/orders/list.html', orders=orders)

@orders_bp.route('/admin/<int:order_id>', methods=['GET', 'POST'])
@login_required
def admin_order_detail(order_id):
    if not current_user.is_admin:
        abort(403)
    
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        # Update order status
        new_status = request.form.get('status')
        if new_status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
            order.status = new_status
            db.session.commit()
            flash('Order status updated', 'success')
        
        return redirect(url_for('orders.admin_order_detail', order_id=order_id))
    
    # Get order items with product details
    order_items = db.session.query(
        OrderItem,
        Product
    ).join(
        Product,
        OrderItem.product_id == Product.product_id
    ).filter(
        OrderItem.order_id == order_id
    ).all()
    
    return render_template('admin/orders/detail.html', order=order, order_items=order_items)
