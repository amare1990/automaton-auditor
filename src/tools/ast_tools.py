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
        return {"file": str(path), "exports": [], "imports": [], "error": str(e)}

    return {
        "file": str(path),
        "exports": extract_exports(tree),
        "imports": extract_imports(tree),
    }
