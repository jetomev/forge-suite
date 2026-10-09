"""defaultappsForge's pages, driven headless on throwaway files (live=False writes nothing)."""

from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from textual.widgets import Collapsible, Select

from defaultappsforge import system as S
from defaultappsforge.app import DefaultAppsForgeApp, TickTable
from defaultappsforge.model import Session
from defaultappsforge.roles import ROLES
from tests.test_model import APPS, FILE


def run(c):
    return asyncio.run(c)


class Pages(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        d = Path(self.dir.name)
        (d / "mimeapps.list").write_text(FILE)
        self.se = Session(apps=dict(APPS), mimeapps=S.MimeApps(d / "mimeapps.list"), pools_path=d / "s.toml",
                          terminals=d / "t.list", ask_system=lambda t: None)

    def tearDown(self):
        self.dir.cleanup()

    def make(self, **kw):
        return DefaultAppsForgeApp(self.se, live=False, **kw)

    def test_the_menu_and_its_keys(self):
        app = self.make()
        self.assertEqual([m["title"] for m in app.MENU], ["Default Apps", "File Types", "Help", "Quit"])
        self.assertEqual([m.get("acc") for m in app.MENU[:3]], ["d", "f", "h"])

    def test_fourteen_drop_downs_under_defaults_and_selection(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                self.assertEqual(str(app.query_one("#da-t1").render()), "Defaults")
                self.assertEqual(str(app.query_one("#da-t2").render()), "Selection")
                selects = list(app.query(Select))
                self.assertEqual(len(selects), len(ROLES))
                self.assertTrue(app.query_one("#da-phone", Select).disabled, "Phone Numbers: none installed")
                self.assertEqual(app.query_one("#da-web", Select).value, "chrome.desktop")
                titles, first = app.query_one("#da-t2").region, app.query_one("#da-web", Select).region
                self.assertEqual(titles.x, first.x, "Selection sits over the drop-downs")
        run(go())

    def test_choosing_in_a_drop_down_counts_and_save_is_a_pop_up(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                app.query_one("#da-pdf", Select).value = "mpdf.desktop"
                await pilot.pause()
                self.assertEqual(app.session.change_count, 1)
                self.assertTrue(app.changes_bar.display)
                await pilot.press("f10")
                await pilot.pause()
                self.assertEqual(len(app.screen_stack), 2, "Save is a pop-up review")
                await pilot.press("enter")
                await pilot.pause()
                await pilot.pause()
                self.assertEqual(app.session.change_count, 0)
        run(go())

    def test_file_types_assign_and_clear_with_the_arrows(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.press("2")
                await pilot.pause()
                await pilot.pause()
                pool = app.query_one("#da-pool", TickTable)
                self.assertIn(".ics", pool.shown_ids())
                app.query_one("#da-c-calendar", Collapsible).collapsed = False
                await pilot.pause()
                pool.set_tick(".ics", True)
                await pilot.press("greater_than_sign")
                await pilot.pause()
                self.assertIn(".ics", app.session.pools["calendar"])
                self.assertNotIn(".ics", pool.shown_ids())
                t = app.query_one("#da-t-calendar", TickTable)
                t.set_tick(".ics", True)
                await pilot.press("less_than_sign")
                await pilot.pause()
                self.assertNotIn(".ics", app.session.pools["calendar"])
        run(go())

    def test_both_tables_start_on_the_same_line(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.press("2")
                await pilot.pause()
                await pilot.pause()
                self.assertEqual(app.query_one("#da-pool").region.y, app.query_one("#da-right").region.y)
        run(go())

    def test_quit_asks_and_hypeforge_has_no_quit(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                app.session.choose("pdf", "mpdf.desktop")
                await pilot.press("q")
                await pilot.pause()
                self.assertEqual(len(app.screen_stack), 2)
                await pilot.press("n")
                await pilot.pause()
        run(go())
        self.assertNotIn("quit", [m["id"] for m in DefaultAppsForgeApp(self.se, live=False, hypeforge=True).MENU])


if __name__ == "__main__":
    unittest.main()
