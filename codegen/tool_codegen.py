# D:\Zenith AI\MAS_UseCase_V2\codegen\tool_codegen.py
from __future__ import annotations
import json, re, os
from typing import Dict, Any, Optional

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    ChatGoogleGenerativeAI = None

TOOL_PROMPT = r"""
You will return a **single Python module** for a **ZERO‑ARG tool** in this NovaMobile Retail codebase.

Output ONLY valid JSON:
{
  "filename": "snake_case_filename.py",
  "code": "<FULL PYTHON MODULE CODE>"
}

Constraints:
- The function must be zero-arg and named exactly [[tool_name]]().
- Return type: pandas.DataFrame.
- MUST import: `from tools._paths import find_data_dir` and do: `data_dir = find_data_dir(Path(__file__))`.
- Read CSVs ONLY from `data_dir` (sales.csv, reviews.csv, customers.csv, kpi_results.csv).
- Never hard-code absolute paths.
- Parse dates after read: `df['date'] = pd.to_datetime(df['date'], errors='coerce')` (and for `review_date` if used).
- Join only if key columns exist and make business sense (e.g., sales.customer_id ↔ customers.customer_id).
- Compute internal filters (e.g., most recent year) — ZERO ARGS.
- No prints; clean, lint-safe Python.
- Do **NOT** pass unexpected parameters to pandas APIs (no `errors=` on `read_csv`); do **NOT** use deprecated `date_parser`.
- Prefer canonical aggregation field names where sensible: `revenue`, `sales_units`, `average_price`, `stockout_rate`.
- If a needed column is missing, compute a safe fallback (e.g., `stockout_rate` from `stockout_flag`).

Context:
- Tool spec (freeform): [[tool_description]]
- Datasets & columns (JSON): [[datasets_json]]
- Existing tools (names): [[existing_tools]]
""".strip()


def _get_llm():
    key = os.getenv("GOOGLE_API_KEY")
    if not key or ChatGoogleGenerativeAI is None:
        return None
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=key, temperature=0.2)


def _robust_json(text: str) -> Optional[dict]:
    text = text.strip().strip("```").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        return None


def fmt(template: str, mapping: dict) -> str:
    out = template
    for k, v in mapping.items():
        out = out.replace(f"[[{k}]]", str(v))
    return out


def generate_tool_module(spec: Dict[str, Any], datasets_json: str, existing_tool_names: str) -> Dict[str, str]:
    name = spec.get("name") or "unnamed_tool"
    description = spec.get("description", "")
    llm = _get_llm()

    if not llm:
        filename = f"{re.sub(r'[^0-9a-zA-Z_]+', '_', name).lower()}.py"
        code = f"""import pandas as pd
from pathlib import Path
from tools._paths import find_data_dir

def {name}() -> pd.DataFrame:
    data_dir = find_data_dir(Path(__file__))
    return pd.DataFrame()
"""
        return {"filename": filename, "code": code}

    prompt = fmt(TOOL_PROMPT, {
        "tool_name": name,
        "tool_description": description,
        "datasets_json": datasets_json,
        "existing_tools": existing_tool_names,
    })

    # Debug echo
    if os.getenv("ZENITH_DEBUG_PROMPTS", "0") in ("1", "true", "True"):
        print("\n\n==================== DEBUG: TOOL CODEGEN PROMPT ====================\n")
        print(prompt)
        print("\n==================== END TOOL CODEGEN PROMPT ====================\n\n")

    res = llm.invoke(prompt)
    data = _robust_json(res.content if hasattr(res, "content") else str(res))
    if not data or "code" not in data:
        filename = f"{re.sub(r'[^0-9a-zA-Z_]+', '_', name).lower()}.py"
        code = f"""import pandas as pd
from pathlib import Path
from tools._paths import find_data_dir

def {name}() -> pd.DataFrame:
    data_dir = find_data_dir(Path(__file__))
    return pd.DataFrame()
"""
        return {"filename": filename, "code": code}
    return {"filename": data.get("filename") or f"{name}.py", "code": data["code"]}
