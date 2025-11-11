from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Customer

User = get_user_model()

# ML Model Categorical Value Choices
# These MUST match the training data exactly for accurate predictions
GENDER_CHOICES = [
    ('', '-- Select Gender --'),
    ('Male', 'Male'),
    ('Female', 'Female'),
]

EMPLOYMENT_STATUS_CHOICES = [
    ('', '-- Select Employment Status --'),
    ('Full-time', 'Full-time'),
    ('Part-time', 'Part-time'),
    ('Retired', 'Retired'),
    ('Self-employed', 'Self-employed'),
    ('Student', 'Student'),
]

OCCUPATION_CHOICES = [
    ('', '-- Select Occupation --'),
    ('Admin', 'Admin'),
    ('Education', 'Education'),
    ('Sales', 'Sales'),
    ('Service', 'Service'),
    ('Skilled Trades', 'Skilled Trades'),
    ('Tech', 'Tech'),
]

EDUCATION_CHOICES = [
    ('', '-- Select Education Level --'),
    ('Secondary', 'Secondary School'),
    ('Diploma', 'Diploma'),
    ('Bachelor', 'Bachelor\'s Degree'),
    ('Master', 'Master\'s Degree'),
    ('Doctorate', 'Doctorate/PhD'),
]

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class CustomerForm(forms.ModelForm):
    # Override fields to use choices
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    employment_status = forms.ChoiceField(choices=EMPLOYMENT_STATUS_CHOICES, required=False)
    occupation = forms.ChoiceField(choices=OCCUPATION_CHOICES, required=False)
    education = forms.ChoiceField(choices=EDUCATION_CHOICES, required=False)
    
    class Meta:
        model = Customer
        fields = [
            "age", "gender", "employment_status", "occupation", "education",
            "household_size", "has_children", "monthly_income_sgd",
        ]
        widgets = {
            'age': forms.NumberInput(attrs={'min': 18, 'max': 100}),
            'household_size': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'monthly_income_sgd': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional for registration
        for field in self.fields:
            self.fields[field].required = False