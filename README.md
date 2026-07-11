# Customer Segmentation with SQL + Python

A beginner-to-intermediate data analysis project that segments customers from a sample retail dataset using SQL for aggregation and Python (Pandas + scikit-learn) for K-Means clustering.

## What It Does

1. Loads sample customer transaction data into a SQLite database
2. Uses SQL queries to compute RFM features (Recency, Frequency, Monetary value) per customer
3. Applies K-Means clustering to group customers into segments
4. Prints a profile summary for each segment

## Skills Demonstrated

- SQL (aggregation, GROUP BY, date functions via SQLite)
- Python (Pandas, scikit-learn, matplotlib)
- Data preprocessing and feature scaling
- Cluster analysis and interpretation

## Project Structure

```
customer-segmentation/
├── README.md
├── requirements.txt
├── generate_data.py      # Creates sample_data.csv with fake transactions
├── segment.py            # Main script: SQL -> features -> clustering -> profiles
```

## Setup & Run

```bash
pip install -r requirements.txt

# Step 1: Generate sample data
python generate_data.py

# Step 2: Run segmentation
python segment.py
```

## Sample Output

```
=== Customer Segment Profiles ===

Segment 0 - "Occasional Shoppers"
  Customers : 142
  Avg Recency (days ago): 85.3
  Avg Frequency (orders): 2.1
  Avg Spend ($)         : 134.50

Segment 1 - "High-Value Loyalists"
  Customers : 58
  Avg Recency (days ago): 12.4
  Avg Frequency (orders): 9.7
  Avg Spend ($)         : 892.30
...
```

## Notes

- SQLite is used so no external database setup is needed
- Data is randomly generated but realistic enough to produce meaningful clusters
- Tweak `N_CLUSTERS` in `segment.py` to experiment with different segmentations