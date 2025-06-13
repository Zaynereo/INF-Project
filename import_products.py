import pandas as pd
from models.sql_models import Product, db
from app import create_app
import sys

def import_products():
    try:
        # Create app and push context
        app = create_app()
        
        with app.app_context():
            # Load CSV
            print("Loading CSV file...")
            try:
                df = pd.read_csv("bigbasket_first_20.csv")
                print(f"Found {len(df)} products in CSV")
            except Exception as e:
                print(f"Error reading CSV file: {e}")
                return
            
            # Check required columns
            required_columns = ['product', 'category', 'brand', 'sale_price']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"Error: Missing required columns: {', '.join(missing_columns)}")
                return
            
            # Initialize counters
            imported = 0
            skipped = 0
            
            # Process each row
            for _, row in df.iterrows():
                try:
                    # Check if product already exists
                    if Product.query.filter_by(name=row['product']).first():
                        print(f"Skipping existing product: {row['product']}")
                        skipped += 1
                        continue
                        
                    # Create new product
                    product = Product(
                        name=row['product'][:100],  # Truncate to max length
                        category=row['category'].split(',')[0].strip()[:100] if pd.notna(row['category']) else 'Uncategorized',
                        sub_category=row['category'].strip()[:100] if pd.notna(row['category']) else '',
                        brand=row['brand'][:100] if pd.notna(row['brand']) else 'Unknown',
                        price=float(row['sale_price']),
                        unit='pc',  # Default unit
                        stock_level=100,  # Default stock level
                        description=str(row.get('description', ''))[:500]  # Truncate description
                    )
                    
                    db.session.add(product)
                    imported += 1
                    
                    # Print progress
                    if imported % 5 == 0:
                        print(f"Processed {imported + skipped} products...")
                        
                except Exception as e:
                    print(f"Error processing product '{row.get('product', 'Unknown')}': {e}")
                    skipped += 1
            
            # Commit all changes
            db.session.commit()
            
            print(f"\nImport complete!")
            print(f"Successfully imported: {imported} products")
            print(f"Skipped: {skipped} products")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        if 'db' in locals() and db.session:
            db.session.rollback()
        sys.exit(1)

if __name__ == '__main__':
    import_products()
