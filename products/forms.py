from django import forms
from .models import Product, Brand, Category, Subcategory


class ProductForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}), required=False)
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    subcategory = forms.ModelChoiceField(queryset=Subcategory.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    market_price = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    sale_price = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    unit = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    stock_level = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    rating = forms.DecimalField(max_digits=3, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)

class ReviewForm(forms.Form):
    rating = forms.DecimalField(min_value=0, max_value=5, decimal_places=1)
    review = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), max_length=1000)