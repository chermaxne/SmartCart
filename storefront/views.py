from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Customer, Category
from django.contrib import messages
from .forms import UserRegisterForm, CustomerForm
from decimal import Decimal
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
import logging

# Import the simplified predictions_code module
from predictions_code.predict_category import predict_customer_category
from predictions_code.predict_products import get_product_recommendations, get_product_recommendations_by_skus

logger = logging.getLogger(__name__)

# -------------------------
# Utility functions
# -------------------------
def _cart_dict(request):
    return request.session.setdefault('cart', {})  # keys: str(product_id) -> int(quantity)

def cart_count(request):
    """
    Context processor to add cart count to all templates
    """
    cart = request.session.get('cart', {})
    total_items = sum(int(qty) for qty in cart.values())
    return {
        'cart_count': total_items
    }

def _compute_totals(cart):
    subtotal = Decimal('0.00')
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(id=int(pid))
            subtotal += p.price * int(qty)
        except Product.DoesNotExist:
            continue
    shipping = Decimal('9.99') if subtotal > 0 else Decimal('0.00')
    tax = (subtotal * Decimal('0.08')).quantize(Decimal('0.01'))
    total = (subtotal + shipping + tax).quantize(Decimal('0.01'))
    return subtotal, shipping, tax, total

def buy_now(request, product_id):
    """Add to cart and go directly to checkout"""
    cart = _cart_dict(request)
    qty = int(request.POST.get('quantity', 1))
    
    try:
        product = Product.objects.get(id=product_id)
        cart[str(product_id)] = cart.get(str(product_id), 0) + qty
        request.session.modified = True
        messages.success(request, f'Added {product.name} to cart')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
        return redirect('storefront:home')
    
    return redirect('storefront:checkout')

# -------------------------
# Home and Product Views
# -------------------------
def home_view(request):
    """
    Home page with personalized recommendations using new predictions_code module
    """
    products = Product.objects.filter(is_active=True).order_by('-rating')
    
    recommended_products = None
    predicted_category = None
    
    if request.user.is_authenticated:
        try:
            # Predict customer's preferred category
            predicted_category = predict_customer_category(request.user)
            
            # Get products from predicted category
            if predicted_category:
                try:
                    category = Category.objects.get(name__icontains=predicted_category)
                    recommended_products = Product.objects.filter(
                        category=category,
                        is_active=True
                    ).order_by('-rating')
                except Category.DoesNotExist:
                    recommended_products = Product.objects.filter(
                        is_active=True
                    ).order_by('-rating')
                except Category.MultipleObjectsReturned:
                    category = Category.objects.filter(name__icontains=predicted_category).first()
                    recommended_products = Product.objects.filter(
                        category=category,
                        is_active=True
                    ).order_by('-rating')
        except Exception as e:
            logger.error(f"Recommendation error in home_view: {e}", exc_info=True)
            recommended_products = Product.objects.filter(is_active=True).order_by('-rating')
    else:
        recommended_products = Product.objects.filter(is_active=True).order_by('-rating')
    
    return render(request, 'storefront/home.html', {
        'products': products,
        'recommended_products': recommended_products,
        'predicted_category': predicted_category,
    })

def product_detail(request, id):
    """
    Product detail page with ML-powered "Frequently Bought Together" recommendations
    """
    product = get_object_or_404(Product, id=id)
    
    # Get recommendations using the new predictions_code module
    related_products = []
    try:
        # Use association rules to find frequently bought together products
        recommended_skus = get_product_recommendations_by_skus([product.sku], top_n=4)
        
        if recommended_skus:
            related_products = Product.objects.filter(
                sku__in=recommended_skus,
                is_active=True
            )[:4]
    except Exception as e:
        logger.error(f"Recommendation error in product_detail: {e}", exc_info=True)
        # Fallback: same category products
        related_products = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id).order_by('-rating')[:4]
    
    return render(request, 'storefront/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })

# -------------------------
# Cart Views
# -------------------------
@require_POST
def cart_add(request, product_id):
    """Add product to cart and redirect to cart page"""
    cart = _cart_dict(request)
    qty = int(request.POST.get('quantity', 1))
    
    try:
        product = Product.objects.get(id=product_id)
        
        # Check if item already exists
        old_qty = cart.get(str(product_id), 0)
        cart[str(product_id)] = old_qty + qty
        request.session.modified = True
        
        if old_qty > 0:
            messages.success(request, f'Updated {product.name} quantity to {cart[str(product_id)]}')
        else:
            messages.success(request, f'✓ Added {product.name} to cart')
            
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
    
    return redirect('storefront:cart')

@require_POST
def cart_update(request, product_id):
    """Update quantity of item in cart"""
    cart = _cart_dict(request)
    
    try:
        qty = int(request.POST.get('quantity', 0))
        product = Product.objects.get(id=product_id)
        
        if qty <= 0:
            cart.pop(str(product_id), None)
            messages.success(request, f'Removed {product.name} from cart')
        else:
            cart[str(product_id)] = qty
            messages.success(request, f'Updated {product.name} quantity to {qty}')
        
        request.session.modified = True
        
    except (TypeError, ValueError):
        messages.error(request, 'Invalid quantity')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
    
    return redirect('storefront:cart')

@require_POST
def cart_remove(request, product_id):
    """Remove item from cart"""
    cart = _cart_dict(request)
    
    try:
        product = Product.objects.get(id=product_id)
        cart.pop(str(product_id), None)
        request.session.modified = True
        messages.success(request, f'Removed {product.name} from cart')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
    
    return redirect('storefront:cart')

def cart_view(request):
    """
    Display cart page with ML-powered recommendations using predictions_code
    """
    cart = _cart_dict(request)
    order_items = []
    subtotal = Decimal('0.00')
    cart_skus = []

    for pid, qty in cart.items():
        try:
            p = Product.objects.get(id=int(pid))
        except Product.DoesNotExist:
            continue
        total_price = (p.price * int(qty)).quantize(Decimal('0.01'))
        subtotal += total_price
        order_items.append({
            'id': p.id,
            'product': p,
            'quantity': int(qty),
            'total_price': total_price
        })
        cart_skus.append(p.sku)

    shipping = Decimal('9.99') if subtotal > 0 else Decimal('0.00')
    tax = (subtotal * Decimal('0.08')).quantize(Decimal('0.01'))
    total = (subtotal + shipping + tax).quantize(Decimal('0.01'))

    discount = Decimal('0.00')
    if request.session.get('promo_code') == 'SAVE10':
        discount = (subtotal * Decimal('0.1')).quantize(Decimal('0.01'))
        total -= discount

    # ML Integration: Get smart recommendations based on cart
    recommended_products = []
    if cart_skus:
        try:
            if request.user.is_authenticated:
                # Use hybrid recommendation system (cart + customer profile)
                recommended_skus = get_product_recommendations(cart_skus, request.user, top_n=6)
            else:
                # For non-authenticated users, use association rules only
                recommended_skus = get_product_recommendations_by_skus(cart_skus, top_n=6)
            
            if recommended_skus:
                recommended_products = list(Product.objects.filter(
                    sku__in=recommended_skus,
                    is_active=True
                )[:6])
        except Exception as e:
            logger.error(f"Cart recommendations error: {e}", exc_info=True)

    return render(request, 'storefront/cart.html', {
        'order_items': order_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'discount': discount,
        'recommended_products': recommended_products,
    })

@require_POST
def cart_apply_promo(request):
    """Apply promo code"""
    promo_code = request.POST.get('promo_code', '').strip().upper()
    request.session['promo_code'] = None
    
    if promo_code == 'SAVE10':
        request.session['promo_code'] = 'SAVE10'
        messages.success(request, '🎉 Promo code applied! 10% off')
    elif promo_code:
        messages.error(request, 'Invalid promo code')
    else:
        messages.error(request, 'Please enter a promo code')
    
    return redirect('storefront:cart')

# -------------------------
# Checkout
# -------------------------
def checkout(request):
    """
    Checkout page with ML-powered product recommendations
    """
    cart = _cart_dict(request)
    order_items = []
    subtotal = Decimal('0.00')
    cart_skus = []
    
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(id=int(pid))
            total_price = (p.price * int(qty)).quantize(Decimal('0.01'))
            subtotal += total_price
            order_items.append({'product': p, 'quantity': qty, 'total_price': total_price})
            cart_skus.append(p.sku)
        except Product.DoesNotExist:
            continue

    if not order_items:
        messages.warning(request, 'Your cart is empty')
        return redirect('storefront:cart')

    shipping = Decimal('9.99') if subtotal > 0 else Decimal('0.00')
    tax = (subtotal * Decimal('0.08')).quantize(Decimal('0.01'))
    discount = Decimal('0.00')
    if request.session.get('promo_code') == 'SAVE10':
        discount = (subtotal * Decimal('0.1')).quantize(Decimal('0.01'))

    total = (subtotal + shipping + tax - discount).quantize(Decimal('0.01'))

    # ML Integration: Get personalized recommendations for checkout page
    checkout_recommendations = []
    if cart_skus:
        try:
            if request.user.is_authenticated:
                # Use hybrid recommendation system
                recommended_skus = get_product_recommendations(cart_skus, request.user, top_n=4)
            else:
                # Use association rules only
                recommended_skus = get_product_recommendations_by_skus(cart_skus, top_n=4)
            
            print(f"DEBUG CHECKOUT: cart_skus={cart_skus}, recommended_skus={recommended_skus}")
            
            if recommended_skus:
                checkout_recommendations = list(Product.objects.filter(
                    sku__in=recommended_skus,
                    is_active=True
                )[:4])
                print(f"DEBUG CHECKOUT: Found {len(checkout_recommendations)} products")
            else:
                print("DEBUG CHECKOUT: No recommended SKUs returned")
        except Exception as e:
            logger.error(f"Checkout recommendations error: {e}", exc_info=True)
            print(f"DEBUG CHECKOUT: Exception - {e}")
    else:
        print(f"DEBUG CHECKOUT: No cart_skus (cart_skus={cart_skus})")

    if request.method == "POST":
        # Process order
        messages.success(request, "🎉 Order placed successfully! Thank you for shopping with us.")
        request.session['cart'] = {}  # clear cart
        request.session['promo_code'] = None  # clear promo
        return redirect("storefront:home")

    return render(request, "storefront/checkout.html", {
        "cart_items": order_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "tax": tax,
        "discount": discount,
        "total": total,
        "recommended_products": checkout_recommendations,  # Fixed: was checkout_recommendations
    })

# -------------------------
# Auth & Customer
# -------------------------
def register(request):
    """
    User registration with ML-powered category prediction
    """
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        customer_form = CustomerForm(request.POST)
        
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password1'])

            # Copy customer form fields
            for field, value in customer_form.cleaned_data.items():
                if hasattr(user, field):
                    try:
                        setattr(user, field, value)
                    except Exception:
                        pass

            user.save()

            # ML Integration: Predict preferred category using new predictions_code
            try:
                predicted_category = predict_customer_category(user)

                # Save predicted category to customer profile
                try:
                    category = Category.objects.get(name__icontains=predicted_category)
                    user.preferred_category = category
                    user.save()

                    messages.success(
                        request,
                        f"🎉 Welcome to AuroraMart! Based on your profile, you might love our {predicted_category} products."
                    )
                except Category.DoesNotExist:
                    messages.success(request, "🎉 Account created successfully! Welcome to AuroraMart!")

            except Exception as e:
                logger.error(f"Category prediction error during registration: {e}", exc_info=True)
                messages.success(request, "🎉 Account created successfully! Welcome to AuroraMart!")

            # Auto-login
            auth_login(request, user)
            return redirect('storefront:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserRegisterForm()
        customer_form = CustomerForm()

    return render(request, 'storefront/register.html', {
        'user_form': user_form,
        'customer_form': customer_form,
    })

def login(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('rememberMe') == 'on'

        if not username or not password:
            if not username:
                messages.error(request, "Username or email is required")
            if not password:
                messages.error(request, "Password is required")
            return render(request, 'storefront/login.html', {'username': username})

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            request.session.set_expiry(60*60*24*30 if remember_me else 0)
            messages.success(request, f"👋 Welcome back, {user.username}!")
            return redirect('storefront:home')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return render(request, 'storefront/login.html', {'username': username})

    return render(request, 'storefront/login.html')

def logout_view(request):
    """
    Logout view
    """
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('storefront:home')
