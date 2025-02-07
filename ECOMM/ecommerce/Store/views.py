from decimal import Decimal
from django.forms import modelform_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.db import transaction
from .models import *
from .forms import ReviewForm
from User.decorators import buyer_required, seller_required


def product_detail(request, product_id):
    # Fetch the product or return a 404 error
    product = get_object_or_404(Product, id=product_id)
    
    # Get all reviews for the product
    reviews = MyReview.objects.filter(product=product)
    avg_rating = MyReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    
    # If no reviews, set avg_rating to 0
    if avg_rating is None:
        avg_rating = 0
    
    # Initialize the review form
    form = ReviewForm(request.POST or None)
    
    if request.method == 'POST':
        # Process the form submission
        if form.is_valid():
            # Create or update the review
            MyReview.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'description': form.cleaned_data['description'],
                },
            )
            return redirect('product_detail', product_id=product_id)

    # Pass the product, reviews, and form to the template
    context = {
        'avg_rating': avg_rating,
        'product': product,
        'reviews': reviews,
        'form': form
    }
    return render(request, 'Store/product_details.html', context)

@login_required
def createstore(request):
    if request.method == "POST":
        store = Mystore.objects.create(
            owner=request.user,
            name=request.POST.get('name'),
            cac_name=request.POST.get('cac_name'),
            physicaladdress=request.POST.get('physicaladdress'),
        )
        messages.success(request, "Store created successfully.")
        return redirect("sellerdashboard")
    return render(request, "Store/createstore.html")
@login_required
def add_product(request):
    """Add a product to the store."""
    try:
        store = Mystore.objects.get(owner=request.user)
    except Mystore.DoesNotExist:
        messages.error(request, "You must create a store before adding products.")
        return redirect("createstore")  # Redirect to a store creation page or appropriate action

    if request.method == "POST":
        product = Product.objects.create(
            store=store,
            name=request.POST.get('name'),
            price=request.POST.get('price'),
            description=request.POST.get('description'),
            image=request.FILES.get('image'),
        )
        messages.success(request, "Product added successfully.")
        return redirect("sellerdashboard")

    return render(request, "Store/add_product.html", {"store": store})
@login_required
@buyer_required
def view_cart(request):
    """Display items in the user's cart."""
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    cart_count = Cart.objects.filter(user=request.user).aggregate(Sum('quantity'))['quantity__sum'] or 0
    return render(request, "Store/cart.html", {"cart_items": cart_items, "total_price": total_price, "cart_count": cart_count})


@login_required
@buyer_required
def add_to_cart(request, product_id):
    """Add a product to the cart or update quantity if it already exists."""
    if request.user.role == "seller":
        messages.error(request, f"a seller cannot add items to cart.")
        return redirect("sellerdashboard")
    else:
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
@buyer_required
def remove_from_cart(request, cart_item_id):
    """Remove an item from the cart."""
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.warning(request, f"Removed {cart_item.product.name} from your cart.")
    return redirect("view_cart")

@login_required
@buyer_required

def checkout(request):
    # Ensure the user has a cart
    try:
        cart_items = Cart.objects.filter(user=request.user)
    except Cart.DoesNotExist:
        cart_items = []

    if not cart_items:
        return redirect('view_cart')

    # Calculate the total amount
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    item_subtotals = [(item, item.product.price * item.quantity) for item in cart_items]

    # Get the user's profile
    profile = request.user.profile  # Assumes a OneToOneField between User and Profile

    if request.method == "POST":
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        state = request.POST.get("state")

        # Start atomic transaction for order creation and profile update
        with transaction.atomic():
            try:
                # Update the profile with phone and address
                profile.phone = phone
                profile.address = address
                profile.state = state
                profile.save()

                # Create a placeholder order but don't save it yet
                order = Order(
                    buyer=request.user,
                    seller=cart_items[0].product.store.owner,  # Assumes all items are from the same seller
                    amount=total_amount,
                    status=Order.PENDING,
                )

                # Initiate payment (add to escrow)
                if order.initiate_payment():  # Assuming initiate_payment handles payment gateway logic
                    order.save()
                    
                for cart_item in cart_items:
                    OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                )


                    # Clear the user's cart after the order is created
                    cart_items.delete()

                    messages.success(request, "Order created successfully. Your payment is in escrow.")
                    return redirect("buyerdashboard")
                else:
                    messages.error(request, "Payment initiation failed. Order not created.")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return redirect("checkout")

    return render(request, "Store/checkout.html", {
        "cart_items": cart_items,
        "total_amount": total_amount,
        "item_subtotals": item_subtotals,
        "profile": profile,  # Pass the profile to prefill fields if needed
    })
@login_required
@buyer_required
def order_summary(request):
    # Get all orders for the authenticated buyer
    orders = Order.objects.filter(buyer=request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        order_id = request.POST.get("order_id")
        order = get_object_or_404(Order, id=order_id, buyer=request.user)

        try:
            if action == "accept_delivery":
                    if order.status == Order.PENDING:
                        order.complete_order()
                        messages.success(request, f"Order #{order.id} completed. Seller earnings and admin fee processed.")
                    else:
                        messages.error(request, f"Order #{order.id} cannot be completed in its current state.")
            

            elif action == "reject_delivery":

                    if order.status == Order.PENDING:
                        # Update the order status
                        order.status = Order.CANCELLED
                        order.save()
                        
                        # Automatically create a Dispute entry
                        Dispute.objects.create(
                            order=order,
                            buyer_email=order.buyer.email,  # Email of the buyer from the order
                            seller_email=order.seller.email,  # Email of the seller from the order
                        )
                        
                        messages.success(request, f"You have rejected delivery for Order #{order.id}. A dispute has been opened.")
                    else:
                        messages.error(request, f"Order #{order.id} cannot be rejected in its current state.")

            elif action == "cancel_order":
                if order.status == Order.PENDING:
                    order.cancel_order()
                    messages.success(request, f"Order #{order.id} has been cancelled.")
                else:
                    messages.error(request, f"Order #{order.id} cannot be cancelled.")

            elif action == "open_dispute":
                if order.status in [Order.PENDING, Order.COMPLETED]:
                    messages.success(request, f"A dispute has been opened for Order #{order.id}.")
                else:
                    messages.error(request, f"Cannot open a dispute for Order #{order.id}.")

        except Exception as e:
            messages.error(request, f"Error processing your request: {e}")

        return redirect("order_summary")

    return render(request, "Store/order_summary.html", {"orders": orders})

@login_required
@buyer_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = MyReview.objects.filter(product=product)
    form = ReviewForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # Create or update the review for the product
            MyReview.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'description': form.cleaned_data['description'],
                },
            )
            return redirect('product_details', id=product_id)  # Adjust to your product details URL name

    return render(request, 'Store/add_review.html', {'form': form, 'product': product, 'reviews':reviews})



@login_required
def add_to_wishlist(request, product_id):
    if request.method == "POST":
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "You need to log in to add items to your wishlist.")
            return redirect('login')

        # Get the product
        product = get_object_or_404(Product, id=product_id)

        # Check if the product is already in the user's wishlist
        wishlist_item, created = MyWishlist.objects.get_or_create(user=request.user, product=product)

        if created:
            messages.success(request, f"{product.name} has been added to your wishlist!")
        else:
            messages.info(request, f"{product.name} is already in your wishlist.")

        return redirect('product_detail', product_id=product_id)

    # Redirect back if the method is not POST
    return redirect('product_list')

@login_required
def wishlist_view(request):
    # Fetch all wishlist items for the logged-in user
    wishlist_items = MyWishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'Store/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def remove_from_wishlist(request, product_id):
    if request.method == "POST":
        MyWishlist.objects.filter(user=request.user, product_id=product_id).delete()
        messages.success(request, "Item removed from your wishlist.")
    return redirect('wishlist')