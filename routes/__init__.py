# This file makes the routes directory a Python package
# Import all blueprints here to avoid circular imports
from .auth import auth_bp
from .products import products_bp
from .cart import cart_bp
from .orders import orders_bp
from .admin import admin_bp

# Export all blueprints
__all__ = ['auth_bp', 'products_bp', 'cart_bp', 'orders_bp', 'admin_bp']
