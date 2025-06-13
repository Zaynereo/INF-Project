from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models.sql_models import db, CartItem, Product
from forms import AddToCartForm
from functools import wraps
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_ajax_response(f):
    """Decorator to handle AJAX responses consistently."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], dict):
                return jsonify(result[0]), result[1]
            return jsonify(result) if isinstance(result, dict) else result
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'An error occurred while processing your request.',
                    'error': str(e)
                }), 500
            flash('An error occurred while processing your request.', 'danger')
            return redirect(url_for('cart.view_cart'))
    return decorated_function

cart_bp = Blueprint('cart', __name__)

@cart_bp.before_request
@login_required
def require_login():
    """Ensure user is logged in for all cart routes."""
    pass

@cart_bp.route('/')
@login_required
def view_cart():
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
    
    # Calculate total
    total = sum(item.Product.price * item.CartItem.quantity for item in cart_items)
    
    return render_template('cart/view.html', cart_items=cart_items, total=total)

@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@handle_ajax_response
def add_item(product_id):
    form = AddToCartForm()
    
    if not form.validate_on_submit():
        errors = {field.name: field.errors for field in form if field.errors}
        return {
            'success': False, 
            'message': 'Validation failed',
            'errors': errors
        }, 400
    
    quantity = form.quantity.data
    
    # Check if product exists and is in stock
    product = Product.query.get_or_404(product_id)
    if product.stock < quantity:
        return {
            'success': False,
            'message': f'Only {product.stock} items available in stock',
            'available': product.stock
        }, 400
    
    # Use a transaction to ensure data consistency
    try:
        # Check if item already in cart
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).with_for_update().first()
        
        if cart_item:
            # Ensure we don't exceed available stock
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                return {
                    'success': False,
                    'message': f'Cannot add {quantity} more items. Only {product.stock - cart_item.quantity} more available.',
                    'available': product.stock - cart_item.quantity
                }, 400
                
            cart_item.quantity = new_quantity
        else:
            # Add new item to cart
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        # Return success response
        response = {
            'success': True,
            'message': f'Added {product.name} to your cart',
            'cart_count': get_cart_count(),
            'item': {
                'id': cart_item.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': cart_item.quantity,
                'subtotal': float(product.price * cart_item.quantity),
                'image_url': product.image_url or url_for('static', filename='images/placeholder-product.png')
            }
        }
        
        # Add flash message for non-AJAX requests
        if not request.is_json and not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            flash(response['message'], 'success')
            
        return response
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding item to cart: {str(e)}", exc_info=True)
        raise  # Let the error handler deal with it

@cart_bp.route('/update/<int:item_id>', methods=['POST'])
@handle_ajax_response
def update_item(item_id):
    form = AddToCartForm()
    
    if not form.validate():
        errors = {field.name: field.errors for field in form if field.errors}
        return {
            'success': False, 
            'message': 'Validation failed',
            'errors': errors
        }, 400
    
    new_quantity = form.quantity.data
    
    # Start a transaction
    try:
        # Lock the cart item for update to prevent race conditions
        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=current_user.id
        ).join(Product).with_for_update().first_or_404()
        
        product = cart_item.product
        
        # Check stock if increasing quantity
        if new_quantity > cart_item.quantity and product.stock < new_quantity:
            return {
                'success': False,
                'message': f'Only {product.stock} items available in stock',
                'available': product.stock
            }, 400
        
        if new_quantity < 1:
            # Remove item if quantity is 0 or negative
            db.session.delete(cart_item)
            message = 'Item removed from cart'
            removed = True
        else:
            cart_item.quantity = new_quantity
            message = 'Cart updated'
            removed = False
        
        db.session.commit()
        
        # Prepare response
        response = {
            'success': True,
            'message': message,
            'item_id': item_id,
            'new_quantity': new_quantity if new_quantity > 0 else 0,
            'subtotal': float(product.price * new_quantity) if new_quantity > 0 else 0,
            'cart_count': get_cart_count(),
            'removed': removed,
            'item': {
                'id': cart_item.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': new_quantity,
                'subtotal': float(product.price * new_quantity) if new_quantity > 0 else 0,
                'image_url': product.image_url or url_for('static', filename='images/placeholder-product.png')
            }
        }
        
        # Add flash message for non-AJAX requests
        if not request.is_json and not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            flash(response['message'], 'success')
            
        return response
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating cart item {item_id}: {str(e)}", exc_info=True)
        raise  # Let the error handler deal with it

@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@handle_ajax_response
def remove_item(item_id):
    # Start a transaction
    try:
        # Lock the cart item for update to prevent race conditions
        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=current_user.id
        ).join(Product).with_for_update().first_or_404()
        
        product = cart_item.product
        db.session.delete(cart_item)
        db.session.commit()
        
        # Prepare response
        response = {
            'success': True,
            'message': 'Item removed from cart',
            'item_id': item_id,
            'cart_count': get_cart_count(),
            'item': {
                'id': cart_item.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': 0,
                'subtotal': 0,
                'image_url': product.image_url or url_for('static', filename='images/placeholder-product.png')
            }
        }
        
        # Add flash message for non-AJAX requests
        if not request.is_json and not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            flash(response['message'], 'success')
            
        return response
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing cart item {item_id}: {str(e)}", exc_info=True)
        raise  # Let the error handler deal with it

@cart_bp.route('/count')
@login_required
def cart_count():
    return jsonify({'count': get_cart_count()})

def get_cart_count():
    """Helper function to get cart item count for current user"""
    return db.session.query(CartItem).filter_by(user_id=current_user.id).count()

def get_cart_subtotal(product_id, quantity):
    """Helper function to calculate subtotal for a cart item"""
    product = Product.query.get(product_id)
    return {
        'subtotal': product.price * quantity,
        'formatted': f'${product.price * quantity:.2f}'
    }

# Context processor to make cart count available in all templates
@cart_bp.app_context_processor
def inject_cart_count():
    if current_user.is_authenticated:
        return {'cart_count': get_cart_count()}
    return {'cart_count': 0}
