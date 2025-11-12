from django import forms
from storefront.models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'description', 'category', 'subcategory', 'stock', 
                  'reorder_threshold', 'price', 'rating', 'image', 'is_active']
        widgets = {
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., SKU-001'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Product description'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subcategory': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional subcategory'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'reorder_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': 0,
                'max': 5
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

