# D:\Zenith AI\MAS_UseCase_V2\planning\agent_planner.py
from __future__ import annotations
import json, re, os
from typing import Dict, Any, Optional

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    ChatGoogleGenerativeAI = None

# --- Retail base context (NovaMobile) ---
BASE_CONTEXT_RETAIL = """
You are the planner for NovaMobile Retail (multi-region mobile-phone retailer).

Business primitives:
- Products: flagship, mid-range, entry-level phones; accessories (chargers, cases, wearables).
- Channels: Stores, Online, Partners.
- Regions: North, South, East, West.
- Constraints: promotions ≤ 15% (VP approval required if higher); inventory transfers ≤ 20%/week; target stockout_rate < 2%.
- Seasonality: Q4 demand spike; heat reduces South footfall in May-June.
- Prefer experiments (A/B, geo-split) over blanket changes.

Planning goal:
- Given an objective, propose the agents and any missing zero‑arg tools they need, then produce a runbook.
""".strip()

PLANNER_SCHEMA = """
{
  "goals": ["..."],
  "tools_to_create": [
    {
      "name": "...",
      "description": "Business purpose + exact logic (filters, windows, joins, dedupe), data-quality checks, validations, failure modes, performance notes.",
      "inputs": [],
      "outputs": [{"name":"...","type":"pd.DataFrame","description":"...","schema":"optional"}],
      "datasets": ["..."],
      "assumptions": ["List all hard assumptions explicitly"]
    }
  ],
  "agents_to_create": [
    {
      "name":"...",
      "goal":"Business role & how it moves KPIs using tools",
      "uses_tools":["..."],
      "inputs": [],
      "outputs":[{"name":"summary","type":"markdown"},{"name":"table","type":"pd.DataFrame"}],
      "implementation_notes":"Decision logic, ordering, empty-data handling, minimal facts, thresholds"
    }
  ],
  "runbook": [
    {"agent":"ExistingOrProposedAgentName", "inputs": {} }
  ]
}
""".strip()


def _get_llm():
    key = os.getenv("GOOGLE_API_KEY")
    if not key or ChatGoogleGenerativeAI is None:
        return None
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=key, temperature=0.2)


def _robust_json(text: str) -> Optional[dict]:
    text = str(text).strip().strip("```").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        return None


def build_planner_prompt(
    objective: str,
    datasets_meta_json: str,
    business_yaml: str,
    existing_tools_json: str,
    existing_agents_json: str
) -> str:
    return f"""
You are the **Agent Planner** for NovaMobile Retail.

Based on the business use case, analyze and identify all required agents and tools for the multi-agent system.
Return ONLY valid JSON (no fences) that matches this schema:
{PLANNER_SCHEMA}

Authoring rules (MANDATORY)
- Design agents first (roles & handoffs), not tasks.
- Reuse existing zero-arg tools if they suffice; propose new tools only for real gaps.
- Use ONLY columns present in Dataset Metadata.
- New tools: must read via `tools._paths.find_data_dir(Path(__file__))`, be zero-arg, compute internal filters (e.g., latest year), return DataFrame.
- Agents must return: summary (markdown), table (DataFrame), facts (dict) and call `agents.base.llm_analyze(context, fallback)`.
- Experiments preferred (A/B, geo-split) over blanket changes.
- Respect constraints: promotions ≤ 15%, transfers ≤ 20%/week, stockout_rate < 2%.

Dataset Selection Rules (MANDATORY)
- Objectives about sales/units/time → prefer sales.csv (via `sales_this_year`) for core performance.
- Use kpi_results.csv for drivers (marketing_spend, competitor_price, inventory_count, stockout_flag, temperature).
- Objectives about reviews/sentiment → prefer reviews.csv (via `reviews_this_year`).

Base Retail Context:
{BASE_CONTEXT_RETAIL}

Dataset Metadata (AUTO‑DISCOVERED; use only these columns):
{datasets_meta_json}

Existing Zero‑Arg Tools:
{existing_tools_json}

Existing Agents:
{existing_agents_json}

Objective:
{objective}

Business YAML (reference only; do not contradict):
---
{business_yaml}
---
""".strip()


def plan(objective: str, datasets_meta_json: str, business_yaml: str,
         existing_tools_json: str, existing_agents_json: str) -> Dict[str, Any]:
    llm = _get_llm()
    if not llm:
        # deterministic fallback
        return {
            "goals": ["Explain this year's sales and reviews."],
            "tools_to_create": [],
            "agents_to_create": [],
            "runbook": [
                {"agent": "SalesThisYearAnalyst", "inputs": {}},
                {"agent": "ReviewThisYearInvestigator", "inputs": {}},
            ],
        }

    prompt = build_planner_prompt(
        objective, datasets_meta_json, business_yaml, existing_tools_json, existing_agents_json
    )

    # Debug echo – set ZENITH_DEBUG_PROMPTS=1 to print
    if os.getenv("ZENITH_DEBUG_PROMPTS", "0") in ("1", "true", "True"):
        print("\n\n==================== DEBUG: PLANNER PROMPT ====================\n")
        print(prompt)
        print("\n==================== END PLANNER PROMPT ====================\n\n")

    res = llm.invoke(prompt)
    data = _robust_json(res.content if hasattr(res, "content") else str(res))
    if not data:
        return {
            "goals": [objective],
            "tools_to_create": [],
            "agents_to_create": [],
            "runbook": [],
        }
    return data
