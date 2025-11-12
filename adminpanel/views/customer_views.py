from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from storefront.models import Customer

@login_required(login_url='adminpanel:login')
def customer_list(request):
    customers = Customer.objects.filter(is_active=True)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        customers = customers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(customers, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'adminpanel/customer/customer_list.html', context)


@login_required(login_url='adminpanel:login')
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    context = {
        'customer': customer,
    }
    
    return render(request, 'adminpanel/customer/customer_detail.html', context)
