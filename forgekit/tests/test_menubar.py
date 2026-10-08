"""The menu bar wraps on a narrow window (0.9.0, forge-suite #40): every title stays on
screen and reachable; a wide window keeps the one-row bar it always had."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from textual.widgets import Static  # noqa: E402

from forgekit import ForgeApp  # noqa: E402
from forgekit.menu import MenuBar  # noqa: E402
from forgekit.theme import FORGE_CSS  # noqa: E402

# Help & Keys' real bar: seven sections and Quit — 66 cells of titles.
SECTIONS = ["Keys", "Start", "Workspaces", "Windows", "Apps", "Tools", "About"]
MENU = [{"id": s.lower(), "title": s, "kind": "section"} for s in SECTIONS] + [
    {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"},
]


class SevenTabs(ForgeApp):
    APP_NAME = "Seven tabs"
    MENU = MENU
    SHORTCUTS = [("Q", "quit")]
    ABOUT = {"name": "Seven tabs", "version": "0", "summary": "a test app", "authors": []}
    CSS = FORGE_CSS

    def compose_sections(self):
        for s in SECTIONS:
            yield Static(f"page {s}", id=f"sec-{s.lower()}")


def titles(app):
    return list(app.query(".menu-title"))


class RowSplit(unittest.TestCase):
    """The pure arithmetic, no screen needed."""

    def test_wide_window_is_one_row(self):
        bar = MenuBar(MENU)
        self.assertEqual(len(bar.layout_rows(100)), 1)

    def test_narrow_window_splits_in_order(self):
        bar = MenuBar(MENU)
        rows = bar.layout_rows(40)
        self.assertGreaterEqual(len(rows), 2)
        flat = [m["id"] for row in rows for m in row]
        self.assertEqual(flat, [m["id"] for m in MENU], "every entry, same order, none lost")
        for row in rows:
            self.assertLessEqual(sum(MenuBar._width(m) for m in row), 40, "a row never overflows")

    def test_a_title_wider_than_the_window_gets_its_own_row(self):
        bar = MenuBar([{"id": "a", "title": "A", "kind": "section"},
                       {"id": "long", "title": "A very long section name", "kind": "section"}])
        rows = bar.layout_rows(10)
        self.assertEqual([[m["id"] for m in r] for r in rows], [["a"], ["long"]])


class OnScreen(unittest.IsolatedAsyncioTestCase):
    async def test_narrow_window_shows_every_title(self):
        app = SevenTabs()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            ts = titles(app)
            self.assertEqual(len(ts), len(MENU))
            for t in ts:
                self.assertGreaterEqual(t.region.x, 0, t.id)
                self.assertLessEqual(t.region.x + t.region.width, 40,
                                     f"{t.id} would be cut off at the right edge (the #40 bug)")
            rows = {t.region.y for t in ts}
            self.assertGreaterEqual(len(rows), 2, "the titles use more than one row")
            self.assertGreaterEqual(app.query_one("#forge-header").region.height, 3,
                                    "the header grew with the bar (title row + 2 bar rows)")

    async def test_wide_window_keeps_one_row(self):
        app = SevenTabs()
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            rows = {t.region.y for t in titles(app)}
            self.assertEqual(len(rows), 1)
            self.assertEqual(app.query_one("#forge-header").region.height, 2, "as before 0.9.0")

    async def test_a_second_row_title_is_clickable_and_keeps_the_active_mark(self):
        app = SevenTabs()
        async with app.run_test(size=(40, 20)) as pilot:
            await pilot.pause()
            about = app.query_one("#menu-about")
            self.assertGreater(about.region.y, min(t.region.y for t in titles(app)), "About sits on a later row")
            await pilot.click("#menu-about")
            await pilot.pause()
            self.assertTrue(app.query_one("#menu-about").has_class("active"))
            # grow the window: the bar reflows to one row and About stays marked active
            await pilot.resize_terminal(120, 30)
            await pilot.pause()
            self.assertEqual(len({t.region.y for t in titles(app)}), 1)
            self.assertTrue(app.query_one("#menu-about").has_class("active"), "the active mark survives a reflow")


if __name__ == "__main__":
    unittest.main()
