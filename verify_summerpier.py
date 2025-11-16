#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuroraMartProj.settings')
django.setup()

from storefront.models import Customer

user = Customer.objects.get(username="summerpier")
print(f"User: {user.username}")
print(f"Preferred Category: {user.preferred_category.name if user.preferred_category else 'None'}")
print(f"\nExpected Next Best Action: Fashion - Women")
print(f"(Because Beauty & Personal Care → Fashion - Women is the first complementary category)")
