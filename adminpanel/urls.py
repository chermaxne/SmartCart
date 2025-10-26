from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_add'),
    path('products/<int:id>/edit/', views.product_edit, name='product_edit'),
    path('customer/', views.customer_list, name='customer_list'),
    path('recommendations/', views.recommendation_list, name='recommendation_list'),
]