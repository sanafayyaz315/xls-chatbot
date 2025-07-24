# generate fake data
import pandas as pd
import random
from faker import Faker

fake = Faker()

# Generate customers
customers = pd.DataFrame({
    "customer_id": list(range(1, 51)),
    "customer_name": [fake.name() for _ in range(50)],
    "email": [fake.email() for _ in range(50)],
    "signup_date": [fake.date_between(start_date='-2y', end_date='today') for _ in range(50)]
})

# Generate products
product_names = ["iPhone 14 Pro", "MacBook Air", "iPad Mini", "Apple Watch", "AirPods Pro",
                 "Samsung Galaxy S23", "Dell XPS 13", "Lenovo ThinkPad", "Google Pixel 7", "Sony WH-1000XM5"]
categories = ["Smartphone", "Laptop", "Tablet", "Wearable", "Audio"]

products = pd.DataFrame({
    "product_id": list(range(101, 111)),
    "product_name": product_names,
    "category": [random.choice(categories) for _ in range(10)],
    "amount_paid": [round(random.uniform(200, 2000), 2) for _ in range(10)]
})

# Generate sales
sales = pd.DataFrame({
    "sale_id": list(range(1001, 1101)),
    "customer_id": [random.randint(1, 50) for _ in range(100)],
    "product_id": [random.randint(101, 110) for _ in range(100)],
    "sale_date": [fake.date_between(start_date='-1y', end_date='today') for _ in range(100)]
})

# Merge sales with customers on customer_id
df = sales.merge(customers, on="customer_id", how="left")

# Merge the result with products on product_id
df = df.merge(products, on="product_id", how="left")

# Reorder columns for readability (optional)
df = df[[
    "sale_id", "sale_date", "customer_id", "customer_name", "email", "signup_date",
    "product_id", "product_name", "category", "amount_paid"
]]

# Save to Excel (single sheet)
df.to_csv("../data/customer_sales.csv", index=False)
