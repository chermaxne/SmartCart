from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Product, Customer, Order, Review
from storefront.serializers import ProductSerializer
from django.contrib.auth.decorators import login_required


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Customer registration with ML prediction"""
    username = request.data.get('email')
    password = request.data.get('password')
    
    # Create user
    user = User.objects.create_user(username=username, email=username, password=password)
    
    # Create customer profile
    customer = Customer.objects.create(
        user=user,
        age=request.data.get('age'),
        gender=request.data.get('gender'),
        location=request.data.get('location'),
        income_level=request.data.get('incomeLevel')
    )
    
    # Run ML prediction (implement your decision tree here)
    predicted_category = predict_category(customer)
    customer.predicted_category = predicted_category
    customer.save()
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'customer': CustomerSerializer(customer).data
    })

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create order from cart"""
    customer = request.user.customer
    items = request.data.get('items', [])
    
    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in items)
    
    # Create order
    order = Order.objects.create(customer=customer, total=total)
    
    # Create order items
    for item in items:
        OrderItem.objects.create(
            order=order,
            product_id=item['sku'],
            quantity=item['quantity'],
            price=item['price']
        )
    
    return Response(OrderSerializer(order).data)

@login_required
def customer_profile(request):
    return render(request, 'core/account.html', {'user': request.user})