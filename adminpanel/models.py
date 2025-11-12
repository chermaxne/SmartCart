from django.db import models
from django.conf import settings

class Category(models.Model):

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products'
    )
    
    subcategory = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Product subcategory - specific classification within the main category"
    )
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    reorder_threshold = models.IntegerField(default=10)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['subcategory']),  
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def is_low_stock(self):
        """Check if product is below reorder threshold"""
        return self.stock <= self.reorder_threshold
    
    @property
    def full_category_path(self):
        """Get full category path (e.g., 'Beauty & Personal Care / Makeup')"""
        if self.subcategory:
            return f"{self.category.name} / {self.subcategory}"
        return self.category.name
    
    @property
    def category_breadcrumb(self):
        """Get category breadcrumb list for display"""
        if self.subcategory:
            return [self.category.name, self.subcategory]
        return [self.category.name]

class Customer(models.Model):
    
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    EMPLOYMENT_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Self-employed', 'Self-employed'),
        ('Student', 'Student'),
        ('Unemployed', 'Unemployed'),
        ('Retired', 'Retired'),
    ]
    
    OCCUPATION_CHOICES = [
        ('Sales', 'Sales'),
        ('Service', 'Service'),
        ('Admin', 'Admin'),
        ('Tech', 'Tech'),
        ('Education', 'Education'),
        ('Skilled Trades', 'Skilled Trades'),
        ('Healthcare', 'Healthcare'),
        ('Other', 'Other'),
    ]
    
    EDUCATION_CHOICES = [
        ('Secondary', 'Secondary'),
        ('Diploma', 'Diploma'),
        ('Bachelor', 'Bachelor'),
        ('Master', 'Master'),
        ('PhD', 'PhD'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    
    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES)
    occupation = models.CharField(max_length=50, choices=OCCUPATION_CHOICES)
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES)
    monthly_income_sgd = models.DecimalField(max_digits=12, decimal_places=2)
    
    household_size = models.IntegerField(default=1)
    has_children = models.BooleanField(default=False)
    
    registration_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-registration_date']
        verbose_name_plural = "Customers"
    
    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email.split('@')[0].replace('.', ' ').title()
    
    @property
    def display_name(self):
        return self.full_name


class StockHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_history')
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    change_amount = models.IntegerField()
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = "Stock Histories"