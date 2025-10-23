from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'storefront'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('products/', views.products_list, name='products_list'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('register/', views.register, name='register'),
    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='storefront/login.html'),
         name='login'),
]
