from django.db import models

class Mystore(models.Model):
    name = models.CharField(max_length=100)
    cac_name = models.CharField(max_length=100)
    physicaladdress = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)

    def verifications():
       pass


class Product(models.Model):
    store = models.OneToOneField(Mystore, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=15, decimal_places=3)
    description = models.CharField(max_length=100)
    image = models.ImageField(upload_to='productimages')

