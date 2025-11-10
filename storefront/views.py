from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Customer, Category
from django.contrib import messages
from .forms import UserRegisterForm, CustomerForm
from decimal import Decimal
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login as auth_login
from .ml_utils import get_category_predictor, get_product_recommender

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
    Home page with personalized recommendations based on ML
    - If user is logged in: show category-based recommendations using Decision Tree model
    - Otherwise: show popular products
    """
    products = Product.objects.all()[:12]  # limit for performance
    
    # ML Integration: Category-based recommendations for logged-in users
    recommended_products = None
    predicted_category = None
    
    if request.user.is_authenticated and hasattr(request.user, 'customer'):
        try:
            predictor = get_category_predictor()
            customer = request.user
            
            # Prepare customer data for prediction
            customer_data = {
                'age': customer.age or 30,
                'household_size': customer.household_size or 2,
                'has_children': 1 if customer.has_children else 0,
                'monthly_income_sgd': float(customer.monthly_income_sgd or 5000),
                'gender': customer.gender or 'Male',
                'employment_status': customer.employment_status or 'Full-time',
                'occupation': customer.occupation or 'Tech',
                'education': customer.education or 'Bachelor',
            }
            
            # Predict preferred category
            predicted_category = predictor.predict_category(customer_data)
            
            # Get products from predicted category
            try:
                category = Category.objects.get(name__icontains=predicted_category)
                recommended_products = Product.objects.filter(category=category).order_by('-rating')[:6]
            except Category.DoesNotExist:
                # Fallback to top-rated products
                recommended_products = Product.objects.order_by('-rating')[:6]
                
        except Exception as e:
            # Fallback on error
            print(f"ML prediction error: {e}")
            recommended_products = Product.objects.order_by('-rating')[:6]
    else:
        # For non-authenticated users, show popular products
        recommended_products = Product.objects.order_by('-rating')[:6]
    
    return render(request, 'storefront/home.html', {
        'products': products,
        'recommended_products': recommended_products,
        'predicted_category': predicted_category,
    })

def product_detail(request, id):
    """
    Product detail page with ML-powered "Frequently Bought Together" recommendations
    Uses Association Rules model
    """
    product = get_object_or_404(Product, id=id)
    
    # ML Integration: Association Rules - Frequently Bought Together
    related_products = []
    try:
        recommender = get_product_recommender()
        recommended_skus = recommender.get_recommendations(
            [product.sku],
            metric='lift',
            top_n=4
        )
        
        if recommended_skus:
            related_products = Product.objects.filter(sku__in=recommended_skus)[:4]
    except Exception as e:
        print(f"Association rules error: {e}")
        # Fallback: same category products
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id).order_by('-rating')[:4]
    
    return render(request, 'storefront/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })

def products_list(request):
    search_query = request.GET.get('search', '').strip().lower()
    sort_option = request.GET.get('sort', '')

    products = Product.objects.all()
    if search_query:
        products = products.filter(name__icontains=search_query)

    if sort_option == 'name-asc':
        products = products.order_by('name')
    elif sort_option == 'name-desc':
        products = products.order_by('-name')
    elif sort_option == 'price-asc':
        products = products.order_by('price')
    elif sort_option == 'price-desc':
        products = products.order_by('-price')

    return render(request, 'storefront/products_list.html', {
        'products': products,
        'search_query': search_query,
        'sort_option': sort_option,
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
            messages.success(request, f'Added {product.name} to cart')
            
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
    Display cart page with ML-powered recommendations
    Uses Association Rules model for "You May Also Like" based on cart contents
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

    # ML Integration: Association Rules - Smart recommendations based on cart
    recommended_products = []
    if cart_skus:
        try:
            recommender = get_product_recommender()
            recommended_skus = recommender.get_recommendations(
                cart_skus,
                metric='confidence',  # use confidence for cart recommendations
                top_n=6
            )
            
            if recommended_skus:
                recommended_products = Product.objects.filter(sku__in=recommended_skus)[:6]
        except Exception as e:
            print(f"Cart recommendations error: {e}")
            # Fallback to popular products
            recommended_products = Product.objects.order_by('-rating')[:6]
    else:
        # Empty cart - show popular products
        recommended_products = Product.objects.order_by('-rating')[:6]

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
        messages.success(request, 'Promo code applied! 10% off')
    elif promo_code:
        messages.error(request, 'Invalid promo code')
    else:
        messages.error(request, 'Please enter a promo code')
    
    return redirect('storefront:cart')

# -------------------------
# Checkout
# -------------------------
def checkout(request):
    cart = _cart_dict(request)
    order_items = []
    subtotal = Decimal('0.00')
    
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(id=int(pid))
            total_price = (p.price * int(qty)).quantize(Decimal('0.01'))
            subtotal += total_price
            order_items.append({'product': p, 'quantity': qty, 'total_price': total_price})
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

    if request.method == "POST":
        # Here you would save order to DB
        messages.success(request, "Order placed successfully!")
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
    })

# -------------------------
# Auth & Customer
# -------------------------
def register(request):
    """
    User registration with ML-powered category prediction
    After registration, predict preferred category and show personalized message
    """
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password1'])
            user.save()
            customer = customer_form.save(commit=False)
            customer.user = user
            customer.save()
            
            # ML Integration: Predict preferred category for new customer
            try:
                predictor = get_category_predictor()
                customer_data = {
                    'age': customer.age or 30,
                    'household_size': customer.household_size or 2,
                    'has_children': 1 if customer.has_children else 0,
                    'monthly_income_sgd': float(customer.monthly_income_sgd or 5000),
                    'gender': customer.gender or 'Male',
                    'employment_status': customer.employment_status or 'Full-time',
                    'occupation': customer.occupation or 'Tech',
                    'education': customer.education or 'Bachelor',
                }
                
                predicted_category = predictor.predict_category(customer_data)
                
                # Save predicted category to customer profile
                try:
                    category = Category.objects.get(name__icontains=predicted_category)
                    customer.preferred_category = category
                    customer.save()
                    
                    messages.success(
                        request, 
                        f"Account created successfully! Based on your profile, you might like our {predicted_category} products."
                    )
                except Category.DoesNotExist:
                    messages.success(request, "Account created successfully!")
                    
            except Exception as e:
                print(f"Category prediction error during registration: {e}")
                messages.success(request, "Account created successfully!")
            
            return redirect('storefront:home')
    else:
        user_form = UserRegisterForm()
        customer_form = CustomerForm()

    return render(request, 'storefront/register.html', {
        'user_form': user_form,
        'customer_form': customer_form,
    })

def customer_profile(request, id):
    customer = get_object_or_404(Customer, id=id)
    return render(request, 'storefront/customer_profile.html', {'customer': customer})

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
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('storefront:home')
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'storefront/login.html', {'username': username})

    return render(request, 'storefront/login.html')

# -------------------------
# ML Model Showcase
# -------------------------
def ml_insights(request):
    """
    Showcase page for ML model insights
    Shows personalized category prediction and product recommendations
    """
    insights = {}
    
    # Category prediction - only for authenticated users with customer profile
    if request.user.is_authenticated and hasattr(request.user, 'customer'):
        try:
            customer = request.user
            predictor = get_category_predictor()
            
            # Category Prediction Insights
            customer_data = {
                'age': customer.age or 30,
                'household_size': customer.household_size or 2,
                'has_children': 1 if customer.has_children else 0,
                'monthly_income_sgd': float(customer.monthly_income_sgd or 5000),
                'gender': customer.gender or 'Male',
                'employment_status': customer.employment_status or 'Full-time',
                'occupation': customer.occupation or 'Tech',
                'education': customer.education or 'Bachelor',
            }
            
            predicted_category = predictor.predict_category(customer_data)
            
            # Get products from predicted category
            try:
                category = Category.objects.get(name__icontains=predicted_category)
                category_products = Product.objects.filter(category=category).order_by('-rating')[:8]
            except Category.DoesNotExist:
                category_products = []
            
            insights['predicted_category'] = predicted_category
            insights['category_products'] = category_products
            insights['customer_profile'] = customer_data
                    
        except Exception as e:
            print(f"Category prediction error: {e}")
    
    # Association Rules - works for everyone with cart items (logged in or not)
    try:
        recommender = get_product_recommender()
        cart = _cart_dict(request)
        
        print(f"DEBUG: Cart contents: {cart}")  # Debug line
        
        if cart:
            cart_skus = []
            cart_products = []
            for pid in cart.keys():
                try:
                    p = Product.objects.get(id=int(pid))
                    cart_skus.append(p.sku)
                    cart_products.append(p)
                    print(f"DEBUG: Added product {p.name} (SKU: {p.sku})")  # Debug line
                except Product.DoesNotExist:
                    print(f"DEBUG: Product {pid} not found")  # Debug line
                    pass
            
            print(f"DEBUG: Cart SKUs: {cart_skus}")  # Debug line
            
            if cart_skus:
                recommended_skus = recommender.get_recommendations(
                    cart_skus,
                    metric='lift',
                    top_n=8
                )
                
                print(f"DEBUG: Recommended SKUs: {recommended_skus}")  # Debug line
                
                association_recommendations = Product.objects.filter(sku__in=recommended_skus)[:8]
                insights['cart_products'] = cart_products
                insights['association_recommendations'] = association_recommendations
                
                print(f"DEBUG: Found {len(association_recommendations)} recommendations")  # Debug line
            else:
                print("DEBUG: No cart SKUs found")  # Debug line
        else:
            print("DEBUG: Cart is empty")  # Debug line
    except Exception as e:
        print(f"Association rules error: {e}")
        import traceback
        traceback.print_exc()  # Print full error traceback
        insights['association_error'] = str(e)
    
    return render(request, 'storefront/ml_insights.html', {'insights': insights})