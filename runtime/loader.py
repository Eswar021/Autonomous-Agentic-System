# D:\Zenith AI\MAS_UseCase\runtime\loader.py
from __future__ import annotations
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Callable


def load_module_from_path(module_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore
    return module


def resolve_callable(module: ModuleType, name: str) -> Callable:
    fn = getattr(module, name)
    if not callable(fn):
        raise TypeError(f"{name} in {module.__name__} is not callable")
    return fn