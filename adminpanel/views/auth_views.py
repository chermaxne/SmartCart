from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

@never_cache
@csrf_protect
def admin_login(request):
    # If user is already authenticated and is staff, redirect to dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('adminpanel:dashboard')
    
    # If user is authenticated but not staff, show error (don't logout here to avoid CSRF issues)
    if request.user.is_authenticated and not request.user.is_staff:
        messages.error(request, 'You do not have permission to access the admin panel. Please logout from the storefront first.')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            
            if not remember_me:
                request.session.set_expiry(0)
            
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next', 'adminpanel:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    # Ensure CSRF token is generated for the template
    get_token(request)
    return render(request, 'adminpanel/login.html')


@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def admin_logout(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect('adminpanel:login')