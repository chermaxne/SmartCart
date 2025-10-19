from django.urls import path
from . import views

urlpatterns = [
    path('base_admin/', views.is_admin, name='admin_products'),
    path('home/', views.home, name='admin_home'),
    path('register/', views.register, name='admin_register'),
]