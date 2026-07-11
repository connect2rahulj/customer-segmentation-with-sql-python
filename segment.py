"""
segment.py
Main pipeline:
  1. Load sample_data.csv into SQLite
  2. Run SQL to compute RFM features
  3. Scale features and run K-Means clustering
  4. Print segment profiles
"""

import sqlite3
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# ── Config ──────────────────────────────────────────────────────────────────
CSV_FILE = "sample_data.csv"
N_CLUSTERS = 3
RANDOM_STATE = 42

# ── 1. Load CSV into SQLite ──────────────────────────────────────────────────
print("Loading data into SQLite...")
conn = sqlite3.connect(":memory:")
df_raw = pd.read_csv(CSV_FILE, parse_dates=["transaction_date"])
df_raw.to_sql("transactions", conn, index=False, if_exists="replace")
print(f"  {len(df_raw)} rows loaded.")

# ── 2. Compute RFM via SQL ───────────────────────────────────────────────────
# Reference date = day after the last transaction in the dataset
ref_date_row = conn.execute("SELECT MAX(transaction_date) FROM transactions").fetchone()
ref_date = ref_date_row[0]  # string like '2024-06-30'

sql = f"""
SELECT
    customer_id,
    CAST(julianday('{ref_date}') - julianday(MAX(transaction_date)) AS INTEGER) AS recency_days,
    COUNT(transaction_id)                                                         AS frequency,
    ROUND(SUM(amount), 2)                                                         AS monetary
FROM transactions
GROUP BY customer_id
"""

rfm = pd.read_sql_query(sql, conn)
conn.close()

print(f"\nRFM table shape: {rfm.shape}")
print(rfm.head())

# ── 3. Scale & Cluster ───────────────────────────────────────────────────────
features = ["recency_days", "frequency", "monetary"]
X = rfm[features].copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"\nFitting K-Means with {N_CLUSTERS} clusters...")
kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
rfm["segment"] = kmeans.fit_predict(X_scaled)

# ── 4. Label Segments ────────────────────────────────────────────────────────
# Sort segments by monetary value so labels are consistent
segment_means = rfm.groupby("segment")["monetary"].mean().sort_values()
rank_map = {seg: rank for rank, seg in enumerate(segment_means.index)}
rfm["segment_rank"] = rfm["segment"].map(rank_map)

LABELS = {
    0: "Budget / Lapsed",
    1: "Mid-Tier Regulars",
    2: "High-Value Loyalists",
}

rfm["segment_label"] = rfm["segment_rank"].map(LABELS)

# ── 5. Print Profiles ────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("  Customer Segment Profiles")
print("=" * 50)

profile = (
    rfm.groupby(["segment_rank", "segment_label"])
    .agg(
        customers=("customer_id", "count"),
        avg_recency=("recency_days", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
    )
    .reset_index()
    .sort_values("segment_rank")
)

for _, row in profile.iterrows():
    print(f"\nSegment {int(row.segment_rank)} — \"{row.segment_label}\"")
    print(f"  Customers              : {int(row.customers)}")
    print(f"  Avg Recency (days ago) : {row.avg_recency:.1f}")
    print(f"  Avg Frequency (orders) : {row.avg_frequency:.1f}")
    print(f"  Avg Total Spend ($)    : {row.avg_monetary:.2f}")

# ── 6. Save results & plot ───────────────────────────────────────────────────
rfm.to_csv("customer_segments.csv", index=False)
print("\nFull results saved to customer_segments.csv")

# Scatter plot: Frequency vs Monetary, colored by segment
colors = ["#e07b39", "#4c8baf", "#5ba55b"]
fig, ax = plt.subplots(figsize=(8, 5))
for rank, label in LABELS.items():
    subset = rfm[rfm["segment_rank"] == rank]
    ax.scatter(subset["frequency"], subset["monetary"],
               label=label, alpha=0.6, color=colors[rank], edgecolors="none", s=40)

ax.set_xlabel("Frequency (# orders)")
ax.set_ylabel("Monetary (total spend $)")
ax.set_title("Customer Segmentation — Frequency vs Spend")
ax.legend()
plt.tight_layout()
plt.savefig("segments_plot.png", dpi=120)
print("Plot saved to segments_plot.png")
plt.show()