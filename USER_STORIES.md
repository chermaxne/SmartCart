# AuroraMart User Stories

**Generated:** 14 November 2025  
**Total Stories:** 42  
**Status Legend:** ✅ Implemented | 🟡 Partially Implemented | ❌ Not Implemented

---

## Table of Contents
1. [Storefront - Product Discovery & Browsing](#storefront---product-discovery--browsing) (7 stories)
2. [Storefront - Shopping Cart & Checkout](#storefront---shopping-cart--checkout) (6 stories)
3. [Storefront - User Account & Authentication](#storefront---user-account--authentication) (5 stories)
4. [Storefront - ML-Powered Personalization](#storefront---ml-powered-personalization) (4 stories)
5. [Admin Panel - Authentication & Dashboard](#admin-panel---authentication--dashboard) (2 stories)
6. [Admin Panel - Product Management](#admin-panel---product-management) (6 stories)
7. [Admin Panel - Category Management](#admin-panel---category-management) (4 stories)
8. [Admin Panel - Customer Management](#admin-panel---customer-management) (2 stories)
9. [Admin Panel - Data Import](#admin-panel---data-import) (2 stories)
10. [Future Features & Enhancements](#future-features--enhancements) (4 stories)

---

## Storefront - Product Discovery & Browsing

### US-001: View Homepage with Featured Products ✅
**As a** visitor  
**I want to** view the homepage with featured and recommended products  
**So that** I can quickly discover items available in the store

**Acceptance Criteria:**
- Homepage displays active products sorted by rating
- Personalized recommendations shown for logged-in users based on predicted category
- Clean, responsive layout with product cards showing image, name, price, and category
- "Welcome back" message for authenticated users

**Implementation:** `storefront/views.home_view`, `storefront/templates/storefront/home.html`

---

### US-002: View Product Detail Page ✅
**As a** shopper  
**I want to** view detailed product information including images, description, price, stock status, and rating  
**So that** I can make informed purchase decisions

**Acceptance Criteria:**
- Product detail page shows full product information
- Displays product image (or placeholder if none)
- Shows current stock status
- Includes product rating and category/subcategory
- Add to Cart and Buy Now buttons available
- Related products section displayed

**Implementation:** `storefront/views.product_detail`, `storefront/templates/storefront/product_detail.html`

---

### US-003: See "Frequently Bought Together" Recommendations ✅
**As a** shopper  
**I want to** see products frequently bought together with the current product  
**So that** I can discover complementary items

**Acceptance Criteria:**
- Related products shown on product detail page
- Uses ML association rules (`get_product_recommendations_by_skus`)
- Falls back to same-category products if ML recommendations unavailable
- Shows up to 4 related products
- Each related product is clickable

**Implementation:** `storefront/views.product_detail`, `predictions_code/predict_products.py`

---

### US-004: Browse Products by Category 🟡
**As a** shopper  
**I want to** browse products filtered by category and subcategory  
**So that** I can find items in specific product types

**Acceptance Criteria:**
- Category browsing interface available
- Products can be filtered by main category
- Subcategory filtering available
- Category breadcrumbs show current location
- Product count shown per category

**Implementation:** Partially - models support categories (`Product.category`, `Product.subcategory`), but dedicated category browse view not implemented in storefront (exists in admin)

---

### US-005: Search for Products ❌
**As a** shopper  
**I want to** search for products by keyword (name, SKU, description)  
**So that** I can quickly find specific items

**Acceptance Criteria:**
- Search bar available in header
- Search returns relevant products matching keywords
- Search covers product name, SKU, and description
- Results page shows matching products with filters

**Implementation:** Not implemented in storefront (search exists in admin panel: `adminpanel/views/product_views.product_list`)

---

### US-006: Filter and Sort Product Lists ❌
**As a** shopper  
**I want to** filter products by price range, rating, availability and sort by various criteria  
**So that** I can narrow down my options

**Acceptance Criteria:**
- Filter options: price range, rating, stock availability
- Sort options: price (low-high, high-low), rating, newest
- Filters apply without full page reload
- Selected filters clearly indicated

**Implementation:** Not implemented in storefront (exists in admin: `adminpanel/views/product_views.product_list`)

---

### US-007: View Product Ratings and Reviews ❌
**As a** shopper  
**I want to** view product ratings and customer reviews  
**So that** I can evaluate product quality

**Acceptance Criteria:**
- Product rating displayed (star rating)
- Customer reviews shown with reviewer name and date
- Ability to sort/filter reviews
- Review helpfulness voting

**Implementation:** Product model has `rating` field, but review system not implemented

---

## Storefront - Shopping Cart & Checkout

### US-008: Add Products to Cart ✅
**As a** shopper  
**I want to** add products to my shopping cart with specified quantities  
**So that** I can prepare my order

**Acceptance Criteria:**
- Add to Cart button on product pages
- Quantity selector available
- Success message shown when item added
- Cart count updates in header
- Session-based cart persists across pages

**Implementation:** `storefront/views.cart_add`, session-based cart in `_cart_dict()`

---

### US-009: View and Manage Shopping Cart ✅
**As a** shopper  
**I want to** view my cart contents and update quantities or remove items  
**So that** I can modify my order before checkout

**Acceptance Criteria:**
- Cart page shows all items with images, names, prices, quantities
- Update quantity for each item
- Remove item button
- Subtotal calculated per item
- Order totals shown (subtotal, shipping, tax, total)
- ML-powered recommendations shown in cart

**Implementation:** `storefront/views.cart_view`, `cart_update`, `cart_remove`, `storefront/templates/storefront/cart.html`

---

### US-010: Apply Promo Code ✅
**As a** shopper  
**I want to** apply promotional codes to receive discounts  
**So that** I can save money on my purchase

**Acceptance Criteria:**
- Promo code input field in cart
- Code validation and discount application
- Discount amount clearly shown
- Total updates when promo applied
- Success/error message for code entry

**Implementation:** `storefront/views.cart_apply_promo` (currently supports hard-coded `SAVE10` for 10% off)

---

### US-011: Proceed to Checkout ✅
**As a** shopper  
**I want to** proceed to checkout with my cart items  
**So that** I can complete my purchase

**Acceptance Criteria:**
- Checkout page displays order summary
- Shipping cost, tax, and total calculated
- Promo discount applied if valid
- ML recommendations shown at checkout
- Clear call-to-action to place order

**Implementation:** `storefront/views.checkout`, `storefront/templates/storefront/checkout.html`

---

### US-012: Buy Now (Quick Checkout) ✅
**As a** shopper  
**I want to** buy a product immediately without browsing my cart  
**So that** I can complete purchases quickly

**Acceptance Criteria:**
- "Buy Now" button on product pages
- Adds product to cart and goes directly to checkout
- Quantity selection available
- Success message shown

**Implementation:** `storefront/views.buy_now`

---

### US-013: Complete Order ❌
**As a** shopper  
**I want to** submit my order and receive confirmation  
**So that** I can finalize my purchase and track it

**Acceptance Criteria:**
- Order submission creates Order and OrderItem records
- Stock quantities reduced
- Order confirmation page with order number
- Confirmation email sent
- Cart cleared after order placed

**Implementation:** Partially - checkout POST clears cart and shows success, but doesn't persist Order/OrderItem to database or reduce stock

---

## Storefront - User Account & Authentication

### US-014: Register for Account ✅
**As a** new visitor  
**I want to** create an account with my personal and demographic information  
**So that** I can receive personalized recommendations

**Acceptance Criteria:**
- Registration form with username, email, password
- Extended profile form for demographics (age, gender, employment, education, income, household)
- Form validation and error messages
- ML category prediction on registration
- Auto-login after successful registration
- Welcome message with predicted category

**Implementation:** `storefront/views.register`, `storefront/forms.UserRegisterForm`, `CustomerForm`, `predictions_code/predict_category.py`

---

### US-015: Login to Account ✅
**As a** registered user  
**I want to** log in with my credentials  
**So that** I can access personalized features

**Acceptance Criteria:**
- Login form with username/email and password
- "Remember me" option for extended session
- Success message on login
- Error message for invalid credentials
- Redirect to homepage after login

**Implementation:** `storefront/views.login`, `storefront/templates/storefront/login.html`

---

### US-016: Logout from Account ✅
**As a** logged-in user  
**I want to** log out securely  
**So that** my account is protected

**Acceptance Criteria:**
- Logout option in navigation
- Session cleared on logout
- Success message shown
- Redirect to homepage

**Implementation:** `storefront/views.logout_view`

---

### US-017: View Order History ❌
**As a** registered customer  
**I want to** view my past orders and their details  
**So that** I can track my purchase history

**Acceptance Criteria:**
- Order history page lists all orders
- Shows order number, date, total, status
- Click to view order details
- Order details show items, quantities, prices
- Reorder button available

**Implementation:** Not implemented (Order model exists but order creation not wired)

---

### US-018: Manage Profile and Settings ❌
**As a** registered user  
**I want to** update my profile information and preferences  
**So that** I can keep my account current

**Acceptance Criteria:**
- Profile edit form
- Update demographic information
- Change password option
- Save changes with validation
- Success confirmation

**Implementation:** Not implemented

---

## Storefront - ML-Powered Personalization

### US-019: Receive Category Predictions Based on Demographics ✅
**As a** new registered user  
**I want to** receive product category recommendations based on my demographic profile  
**So that** I see relevant products immediately

**Acceptance Criteria:**
- ML model predicts preferred category on registration
- Prediction based on age, gender, income, employment, education, household
- Predicted category displayed on homepage
- Category saved to user profile
- Fallback to default if prediction fails

**Implementation:** `predictions_code/predict_category.predict_customer_category`, uses decision tree model in `ml_models/b2c_customers_100.joblib`

---

### US-020: See Personalized Homepage Recommendations ✅
**As a** logged-in user  
**I want to** see personalized product recommendations on the homepage  
**So that** I discover products matching my preferences

**Acceptance Criteria:**
- Homepage shows "Recommended for You" section
- Recommendations based on predicted category
- Shows up to 4 recommended products
- Products from predicted category prioritized
- Falls back to top-rated products if category unavailable

**Implementation:** `storefront/views.home_view`, filters products by predicted category

---

### US-021: Receive Cart-Based Recommendations ✅
**As a** shopper with items in cart  
**I want to** see product recommendations based on my cart contents  
**So that** I can discover complementary items

**Acceptance Criteria:**
- Recommendations shown on cart page
- Uses association rules based on cart SKUs
- For logged-in users, combines cart + customer profile
- Shows up to 6 recommendations
- Excludes items already in cart

**Implementation:** `storefront/views.cart_view`, uses `predictions_code/predict_products.get_product_recommendations`

---

### US-022: See Checkout Page Recommendations ✅
**As a** shopper at checkout  
**I want to** see last-minute product recommendations  
**So that** I can add complementary items before completing purchase

**Acceptance Criteria:**
- Recommendations shown at checkout
- Based on cart items using association rules
- Up to 4 recommendations displayed
- Quick add to cart option
- Doesn't disrupt checkout flow

**Implementation:** `storefront/views.checkout`, uses ML recommendations

---

## Admin Panel - Authentication & Dashboard

### US-023: Admin Login with Staff Verification ✅
**As an** admin user  
**I want to** log in securely with staff-only access  
**So that** I can manage the store

**Acceptance Criteria:**
- Admin login page separate from storefront
- Username/password authentication
- Staff-only access (is_staff check)
- Remember me option
- Redirect to dashboard on success
- Error for non-staff users

**Implementation:** `adminpanel/views/auth_views.admin_login`, decorator `is_staff_user`

---

### US-024: View Admin Dashboard with Store Metrics ✅
**As an** admin  
**I want to** see key store metrics on my dashboard  
**So that** I can monitor store health at a glance

**Acceptance Criteria:**
- Dashboard shows total products, customers, categories
- Low stock count prominently displayed
- List of low stock products (top 5)
- Category distribution with product counts
- Top 5 categories by product count
- Clean, organized layout

**Implementation:** `adminpanel/views/dashboard_views.dashboard`, `adminpanel/templates/adminpanel/dashboard.html`

---

## Admin Panel - Product Management

### US-025: View Product List with Search and Filters ✅
**As an** admin  
**I want to** view all products with search, category filter, and sorting  
**So that** I can find and manage products efficiently

**Acceptance Criteria:**
- Paginated product list (20 per page)
- Search by name, SKU, or description
- Filter by category
- Sort options (name, price, stock, date)
- Product count shown
- Quick links to edit/view each product

**Implementation:** `adminpanel/views/product_views.product_list`, `adminpanel/templates/adminpanel/product/product_list.html`

---

### US-026: Add New Product ✅
**As an** admin  
**I want to** add new products with all details and images  
**So that** I can expand the catalog

**Acceptance Criteria:**
- Product form with all fields (SKU, name, description, category, subcategory, price, stock, reorder threshold, rating, image, active status)
- Form validation
- Image upload support
- Success message on creation
- Redirect to product detail after creation

**Implementation:** `adminpanel/views/product_views.product_add`, `adminpanel/forms.ProductForm`

---

### US-027: Edit Product Details ✅
**As an** admin  
**I want to** edit existing product information  
**So that** I can keep product data current

**Acceptance Criteria:**
- Edit form pre-populated with current data
- All fields editable
- Image replacement option
- Validation on save
- Success message
- Redirect to product detail

**Implementation:** `adminpanel/views/product_views.product_edit`

---

### US-028: View Product Details ✅
**As an** admin  
**I want to** view complete product information and stock history  
**So that** I can review product status

**Acceptance Criteria:**
- Product detail page shows all information
- Stock history section (placeholder currently)
- Low stock indicator
- Edit and delete action buttons
- Breadcrumb navigation

**Implementation:** `adminpanel/views/product_views.product_detail`, stock history currently stubbed

---

### US-029: Soft Delete (Deactivate) Products ✅
**As an** admin  
**I want to** deactivate products instead of deleting them  
**So that** I preserve historical data while removing from storefront

**Acceptance Criteria:**
- Delete action sets is_active=False
- Product remains in database
- Removed from storefront listings
- Can be reactivated by editing
- Success confirmation message

**Implementation:** `adminpanel/views/product_views.product_delete`

---

### US-030: View Low Stock Products ✅
**As an** admin  
**I want to** see all products below reorder threshold  
**So that** I can replenish inventory proactively

**Acceptance Criteria:**
- List of products where stock ≤ reorder_threshold
- Filter by category
- Sort options
- Shows current stock and reorder threshold
- Quick link to edit product

**Implementation:** `adminpanel/views/product_views.low_stock`, `adminpanel/templates/adminpanel/product/low_stock.html`

---

## Admin Panel - Category Management

### US-031: View Category List with Statistics ✅
**As an** admin  
**I want to** view all categories with product counts and statistics  
**So that** I can understand category distribution

**Acceptance Criteria:**
- List of all categories
- Product count per category (active products only)
- Total stock per category
- Average price per category
- Average rating per category
- Links to category detail and edit

**Implementation:** `adminpanel/views/category_views.category_list`

---

### US-032: View Category Details ✅
**As an** admin  
**I want to** view detailed category information and associated products  
**So that** I can manage category content

**Acceptance Criteria:**
- Category detail page shows description
- Statistics: total products, total stock, avg price, avg rating
- Low stock product count
- List of all products in category
- Edit and delete options

**Implementation:** `adminpanel/views/category_views.category_detail`

---

### US-033: Add New Category ✅
**As an** admin  
**I want to** create new product categories  
**So that** I can organize the catalog

**Acceptance Criteria:**
- Category form with name and description
- Duplicate name validation
- Success message
- Redirect to category list

**Implementation:** `adminpanel/views/category_views.category_add`

---

### US-034: Edit and Delete Categories ✅
**As an** admin  
**I want to** edit category names/descriptions and delete empty categories  
**So that** I can maintain clean taxonomy

**Acceptance Criteria:**
- Edit form for category
- Duplicate name validation on edit
- Delete prevented if category has active products
- Success/error messages
- Redirect to category list

**Implementation:** `adminpanel/views/category_views.category_edit`, `category_delete`

---

## Admin Panel - Customer Management

### US-035: View Customer List ✅
**As an** admin  
**I want to** view all registered customers with pagination  
**So that** I can manage user accounts

**Acceptance Criteria:**
- Paginated customer list (20 per page)
- Shows username, email, registration date
- Sort options
- Filter for active customers only
- Link to customer detail

**Implementation:** `adminpanel/views/customer_views.customer_list`

---

### US-036: View Customer Details ✅
**As an** admin  
**I want to** view detailed customer profile information  
**So that** I can support customers and understand demographics

**Acceptance Criteria:**
- Customer detail page shows all profile data
- Demographics: age, gender, employment, education, income, household
- Preferred category
- Registration date and status
- Order history (when implemented)

**Implementation:** `adminpanel/views/customer_views.customer_detail`

---

## Admin Panel - Data Import

### US-037: Import Products from CSV ✅
**As an** admin  
**I want to** bulk import products from CSV files  
**So that** I can quickly populate the catalog

**Acceptance Criteria:**
- CSV file upload
- Maps CSV columns to product fields
- Creates or updates products based on SKU
- Handles categories (creates if not exists)
- Reports created/updated/skipped counts
- Error handling for invalid data

**Implementation:** `storefront/import_products.py` (script-based, not UI-integrated)

---

### US-038: Import Customers from CSV ✅
**As an** admin  
**I want to** bulk import customer data from CSV  
**So that** I can migrate existing customer base

**Acceptance Criteria:**
- CSV file upload
- Creates customer accounts with demographics
- Generates unique usernames
- Sets preferred category based on data
- Reports created/skipped counts
- Error handling

**Implementation:** `storefront/import_customers.py` (script-based, not UI-integrated)

---

## Future Features & Enhancements

### US-039: Payment Gateway Integration ❌
**As a** customer  
**I want to** pay securely using credit card or digital wallets  
**So that** I can complete real purchases

**Acceptance Criteria:**
- Stripe/PayPal integration
- Secure card tokenization
- Payment success/failure handling
- Order status update on payment
- PCI compliance maintained

**Implementation:** Not implemented

---

### US-040: Order Management and Fulfillment ❌
**As an** admin  
**I want to** view, process, and fulfill customer orders  
**So that** I can deliver products to customers

**Acceptance Criteria:**
- Order list with status filters
- Order detail view with line items
- Status transitions (pending → processing → shipped → delivered)
- Shipping label generation
- Tracking number entry
- Email notifications on status change

**Implementation:** Not implemented (Order models exist but no admin workflow)

---

### US-041: Wishlist/Save for Later ❌
**As a** shopper  
**I want to** save products to a wishlist  
**So that** I can purchase them later

**Acceptance Criteria:**
- Add/remove from wishlist
- Wishlist page shows saved items
- Move to cart option
- Persisted to user account
- Share wishlist option

**Implementation:** Not implemented

---

### US-042: Product Reviews and Ratings ❌
**As a** customer  
**I want to** write reviews and rate products I've purchased  
**So that** I can help other shoppers make decisions

**Acceptance Criteria:**
- Review form on product page
- Star rating (1-5)
- Review text and title
- Verified purchase badge
- Review moderation by admin
- Helpfulness voting

**Implementation:** Not implemented (rating field exists but no review model/system)

---

## Summary Statistics

**By Implementation Status:**
- ✅ Fully Implemented: 28 stories (67%)
- 🟡 Partially Implemented: 4 stories (9%)
- ❌ Not Implemented: 10 stories (24%)

**By Epic:**
- Storefront Product Discovery: 4/7 implemented
- Storefront Cart & Checkout: 5/6 implemented
- Storefront Authentication: 3/5 implemented
- Storefront ML Features: 4/4 implemented
- Admin Authentication: 2/2 implemented
- Admin Product Management: 6/6 implemented
- Admin Category Management: 4/4 implemented
- Admin Customer Management: 2/2 implemented
- Admin Data Import: 2/2 implemented
- Future Features: 0/4 implemented

---

## Priority Recommendations for Next Sprint

**High Priority (MVP Completion):**
1. US-013: Complete Order Persistence - Wire checkout to create Order/OrderItem records and reduce stock
2. US-005: Product Search - Implement storefront search functionality
3. US-040: Basic Order Management - Admin order list and detail views
4. US-039: Payment Integration - Stripe checkout integration

**Medium Priority (Enhanced UX):**
5. US-004: Category Browsing - Dedicated category browse pages
6. US-017: Order History - Customer order history page
7. US-018: Profile Management - Edit profile functionality
8. US-006: Product Filters - Enhanced filtering and sorting

**Nice to Have:**
9. US-041: Wishlist - Save for later functionality
10. US-042: Reviews - Product review system

---

**End of User Stories Document**
