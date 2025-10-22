from django import forms
from storefront.models import Product, Recommendation

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'description', 'category', 'price', 'rating', 'stock']

class RecommendationForm(forms.ModelForm):
    class Meta:
        model = Recommendation
        fields = ['customer', 'product', 'reason']
