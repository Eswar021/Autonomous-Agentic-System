import pandas as pd
from typing import Any, Dict, Optional
from tools.reviews_this_year import reviews_this_year
from .base import llm_analyze

class ReviewThisYearInvestigator:
    """
    Zero-arg agent:
    - fetch review rows for detected year (tool)
    - compute rating distribution & basic KPIs
    - send objective + memory + facts to LLM for analysis
    """
    def __init__(self, objective: str = "", memory: Optional[Dict[str, Any]] = None):
        self.objective = objective or "Summarize this year's review signals and implications."
        self.memory = memory or {}

    def run(self) -> Dict[str, Any]:
        df = reviews_this_year()
        if df.empty:
            return {"summary": "No reviews found for the detected year.", "table": pd.DataFrame(), "facts": {}}

        if "review_date" in df.columns:
            df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")

        if "rating" in df.columns:
            dist = df.groupby("rating").size().reset_index(name="count").sort_values("rating")
            mean_rating = float(df["rating"].mean())
        else:
            dist = pd.DataFrame(columns=["rating","count"])
            mean_rating = float("nan")

        facts = {
            "detected_year": int(df["review_date"].dt.year.max()) if "review_date" in df.columns else None,
            "total_reviews": int(len(df)),
            "mean_rating": mean_rating,
            "columns": list(df.columns),
        }

        context = {"objective": self.objective, "memory": self.memory, "facts": facts}
        fallback = f"Detected Year Reviews: n={facts['total_reviews']}, avg_rating={facts['mean_rating']:.2f}."
        summary_md = llm_analyze(context, fallback)
        return {"summary": summary_md, "table": dist, "facts": facts}
