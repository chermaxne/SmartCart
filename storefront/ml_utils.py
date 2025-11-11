"""
ML Model Integration Utilities
Provides functions to load and use the pretrained ML models
"""
import os
import joblib
import pandas as pd
import logging
from django.conf import settings


class CategoryPredictor:
    """
    Wrapper for the decision tree classification model that predicts
    customer preferred categories based on demographics.
    """
    
    def __init__(self, model_path):
        """Load the trained decision tree model."""
        self.model = joblib.load(model_path)
        
        # Define expected feature columns from training
        # These must match exactly what the model was trained on
        # Based on b2c_customers_100.csv actual values:
        # - employment_status: Full-time, Part-time, Retired, Self-employed, Student
        # - occupation: Admin, Education, Sales, Service, Skilled Trades, Tech
        # - education: Bachelor, Diploma, Doctorate, Master, Secondary
        self.feature_columns = [
            'age', 'household_size', 'has_children', 'monthly_income_sgd',
            'gender_Female', 'gender_Male',
            'employment_status_Full-time', 'employment_status_Part-time',
            'employment_status_Retired', 'employment_status_Self-employed', 
            'employment_status_Student',
            'occupation_Admin', 'occupation_Education', 'occupation_Sales',
            'occupation_Service', 'occupation_Skilled Trades', 'occupation_Tech',
            'education_Bachelor', 'education_Diploma', 'education_Doctorate',
            'education_Master', 'education_Secondary'
        ]
    
    def predict_category(self, customer_data):
        """
        Predict preferred category for a customer
        
        Args:
            customer_data (dict): Dictionary with keys:
                - age (int)
                - household_size (int)
                - has_children (bool or int)
                - monthly_income_sgd (float)
                - gender (str): 'Male' or 'Female'
                - employment_status (str): 'Full-time', 'Part-time', etc.
                - occupation (str): 'Tech', 'Sales', etc.
                - education (str): 'Bachelor', 'Master', etc.
        
        Returns:
            str: Predicted category name
        """
        # Convert to DataFrame
        input_df = pd.DataFrame([customer_data])
        
        # One-hot encode categorical variables
        input_encoded = pd.get_dummies(
            input_df, 
            columns=['gender', 'employment_status', 'occupation', 'education']
        )
        
        # Ensure all required columns are present
        for col in self.feature_columns:
            if col not in input_encoded.columns:
                input_encoded[col] = False if col.startswith(('gender_', 'employment_', 'occupation_', 'education_')) else 0
        
        # Reorder columns to match training data
        input_encoded = input_encoded[self.feature_columns]
        
        # Predict
        prediction = self.model.predict(input_encoded)
        return prediction[0]


class ProductRecommender:
    """
    Association Rules model for recommending products based on 
    frequently bought together patterns
    """
    
    def __init__(self, model_path):
        """Load the association rules model."""
        self.rules = joblib.load(model_path)
    
    def get_recommendations(self, product_skus, metric='lift', top_n=5):
        """
        Get product recommendations based on association rules
        
        Args:
            product_skus (list): List of product SKUs already in cart/viewed
            metric (str): Metric to sort by ('confidence' or 'lift')
            top_n (int): Number of recommendations to return
        
        Returns:
            list: List of recommended product SKUs
        """
        if not product_skus:
            return []
        
        recommendations = set()
        
        for sku in product_skus:
            # Find rules where the SKU is in the antecedents
            matched_rules = self.rules[
                self.rules['antecedents'].apply(lambda x: sku in x)
            ]
            
            # Sort by the specified metric and get top N
            top_rules = matched_rules.sort_values(
                by=metric, 
                ascending=False
            ).head(top_n)
            
            # Extract consequents (recommended items)
            for _, row in top_rules.iterrows():
                recommendations.update(row['consequents'])
        
        # Remove items that are already in the input list
        recommendations.difference_update(product_skus)
        
        return list(recommendations)[:top_n]


# --- Notebook-style helper functions (convenience wrappers) ---
def load_category_model(model_path=None):
    """Load and return the category prediction model (joblib).

    If model_path is None, uses the repo `ml_models/b2c_customers_100.joblib` path.
    """
    if model_path is None:
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'b2c_customers_100.joblib')
    if not os.path.exists(model_path):
        logging.error('Category model not found at %s', model_path)
        raise FileNotFoundError(model_path)
    return joblib.load(model_path)


def predict_preferred_category(model_or_path, customer_data):
    """
    Notebook-style function to predict preferred category.

    Args:
        model_or_path: either a loaded model object (scikit-learn estimator) or a path to a .joblib file
        customer_data: dict with same keys as CategoryPredictor.predict_category expects

    Returns:
        single prediction value (e.g., a string label)
    """
    # load model if path was provided
    model = model_or_path
    if isinstance(model_or_path, str):
        model = load_category_model(model_or_path)

    # Define the expected columns and dtypes (same as in CategoryPredictor)
    columns = {
        'age': 'int64', 'household_size': 'int64', 'has_children': 'int64',
        'monthly_income_sgd': 'float64',
        'gender_Female': 'bool', 'gender_Male': 'bool',
        'employment_status_Full-time': 'bool', 'employment_status_Part-time': 'bool',
        'employment_status_Retired': 'bool', 'employment_status_Self-employed': 'bool',
        'employment_status_Student': 'bool',
        'occupation_Admin': 'bool', 'occupation_Education': 'bool', 'occupation_Sales': 'bool',
        'occupation_Service': 'bool', 'occupation_Skilled Trades': 'bool', 'occupation_Tech': 'bool',
        'education_Bachelor': 'bool', 'education_Diploma': 'bool', 'education_Doctorate': 'bool',
        'education_Master': 'bool', 'education_Secondary': 'bool'
    }

    # Build an empty DataFrame with expected dtypes
    df_template = pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in columns.items()})

    # Prepare customer row and one-hot encode categorical fields
    customer_df = pd.DataFrame([customer_data])
    customer_encoded = pd.get_dummies(
        customer_df, columns=['gender', 'employment_status', 'occupation', 'education']
    )

    # Fill missing columns from template
    for col in df_template.columns:
        if col not in customer_encoded.columns:
            # for bool columns use False, otherwise 0
            if df_template[col].dtype == 'bool':
                customer_encoded[col] = False
            else:
                customer_encoded[col] = 0

    # Reorder to match training
    input_encoded = customer_encoded[df_template.columns]

    # Predict using the provided model
    pred = model.predict(input_encoded)
    return pred[0]


def load_rules_model(model_path=None):
    """Load and return association rules DataFrame saved with joblib.
    Default path is `ml_models/b2c_products_500_transactions_50k.joblib`.
    """
    if model_path is None:
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'b2c_products_500_transactions_50k.joblib')
    if not os.path.exists(model_path):
        logging.error('Rules model not found at %s', model_path)
        raise FileNotFoundError(model_path)
    return joblib.load(model_path)


def get_recommendations(loaded_rules, items, metric='confidence', top_n=5):
    """
    Notebook-style function that mirrors the sample notebook.

    Args:
        loaded_rules: DataFrame of association rules (as in the sample joblib file)
        items: list of item SKUs to base recommendations on
        metric: metric to sort by (e.g., 'confidence' or 'lift')
        top_n: number of recommendations to return

    Returns:
        list of recommended item SKUs
    """
    if loaded_rules is None:
        return []

    recommendations = set()
    for item in items:
        matched_rules = loaded_rules[loaded_rules['antecedents'].apply(lambda x: item in x)]
        top_rules = matched_rules.sort_values(by=metric, ascending=False).head(top_n)
        for _, row in top_rules.iterrows():
            recommendations.update(row['consequents'])

    recommendations.difference_update(items)
    return list(recommendations)[:top_n]


# Singleton instances
_category_predictor = None
_product_recommender = None


def get_category_predictor():
    """Get or create CategoryPredictor singleton"""
    global _category_predictor
    if _category_predictor is None:
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'b2c_customers_100.joblib')
        _category_predictor = CategoryPredictor(model_path)
    return _category_predictor


def get_product_recommender():
    """Get or create ProductRecommender singleton"""
    global _product_recommender
    if _product_recommender is None:
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'b2c_products_500_transactions_50k.joblib')
        _product_recommender = ProductRecommender(model_path)
    return _product_recommender
