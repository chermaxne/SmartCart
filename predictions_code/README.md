# Predictions Code

Simple ML prediction module for AuroraMart with just 2 files!

## Files

### 1. `predict_category.py`
Predicts customer's preferred product category based on demographics.

**Function:**
```python
predict_customer_category(customer) -> str
```
- Takes a Customer model instance
- Returns predicted category name (e.g., 'Skincare', 'Electronics')

### 2. `predict_products.py`
Recommends products using association rules (frequently bought together).

**Functions:**
```python
get_product_recommendations(cart_skus, customer=None, top_n=5) -> list
```
- Recommends products based on cart items
- If customer provided, boosts recommendations matching their predicted category
- Returns list of recommended product SKUs

```python
get_product_recommendations_by_skus(cart_skus, top_n=5) -> list
```
- Recommends products based only on association rules (no personalization)
- Useful for non-authenticated users
- Returns list of recommended product SKUs

## Usage in Views

```python
from predictions_code.predict_category import predict_customer_category
from predictions_code.predict_products import get_product_recommendations

# Predict customer category
category = predict_customer_category(request.user)

# Get personalized recommendations
cart_skus = ['SKU001', 'SKU002']
recommendations = get_product_recommendations(cart_skus, request.user, top_n=5)

# Or for non-authenticated users
recommendations = get_product_recommendations_by_skus(cart_skus, top_n=5)
```

## How It Works

1. **Category Prediction**: Uses Decision Tree Classifier trained on customer demographics
2. **Association Rules**: Finds products frequently bought together using ML model
3. **Hybrid Approach**: Combines both - uses association rules but boosts recommendations matching customer's predicted category

Simple and effective! 🎯
