"""
generate_data.py
Generates a synthetic retail transactions CSV with ~1000 customers and ~5000 orders.
"""

import random
import csv
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

N_CUSTOMERS = 400
N_TRANSACTIONS = 3000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 6, 30)

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

# Build customer list
customers = [fake.uuid4()[:8] for _ in range(N_CUSTOMERS)]

# Assign customer "types" to make clusters meaningful
# Type A: high frequency, high spend, recent
# Type B: low frequency, low spend, older
# Type C: medium everything
def customer_profile(cid):
    h = hash(cid) % 3
    if h == 0:
        return "high"
    elif h == 1:
        return "low"
    else:
        return "medium"

rows = []
for _ in range(N_TRANSACTIONS):
    cid = random.choice(customers)
    profile = customer_profile(cid)

    if profile == "high":
        date = random_date(datetime(2024, 3, 1), END_DATE)
        amount = round(random.uniform(80, 300), 2)
    elif profile == "low":
        date = random_date(START_DATE, datetime(2023, 9, 1))
        amount = round(random.uniform(10, 60), 2)
    else:
        date = random_date(datetime(2023, 6, 1), datetime(2024, 3, 1))
        amount = round(random.uniform(30, 150), 2)

    rows.append({
        "transaction_id": fake.uuid4()[:12],
        "customer_id": cid,
        "transaction_date": date.strftime("%Y-%m-%d"),
        "amount": amount
    })

output_file = "sample_data.csv"
with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["transaction_id", "customer_id", "transaction_date", "amount"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} transactions for {N_CUSTOMERS} customers -> {output_file}")