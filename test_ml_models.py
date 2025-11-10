#!/usr/bin/env python
"""
Quick test script to verify ML models load and work correctly.
Run this with: python test_ml_models.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuroraMartProj.settings')
django.setup()

from storefront.ml_utils import get_category_predictor, get_product_recommender
from storefront.models import Product

def test_category_predictor():
    """Test the decision tree category predictor."""
    print("=" * 60)
    print("Testing Category Predictor (Decision Tree)")
    print("=" * 60)
    
    try:
        predictor = get_category_predictor()
        print("✓ Model loaded successfully")
        
        # Test with sample customer data (using actual training data values)
        # Note: categorical values must match training data exactly:
        # - occupation: Admin, Education, Sales, Service, Skilled Trades, Tech
        # - education: Bachelor, Diploma, Doctorate, Master, Secondary
        # - employment_status: Full-time, Part-time, Self-employed, Student
        test_customer = {
            'age': 35,
            'gender': 'Male',
            'employment_status': 'Full-time',
            'occupation': 'Tech',
            'education': 'Bachelor',
            'household_size': 3,
            'has_children': True,
            'monthly_income_sgd': 5000.0
        }
        
        print(f"\nTest customer profile:")
        for key, value in test_customer.items():
            print(f"  {key}: {value}")
        
        predicted_category = predictor.predict_category(test_customer)
        print(f"\n✓ Predicted category: {predicted_category}")
        
        # Test with different profile
        test_customer2 = {
            'age': 22,
            'gender': 'Female',
            'employment_status': 'Student',
            'occupation': 'Education',  # Changed from 'Student' to valid value
            'education': 'Secondary',  # Changed from 'Diploma' to match student profile
            'household_size': 1,
            'has_children': False,
            'monthly_income_sgd': 1500.0
        }
        
        print(f"\nTest customer 2 profile:")
        for key, value in test_customer2.items():
            print(f"  {key}: {value}")
        
        predicted_category2 = predictor.predict_category(test_customer2)
        print(f"\n✓ Predicted category: {predicted_category2}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_product_recommender():
    """Test the association rules product recommender."""
    print("\n" + "=" * 60)
    print("Testing Product Recommender (Association Rules)")
    print("=" * 60)
    
    try:
        recommender = get_product_recommender()
        print("✓ Model loaded successfully")
        
        # Get a few sample products from database
        sample_products = Product.objects.all()[:3]
        
        if not sample_products:
            print("✗ No products in database to test with")
            return False
        
        test_skus = [p.sku for p in sample_products]
        print(f"\nTest SKUs: {test_skus}")
        
        # Test with lift metric
        recommendations_lift = recommender.get_recommendations(
            test_skus, 
            metric='lift', 
            top_n=5
        )
        print(f"\n✓ Recommendations (lift metric): {recommendations_lift}")
        
        # Test with confidence metric
        recommendations_conf = recommender.get_recommendations(
            test_skus, 
            metric='confidence', 
            top_n=5
        )
        print(f"✓ Recommendations (confidence metric): {recommendations_conf}")
        
        # Verify recommended products exist
        if recommendations_lift:
            existing_products = Product.objects.filter(sku__in=recommendations_lift)
            print(f"\n✓ Found {existing_products.count()} matching products in database:")
            for p in existing_products:
                print(f"  - {p.name} (SKU: {p.sku})")
        else:
            print("\n⚠ No recommendations found (may be normal if test SKUs don't have associations)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n🤖 ML Models Integration Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test category predictor
    results.append(("Category Predictor", test_category_predictor()))
    
    # Test product recommender
    results.append(("Product Recommender", test_product_recommender()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n✓ All tests passed! ML models are working correctly.")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
