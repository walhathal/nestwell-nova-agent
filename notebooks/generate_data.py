"""
generate_data.py
Generates a realistic Olist-style synthetic dataset scoped to Nestwell's use case.
Produces 3 CSVs: nestwell_orders.csv, nestwell_order_items.csv, nestwell_customers.csv

Key decisions (per our status update):
- Portuguese product names replaced with English equivalents
- Agent scoped to order-ID lookups only
- Fixed reference date 2024-01-01 so statuses / delivery dates stay consistent
"""
import pandas as pd
import numpy as np
import random
import uuid
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

N_CUSTOMERS    = 300
N_ORDERS       = 800
REFERENCE_DATE = datetime(2024, 1, 1)

STATUSES = ["delivered", "shipped", "processing", "canceled", "invoiced"]
WEIGHTS  = [0.62, 0.20, 0.09, 0.06, 0.03]

CATEGORIES = [
    "Home Appliances", "Kitchen Accessories", "Bed & Bath",
    "Furniture & Decor", "Garden Tools", "Office Furniture",
    "Sports & Leisure", "Electronics"
]

PRODUCT_NAMES = {
    "Home Appliances":     ["Cordless Vacuum", "Air Purifier", "Electric Kettle", "Robot Vacuum"],
    "Kitchen Accessories": ["Chef Knife Set", "Cutting Board", "Cast Iron Pan", "Mixing Bowls"],
    "Bed & Bath":          ["Cotton Duvet", "Memory Foam Pillow", "Bamboo Towels", "Weighted Blanket"],
    "Furniture & Decor":   ["Side Table", "Floor Lamp", "Bookshelf", "Wall Mirror"],
    "Garden Tools":        ["Pruning Shears", "Garden Hose", "Planter Pot", "Soil Meter"],
    "Office Furniture":    ["Ergonomic Chair", "Standing Desk", "Monitor Riser", "Desk Organizer"],
    "Sports & Leisure":    ["Yoga Mat", "Resistance Bands", "Water Bottle", "Foam Roller"],
    "Electronics":         ["Smart Plug", "LED Desk Lamp", "Wireless Charger", "Bluetooth Speaker"],
}

CITIES = [
    ("San Diego", "CA"), ("Los Angeles", "CA"), ("Austin", "TX"),
    ("Denver", "CO"),    ("Chicago", "IL"),     ("New York", "NY"),
    ("Seattle", "WA"),   ("Boston", "MA"),      ("Miami", "FL"),  ("Phoenix", "AZ"),
]

FIRST = ["James","Maria","David","Sarah","Robert","Emily","Michael","Ashley",
         "William","Jessica","John","Amanda","Thomas","Melissa","Carlos","Priya"]
LAST  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
         "Rodriguez","Martinez","Wilson","Anderson","Taylor","Nguyen","Patel","Lee"]

def rand_date(start, end):
    delta = (end - start).total_seconds()
    return start + timedelta(seconds=random.randint(0, int(delta)))

start_date = REFERENCE_DATE - timedelta(days=365)
end_date   = REFERENCE_DATE - timedelta(days=1)

# ── CUSTOMERS ──────────────────────────────────────────────────────────────────
customers = []
for _ in range(N_CUSTOMERS):
    city, state = random.choice(CITIES)
    customers.append({
        "customer_id":       str(uuid.uuid4())[:8].upper(),
        "customer_name":     f"{random.choice(FIRST)} {random.choice(LAST)}",
        "customer_email":    f"customer{random.randint(1000,9999)}@example.com",
        "customer_city":     city,
        "customer_state":    state,
        "customer_zip_code": str(random.randint(10000, 99999)),
    })
df_customers = pd.DataFrame(customers)

# ── ORDERS ─────────────────────────────────────────────────────────────────────
orders = []
for i in range(N_ORDERS):
    cust     = random.choice(customers)
    purchase = rand_date(start_date, end_date)
    status   = random.choices(STATUSES, WEIGHTS)[0]

    if status == "delivered":
        approved  = purchase + timedelta(hours=random.randint(1, 4))
        shipped   = approved + timedelta(days=random.randint(1, 3))
        delivered = shipped  + timedelta(days=random.randint(2, 8))
        est_deliv = shipped  + timedelta(days=random.randint(3, 10))
    elif status == "shipped":
        approved  = purchase + timedelta(hours=random.randint(1, 4))
        shipped   = approved + timedelta(days=random.randint(1, 2))
        delivered = None
        est_deliv = shipped  + timedelta(days=random.randint(3, 10))
    elif status == "canceled":
        approved  = None
        shipped   = None
        delivered = None
        est_deliv = None
    else:  # processing / invoiced
        approved  = purchase + timedelta(hours=random.randint(1, 6))
        shipped   = None
        delivered = None
        est_deliv = purchase + timedelta(days=random.randint(5, 14))

    days_since = (REFERENCE_DATE - purchase).days
    return_eligible = (status == "delivered" and days_since <= 30)

    orders.append({
        "order_id":                      f"ORD-{1000 + i}",
        "customer_id":                   cust["customer_id"],
        "order_status":                  status,
        "order_purchase_timestamp":      purchase.strftime("%Y-%m-%d %H:%M:%S"),
        "order_approved_at":             approved.strftime("%Y-%m-%d %H:%M:%S")  if approved  else "",
        "order_delivered_carrier_date":  shipped.strftime("%Y-%m-%d %H:%M:%S")   if shipped   else "",
        "order_delivered_customer_date": delivered.strftime("%Y-%m-%d %H:%M:%S") if delivered else "",
        "order_estimated_delivery_date": est_deliv.strftime("%Y-%m-%d")          if est_deliv else "",
        "return_eligible":               return_eligible,
        "days_since_purchase":           days_since,
    })
df_orders = pd.DataFrame(orders)

# ── ORDER ITEMS ────────────────────────────────────────────────────────────────
items = []
for o in orders:
    n_items = random.choices([1, 2, 3], weights=[0.58, 0.30, 0.12])[0]
    for j in range(n_items):
        cat  = random.choice(CATEGORIES)
        name = random.choice(PRODUCT_NAMES[cat])
        items.append({
            "order_id":      o["order_id"],
            "order_item_id": j + 1,
            "product_id":    str(uuid.uuid4())[:8].upper(),
            "product_name":  name,
            "category_name": cat,
            "price":         round(random.uniform(12.99, 229.99), 2),
            "freight_value": round(random.uniform(4.99, 19.99), 2),
            "is_final_sale": random.random() < 0.10,
        })
df_items = pd.DataFrame(items)

# ── SAVE ───────────────────────────────────────────────────────────────────────
df_customers.to_csv("nestwell_customers.csv",    index=False)
df_orders.to_csv(   "nestwell_orders.csv",       index=False)
df_items.to_csv(    "nestwell_order_items.csv",  index=False)

print(f"Customers : {len(df_customers):,}")
print(f"Orders    : {len(df_orders):,}")
print(f"Items     : {len(df_items):,}")
print("\nStatus distribution:")
print(df_orders["order_status"].value_counts().to_string())
print(f"\nReturn-eligible orders : {df_orders['return_eligible'].sum()}")
print(f"Sample order IDs       : {df_orders['order_id'].head(5).tolist()}")
