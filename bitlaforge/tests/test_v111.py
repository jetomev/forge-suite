"""bitlaForge 1.1.1: the launcher entry ships (forge-suite#118, was bitlaforge#12), and the app points at
its home in the Forge Suite (moved 2026-10-22, D-60) — never at the archived repository."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Home(unittest.TestCase):
    def test_no_link_to_the_archived_repository(self):
        old = re.compile(r"github\.com/jetomev/bitlaforge(?![\w-])")
        hits = [f"{p.relative_to(ROOT)}:{n}" for p in sorted((ROOT / "bitlaforge").rglob("*"))
                if p.is_file() and p.suffix in (".py", ".md", ".txt")
                for n, line in enumerate(p.read_text(errors="replace").splitlines(), 1) if old.search(line)]
        self.assertEqual(hits, [], "the app still links to the archived repository")

    def test_the_links_name_the_suite(self):
        from bitlaforge import cli
        self.assertIn("github.com/jetomev/forge-suite/tree/main/bitlaforge", cli.USAGE, "--help names the manual in its new home")


if __name__ == "__main__":
    unittest.main()
