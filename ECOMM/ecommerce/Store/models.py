from datetime import timedelta, timezone
from decimal import Decimal
from django.conf import settings
from django.db import models
from User.models import Account, Adminwallet

from django.contrib.auth import get_user_model


class Mystore(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cac_name = models.CharField(max_length=100)
    physicaladdress = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name


    def verifications():
       pass

    def product_count(self):
        # Count products linked to this specific store
        return Product.objects.filter(store=self).count()


class Product(models.Model):
    store = models.ForeignKey(Mystore, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=50)
    price = models.PositiveIntegerField(default=1)
    description = models.CharField(max_length=100)
    image = models.ImageField(upload_to='productimages')

    def __str__(self):
        return self.name
    

class Wishlist(models.Model):
    name = models.ForeignKey(Product, on_delete=models.CASCADE, max_length=30)

class MyWishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mywishlist')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Ensure a user can't add the same product multiple times

RATING_CHOICES =(
("ONE", "1"),
("TWO", "2"),
("THREE", "3"),
("FOUR", "4"),
("FIVE", "5"),

)




class Cart(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_on = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s cart - {self.product.name}"

    def total_price(self):
        return self.product.price * self.quantity


STATUS_CHOICES = (
    ("processing", "Processing"),
    ("cancelled","Cancelled"),
    ("delivery", "Delivery"),
)    
class Orderdetails(models.Model):
    name = models.ForeignKey(Account, on_delete=models.DO_NOTHING, max_length=35)
    items = models.CharField(max_length=255, verbose_name="items")
    store_name = models.CharField(max_length=100)
    total_price = models.DecimalField(max_digits=20, decimal_places=3)
    location =models.CharField(max_length=100)
    date_ordered = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=35, default="Processing", choices=STATUS_CHOICES)
    

    

class Order(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    ORDER_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    buyer = models.ForeignKey(get_user_model(), related_name='orders_as_buyer', on_delete=models.CASCADE)
    seller = models.ForeignKey(get_user_model(), related_name='orders_as_seller', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount of the transaction
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def count_completed_orders_for_seller(cls, seller):
        """
        Counts completed orders for a specific seller.
        """
        return cls.objects.filter(seller=seller, status=cls.COMPLETED).count()
    @classmethod
    def count_pending_orders_for_seller(cls, seller):
        """
        Counts pending orders for a specific seller.
        """
        return cls.objects.filter(seller=seller, status=cls.PENDING).count()
    
    def initiate_payment(self):
        """
        Initiates the payment by deducting funds from the buyer's wallet and placing them in escrow.
        """
        buyer_wallet = self.buyer.wallet
        if buyer_wallet.balance >= self.amount:
            buyer_wallet.add_to_escrow(self.amount)  # Add funds to escrow
            return True
        else:
            raise ValueError("Insufficient balance to complete the order.")

    def complete_order(self):
        """
        Complete the order: Charge admin fee and transfer remaining amount to seller.
        """
        if self.status != self.PENDING:
            raise ValueError("Only pending orders can be completed.")

        admin_wallet= Adminwallet.objects.get(id=1)  # Ensure admin wallet exists
        escrow_fee = self.amount * Decimal("0.02")  # Calculate 2% fee
        seller_earnings = self.amount - escrow_fee

        # Ensure buyer wallet has enough escrow balance
        if self.buyer.wallet.escrow_balance < self.amount:
            raise ValueError("Insufficient escrow balance in buyer's wallet.")

        # Release funds from escrow
        self.buyer.wallet.release_from_escrow(self.amount)

        # Admin fee deposit
        admin_wallet.deposit(escrow_fee)

        # Transfer remaining funds to seller
        self.seller.wallet.deposit(seller_earnings)

        self.status = self.COMPLETED
        self.save()

    def cancel_order(self):
        """
        Cancels the order and refunds the buyer.
        """
        if timezone.now() - self.created_at > timedelta(hours=12):
            raise ValueError("Order cannot be cancelled after 12 hours.")
        
        if self.status == self.PENDING:
            self.status = self.CANCELLED
            self.save()
            buyer_wallet = self.buyer.wallet
            buyer_wallet.escrow_balance -= self.amount  # Refund escrowed amount
            buyer_wallet.balance += self.amount  # Return money to buyer's balance
            buyer_wallet.save()
            return True
        else:
            raise ValueError("Order cannot be cancelled. It might already be completed or cancelled.")
        
    def reject_delivery(self):
        """
        Reject the delivery and create a dispute.
        """
        if self.status != self.PENDING:
            raise ValueError("Only pending orders can be rejected.")
        # Create a dispute
        Dispute.objects.create(
            order=self,
            buyer_email=self.buyer.email,
            seller_email=self.seller.email,
            status=Dispute.OPEN,
        )
        # Keep funds in escrow
        self.save()
    
    def resolve_dispute(self, action):
        """
        Resolve the dispute by canceling or completing the order.
        `action` can be 'cancel' or 'complete'.
        """
        dispute = self.dispute
        if not dispute or dispute.status != Dispute.OPEN:
            raise ValueError("No open dispute to resolve.")
        if action == "cancel":
            # Refund the buyer
            self.buyer.wallet.deposit(self.amount)
            dispute.mark_resolved()
            self.status = self.CANCELLED
        elif action == "complete":
            # Release funds to seller and deduct admin fee
            seller_share = self.amount * Decimal(0.98)  # 2% fee
            admin_fee = self.amount * Decimal(0.02)
            self.seller.wallet.deposit(seller_share)
            Adminwallet.objects.get(id=1).deposit(admin_fee)
            dispute.mark_resolved()
            self.status = self.COMPLETED
        else:
            raise ValueError("Invalid action. Must be 'cancel' or 'complete'.")
        self.save()
    
    def __str__(self):
        return f"Order {self.id}: {self.buyer.username} -> {self.seller.username}, Status: {self.status}"
    

class Reviews(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.CharField(choices=RATING_CHOICES, default="1", max_length=6)
    description= models.CharField(max_length=200)

RATING_CHOICES =(
("ONE", "1"),
("TWO", "2"),
("THREE", "3"),
("FOUR", "4"),
("FIVE", "5"),

)

class MyReviews(models.Model):
    RATING_CHOICES =(
("ONE", "1"),
("TWO", "2"),
("THREE", "3"),
("FOUR", "4"),
("FIVE", "5"),

)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.CharField(choices=RATING_CHOICES, default="1", max_length=6)
    description= models.CharField(max_length=200)

class Dispute(models.Model):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    STATUS_CHOICES = [
        (OPEN, "Open"),
        (RESOLVED, "Resolved"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="dispute")
    buyer_email = models.EmailField()
    seller_email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def mark_resolved(self):
        """
        Mark the dispute as resolved.
        """
        self.status = self.RESOLVED
        self.resolved_at = timezone.now()
        self.save()
