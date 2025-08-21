import pandas as pd
from pathlib import Path
from tools._paths import find_data_dir

def sales_this_year() -> pd.DataFrame:
    """
    Return raw sales rows for the most recent year present in DB/data/sales.csv.
    Detect 'this year' from max(sales['date']).
    Join customers on customer_id to add region if available.
    """
    data_dir = find_data_dir(Path(__file__))
    sales_path = data_dir / "sales.csv"
    cust_path = data_dir / "customers.csv"

    sales = pd.read_csv(sales_path)
    if "date" not in sales.columns or sales.empty:
        return sales.head(0)

    sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
    if sales["date"].isna().all():
        return sales.head(0)

    target_year = int(sales["date"].dt.year.max())
    yr = sales[sales["date"].dt.year == target_year].copy()

    try:
        customers = pd.read_csv(cust_path)
        if {"customer_id","region"}.issubset(customers.columns) and "customer_id" in yr.columns:
            yr = yr.merge(customers[["customer_id","region"]], on="customer_id", how="left")
    except Exception:
        pass

    return yr
