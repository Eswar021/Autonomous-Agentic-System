import pandas as pd
from pathlib import Path
from tools._paths import find_data_dir

def reviews_this_year() -> pd.DataFrame:
    """
    Return raw review rows for the most recent year present in DB/data/reviews.csv.
    Detect 'this year' from max(reviews['review_date']).
    Join customers to add region if available.
    """
    data_dir = find_data_dir(Path(__file__))
    reviews_path = data_dir / "reviews.csv"
    cust_path = data_dir / "customers.csv"

    reviews = pd.read_csv(reviews_path)
    if "review_date" not in reviews.columns or reviews.empty:
        return reviews.head(0)

    reviews["review_date"] = pd.to_datetime(reviews["review_date"], errors="coerce")
    if reviews["review_date"].isna().all():
        return reviews.head(0)

    target_year = int(reviews["review_date"].dt.year.max())
    yr = reviews[reviews["review_date"].dt.year == target_year].copy()

    try:
        customers = pd.read_csv(cust_path)
        if {"customer_id","region"}.issubset(customers.columns) and "customer_id" in yr.columns:
            yr = yr.merge(customers[["customer_id","region"]], on="customer_id", how="left")
    except Exception:
        pass

    return yr
