"""Every module themeForge imports is in docs/PACKAGING.md, so the package's depends=() can't fall behind the
code (Javier, 2026-10-11: "did you take notes of all of those dependencies … for the package?")."""

from __future__ import annotations

import ast
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
OURS = {"themeforge", "tests"}


def imported(root: Path) -> dict[str, set[str]]:
    """{top-level module: {files using it}} for every import in the code (not the tests)."""
    found: dict[str, set[str]] = {}
    for f in [HERE / "main.py"] + sorted((root).rglob("*.py")):
        for node in ast.walk(ast.parse(f.read_text())):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                [node.module] if isinstance(node, ast.ImportFrom) and node.module and not node.level else []
            for n in names:
                found.setdefault(n.split(".")[0], set()).add(f.name)
        for ns in re.findall(r'require_version\("([A-Za-z]+)"', f.read_text()):
            found.setdefault(f"gi:{ns}", set()).add(f.name)
    return found


def listed() -> str:
    return (HERE / "docs/PACKAGING.md").read_text()


class Needs(unittest.TestCase):
    def test_every_import_is_listed(self):
        doc = listed()
        third_party = {m: fs for m, fs in imported(HERE / "themeforge").items()
                       if m not in sys.stdlib_module_names and m not in OURS and m != "__future__"}
        self.assertTrue(third_party, "the scan found the app's imports")
        for module, files in sorted(third_party.items()):
            with self.subTest(module=module):
                name = module.split(":", 1)[1] if module.startswith("gi:") else module
                self.assertRegex(doc, rf"\b{re.escape(name)}\b",
                                 f"{module} (used in {', '.join(sorted(files))}) isn't in docs/PACKAGING.md")

    def test_the_gtk_pieces_are_named(self):
        found = imported(HERE / "themeforge")
        for ns in ("gi:Gtk", "gi:GtkLayerShell"):
            self.assertIn(ns, found, "the scan sees the GTK versions the overlay asks for")


if __name__ == "__main__":
    unittest.main()
