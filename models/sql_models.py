from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# This import must be after db is created to avoid circular imports
from . import db

@login_manager.user_loader
def load_user(user_id):
    # Use the current model to avoid circular imports
    return User.query.get(int(user_id))

class Product(db.Model):
    __tablename__ = 'products'
    
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    sub_category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10))
    stock_level = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(200))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def serialize(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category,
            'sub_category': self.sub_category,
            'brand': self.brand,
            'price': self.price,
            'unit': self.unit,
            'stock_level': self.stock_level,
            'image_url': self.image_url,
            'description': self.description
        }

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)  # Increased length for hashed password
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        # Remove password from kwargs before calling parent __init__
        password = kwargs.pop('password', None)
        super(User, self).__init__(**kwargs)
        if password:
            self.set_password(password)
    
    def set_password(self, password):
        """Create hashed password."""
        self.password_hash = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=16
        )
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<User {self.username}>'

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, processing, shipped, delivered, cancelled
    shipping_address = db.Column(db.String(200))
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(20), default='pending')
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def calculate_total(self):
        self.total_amount = sum(item.quantity * item.item_price for item in self.items)
        return self.total_amount

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    item_price = db.Column(db.Float, nullable=False)
    
    # Relationships
    product = db.relationship('Product')
    
    def __init__(self, product_id, quantity, item_price):
        self.product_id = product_id
        self.quantity = quantity
        self.item_price = item_price

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    # Relationships
    product = db.relationship('Product')
    
    def __init__(self, user_id, product_id, quantity=1):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
        
    def to_dict(self):
        return {
            'id': self.id,
            'product': self.product.serialize(),
            'quantity': self.quantity
        }

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    contact_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplies = db.relationship('Supply', backref='supplier', lazy=True)
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'contact_number': self.contact_number,
            'email': self.email,
            'address': self.address,
            'city': self.city,
            'country': self.country
        }

class Supply(db.Model):
    __tablename__ = 'supplies'
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    supply_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    cost_price = db.Column(db.Float, nullable=False)  # Per unit cost
    total_cost = db.Column(db.Float, nullable=False)
    received_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    
    # Relationships
    product = db.relationship('Product')
    
    def __init__(self, supplier_id, product_id, quantity, cost_price, received_by=None, notes=None):
        self.supplier_id = supplier_id
        self.product_id = product_id
        self.quantity = quantity
        self.cost_price = cost_price
        self.total_cost = quantity * cost_price
        self.received_by = received_by
        self.notes = notes
    
    def serialize(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'product': self.product.serialize(),
            'supply_date': self.supply_date.isoformat(),
            'quantity': self.quantity,
            'cost_price': self.cost_price,
            'total_cost': self.total_cost,
            'received_by': self.received_by,
            'notes': self.notes
        }
