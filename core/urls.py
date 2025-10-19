from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', views.customer_profile, name='customer-profile'),
]
