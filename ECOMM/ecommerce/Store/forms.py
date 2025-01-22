from django import forms
from .models import MyReviews

class ReviewForm(forms.ModelForm):
    class Meta:
        model = MyReviews
        fields = ['rating', 'description']
        widgets = {
            'rating': forms.Select(choices=MyReviews.RATING_CHOICES, attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Write your review here...'}),
        }
