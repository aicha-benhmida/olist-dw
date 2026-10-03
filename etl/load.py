from pathlib import Path
import pandas as pd
customers=Path("data/raw/olist_customers_dataset.csv")
orders=Path("data/raw/olist_orders_dataset.csv")
order_items=Path("data/raw/olist_order_items_dataset.csv")
order_reviews=Path("data/raw/olist_order_reviews_dataset.csv")
df_customers=pd.read_csv(customers,usecols=["customer_id","customer_unique_id","customer_city","customer_state"])
df_orders=pd.read_csv(orders,usecols=["order_id","order_delivered_customer_date","order_status","order_estimated_delivery_date","order_approved_at","order_purchase_timestamp","customer_id"])
df_order_items=pd.read_csv(order_items,usecols=["order_id","price"])
df_order_reviews=pd.read_csv(order_reviews,usecols=["order_id","review_score"])
"""
print(f"shape of customers dataset :{df_customers.shape}")
print(f"shape of orders dataset :{df_orders.shape}")
print(f"shape of order items dataset :{df_order_items.shape}")
print(f"shape of order reviews dataset :{df_order_reviews.shape}")
"""
df_revenue=df_order_items.groupby("order_id").agg({"price":"sum"}).reset_index()
df_revenue=df_revenue.rename(columns={"price":"order_revenue"})
"""
print(f"shape of revenue dataset :{df_revenue.shape}")
print(df_revenue.head())

"""
df_scores = df_order_reviews.groupby("order_id").agg({"review_score": "mean"}).reset_index()
#print(f"shape of scores dataset :{df_scores.shape}")

df_orders=pd.merge(df_orders,df_revenue,on="order_id",how="left")
df_orders=pd.merge(df_orders,df_scores,on="order_id",how="left")
"""
print(f"shape of order dataset :{df_orders.shape}")
print(df_orders.head())
print(df_orders.duplicated().sum())
"""
no_items = df_orders[df_orders["order_revenue"].isnull()]
"""
print(no_items["order_status"].value_counts())

print(df_orders["order_status"].value_counts())
"""
df_orders=df_orders[df_orders["order_status"]!="canceled"]
df_orders=df_orders.dropna(subset=["order_revenue"])
"""
print(df_orders.shape)
print(df_orders["order_revenue"].isnull().sum())
print(df_orders["order_status"].value_counts())
"""
df_orders["order_delivered_customer_date"]=pd.to_datetime(df_orders["order_delivered_customer_date"])
df_orders["order_estimated_delivery_date"]=pd.to_datetime(df_orders["order_estimated_delivery_date"])
df_orders["is_on_time"]=(df_orders["order_delivered_customer_date"]<=df_orders["order_estimated_delivery_date"]).astype("Int64")
df_orders["is_on_time"]=df_orders["is_on_time"].mask(df_orders["order_delivered_customer_date"].isnull())
"""print(df_orders["is_on_time"].isnull().sum())
print(df_orders["order_delivered_customer_date"].isnull().sum())
print(df_orders["is_on_time"].value_counts(dropna=False))
print(df_orders["is_on_time"].mean())"""

df_customers=df_customers[ df_customers["customer_id"] .isin( df_orders["customer_id"] ) ]
print(df_customers.shape)
print(df_customers["customer_id"].duplicated().sum())

df_orders["order_purchase_timestamp"] = pd.to_datetime(df_orders["order_purchase_timestamp"])
df_orders["date_key"] = df_orders["order_purchase_timestamp"].dt.strftime("%Y%m%d").astype(int)

print(df_orders[["order_purchase_timestamp", "date_key"]].head())


first_year = df_orders["order_purchase_timestamp"].dt.year.min()
last_year = df_orders["order_purchase_timestamp"].dt.year.max()

dim_date = pd.DataFrame({"full_date": pd.date_range(start=f"{first_year}-01-01", end=f"{last_year}-12-31")})
dim_date["year"] = dim_date["full_date"].dt.year
dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)

print(dim_date["date_key"].duplicated().sum())
print((~df_orders["date_key"].isin(dim_date["date_key"])).sum())
print(dim_date.shape)