import ast
from pathlib import Path


def parse(path: str) -> ast.Module:
    return ast.parse(Path(path).read_text(encoding="utf-8"))


def calls(tree: ast.Module, name: str) -> list[ast.Call]:
    found: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == name:
            found.append(node)
        elif isinstance(func, ast.Attribute) and func.attr == name:
            found.append(node)
    return found


def keyword(call: ast.Call, name: str) -> ast.expr | None:
    for item in call.keywords:
        if item.arg == name:
            return item.value
    return None
