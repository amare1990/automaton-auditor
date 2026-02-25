# src/tools/ast_tools.py

import ast
from pathlib import Path
from typing import Dict, List


def parse_python_file(path: Path) -> ast.AST:
    with open(path, "r", encoding="utf-8") as f:
        return ast.parse(f.read())


def extract_exports(tree: ast.AST) -> List[str]:
    exports = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            exports.append(node.name)

    return exports


def extract_imports(tree: ast.AST) -> List[str]:
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")

    return imports


def analyze_python_file(path: Path) -> Dict[str, list | str]:
    try:
        tree = parse_python_file(path)
    except SyntaxError as e:
        return {"file": str(path), "exports": [], "imports": [], "error": str(e), "safety_warnings": []}

    exports = extract_exports(tree)
    imports = extract_imports(tree)

    # Basic safety checks: look for dynamic execution and common unsafe patterns
    warnings: List[str] = []
    for node in ast.walk(tree):
        # eval/exec usage
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec"}:
                warnings.append(f"uses dynamic execution: {node.func.id}()")

        # subprocess usage detection
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
                warnings.append(f"calls subprocess.{node.func.attr}")

        # direct open/use of builtin open at top level
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
            warnings.append("uses builtin open(); review for safe paths and sanitization")

    return {
        "file": str(path),
        "exports": exports,
        "imports": imports,
        "safety_warnings": warnings,
    }
