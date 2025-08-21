import pandas as pd
from typing import Optional, Dict, Any
from agents.base import llm_analyze
from created_tools.kpi_results_this_year import kpi_results_this_year
from created_tools.product_category_mapping import product_category_mapping

class ProfitDriverAnalyst:
    def __init__(self, objective: str = "", memory: Optional[Dict[str, Any]] = None):
        self.objective = objective
        self.memory = memory if memory is not None else {}

    def run(self) -> Dict[str, Any]:
        kpi_df = kpi_results_this_year()
        product_category_df = product_category_mapping()

        # Ensure expected columns exist and coerce to numeric
        for df in [kpi_df]:
            for col in ["revenue","sales_units","average_price","stockout_rate","marketing_spend","competitor_price","inventory_count"]: # Added missing columns
                if col not in df.columns: df[col] = pd.NA
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Calculate profit
        kpi_df['profit'] = kpi_df['revenue'] - kpi_df['marketing_spend'] # Simplified cost to marketing spend

        # Aggregate KPIs by product category
        if 'product_category' in product_category_df.columns and 'product_id' in kpi_df.columns:
            merged_df = pd.merge(kpi_df, product_category_df, on='product_id', how='left')
            category_profit = merged_df.groupby('product_category')['profit'].sum().reset_index()
            category_sales_units = merged_df.groupby('product_category')['sales_units'].sum().reset_index()
            category_marketing_spend = merged_df.groupby('product_category')['marketing_spend'].sum().reset_index()

            # Calculate profit margin by category
            category_profit['profit_margin'] = category_profit['profit'] / category_sales_units['sales_units']

            # Sort by profit margin
            category_profit = category_profit.sort_values(by='profit_margin', ascending=False)

            table = category_profit

            total_profit = kpi_df['profit'].sum()
            mean_marketing_spend = kpi_df['marketing_spend'].mean()
            mean_competitor_price = kpi_df['competitor_price'].mean()
            mean_stockout_flag = kpi_df['stockout_flag'].mean()

            facts = {
                "total_profit": total_profit,
                "mean_marketing_spend": mean_marketing_spend,
                "mean_competitor_price": mean_competitor_price,
                "mean_stockout_flag": mean_stockout_flag
            }

        else:
            table = pd.DataFrame()
            facts = {}

        context = {"objective": self.objective, "memory": self.memory, "facts": facts}
        fallback = "Unable to analyze profit drivers due to missing data."
        summary_md = llm_analyze(context, fallback)

        return {"summary": summary_md, "table": table, "facts": facts}
