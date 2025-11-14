from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Avg, Sum, Q
from storefront.models import Category, Product

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def category_list(request):
    """Display all categories with statistics"""
    categories = Category.objects.annotate(
        product_count=Count('product', filter=Q(product__is_active=True)),
        total_stock=Sum('product__stock', filter=Q(product__is_active=True)),
        avg_price=Avg('product__price', filter=Q(product__is_active=True)),
        avg_rating=Avg('product__rating', filter=Q(product__is_active=True))
    ).order_by('name')
    
    context = {
        'categories': categories,
    }
    return render(request, 'adminpanel/category/category_list.html', context)

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def category_detail(request, pk):
    """Display category details and associated products"""
    category = get_object_or_404(Category, pk=pk)
    products = Product.objects.filter(category=category, is_active=True).order_by('name')
    
    # Calculate statistics
    total_products = products.count()
    total_stock = products.aggregate(Sum('stock'))['stock__sum'] or 0
    avg_price = products.aggregate(Avg('price'))['price__avg'] or 0
    avg_rating = products.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Count low stock products (products where stock is below reorder threshold)
    low_stock_count = 0
    for p in products:
        if p.stock < p.reorder_threshold:
            low_stock_count += 1
    
    context = {
        'category': category,
        'products': products,
        'total_products': total_products,
        'total_stock': total_stock,
        'avg_price': avg_price,
        'avg_rating': avg_rating,
        'low_stock_count': low_stock_count,
    }
    return render(request, 'adminpanel/category/category_detail.html', context)

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def category_add(request):
    """Add a new category"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, 'Category name is required.')
            return redirect('adminpanel:category_add')
        
        # Check if category already exists
        if Category.objects.filter(name__iexact=name).exists():
            messages.error(request, f'Category "{name}" already exists.')
            return redirect('adminpanel:category_add')
        
        Category.objects.create(name=name, description=description)
        messages.success(request, f'Category "{name}" added successfully!')
        return redirect('adminpanel:category_list')
    
    return render(request, 'adminpanel/category/category_form.html', {'action': 'Add'})

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def category_edit(request, pk):
    """Edit an existing category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, 'Category name is required.')
            return redirect('adminpanel:category_edit', pk=pk)
        
        # Check if another category with this name exists
        if Category.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, f'Another category with name "{name}" already exists.')
            return redirect('adminpanel:category_edit', pk=pk)
        
        category.name = name
        category.description = description
        category.save()
        
        messages.success(request, f'Category "{name}" updated successfully!')
        return redirect('adminpanel:category_list')
    
    context = {
        'category': category,
        'action': 'Edit'
    }
    return render(request, 'adminpanel/category/category_form.html', context)

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def category_delete(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, pk=pk)
    
    # Check if category has active products
    product_count = Product.objects.filter(category=category, is_active=True).count()
    
    if product_count > 0:
        messages.error(request, f'Cannot delete category "{category.name}" - it has {product_count} active product(s). Please reassign or remove the products first.')
        return redirect('adminpanel:category_list')
    
    category_name = category.name
    category.delete()
    messages.success(request, f'Category "{category_name}" deleted successfully!')
    return redirect('adminpanel:category_list')
