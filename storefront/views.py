from django.shortcuts import render, get_object_or_404
from .models import Product, Customer  # adjust based on your actual models

# Home page
def home_view(request):
    products = Product.objects.all()
    return render(request, 'storefront/home.html', {'products': products})

# Product detail page
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'storefront/product_detail.html', {'product': product})

# Cart
def cart_view(request):
    return render(request, 'storefront/cart.html')
# Checkout page
def checkout_view(request):
    return render(request, 'storefront/checkout.html')

# Optional: Customer profile (if needed)
def customer_profile(request, id):
    customer = get_object_or_404(Customer, id=id)
    return render(request, 'storefront/customer_profile.html', {'customer': customer})

def register_view(request):
    return render(request, 'storefront/register.html')