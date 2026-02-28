# src/tools/repo_tools.py
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict
import ast
from typing_extensions import TypedDict

# -------------------------------------------------
# TypedDict for AST Graph Scan Results
# -------------------------------------------------
class GraphScanResult(TypedDict):
    add_edge_calls: List[str]
    add_conditional_edges: List[str]
    stategraph_inits: List[str]
    counts: Dict[str, int]

# -------------------------------------------------
# Repo Sandbox
# -------------------------------------------------
_SANDBOX_REGISTRY: List[tempfile.TemporaryDirectory] = []

def clone_repo_sandbox(repo_url: str, timeout: int = 60) -> Path:
    """Clone repository into an isolated temp dir."""
    tmp = tempfile.TemporaryDirectory(prefix="repo_sandbox_")
    _SANDBOX_REGISTRY.append(tmp)
    dest = Path(tmp.name)

    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(dest)],
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return dest

# -------------------------------------------------
# Git History
# -------------------------------------------------
def extract_git_history(repo_path: Path, limit: int = 200) -> List[Dict[str, str]]:
    """Return the last `limit` commit hashes, timestamps, and messages."""
    result = subprocess.run(
        ["git", "-C", str(repo_path), "log", f"-n{limit}", "--pretty=%H|%cI|%s"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    commits = []
    for line in result.stdout.splitlines():
        if "|" not in line:
            continue
        h, ts, msg = line.split("|", 2)
        commits.append({"hash": h, "timestamp": ts, "message": msg})
    return commits

# -------------------------------------------------
# AST Graph Structure Analysis
# -------------------------------------------------
def analyze_graph_structure(repo_path: Path) -> GraphScanResult:
    """
    Detect LangGraph wiring patterns in Python files using AST:
    - add_edge calls
    - add_conditional_edges calls
    - StateGraph initializations
    """
    results: GraphScanResult = {
        "add_edge_calls": [],
        "add_conditional_edges": [],
        "stategraph_inits": [],
        "counts": {},
    }

    for pyfile in repo_path.rglob("*.py"):
        try:
            tree = ast.parse(pyfile.read_text(encoding="utf-8"))
        except Exception:
            continue

        rel = str(pyfile.relative_to(repo_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "add_edge":
                        results["add_edge_calls"].append(rel)
                    elif node.func.attr == "add_conditional_edges":
                        results["add_conditional_edges"].append(rel)
                elif isinstance(node.func, ast.Name):
                    if node.func.id == "StateGraph":
                        results["stategraph_inits"].append(rel)

    # Add summary counts
    results["counts"] = {
        "add_edge_calls": len(results["add_edge_calls"]),
        "add_conditional_edges": len(results["add_conditional_edges"]),
        "stategraph_inits": len(results["stategraph_inits"]),
    }

    return results

# -------------------------------------------------
# Repo Metadata Helpers
# -------------------------------------------------
def repo_file_stats(repo_path: Path) -> Dict[str, int]:
    """Quick structural stats for Python repo."""
    py_files = list(repo_path.rglob("*.py"))
    total_files = sum(1 for _ in repo_path.rglob("*") if _.is_file())
    return {"python_files": len(py_files), "total_files": total_files}
