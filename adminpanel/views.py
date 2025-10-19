from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from core.models import (
    Product, Category, Customer, Order, OrderItem,
    AssociationRule
)

@staff_member_required
def admin_home(request):
    """Admin dashboard homepage"""
    # Key metrics
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()
    low_stock_count = Product.objects.filter(stock__lte=models.F('reorder_threshold')).count()
    
    # Recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    # Low stock alerts
    low_stock_products = Product.objects.filter(
        stock__lte=models.F('reorder_threshold')
    ).order_by('stock')[:10]
    
    context = {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'low_stock_count': low_stock_count,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products
    }
    
    return render(request, 'adminpanel/home.html', context)

@staff_member_required
def product_list(request):
    """List all products"""
    products = Product.objects.all().select_related('category')
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Search
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(sku__icontains=search)
        )
    
    context = {
        'products': products,
        'categories': Category.objects.all()
    }
    
    return render(request, 'adminpanel/product_list.html', context)

@staff_member_required
def product_create(request):
    """Create new product"""
    if request.method == 'POST':
        product = Product.objects.create(
            sku=request.POST.get('sku'),
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            category_id=request.POST.get('category'),
            subcategory=request.POST.get('subcategory', ''),
            price=request.POST.get('price'),
            rating=request.POST.get('rating', 0),
            stock=request.POST.get('stock', 0),
            reorder_threshold=request.POST.get('reorder_threshold', 10),
            image_url=request.POST.get('image_url', ''),
            is_active=request.POST.get('is_active') == 'on'
        )
        
        messages.success(request, f'Product {product.name} created successfully!')
        return redirect('adminpanel:product_list')
    
    context = {
        'categories': Category.objects.all()
    }
    
    return render(request, 'adminpanel/product_form.html', context)

@staff_member_required
def product_update(request, product_id):
    """Update existing product"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.sku = request.POST.get('sku')
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.category_id = request.POST.get('category')
        product.subcategory = request.POST.get('subcategory', '')
        product.price = request.POST.get('price')
        product.rating = request.POST.get('rating', 0)
        product.stock = request.POST.get('stock', 0)
        product.reorder_threshold = request.POST.get('reorder_threshold', 10)
        product.image_url = request.POST.get('image_url', '')
        product.is_active = request.POST.get('is_active') == 'on'
        product.save()
        
        messages.success(request, f'Product {product.name} updated successfully!')
        return redirect('adminpanel:product_list')
    
    context = {
        'product': product,
        'categories': Category.objects.all()
    }
    
    return render(request, 'adminpanel/product_form.html', context)

@staff_member_required
def product_delete(request, product_id):
    """Delete product"""
    product = get_object_or_404(Product, id=product_id)
    product_name = product.name
    product.delete()
    
    messages.success(request, f'Product {product_name} deleted successfully!')
    return redirect('adminpanel:product_list')

@staff_member_required
def inventory_dashboard(request):
    """Inventory management dashboard"""
    # Products needing reorder
    low_stock_products = Product.objects.filter(
        stock__lte=models.F('reorder_threshold')
    ).annotate(
        urgency_level=models.Case(
            models.When(stock=0, then=models.Value('critical')),
            models.When(stock__lte=models.F('reorder_threshold') / 2, then=models.Value('high')),
            default=models.Value('medium'),
            output_field=models.CharField()
        )
    ).order_by('stock')
    
    # Stock statistics
    total_stock_value = Product.objects.aggregate(
        total=Sum(models.F('stock') * models.F('price'))
    )['total'] or 0
    
    context = {
        'low_stock_products': low_stock_products,
        'total_stock_value': total_stock_value,
        'critical_count': low_stock_products.filter(stock=0).count(),
        'high_urgency_count': low_stock_products.filter(
            stock__gt=0,
            stock__lte=models.F('reorder_threshold') / 2
        ).count()
    }
    
    return render(request, 'adminpanel/inventory_dashboard.html', context)

@staff_member_required
def restock_product(request, product_id):
    """Quick restock action"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        restock_quantity = int(request.POST.get('quantity', 0))
        product.stock += restock_quantity
        product.save()
        
        messages.success(request, f'Restocked {product.name} with {restock_quantity} units')
        return redirect('adminpanel:inventory_dashboard')
    
    return render(request, 'adminpanel/restock_form.html', {'product': product})

@staff_member_required
def customer_list(request):
    """List all customers"""
    customers = Customer.objects.all().annotate(
        total_orders=Count('orders'),
        total_spent=Sum('orders__total_amount')
    )
    
    # Search
    search = request.GET.get('search')
    if search:
        customers = customers.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )
    
    context = {
        'customers': customers
    }
    
    return render(request, 'adminpanel/customer_list.html', context)

@staff_member_required
def customer_details(request, customer_id):
    """View customer details"""
    customer = get_object_or_404(Customer, id=customer_id)
    orders = customer.orders.all().order_by('-created_at')
    total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'customer': customer,
        'orders': orders,
        'total_spent': total_spent
    }
    
    return render(request, 'adminpanel/customer_details.html', context)

@staff_member_required
def customer_segmentation(request):
    """Customer segmentation dashboard"""
    # Segment by predicted category
    category_segments = Customer.objects.values('predicted_category').annotate(
        count=Count('id'),
        avg_spent=Avg('orders__total_amount')
    ).order_by('-count')
    
    # Segment by income range
    income_segments = Customer.objects.values('income_range').annotate(
        count=Count('id'),
        avg_spent=Avg('orders__total_amount')
    ).order_by('-count')
    
    # Segment by age groups
    age_segments = Customer.objects.filter(age__isnull=False).extra(
        select={'age_group': "CASE WHEN age < 25 THEN '18-24' WHEN age < 35 THEN '25-34' WHEN age < 45 THEN '35-44' WHEN age < 55 THEN '45-54' ELSE '55+' END"}
    ).values('age_group').annotate(
        count=Count('id'),
        avg_spent=Avg('orders__total_amount')
    )
    
    context = {
        'category_segments': category_segments,
        'income_segments': income_segments,
        'age_segments': age_segments,
        'total_customers': Customer.objects.count()
    }
    
    return render(request, 'adminpanel/customer_segmentation.html', context)

@staff_member_required
def recommendation_rules(request):
    """Manage association rules for recommendations"""
    rules = AssociationRule.objects.all().order_by('-confidence')
    
    # Filter by confidence threshold
    min_confidence = request.GET.get('min_confidence')
    if min_confidence:
        rules = rules.filter(confidence__gte=float(min_confidence))
    
    # Filter by active status
    status = request.GET.get('status')
    if status == 'active':
        rules = rules.filter(is_active=True)
    elif status == 'inactive':
        rules = rules.filter(is_active=False)
    
    context = {
        'rules': rules,
        'total_rules': AssociationRule.objects.count(),
        'active_rules': AssociationRule.objects.filter(is_active=True).count()
    }
    
    return render(request, 'adminpanel/recommendation_rules.html', context)

@staff_member_required
def toggle_rule(request, rule_id):
    """Enable/disable a recommendation rule"""
    rule = get_object_or_404(AssociationRule, id=rule_id)
    rule.is_active = not rule.is_active
    rule.save()
    
    status = 'enabled' if rule.is_active else 'disabled'
    messages.success(request, f'Rule {status} successfully!')
    
    return redirect('adminpanel:recommendation_rules')

@staff_member_required
def update_confidence_threshold(request):
    """Bulk update confidence threshold"""
    if request.method == 'POST':
        threshold = float(request.POST.get('threshold'))
        AssociationRule.objects.filter(confidence__lt=threshold).update(is_active=False)
        AssociationRule.objects.filter(confidence__gte=threshold).update(is_active=True)
        
        messages.success(request, f'Updated rules based on confidence threshold {threshold}')
        return redirect('adminpanel:recommendation_rules')
    
    return redirect('adminpanel:recommendation_rules')

@staff_member_required
def category_list(request):
    """List all categories"""
    categories = Category.objects.annotate(
        product_count=Count('products')
    )
    
    context = {
        'categories': categories
    }
    
    return render(request, 'adminpanel/category_list.html', context)

@staff_member_required
def category_create(request):
    """Create new category"""
    if request.method == 'POST':
        category = Category.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description', '')
        )
        
        messages.success(request, f'Category {category.name} created successfully!')
        return redirect('adminpanel:category_list')
    
    return render(request, 'adminpanel/category_form.html')

@staff_member_required
def order_list(request):
    """List all orders"""
    orders = Order.objects.all().select_related('customer').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES
    }
    
    return render(request, 'adminpanel/order_list.html', context)

@staff_member_required
def order_details(request, order_id):
    """View order details"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # Update order status
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        
        messages.success(request, f'Order status updated to {order.get_status_display()}')
        return redirect('adminpanel:order_details', order_id=order_id)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES
    }
    
    return render(request, 'adminpanel/order_details.html', context)