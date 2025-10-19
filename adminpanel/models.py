from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Customer(AbstractUser):
    """Extended user model for customer profiles"""
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=[
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ], null=True, blank=True)
    employment = models.CharField(max_length=100, null=True, blank=True)
    income_range = models.CharField(max_length=50, choices=[
        ('0-30k', '0-30k'),
        ('30k-60k', '30k-60k'),
        ('60k-100k', '60k-100k'),
        ('100k+', '100k+')
    ], null=True, blank=True)
    predicted_category = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer'

class Category(models.Model):
    """Product categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    """Product catalogue"""
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    reorder_threshold = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def needs_reorder(self):
        return self.stock <= self.reorder_threshold

class Order(models.Model):
    """Customer orders"""
    STATUS_CHOICES = [
        ('pending', 'To Pay'),
        ('processing', 'To Ship'),
        ('shipped', 'To Receive'),
        ('delivered', 'To Rate'),
        ('cancelled', 'Cancelled')
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    promo_code = models.CharField(max_length=50, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'order'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"

class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_item'

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class Cart(models.Model):
    """Shopping cart"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart'

    def __str__(self):
        return f"Cart for {self.customer.username}"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    """Items in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        db_table = 'cart_item'
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity

class Review(models.Model):
    """Product reviews"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'review'
        unique_together = ('product', 'customer')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.customer.username} for {self.product.name}"

class BrowsingHistory(models.Model):
    """Track customer browsing history"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='browsing_history')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'browsing_history'
        ordering = ['-viewed_at']

class AssociationRule(models.Model):
    """Store association rules for recommendations"""
    antecedent = models.CharField(max_length=255)  # Product SKUs in basket
    consequent = models.CharField(max_length=255)  # Recommended product SKU
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    lift = models.DecimalField(max_digits=5, decimal_places=4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'association_rule'

    def __str__(self):
        return f"{self.antecedent} -> {self.consequent}"