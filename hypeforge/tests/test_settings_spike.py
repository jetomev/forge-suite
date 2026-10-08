"""hypeForge Settings — the spike (2026-10-07): a Forge app runs inside the control centre's
terminal pane; the list keeps the left, the pane the right; F2 goes back to the list."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
APP = HERE / "applets/settings/hypeforge-settings"


def load_app_class():
    """Import the applet as a module and build its App class without running it."""
    spec = importlib.util.spec_from_loader("hfsettings", importlib.machinery.SourceFileLoader("hfsettings", str(APP)))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    # main() builds the class and runs it; rebuild the class the same way without .run()
    src = APP.read_text()
    body = src[src.index("    from textual.app import ComposeResult"):src.index("    SettingsApp().run()")]
    ns = {"os": os, "sys": sys, "pages": m.pages, "VERSION": m.VERSION}
    exec("\n".join(line[4:] if line.startswith("    ") else line for line in body.splitlines()), ns)
    return ns["SettingsApp"], m


class Spike(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        conf = self.dir / "settings.toml"
        conf.write_text('[[page]]\nname = "Colours"\nsummary = "a tiny coloured program"\n'
                        'command = "sh -c \'printf \\"\\\\033[31mred\\\\033[0m hello from inside\\\\n\\"; sleep 30\'"\n'
                        '[[page]]\nname = "Second"\nsummary = "another"\ncommand = "sleep 30"\n')
        self._old = os.environ.get("XDG_CONFIG_HOME")
        os.environ["XDG_CONFIG_HOME"] = str(self.dir)
        (self.dir / "hypeforge/applets").mkdir(parents=True)
        conf.rename(self.dir / "hypeforge/applets/settings.toml")

    def tearDown(self):
        if self._old is None:
            os.environ.pop("XDG_CONFIG_HOME", None)
        else:
            os.environ["XDG_CONFIG_HOME"] = self._old

    async def test_a_program_runs_in_the_pane_on_the_right(self):
        SettingsApp, m = load_app_class()
        app = SettingsApp()
        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.pause()
            lst = app.query_one("#hf-pages")
            self.assertEqual(lst.region.x, 2, "the list starts at the left edge of the work area")
            self.assertEqual(lst.region.width, 30)
            self.assertIs(app.focused, lst, "the list has the keys at start")
            await pilot.press("enter")                       # open the first page
            pane = app.query_one("#hf-pane")
            end = 0
            for _ in range(40):
                await pilot.pause(0.1)
                if any("hello from inside" in ln for ln in pane.lines_plain()):
                    break
            self.assertTrue(any("hello from inside" in ln for ln in pane.lines_plain()), pane.lines_plain()[:5])
            self.assertTrue(pane.display and pane.region.x > lst.region.x + lst.region.width - 1, "the pane sits right of the list")
            self.assertGreater(pane.region.width, 60)
            self.assertIs(app.focused, pane, "the keys go to the running program")
            await pilot.press("f2")
            await pilot.pause()
            self.assertIs(app.focused, lst, "F2 brings the keys back to the list")
            self.assertTrue(pane.running, "the program keeps running meanwhile")
            pane.terminate()


if __name__ == "__main__":
    unittest.main()
