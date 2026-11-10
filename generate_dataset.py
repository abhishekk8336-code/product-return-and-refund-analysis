
import pandas as pd
import numpy as np
import random
import os

# Reproducible dataset
np.random.seed(42)
random.seed(42)

# Create data folder if it doesn't exist
os.makedirs("data", exist_ok=True)

# Product catalogue
products = {
    "Electronics": [
        "Wireless Mouse", "Keyboard", "Headphones",
        "Smartphone", "Power Bank", "Bluetooth Speaker"
    ],
    "Fashion": [
        "T-Shirt", "Jeans", "Shoes",
        "Jacket", "Watch", "Backpack"
    ],
    "Home": [
        "Water Bottle", "Bedsheet", "Lamp",
        "Cookware Set", "Chair", "Wall Clock"
    ],
    "Beauty": [
        "Face Wash", "Moisturizer", "Sunscreen",
        "Shampoo", "Perfume", "Face Serum"
    ],
    "Sports": [
        "Football", "Cricket Bat", "Yoga Mat",
        "Dumbbells", "Running Shoes", "Gym Bag"
    ]
}

# Return probabilities by category
return_probability = {
    "Electronics": 0.18,
    "Fashion": 0.25,
    "Home": 0.10,
    "Beauty": 0.07,
    "Sports": 0.12
}

regions = [
    "Delhi", "Mumbai", "Bengaluru", "Hyderabad",
    "Lucknow", "Kolkata", "Chennai", "Pune",
    "Jaipur", "Ahmedabad"
]

payment_methods = [
    "UPI", "Credit Card", "Debit Card",
    "Cash on Delivery", "Net Banking"
]

return_reasons = [
    "Defective Product",
    "Wrong Product Delivered",
    "Damaged During Shipping",
    "Size Issue",
    "Quality Issue",
    "Product Not As Described",
    "Changed Mind"
]

refund_statuses = ["Completed", "Pending", "Processing"]

data = []

# Generate 10,000 orders
for i in range(10000):

    category = random.choice(list(products.keys()))

    product = random.choice(products[category])

    quantity = random.randint(1, 3)

    price = random.randint(200, 10000)

    order_date = pd.Timestamp("2026-01-01") + pd.Timedelta(
        days=random.randint(0, 287)
    )

    returned = random.random() < return_probability[category]

    if returned:
        return_status = "Returned"

        return_date = order_date + pd.Timedelta(
            days=random.randint(1, 14)
        )

        return_reason = random.choice(return_reasons)

        refund_amount = quantity * price

        refund_status = random.choices(
            refund_statuses,
            weights=[70, 15, 15]
        )[0]

    else:
        return_status = "Not Returned"
        return_date = pd.NaT
        return_reason = None
        refund_amount = 0
        refund_status = "Not Applicable"

    data.append({
        "Order_ID": f"ORD{i + 1001}",
        "Customer_ID": f"CUST{random.randint(1001, 3000)}",
        "Order_Date": order_date,
        "Product_Name": product,
        "Category": category,
        "Quantity": quantity,
        "Unit_Price": price,
        "Region": random.choice(regions),
        "Payment_Method": random.choice(payment_methods),
        "Delivery_Status": "Delivered",
        "Return_Status": return_status,
        "Return_Date": return_date,
        "Return_Reason": return_reason,
        "Refund_Amount": refund_amount,
        "Refund_Status": refund_status
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Introduce some missing values for data cleaning practice
for column in ["Region", "Payment_Method"]:
    indexes = df.sample(frac=0.005, random_state=42).index
    df.loc[indexes, column] = np.nan

# Introduce a few missing return reasons
returned_indexes = df[df["Return_Status"] == "Returned"].sample(
    frac=0.01, random_state=42
).index

df.loc[returned_indexes, "Return_Reason"] = np.nan

# Introduce 50 duplicate records intentionally
duplicates = df.sample(n=50, random_state=42)
df = pd.concat([df, duplicates], ignore_index=True)

# Save raw dataset
df.to_csv("data/ecommerce_returns_raw.csv", index=False)

print("\nDATASET GENERATED SUCCESSFULLY!")
print("--------------------------------")
print("Total records:", len(df))
print("Unique orders:", df["Order_ID"].nunique())
print("Returned orders:", (df["Return_Status"] == "Returned").sum())
print("Not returned:", (df["Return_Status"] == "Not Returned").sum())
print("Duplicate records:", df.duplicated().sum())
print("\nDataset saved at:")
print("data/ecommerce_returns_raw.csv")

print("\nFirst five records:")
print(df.head())
