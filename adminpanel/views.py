from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from storefront.models import Product, Customer, Recommendation
from .forms import ProductForm, RecommendationForm

# Dashboard view (Inventory alerts)
@staff_member_required
def dashboard_view(request):
    low_stock_products = Product.objects.filter(stock__lte=5)  # Example threshold
    return render(request, "adminpanel/dashboard.html", {
        'low_stock_products': low_stock_products
    })

# Product CRUD
@staff_member_required
def product_list(request):
    products = Product.objects.all()
    return render(request, "adminpanel/product_list.html", {'products': products})

@staff_member_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('adminpanel/product_list')
    else:
        form = ProductForm()
    return render(request, "adminpanel/product_form.html", {'form': form})

@staff_member_required
def product_edit(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('adminpanel:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, "adminpanel:product_form.html", {'form': form})

# Customer management
@staff_member_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "adminpanel/customer_list.html", {'customers': customers})

# Recommendation review
@staff_member_required
def recommendation_list(request):
    recommendations = Recommendation.objects.all()
    return render(request, "adminpanel/recommendation_list.html", {'recommendations': recommendations})
