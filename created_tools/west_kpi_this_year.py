import pandas as pd
from pathlib import Path
from tools._paths import find_data_dir


def west_kpi_this_year() -> pd.DataFrame:
    """Returns KPI rows for the West region for the most recent year.

    Filters kpi_results to the West region and the most recent year found in the date column.
    Returns a DataFrame with all columns from kpi_results, filtered by region and year.
    """
    data_dir = find_data_dir(Path(__file__))
    kpi_results_path = data_dir / "kpi_results.csv"
    kpi_results = pd.read_csv(kpi_results_path)
    kpi_results['date'] = pd.to_datetime(kpi_results['date'], errors='coerce')

    latest_year = kpi_results['date'].dt.year.max()

    west_kpi_latest_year = kpi_results[
        (kpi_results['region'] == 'West') & (kpi_results['date'].dt.year == latest_year)
    ]

    return west_kpi_latest_year
