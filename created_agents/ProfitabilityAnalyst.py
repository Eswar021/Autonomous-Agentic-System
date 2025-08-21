import pandas as pd
from typing import Optional, Dict, Any
from agents.base import llm_analyze
from tools.sales_this_year import sales_this_year
from created_tools.west_kpi_this_year import west_kpi_this_year

class ProfitabilityAnalyst:
    def __init__(self, objective: str = "", memory: Optional[Dict[str, Any]] = None):
        self.objective = objective
        self.memory = memory

    def run(self) -> Dict[str, Any]:
        df_sales = sales_this_year()
        df_kpi = west_kpi_this_year()

        # Ensure required columns exist and coerce to numeric
        for df in [df_sales, df_kpi]:
            for col in ["revenue", "sales_units", "average_price", "stockout_rate", "marketing_spend"]: # Added marketing_spend
                if col not in df.columns: df[col] = pd.NA
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Calculate profit for sales data
        if 'price' in df_sales.columns and 'quantity' in df_sales.columns:
            df_sales['cost'] = df_sales['price'] * df_sales['quantity']
            df_sales['profit'] = df_sales['price'] * df_sales['quantity'] # Placeholder, refine with actual cost data
        else:
            df_sales['cost'] = pd.NA
            df_sales['profit'] = pd.NA

        # Calculate profit margin for KPI data
        if 'revenue' in df_kpi.columns and 'sales_units' in df_kpi.columns:
            df_kpi['average_price'] = df_kpi['revenue'] / df_kpi['sales_units'] if df_kpi['sales_units'].sum() > 0 else 0
            df_kpi['cost'] = df_kpi['average_price'] * df_kpi['sales_units'] # Placeholder, refine with actual cost data
            df_kpi['profit'] = df_kpi['revenue'] - df_kpi['marketing_spend'] # More accurate profit calc
            df_kpi['profit_margin'] = (df_kpi['profit'] / df_kpi['revenue']) * 100 if df_kpi['revenue'].sum() > 0 else 0
        else:
            df_kpi['cost'] = pd.NA
            df_kpi['profit'] = pd.NA
            df_kpi['profit_margin'] = pd.NA

        # Basic aggregation for facts
        total_revenue_sales = df_sales['price'].sum() if 'price' in df_sales.columns else 0
        total_revenue_kpi = df_kpi['revenue'].sum() if 'revenue' in df_kpi.columns else 0
        total_profit_kpi = df_kpi['profit'].sum() if 'profit' in df_kpi.columns else 0
        average_profit_margin = df_kpi['profit_margin'].mean() if 'profit_margin' in df_kpi.columns else 0

        facts = {
            "total_revenue_sales": total_revenue_sales,
            "total_revenue_kpi": total_revenue_kpi,
            "total_profit_kpi": total_profit_kpi,
            "average_profit_margin": average_profit_margin
        }

        context = {
            "objective": self.objective,
            "memory": self.memory,
            "facts": facts
        }

        fallback = "Analyzed sales and KPI data.  Unable to determine specific insights."
        summary_md = llm_analyze(context, fallback)

        return {
            "summary": summary_md,
            "table": df_kpi,
            "facts": facts
        }
