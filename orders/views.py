from django.shortcuts import render, redirect
from django.contrib import messages
from connection import get_mongo_connection
from django.db import connection
from datetime import datetime


def order_list_view(request):
    """Display user's order history with pagination"""
    if not request.session.get("customer_id"):
        return redirect("accounts:login")
    
    customer_id = str(request.session.get("customer_id"))
    page = int(request.GET.get('page', 1))
    ORDERS_PER_PAGE = 10
    
    with connection.cursor() as cursor:
        # Get total count for pagination
        cursor.execute("""
            SELECT COUNT(*)
            FROM ordertable o
            WHERE o.customer_id = %s
        """, (int(customer_id),))
        total_orders = cursor.fetchone()[0]
        total_pages = (total_orders + ORDERS_PER_PAGE - 1) // ORDERS_PER_PAGE
        
        # Get paginated orders
        cursor.execute("""
            SELECT o.order_id, o.order_date, o.total_amount
            FROM ordertable o
            WHERE o.customer_id = %s
            ORDER BY o.order_date DESC
            LIMIT %s OFFSET %s
        """, (int(customer_id), ORDERS_PER_PAGE, (page - 1) * ORDERS_PER_PAGE))
        
        orders = []
        order_ids = []
        for row in cursor.fetchall():
            orders.append({
                'order_id': row[0],
                'order_date': row[1],
                'status': 'completed',  # Default status since schema doesn't have status
                'total_amount': row[2]
            })
            order_ids.append(row[0])
        
        # Get order details for all orders on this page
        order_details = {}
        if order_ids:
            format_strings = ','.join(['%s'] * len(order_ids))
            cursor.execute(f"""
                SELECT oi.order_id, p.name, oi.quantity, p.sale_price
                FROM orderitem oi
                JOIN product p ON oi.product_id = p.product_id
                WHERE oi.order_id IN ({format_strings})
            """, order_ids)
            
            for row in cursor.fetchall():
                order_id, product_name, quantity, sale_price = row
                order_details.setdefault(order_id, []).append({
                    'name': product_name,
                    'quantity': quantity,
                    'unit_price': sale_price,
                })
        
        context = {
            'orders': orders,
            'order_details': order_details,
            'page': page,
            'total_pages': total_pages,
            'has_previous': page > 1,
            'has_next': page < total_pages,
            'previous_page_number': page - 1,
            'next_page_number': page + 1,
        }
        return render(request, 'orders/list.html', context)
