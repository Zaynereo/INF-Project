from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from connection import get_mongo_connection
from products.models import Product
from django.views import View
from django.db import connection



class CartView(ListView):
    template_name = 'cart/cart_detail.html'
    context_object_name = 'cart_items'

    #checks if logged in, if not in -> login page
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("customer_id"):
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)
    
    #retrieve items from mongoDB for the logged in user, ret list of items or an empty one
    def get_queryset(self):

        customer_id = str(self.request.session.get("customer_id"))
        if not customer_id:
            return []  # or: redirect('accounts:login') but ListView expects a list
        
        db = get_mongo_connection()
        cart = db["Carts"].find_one({"customer_id": customer_id, "status": "active"})
        return cart["items"] if cart else[]
    
    #quantity,subtotal,total
    def get_context_data(self, **kwargs):

        customer_id = str(self.request.session.get("customer_id"))
        if not customer_id:
            return super().get_context_data(**kwargs)  # optionally handle unauthenticated
        
        context = super().get_context_data(**kwargs)
        db = get_mongo_connection()
        cart = db["Carts"].find_one({"customer_id": customer_id, "status": "active"})

        if cart:

            for item in cart["items"]:
                item["total_price"] = item["price"] * item["quantity"]
            subtotal = sum(item["total_price"] for item in cart["items"])
    
            context['cart'] = cart
            
            context['cart_items'] = cart["items"]
            context['total_amount'] = subtotal
            context['subtotal'] = subtotal
            context['total'] = subtotal 
            context['item_count'] = sum(i['quantity'] for i in cart['items'])
            #context['total_amount'] = sum(i['price'] * i['quantity'] for i in cart['items'])
        else:
            context['cart'] = {}
            context['cart_items'] = []
            context['total_amount'] = 0
            context['subtotal'] = 0
            context['total'] = 0
            context['item_count'] = 0

        return context


class AddToCartView(View):

    #checks if logged in when adding to cart, if not in -> login page
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("customer_id"):
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    #retrieve prod id and quantity from POST, add item into cart/increase its quantity
    def post(self, request, *args, **kwargs):

        customer_id = str(request.session.get("customer_id"))
        if not customer_id:
            return redirect("accounts:login")
        
        db = get_mongo_connection()
        product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        quantity = int(request.POST.get('quantity', 1))

        product_id = str(product.product_id)

        #Ensure cart exsists
        cart = db["Carts"].find_one({"customer_id": customer_id, "status": "active"})

        if not cart:
            db["Carts"].insert_one({
                "customer_id": customer_id,
                "items": [],
                "status": "active"
            })

        #Check if item exists in cart already
        existing_item = db["Carts"].find_one({
            "customer_id": customer_id,
            "status": "active",
            "items.product_id": product_id
        })

        if existing_item:
            # If item already exists, increment quantity
            db["Carts"].update_one(
                {
                    "customer_id": customer_id,
                    "status": "active",
                    "items.product_id": product_id
                },
                {
                    "$inc": {"items.$.quantity": quantity}
                }
            )
        else:
            
            db["Carts"].update_one(
                {"customer_id": customer_id, "status": "active"},
                {
                    "$push": {
                        "items": {
                            "product_id": str(product.product_id),
                            "name": product.name,
                            "price": float(product.sale_price),
                            "quantity": quantity
                        }
                    }
                }
            )

        messages.success(request, f"{product.name} added to cart.")
        return redirect("cart:cart_detail")

class UpdateCartItemView(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("customer_id"):
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    #gets prod id and updated quantity
    def post(self, request, *args, **kwargs):

        customer_id = str(request.session.get("customer_id"))
        if not customer_id:
            return redirect("accounts:login")

        db = get_mongo_connection()
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        print(f"Updating {product_id} to quantity {quantity}")


        db["Carts"].update_one(
            {
                "customer_id": customer_id,
                "status": "active",
                "items.product_id": product_id
            },
            {
                "$set": {"items.$.quantity": quantity}
            }
        )

        messages.success(request, "Cart updated successfully.")
        return redirect("cart:cart_detail")

class RemoveFromCartView(View): #single removal

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("customer_id"):
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    #gets prod id from POST data to use for removal
    def post(self, request, *args, **kwargs):

        customer_id = str(request.session.get("customer_id"))
        if not customer_id:
            return redirect("accounts:login")

        db = get_mongo_connection()
        product_id = request.POST.get("product_id")

        db["Carts"].update_one(
            {"customer_id": customer_id, "status": "active"},
            {"$pull": {"items": {"product_id": product_id}}}
        )

        messages.success(request, "Item removed from cart.")
        return redirect("cart:cart_detail")
    
class ClearCartView(View): #remove all

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("customer_id"):
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        customer_id = str(request.session.get("customer_id"))
        if not customer_id:
            return redirect("accounts:login")

        db = get_mongo_connection()
        db["Carts"].update_one(
            {"customer_id": customer_id, "status": "active"},
            {"$set": {"items": []}}
        )

        messages.success(request, "Cart cleared successfully.")
        return redirect("cart:cart_detail")

class PlaceOrderView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("customer_id"):
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        customer_id = str(request.session.get("customer_id"))
        if not customer_id:
            return redirect("accounts:login")

        db = get_mongo_connection()
        cart = db["Carts"].find_one({"customer_id": customer_id, "status": "active"})

        if not cart or not cart.get("items"):
            messages.error(request, "Your cart is empty. Cannot place order.")
            return redirect("cart:cart_detail")

        try:
            # Create order in database
            order_id = self.create_order_in_database(customer_id, cart)
            
            # Clear the cart
            db["Carts"].update_one(
                {"customer_id": customer_id, "status": "active"},
                {"$set": {"items": []}}
            )

            messages.success(request, "Order placed successfully! Thank you for your purchase.")
            return redirect("orders:order_list")
            
        except Exception as e:
            messages.error(request, f"Error placing order: {str(e)}")
            return redirect("cart:cart_detail")

    def create_order_in_database(self, customer_id, cart):
        """Create order in PostgreSQL database and update stock levels"""
        from datetime import datetime
        
        with connection.cursor() as cursor:
            # Calculate totals
            cart_items = cart.get("items", [])
            subtotal = sum(item["price"] * item["quantity"] for item in cart_items)
            total_amount = subtotal  # No tax or shipping for simplicity
            
            # Check stock levels before placing order
            for item in cart_items:
                cursor.execute("""
                    SELECT stock_level FROM product WHERE product_id = %s
                """, (int(item["product_id"]),))
                current_stock = cursor.fetchone()
                
                if not current_stock:
                    raise Exception(f"Product with ID {item['product_id']} not found")
                
                if current_stock[0] < item["quantity"]:
                    raise Exception(f"Insufficient stock for product {item['name']}. Available: {current_stock[0]}, Requested: {item['quantity']}")
            
            # Insert order
            cursor.execute("""
                INSERT INTO ordertable (customer_id, order_date, total_amount)
                VALUES (%s, %s, %s)
                RETURNING order_id
            """, (
                int(customer_id), datetime.now(), total_amount
            ))
            
            order_id = cursor.fetchone()[0]
            
            # Insert order items and update stock levels
            for item in cart_items:
                # Insert order item
                cursor.execute("""
                    INSERT INTO orderitem (order_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                """, (
                    order_id, int(item["product_id"]), item["quantity"]
                ))
                
                # Update stock level
                cursor.execute("""
                    UPDATE product 
                    SET stock_level = stock_level - %s 
                    WHERE product_id = %s
                """, (item["quantity"], int(item["product_id"])))
            
            return order_id