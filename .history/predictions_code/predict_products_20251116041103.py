"""
Product Recommendations
Uses association rules to recommend products based on cart items
"""
import joblib
import os
from django.conf import settings


def get_product_recommendations(cart_skus, customer=None, top_n=5):
    """
    Get product recommendations based on cart items and optionally customer profile
    
    Args:
        cart_skus: List of product SKUs in cart
        customer: Optional Customer model instance for personalization
        top_n: Number of recommendations to return
    
    Returns:
        list: List of recommended product SKUs
    """
    try:
        # Load association rules model
        rules_path = os.path.join(settings.BASE_DIR, 'AuroraMartProj', 'ml_models', 'b2c_products_500_transactions_50k.joblib')
        rules = joblib.load(rules_path)
        
        if not cart_skus:
            return []
        
        # Find products frequently bought together with cart items
        recommendations = set()
        
        for sku in cart_skus:
            # Find rules where this SKU is in the antecedents
            matched_rules = rules[rules['antecedents'].apply(lambda x: sku in x)]
            
            # Sort by lift and get top rules
            top_rules = matched_rules.sort_values(by='lift', ascending=False).head(top_n)
            
            # Extract recommended products (consequents)
            for _, row in top_rules.iterrows():
                recommendations.update(row['consequents'])
        
        # Remove items already in cart
        recommendations.difference_update(cart_skus)
        
        recommended_skus = list(recommendations)[:top_n]
        
        # If customer provided, boost recommendations matching their preferred category
        if customer and recommended_skus:
            from .predict_category import predict_customer_category
            preferred_category = predict_customer_category(customer)
            
            if preferred_category:
                # Get product objects to check categories
                from storefront.models import Product
                products = Product.objects.filter(sku__in=recommended_skus, is_active=True)
                
                # Prioritize products matching preferred category
                category_matches = []
                others = []
                
                for product in products:
                    if product.category and preferred_category.lower() in product.category.name.lower():
                        category_matches.append(product.sku)
                    else:
                        others.append(product.sku)
                
                # Return category matches first, then others
                recommended_skus = category_matches + others
        
        return recommended_skus[:top_n]
        
    except Exception as e:
        print(f"Product recommendation error: {e}")
        return []


def get_product_recommendations_by_skus(cart_skus, top_n=5):
    """
    Get product recommendations based only on association rules (no personalization)
    Useful for non-authenticated users
    
    Args:
        cart_skus: List of product SKUs in cart
        top_n: Number of recommendations to return
    
    Returns:
        list: List of recommended product SKUs
    """
    try:
        rules_path = os.path.join(settings.BASE_DIR, 'ml_models', 'b2c_products_500_transactions_50k.joblib')
        rules = joblib.load(rules_path)
        
        if not cart_skus:
            return []
        
        recommendations = set()
        
        for sku in cart_skus:
            matched_rules = rules[rules['antecedents'].apply(lambda x: sku in x)]
            top_rules = matched_rules.sort_values(by='lift', ascending=False).head(top_n)
            
            for _, row in top_rules.iterrows():
                recommendations.update(row['consequents'])
        
        recommendations.difference_update(cart_skus)
        return list(recommendations)[:top_n]
        
    except Exception as e:
        print(f"Association rules error: {e}")
        return []
