from app import create_app
from models.sql_models import db, User, Product

def verify_database():
    app = create_app()
    with app.app_context():
        # Check admin user
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("✅ Admin user exists")
            print(f"  - Email: {admin.email}")
            print(f"  - Is Admin: {admin.is_admin}")
        else:
            print("❌ Admin user not found")
        
        # Count products
        product_count = Product.query.count()
        print(f"\n📦 Found {product_count} products in the database")
        
        # Show first 5 products as sample
        if product_count > 0:
            print("\nSample products:")
            products = Product.query.limit(5).all()
            for i, product in enumerate(products, 1):
                print(f"{i}. {product.name} - ${product.price:.2f}")

if __name__ == '__main__':
    verify_database()
