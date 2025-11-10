from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'storefront'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path("cart/apply_promo/", views.cart_apply_promo, name="cart_apply_promo"),
    path('buy_now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.register, name='register'),
    path('ml-insights/', views.ml_insights, name='ml_insights'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='storefront/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='storefront:home'), name='logout'),
]