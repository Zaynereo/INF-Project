from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import CustomerProfile, Address
from orders.models import Order
from cart.models import Wishlist
from django.http import HttpResponse
from django.contrib.auth import login
from .forms import UserRegistrationForm


class ProfileView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Profile page coming soon.", content_type="text/plain")


class ProfileUpdateView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Profile update page coming soon.", content_type="text/plain")


class AddressListView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Address list page coming soon.", content_type="text/plain")


class AddressCreateView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Address create page coming soon.", content_type="text/plain")


class AddressUpdateView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Address update page coming soon.", content_type="text/plain")


class AddressDeleteView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Address delete page coming soon.", content_type="text/plain")


class OrderHistoryView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Order history page coming soon.", content_type="text/plain")


class OrderDetailView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Order detail page coming soon.", content_type="text/plain")


class WishlistView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Wishlist page coming soon.", content_type="text/plain")


def register(request):
    """
    Handle user registration.
    Creates a new user and logs them in upon successful registration.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            # Log the user in
            login(request, new_user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('products:home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})
