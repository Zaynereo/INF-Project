from django import forms
from .models import ProductReview


class ProductReviewForm(forms.ModelForm):
    """Form for submitting product reviews"""
    
    class Meta:
        model = ProductReview
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Review title'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your review here...'}),
        }
    
    def clean_rating(self):
        """Validate rating is between 1 and 5"""
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError('Rating must be between 1 and 5.')
        return rating
    
    def clean_title(self):
        """Validate title length"""
        title = self.cleaned_data.get('title')
        if title and len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters long.')
        return title
    
    def clean_comment(self):
        """Validate comment length"""
        comment = self.cleaned_data.get('comment')
        if comment and len(comment) < 10:
            raise forms.ValidationError('Comment must be at least 10 characters long.')
        return comment 