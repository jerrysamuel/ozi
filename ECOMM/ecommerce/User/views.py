from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
import requests
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import buyer_required, seller_required
import re
from django.contrib.auth.views import LoginView
from .forms import SignupForm, SigninForm, ProfileForm
from django.urls import reverse, reverse_lazy
from .models import Account, Profile, Wallet,Adminwallet
from django.views.generic import CreateView
from Store.models import *
from decimal import Decimal
from django.db.models import Sum
from django.db.models import Q


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
@login_required
def profile(request):
    """
    View to display and update the user's profile information.
    """
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Save the updated profile
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')  # Redirect to profile page after saving
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'User/profile.html', {'form': form, 'profile': profile})

    
def signout_view(request):
    logout(request)
    return redirect(reverse('signin'))

@login_required
@seller_required
def sellerdashboard(request):
    
    try:
        seller = request.user  # Assuming the user is the seller
        completed_orders = Order.count_completed_orders_for_seller(seller)
        pending_orders = Order.count_pending_orders_for_seller(seller)
        store = Mystore.objects.get(owner=request.user)  
        product_count = store.product_count() 
        recent_orders = Order.objects.filter(seller=seller).order_by('-created_at')
    except Mystore.DoesNotExist:
        store = None
        product_count = Decimal(0)
        completed_orders = Decimal(0)
        pending_orders = Decimal(0)
        recent_orders = []
    return render(request, 'User/sellerdashboard.html', {"store": store, "product_count": product_count, "completed_orders": completed_orders, "pending_orders": pending_orders, "recent_orders": recent_orders})

@login_required
@buyer_required
def buyerdashboard(request):
    cart_count = Cart.objects.filter(user=request.user).aggregate(Sum('quantity'))['quantity__sum'] or 0
    order_count = Order.objects.filter(buyer=request.user).count() or Decimal(0)
    wishlist_count = MyWishlist.objects.filter(user=request.user).count() or Decimal(0)
    
    try:

        allorders= Order.objects.all()
        total_orders = Decimal(allorders.count())
        allwishlist = MyWishlist.objects.all()
        mywishlist = Decimal(allwishlist.count())
        allreviews = MyReview.objects.filter(user=request.user)
        reviews = Decimal(allreviews.count())
        wallet = request.user.wallet

    except:
        total_orders = Decimal(0)
        mywishlist = Decimal(0)
        reviews = Decimal(0)
        wallet = Decimal(0)
       

     
    return render(request, 'User/buyerdashboard.html', { "reviews":reviews, "cart_count": cart_count, 'wallet': wallet, 'order_count': order_count, 'wishlist_count': wishlist_count, 'total_orders': total_orders, 'mywishlist': mywishlist})
@login_required

def index(request):
    cart_count = Cart.objects.filter(user=request.user).aggregate(Sum('quantity'))['quantity__sum']
    store = Mystore.objects.filter(owner=request.user)

    # Annotate products with their average rating
    products = Product.objects.annotate(avg_rating=Avg('reviews__rating'))

    # Handle search functionality
    search_term = request.GET.get('search', '')
    if search_term:
        products = products.filter(Q(name__icontains=search_term) | Q(description__icontains=search_term))

    return render(
        request,
        "User/index.html",
        {
            "cart_count": cart_count,
            "products": products,
            "store": store,
            "search_term": search_term,
        },
    )
def searchresult(request):
      products = Product.objects.all()
   

      search_term = request.GET.get('search', '')  # Default to an empty string if no search term is provided

        # If there's a search term, filter the products
      if search_term:
            products = products.filter(Q(name__icontains=search_term) | Q(description__icontains=search_term))
            # This filters products where either the name or description contains the search term (case insensitive)

      return render(request, "User/searchresult.html", {'search_term':search_term, 'products':products})

@login_required
def deposit_to_wallet(request):
    """Handles wallet deposits via Paystack."""
    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get("amount"))  # Amount in Naira
            if amount <= 0:
                messages.error(request, "Deposit amount must be greater than zero.")
                return redirect("deposit_to_wallet")

            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "email": request.user.email,
                "amount": int(amount * 100),  # Convert Naira to Kobo
                "reference": f"wallet-{request.user.id}-{int(amount * 100)}",
                "callback_url": request.build_absolute_uri("/verify-deposit/"),
            }

            response = requests.post(
                "https://api.paystack.co/transaction/initialize", headers=headers, json=data
            )
            response_data = response.json()

            if response_data.get("status"):
                return redirect(response_data["data"]["authorization_url"])
            else:
                messages.error(request, "Failed to initiate payment. Please try again.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
        return redirect("deposit_to_wallet")

    return render(request, "User/deposit.html")

@login_required
def verify_deposit(request):
    """Verifies the wallet deposit payment."""
    reference = request.GET.get("reference")
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    try:
        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}", headers=headers
        )
        response_data = response.json()

        if response_data.get("status") and response_data["data"]["status"] == "success":
            amount = Decimal(response_data["data"]["amount"]) / 100  # Convert Kobo to Naira
            request.user.wallet.deposit(amount)  # Use the deposit method
            messages.success(request, "Wallet deposit successful!")
            return redirect("buyerdashboard")
        else:
            messages.error(request, "Failed to verify deposit. Please try again.")
    except Exception as e:
        messages.error(request, f"An error occurred during verification: {e}")

    return redirect("deposit_to_wallet")
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url="index")
@login_required
def adminwallet(request):
    adminwallets = Adminwallet.objects.get(id=1)
    balance = adminwallets.balance
    return render(request, "User/adminwallet.html", {"balance": balance})

@login_required
def seller_products(request):
    try:
        # Fetch the store associated with the logged-in user
        store = Mystore.objects.get(owner=request.user)
        # Retrieve all products for the store
        products = store.products.all()
    except Mystore.DoesNotExist:
        # If no store exists, return an empty product list
        products = []

    return render(request, "User/products.html", {"products": products})
@login_required
def store_orders(request):
    try:
        # Get the store owned by the logged-in user
        store = Mystore.objects.get(owner=request.user)
        # Get all orders linked to products from this store
        orders = Order.objects.filter(seller=request.user).order_by('-created_at')
    except Mystore.DoesNotExist:
        store = None
        orders = []

    return render(request, "User/store_orders.html", {"store": store, "orders": orders, })    