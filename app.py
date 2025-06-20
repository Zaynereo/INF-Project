import os
from flask import Flask, render_template, redirect, url_for, session, request
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from datetime import timedelta
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

# Load environment variables
load_dotenv()

# Configure upload folder for product images
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def create_app():
    # Create and configure the app
    app = Flask(__name__)
    
    # Configure the SQLAlchemy part of the app instance
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'mysql+pymysql://root:Ngkh2002@localhost:3307/grocerydb')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    }
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    
    # Initialize SQLAlchemy with the app
    from models.sql_models import db, login_manager
    db.init_app(app)
    
    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Configure upload folder
    os.makedirs(os.path.join(app.root_path, UPLOAD_FOLDER), exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Set secret key for CSRF protection
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
    
    # Disable CSRF for API endpoints that don't need it
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False
    app.config['WTF_CSRF_SSL_STRICT'] = False
    
    # Initialize Migrate
    migrate.init_app(app, db)
    
    def init_db():
        """Initialize the database and create tables"""
        try:
            # Import models inside the function to avoid circular imports
            from models.sql_models import User, Product, Order, OrderItem, CartItem, Supplier, Supply
            
            # Create all tables
            print("Creating database tables...")
            with app.app_context():
                db.create_all()
            
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("Creating admin user...")
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True,
                    phone='1234567890',
                    address='123 Admin St, Admin City',
                    password='admin123'  # Will be hashed by the model
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created successfully!")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Import models here to avoid circular imports
    from models.sql_models import User, Product, Order, OrderItem, CartItem, Supplier, Supply
    
    # Initialize the database
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("Creating admin user...")
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True,
                    phone='1234567890',
                    address='123 Admin St, Admin City',
                    password='admin123'  # Will be hashed by the model
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created successfully!")
            else:
                print("✅ Admin user already exists.")
                
            print("✅ Database initialization complete!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
    
    # Register blueprints
    from routes import auth_bp, products_bp, cart_bp, orders_bp, admin_bp
    
    # Register blueprints with CSRF exemption where needed
    csrf.exempt(auth_bp)  # Auth endpoints handle CSRF differently
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'CSRF token missing or invalid.'
            }), 400
        return render_template('errors/403.html', reason=e.description), 400
    
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        def get_csrf_token():
            return generate_csrf()
        return dict(csrf_token=get_csrf_token)
    
    @app.context_processor
    def inject_cart_count():
        from models.sql_models import CartItem
        from flask import current_app
        from flask_login import current_user
        
        cart_count = 0
        if current_user.is_authenticated:
            try:
                with current_app.app_context():
                    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
            except Exception as e:
                current_app.logger.error(f"Error getting cart count: {e}")
        return {'cart_count': cart_count}
    
    # Add home route
    @app.route('/')
    @app.route('/home')
    def home():
        # Redirect to products page for now
        return redirect(url_for('products.list_products'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Use port 5001 if 5000 is in use
    port = int(os.environ.get('PORT', 5001))
    try:
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Port {port} is in use. Trying port {port + 1}...")
            app.run(host='0.0.0.0', port=port + 1, debug=True, use_reloader=False)
        else:
            raise e