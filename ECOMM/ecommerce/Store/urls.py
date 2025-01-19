from django.urls import path
from . import views

urlpatterns = [
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:cart_item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("createstore/", views.createstore, name="createstore"),
    path("add_product/", views.add_product, name="add_product"),
    path('checkout/', views.checkout, name='checkout'),
    path('order_summary/', views.order_summary, name='order_summary'),
]