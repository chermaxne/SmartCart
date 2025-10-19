from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    location = models.CharField(max_length=100)
    income_level = models.CharField(max_length=20)
    predicted_category = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image_url = models.URLField()
    stock = models.IntegerField()
    rating = models.FloatField(default=0)
    reviews_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='core_orders')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='core_reviews')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='core_reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)