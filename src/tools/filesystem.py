# src/tools/filesystem.py

import hashlib
import tempfile
from pathlib import Path


def make_temp_dir(prefix: str = "audit_") -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)

    return h.hexdigest()


def safe_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
