from pathlib import Path
import pandas as pd

RAW=Path("data/raw")
for file in RAW.glob("*.csv"):
    df = pd.read_csv(file)
    print("="*50)
    print(f"file name:{file.name}")
    print(f"number of rows :{len(df)}")
    print(f"columns :{list(df.columns)}")
    print("\n missing values :")
    print(df.isnull().sum())

path=Path("data/raw/olist_customers_dataset.csv")
df = pd.read_csv(path)
print(f"dataset name :{path.name}")
print(f"id customer unique unique:{df.customer_unique_id.nunique()}")
print(f"id customer unique :{df.customer_id.nunique()}")
print(f"id customer duplicated :{df.customer_id.duplicated().sum()}")

pathh=Path("data/raw/olist_order_reviews_dataset.csv")
df = pd.read_csv(pathh)
print(f"dataset name :{pathh.name}")
print(f"id order unique :{df.order_id.nunique()}")
print(f"id order duplicated :{df.order_id.duplicated().sum()}")
