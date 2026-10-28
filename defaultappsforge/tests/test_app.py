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
                # nothing installed for phone numbers, but Google Voice is a web app choice since D-5 (2026-10-27)
                self.assertFalse(app.query_one("#da-phone", Select).disabled, "Phone Numbers: Google Voice offered")
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



class AnyAppAndFindMore(Pages):
    """D-5 (Javier, 2026-10-27): "offer an option for one to look and select the app that one wants"."""

    def test_each_list_ends_with_any_app_and_find_more(self):
        from defaultappsforge.app import ANY_APP, FIND_MORE
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                for sel in app.query(Select):
                    values = [v for _l, v in sel._options]
                    self.assertEqual(values[-2:], [ANY_APP, FIND_MORE], sel.id)
        run(go())

    def test_any_app_picks_an_app_that_doesnt_claim_the_job(self):
        from forgekit import FilterPicker
        from defaultappsforge.app import ANY_APP
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                sel = app.query_one("#da-pdf", Select)
                sel.value = ANY_APP
                await pilot.pause()
                picker = app.screen
                self.assertIsInstance(picker, FilterPicker)
                self.assertNotIn("gimp.desktop", [a.id for a in self.se.candidates("pdf")], "GIMP doesn't claim PDFs")
                picker.dismiss("gimp.desktop")
                await pilot.pause()
                self.assertEqual(self.se.apps_now["pdf"], "gimp.desktop")
                self.assertEqual(app.query_one("#da-pdf", Select).value, "gimp.desktop")
        run(go())

    def test_find_more_opens_nogforge_searching(self):
        from defaultappsforge.app import FIND_MORE
        ran = []
        orig = S.find_more
        S.find_more = lambda words, run=None: ran.append(words)
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                sel = app.query_one("#da-email", Select)
                before = sel.value
                sel.value = FIND_MORE
                await pilot.pause()
                self.assertEqual(ran, ["email"])
                self.assertEqual(sel.value, before, "the choice stays what it was")
        try:
            run(go())
        finally:
            S.find_more = orig

    def test_find_more_command(self):
        cmd = S.find_more("email", run=lambda *a, **k: None)
        self.assertEqual(cmd[:4], ["alacritty", "--class", "nogforge", "-e"])
        self.assertEqual(cmd[-2:], ["--search", "email"])

if __name__ == "__main__":
    unittest.main()


class CommandLine(unittest.TestCase):
    """--help and --version answer and exit, never opening the app (1.0.0: `--help` opened the whole
    app, found while preparing the release); a word it doesn't know is refused, never ignored."""

    def run_main(self, argv):
        import contextlib
        import io
        from defaultappsforge.app import main
        from unittest import mock
        out, err = io.StringIO(), io.StringIO()
        opened = []
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                mock.patch("defaultappsforge.app.DefaultAppsForgeApp.run", lambda *_a, **_k: opened.append("app")):
            code = main(argv)
        return code, out.getvalue(), err.getvalue(), opened

    def test_help_and_version_answer_without_opening(self):
        from defaultappsforge import __version__
        code, out, _e, opened = self.run_main(["--help"])
        self.assertEqual((code, opened), (0, []))
        self.assertIn("defaultappsforge --version", out)
        self.assertNotIn("hypeforge", out.lower())
        code, out, _e, opened = self.run_main(["--version"])
        self.assertEqual((code, out.strip(), opened), (0, f"defaultappsForge {__version__}", []))

    def test_an_unknown_word_is_refused(self):
        code, _o, err, opened = self.run_main(["--frobnicate"])
        self.assertEqual((code, opened), (2, []))
        self.assertIn("--frobnicate", err)

    def test_with_no_words_the_app_opens(self):
        code, _o, _e, opened = self.run_main([])
        self.assertEqual((code, opened), (0, ["app"]))
