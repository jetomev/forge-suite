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
    import shlex
    ns = {"os": os, "sys": sys, "shlex": shlex, "pages": m.pages, "VERSION": m.VERSION}
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
            pane = app.query_one("#hf-pane-0")
            end = 0
            for _ in range(40):
                await pilot.pause(0.1)
                if any("hello from inside" in ln for ln in pane.lines_plain()):
                    break
            self.assertTrue(any("hello from inside" in ln for ln in pane.lines_plain()), pane.lines_plain()[:5])
            self.assertTrue(pane.display and pane.region.x > lst.region.x + lst.region.width - 1, "the pane sits right of the list")
            self.assertGreater(pane.region.width, 60)
            self.assertIs(app.focused, pane, "the keys go to the running program")
            # 0.2 (Javier): Settings has no bar and no keys of its own; a click on the list is the way back
            self.assertFalse(app.query_one("#forge-menubar").display, "Settings' own menu bar is hidden")
            self.assertEqual([str(o.prompt) for o in lst._options][-4:], ["Manual", "License", "About", "Quit"])
            await pilot.click("#hf-pages")
            await pilot.pause()
            self.assertIs(app.focused, lst, "a click on the list brings the keys back")
            self.assertTrue(pane.running, "the program keeps running meanwhile")
            # 0.3: switching pages keeps the app you leave; coming back shows the same pane
            lst.highlighted = 1
            await pilot.press("enter")
            await pilot.pause(0.5)
            second = app.query_one("#hf-pane-1")
            self.assertTrue(second.display and not pane.display, "the second page's pane is on screen")
            self.assertTrue(pane.running, "the first app still runs, hidden")
            self.assertTrue(second.running)
            await pilot.click("#hf-pages")
            lst.highlighted = 0
            await pilot.press("enter")
            await pilot.pause(0.3)
            self.assertTrue(pane.display and not second.display, "back to the first pane")
            self.assertTrue(any("hello from inside" in ln for ln in pane.lines_plain()), "as we left it")
            # Settings has no shortcuts of its own: Ctrl+H reaches the pane, not forgekit's Help
            await pilot.press("ctrl+h")
            await pilot.pause(0.2)
            self.assertEqual(type(app.screen).__name__, "Screen", "no Settings help screen opened on Ctrl+H")
            self.assertFalse(app.query_one("#forge-menubar").display)
            pane.terminate(); second.terminate()


if __name__ == "__main__":
    unittest.main()
