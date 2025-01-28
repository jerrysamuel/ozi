from django import forms
from .models import MyReview

class ReviewForm(forms.ModelForm):
    class Meta:
        model = MyReview
        fields = ['rating', 'description']
        widgets = {
    'rating': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'block w-full mt-1 p-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none'}),
    'description': forms.Textarea(attrs={'class': 'block w-full mt-1 p-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none', 'rows': 4}),
}
