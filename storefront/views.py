from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from decimal import Decimal
import joblib
import json
from core.models import (
    Customer, Product, Category, Cart, CartItem, 
    Order, OrderItem, Review, BrowsingHistory, AssociationRule
)

# Load ML models (adjust paths as needed)
try:
    decision_tree_model = joblib.load('ml_models/decision_tree_model.joblib')
except:
    decision_tree_model = None

try:
    association_rules = joblib.load('ml_models/association_rules.joblib')
except:
    association_rules = None

def home(request):
    """Homepage with personalized recommendations"""
    context = {
        'categories': Category.objects.all(),
        'trending_products': Product.objects.filter(is_active=True).order_by('-rating')[:8]
    }
    
    if request.user.is_authenticated:
        # Get predicted category products
        if request.user.predicted_category:
            category = Category.objects.filter(name=request.user.predicted_category).first()
            if category:
                context['recommended_products'] = category.products.filter(is_active=True)[:8]
        
        # Recently viewed products
        recent_views = BrowsingHistory.objects.filter(customer=request.user).select_related('product')[:8]
        context['recently_viewed'] = [view.product for view in recent_views]
    
    return render(request, 'storefront/home.html', context)

def register(request):
    """Customer registration with ML prediction"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        employment = request.POST.get('employment')
        income_range = request.POST.get('income_range')
        
        # Create customer
        customer = Customer.objects.create_user(
            username=username,
            email=email,
            password=password,
            age=age,
            gender=gender,
            employment=employment,
            income_range=income_range
        )
        
        # Predict preferred category using decision tree
        if decision_tree_model:
            try:
                features = [[int(age), gender, employment, income_range]]
                predicted_category = decision_tree_model.predict(features)[0]
                customer.predicted_category = predicted_category
                customer.save()
            except:
                pass
        
        # Create cart for customer
        Cart.objects.create(customer=customer)
        
        login(request, customer)
        messages.success(request, 'Registration successful!')
        return redirect('storefront:home')
    
    return render(request, 'storefront/register.html')

def user_login(request):
    """Customer login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('storefront:home')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'storefront/login.html')

def user_logout(request):
    """Customer logout"""
    logout(request)
    return redirect('storefront:home')

@login_required
def profile(request):
    """View and update customer profile"""
    if request.method == 'POST':
        request.user.email = request.POST.get('email')
        request.user.age = request.POST.get('age')
        request.user.gender = request.POST.get('gender')
        request.user.employment = request.POST.get('employment')
        request.user.income_range = request.POST.get('income_range')
        
        # Re-predict category if demographics changed
        if decision_tree_model:
            try:
                features = [[
                    int(request.user.age),
                    request.user.gender,
                    request.user.employment,
                    request.user.income_range
                ]]
                predicted_category = decision_tree_model.predict(features)[0]
                request.user.predicted_category = predicted_category
            except:
                pass
        
        request.user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('storefront:profile')
    
    return render(request, 'storefront/profile.html')

def products(request):
    """Product listing with filtering and sorting"""
    products_list = Product.objects.filter(is_active=True)
    
    # Filtering
    category_id = request.GET.get('category')
    if category_id:
        products_list = products_list.filter(category_id=category_id)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products_list = products_list.filter(price__gte=min_price)
    if max_price:
        products_list = products_list.filter(price__lte=max_price)
    
    min_rating = request.GET.get('min_rating')
    if min_rating:
        products_list = products_list.filter(rating__gte=min_rating)
    
    in_stock = request.GET.get('in_stock')
    if in_stock == 'true':
        products_list = products_list.filter(stock__gt=0)
    
    search = request.GET.get('search')
    if search:
        products_list = products_list.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_desc':
        products_list = products_list.order_by('-price')
    elif sort_by == 'rating':
        products_list = products_list.order_by('-rating')
    elif sort_by == 'newest':
        products_list = products_list.order_by('-created_at')
    
    context = {
        'products': products_list,
        'categories': Category.objects.all(),
        'selected_category': category_id,
        'sort_by': sort_by
    }
    
    return render(request, 'storefront/products.html', context)

def product_details(request, product_id):
    """Product details page with recommendations"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Track browsing history
    if request.user.is_authenticated:
        BrowsingHistory.objects.create(customer=request.user, product=product)
    
    # Get reviews
    reviews = product.reviews.all().order_by('-created_at')
    
    # Get "Frequently bought together" using association rules
    recommended_products = []
    if association_rules is not None:
        try:
            # Filter rules where product SKU is in antecedent
            matching_rules = AssociationRule.objects.filter(
                antecedent__contains=product.sku,
                is_active=True
            ).order_by('-confidence')[:4]
            
            for rule in matching_rules:
                consequent_sku = rule.consequent
                rec_product = Product.objects.filter(sku=consequent_sku, is_active=True).first()
                if rec_product:
                    recommended_products.append(rec_product)
        except:
            pass
    
    context = {
        'product': product,
        'reviews': reviews,
        'recommended_products': recommended_products[:4]
    }
    
    return render(request, 'storefront/product_details.html', context)

@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    # Get or create cart
    cart, _ = Cart.objects.get_or_create(customer=request.user)
    
    # Check stock
    if product.stock < quantity:
        messages.error(request, 'Not enough stock available')
        return redirect('storefront:product_details', product_id=product_id)
    
    # Add or update cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart')
    return redirect('storefront:cart')

@login_required
def cart(request):
    """View shopping cart with smart suggestions"""
    cart, _ = Cart.objects.get_or_create(customer=request.user)
    cart_items = cart.items.all().select_related('product')
    
    # Get smart suggestions based on cart contents
    suggestions = []
    if association_rules is not None and cart_items.exists():
        try:
            cart_skus = [item.product.sku for item in cart_items]
            
            # Find rules matching cart combination
            for rule in AssociationRule.objects.filter(is_active=True).order_by('-confidence')[:10]:
                antecedent_skus = rule.antecedent.split(',')
                if any(sku in cart_skus for sku in antecedent_skus):
                    suggested_product = Product.objects.filter(
                        sku=rule.consequent,
                        is_active=True
                    ).exclude(sku__in=cart_skus).first()
                    
                    if suggested_product and suggested_product not in [s['product'] for s in suggestions]:
                        suggestions.append({
                            'product': suggested_product,
                            'confidence': float(rule.confidence)
                        })
                        
                    if len(suggestions) >= 4:
                        break
        except:
            pass
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'suggestions': suggestions,
        'total': cart.total_amount
    }
    
    return render(request, 'storefront/cart.html', context)

@login_required
def update_cart(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    action = request.POST.get('action')
    
    if action == 'increase':
        if cart_item.product.stock > cart_item.quantity:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.error(request, 'Not enough stock')
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    elif action == 'remove':
        cart_item.delete()
    
    return redirect('storefront:cart')

@login_required
def checkout(request):
    """Checkout process"""
    cart = get_object_or_404(Cart, customer=request.user)
    cart_items = cart.items.all()
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('storefront:cart')
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        promo_code = request.POST.get('promo_code', '')
        
        # Create order
        import uuid
        order = Order.objects.create(
            customer=request.user,
            order_number=f'ORD-{uuid.uuid4().hex[:8].upper()}',
            total_amount=cart.total_amount,
            shipping_address=shipping_address,
            promo_code=promo_code
        )
        
        # Create order items and update stock
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                subtotal=cart_item.subtotal
            )
            
            # Update stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
        
        # Clear cart
        cart_items.delete()
        
        messages.success(request, 'Order placed successfully!')
        return redirect('storefront:order_success', order_id=order.id)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': cart.total_amount
    }
    
    return render(request, 'storefront/checkout.html', context)

@login_required
def order_success(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'storefront/order_success.html', {'order': order})

@login_required
def orders(request):
    """Order history"""
    orders_list = Order.objects.filter(customer=request.user).prefetch_related('items')
    
    context = {
        'orders': orders_list
    }
    
    return render(request, 'storefront/orders.html', context)