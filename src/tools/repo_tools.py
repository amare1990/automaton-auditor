import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict
import shlex
import ast


def clone_repo_sandbox(repo_url: str) -> Path:
    """Clone a repository into an isolated temporary directory and return the Path.

    Uses a temporary directory to ensure sandboxing. Caller is responsible for
    retaining the path while needed (TemporaryDirectory() context manager will
    clean up when out of scope if used that way).
    """
    tmp = tempfile.TemporaryDirectory(prefix="repo_sandbox_")
    dest = Path(tmp.name)
    try:
        subprocess.run(["git", "clone", repo_url, str(dest)], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        # propagate a readable error
        raise RuntimeError(f"git clone failed: {exc.stderr}")
    return dest


def extract_git_history(repo_path: Path, limit: int = 200) -> List[Dict[str, str]]:
    """Return commit history as list of dicts: {hash, timestamp, message}.
    """
    result = subprocess.run(
        ["git", "-C", str(repo_path), "log", f"-n{limit}", "--pretty=%H|%cI|%s"],
        capture_output=True,
        text=True,
        check=True,
    )
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    commits = []
    for line in lines:
        try:
            h, ts, msg = line.split("|", 2)
        except ValueError:
            continue
        commits.append({"hash": h, "timestamp": ts, "message": msg})
    return commits


def analyze_graph_structure(repo_path: Path) -> Dict[str, List[str]]:
    """Do a lightweight AST scan for graph wiring patterns.

    Returns a dict with keys like 'add_edge_calls' and 'stategraph_inits'
    mapping to lists of file locations (relative to repo_path).
    """
    results = {"add_edge_calls": [], "add_conditional_edges": [], "stategraph_inits": []}

    for pyfile in repo_path.rglob("*.py"):
        try:
            src = pyfile.read_text(encoding="utf-8")
        except Exception:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            # detect builder.add_edge / builder.add_conditional_edges
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                attr = node.func.attr
                if attr == "add_edge":
                    results["add_edge_calls"].append(str(pyfile))
                if attr == "add_conditional_edges":
                    results["add_conditional_edges"].append(str(pyfile))

            # detect StateGraph(...) instantiation
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "StateGraph":
                    results["stategraph_inits"].append(str(pyfile))

    return results
