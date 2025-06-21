from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Category, SubCategory, Brand, Product
from orders.models import Supplier
from django.utils import timezone
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up initial data for the grocery store'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superuser created: admin/admin123'))
        
        # Create categories
        categories_data = [
            {'name': 'Beauty & Hygiene', 'description': 'Personal care and beauty products'},
            {'name': 'Kitchen, Garden & Pets', 'description': 'Kitchen essentials and pet supplies'},
            {'name': 'Cleaning & Household', 'description': 'Cleaning supplies and household items'},
            {'name': 'Gourmet & World Food', 'description': 'Premium and international food products'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create subcategories
        subcategories_data = [
            {'name': 'Hair Care', 'category': 'Beauty & Hygiene'},
            {'name': 'Skin Care', 'category': 'Beauty & Hygiene'},
            {'name': 'Bath', 'category': 'Beauty & Hygiene'},
            {'name': 'Storage', 'category': 'Kitchen, Garden & Pets'},
            {'name': 'Storage', 'category': 'Cleaning & Household'},
            {'name': 'Snacks', 'category': 'Gourmet & World Food'},
            {'name': 'Dairy & Cheese', 'category': 'Gourmet & World Food'},
            {'name': 'Health Food', 'category': 'Gourmet & World Food'},
        ]
        
        subcategories = {}
        for subcat_data in subcategories_data:
            subcategory, created = SubCategory.objects.get_or_create(
                name=subcat_data['name'],
                category=categories[subcat_data['category']],
                defaults={'description': f'{subcat_data["name"]} products'}
            )
            subcategories[f"{subcat_data['category']} - {subcat_data['name']}"] = subcategory
            if created:
                self.stdout.write(f'Created subcategory: {subcategory.name}')
        
        # Create brands
        brands_data = [
            {'name': 'Sri Sri Ayurveda', 'description': 'Traditional Ayurvedic products'},
            {'name': 'Mastercook', 'description': 'Kitchen and cooking essentials'},
            {'name': 'Nakoda', 'description': 'Quality household products'},
            {'name': 'Oxy', 'description': 'Personal care products'},
            {'name': 'Bionova', 'description': 'Natural and organic products'},
            {'name': 'Aroma Treasures', 'description': 'Aromatherapy and wellness products'},
            {'name': 'Graminway', 'description': 'Traditional and gourmet foods'},
            {'name': 'Murginns', 'description': 'Premium dairy products'},
            {'name': 'NUTRASHIL', 'description': 'Health and nutrition supplements'},
            {'name': 'StBotanica', 'description': 'Natural beauty and hair care'},
        ]
        
        brands = {}
        for brand_data in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults={'description': brand_data['description']}
            )
            brands[brand_data['name']] = brand
            if created:
                self.stdout.write(f'Created brand: {brand.name}')
        
        # Create products
        products_data = [
            {
                'name': 'Garlic Oil',
                'category': 'Beauty & Hygiene',
                'sub_category': 'Hair Care',
                'brand': 'Sri Sri Ayurveda',
                'price': Decimal('220.00'),
                'unit': 'ml',
                'stock_level': 100,
                'description': 'Natural garlic oil for hair care and growth'
            },
            {
                'name': 'Water Bottle',
                'category': 'Kitchen, Garden & Pets',
                'sub_category': 'Storage',
                'brand': 'Mastercook',
                'price': Decimal('180.00'),
                'unit': 'pcs',
                'stock_level': 50,
                'description': 'Reusable water bottle for daily use'
            },
            {
                'name': 'Cereal Jar',
                'category': 'Cleaning & Household',
                'sub_category': 'Storage',
                'brand': 'Nakoda',
                'price': Decimal('149.00'),
                'unit': 'pcs',
                'stock_level': 200,
                'description': 'Airtight cereal storage jar'
            },
            {
                'name': 'Face Wash',
                'category': 'Beauty & Hygiene',
                'sub_category': 'Skin Care',
                'brand': 'Oxy',
                'price': Decimal('110.00'),
                'unit': 'ml',
                'stock_level': 80,
                'description': 'Gentle face wash for daily cleansing'
            },
            {
                'name': 'Hand Sanitizer',
                'category': 'Beauty & Hygiene',
                'sub_category': 'Bath',
                'brand': 'Bionova',
                'price': Decimal('250.00'),
                'unit': 'ml',
                'stock_level': 150,
                'description': 'Alcohol-based hand sanitizer'
            },
            {
                'name': 'Smooth Skin Oil',
                'category': 'Beauty & Hygiene',
                'sub_category': 'Skin Care',
                'brand': 'Aroma Treasures',
                'price': Decimal('324.00'),
                'unit': 'ml',
                'stock_level': 70,
                'description': 'Natural oil for smooth and glowing skin'
            },
            {
                'name': 'Salted Pumpkin',
                'category': 'Gourmet & World Food',
                'sub_category': 'Snacks',
                'brand': 'Graminway',
                'price': Decimal('180.00'),
                'unit': 'gm',
                'stock_level': 40,
                'description': 'Delicious salted pumpkin seeds'
            },
            {
                'name': 'Organic Tofu',
                'category': 'Gourmet & World Food',
                'sub_category': 'Dairy & Cheese',
                'brand': 'Murginns',
                'price': Decimal('85.14'),
                'unit': 'gm',
                'stock_level': 90,
                'description': 'Fresh organic tofu'
            },
            {
                'name': 'Wheat Grass Powder',
                'category': 'Gourmet & World Food',
                'sub_category': 'Health Food',
                'brand': 'NUTRASHIL',
                'price': Decimal('261.00'),
                'unit': 'gm',
                'stock_level': 60,
                'description': 'Natural wheat grass powder for health'
            },
            {
                'name': 'Biotin Shampoo',
                'category': 'Beauty & Hygiene',
                'sub_category': 'Hair Care',
                'brand': 'StBotanica',
                'price': Decimal('1098.00'),
                'unit': 'ml',
                'stock_level': 30,
                'description': 'Biotin-enriched shampoo for hair growth'
            },
        ]
        
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'category': categories[product_data['category']],
                    'sub_category': subcategories[f"{product_data['category']} - {product_data['sub_category']}"],
                    'brand': brands[product_data['brand']],
                    'price': product_data['price'],
                    'unit': product_data['unit'],
                    'stock_level': product_data['stock_level'],
                    'description': product_data['description'],
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        # Create suppliers
        suppliers_data = [
            {'name': 'ABC Supplies', 'contact': 'abc@example.com'},
            {'name': 'XYZ Traders', 'contact': 'xyz@example.com'},
            {'name': 'Global Products', 'contact': 'global@example.com'},
            {'name': 'FreshMart', 'contact': 'fresh@example.com'},
            {'name': 'Beauty Essentials', 'contact': 'beauty@example.com'},
            {'name': 'Daily Needs', 'contact': 'daily@example.com'},
            {'name': 'Wellness Co', 'contact': 'wellness@example.com'},
            {'name': 'Eco Store', 'contact': 'eco@example.com'},
            {'name': 'Nature Hub', 'contact': 'nature@example.com'},
            {'name': 'Organic World', 'contact': 'organic@example.com'},
        ]
        
        for supplier_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=supplier_data['name'],
                defaults={'contact': supplier_data['contact']}
            )
            if created:
                self.stdout.write(f'Created supplier: {supplier.name}')
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed successfully!'))
        self.stdout.write('You can now run: python manage.py runserver')
        self.stdout.write('Admin login: admin/admin123') 