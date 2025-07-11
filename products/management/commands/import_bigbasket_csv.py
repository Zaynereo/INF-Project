import csv
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Import products from bigbasket_first_20.csv into the database'

    def handle(self, *args, **kwargs):
        with open('bigbasket_first_20.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = (row['product'] or '').strip()
                description = (row['description'] or '').strip()
                brand = (row['brand'] or '').strip()
                category = (row['category'] or '').strip()
                subcategory = (row['sub_category'] or '').strip()
                sale_price = row['sale_price']
                market_price = row['market_price']
                rating = row['rating']
                unit = row.get('unit', None)
                stock_level = 0

                # Required fields: name, brand, category, sale_price, market_price
                if not (name and brand and category and sale_price and market_price):
                    self.stdout.write(self.style.WARNING(f"Skipping row with missing required fields: {row}"))
                    continue

                # Convert prices and rating
                try:
                    sale_price = float(sale_price)
                except Exception:
                    sale_price = 0.0
                try:
                    market_price = float(market_price)
                except Exception:
                    market_price = 0.0
                try:
                    rating = float(rating) if rating else 0.0
                except Exception:
                    rating = 0.0

                # Lookup or insert brand (case-insensitive)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT brand_id FROM brand WHERE LOWER(name) = LOWER(%s)", [brand])
                    brand_row = cursor.fetchone()
                    if brand_row:
                        brand_id = brand_row[0]
                    else:
                        cursor.execute("INSERT INTO brand (name) VALUES (%s) RETURNING brand_id", [brand])
                        brand_id = cursor.fetchone()[0]

                # Lookup or insert category (case-insensitive)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT category_id FROM category WHERE LOWER(name) = LOWER(%s)", [category])
                    cat_row = cursor.fetchone()
                    if cat_row:
                        category_id = cat_row[0]
                    else:
                        cursor.execute("INSERT INTO category (name) VALUES (%s) RETURNING category_id", [category])
                        category_id = cursor.fetchone()[0]

                # Lookup or insert subcategory (case-insensitive, must be linked to category)
                subcategory_id = None
                if subcategory:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT subcategory_id FROM subcategory WHERE LOWER(name) = LOWER(%s) AND category_id = %s", [subcategory, category_id])
                        subcat_row = cursor.fetchone()
                        if subcat_row:
                            subcategory_id = subcat_row[0]
                        else:
                            cursor.execute("INSERT INTO subcategory (name, category_id) VALUES (%s, %s) RETURNING subcategory_id", [subcategory, category_id])
                            subcategory_id = cursor.fetchone()[0]

                # Check for duplicate product (case-insensitive)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT product_id FROM product WHERE LOWER(name) = LOWER(%s)", [name])
                    if cursor.fetchone():
                        self.stdout.write(self.style.WARNING(f"Product '{name}' already exists. Skipping."))
                        continue

                # Insert product
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO product (name, description, brand_id, category_id, subcategory_id, market_price, sale_price, unit, stock_level, rating, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                    """, [name, description, brand_id, category_id, subcategory_id, market_price, sale_price, unit if unit else None, stock_level, rating])
                self.stdout.write(self.style.SUCCESS(f"Inserted product: {name}")) 