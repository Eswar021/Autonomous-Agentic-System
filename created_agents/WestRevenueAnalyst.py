import pandas as pd
from typing import Optional, Dict, Any
from agents.base import llm_analyze
from tools.sales_this_year import sales_this_year
from created_tools.west_kpi_this_year import west_kpi_this_year

class WestRevenueAnalyst:
    def __init__(self, objective: str = "", memory: Optional[Dict[str, Any]] = None):
        self.objective = objective
        self.memory = memory if memory is not None else {}

    def run(self) -> Dict[str, Any]:
        sales_df = sales_this_year()
        kpi_df = west_kpi_this_year()

        # Ensure required columns exist and coerce to numeric
        for df in [sales_df, kpi_df]:
            if df is not None:
                for col in ["revenue","sales_units","average_price","stockout_rate"]: #average_price not in data
                    if col not in df.columns: df[col] = pd.NA
                    df[col] = pd.to_numeric(df[col], errors="coerce")

        facts = {}
        if sales_df is not None and not sales_df.empty:
            total_revenue = sales_df['price'].sum()
            facts['total_revenue'] = total_revenue
        else:
            facts['total_revenue'] = 0

        if kpi_df is not None and not kpi_df.empty:
            avg_stockout_rate = kpi_df['stockout_flag'].mean()
            facts['avg_stockout_rate'] = avg_stockout_rate
        else:
            facts['avg_stockout_rate'] = 0

        context = {"objective": self.objective, "memory": self.memory, "facts": facts}
        fallback = "No significant insights could be derived from the available data."
        summary_md = llm_analyze(context, fallback)

        return {
            "summary": summary_md,
            "table": kpi_df if kpi_df is not None else pd.DataFrame(),
            "facts": facts
        }
