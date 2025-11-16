#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuroraMartProj.settings')
django.setup()

from storefront.models import Customer, Product

username = "chermaine"

try:
    user = Customer.objects.get(username=username)
    
    print(f"=== Testing Recommendation Logic for {username} ===")
    print(f"Preferred Category: {user.preferred_category.name if user.preferred_category else 'None'}")
    
    if user.preferred_category:
        # This is what the view does
        predicted_category = user.preferred_category.name
        recommended_products = list(Product.objects.filter(
            category=user.preferred_category,
            is_active=True
        ).order_by('-rating')[:6])
        
        print(f"\nCategory being used for recommendations: {predicted_category}")
        print(f"Number of products found: {len(recommended_products)}")
        
        if recommended_products:
            print("\nRecommended products:")
            for i, p in enumerate(recommended_products, 1):
                print(f"  {i}. {p.name}")
                print(f"     Category: {p.category.name}")
                print(f"     Price: ${p.price}, Rating: {p.rating}")
        else:
            print("\nNo products found!")
    else:
        print("\nNo preferred category set - would use ML prediction")
        
except Customer.DoesNotExist:
    print(f"User {username} not found!")
