# D:\Zenith AI\MAS_UseCase_V2\schemas\datasets.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

# ---------- Column description heuristics ----------
_NAME_HINTS = {
    "date": "Calendar date for the record (parseable to datetime).",
    "product_id": "Unique product identifier.",
    "order_id": "Unique sales order identifier.",
    "customer_id": "Unique customer identifier.",
    "region": "Sales/Customer geographic region.",
    "quantity": "Units sold in the transaction.",
    "price": "Unit price at time of sale (local currency).",
    "sales_units": "Units sold during the period (aggregated).",
    "revenue": "Sales revenue for the row/period (local currency).",
    "marketing_spend": "Marketing spend for the row/period (local currency).",
    "competitor_price": "Observed competitor price level.",
    "inventory_count": "Available inventory units at row time.",
    "stockout_flag": "1 if stockout occurred on the row date, else 0.",
    "temperature": "Ambient temperature for the row location/date.",
    "rating": "Customer review rating (e.g., 1–5).",
    "review_text": "Free‑text customer review content.",
}

def _describe_col(name: str) -> str:
    key = name.lower()
    return _NAME_HINTS.get(key, f"'{name}' column; auto‑discovered. Provide semantics in docs if critical.")

# ---------- Metadata discovery ----------

def _examples(series: pd.Series, k: int = 3) -> List[Any]:
    vals = series.dropna().unique().tolist()
    return vals[:k]


def discover_csv_meta(data_dir: Path) -> Dict[str, Any]:
    """Discover all CSVs under the provided data_dir. Read a small sample
    to infer columns/dtypes, collect example values, and create natural
    descriptions per column. Returns a nested dict suitable for registry and prompts.
    """
    meta: Dict[str, Any] = {}
    if not data_dir.exists():
        return meta

    for path in sorted(data_dir.glob("*.csv")):
        name = path.stem  # e.g., sales, reviews, kpi_results
        try:
            df = pd.read_csv(path, nrows=200)
        except Exception:
            continue
        cols = list(df.columns)
        dtypes = {c: str(df[c].dtype) for c in cols}
        # examples per column (primitive JSON‑serializable)
        col_examples = {c: _examples(df[c]) for c in cols}
        col_desc = {c: _describe_col(c) for c in cols}
        meta[name] = {
            "name": name,
            "path": str(path),
            "columns": cols,
            "dtypes": dtypes,
            "examples": col_examples,
            "descriptions": col_desc,
            "sample_rows": df.head(3).to_dict(orient="records"),
            "row_count_estimate": None,
        }
    return meta


def _truncate_examples(m: Dict[str, Any], max_chars: int = 8000) -> Dict[str, Any]:
    """Create a compact copy of metadata for LLM prompts (avoid token blow‑ups)."""
    import copy, json as _json
    cpy = copy.deepcopy(m)
    # Keep 3 sample rows and 3 example values per column (already done).
    s = _json.dumps(cpy)
    if len(s) <= max_chars:
        return cpy
    # If still too long, drop sample_rows first, then examples
    for ds in cpy.values():
        ds.pop("sample_rows", None)
    s = _json.dumps(cpy)
    if len(s) <= max_chars:
        return cpy
    for ds in cpy.values():
        ds.pop("examples", None)
    return cpy


def meta_as_json(meta: Dict[str, Any], compact: bool = True) -> str:
    data = _truncate_examples(meta) if compact else meta
    return json.dumps(data, indent=2)