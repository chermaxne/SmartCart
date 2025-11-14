"""
Predictions Code Module
Simplified ML prediction functions for AuroraMart
"""

from .predict_category import predict_customer_category
from .predict_products import get_product_recommendations, get_product_recommendations_by_skus

__all__ = [
    'predict_customer_category',
    'get_product_recommendations',
    'get_product_recommendations_by_skus',
]
