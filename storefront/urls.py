from django.urls import path
from . import views

app_name = 'storefront'  # Enables namespaced URL lookups like storefront:home

urlpatterns = [
    path('', views.home_view, name='home'),  # Store homepage
    path('product/<int:id>/', views.product_detail, name='product_detail'),  # Product details
    path('cart/', views.cart_view, name='cart'),  # Shopping cart
    path('checkout/', views.checkout_view, name='checkout'),  # Checkout page
    path('register/', views.register_view, name='register'),  # User registration
]
