from django.core.management.base import BaseCommand
from products.models import Category, SubCategory, Brand, Product, Supplier
from django.utils import timezone
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up initial data for the grocery store'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
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
            )
            subcategories[f"{subcat_data['category']} - {subcat_data['name']}"] = subcategory
            if created:
                self.stdout.write(f'Created subcategory: {subcategory.name}')
        
        # Create brands
        brands_data = [
            {'name': 'Sri Sri Ayurveda'},
            {'name': 'Mastercook'},
            {'name': 'Nakoda'},
            {'name': 'Oxy'},
            {'name': 'Bionova'},
            {'name': 'Aroma Treasures'},
            {'name': 'Graminway'},
            {'name': 'Murginns'},
            {'name': 'NUTRASHIL'},
            {'name': 'StBotanica'},
        ]
        
        brands = {}
        for brand_data in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name']
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
                'market_price': Decimal('220.00'),
                'sale_price': Decimal('220.00'),
                'unit': 'ml',
                'stock_level': 100,
                'description': 'Natural garlic oil for hair care and growth',
                'rating': Decimal('4.1')
            },
            {
                'name': 'Water Bottle',
                'category': 'Kitchen, Garden & Pets',
                'sub_category': 'Storage',
                'brand': 'Mastercook',
                'market_price': Decimal('180.00'),
                'sale_price': Decimal('180.00'),
                'unit': 'pcs',
                'stock_level': 50,
                'description': 'Reusable water bottle for daily use',
                'rating': Decimal('2.3')
            },
            {
                'name': 'Cereal Jar',
                'category': 'Cleaning & Household',
                'sub_category': 'Storage',
                'brand': 'Nakoda',
                'market_price': Decimal('176.00'),
                'sale_price': Decimal('149.00'),
                'unit': 'pcs',
                'stock_level': 200,
                'description': 'Airtight cereal storage jar',
                'rating': Decimal('3.7')
            },
            {
                'name': 'Face Wash',
                'category': 'Beauty & Hygiene',
                'sub_category': 'Skin Care',
                'brand': 'Oxy',
                'market_price': Decimal('110.00'),
                'sale_price': Decimal('110.00'),
                'unit': 'ml',
                'stock_level': 80,
                'description': 'Gentle face wash for daily cleansing',
                'rating': Decimal('5.0')
            },
            {
                'name': 'Hand Sanitizer',
                'category': 'Beauty & Hygiene',
                'sub_category': 'Bath',
                'brand': 'Bionova',
                'market_price': Decimal('250.00'),
                'sale_price': Decimal('250.00'),
                'unit': 'ml',
                'stock_level': 150,
                'description': 'Alcohol-based hand sanitizer',
                'rating': Decimal('4.5')
            },
            {
                'name': 'Smooth Skin Oil',
                'category': 'Beauty & Hygiene',
                'sub_category': 'Skin Care',
                'brand': 'Aroma Treasures',
                'market_price': Decimal('324.00'),
                'sale_price': Decimal('324.00'),
                'unit': 'ml',
                'stock_level': 70,
                'description': 'Natural oil for smooth and glowing skin',
                'rating': Decimal('4.2')
            },
            {
                'name': 'Salted Pumpkin',
                'category': 'Gourmet & World Food',
                'sub_category': 'Snacks',
                'brand': 'Graminway',
                'market_price': Decimal('180.00'),
                'sale_price': Decimal('180.00'),
                'unit': 'gm',
                'stock_level': 40,
                'description': 'Delicious salted pumpkin seeds',
                'rating': Decimal('4.9')
            },
            {
                'name': 'Organic Tofu',
                'category': 'Gourmet & World Food',
                'sub_category': 'Dairy & Cheese',
                'brand': 'Murginns',
                'market_price': Decimal('90.00'),
                'sale_price': Decimal('85.14'),
                'unit': 'gm',
                'stock_level': 90,
                'description': 'Fresh organic tofu',
                'rating': Decimal('3.9')
            },
            {
                'name': 'Wheat Grass Powder',
                'category': 'Gourmet & World Food',
                'sub_category': 'Health Food',
                'brand': 'NUTRASHIL',
                'market_price': Decimal('261.00'),
                'sale_price': Decimal('261.00'),
                'unit': 'gm',
                'stock_level': 60,
                'description': 'Natural wheat grass powder for health',
                'rating': Decimal('4.0')
            },
            {
                'name': 'Biotin Shampoo',
                'category': 'Beauty & Hygiene',
                'sub_category': 'Hair Care',
                'brand': 'StBotanica',
                'market_price': Decimal('1098.00'),
                'sale_price': Decimal('1098.00'),
                'unit': 'ml',
                'stock_level': 30,
                'description': 'Biotin-enriched shampoo for hair growth',
                'rating': Decimal('4.3')
            },
        ]
        
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'category': categories[product_data['category']],
                    'subcategory': subcategories[f"{product_data['category']} - {product_data['sub_category']}"],
                    'brand': brands[product_data['brand']],
                    'market_price': product_data['market_price'],
                    'sale_price': product_data['sale_price'],
                    'unit': product_data['unit'],
                    'stock_level': product_data['stock_level'],
                    'description': product_data['description'],
                    'rating': product_data['rating'],
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