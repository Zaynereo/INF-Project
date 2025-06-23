# Grocery Store Project

A simple e-commerce grocery store web app using Django ORM and a custom SQL schema. Focuses on SQL skills and minimal Django usage.

## Features
- Product catalog, categories, brands
- Cart and order management
- User sessions (no Django admin or built-in authentication)

## Setup
1. Install requirements
2. Configure your database in `.env`
3. Run migrations and start the server

## Database
- Uses a custom SQL schema for all core tables
- Only minimal Django tables (`django_session`, `django_migrations`) are present

## Project Structure

```
database project/
├── grocery_store/          # Django project settings
├── products/              # Product management app
├── accounts/              # User accounts and profiles
├── orders/                # Order processing app
├── cart/                  # Shopping cart functionality
├── templates/             # HTML templates
├── static/                # CSS, JS, and media files
├── connection.py          # PostgreSQL connection utility
├── main.py               # Database connection test
├── setup_schema.sql      # Database schema
└── requirements.txt      # Python dependencies
```

## Setup Instructions

### 1. Environment Setup

Create a `.env` file in the project root with your Supabase PostgreSQL credentials:

```env
DB_HOST=your-supabase-host
DB_PORT=5432
DB_NAME=your-database-name
DB_USER=your-username
DB_PASSWORD=your-password
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Initial Data

```bash
python manage.py setup_initial_data
```

This will create:
- Admin user (admin/admin123)
- Sample categories and subcategories
- Sample brands and products
- Sample suppliers

### 5. Run the Development Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to see your application.

## Database Models

### Products App
- **Category**: Product categories
- **SubCategory**: Product subcategories
- **Brand**: Product brands
- **Product**: Main product model
- **ProductImage**: Additional product images
- **ProductReview**: Customer reviews and ratings

### Accounts App
- **CustomerProfile**: Extended user profiles
- **Address**: Customer shipping/billing addresses

### Orders App
- **Supplier**: Product suppliers
- **Order**: Customer orders
- **OrderItem**: Individual order items
- **Supply**: Supplier inventory
- **OrderHistory**: Order status tracking

### Cart App
- **Cart**: Shopping cart
- **CartItem**: Cart items
- **Wishlist**: User wishlists
- **Coupon**: Discount coupons
- **CouponUsage**: Coupon usage tracking

## API Endpoints

### Products
- `GET /` - Product listing
- `GET /product/<id>/` - Product details
- `GET /category/<slug>/` - Category products
- `GET /brand/<slug>/` - Brand products
- `GET /search/` - Product search
- `GET /filter/` - Product filtering

### Cart
- `GET /cart/` - View cart
- `POST /cart/add/<id>/` - Add to cart
- `POST /cart/update/<id>/` - Update cart item
- `POST /cart/remove/<id>/` - Remove from cart

### Orders
- `GET /orders/checkout/` - Checkout page
- `POST /orders/checkout/` - Process order
- `GET /orders/order/<id>/` - Order details

### Accounts
- `GET /accounts/profile/` - User profile
- `GET /accounts/orders/` - Order history
- `GET /accounts/wishlist/` - User wishlist

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations <app_name>
python manage.py migrate
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

## Database Connection

The project uses your existing PostgreSQL connection from `connection.py`. Django automatically handles the connection through the settings configuration.

## Future Enhancements

1. **MongoDB Integration**: Add MongoDB Atlas for additional data storage
2. **Payment Gateway**: Integrate Stripe or PayPal
3. **Email Notifications**: Order confirmations and updates
4. **Inventory Management**: Real-time stock tracking
5. **Analytics Dashboard**: Sales and customer analytics
6. **Mobile App**: React Native or Flutter mobile app
7. **API Development**: RESTful API for mobile apps
8. **Search Optimization**: Elasticsearch integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository. 