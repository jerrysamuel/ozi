from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
import re
from django.contrib.auth.views import LoginView
from .forms import SignupForm, SigninForm
from django.urls import reverse, reverse_lazy
from .models import Account, Profile
from django.views.generic import CreateView
class SignUpView(CreateView):
    form_class = SignupForm
    template_name = "User/signup.html"
    success_url = "/user/signin/"
    
class SignInView(LoginView):
    form_class = SigninForm
    template_name = "User/signin.html"
    
    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_admin:
                # Redirect admin to admin dashboard
                return reverse_lazy("index")  # Define admin_dashboard URL
            elif user.role =="buyer":
                # Redirect customer to customer dashboard
                return reverse_lazy("buyerdashboard")  # Define customer_dashboard URL
            elif user.role =="seller":
                # Redirect waiter to waiter dashboard
                return reverse_lazy("sellerdashboard")  # Define waiter_dashboard URL
        # Default redirect to dashboard
        return reverse_lazy("index")
    
def signout_view(request):
    logout(request)
    return redirect(reverse('signin'))


def sellerdashboard(request):
    return render(request, 'User/sellerdashboard.html')

def buyerdashboard(request):
    return render(request, 'User/buyerdashboard.html')

def index(request):
    return render(request, "User/index.html")    
