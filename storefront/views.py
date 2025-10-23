from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Customer  # adjust based on your actual models
from django.contrib import messages
from .forms import UserRegisterForm, CustomerForm
from decimal import Decimal
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST

# Home page
def home_view(request):
    products = Product.objects.all()
    return render(request, 'storefront/home.html', {'products': products})

# Product detail page
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'storefront/product_detail.html', {'product': product})

def products_list(request):
    products = Product.objects.all()
    return render(request, 'storefront/products_list.html', {'products': products})

# Cart
def cart_view(request):
    return render(request, 'storefront/cart.html')

def _cart_dict(request):
    return request.session.setdefault('cart', {})  # keys: str(product_id) -> int(quantity)

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

@require_POST
def cart_add(request, product_id):
    cart = _cart_dict(request)
    qty = int(request.POST.get('quantity', 1))
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    request.session.modified = True
    subtotal, shipping, tax, total = _compute_totals(cart)
    return JsonResponse({
        'cart_count': sum(cart.values()),
        'subtotal': str(subtotal),
        'total': str(total),
    })

@require_POST
def cart_update(request, product_id):
    cart = _cart_dict(request)
    try:
        qty = int(request.POST.get('quantity'))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("invalid quantity")
    if qty <= 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = qty
    request.session.modified = True
    subtotal, shipping, tax, total = _compute_totals(cart)
    # compute item total
    try:
        p = Product.objects.get(id=product_id)
        item_total = (p.price * qty).quantize(Decimal('0.01'))
    except Product.DoesNotExist:
        item_total = Decimal('0.00')
    return JsonResponse({'item_total': str(item_total), 'subtotal': str(subtotal), 'total': str(total), 'cart_count': sum(cart.values())})

@require_POST
def cart_remove(request, product_id):
    cart = _cart_dict(request)
    cart.pop(str(product_id), None)
    request.session.modified = True
    subtotal, shipping, tax, total = _compute_totals(cart)
    return JsonResponse({'subtotal': str(subtotal), 'total': str(total), 'cart_count': sum(cart.values())})

# Update cart_view to build order_items from session cart
def cart_view(request):
    cart = _cart_dict(request)
    order_items = []
    subtotal = Decimal('0.00')
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(id=int(pid))
        except Product.DoesNotExist:
            continue
        total_price = (p.price * int(qty)).quantize(Decimal('0.01'))
        subtotal += total_price
        order_items.append({'id': p.id, 'product': p, 'quantity': int(qty), 'total_price': total_price})
    shipping = Decimal('9.99') if subtotal > 0 else Decimal('0.00')
    tax = (subtotal * Decimal('0.08')).quantize(Decimal('0.01'))
    total = (subtotal + shipping + tax).quantize(Decimal('0.01'))
    # recommended_products can be simple top products:
    recommended_products = Product.objects.order_by('-rating')[:6]
    return render(request, 'storefront/cart.html', {
        'order_items': order_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'recommended_products': recommended_products,
    })

# Checkout page
def checkout_view(request):
    return render(request, 'storefront/checkout.html')

# Optional: Customer profile (if needed)
def customer_profile(request, id):
    customer = get_object_or_404(Customer, id=id)
    return render(request, 'storefront/customer_profile.html', {'customer': customer})

# User registration
def register(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])  # Hash password
            user.save()
            customer = customer_form.save(commit=False)
            customer.user = user
            customer.save()
            messages.success(request, "Account created successfully!")
            return redirect('storefront:home')
    else:
        user_form = UserRegisterForm()
        customer_form = CustomerForm()

    return render(request, 'storefront/register.html', {
        'user_form': user_form,
        'customer_form': customer_form,
    })

def login(request):
    return render(request, 'storefront/login.html')