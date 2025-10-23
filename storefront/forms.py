from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Customer

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "age", "gender", "employment", "income_range",
            "employment_status", "occupation", "education",
            "household_size", "has_children", "monthly_income_sgd",
        ]