import pandas as pd
from typing import Any, Dict, Optional
from tools.sales_this_year import sales_this_year
from .base import llm_analyze

class SalesThisYearAnalyst:
    """
    Zero-arg agent:
    - fetch sales rows for detected year (tool)
    - compute daily units/revenue
    - send objective + memory + facts to LLM for analysis
    """
    def __init__(self, objective: str = "", memory: Optional[Dict[str, Any]] = None):
        self.objective = objective or "Explain this year's sales movement and key drivers."
        self.memory = memory or {}

    def run(self) -> Dict[str, Any]:
        df = sales_this_year()
        if df.empty:
            return {"summary": "No sales found for the detected year.", "table": pd.DataFrame(), "facts": {}}

        qty = df["quantity"] if "quantity" in df.columns else 0
        price = df["price"] if "price" in df.columns else 0.0
        df["revenue"] = qty * price

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            daily = df.dropna(subset=["date"]).groupby(df["date"].dt.date).agg(
                units=("quantity","sum") if "quantity" in df.columns else ("revenue","size"),
                revenue=("revenue","sum")
            ).reset_index().rename(columns={"date":"day"})
        else:
            daily = pd.DataFrame(columns=["day","units","revenue"])

        facts = {
            "detected_year": int(df["date"].dt.year.max()) if "date" in df.columns else None,
            "days": int(len(daily)),
            "total_units": int(daily["units"].sum()) if "units" in daily.columns else None,
            "total_revenue": float(daily["revenue"].sum()) if "revenue" in daily.columns else None,
            "columns": list(df.columns),
        }

        context = {"objective": self.objective, "memory": self.memory, "facts": facts}
        fallback = f"Detected Year Sales: days={facts['days']}, total_revenue={facts['total_revenue']}."
        summary_md = llm_analyze(context, fallback)
        return {"summary": summary_md, "table": daily, "facts": facts}
