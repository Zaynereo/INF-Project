from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
from .forms import RegistrationForm, LoginForm

def register_view(request):
    """
    Handles new user registration using raw SQL.
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            with connection.cursor() as cursor:
                # Check if email already exists
                cursor.execute("SELECT 1 FROM customer WHERE email = %s", [email])
                if cursor.fetchone():
                    messages.error(request, 'An account with this email already exists.')
                    
                else:
                    # Hash password and insert new customer
                    hashed_password = make_password(password)
                    cursor.execute(
                        "INSERT INTO customer (name, email, password) VALUES (%s, %s, %s) RETURNING customer_id",
                        [name, email, hashed_password]
                    )
                    customer_id = cursor.fetchone()[0]
                    
                    # Log the user in by setting a session variable
                    request.session['customer_id'] = customer_id
                    request.session['customer_name'] = name
                    messages.success(request, 'Registration successful. Welcome!')
                    return redirect('products:home')
    else:
        form = RegistrationForm()
        
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    """
    Handles user login using raw SQL.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT customer_id, name, password, is_admin FROM customer WHERE email = %s", [email])
                customer = cursor.fetchone()
                
                if customer and check_password(password, customer[2]):
                    # Password is correct, log the user in
                    request.session['customer_id'] = customer[0]
                    request.session['customer_name'] = customer[1]
                    request.session['is_admin'] = customer[3]
                    messages.success(request, 'You have been successfully logged in.')
                    return redirect('products:home')
                else:
                    messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
        
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    """
    Logs the user out by flushing the session.
    """
    request.session.flush()
    messages.success(request, 'You have been successfully logged out.')
    return redirect('products:home')