from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum

from .models import *


def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {'product': product}
    return render(request, 'product_detail.html', context)



@login_required
def view_cart(request):
    """Display items in the user's cart."""
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    cart_count = Cart.objects.filter(user=request.user).aggregate(Sum('quantity'))['quantity__sum'] or 0
    return render(request, "Store/cart.html", {"cart_items": cart_items, "total_price": total_price, "cart_count": cart_count})


@login_required
def add_to_cart(request, product_id):
    """Add a product to the cart or update quantity if it already exists."""
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.info(request, f"Updated quantity of {product.name} in your cart.")
    else:
        messages.success(request, f"Added {product.name} to your cart.")
    return redirect("view_cart")


@login_required
def remove_from_cart(request, cart_item_id):
    """Remove an item from the cart."""
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.warning(request, f"Removed {cart_item.product.name} from your cart.")
    return redirect("view_cart")

