"""grubForge moved into the Forge Suite on 2026-10-22 (D-60, the last app to move): the app points at its home there, never at the
archived repository (its About page's Code link; the next version carries it)."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Home(unittest.TestCase):
    def test_no_link_to_the_archived_repository(self):
        old = re.compile(r"github\.com/jetomev/grubforge(?![\w-])")
        hits = [f"{p.relative_to(ROOT)}:{n}" for p in sorted((ROOT / "grubforge").rglob("*"))
                if p.is_file() and p.suffix in (".py", ".md", ".txt")
                for n, line in enumerate(p.read_text(errors="replace").splitlines(), 1) if old.search(line)]
        self.assertEqual(hits, [], "the app still links to the archived repository")

    def test_help_names_the_manual_in_the_suite(self):
        from grubforge import cli
        self.assertIn("github.com/jetomev/forge-suite/tree/main/grubforge", cli.USAGE)


if __name__ == "__main__":
    unittest.main()
