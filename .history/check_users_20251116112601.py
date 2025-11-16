#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuroraMartProj.settings')
django.setup()

from storefront.models import Category, Customer

print("=== Categories ===")
for cat in Category.objects.all():
    print(f"  {cat.id}: {cat.name}")

print("\n=== Sample Users with Preferred Categories ===")
users_with_pref = Customer.objects.filter(preferred_category__isnull=False)[:10]
if users_with_pref:
    for user in users_with_pref:
        print(f"  {user.username}: {user.preferred_category.name}")
else:
    print("  No users have preferred categories set!")

print("\n=== Sample Users without Preferred Categories ===")
users_without_pref = Customer.objects.filter(preferred_category__isnull=True)[:5]
if users_without_pref:
    for user in users_without_pref:
        print(f"  {user.username}: None")
else:
    print("  All users have preferred categories!")

print(f"\n=== Summary ===")
print(f"Total categories: {Category.objects.count()}")
print(f"Total users: {Customer.objects.count()}")
print(f"Users with preferred category: {Customer.objects.filter(preferred_category__isnull=False).count()}")
print(f"Users without preferred category: {Customer.objects.filter(preferred_category__isnull=True).count()}")
