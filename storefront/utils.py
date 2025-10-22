import joblib
import os
from django.conf import settings

# Decision Tree Model
decision_tree_path = os.path.join(settings.BASE_DIR, 'store', 'ai_models', 'decision_tree.joblib')
try:
    decision_tree_model = joblib.load(decision_tree_path)
except FileNotFoundError:
    decision_tree_model = None  # Skip for now
    print("Warning: decision_tree.joblib not found. Model disabled.")

# Association Rules Model
association_rules_path = os.path.join(settings.BASE_DIR, 'store', 'ai_models', 'association_rules.joblib')
try:
    association_rules_model = joblib.load(association_rules_path)
except FileNotFoundError:
    association_rules_model = None  # Skip for now
    print("Warning: association_rules.joblib not found. Model disabled.")
