from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q, Count
from storefront.models import Product, Customer, Category

@login_required(login_url='adminpanel:login')
def dashboard(request):
    # Statistics
    total_products = Product.objects.filter(is_active=True).count()
    low_stock_count = Product.objects.filter(
        is_active=True,
        stock__lte=F('reorder_threshold')
    ).count()
    total_customers = Customer.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    
    # Recent low stock products
    low_stock_products = Product.objects.filter(
        is_active=True,
        stock__lte=F('reorder_threshold')
    ).select_related('category').order_by('stock')[:5]
    
    # Category distribution
    category_stats = Category.objects.annotate(
        product_count=Count('product', filter=Q(product__is_active=True))
    ).order_by('-product_count')[:5]
    
    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_customers': total_customers,
        'total_categories': total_categories,
        'low_stock_products': low_stock_products,
        'category_stats': category_stats,
    }
    
    return render(request, 'adminpanel/dashboard.html', context)