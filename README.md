# Indian Grocery Store - Inventory Management System

A full-featured web application for managing an Indian grocery store's inventory, orders, and customers. Built with Python Flask, MySQL, and modern web technologies.

## Features

- **User Authentication**: Register, login, and profile management for customers and administrators
- **Product Management**: Browse, search, and filter products with detailed information
- **Shopping Cart**: Add, update, and remove items from cart
- **Order Processing**: Secure checkout process with order history and tracking
- **Admin Dashboard**: Comprehensive dashboard for managing products, orders, customers, and inventory
- **Responsive Design**: Mobile-friendly interface that works on all devices
- **Real-time Updates**: AJAX-based cart and order updates without page reloads

## Prerequisites

- Python 3.8+
- MySQL 8.0+
- Node.js and npm (for frontend assets)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/indian-grocery-store.git
   cd indian-grocery-store
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with the following content:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   SQLALCHEMY_DATABASE_URI=mysql+pymysql://username:password@localhost/grocery_store
   MONGO_URI=mongodb://localhost:27017/grocery_store
   ```

5. **Set up the database**
   - Create a MySQL database named `grocery_store`
   - Run the database migrations:
     ```bash
     flask db upgrade
     ```
   - Initialize the database with sample data:
     ```bash
     python setup_db.py
     ```

6. **Run the application**
   ```bash
   flask run
   ```
   The application will be available at `http://localhost:5000`

## Default Admin Account

- **Username**: admin@example.com
- **Password**: admin123

## Project Structure

```
indian-grocery-store/
├── app.py                  # Main application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in version control)
├── .gitignore
├── README.md              # This file
├── setup_db.py            # Database initialization script
├── migrations/            # Database migrations
│
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── main.js       # Main JavaScript file
│   └── images/            # Images and icons
│
├── templates/            # Jinja2 templates
│   ├── base.html          # Base template
│   ├── home.html          # Home page
│   ├── auth/              # Authentication templates
│   ├── products/          # Product-related templates
│   ├── cart/              # Shopping cart templates
│   ├── orders/            # Order-related templates
│   └── admin/             # Admin panel templates
│
└── routes/               # Application routes
    ├── __init__.py
    ├── auth.py            # Authentication routes
    ├── products.py        # Product routes
    ├── cart.py            # Shopping cart routes
    ├── orders.py          # Order routes
    └── admin.py           # Admin routes
```

## Available Routes

### Public Routes
- `/` - Home page
- `/products` - Product listing
- `/products/<int:product_id>` - Product details
- `/login` - User login
- `/register` - User registration

### Customer Routes (Requires Login)
- `/profile` - User profile
- `/cart` - Shopping cart
- `/checkout` - Checkout process
- `/orders` - Order history
- `/orders/<int:order_id>` - Order details

### Admin Routes (Requires Admin Privileges)
- `/admin` - Admin dashboard
- `/admin/products` - Manage products
- `/admin/orders` - Manage orders
- `/admin/customers` - Manage customers
- `/admin/suppliers` - Manage suppliers
- `/admin/reports` - View sales reports

## API Endpoints

The application provides a RESTful API for frontend interactions:

### Cart API
- `POST /api/cart/add` - Add item to cart
- `POST /api/cart/update/<int:item_id>` - Update cart item quantity
- `POST /api/cart/remove/<int:item_id>` - Remove item from cart

### Order API
- `POST /api/orders` - Create new order
- `GET /api/orders/<int:order_id>` - Get order details
- `PATCH /api/orders/<int:order_id>/status` - Update order status

## Customizing the Application

### Adding New Features
1. Create a new route file in the `routes` directory
2. Define your routes and business logic
3. Create corresponding templates in the `templates` directory
4. Add any new static assets (CSS/JS) to the `static` directory

### Styling
- The application uses Bootstrap 5 for responsive design
- Custom styles are defined in `static/css/style.css`
- Custom JavaScript is in `static/js/main.js`

## Deployment

For production deployment, consider using:

1. **Web Server**: Gunicorn or uWSGI
2. **Reverse Proxy**: Nginx or Apache
3. **Process Manager**: Systemd or Supervisor
4. **Database**: MySQL with proper backups
5. **Environment**: Set `FLASK_ENV=production` and `DEBUG=False`

Example Gunicorn command:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - The web framework used
- [Bootstrap 5](https://getbootstrap.com/) - Frontend framework
- [Font Awesome](https://fontawesome.com/) - Icons
- [jQuery](https://jquery.com/) - JavaScript library
- [Chart.js](https://www.chartjs.org/) - For charts and graphs

---

**Note**: This is a demo application. For production use, ensure you implement proper security measures, input validation, and error handling.
