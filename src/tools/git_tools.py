# src/tools/git_tools.py
import subprocess
from pathlib import Path
from typing import List, Dict


def clone_repo(repo_url: str, dest: Path) -> Path:
    """
    Clone repo into dest directory.
    """
    dest.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").exists():
        subprocess.run(["git", "clone", repo_url, str(dest)], check=True)
    else:
        print(f"[Repo] Already cloned: {dest}")
    return dest


def get_commit_log(repo_path: Path, n: int = 20) -> List[str]:
    """
    Returns last n commit messages.
    """
    result = subprocess.run(
        ["git", "-C", str(repo_path), "log", f"-n{n}", "--pretty=%s"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.splitlines()


def list_files(repo_path: Path) -> List[Path]:
    """
    Returns all tracked files.
    """
    result = subprocess.run(
        ["git", "-C", str(repo_path), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [repo_path / f for f in result.stdout.splitlines()]
