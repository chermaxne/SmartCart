from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF router for product API
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    # API routes
    path('api/', include(router.urls)),                        # /api/products/
    path('api/orders/', views.create_order, name='api-orders'), 
    path('api/auth/register/', views.register, name='api-register'),

    # Frontend views
    path('', views.home, name='home'),                         # /
    path('products/', views.products, name='products'),        # /products/
    path('cart/', views.cart, name='cart'),                    # /cart/
    path('checkout/', views.checkout, name='checkout'),        # /checkout/
    path('order-success/', views.order_success, name='order-success'),  # /order-success/
    path('product/<int:pk>/', views.product_details, name='product-details'), # /product/1/
]
