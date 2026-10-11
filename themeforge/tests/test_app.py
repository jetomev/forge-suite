"""themeForge's page, driven headless with a stand-in look (nothing is applied for real)."""

from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from textual.widgets import Select

from themeforge.app import ThemeForgeApp, swatch_markup
from themeforge.look import Look
from tests.test_look import fake_home


def run(c):
    return asyncio.run(c)


class FakeLook(Look):
    def __init__(self, home, conf):
        super().__init__(home, conf)
        self.done = []

    def apply(self, style, theme):
        self.done.append(("apply", style, theme))
        (self.config / "hypeforge/theme/state.toml").write_text(f'style = "{style}"\ntheme = "{theme}"\n')
        return True, "the bar restarted"

    def undo(self):
        self.done.append(("undo",))
        return True, "back"


class Page(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        home, conf = fake_home(root), root / "config"
        (conf / "hypeforge/theme").mkdir(parents=True)
        (conf / "hypeforge/theme/state.toml").write_text('style = "rice"\ntheme = "mocha"\n')
        self.look = FakeLook(home, conf)

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_menu(self):
        app = ThemeForgeApp(self.look)
        self.assertEqual([m["title"] for m in app.MENU], ["Theme Picker", "Help", "Quit"])

    def test_two_drop_downs_showing_the_look_in_use(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                self.assertEqual(len(list(app.query(Select))), 2)
                self.assertEqual(app.query_one("#tf-style", Select).value, "rice")
                self.assertEqual(app.query_one("#tf-colour", Select).value, "mocha")
                self.assertIn("Linux rice", str(app.query_one("#tf-now").render()))
                self.assertEqual(str(app.query_one("#tf-style-about").render()), "about rice")
                self.assertFalse(app.changes_bar.display, "nothing picked yet")
        run(go())

    def test_picking_shows_the_bar_and_f10_applies_through_hypeforge(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                app.query_one("#tf-colour", Select).value = "white"
                await pilot.pause()
                self.assertTrue(app.changes_bar.display, "picked, not applied: the bar says so")
                await pilot.press("f10")
                await app.workers.wait_for_complete()
                await pilot.pause()
                self.assertEqual(self.look.done, [("apply", "rice", "white")])
                self.assertEqual(app.look.current(), ("rice", "white"))
                self.assertFalse(app.changes_bar.display, "applied: nothing pending")
        run(go())

    def test_the_same_look_again_does_nothing(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                await pilot.press("f10")
                await pilot.pause()
                self.assertEqual(self.look.done, [])
        run(go())

    def test_undo_runs_hypeforges_undo(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                app.action_undo()
                await app.workers.wait_for_complete()
                await pilot.pause()
                self.assertEqual(self.look.done, [("undo",)])
        run(go())

    def test_put_back_returns_the_drop_downs_to_the_look_in_use(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                app.query_one("#tf-style", Select).value = "classic"
                await pilot.pause()
                app.query_one("#tf-bar-back").press()
                await pilot.pause()
                await pilot.pause()
                self.assertEqual(app.query_one("#tf-style", Select).value, "rice")
                self.assertFalse(app.changes_bar.display)
        run(go())

    def test_the_swatch_is_coloured_blocks(self):
        self.assertIn("[on #123456]", swatch_markup(["#123456", "#abcdef"]))


if __name__ == "__main__":
    unittest.main()
