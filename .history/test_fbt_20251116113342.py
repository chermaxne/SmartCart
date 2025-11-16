#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuroraMartProj.settings')
django.setup()

from storefront.models import Product
from predictions_code.predict_products import get_frequently_bought_together

# Test products from the list
test_products = [
    ("AutoZen Oils & Fluids Pro", "AO&-AZV46ESM"),
    ("BrightNest Bedding Pro", "HKB-AZCCBLSK"),
    ("ChefMate Cookware Set", "HKC-1IYM90PK"),
    ("CleanRide Car Care Care", "ACC-N2ATQYYV"),
]

print("=== Testing Frequently Bought Together ===\n")

for name, sku in test_products:
    print(f"Product: {name}")
    print(f"SKU: {sku}")
    
    try:
        # Test the function
        recommended_skus = get_frequently_bought_together(sku, top_n=4)
        
        if recommended_skus:
            print(f"✓ Found {len(recommended_skus)} recommendations")
            print(f"  Recommended SKUs: {recommended_skus}")
            
            # Try to get actual products
            products = Product.objects.filter(
                sku__in=recommended_skus,
                is_active=True
            )[:4]
            
            if products:
                print(f"  Found {products.count()} matching products:")
                for p in products:
                    print(f"    - {p.name} (${p.price})")
            else:
                print(f"  ✗ No active products found for these SKUs")
        else:
            print(f"✗ No recommendations returned")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()

# Also check if the function exists and is working
print("\n=== Function Test ===")
try:
    from predictions_code import predict_products
    print(f"✓ Module imported successfully")
    print(f"  Available functions: {[x for x in dir(predict_products) if not x.startswith('_')]}")
except Exception as e:
    print(f"✗ Import error: {e}")
