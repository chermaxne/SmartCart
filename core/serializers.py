from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'email', 'age', 'gender', 'location', 'income_level', 'predicted_category']

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    age = serializers.IntegerField()
    gender = serializers.CharField()
    location = serializers.CharField()
    income_level = serializers.CharField()