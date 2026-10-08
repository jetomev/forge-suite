#!/usr/bin/env python3
"""hypeForge commit check (F-47, 2026-10-07): every name an applet uses must be defined,
imported or built in. The Workspaces applet shipped with ``re.escape`` and no ``import re``
(since 2026-10-04); Python only notices when the line runs, which was at login — so the applet
died silently at start and Sway's stock keys took over. This catches that class before a commit.

A deliberately small checker (standard library only). It knows imports, defs, classes,
assignments, function arguments, loop and comprehension targets, ``with … as``, ``except … as``,
``global`` / ``nonlocal``. It does not follow ``from x import *`` (none here). Exit 1 on a hit.
"""

from __future__ import annotations

import ast
import builtins
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = sorted(ROOT.glob("applets/*/hypeforge-*")) + sorted(ROOT.glob("applets/common/*.py")) \
    + sorted(ROOT.glob("scripts/*.py"))
ALWAYS = set(dir(builtins)) | {"__file__", "__name__", "__doc__", "__spec__", "__builtins__"}


def defined_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                names.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, ast.ClassDef):
            names.add(n.name)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(n.name)
            for a in n.args.args + n.args.kwonlyargs + n.args.posonlyargs:
                names.add(a.arg)
            if n.args.vararg: names.add(n.args.vararg.arg)
            if n.args.kwarg: names.add(n.args.kwarg.arg)
        elif isinstance(n, ast.Lambda):
            for a in n.args.args + n.args.kwonlyargs:
                names.add(a.arg)
        elif isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            names.add(n.id)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            names.add(n.name)
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            names.update(n.names)
        elif isinstance(n, ast.MatchAs) and n.name:
            names.add(n.name)
    return names


def check(path: Path) -> list[str]:
    src = path.read_text()
    tree = ast.parse(src, filename=str(path))
    known = defined_names(tree) | ALWAYS
    hits = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id not in known:
            hits.append(f"{path.relative_to(ROOT)}:{n.lineno}: '{n.id}' is used but never defined or imported")
    return hits


def main() -> int:
    hits = [h for f in FILES if f.is_file() for h in check(f)]
    for h in hits:
        print(h)
    print(f"check-names: {len(FILES)} files, {len(hits)} undefined name(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
