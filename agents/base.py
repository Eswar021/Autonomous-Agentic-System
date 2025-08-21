# D:\Zenith AI\MAS_UseCase_V3\agents\base.py
from __future__ import annotations
import os, json
from typing import Any, Dict, Optional

try:
    import numpy as np
except Exception:
    np = None

try:
    import pandas as pd
except Exception:
    pd = None

from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm() -> Optional[ChatGoogleGenerativeAI]:
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        return None
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=key, temperature=0.3)

def _json_default(obj):
    # Numpy scalars/arrays
    if np is not None:
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
    # Pandas timestamps/series/frames
    if pd is not None:
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, pd.Series):
            return obj.tolist()
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
    # Datetimes
    try:
        from datetime import datetime, date
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
    except Exception:
        pass
    # Fallbacks for other iterables / objects
    if hasattr(obj, "__dict__"):
        return {k: _json_default(v) for k, v in obj.__dict__.items()}
    try:
        return str(obj)
    except Exception:
        return None

def llm_analyze(context: Dict[str, Any], fallback: str) -> str:
    llm = get_llm()
    if not llm:
        return fallback

    prompt = f"""
You are a retail analytics expert for a mobile-phone retailer. Return a crisp, bullet-style markdown.
Use ONLY the provided context and facts. Be specific, testable, and avoid hallucinations.

Context (JSON):
{json.dumps(context, indent=2, default=_json_default)}

Write:
- What the data says (trends/spikes/anomalies)
- 2-3 likely drivers grounded in columns we actually have
- 3 prioritized actions (specific, testable)

Return pure markdown (no code fences).
""".strip()

    try:
        res = llm.invoke(prompt)
        return (res.content if hasattr(res, "content") else str(res)).strip()
    except Exception:
        return fallback
