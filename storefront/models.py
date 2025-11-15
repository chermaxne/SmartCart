from django.contrib.auth.models import AbstractUser
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Customer(AbstractUser):
    # Override username field to remove validators and allow any characters
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Any characters allowed.',
        validators=[],  # No validators - allow any characters
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    employment_status = models.CharField(max_length=50, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=100, blank=True)
    household_size = models.IntegerField(null=True, blank=True)
    has_children = models.BooleanField(default=False)
    monthly_income_sgd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=None)
    preferred_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    @property
    def full_name(self):
        """Return full name or username if name not available"""
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username
    
    @property
    def display_name(self):
        return self.full_name

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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-id']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def is_low_stock(self):
        """Check if product is below reorder threshold"""
        return self.stock <= self.reorder_threshold

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_address = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='card')

    def __str__(self):
        return f"Order {self.id} - {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Recommendation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class Favorite(models.Model):
    """Customer's favorite/wishlist products"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('customer', 'product')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.username} - {self.product.name}"