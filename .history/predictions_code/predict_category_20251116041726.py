"""
Customer Category Prediction
Predicts customer's preferred product category based on demographics
"""
import joblib
import pandas as pd
import os
from django.conf import settings


def predict_customer_category(customer):
    """
    Predict preferred category for a customer
    
    Args:
        customer: Customer model instance with demographic fields
    
    Returns:
        str: Predicted category name (e.g., 'Skincare', 'Electronics')
    """
    try:
        # Load the model
        model_path = os.path.join(settings.BASE_DIR, 'AuroraMartProj', 'ml_models', 'b2c_customers_100.joblib')
        model = joblib.load(model_path)
        
        # Prepare customer data
        customer_data = {
            'age': customer.age or 30,
            'household_size': customer.household_size or 2,
            'has_children': 1 if customer.has_children else 0,
            'monthly_income_sgd': float(customer.monthly_income_sgd or 5000),
            'gender': customer.gender or 'Male',
            'employment_status': customer.employment_status or 'Full-time',
            'occupation': customer.occupation or 'Tech',
            'education': customer.education or 'Bachelor',
        }
        
        # Convert to DataFrame and one-hot encode
        input_df = pd.DataFrame([customer_data])
        input_encoded = pd.get_dummies(
            input_df, 
            columns=['gender', 'employment_status', 'occupation', 'education']
        )
        
        # Expected feature columns
        feature_columns = [
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
        
        # Add missing columns
        for col in feature_columns:
            if col not in input_encoded.columns:
                input_encoded[col] = False if col.startswith(
                    ('gender_', 'employment_', 'occupation_', 'education_')
                ) else 0
        
        # Reorder columns
        input_encoded = input_encoded[feature_columns]
        
        # Predict
        prediction = model.predict(input_encoded)
        return prediction[0]
        
    except Exception as e:
        print(f"Category prediction error: {e}")
        return None
