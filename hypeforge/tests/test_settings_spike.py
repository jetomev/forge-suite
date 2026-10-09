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
    body = src[src.index("    sys.path.insert(0, str(HERE))"):src.index("    SettingsApp().run()")]
    import shlex
    import signal
    ns = {"os": os, "sys": sys, "shlex": shlex, "signal": signal, "pages": m.pages, "VERSION": m.VERSION,
          "HERE": m.HERE}
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
            lst.highlighted = 1                              # line 0 is Home (0.5.0)
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
            self.assertEqual([str(o.prompt)[2:] if ord(str(o.prompt)[0]) >= 0xE000 else str(o.prompt)
                              for o in lst._options][-4:],
                             ["Manual", "License", "About", "Quit"])        # each after its icon
            await pilot.click("#hf-pages")
            await pilot.pause()
            self.assertIs(app.focused, lst, "a click on the list brings the keys back")
            self.assertTrue(pane.running, "the program keeps running meanwhile")
            # 0.3: switching pages keeps the app you leave; coming back shows the same pane
            lst.highlighted = 2
            await pilot.press("enter")
            await pilot.pause(0.5)
            second = app.query_one("#hf-pane-1")
            self.assertTrue(second.display and not pane.display, "the second page's pane is on screen")
            self.assertTrue(pane.running, "the first app still runs, hidden")
            self.assertTrue(second.running)
            await pilot.click("#hf-pages")
            lst.highlighted = 1
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

# A stand-in Forge app: writes its arguments down; on SIGUSR1 (Settings' Quit) it closes at once,
# or, started with "dirty", prints a question and closes only on the answer "n".
FAKE = r"""
import os, signal, sys, time, tty
out = sys.argv[1]
open(out, "a").write(" ".join(sys.argv[2:]) + "\n")
dirty = "dirty" in sys.argv
asked = []
def ask(*_):
    if not dirty:
        sys.exit(0)
    asked.append(1)
    print("UNSAVED: quit without saving? n", flush=True)
signal.signal(signal.SIGUSR1, ask)
tty.setraw(0)
while True:
    try:
        b = os.read(0, 1)
    except InterruptedError:
        continue
    if asked and b == b"n":
        sys.exit(0)
"""


class QuitAsksEachApp(unittest.IsolatedAsyncioTestCase):
    """0.4.0 (Javier, 2026-10-08): Forge apps start with --hypeforge; Settings' Quit asks each one
    to close; one with something unsaved is shown and asks its own question; Settings closes after."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        fake = self.dir / "fake.py"
        fake.write_text(FAKE)
        self.log = self.dir / "argv.log"
        py = sys.executable
        conf = self.dir / "pages.toml"
        conf.write_text(
            f'[[page]]\nname = "Clean"\ncommand = "{py} {fake} {self.log} clean"\nforge = true\n'
            f'[[page]]\nname = "Dirty"\ncommand = "{py} {fake} {self.log} dirty"\nforge = true\n'
            f'[[page]]\nname = "Plain"\ncommand = "sleep 30"\n')
        self._old = os.environ.get("HYPEFORGE_SETTINGS_PAGES")
        os.environ["HYPEFORGE_SETTINGS_PAGES"] = str(conf)

    def tearDown(self):
        if self._old is None:
            os.environ.pop("HYPEFORGE_SETTINGS_PAGES", None)
        else:
            os.environ["HYPEFORGE_SETTINGS_PAGES"] = self._old

    async def open_all(self, app, pilot):
        for i in range(3):
            app.open_page(i)
            await pilot.pause(0.4)
        for _ in range(30):
            await pilot.pause(0.1)
            if self.log.exists() and len(self.log.read_text().splitlines()) == 2:
                break

    async def test_forge_apps_get_the_flag_and_others_do_not(self):
        SettingsApp, m = load_app_class()
        app = SettingsApp()
        async with app.run_test(size=(120, 36)) as pilot:
            await self.open_all(app, pilot)
            started = self.log.read_text().splitlines()
            self.assertEqual(sorted(started), ["clean --hypeforge", "dirty --hypeforge"])
            for pane in app.query("TerminalPane"):
                pane.terminate()

    async def test_quit_closes_the_clean_ones_and_waits_for_the_answer(self):
        SettingsApp, m = load_app_class()
        app = SettingsApp()
        async with app.run_test(size=(120, 36)) as pilot:
            exits = []
            app.exit = lambda *a, **k: exits.append(1)
            await self.open_all(app, pilot)
            panes = [app.query_one(f"#hf-pane-{i}") for i in range(3)]
            app.quit_all()
            for _ in range(30):
                await pilot.pause(0.1)
                if not panes[0].running and not panes[2].running and panes[1].display:
                    break
            self.assertFalse(panes[0].running, "the app with nothing unsaved closed at once")
            self.assertFalse(panes[2].running, "a plain program is simply closed")
            self.assertTrue(panes[1].running, "the one with something unsaved waits")
            self.assertTrue(panes[1].display, "and its page is shown")
            self.assertEqual(exits, [], "Settings waits for the answer")
            self.assertTrue(any("UNSAVED" in ln for ln in panes[1].lines_plain()))
            panes[1].write(b"n")
            for _ in range(30):
                await pilot.pause(0.1)
                if exits:
                    break
            self.assertEqual(exits, [1], "Settings closes once the last app has answered")

    async def test_about_and_license_open_on_the_right(self):
        SettingsApp, m = load_app_class()
        app = SettingsApp()
        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.pause()
            app.open_page(0)
            await pilot.pause(0.5)
            for act, wid in (("about", "#hf-about"), ("license", "#hf-license")):
                app.extra(act)
                await pilot.pause()
                self.assertEqual(len(app.screen_stack), 1, f"{act}: no window")
                self.assertTrue(app.query_one(wid).display, act)
                self.assertTrue(app.query_one("#hf-pages").display, "the list stays")
                self.assertFalse(app.query_one("#hf-pane-0").display)
                self.assertTrue(app.query_one("#hf-pane-0").running, "the app keeps running")
            app.open_page(0)
            await pilot.pause()
            self.assertFalse(app.query_one("#hf-license").display, "an app's page hides License again")
            for pane in app.query("TerminalPane"):
                pane.terminate()

    async def test_settings_has_no_menu_keys_of_its_own(self):
        SettingsApp, m = load_app_class()
        app = SettingsApp()
        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.pause()
            keys = set(app._bindings.key_to_bindings)
            self.assertFalse({"1", "2", "ctrl+s"} & keys, keys)


class HomePage(unittest.IsolatedAsyncioTestCase):
    """0.5.0 (#46; Javier picked cards, two columns): Settings opens on Home; a card per setting with
    its summary; a card with a page opens that page; a card without one does nothing harmful."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        conf = self.dir / "pages.toml"
        conf.write_text('[[page]]\nname = "Screens"\ncommand = "sleep 30"\n'
                        '[[page]]\nname = "Packages"\ncommand = "sleep 30"\n')
        self._old = os.environ.get("HYPEFORGE_SETTINGS_PAGES")
        os.environ["HYPEFORGE_SETTINGS_PAGES"] = str(conf)

    def tearDown(self):
        if self._old is None:
            os.environ.pop("HYPEFORGE_SETTINGS_PAGES", None)
        else:
            os.environ["HYPEFORGE_SETTINGS_PAGES"] = self._old

    async def test_opens_on_home_with_every_card_filled(self):
        SettingsApp, m = load_app_class()
        app = SettingsApp()
        async with app.run_test(size=(130, 40)) as pilot:
            for _ in range(30):
                await pilot.pause(0.1)
                if all(str(c.render()) != "…" for c in app.query(".hf-card")):
                    break
            self.assertTrue(app.query_one("#hf-home").display, "Home is what Settings opens on")
            self.assertEqual(app.query_one("#hf-pages").highlighted, 0)
            cards = list(app.query(".hf-card"))
            plain = lambda t: t[2:] if t and ord(t[0]) >= 0xE000 else t     # the name, after its icon
            self.assertEqual([plain(c.border_title) for c in cards],
                             ["Screens", "Workspaces", "Network", "Sound", "Printer", "Night light",
                              "Passwords", "Packages", "Boot Menu", "Terminal"])
            self.assertTrue(all(str(c.render()) not in ("", "…") for c in cards), "every card has its summary")
            xs = {c.region.x for c in cards}
            self.assertEqual(len(xs), 2, "two columns")
            self.assertTrue(all(c.region.height == 5 for c in cards), "three rows inside each box")
            self.assertTrue(any(str(c.render()).count("\n") == 2 for c in cards), "three lines of detail")

    async def test_icons_in_a_window_none_on_a_text_console(self):
        SettingsApp, m = load_app_class()
        pua = lambda t: any(0xF0000 <= ord(ch) <= 0xFFFFF or 0xE000 <= ord(ch) <= 0xF8FF for ch in t)
        for console, want in ((False, True), (True, False)):
            app = SettingsApp(console=console)
            async with app.run_test(size=(130, 40)) as pilot:
                await pilot.pause(0.2)
                lst = app.query_one("#hf-pages")
                prompts = [str(o.prompt) for o in lst._options]
                titles = [c.border_title for c in app.query(".hf-card")]
                self.assertEqual(all(pua(t) for t in prompts), want, f"list, console={console}")
                self.assertEqual(all(pua(t) for t in titles), want, f"cards, console={console}")
                self.assertTrue(prompts[0].endswith("Home") and titles[0].endswith("Screens"))

    async def test_a_card_opens_its_page(self):
        SettingsApp, m = load_app_class()
        app = SettingsApp()
        async with app.run_test(size=(130, 40)) as pilot:
            await pilot.pause(0.3)
            app.query_one("#hf-card-7").on_click()           # Packages
            await pilot.pause(0.5)
            self.assertFalse(app.query_one("#hf-home").display)
            self.assertTrue(app.query_one("#hf-pane-1").display, "the Packages page is shown")
            self.assertEqual(app.query_one("#hf-pages").highlighted, 2)
            app.query_one("#hf-card-1").on_click()           # Workspaces: no page yet, nothing breaks
            await pilot.pause(0.2)
            self.assertTrue(app.query_one("#hf-pane-1").display)
            app.extra("home")                                # back to Home from the list
            await pilot.pause(0.3)
            self.assertTrue(app.query_one("#hf-home").display)
            for pane in app.query("TerminalPane"):
                pane.terminate()


class HomeSummaries(unittest.TestCase):
    """Each card's summary is plain words and never raises — even with no tools and no settings at all."""

    def test_nothing_installed_nothing_breaks(self):
        import importlib, shutil as sh
        sys.path.insert(0, str(HERE / "applets/settings"))
        home = importlib.import_module("home")
        old_which, old_config, old_home = home.shutil.which, home.CONFIG, home.HOME
        empty = Path(tempfile.mkdtemp())
        try:
            home.shutil.which = lambda _n: None
            home.CONFIG, home.HOME = empty, empty
            rows = home.summaries()
        finally:
            home.shutil.which, home.CONFIG, home.HOME = old_which, old_config, old_home
        self.assertEqual(len(rows), 10)
        for title, lines, _page in rows:
            self.assertTrue(lines and all(isinstance(x, str) and x for x in lines), title)
            self.assertLessEqual(len(lines), 3, title)

    def test_a_card_that_breaks_never_takes_the_page_down(self):
        import importlib
        sys.path.insert(0, str(HERE / "applets/settings"))
        home = importlib.import_module("home")
        old = home.screens

        def boom():
            raise RuntimeError("a broken card")
        try:
            home.screens = boom
            rows = home.summaries()
        finally:
            home.screens = old
        self.assertEqual(rows[0][:2], ("Screens", [home.UNKNOWN]))
        self.assertEqual(len(rows), 10)


if __name__ == "__main__":
    unittest.main()
