# D:\Zenith AI\MAS_UseCase_V2\runtime\runbook.py
from __future__ import annotations
from typing import Dict, Any, List
from pathlib import Path
from runtime.registry import load_registry
from runtime.loader import load_module_from_path


def execute_runbook(runbook: List[Dict[str, Any]], objective: str, memory: Dict[str, Any]) -> List[Dict[str, Any]]:
    reg = load_registry()
    out = []
    for step in runbook:
        agent_name = step.get("agent")
        if not agent_name:
            continue
        agent_info = reg.get("agents", {}).get(agent_name)
        if not agent_info:
            out.append({"agent": agent_name, "error": "Agent not registered"})
            continue
        agent_path = Path(agent_info["file"]).resolve()
        try:
            mod = load_module_from_path(agent_path)
        except ModuleNotFoundError as e:
            out.append({"agent": agent_name, "error": f"Import error in {agent_path.name}: {e}"})
            continue
        AgentCls = getattr(mod, agent_name)
        agent = AgentCls(objective=objective, memory=memory)
        result = agent.run()
        out.append({"agent": agent_name, **result})
    return out