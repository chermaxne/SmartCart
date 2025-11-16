#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuroraMartProj.settings')
django.setup()

from storefront.models import Product
from predictions_code.predict_products import get_frequently_bought_together

# Test one product
test_sku = "HKB-AZCCBLSK"  # BrightNest Bedding Pro

print(f"=== Testing get_frequently_bought_together ===")
print(f"Test SKU: {test_sku}")

try:
    # Call the function (should return Product objects)
    recommendations = get_frequently_bought_together(test_sku, top_n=4)
    
    print(f"\nReturn type: {type(recommendations)}")
    print(f"Number of recommendations: {len(recommendations)}")
    
    if recommendations:
        print("\n✓ Recommendations found:")
        for i, product in enumerate(recommendations, 1):
            print(f"  {i}. {product.name}")
            print(f"     SKU: {product.sku}")
            print(f"     Price: ${product.price}")
            print(f"     Active: {product.is_active}")
            print(f"     Category: {product.category.name}")
    else:
        print("\n✗ No recommendations returned")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Now test the view logic
print("\n\n=== Testing View Logic ===")
try:
    test_product = Product.objects.get(sku=test_sku)
    print(f"Product: {test_product.name}")
    
    frequently_bought_together = get_frequently_bought_together(test_product.sku, top_n=4)
    
    if frequently_bought_together:
        frequently_bought_together = list(frequently_bought_together)
        print(f"\n✓ View would show {len(frequently_bought_together)} products:")
        for p in frequently_bought_together:
            print(f"  - {p.name} (${p.price})")
    else:
        print("\n✗ View would show fallback products")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
