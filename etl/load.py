from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine,text

def extract():
    customers=Path("data/raw/olist_customers_dataset.csv")
    orders=Path("data/raw/olist_orders_dataset.csv")
    order_items=Path("data/raw/olist_order_items_dataset.csv")
    order_reviews=Path("data/raw/olist_order_reviews_dataset.csv")
    df_customers=pd.read_csv(customers,usecols=["customer_id","customer_unique_id","customer_city","customer_state"])
    df_customers=df_customers.rename(columns={"customer_city":"city","customer_state":"state"})
    df_orders=pd.read_csv(orders,usecols=["order_id","order_delivered_customer_date","order_status","order_estimated_delivery_date","order_approved_at","order_purchase_timestamp","customer_id"])
    df_order_items=pd.read_csv(order_items,usecols=["order_id","price"])
    df_order_reviews=pd.read_csv(order_reviews,usecols=["order_id","review_score"])
    return df_customers,df_orders,df_order_items,df_order_reviews

def transform(df_customers,df_orders,df_order_items,df_order_reviews):
    df_revenue=df_order_items.groupby("order_id").agg({"price":"sum"}).reset_index()
    df_revenue=df_revenue.rename(columns={"price":"order_revenue"})
    df_scores = df_order_reviews.groupby("order_id").agg({"review_score": "mean"}).reset_index()    

    df_orders=pd.merge(df_orders,df_revenue,on="order_id",how="left")
    df_orders=pd.merge(df_orders,df_scores,on="order_id",how="left")
    no_items = df_orders[df_orders["order_revenue"].isnull()]

    df_orders=df_orders[df_orders["order_status"]!="canceled"]
    df_orders=df_orders.dropna(subset=["order_revenue"])
    df_orders["order_delivered_customer_date"]=pd.to_datetime(df_orders["order_delivered_customer_date"])
    df_orders["order_estimated_delivery_date"]=pd.to_datetime(df_orders["order_estimated_delivery_date"])
    df_orders["is_on_time"]=(df_orders["order_delivered_customer_date"]<=df_orders["order_estimated_delivery_date"]).astype("Int64")
    df_orders["is_on_time"]=df_orders["is_on_time"].mask(df_orders["order_delivered_customer_date"].isnull())

    df_customers=df_customers[ df_customers["customer_id"] .isin( df_orders["customer_id"] ) ]

    df_orders["order_purchase_timestamp"] = pd.to_datetime(df_orders["order_purchase_timestamp"])
    df_orders["date_key"] = df_orders["order_purchase_timestamp"].dt.strftime("%Y%m%d").astype(int)

    first_year = df_orders["order_purchase_timestamp"].dt.year.min()
    last_year = df_orders["order_purchase_timestamp"].dt.year.max()

    dim_date = pd.DataFrame({"full_date": pd.date_range(start=f"{first_year}-01-01", end=f"{last_year}-12-31")})
    dim_date["year"] = dim_date["full_date"].dt.year
    dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim_customers=df_customers[["customer_id","customer_unique_id","city","state"]]
    fact_orders=df_orders[["order_id","customer_id","order_revenue","review_score","is_on_time","date_key"]]
    return dim_customers,fact_orders,dim_date
load_dotenv()

def load(dim_date,dim_customers,fact_orders):
    user=os.getenv("DB_USER")
    password=os.getenv("DB_PASSWORD")   
    host=os.getenv("DB_HOST")
    port=os.getenv("DB_PORT")
    name=os.getenv("DB_NAME")
    postgresql_url=f"postgresql://{user}:{password}@{host}:{port}/{name}"
    engine = create_engine(postgresql_url)
    with engine.connect() as connection:
        print("Connection to PostgreSQL database established successfully.")
    with engine.begin() as connection:
        connection.execute(text("""TRUNCATE table fact_orders, dim_customers, dim_date RESTART IDENTITY CASCADE;"""))
        dim_date.to_sql("dim_date",connection,index=False,if_exists="append")
        dim_customers.to_sql("dim_customers",connection,index=False,if_exists="append")
        df_key=pd.read_sql("select customer_id , customer_key from dim_customers",connection)
        fact_orders=fact_orders.merge(df_key,on="customer_id",how="left")
        fact_orders=fact_orders.drop(columns=["customer_id"])
        fact_orders.to_sql("fact_orders", connection, index=False, if_exists="append")
if __name__=="__main__":
    df_customers,df_orders,df_order_items,df_order_reviews=extract()
    dim_customers,fact_orders,dim_date=transform(df_customers,df_orders,df_order_items,df_order_reviews)
    print(dim_customers.shape)
    print(fact_orders.shape)
    print(dim_date.shape)
    load(dim_date,dim_customers,fact_orders)