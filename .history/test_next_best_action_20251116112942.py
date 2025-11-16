#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuroraMartProj.settings')
django.setup()

from storefront.models import Customer, Category
from django.db.models import Count, Q

# Define complementary category mappings
COMPLEMENTARY_CATEGORIES = {
    'Fashion - Women': ['Beauty & Personal Care', 'Fashion - Men', 'Health'],
    'Fashion - Men': ['Fashion - Women', 'Sports & Outdoors', 'Automotive'],
    'Beauty & Personal Care': ['Fashion - Women', 'Health', 'Fashion - Men'],
    'Electronics': ['Home & Kitchen', 'Sports & Outdoors', 'Automotive'],
    'Sports & Outdoors': ['Health', 'Fashion - Men', 'Electronics'],
    'Books': ['Electronics', 'Home & Kitchen', 'Toys & Games'],
    'Home & Kitchen': ['Electronics', 'Groceries & Gourmet', 'Books'],
    'Groceries & Gourmet': ['Home & Kitchen', 'Health', 'Pet Supplies'],
    'Health': ['Beauty & Personal Care', 'Sports & Outdoors', 'Groceries & Gourmet'],
    'Pet Supplies': ['Groceries & Gourmet', 'Home & Kitchen', 'Health'],
    'Automotive': ['Electronics', 'Sports & Outdoors', 'Fashion - Men'],
    'Toys & Games': ['Books', 'Electronics', 'Sports & Outdoors'],
}

print("=== Testing Next Best Action Logic ===\n")

# Test for each category
for category in Category.objects.all().order_by('name'):
    preferred_name = category.name
    complementary_names = COMPLEMENTARY_CATEGORIES.get(preferred_name, [])
    
    print(f"Preferred: {preferred_name}")
    print(f"Complementary suggestions: {', '.join(complementary_names) if complementary_names else 'None defined'}")
    
    # Find which one would be selected
    next_best = None
    for comp_name in complementary_names:
        try:
            comp_category = Category.objects.annotate(
                product_count=Count('product', filter=Q(product__is_active=True))
            ).get(name__iexact=comp_name, product_count__gt=0)
            next_best = comp_category
            break
        except Category.DoesNotExist:
            continue
    
    if next_best:
        print(f"✓ Next Best Action: {next_best.name}\n")
    else:
        print(f"✗ No complementary category available\n")

# Test specifically for Beauty & Personal Care
print("\n=== Specific Test: Beauty & Personal Care ===")
beauty_cat = Category.objects.get(name__iexact="Beauty & Personal Care")
complementary = COMPLEMENTARY_CATEGORIES.get(beauty_cat.name, [])
print(f"Preferred: {beauty_cat.name}")
print(f"Complementary list: {complementary}")
print(f"First complementary: {complementary[0] if complementary else 'None'}")

try:
    next_best = Category.objects.get(name__iexact=complementary[0])
    print(f"✓ Should suggest: {next_best.name}")
except:
    print("✗ Category not found")
