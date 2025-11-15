from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Customer, Category, Favorite, Order, OrderItem
from django.contrib import messages
from .forms import UserRegisterForm, CustomerForm, UserProfileForm, CustomPasswordChangeForm
from decimal import Decimal
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
import logging

# Import the simplified predictions_code module
from predictions_code.predict_category import predict_customer_category
<<<<<<< Updated upstream
from predictions_code.predict_products import (
    get_product_recommendations, 
    get_product_recommendations_by_skus,
    get_frequently_bought_together,
    get_complete_the_set
)
=======
from predictions_code.predict_products import get_product_recommendations, get_product_recommendations_by_skus, get_frequently_bought_together, get_complete_the_set
>>>>>>> Stashed changes

logger = logging.getLogger(__name__)

# -------------------------
# Utility functions
# -------------------------
def _cart_dict(request):
    return request.session.setdefault('cart', {})  # keys: str(product_id) -> int(quantity)

def _get_next_best_category(request):
    """
    Determine the "Next Best Action" category for the user to explore
    Only shows once per session - returns None after user has seen it
    Returns a category object or None
    """
    # Check if user has already seen the next best action
    if request.session.get('next_best_action_shown', False):
        return None
    
    if not request.user.is_authenticated:
        # For anonymous users, suggest the most popular category
        from django.db.models import Count
        popular_category = Category.objects.annotate(
            product_count=Count('product', filter=Q(product__is_active=True))
        ).filter(product_count__gt=0).order_by('-product_count').first()
        return popular_category
    
    user = request.user
    
    # Strategy 1: If user has a preferred category, suggest a DIFFERENT complementary category
    # Don't suggest the same category they're already seeing in "Recommended For You"
    if hasattr(user, 'preferred_category') and user.preferred_category:
        from django.db.models import Count
        
        # Get a different category (not their preferred one)
        complementary_category = Category.objects.exclude(
            id=user.preferred_category.id
        ).annotate(
            product_count=Count('product', filter=Q(product__is_active=True))
        ).filter(product_count__gt=0).order_by('-product_count').first()
        
        if complementary_category:
            return complementary_category
    
    # Strategy 2: Use ML to predict best category based on user demographics
    try:
        predicted_category_name = predict_customer_category(user)
        if predicted_category_name:
            predicted_category = Category.objects.filter(
                name__icontains=predicted_category_name
            ).first()
            
            if predicted_category:
                return predicted_category
    except Exception as e:
        logger.warning(f"Category prediction failed: {e}")
    
    # Strategy 3: Fallback - suggest most popular category
    from django.db.models import Count
    fallback_category = Category.objects.annotate(
        product_count=Count('product', filter=Q(product__is_active=True))
    ).filter(product_count__gt=0).order_by('-product_count').first()
    
    return fallback_category

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

def _get_next_best_category(request):
    """
    Get next best category to recommend for exploration
    Shows once per session and suggests a complementary category
    
    Returns:
        Category object or None
    """
    # Check if already shown in this session
    if request.session.get('next_best_action_shown'):
        return None
    
    # For authenticated users with preferred category
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(username=request.user.username)
            preferred_category_name = customer.preferred_category
            
            if preferred_category_name:
                # Get all categories except the preferred one
                other_categories = Category.objects.exclude(
                    name__iexact=preferred_category_name
                ).annotate(
                    product_count=Count('product')
                ).filter(product_count__gt=0)
                
                # Return the most popular complementary category
                if other_categories.exists():
                    return other_categories.order_by('-product_count').first()
        except Customer.DoesNotExist:
            pass
    
    # For non-authenticated or users without preferred category
    # Suggest most popular category
    from django.db.models import Count
    popular_category = Category.objects.annotate(
        product_count=Count('product')
    ).filter(product_count__gt=0).order_by('-product_count').first()
    
    return popular_category


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
def shop_view(request):
    """
    Shop page with all products, sorting and filtering
    """
    from django.db.models import Q
    
    # Get all categories for the filter
    all_categories = Category.objects.all().order_by('name')
    
    # Start with active products
    products = Product.objects.filter(is_active=True)
    
    # Category filter
    category_filter = request.GET.get('category', '').strip()
    if category_filter:
        products = products.filter(category__id=category_filter)
        
        # Mark next best action as shown if user clicked on it
        if request.GET.get('from_nba'):
            request.session['next_best_action_shown'] = True
            request.session.modified = True
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Sorting
    sort_option = request.GET.get('sort', '')
    if sort_option == 'name-asc':
        products = products.order_by('name')
    elif sort_option == 'name-desc':
        products = products.order_by('-name')
    elif sort_option == 'price-asc':
        products = products.order_by('price')
    elif sort_option == 'price-desc':
        products = products.order_by('-price')
    elif sort_option == 'rating-desc':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-created_at')  # Default sort by newest
    
    # Get next best category to explore (only shown once)
    next_best_category = _get_next_best_category(request)
    
    return render(request, 'storefront/shop.html', {
        'products': products,
        'search_query': search_query,
        'sort_option': sort_option,
        'all_categories': all_categories,
        'category_filter': category_filter,
        'next_best_category': next_best_category,
    })

def home_view(request):
    """
    Home page with personalized recommendations using new predictions_code module
    """
    from django.db.models import Q
    
    # Mark next best action as shown if user clicked through
    if request.GET.get('from_nba'):
        request.session['next_best_action_shown'] = True
    
    # Get all categories for the filter
    all_categories = Category.objects.all().order_by('name')
    
    # Start with active products
    products = Product.objects.filter(is_active=True)
    
    # Category filter
    category_filter = request.GET.get('category', '').strip()
    if category_filter:
        products = products.filter(category__id=category_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Sorting
    sort_option = request.GET.get('sort', '')
    if sort_option == 'name-asc':
        products = products.order_by('name')
    elif sort_option == 'name-desc':
        products = products.order_by('-name')
    elif sort_option == 'price-asc':
        products = products.order_by('price')
    elif sort_option == 'price-desc':
        products = products.order_by('-price')
    elif sort_option == 'rating-desc':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-rating')  # Default sort
    
    recommended_products = None
    predicted_category = None
    association_recommendations = []
    
    if request.user.is_authenticated:
        try:
            # First check if user has set a preferred category manually
            if request.user.preferred_category:
                predicted_category = request.user.preferred_category.name
                recommended_products = list(Product.objects.filter(
                    category=request.user.preferred_category,
                    is_active=True
                ).order_by('-rating')[:6])
            else:
                # Fallback to ML prediction if no preferred category set
                predicted_category = predict_customer_category(request.user)
                
                # Get products from predicted category (Recommended For You)
                if predicted_category:
                    try:
                        category = Category.objects.get(name__icontains=predicted_category)
                        recommended_products = list(Product.objects.filter(
                            category=category,
                            is_active=True
                        ).order_by('-rating')[:6])
                    except Category.DoesNotExist:
                        recommended_products = list(Product.objects.filter(
                            is_active=True
                        ).order_by('-rating')[:6])
                    except Category.MultipleObjectsReturned:
                        category = Category.objects.filter(name__icontains=predicted_category).first()
                        recommended_products = list(Product.objects.filter(
                            category=category,
                            is_active=True
                        ).order_by('-rating')[:6])
            
            # Fallback: if no recommendations, use top-rated products
            if not recommended_products or len(recommended_products) == 0:
                recommended_products = list(Product.objects.filter(is_active=True).order_by('-rating')[:6])
                
        except Exception as e:
            logger.error(f"Recommendation error in home_view: {e}", exc_info=True)
            recommended_products = list(Product.objects.filter(is_active=True).order_by('-rating')[:6])
    else:
        recommended_products = list(Product.objects.filter(is_active=True).order_by('-rating')[:6])
    
    # Get next best category to explore
    next_best_category = _get_next_best_category(request)
    
    # Get next best action category
    next_best_category = _get_next_best_category(request)
    
    return render(request, 'storefront/home.html', {
        'products': products,
        'recommended_products': recommended_products,
        'predicted_category': predicted_category,
        'search_query': search_query,
        'sort_option': sort_option,
        'all_categories': all_categories,
        'category_filter': category_filter,
        'next_best_category': next_best_category,
    })

def product_detail(request, id):
    """
    Product detail page with ML-powered "Frequently Bought Together" recommendations
    """
    product = get_object_or_404(Product, id=id)
    
    # Get "Frequently Bought Together" recommendations
    frequently_bought_together = []
    try:
<<<<<<< Updated upstream
        # Use the new get_frequently_bought_together function
        recommended_skus = get_frequently_bought_together(product.sku, top_n=4)
        
        if recommended_skus:
            frequently_bought_together = Product.objects.filter(
                sku__in=recommended_skus,
                is_active=True
            )[:4]
=======
        # Use association rules to find frequently bought together products
        related_products = get_frequently_bought_together(product.sku, top_n=4)
>>>>>>> Stashed changes
    except Exception as e:
        logger.error(f"Frequently bought together error in product_detail: {e}", exc_info=True)
        # Fallback: same category products
        frequently_bought_together = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id).order_by('-rating')[:4]
    
    return render(request, 'storefront/product_detail.html', {
        'product': product,
        'related_products': frequently_bought_together,  # Keep same variable name for template compatibility
        'frequently_bought_together': frequently_bought_together,
    })

# -------------------------
# Cart Views
# -------------------------
@require_POST
def cart_add(request, product_id):
    """Add product to cart and redirect to cart page (or return JSON for AJAX)"""
    cart = _cart_dict(request)
    qty = int(request.POST.get('quantity', 1))
    
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        product = Product.objects.get(id=product_id)
        
        # Check if item already exists
        old_qty = cart.get(str(product_id), 0)
        cart[str(product_id)] = old_qty + qty
        request.session.modified = True
        
        # If AJAX request, return JSON
        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': f'Added {product.name} to cart',
                'cart_count': sum(int(q) for q in cart.values())
            })
        
        if old_qty > 0:
            messages.success(request, f'Updated {product.name} quantity to {cart[str(product_id)]}')
        else:
            messages.success(request, f'✓ Added {product.name} to cart')
            
    except Product.DoesNotExist:
        if is_ajax:
            return JsonResponse({
                'status': 'error',
                'message': 'Product not found'
            }, status=404)
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
        
<<<<<<< Updated upstream
        # Get "Complete the Set" recommendations for this specific product
        item_recommendations = []
        try:
            recommended_skus = get_frequently_bought_together(p.sku, top_n=3)
            if recommended_skus:
                item_recommendations = list(Product.objects.filter(
                    sku__in=recommended_skus,
                    is_active=True
                ).exclude(id=p.id)[:3])
        except Exception as e:
            logger.error(f"Complete the set for product {p.sku} error: {e}", exc_info=True)
=======
        # Get "Complete the Set" recommendations for this specific item
        complete_the_set = get_frequently_bought_together(p.sku, top_n=6)
>>>>>>> Stashed changes
        
        order_items.append({
            'id': p.id,
            'product': p,
            'quantity': int(qty),
            'total_price': total_price,
<<<<<<< Updated upstream
            'complete_the_set': item_recommendations,
=======
            'complete_the_set': complete_the_set,
>>>>>>> Stashed changes
        })
        cart_skus.append(p.sku)

    # Free shipping for orders $50 or more
    shipping = Decimal('0.00') if subtotal >= Decimal('50.00') else Decimal('9.99')
    tax = (subtotal * Decimal('0.08')).quantize(Decimal('0.01'))
    
    discount = Decimal('0.00')
    promo_code = request.session.get('promo_code')
    print(f"DEBUG CART: promo_code from session = {promo_code}")
    if promo_code == 'SAVE10':
        discount = (subtotal * Decimal('0.1')).quantize(Decimal('0.01'))
        print(f"DEBUG CART: Applied discount = {discount}")
    
    total = (subtotal + shipping + tax - discount).quantize(Decimal('0.01'))

    # ML Integration: Get "Complete the Set" recommendations based on cart
    complete_the_set_products = []
    if cart_skus:
        try:
            # Use the new get_complete_the_set function
            recommended_skus = get_complete_the_set(cart_skus, top_n=6)
            
            if recommended_skus:
                complete_the_set_products = list(Product.objects.filter(
                    sku__in=recommended_skus,
                    is_active=True
                )[:6])
        except Exception as e:
            logger.error(f"Complete the set recommendations error: {e}", exc_info=True)

    return render(request, 'storefront/cart.html', {
        'order_items': order_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'discount': discount,
        'promo_code': promo_code,
        'recommended_products': complete_the_set_products,  # Keep same variable name for template compatibility
        'complete_the_set_products': complete_the_set_products,
    })

@require_POST
def cart_apply_promo(request):
    """Apply promo code"""
    promo_code = request.POST.get('promo_code', '').strip().upper()
    print(f"DEBUG: Received promo_code = '{promo_code}'")
    
    if promo_code == 'SAVE10':
        request.session['promo_code'] = 'SAVE10'
        request.session.modified = True
        print("DEBUG: Applied SAVE10")
        messages.success(request, '🎉 Promo code applied! 10% off')
    elif promo_code == '':
        # Removing promo code
        request.session['promo_code'] = None
        request.session.modified = True
        print("DEBUG: Removed promo code")
        messages.info(request, 'Promo code removed')
    else:
        # Invalid promo code
        request.session['promo_code'] = None
        request.session.modified = True
        print(f"DEBUG: Invalid promo code: '{promo_code}'")
        messages.error(request, 'Invalid promo code')
    
    print(f"DEBUG: Session promo_code = {request.session.get('promo_code')}")
    request.session.save()
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

    # Free shipping for orders $50 or more
    shipping = Decimal('0.00') if subtotal >= Decimal('50.00') else Decimal('9.99')
    tax = (subtotal * Decimal('0.08')).quantize(Decimal('0.01'))
    
    discount = Decimal('0.00')
    promo_code = request.session.get('promo_code')
    if promo_code == 'SAVE10':
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
        # Create the order
        try:
            # Get customer
            if request.user.is_authenticated:
                try:
                    customer = Customer.objects.get(username=request.user.username)
                except Customer.DoesNotExist:
                    messages.error(request, "Customer profile not found. Please complete your profile.")
                    return redirect("storefront:home")
            else:
                messages.error(request, "Please login to place an order.")
                return redirect("storefront:login")
            
            # Check stock availability before processing order
            for item in order_items:
                if item['product'].stock < int(item['quantity']):
                    messages.error(request, f"Sorry, {item['product'].name} only has {item['product'].stock} in stock. Please update your cart.")
                    return redirect("storefront:cart")
            
            # Get form data
            shipping_address = f"{request.POST.get('address', '')}, {request.POST.get('city', '')}, {request.POST.get('state', '')} {request.POST.get('zip', '')}, {request.POST.get('country', '')}"
            payment_method = request.POST.get('payment_method', 'card')
            
            # Create Order object
            order = Order.objects.create(
                customer=customer,
                total_amount=total,
                shipping_address=shipping_address,
                payment_method=payment_method,
                completed=True  # Mark as completed since it's a mock payment
            )
            
            # Create OrderItem objects for each product and reduce stock
            for item in order_items:
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price
                )
                
                # Reduce stock quantity
                product = item['product']
                product.stock -= int(item['quantity'])
                if product.stock < 0:
                    product.stock = 0  # Prevent negative stock
                product.save()
            
            # Clear cart and promo code
            request.session['cart'] = {}
            request.session['promo_code'] = None
            
            messages.success(request, f"🎉 Order #{order.id} placed successfully! Thank you for shopping with us.")
            return redirect("storefront:profile_orders")
            
        except Exception as e:
            logger.error(f"Order creation error: {e}", exc_info=True)
            messages.error(request, "There was an error processing your order. Please try again.")
            return redirect("storefront:checkout")

    return render(request, "storefront/checkout.html", {
        "cart_items": order_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "tax": tax,
        "discount": discount,
        "promo_code": promo_code,
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
            try:
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
                
            except IntegrityError as e:
                # Handle duplicate username or email
                error_message = str(e).lower()
                if 'username' in error_message:
                    messages.error(request, "This username is already taken. Please choose a different username.")
                elif 'email' in error_message:
                    messages.error(request, "This email is already registered. Please use a different email or login.")
                else:
                    messages.error(request, "An account with this information already exists. Please try different details.")
                logger.error(f"Registration IntegrityError: {e}")
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

# -------------------------
# Favorites/Wishlist
# -------------------------
# Favorites Views
# -------------------------
@login_required
@csrf_exempt
@require_POST
@csrf_exempt
def favorite_toggle(request, product_id):
    """Toggle favorite status for a product"""
    try:
        product = get_object_or_404(Product, id=product_id)
        favorite, created = Favorite.objects.get_or_create(
            customer=request.user,
            product=product
        )
        
        if not created:
            # Already exists, so remove it
            favorite.delete()
            return JsonResponse({
                'status': 'removed',
                'message': f'Removed {product.name} from favorites'
            })
        else:
            # Newly created
            return JsonResponse({
                'status': 'added',
                'message': f'Added {product.name} to favorites'
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def check_favorite(request, product_id):
    """Check if a product is favorited by current user"""
    is_favorited = Favorite.objects.filter(
        customer=request.user,
        product_id=product_id
    ).exists()
    
    return JsonResponse({'is_favorited': is_favorited})

# -------------------------
# Profile Views
# -------------------------
@login_required
def profile_view(request):
    """Profile dashboard"""
    customer = request.user
    
    # Get statistics
    total_orders = Order.objects.filter(customer=customer).count()
    total_favorites = Favorite.objects.filter(customer=customer).count()
    
    # Get recent orders
    recent_orders = Order.objects.filter(customer=customer).order_by('-created_at')[:5]
    
    return render(request, 'storefront/profile.html', {
        'total_orders': total_orders,
        'total_favorites': total_favorites,
        'recent_orders': recent_orders,
    })

@login_required
def profile_orders(request):
    """Order history"""
    try:
        customer = Customer.objects.get(username=request.user.username)
        orders = Order.objects.filter(customer=customer).order_by('-created_at')
    except Customer.DoesNotExist:
        orders = []
    
    # Calculate totals for each order
    orders_with_totals = []
    for order in orders:
        items = order.items.all()
        # Add item_total to each item for display
        items_with_totals = []
        for item in items:
            item_total = item.price * item.quantity
            items_with_totals.append({
                'item': item,
                'item_total': item_total,
            })
        
        # Use the stored total_amount from the order
        orders_with_totals.append({
            'order': order,
            'items': items_with_totals,
            'total': order.total_amount,
        })
    
    return render(request, 'storefront/profile_orders.html', {
        'orders_with_totals': orders_with_totals,
    })

@login_required
def profile_favorites(request):
    """Favorites/Wishlist"""
    try:
        customer = Customer.objects.get(username=request.user.username)
        favorites = Favorite.objects.filter(customer=customer).select_related('product')
    except Customer.DoesNotExist:
        favorites = []
    
    return render(request, 'storefront/profile_favorites.html', {
        'favorites': favorites,
    })

@login_required
def profile_edit(request):
    """Edit profile - basic user info (username, email, names)"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Profile updated successfully!')
            return redirect('storefront:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'storefront/profile_edit.html', {
        'form': form,
    })

@login_required
def change_password(request):
    """Change password"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Important: Update the session to prevent logout
            update_session_auth_hash(request, user)
            messages.success(request, '✓ Password changed successfully!')
            return redirect('storefront:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'storefront/change_password.html', {
        'form': form,
    })

@login_required
@require_POST
def favorite_remove(request, product_id):
    """Remove a product from favorites"""
    try:
        favorite = Favorite.objects.get(customer=request.user, product_id=product_id)
        product_name = favorite.product.name
        favorite.delete()
        messages.success(request, f'Removed {product_name} from favorites')
    except Favorite.DoesNotExist:
        messages.error(request, 'Product not in favorites')
    
    return redirect('storefront:profile_favorites')
