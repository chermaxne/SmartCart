from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['email', 'age', 'gender', 'employment', 'income_range']  