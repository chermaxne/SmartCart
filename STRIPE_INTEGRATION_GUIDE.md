# Stripe Payment Integration Guide

## What is Stripe?
Stripe is a payment processing platform that allows you to accept real payments online. It's widely used by e-commerce sites and is considered one of the most developer-friendly payment solutions.

## Why Use Stripe?
- **Secure**: PCI-compliant, handles sensitive card data securely
- **Real Payments**: Accept actual credit/debit card payments
- **Multiple Methods**: Supports cards, Apple Pay, Google Pay, and more
- **International**: Supports 135+ currencies
- **Developer-Friendly**: Excellent documentation and APIs

## Current Implementation (Mock Payment)
Your current checkout page uses a **mock payment interface** that:
- ✅ Looks realistic with multiple payment methods
- ✅ Shows payment UI (card fields, PayNow QR, etc.)
- ❌ Does NOT process real payments
- ❌ Does NOT charge credit cards
- ❌ Does NOT handle actual money transfers

This is **perfect for academic projects** where you want to demonstrate the UX without dealing with real money.

## If You Want to Add Real Stripe Integration

### Step 1: Install Stripe
```bash
pip install stripe
```

### Step 2: Get Stripe API Keys
1. Sign up at https://stripe.com
2. Get your API keys (Publishable Key & Secret Key)
3. Use **test mode** keys for development (they start with `pk_test_` and `sk_test_`)

### Step 3: Add to settings.py
```python
# AuroraMartProj/settings.py
STRIPE_PUBLIC_KEY = 'pk_test_your_key_here'
STRIPE_SECRET_KEY = 'sk_test_your_key_here'
```

### Step 4: Update checkout view
```python
# storefront/views.py
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    if request.method == 'POST':
        # Create a Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),  # Amount in cents
            currency='sgd',
            payment_method_types=['card'],
        )
        
        # Pass client_secret to template
        context = {
            'client_secret': intent.client_secret,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        }
        return render(request, 'checkout.html', context)
```

### Step 5: Add Stripe.js to checkout.html
```html
<!-- Add in <head> section -->
<script src="https://js.stripe.com/v3/"></script>

<!-- JavaScript to handle payment -->
<script>
const stripe = Stripe('{{ stripe_public_key }}');
const clientSecret = '{{ client_secret }}';

// When user submits payment
const {error, paymentIntent} = await stripe.confirmCardPayment(clientSecret, {
  payment_method: {
    card: cardElement,
    billing_details: {
      name: 'Customer Name'
    }
  }
});

if (error) {
  // Show error
} else if (paymentIntent.status === 'succeeded') {
  // Payment successful!
}
</script>
```

## For Your Project
**RECOMMENDATION**: Keep your current mock implementation because:
1. ✅ No need for real bank account setup
2. ✅ No risk of accidental charges
3. ✅ Demonstrates understanding of payment UX
4. ✅ Faster development (no API setup needed)
5. ✅ Looks professional and realistic

If your professor specifically requires Stripe:
- Use **Stripe Test Mode** (no real money)
- Use test card numbers like `4242 4242 4242 4242`
- Mention in your documentation: "Stripe integration in test mode"

## Testing Stripe (Test Mode)
If you do integrate Stripe, use these test cards:
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **3D Secure**: `4000 0025 0000 3155`
- Use any future expiry date, any CVV

## Resources
- Stripe Docs: https://stripe.com/docs
- Stripe Python Library: https://stripe.com/docs/api/python
- Test Cards: https://stripe.com/docs/testing

## Note
Your current implementation is **excellent for a student project**. It demonstrates:
- Understanding of different payment methods
- Clean UX design
- Proper form validation
- Realistic checkout flow

Only add Stripe if your professor specifically requires real payment processing.
