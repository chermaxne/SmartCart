#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuroraMartProj.settings')
django.setup()

from storefront.models import Category, Customer, Product
from predictions_code.predict_category import predict_customer_category

# Test with a specific user
username = input("Enter username to test (or press Enter for 'chermaine'): ").strip() or "chermaine"

try:
    user = Customer.objects.get(username=username)
    print(f"\n=== User: {user.username} ===")
    print(f"Age: {user.age}")
    print(f"Gender: {user.gender}")
    print(f"Employment: {user.employment_status}")
    print(f"Occupation: {user.occupation}")
    print(f"Education: {user.education}")
    print(f"Household size: {user.household_size}")
    print(f"Has children: {user.has_children}")
    print(f"Monthly income: {user.monthly_income_sgd}")
    print(f"Current preferred category: {user.preferred_category.name if user.preferred_category else 'None'}")
    
    print("\n=== ML Prediction ===")
    predicted_category_name = predict_customer_category(user)
    print(f"Predicted category: {predicted_category_name}")
    
    if predicted_category_name:
        print("\n=== Matching Categories ===")
        # Try exact match
        try:
            exact_match = Category.objects.get(name__iexact=predicted_category_name)
            print(f"Exact match (case-insensitive): {exact_match.name} (ID: {exact_match.id})")
            
            # Count products
            product_count = Product.objects.filter(category=exact_match, is_active=True).count()
            print(f"Active products in this category: {product_count}")
            
            if product_count > 0:
                print("\nSample products:")
                for p in Product.objects.filter(category=exact_match, is_active=True).order_by('-rating')[:3]:
                    print(f"  - {p.name} (${p.price}, rating: {p.rating})")
        except Category.DoesNotExist:
            print(f"No exact match for '{predicted_category_name}'")
            
            # Try contains match
            contains_matches = Category.objects.filter(name__icontains=predicted_category_name)
            if contains_matches.exists():
                print(f"\nCategories containing '{predicted_category_name}':")
                for cat in contains_matches:
                    print(f"  - {cat.name} (ID: {cat.id})")
        except Category.MultipleObjectsReturned:
            print(f"Multiple categories match '{predicted_category_name}':")
            for cat in Category.objects.filter(name__icontains=predicted_category_name):
                print(f"  - {cat.name} (ID: {cat.id})")
    
    print("\n=== All Available Categories ===")
    for cat in Category.objects.all():
        product_count = Product.objects.filter(category=cat, is_active=True).count()
        print(f"{cat.id}: {cat.name} ({product_count} products)")
        
except Customer.DoesNotExist:
    print(f"User '{username}' not found!")
    print("\nAvailable users:")
    for u in Customer.objects.all()[:10]:
        print(f"  - {u.username}")
