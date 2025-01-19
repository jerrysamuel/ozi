from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model

#
class MyAccountManager(BaseUserManager):
	def create_user(self, email, username, password=None):
		if not email:
			raise ValueError("Users must have an email address")
		if not username:
			raise ValueError("Users must have an username")

		user  = self.model(
				email=self.normalize_email(email),
				username=username,
			)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, username, password):
		user  = self.create_user(
				email=self.normalize_email(email),
				password=password,
				username=username,
			)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user
      
ROLE_CHOICES = (
    ('seller'  , 'Seller'),
    ('buyer', 'Buyer'),
)

class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    role      = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    last_login	= models.DateTimeField(verbose_name='last login', auto_now=True)
    is_online = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    objects = MyAccountManager() 

    def __str__(self):
        return self.email
	
    def get_profile_image_filename(self):
        return str(self.profile_image)[str(self.profile_image).index('profile_images/' + str(self.pk) + "/"):]
    
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    
class Profile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=50)
    age = models.CharField(max_length=3)
    address = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, default='080')
    state = models.CharField(max_length=40)
    bio = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='profiles', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class Adminwallet(models.Model):
     balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # store balance as a decimal (e.g., 0.00)

     def __str__(self):
        return f"Admin Wallet with balance: {self.balance}"
     
     def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")
        self.balance += amount
        self.save()
     
    
class Wallet(models.Model):
    account = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # store balance as a decimal (e.g., 0.00)
    escrow_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # funds in escrow
    
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")
        if amount > self.balance:
            raise ValueError("Insufficient balance.")
        self.balance -= amount
        self.save()

    def add_to_escrow(self, amount):
        """
        Add funds to escrow balance.
        """
        if amount <= 0:
            raise ValueError("Escrow amount must be greater than zero.")
        self.balance -= amount
        self.escrow_balance += amount
        self.save()

    def release_from_escrow(self, amount):
        """
        Release funds from escrow balance to the seller.
        """
        if amount <= 0:
            raise ValueError("Release amount must be greater than zero.")
        if amount > self.escrow_balance:
            raise ValueError("Insufficient escrow balance.")
        else:
            self.escrow_balance -= amount
            self.save()

    def __str__(self):
        return f"Wallet for {self.account.email} with balance: {self.balance}, escrow: {self.escrow_balance}"


