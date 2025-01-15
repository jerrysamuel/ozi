from django.db import models
from User.models import Account


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
    store = models.OneToOneField(Mystore, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=15, decimal_places=3)
    description = models.CharField(max_length=100)
    image = models.ImageField(upload_to='productimages')

    def __str__(self):
        return self.name

class Order(models.Model):
    name = models.ForeignKey(Account, on_delete=models.CASCADE, max_length=25)
    product_name = models.ForeignKey(Product, on_delete=models.CASCADE, max_length=35)
    store = models.ForeignKey(Mystore, models.CASCADE, max_length=35)
    quantity = models.DecimalField(decimal_places=1, max_digits=11)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "order of "+ (self.product_name.name) + " by " +(self.name.username)

class Wishlist(models.Model):
    name = models.OneToOneField(Product, on_delete=models.CASCADE, max_length=30)

RATING_CHOICES =(
("ONE", "1"),
("TWO", "2"),
("THREE", "3"),
("FOUR", "4"),
("FIVE", "5"),

)


class Reviews(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    rating = models.CharField(choices=RATING_CHOICES, default="1", max_length=6)
    description= models.CharField(max_length=200)

class Cart(models.Model):
    product_details = models.ForeignKey(Product, on_delete=models.CASCADE)


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
    

    

