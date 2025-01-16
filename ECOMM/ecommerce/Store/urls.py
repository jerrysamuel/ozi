from django.urls import path
from . import views

urlpatterns = [
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:cart_item_id>/", views.remove_from_cart, name="remove_from_cart"),
    # path('checkout/', views.checkout, name='checkout'),
]