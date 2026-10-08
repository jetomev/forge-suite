"""hypeForge Help & Keys 0.2.0 (F-48, Javier 2026-10-08): inside Settings it answered no shortcuts.
Now every tab has a unique underlined letter (Ctrl + it) and a number, made by forgekit 0.10.0;
started with --hypeforge it has no way to quit (Settings closes it)."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
APP = HERE / "applets/help/hypeforge-help"


def load_app_class():
    spec = importlib.util.spec_from_loader("hfhelp", importlib.machinery.SourceFileLoader("hfhelp", str(APP)))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    src = APP.read_text()
    body = src[src.index("    from forgekit import"):src.index("    HelpApp().run()")]
    ns = {name: getattr(m, name) for name in dir(m) if not name.startswith("__")}
    exec("\n".join(line[4:] if line.startswith("    ") else line for line in body.splitlines()), ns)
    return ns["HelpApp"]


class HelpKeys(unittest.IsolatedAsyncioTestCase):
    def active(self, app):
        return [w.id for w in app.query(".menu-title.active")]

    def test_no_two_tabs_share_a_letter(self):
        from forgekit import menu_key_clashes
        self.assertEqual(menu_key_clashes(load_app_class().MENU), [])

    async def test_every_tab_by_ctrl_letter_and_by_number(self):
        from forgekit import accel
        HelpApp = load_app_class()
        app = HelpApp()
        tabs = [m for m in HelpApp.MENU if m["id"] != "quit"]
        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.pause()
            for m in reversed(tabs):
                await pilot.press(f"ctrl+{accel(m)}")
                await pilot.pause(0.1)
                self.assertEqual(self.active(app), [f"menu-{m['id']}"], f"Ctrl+{accel(m).upper()}")
            for n, m in enumerate(tabs, 1):
                app.set_focus(None)
                await pilot.press(str(n))
                await pilot.pause(0.1)
                self.assertEqual(self.active(app), [f"menu-{m['id']}"], str(n))

    async def test_the_hint_counts_the_tabs(self):
        from forgekit import HintBar
        HelpApp = load_app_class()
        app = HelpApp()
        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.pause()
            text = str(app.query_one(HintBar).render())
            self.assertIn("1-7", text)
            self.assertIn("menu", text)

    async def test_inside_settings_nothing_closes_it(self):
        HelpApp = load_app_class()
        old = sys.argv
        sys.argv = ["hypeforge-help", "--hypeforge", "workspaces"]
        try:
            app = HelpApp()
            async with app.run_test(size=(120, 36)) as pilot:
                exits = []
                app.exit = lambda *a, **k: exits.append(1)
                await pilot.pause()
                self.assertEqual(len(app.query("#menu-quit")), 0)
                await pilot.pause(0.2)
                self.assertEqual(self.active(app), ["menu-page-workspaces"], "the page asked for, past --hypeforge")
                for key in ("q", "escape", "ctrl+q"):
                    await pilot.press(key)
                    await pilot.pause(0.1)
                self.assertEqual(exits, [])
                app.host_quit()
                self.assertEqual(exits, [1], "Settings' Quit closes it")
        finally:
            sys.argv = old


if __name__ == "__main__":
    unittest.main()
