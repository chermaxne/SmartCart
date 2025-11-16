from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from storefront.models import Customer, Category, Order

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def customer_list(request):
    # Exclude staff users (admin accounts) from customer list
    customers = Customer.objects.filter(is_active=True, is_staff=False).annotate(
        order_count=Count('order'),
        total_spent=Sum('order__total_amount')
    )
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        customers = customers.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    gender_filter = request.GET.get('gender', '')
    if gender_filter:
        customers = customers.filter(gender=gender_filter)
    
    education_filter = request.GET.get('education', '')
    if education_filter:
        customers = customers.filter(education=education_filter)
    
    employment_filter = request.GET.get('employment', '')
    if employment_filter:
        customers = customers.filter(employment_status=employment_filter)
    
    occupation_filter = request.GET.get('occupation', '')
    if occupation_filter:
        customers = customers.filter(occupation=occupation_filter)
    
    category_filter = request.GET.get('category', '')
    if category_filter:
        customers = customers.filter(preferred_category_id=category_filter)
    
    children_filter = request.GET.get('has_children', '')
    if children_filter:
        has_children_bool = children_filter.lower() == 'true'
        customers = customers.filter(has_children=has_children_bool)
    
    # Filter by Age Range
    age_min = request.GET.get('age_min', '')
    age_max = request.GET.get('age_max', '')
    if age_min:
        customers = customers.filter(age__gte=age_min)
    if age_max:
        customers = customers.filter(age__lte=age_max)
    
    # Filter by Income Range
    income_min = request.GET.get('income_min', '')
    income_max = request.GET.get('income_max', '')
    if income_min:
        customers = customers.filter(monthly_income_sgd__gte=income_min)
    if income_max:
        customers = customers.filter(monthly_income_sgd__lte=income_max)
    
    # Filter by Household Size
    household_size = request.GET.get('household_size', '')
    if household_size:
        customers = customers.filter(household_size=household_size)
    
    # Sorting
    sort_by = request.GET.get('sort', '')
    if sort_by:
        customers = customers.order_by(sort_by)
    else:
        customers = customers.order_by('-id')  # Default sort by newest
    
    # Pagination
    paginator = Paginator(customers, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # Get all categories for filter dropdown
    all_categories = Category.objects.all().order_by('name')
    
    # Get distinct values for filters (only from non-staff customers)
    distinct_genders = Customer.objects.filter(is_active=True, is_staff=False).values_list('gender', flat=True).distinct().order_by('gender')
    distinct_educations = Customer.objects.filter(is_active=True, is_staff=False).values_list('education', flat=True).distinct().order_by('education')
    distinct_employments = Customer.objects.filter(is_active=True, is_staff=False).values_list('employment_status', flat=True).distinct().order_by('employment_status')
    distinct_occupations = Customer.objects.filter(is_active=True, is_staff=False).values_list('occupation', flat=True).distinct().order_by('occupation')
    distinct_household_sizes = Customer.objects.filter(is_active=True, is_staff=False).values_list('household_size', flat=True).distinct().order_by('household_size')
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'all_categories': all_categories,
        'distinct_genders': [g for g in distinct_genders if g],
        'distinct_educations': [e for e in distinct_educations if e],
        'distinct_employments': [e for e in distinct_employments if e],
        'distinct_occupations': [o for o in distinct_occupations if o],
        'distinct_household_sizes': [h for h in distinct_household_sizes if h],
    }
    
    return render(request, 'adminpanel/customer/customer_list.html', context)

@login_required(login_url='adminpanel:login')
@user_passes_test(is_staff_user, login_url='adminpanel:login')
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    # Get customer's orders
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    
    # Calculate statistics
    total_orders = orders.count()
    total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    completed_orders = orders.filter(completed=True).count()
    
    context = {
        'customer': customer,
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'completed_orders': completed_orders,
    }
    
    return render(request, 'adminpanel/customer/customer_detail.html', context)
