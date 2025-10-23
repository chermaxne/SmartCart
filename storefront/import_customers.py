import csv
from django.db import IntegrityError, transaction
from storefront.models import Customer, Category

csv_path = '/Users/chermaine/Downloads/SmartCart/proj info/data/b2c_customers_100.csv'

def make_unique_username(base):
    base = base.lower()
    candidate = base
    i = 1
    while Customer.objects.filter(username=candidate).exists():
        candidate = f"{base}{i}"
        i += 1
    return candidate

created = 0
skipped = 0
updated = 0

with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        age = int(row['age']) if row.get('age') else None
        household_size = int(row['household_size']) if row.get('household_size') else 0
        has_children = row.get('has_children', '').strip() in ['1', 'True', 'true']
        monthly_income = float(row['monthly_income_sgd']) if row.get('monthly_income_sgd') else 0.0

        category_name = row.get('preferred_category', '').strip() or 'Other'
        category, _ = Category.objects.get_or_create(name=category_name)

        occupation_raw = (row.get('occupation') or "user").strip().replace(" ", "")
        base_username = (occupation_raw[:10] + (str(age) if age else ""))[:30] or "user"
        username = make_unique_username(base_username)

        email_local = occupation_raw[:10].lower() + (str(age) if age else "")
        email = f"{email_local}@example.com"

        # Build profile fields only (don't pass username/email to Customer.create -> use create_user)
        profile_fields = {
            'age': age,
            'gender': (row.get('gender') or '').strip(),
            'employment_status': (row.get('employment_status') or '').strip(),
            'occupation': (row.get('occupation') or '').strip(),
            'education': (row.get('education') or '').strip(),
            'household_size': household_size,
            'has_children': has_children,
            'monthly_income_sgd': monthly_income,
            'preferred_category': category,
        }

        try:
            with transaction.atomic():
                # create_user will set an unusable password if password is None
                user = Customer.objects.create_user(username=username, email=email, password=None)
                for k, v in profile_fields.items():
                    if hasattr(user, k):
                        setattr(user, k, v)
                user.save()
                created += 1
        except IntegrityError:
            # this should not normally happen because make_unique_username checks existence,
            # but handle it defensively
            skipped += 1
            continue

print(f"✅ CSV import completed: created={created}, skipped={skipped}, updated={updated}")
