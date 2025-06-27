from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from connection import get_mongo_connection
import sqlite3
from datetime import datetime
import uuid


def checkout_view(request):
    """Checkout process that converts cart to order"""
    if not request.session.get("customer_id"):
        return redirect("accounts:login")
    
    customer_id = str(request.session.get("customer_id"))
    
    if request.method == 'POST':
        # Process the checkout form
        return process_checkout(request, customer_id)
    
    # GET request - show checkout form
    return show_checkout_form(request, customer_id)


def show_checkout_form(request, customer_id):
    """Display the checkout form with cart data"""
    db = get_mongo_connection()
    cart = db["Carts"].find_one({"customer_id": customer_id, "status": "active"})
    
    if not cart or not cart.get("items"):
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart_detail")
    
    # Calculate totals
    cart_items = cart.get("items", [])
    for item in cart_items:
        item["total_price"] = item["price"] * item["quantity"]
    
    subtotal = sum(item["total_price"] for item in cart_items)
    shipping_cost = 0  # Free shipping for now
    tax_amount = subtotal * 0.08  # 8% tax
    total = subtotal + shipping_cost + tax_amount
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'tax_amount': tax_amount,
        'total': total,
        'customer_id': customer_id,
    }
    
    return render(request, 'orders/checkout.html', context)


def process_checkout(request, customer_id):
    """Process the checkout form and create order"""
    db = get_mongo_connection()
    cart = db["Carts"].find_one({"customer_id": customer_id, "status": "active"})
    
    if not cart or not cart.get("items"):
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart_detail")
    
    # Get form data
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    address = request.POST.get('address')
    city = request.POST.get('city')
    state = request.POST.get('state')
    zip_code = request.POST.get('zip_code')
    notes = request.POST.get('notes', '')
    
    # Validate required fields
    required_fields = [first_name, last_name, email, phone, address, city, state, zip_code]
    if not all(required_fields):
        messages.error(request, "Please fill in all required fields.")
        return show_checkout_form(request, customer_id)
    
    try:
        # Create order in database
        order_id = create_order_in_database(
            customer_id, cart, first_name, last_name, email, phone, 
            address, city, state, zip_code, notes
        )
        
        # Clear the cart
        db["Carts"].update_one(
            {"customer_id": customer_id, "status": "active"},
            {"$set": {"items": []}}
        )
        
        messages.success(request, f"Order #{order_id} created successfully!")
        return redirect("orders:order_detail", order_id=order_id)
        
    except Exception as e:
        messages.error(request, f"Error creating order: {str(e)}")
        return show_checkout_form(request, customer_id)


def create_order_in_database(customer_id, cart, first_name, last_name, email, phone, 
                           address, city, state, zip_code, notes):
    """Create order in SQLite database"""
    conn = sqlite3.connect('grocery_store.db')
    cursor = conn.cursor()
    
    try:
        # Calculate totals
        cart_items = cart.get("items", [])
        subtotal = sum(item["price"] * item["quantity"] for item in cart_items)
        shipping_cost = 0
        tax_amount = subtotal * 0.08
        total_amount = subtotal + shipping_cost + tax_amount
        
        # Generate order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Insert order
        cursor.execute("""
            INSERT INTO Orders (customer_id, order_number, order_date, status, 
                              subtotal, shipping_cost, tax_amount, total_amount,
                              shipping_address, billing_address, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(customer_id), order_number, datetime.now(), 'pending',
            subtotal, shipping_cost, tax_amount, total_amount,
            f"{address}, {city}, {state} {zip_code}",
            f"{address}, {city}, {state} {zip_code}",
            'credit_card', notes
        ))
        
        order_id = cursor.lastrowid
        
        # Insert order items
        for item in cart_items:
            cursor.execute("""
                INSERT INTO OrderItems (order_id, product_id, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
            """, (
                order_id, int(item["product_id"]), item["quantity"], 
                item["price"], item["price"] * item["quantity"]
            ))
        
        # Insert order history
        cursor.execute("""
            INSERT INTO OrderHistory (order_id, status, created_at, created_by, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, 'pending', datetime.now(), int(customer_id), 'Order created'))
        
        conn.commit()
        return order_id
        
    finally:
        conn.close()


def order_list_view(request):
    """Display user's order history"""
    if not request.session.get("customer_id"):
        return redirect("accounts:login")
    
    customer_id = str(request.session.get("customer_id"))
    
    conn = sqlite3.connect('grocery_store.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT o.order_id, o.order_number, o.order_date, o.status, o.total_amount
            FROM Orders o
            WHERE o.customer_id = ?
            ORDER BY o.order_date DESC
        """, (int(customer_id),))
        
        orders = []
        for row in cursor.fetchall():
            orders.append({
                'order_id': row[0],
                'order_number': row[1],
                'order_date': row[2],
                'status': row[3],
                'total_amount': row[4]
            })
        
        context = {'orders': orders}
        return render(request, 'orders/list.html', context)
        
    finally:
        conn.close()


def order_detail_view(request, order_id):
    """Display order details"""
    if not request.session.get("customer_id"):
        return redirect("accounts:login")
    
    customer_id = str(request.session.get("customer_id"))
    
    conn = sqlite3.connect('grocery_store.db')
    cursor = conn.cursor()
    
    try:
        # Get order details
        cursor.execute("""
            SELECT o.order_id, o.order_number, o.order_date, o.status, 
                   o.subtotal, o.shipping_cost, o.tax_amount, o.total_amount,
                   o.shipping_address, o.billing_address, o.payment_method, o.notes
            FROM Orders o
            WHERE o.order_id = ? AND o.customer_id = ?
        """, (order_id, int(customer_id)))
        
        order_row = cursor.fetchone()
        if not order_row:
            messages.error(request, "Order not found.")
            return redirect("orders:order_list")
        
        order = {
            'order_id': order_row[0],
            'order_number': order_row[1],
            'order_date': order_row[2],
            'status': order_row[3],
            'subtotal': order_row[4],
            'shipping_cost': order_row[5],
            'tax_amount': order_row[6],
            'total_amount': order_row[7],
            'shipping_address': order_row[8],
            'billing_address': order_row[9],
            'payment_method': order_row[10],
            'notes': order_row[11]
        }
        
        # Get order items
        cursor.execute("""
            SELECT oi.order_item_id, oi.product_id, oi.quantity, oi.unit_price, oi.total_price,
                   p.name, p.description
            FROM OrderItems oi
            JOIN Products p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
        """, (order_id,))
        
        order_items = []
        for row in cursor.fetchall():
            order_items.append({
                'order_item_id': row[0],
                'product_id': row[1],
                'quantity': row[2],
                'unit_price': row[3],
                'total_price': row[4],
                'name': row[5],
                'description': row[6]
            })
        
        # Get order history
        cursor.execute("""
            SELECT oh.status, oh.created_at, oh.notes
            FROM OrderHistory oh
            WHERE oh.order_id = ?
            ORDER BY oh.created_at DESC
        """, (order_id,))
        
        order_history = []
        for row in cursor.fetchall():
            order_history.append({
                'status': row[0],
                'created_at': row[1],
                'notes': row[2]
            })
        
        context = {
            'order': order,
            'order_items': order_items,
            'order_history': order_history
        }
        
        return render(request, 'orders/order_detail.html', context)
        
    finally:
        conn.close()
