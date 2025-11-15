from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import Customer, Category

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

class UserProfileForm(forms.ModelForm):
    """Form for editing complete user profile information"""
    phone = forms.CharField(max_length=20, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    city = forms.CharField(max_length=100, required=False)
    postal_code = forms.CharField(max_length=20, required=False)
    country = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = Customer
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone', 'age', 'gender', 'date_of_birth',
            'address', 'city', 'postal_code', 'country',
            'occupation', 'education', 'employment_status',
            'household_size', 'monthly_income_sgd', 'has_children'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'min': 18, 'max': 100}),
            'household_size': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'monthly_income_sgd': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make most fields optional
        for field in self.fields:
            if field not in ['username', 'email', 'first_name', 'last_name']:
                self.fields[field].required = False
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Check if username is taken by another user
        if Customer.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email is taken by another user
        if Customer.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class CustomerForm(forms.ModelForm):
    # Override fields to use choices
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    employment_status = forms.ChoiceField(choices=EMPLOYMENT_STATUS_CHOICES, required=False)
    occupation = forms.ChoiceField(choices=OCCUPATION_CHOICES, required=False)
    education = forms.ChoiceField(choices=EDUCATION_CHOICES, required=False)
    preferred_category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="-- Select Your Preferred Category --",
        help_text="Choose a category you're most interested in"
    )
    
    class Meta:
        model = Customer
        fields = [
            "age", "gender", "employment_status", "occupation", "education",
            "household_size", "has_children", "monthly_income_sgd", "preferred_category",
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

class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with styled fields"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})