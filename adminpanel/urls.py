from django.urls import path
from adminpanel.views import auth_views, dashboard_views, product_views, customer_views

app_name = 'adminpanel'

urlpatterns = [
    # Authentication
    path('login/', auth_views.admin_login, name='login'),
    path('logout/', auth_views.admin_logout, name='logout'),
    
    # Dashboard
    path('', dashboard_views.dashboard, name='dashboard'),
    
    # Products
    path('products/', product_views.product_list, name='product_list'),
    path('products/add/', product_views.product_add, name='product_add'),
    path('products/<int:pk>/', product_views.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', product_views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', product_views.product_delete, name='product_delete'),
    path('products/low-stock/', product_views.low_stock, name='low_stock'),
    
    # Customers
    path('customers/', customer_views.customer_list, name='customer_list'),
    path('customers/<int:pk>/', customer_views.customer_detail, name='customer_detail'),
]