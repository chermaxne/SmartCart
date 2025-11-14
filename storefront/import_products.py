import csv
from decimal import Decimal, InvalidOperation
from django.db import transaction, IntegrityError
from storefront.models import Product, Category

csv_path = '/Users/chermaine/Downloads/SmartCart/proj info/data/b2c_products_500.csv'

def open_csv_with_fallback(path):
    encodings = ('utf-8-sig', 'utf-8', 'cp1252', 'latin-1')
    for enc in encodings:
        try:
            fh = open(path, newline='', encoding=enc)
            fh.readline()          # force decode to detect errors
            fh.seek(0)
            return fh, enc
        except UnicodeDecodeError:
            continue
    # last-resort: open with replacement to avoid crash
    fh = open(path, newline='', encoding='latin-1', errors='replace')
    return fh, 'latin-1 (replace)'

created = 0
updated = 0
skipped = 0

def to_int(val, default=0):
    try:
        return int(float(val)) if val not in (None, '') else default
    except (ValueError, TypeError):
        return default

def to_decimal(val, default=Decimal('0.00')):
    try:
        if val in (None, ''):
            return default
        return Decimal(str(val)).quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError, TypeError):
        return default

def to_float(val, default=0.0):
    try:
        return float(val) if val not in (None, '') else default
    except (ValueError, TypeError):
        return default

fh, used_enc = open_csv_with_fallback(csv_path)
print(f"Opening CSV with encoding: {used_enc}")

with fh:
    reader = csv.DictReader(fh)
    with transaction.atomic():
        for row in reader:
            sku = (row.get('SKU code') or row.get('SKU') or '').strip()
            name = (row.get('Product name') or row.get('name') or '').strip()
            description = (row.get('Product description') or '').strip()
            category_name = (row.get('Product Category') or '').strip()
            subcategory = (row.get('Product Subcategory') or '').strip()

            if not sku or not name:
                skipped += 1
                continue

            # Use only category name without subcategory
            cat_name = category_name or "Uncategorized"
            category, _ = Category.objects.get_or_create(name=cat_name)

            stock = to_int(row.get('Quantity on hand'))
            reorder = to_int(row.get('Reorder Quantity'))
            price = to_decimal(row.get('Unit price'))
            rating = to_float(row.get('Product rating'))

            defaults = {
                'name': name,
                'description': description,
                'category': category,
                'subcategory': subcategory,  # Store subcategory separately
                'price': price,
                'rating': rating,
                'stock': stock,
                'reorder_threshold': reorder,
            }

            try:
                obj, created_flag = Product.objects.update_or_create(sku=sku, defaults=defaults)
                if created_flag:
                    created += 1
                else:
                    updated += 1
            except IntegrityError:
                skipped += 1
                continue

print(f"Products import finished — created={created}, updated={updated}, skipped={skipped}")