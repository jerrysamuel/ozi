from .models import Account, Profile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django import forms
from django.utils.translation import gettext_lazy as _

class SignupForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ('username', 'email','role', )

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            self.fields[field_name].widget.attrs['placeholder'] = field.label
            self.fields[field_name].widget.attrs['class'] = 'bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'
            self.fields[field_name].widget.attrs['required'] = True

class SigninForm(AuthenticationForm):
    username = UsernameField(widget=forms.EmailInput(attrs={
        'autofocus': True, 
        'class': 'bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
        'placeholder': 'name@company.com'
    }))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
            'placeholder': '••••••••'
        }),
    )
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['fullname', 'age', 'address', 'phone', 'state', 'bio', 'image']
        widgets = {
            'fullname': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'age': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Age'}),
            'address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'state': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'State'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Short Bio'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:  # If no image is provided
            return None
        return image