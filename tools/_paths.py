# D:\Zenith AI\MAS_UseCase\tools\_paths.py
from pathlib import Path

def find_data_dir(start: Path) -> Path:
    cur = start.resolve()
    print(cur)
    for p in [cur] + list(cur.parents):
        candidate = p / "DB" / "data"
        if candidate.exists():
            return candidate
        sibling_candidate = p.parent / "DB" / "data"
        if sibling_candidate.exists():
            return sibling_candidate
    # Final fallback relative to MAS_UseCase
    fallback = (start.parent.parent / "DB" / "data").resolve()
    return fallback