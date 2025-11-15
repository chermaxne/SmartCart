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


def get_frequently_bought_together(product_sku, top_n=4):
    """
    Get products frequently bought together with a specific product
    Used for "Frequently Bought Together" sections on product detail pages
    
    Args:
        product_sku: The SKU of the product to find companions for
        top_n: Number of recommendations to return
    
    Returns:
        list: List of Product objects frequently bought with this product
    """
    try:
        rules_path = os.path.join(settings.BASE_DIR, 'AuroraMartProj', 'ml_models', 'b2c_products_500_transactions_50k.joblib')
        rules = joblib.load(rules_path)
        
        # Find rules where this SKU is in the antecedents
        matched_rules = rules[rules['antecedents'].apply(lambda x: product_sku in x)]
        
        # Sort by lift and get top rules
        top_rules = matched_rules.sort_values(by='lift', ascending=False).head(top_n * 2)
        
        # Extract recommended products (consequents)
        recommendations = set()
        for _, row in top_rules.iterrows():
            recommendations.update(row['consequents'])
        
        # Remove the original product
        recommendations.discard(product_sku)
        
        # Get actual product objects
        from storefront.models import Product
        recommended_skus = list(recommendations)[:top_n]
        products = Product.objects.filter(sku__in=recommended_skus, is_active=True)
        
        return list(products)
        
    except Exception as e:
        print(f"Frequently bought together error: {e}")
        return []


def get_complete_the_set(cart_skus, top_n=6):
    """
    Get products that complete the set based on all items in cart
    Aggregates recommendations from all cart items
    
    Args:
        cart_skus: List of product SKUs currently in cart
        top_n: Number of recommendations to return
    
    Returns:
        list: List of Product objects that complete the set
    """
    try:
        rules_path = os.path.join(settings.BASE_DIR, 'AuroraMartProj', 'ml_models', 'b2c_products_500_transactions_50k.joblib')
        rules = joblib.load(rules_path)
        
        if not cart_skus:
            return []
        
        # Aggregate recommendations from all cart items with confidence scores
        recommendation_scores = {}
        
        for sku in cart_skus:
            matched_rules = rules[rules['antecedents'].apply(lambda x: sku in x)]
            top_rules = matched_rules.sort_values(by='lift', ascending=False).head(top_n)
            
            for _, row in top_rules.iterrows():
                for consequent in row['consequents']:
                    if consequent not in cart_skus:
                        # Use lift as the score
                        if consequent in recommendation_scores:
                            recommendation_scores[consequent] += row['lift']
                        else:
                            recommendation_scores[consequent] = row['lift']
        
        # Sort by aggregated score and get top recommendations
        sorted_recommendations = sorted(recommendation_scores.items(), key=lambda x: x[1], reverse=True)
        recommended_skus = [sku for sku, score in sorted_recommendations[:top_n]]
        
        # Get actual product objects
        from storefront.models import Product
        products = Product.objects.filter(sku__in=recommended_skus, is_active=True)
        
        # Return in order of recommendation score
        products_dict = {p.sku: p for p in products}
        ordered_products = [products_dict[sku] for sku in recommended_skus if sku in products_dict]
        
        return ordered_products
        
    except Exception as e:
        print(f"Complete the set error: {e}")
        return []
