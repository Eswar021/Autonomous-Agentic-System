# D:\Zenith AI\MAS_UseCase_V2\codegen\agent_codegen.py
from __future__ import annotations
import json, re, os
from typing import Dict, Any, Optional

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    ChatGoogleGenerativeAI = None

AGENT_PROMPT = r"""
You will return a **single Python module** defining a ZERO-ARG Agent class that calls one or more ZERO-ARG tools
and then asks an LLM to analyze via `agents.base.llm_analyze(context, fallback)`.

Output ONLY valid JSON:
{
  "filename": "ClassName.py",
  "code": "<FULL PYTHON MODULE CODE>"
}

Constraints:
- Class name must be exactly [[agent_name]].
- __init__(self, objective: str = "", memory: Optional[Dict[str, Any]] = None)
- run(self) -> Dict[str, Any] MUST return: summary (markdown str), table (pd.DataFrame), facts (dict).
- Import helper: `from agents.base import llm_analyze`.
- Import zero-arg tools by name:
  - Tools listed under **new_tool_names** MUST be imported from `created_tools.<snake_file>`.
  - All other tools MUST be imported from `tools.<snake_file>`.
- Facts must include minimal numeric aggregates (e.g., totals/means).
- Only pandas + stdlib; no scipy/stats.
- Never call non-existent DataFrame methods like `.use()`.
- After loading a DataFrame, ensure expected columns exist; if not, create them and coerce numerics:
  for col in ["revenue","sales_units","average_price","stockout_rate"]:
      if col not in df.columns: df[col] = pd.NA
      df[col] = pd.to_numeric(df[col], errors="coerce")
- Call pattern (MANDATORY):
    context = {"objective": self.objective, "memory": self.memory, "facts": facts}
    summary_md = llm_analyze(context, fallback)

NovaMobile Retail context applies (datasets: sales, reviews, customers, kpi_results; constraints: promo ≤15%, transfer ≤20%/wk, stockout <2%).

Inputs to the generator:
- Agent goal: [[agent_goal]]
- Tools to use (comma delimited names): [[uses_tools]]
- Datasets metadata (JSON): [[datasets_json]]
- ALL available zero‑arg tools (names): [[existing_tools]]
- Newly created tool names (names): [[new_tool_names]]
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


def generate_agent_module(spec: Dict[str, Any], datasets_json: str, all_tool_names: str, new_tool_names: str) -> Dict[str, str]:
    name = spec.get("name") or "UnnamedAgent"
    goal = spec.get("goal", "")
    uses_tools = ", ".join(spec.get("uses_tools", []))

    llm = _get_llm()
    if not llm:
        filename = f"{name}.py"
        code = (
            f"""import pandas as pd
from typing import Any, Dict, Optional
from agents.base import llm_analyze

class {name}:
    def __init__(self, objective: str = "", memory: Optional[Dict[str, Any]] = None):
        self.objective = objective or "{goal}"
        self.memory = memory or {{}}

    def run(self) -> Dict[str, Any]:
        facts = {{"note": "LLM key missing – deterministic stub"}}
        context = {{"objective": self.objective, "memory": self.memory, "facts": facts}}
        summary = llm_analyze(context, "{name}: no data yet.")
        return {{"summary": summary, "table": pd.DataFrame(), "facts": facts}}
"""
        )
        return {"filename": filename, "code": code}

    prompt = fmt(AGENT_PROMPT, {
        "agent_name": name,
        "agent_goal": goal,
        "uses_tools": uses_tools,
        "datasets_json": datasets_json,
        "existing_tools": all_tool_names,
        "new_tool_names": new_tool_names or "",
    })

    # Debug echo
    if os.getenv("ZENITH_DEBUG_PROMPTS", "0") in ("1", "true", "True"):
        print(f"\n\n==================== DEBUG: AGENT CODEGEN PROMPT ({name}) ====================\n")
        print(prompt)
        print(f"\n==================== END AGENT CODEGEN PROMPT ({name}) ====================\n\n")

    res = llm.invoke(prompt)
    data = _robust_json(res.content if hasattr(res, "content") else str(res))
    if not data or "code" not in data:
        filename = f"{name}.py"
        code = (
            f"""import pandas as pd
from typing import Any, Dict, Optional
from agents.base import llm_analyze

class {name}:
    def __init__(self, objective: str = "", memory: Optional[Dict[str, Any]] = None):
        self.objective = objective or "{goal}"
        self.memory = memory or {{}}

    def run(self) -> Dict[str, Any]:
        facts = {{"note": "LLM generation failed – stub"}}
        context = {{"objective": self.objective, "memory": self.memory, "facts": facts}}
        summary = llm_analyze(context, "{name}: no data yet.")
        return {{"summary": summary, "table": pd.DataFrame(), "facts": facts}}
"""
        )
        return {"filename": filename, "code": code}
    return {"filename": data.get("filename") or f"{name}.py", "code": data["code"]}
