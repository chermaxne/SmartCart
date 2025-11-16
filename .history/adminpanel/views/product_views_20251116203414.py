from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.views.decorators.http import require_POST
from storefront.models import Product, Category
from adminpanel.forms import ProductForm

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)
    
    sort_by = request.GET.get('sort', '-created_at')
    products = products.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'sort_by': sort_by,
    }
    
    return render(request, 'adminpanel/product/product_list.html', context)

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Stock history not available in storefront model
    stock_history = []
    
    context = {
        'product': product,
        'stock_history': stock_history,
    }
    
    return render(request, 'adminpanel/product/product_detail.html', context)

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def low_stock(request):
    products = Product.objects.filter(
        is_active=True,
        stock__lte=F('reorder_threshold')
    ).select_related('category')
    
    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Sort
    sort_by = request.GET.get('sort', 'stock')
    products = products.order_by(sort_by)
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'sort_by': sort_by,
    }
    return render(request, 'adminpanel/product/low_stock.html', context)

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" has been added successfully!')
            return redirect('adminpanel:product_detail', pk=product.pk)
    else:
        form = ProductForm()
    
    context = {'form': form, 'is_edit': False}
    return render(request, 'adminpanel/product/product_form.html', context)

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" has been updated successfully!')
            return redirect('adminpanel:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    
    context = {'form': form, 'is_edit': True, 'product': product}
    return render(request, 'adminpanel/product/product_form.html', context)

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
@require_POST
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product_name = product.name
    
    # Instead of deleting, mark as inactive (soft delete)
    # This preserves data for AI model and order history
    product.is_active = False
    product.save()
    
    messages.success(request, f'Product "{product_name}" has been deactivated.')
    return redirect('adminpanel:product_list')
