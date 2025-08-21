import pandas as pd
from pathlib import Path
from tools._paths import find_data_dir


def kpi_results_this_year() -> pd.DataFrame:
    """Returns kpi_results rows for the most recent year."""
    data_dir = find_data_dir(Path(__file__))
    kpi_results_df = pd.read_csv(data_dir / 'kpi_results.csv')
    kpi_results_df['date'] = pd.to_datetime(kpi_results_df['date'], errors='coerce')

    most_recent_year = kpi_results_df['date'].dt.year.max()
    kpi_results_this_year_df = kpi_results_df[kpi_results_df['date'].dt.year == most_recent_year]

    return kpi_results_this_year_df
