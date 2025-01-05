from django.urls import path
from . import views

urlpatterns = [
    
    path('user/signup/', views.SignUpView.as_view(), name='signup'),
    path('user/signin/', views.SignInView.as_view(), name='signin'),
    path('user/logout/', views.signout_view, name='logout'),
    path('user/sellerdashboard/', views.sellerdashboard, name='sellerdashboard'),
    path('user/buyerdashboard/', views.buyerdashboard, name='buyerdashboard'),
    path('index/',views.index, name='index' ),
]