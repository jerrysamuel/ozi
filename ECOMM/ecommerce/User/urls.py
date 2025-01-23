from django.urls import path
from . import views

urlpatterns = [
    
    path('user/signup/', views.SignUpView.as_view(), name='signup'),
    path('user/signin/', views.SignInView.as_view(), name='signin'),
    path('user/logout/', views.signout_view, name='logout'),
    path('user/sellerdashboard/', views.sellerdashboard, name='sellerdashboard'),
    path('user/buyerdashboard/', views.buyerdashboard, name='buyerdashboard'),
    path("deposit-to-wallet/", views.deposit_to_wallet, name="deposit_to_wallet"),
    path("verify-deposit/", views.verify_deposit, name="verify_deposit"),
    path('',views.index, name='index' ),
    path('user/adminwallet/', views.adminwallet, name='adminwallet'),
    path('search/', views.searchresult, name='search'),
    path('user/profile/', views.profile, name='profile'),
    path("products/", views.seller_products, name="seller_products"),
    path("store_orders/", views.store_orders, name="store_orders"),
    
]