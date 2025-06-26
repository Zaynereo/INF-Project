from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from .forms import RegistrationForm, LoginForm, ProfileForm

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
                    cursor.execute(
                        "INSERT INTO customer (name, email, password) VALUES (%s, %s, %s) RETURNING customer_id",
                        [name, email, password]
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
                
                if customer and customer[2] == password:
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

def profile_view(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, 'You must be logged in to view your profile.')
        return redirect('accounts:login')

    with connection.cursor() as cursor:
        cursor.execute("SELECT name, email, phone, password FROM customer WHERE customer_id = %s", [customer_id])
        row = cursor.fetchone()
        if not row:
            messages.error(request, 'User not found.')
            return redirect('products:home')
        current_data = {'name': row[0], 'email': row[1], 'phone': row[2] or '', 'password': row[3]}

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            # Only update password if provided
            if password:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE customer SET name=%s, email=%s, phone=%s, password=%s WHERE customer_id=%s", [name, email, phone, password, customer_id])
            else:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE customer SET name=%s, email=%s, phone=%s WHERE customer_id=%s", [name, email, phone, customer_id])
            # Update session info
            request.session['customer_name'] = name
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(initial={'name': current_data['name'], 'email': current_data['email'], 'phone': current_data['phone']})

    return render(request, 'accounts/profile.html', {'form': form, 'user': current_data})