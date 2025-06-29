# Grocery Store E-Commerce Project

A modern e-commerce grocery store web application built with Django, PostgreSQL (Supabase), and MongoDB Atlas. Features a hybrid database architecture with PostgreSQL for structured data and MongoDB for flexible document storage.

## 🚀 Features

### **Core E-Commerce Features**
- ✅ **Product Catalog** with categories, brands, and subcategories
- ✅ **Shopping Cart** with MongoDB storage for session persistence
- ✅ **Order Management** with PostgreSQL for reliable transactions
- ✅ **User Authentication** with custom session management
- ✅ **Product Reviews & Ratings** with MongoDB for flexible data
- ✅ **Stock Management** with automatic inventory updates
- ✅ **Admin Panel** for product and order management

### **Technical Features**
- ✅ **Hybrid Database Architecture**: PostgreSQL + MongoDB
- ✅ **Raw SQL Queries** for optimal performance
- ✅ **MongoDB Aggregation** for complex data operations
- ✅ **Responsive Bootstrap UI** with modern design
- ✅ **Pagination** for large datasets
- ✅ **Search & Filtering** capabilities
- ✅ **Dynamic Testimonials** from customer reviews

## 🏗️ Architecture

### **Database Design**
- **PostgreSQL (Supabase)**: Products, orders, customers, categories
- **MongoDB Atlas**: Shopping carts, product reviews, user sessions
- **Raw SQL**: All database operations use optimized SQL queries
- **No Django ORM**: Direct database control for better performance

### **Project Structure**
```
database project/
├── grocery_store/          # Django project settings
├── products/              # Product management & catalog
├── accounts/              # User authentication & profiles
├── orders/                # Order processing & history
├── cart/                  # Shopping cart functionality
├── templates/             # HTML templates
├── static/                # CSS, JS, and media files
├── connection.py          # MongoDB connection utility
├── setup_schema.sql      # PostgreSQL database schema
└── requirements.txt      # Python dependencies
```

## 🛠️ Setup Instructions

### **1. Prerequisites**
- Python 3.8+
- PostgreSQL database (Supabase recommended)
- MongoDB Atlas cluster
- Git

### **2. Clone & Install**
```bash
git clone <repository-url>
cd database-project
pip install -r requirements.txt
```

### **3. Environment Configuration**

Create a `.env` file in the project root with your database credentials:

```env
# PostgreSQL (Supabase) - Cloud database already set up
DB_HOST=aws-0-ap-southeast-1.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres.tgubrjnbwvmqtxzennwp
DB_PASSWORD=INF2003!

# MongoDB Atlas - Cloud database already set up
MONGO_URI=mongodb+srv://adminuser:49zfvg7FMo4uHr2J@cluster0.ssxp2vc.mongodb.net/
MONGO_DB_NAME=my_mongo
```

**Note**: The cloud databases (Supabase PostgreSQL and MongoDB Atlas) are already configured and running.

### **4. Django Setup**

Since the cloud databases are already set up with sample data, you only need to run Django migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### **5. Run Development Server**

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to see your application.

**Note**: The `setup_schema.sql` file already contains sample data including categories, brands, products, customers, and orders, so no additional data setup is needed.

## 📊 Database Schema

### **PostgreSQL Tables (Supabase)**
- **Customer**: User accounts and profiles
- **Product**: Product catalog with categories and brands
- **Category/SubCategory**: Product organization
- **Brand**: Product brands
- **OrderTable**: Customer orders
- **OrderItem**: Individual items in orders
- **Supplier**: Product suppliers

### **MongoDB Collections (Atlas)**
- **Carts**: Shopping cart data with session persistence
- **ProductReviews**: Customer reviews and ratings with voting system

## 🔧 API Endpoints

### **Products**
- `GET /` - Homepage with product catalog
- `GET /search/` - Product search functionality
- `GET /category/<id>/` - Products by category
- `GET /brand/<id>/` - Products by brand
- `GET /product/<id>/` - Product details with reviews

### **Cart & Orders**
- `GET /cart/` - View shopping cart
- `POST /cart/add/<id>/` - Add product to cart
- `POST /cart/update/` - Update cart quantities
- `POST /cart/remove/` - Remove items from cart
- `POST /cart/place-order/` - Place order
- `GET /orders/list/` - Order history with pagination

### **User Management**
- `GET /accounts/login/` - User login
- `GET /accounts/register/` - User registration
- `GET /accounts/profile/` - User profile
- `GET /accounts/logout/` - User logout

### **Admin (Admin Users Only)**
- `GET /manage/` - Product and order management
- `POST /manage/add-product/` - Add new products
- `POST /manage/update-product/<id>/` - Update products

## 🎯 Key Features Explained

### **Hybrid Database Strategy**
- **PostgreSQL**: Structured data (products, orders, users)
- **MongoDB**: Flexible data (carts, reviews, sessions)
- **Benefits**: Best of both worlds - ACID compliance + flexibility

### **Raw SQL Implementation**
- Direct database control for optimal performance
- No Django ORM overhead
- Custom queries for complex operations
- Better understanding of database operations

### **Session Management**
- Custom session handling without Django's built-in auth
- MongoDB for session persistence
- Secure user authentication flow

### **Stock Management**
- Automatic stock level updates when orders are placed
- Stock validation before order processing
- Real-time inventory tracking

## 🚀 Deployment

### **Production Setup**
1. Set `DEBUG=False` in settings
2. Configure production database credentials
3. Set up static file serving
4. Configure HTTPS
5. Set up monitoring and logging

### **Recommended Hosting**
- **Backend**: Railway, Heroku, or DigitalOcean
- **Database**: Supabase (PostgreSQL) + MongoDB Atlas
- **Static Files**: AWS S3 or Cloudflare

## 🔍 Development

### **Running Tests**
```bash
python manage.py test
```

### **Database Migrations**
Since we use raw SQL, migrations are handled manually:
1. Update `setup_schema.sql`
2. Run the updated schema
3. Update any affected views

### **Adding New Features**
1. Update database schema if needed
2. Add new views in appropriate apps
3. Update URL patterns
4. Create/update templates
5. Test thoroughly

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Open an issue in the repository
- Check the documentation
- Review the code comments

---

**Built with ❤️ using Django, PostgreSQL, and MongoDB** 