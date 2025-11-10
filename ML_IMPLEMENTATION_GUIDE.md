# SmartCart ML Implementation Guide

## Overview
SmartCart uses two AI models to provide personalized shopping recommendations:
1. **Decision Tree Classifier** - Predicts preferred product categories based on customer demographics
2. **Association Rules Mining** - Recommends products frequently bought together

---

## 🚀 Quick Start

### Installation
```bash
# Activate virtual environment
source venv/bin/activate

# Install ML dependencies
pip install joblib pandas scikit-learn mlxtend
```

### Test Models
```bash
python test_ml_models.py
```
Expected output:
- ✓ CategoryPredictor PASS
- ✓ ProductRecommender PASS

---

## 📊 Model 1: Decision Tree Classifier

### Purpose
Predicts which product category a customer is most likely to purchase based on their demographic profile.

### Input Features
- **age**: Customer age (integer)
- **gender**: "Male" or "Female"
- **employment_status**: "Full-time", "Part-time", "Unemployed", "Self-employed"
- **occupation**: "Tech", "Healthcare", "Education", "Business", "Service", "Other"
- **education**: "High School", "Bachelor", "Master", "PhD"
- **household_size**: Number of people in household (integer)
- **has_children**: 1 if has children, 0 otherwise
- **monthly_income_sgd**: Monthly income in SGD (float)

### Output
Predicted category name (e.g., "Electronics", "Groceries", "Beauty")

### Usage Example
```python
from storefront.ml_utils import get_category_predictor

predictor = get_category_predictor()
customer_data = {
    'age': 28,
    'household_size': 2,
    'has_children': 0,
    'monthly_income_sgd': 6000.0,
    'gender': 'Female',
    'employment_status': 'Full-time',
    'occupation': 'Tech',
    'education': 'Bachelor'
}
category = predictor.predict_category(customer_data)
print(f"Predicted: {category}")  # e.g., "Electronics"
```

### Model File
`ml_models/b2c_customers_100.joblib`

### Training Data
- 100 synthetic B2C customers
- Demographics + purchase history
- Located in `proj info/data/b2c_customers_100.csv`

---

## 🛒 Model 2: Association Rules Mining

### Purpose
Discovers "frequently bought together" patterns from transaction data to recommend complementary products.

### Input
List of product SKUs currently in cart (e.g., `['BPM-JRNJ6225', 'HKS&-8KCMM7DB']`)

### Output
List of recommended product SKUs based on association rules

### Parameters
- **metric**: 'lift', 'confidence', or 'support' (default: 'lift')
- **top_n**: Number of recommendations to return (default: 5)

### Usage Example
```python
from storefront.ml_utils import get_product_recommender

recommender = get_product_recommender()
cart_skus = ['BPM-JRNJ6225', 'HKS&-8KCMM7DB']
recommendations = recommender.get_recommendations(
    cart_skus, 
    metric='lift', 
    top_n=8
)
print(f"Recommended: {recommendations}")
```

### Model File
`ml_models/b2c_products_500_transactions_50k.joblib`

### Training Data
- 500 products
- 50,000 synthetic transactions
- Located in `proj info/data/b2c_products_500_transactions_50k.csv`

---

## 📁 File Structure

```
SmartCart/
├── ml_models/
│   ├── b2c_customers_100.joblib                      # Decision Tree model
│   ├── b2c_products_500_transactions_50k.joblib      # Association Rules model
│   ├── decision_tree_classifier.ipynb                # Training notebook
│   └── association_rules_mining.ipynb                # Training notebook
├── storefront/
│   ├── ml_utils.py                                   # Model loading utilities
│   └── views.py                                      # ML insights view + cart functions
├── proj info/data/
│   ├── b2c_customers_100.csv                         # Training data
│   ├── b2c_products_500_transactions_50k.csv         # Transaction data
│   └── b2c_products_500.csv                          # Product catalog
└── test_ml_models.py                                 # Model validation tests
```

---

## 🔧 Implementation Details

### ML Utilities (`storefront/ml_utils.py`)
```python
def get_category_predictor():
    """Lazy-load Decision Tree model"""
    return CategoryPredictor('ml_models/b2c_customers_100.joblib')

def get_product_recommender():
    """Lazy-load Association Rules model"""
    return ProductRecommender('ml_models/b2c_products_500_transactions_50k.joblib')
```

### ML Insights View (`storefront/views.py`)
```python
def ml_insights(request):
    insights = {}
    
    # Category prediction (authenticated users only)
    if request.user.is_authenticated and hasattr(request.user, 'customer'):
        predictor = get_category_predictor()
        customer_data = {...}  # Extract from user profile
        predicted_category = predictor.predict_category(customer_data)
        insights['predicted_category'] = predicted_category
        insights['category_products'] = Product.objects.filter(category=...)
    
    # Association rules (works for everyone with cart items)
    recommender = get_product_recommender()
    cart = request.session.get('cart', {})
    if cart:
        cart_skus = [Product.objects.get(id=pid).sku for pid in cart.keys()]
        recommended_skus = recommender.get_recommendations(cart_skus)
        insights['association_recommendations'] = Product.objects.filter(sku__in=recommended_skus)
    
    return render(request, 'storefront/ml_insights.html', {'insights': insights})
```

### Cart System
- **Storage**: Session-based (`request.session['cart']`)
- **Format**: `{product_id: quantity}` (e.g., `{'499': 3, '500': 2}`)
- **Context Processor**: `cart_count()` in `views.py` makes cart count available globally

---

## 🧪 Testing

### Run Tests
```bash
python test_ml_models.py
```

### Test Output
```
Testing CategoryPredictor...
Customer profile: age=35, occupation=Tech worker
Predicted category: Electronics
✓ CategoryPredictor PASS

Testing ProductRecommender...
Cart items: ['BPM-ABC123', 'HKS&-XYZ789']
Recommended products (5): ['HKC-1IYM90PK', 'HKB-LDALMJEG', ...]
✓ ProductRecommender PASS
```

---

## 🎨 Frontend Integration

### ML Insights Page
**URL**: `/storefront/ml-insights/`

**Template**: `storefront/templates/storefront/ml_insights.html`

**Sections**:
1. **Category Prediction** (purple box) - Shows only for logged-in users
   - Predicted category based on profile
   - 8 recommended products from that category

2. **Frequently Bought Together** (green box) - Shows for everyone with cart
   - Current cart items
   - AI-recommended complementary products

3. **Empty Cart Message** (yellow box) - Shows when cart is empty
   - Prompts user to add items

4. **Model Information** (gray box) - Educational section
   - Explains how each AI model works

---

## 🚨 Debugging

### Check if models are loaded
```python
python manage.py shell
>>> from storefront.ml_utils import get_category_predictor, get_product_recommender
>>> predictor = get_category_predictor()
>>> recommender = get_product_recommender()
>>> print("Models loaded successfully!")
```

### View debug logs
When you visit `/storefront/ml-insights/`, check terminal for:
```
DEBUG: Cart contents: {'500': 2, '499': 3}
DEBUG: Cart SKUs: ['BPM-JRNJ6225', 'HKS&-8KCMM7DB']
DEBUG: Recommended SKUs: ['HKC-1IYM90PK', ...]
DEBUG: Found 7 recommendations
```

### Common Issues
❌ **Models not found**: Check `ml_models/` directory has `.joblib` files
❌ **No recommendations**: Ensure cart has items with valid SKUs
❌ **Import errors**: Run `pip install joblib pandas scikit-learn mlxtend`

---

## 📈 Future Enhancements

- [ ] Real-time model retraining with new transaction data
- [ ] A/B testing different recommendation algorithms
- [ ] Personalized pricing based on customer segments
- [ ] Seasonal product recommendations
- [ ] Collaborative filtering (user-user similarity)

---

## 📝 Notes

- Models are **lazy-loaded** - only loaded when first accessed (improves startup time)
- Association rules work **without authentication** - great for guest shoppers
- Category prediction requires **complete customer profile** (all demographic fields)
- Recommendations are cached in memory for better performance
- Cart uses **Django sessions** - no database queries needed for cart operations

---

**Built with**: Django 5.2.7, Python 3.13.6, scikit-learn, mlxtend
**Last Updated**: November 10, 2025
