from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from storefront.models import Customer

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def customer_list(request):
    customers = Customer.objects.filter(is_active=True)
    
    # Sorting
    sort_by = request.GET.get('sort', '')
    if sort_by:
        customers = customers.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(customers, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'adminpanel/customer/customer_list.html', context)

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    context = {
        'customer': customer,
    }
    
    return render(request, 'adminpanel/customer/customer_detail.html', context)
