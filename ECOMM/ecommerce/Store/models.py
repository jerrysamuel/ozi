from django.db import models
from User.models import Account

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


class Product(models.Model):
    store = models.ForeignKey(Mystore, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.PositiveIntegerField(default=1)
    description = models.CharField(max_length=100)
    image = models.ImageField(upload_to='productimages')

    def __str__(self):
        return self.name
    

class Wishlist(models.Model):
    name = models.OneToOneField(Product, on_delete=models.CASCADE, max_length=30)

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
        Completes the order, releases funds from escrow to the seller.
        """
        if self.status == self.PENDING:
            self.status = self.COMPLETED
            self.save()
            seller_wallet = self.seller.wallet
            seller_wallet.release_from_escrow(self.amount)
            seller_wallet.deposit(self.amount)  # Add funds to seller's main wallet
            return True
        else:
            raise ValueError("Order cannot be completed. It might already be completed or cancelled.")

    def cancel_order(self):
        """
        Cancels the order and refunds the buyer.
        """
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
    
    def __str__(self):
        return f"Order {self.id}: {self.buyer.username} -> {self.seller.username}, Status: {self.status}"
    

class Reviews(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    rating = models.CharField(choices=RATING_CHOICES, default="1", max_length=6)
    description= models.CharField(max_length=200)
