from pathlib import Path
import pandas as pd
customers=Path("data/raw/olist_customers_dataset.csv")
orders=Path("data/raw/olist_orders_dataset.csv")
order_items=Path("data/raw/olist_order_items_dataset.csv")
order_reviews=Path("data/raw/olist_order_reviews_dataset.csv")
df_customers=pd.read_csv(customers,usecols=["customer_id","customer_unique_id","customer_city","customer_state"])
df_orders=pd.read_csv(orders,usecols=["order_id","order_delivered_customer_date","order_estimated_delivery_date","order_approved_at","customer_id"])
df_order_items=pd.read_csv(order_items,usecols=["order_id","price"])
df_order_reviews=pd.read_csv(order_reviews,usecols=["order_id","review_score"])

print(f"shape of customers dataset :{df_customers.shape}")
print(f"shape of orders dataset :{df_orders.shape}")
print(f"shape of order items dataset :{df_order_items.shape}")
print(f"shape of order reviews dataset :{df_order_reviews.shape}")

df_revenue=df_order_items.groupby("order_id").agg({"price":"sum"}).reset_index()
df_revenue=df_revenue.rename(columns={"price":"order_revenue"})
print(f"shape of revenue dataset :{df_revenue.shape}")
print(df_revenue.head())
df_scores = df_order_reviews.groupby("order_id").agg({"review_score": "mean"}).reset_index()
print(f"shape of scores dataset :{df_scores.shape}")