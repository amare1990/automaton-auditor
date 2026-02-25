from pathlib import Path
from typing import List


def find_images(repo_path: Path) -> List[Path]:
    """
    Returns image files for optional inspection.
    """
    exts = {".png", ".jpg", ".jpeg", ".webp"}
    return [p for p in repo_path.rglob("*") if p.suffix.lower() in exts]


def inspect_images(_: List[Path]) -> List[str]:
    """
    Stub: return metadata only for now.
    """
    return ["Vision inspection skipped (optional tool)."]
