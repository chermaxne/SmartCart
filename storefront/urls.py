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
    path('accounts/login/', views.login, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    
    # Favorites/Wishlist
    path('favorite/toggle/<int:product_id>/', views.favorite_toggle, name='favorite_toggle'),
    path('favorite/check/<int:product_id>/', views.check_favorite, name='check_favorite'),
    path('favorite/remove/<int:product_id>/', views.favorite_remove, name='favorite_remove'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/orders/', views.profile_orders, name='profile_orders'),
    path('profile/favorites/', views.profile_favorites, name='profile_favorites'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]