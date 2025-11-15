"""
Product Recommendations
Uses association rules to recommend products based on cart items
"""
import joblib
import os
from django.conf import settings


def get_frequently_bought_together(product_sku, top_n=4):
    """
    Get products frequently bought together with a specific product
    For "Frequently Bought Together" section on product detail pages
    
    Args:
        product_sku: SKU of the product being viewed
        top_n: Number of recommendations to return
    
    Returns:
        list: List of recommended product SKUs frequently bought with this product
    """
    try:
        rules_path = os.path.join(settings.BASE_DIR, 'AuroraMartProj', 'ml_models', 'b2c_products_500_transactions_50k.joblib')
        rules = joblib.load(rules_path)
        
        if not product_sku:
            return []
        
        # Find rules where this SKU is in the antecedents (people who bought X also bought Y)
        matched_rules = rules[rules['antecedents'].apply(lambda x: product_sku in x)]
        
        # Sort by lift (strength of association) and confidence
        top_rules = matched_rules.sort_values(by=['lift', 'confidence'], ascending=False).head(top_n * 2)
        
        # Extract recommended products (consequents)
        recommendations = set()
        for _, row in top_rules.iterrows():
            recommendations.update(row['consequents'])
        
        # Remove the original product if it appears
        recommendations.discard(product_sku)
        
        return list(recommendations)[:top_n]
        
    except Exception as e:
        print(f"Frequently bought together error: {e}")
        return []


def get_complete_the_set(cart_skus, top_n=6):
    """
    Get products that complete the set based on what's in the cart
    For "Complete the Set" section on cart pages
    Shows products that are commonly bought together with cart items
    
    Args:
        cart_skus: List of product SKUs currently in cart
        top_n: Number of recommendations to return
    
    Returns:
        list: List of recommended product SKUs to complete the set
    """
    try:
        rules_path = os.path.join(settings.BASE_DIR, 'AuroraMartProj', 'ml_models', 'b2c_products_500_transactions_50k.joblib')
        rules = joblib.load(rules_path)
        
        if not cart_skus:
            return []
        
        # Collect recommendations with their scores
        recommendations_with_scores = {}
        
        for sku in cart_skus:
            # Find rules where this SKU is in the antecedents
            matched_rules = rules[rules['antecedents'].apply(lambda x: sku in x)]
            
            # Get recommendations with lift scores
            for _, row in matched_rules.iterrows():
                for consequent in row['consequents']:
                    if consequent not in cart_skus:  # Don't recommend items already in cart
                        # Use lift as the score - higher lift means stronger association
                        if consequent in recommendations_with_scores:
                            # If already recommended, take the higher score
                            recommendations_with_scores[consequent] = max(
                                recommendations_with_scores[consequent],
                                row['lift']
                            )
                        else:
                            recommendations_with_scores[consequent] = row['lift']
        
        # Sort by score (lift) and return top N
        sorted_recommendations = sorted(
            recommendations_with_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [sku for sku, score in sorted_recommendations[:top_n]]
        
    except Exception as e:
        print(f"Complete the set error: {e}")
        return []


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
            # First check if customer has manually set preferred category
            if hasattr(customer, 'preferred_category') and customer.preferred_category:
                preferred_category_name = customer.preferred_category.name
            else:
                # Fall back to ML prediction
                from .predict_category import predict_customer_category
                preferred_category_name = predict_customer_category(customer)
            
            if preferred_category_name:
                # Get product objects to check categories
                from storefront.models import Product
                products = Product.objects.filter(sku__in=recommended_skus, is_active=True)
                
                # Prioritize products matching preferred category
                category_matches = []
                others = []
                
                for product in products:
                    if product.category and preferred_category_name.lower() in product.category.name.lower():
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
        rules_path = os.path.join(settings.BASE_DIR, 'AuroraMartProj', 'ml_models', 'b2c_products_500_transactions_50k.joblib')
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
