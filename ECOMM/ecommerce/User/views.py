from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
import re
from django.contrib.auth.views import LoginView
from .forms import SignupForm, SigninForm
from django.urls import reverse, reverse_lazy
from .models import Account, Profile
from django.views.generic import CreateView
from Store.models import *
from decimal import Decimal

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
@login_required
def buyerdashboard(request):
    try:

        allorders= Order.objects.all()
        total_orders = Decimal(allorders.count())
        allwishlist = Wishlist.objects.all()
        mywishlist = Decimal(allwishlist.count())
    except:
        total_orders = Decimal(0)
        mywishlist = Decimal(0)
        

     
    return render(request, 'User/buyerdashboard.html', {"total_orders":total_orders, "mywishlist":mywishlist},)

def index(request):
    return render(request, "User/index.html")    
