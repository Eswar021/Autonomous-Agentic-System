# D:\Zenith AI\MAS_UseCase_V2\runtime\registry.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Optional

REGISTRY_PATH = Path("registry") / "generated.json"
DEFAULT_REG: Dict[str, Any] = {"tools": {}, "agents": {}, "metadata": {"datasets": {}}}


def _safe_write(payload: Dict[str, Any]) -> None:
    REGISTRY_PATH.parent.mkdir(exist_ok=True)
    tmp = REGISTRY_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(REGISTRY_PATH)


def load_registry() -> Dict[str, Any]:
    if not REGISTRY_PATH.exists():
        _safe_write(DEFAULT_REG)
        return {**DEFAULT_REG}
    try:
        text = REGISTRY_PATH.read_text(encoding="utf-8")
        if not text.strip():
            _safe_write(DEFAULT_REG)
            return {**DEFAULT_REG}
        data = json.loads(text)
        if not isinstance(data, dict):
            _safe_write(DEFAULT_REG)
            return {**DEFAULT_REG}
        for k in ("tools", "agents", "metadata"):
            data.setdefault(k, DEFAULT_REG.get(k, {}))
        data["metadata"].setdefault("datasets", {})
        return data
    except Exception:
        _safe_write(DEFAULT_REG)
        return {**DEFAULT_REG}


def save_registry(reg: Dict[str, Any]) -> None:
    _safe_write(reg)

# ---------- Convenience updaters ----------

def set_datasets_metadata(meta: Dict[str, Any]) -> None:
    reg = load_registry()
    reg.setdefault("metadata", {}).setdefault("datasets", {})
    reg["metadata"]["datasets"] = meta
    save_registry(reg)


def register_tool(name: str, file: str, description: Optional[str] = None) -> None:
    reg = load_registry()
    reg.setdefault("tools", {})[name] = {"file": file, "description": description or ""}
    save_registry(reg)


def register_agent(name: str, file: str, description: Optional[str] = None) -> None:
    reg = load_registry()
    reg.setdefault("agents", {})[name] = {"file": file, "description": description or ""}
    save_registry(reg)