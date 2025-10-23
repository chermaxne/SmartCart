from django.contrib.auth.models import AbstractUser
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Customer(AbstractUser):
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    employment = models.CharField(max_length=100, blank=True)        # used in forms
    income_range = models.CharField(max_length=50, blank=True)       # used in forms
    employment_status = models.CharField(max_length=50, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=100, blank=True)
    household_size = models.IntegerField(null=True, blank=True)
    has_children = models.BooleanField(default=False)
    monthly_income_sgd = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    preferred_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

class Product(models.Model):
    sku = models.CharField(max_length=40, unique=True, db_index=True)  # maps "SKU code"
    name = models.CharField(max_length=200)                            # maps "Product name"
    description = models.TextField(blank=True)                         # maps "Product description"
    category = models.ForeignKey(Category, on_delete=models.CASCADE)    # maps "Product Category"
    subcategory = models.CharField(max_length=150, blank=True)         # maps "Product Subcategory"
    stock = models.IntegerField(default=0)                             # maps "Quantity on hand"
    reorder_threshold = models.IntegerField(default=5)                 # maps "Reorder Quantity"
    price = models.DecimalField(max_digits=10, decimal_places=2)       # maps "Unit price"
    rating = models.FloatField(default=0)                              # maps "Product rating"
    image = models.ImageField(upload_to='products/', blank=True, null=True, default='products/default-product.png')

    class Meta:
        ordering = ['-id']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} ({self.sku})"

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} - {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Recommendation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)