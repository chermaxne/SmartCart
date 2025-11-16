#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuroraMartProj.settings')
django.setup()

from storefront.models import Customer, Category
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from storefront.views import _get_next_best_category

# Create a mock request
factory = RequestFactory()
request = factory.get('/')

# Test 1: User with Beauty & Personal Care preference
print("=== Test 1: User with Beauty & Personal Care ===")
try:
    user = Customer.objects.filter(preferred_category__name__iexact="Beauty & Personal Care").first()
    if user:
        request.user = user
        request.session = {'next_best_action_shown': False}
        
        next_best = _get_next_best_category(request)
        
        print(f"User: {user.username}")
        print(f"Preferred Category: {user.preferred_category.name}")
        print(f"Next Best Action: {next_best.name if next_best else 'None'}")
        print(f"Expected: Fashion - Women")
        print(f"✓ PASS" if next_best and next_best.name == "Fashion - Women" else "✗ FAIL")
    else:
        print("No user found with Beauty & Personal Care preference")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test 2: User with Fashion - Women ===")
try:
    # Let's update chermaine to test
    user = Customer.objects.get(username="chermaine")
    request.user = user
    request.session = {'next_best_action_shown': False}
    
    next_best = _get_next_best_category(request)
    
    print(f"User: {user.username}")
    print(f"Preferred Category: {user.preferred_category.name if user.preferred_category else 'None'}")
    print(f"Next Best Action: {next_best.name if next_best else 'None'}")
    print(f"Expected: Beauty & Personal Care")
    print(f"✓ PASS" if next_best and next_best.name == "Beauty & Personal Care" else "✗ FAIL")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test 3: Anonymous user ===")
request.user = AnonymousUser()
request.session = {'next_best_action_shown': False}

next_best = _get_next_best_category(request)
print(f"User: Anonymous")
print(f"Next Best Action: {next_best.name if next_best else 'None'}")
print(f"(Should be most popular category)")
