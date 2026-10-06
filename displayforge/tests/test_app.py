"""displayForge · the app, driven in memory (Textual's test pilot) — no screen, no real Sway,
no real ddcutil, no real files: a fake swaymsg and a fake ddcutil write down what they get, and
every save goes to a throwaway folder (the paths are redirected; a test checks the real ones are
untouched)."""

from __future__ import annotations

import asyncio
import json
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from displayforge import brightness as B, saving as V, screens as S  # noqa: E402
from displayforge.app import DisplayForgeApp, IdentifyView, SettingsView  # noqa: E402
from displayforge.session import Session  # noqa: E402

DATA = Path(__file__).parent / "data/three-sceptre-y27.json"


def tool(folder: Path, name: str, body: str) -> str:
    p = folder / name
    p.write_text("#!/bin/sh\n" + body)
    p.chmod(p.stat().st_mode | stat.S_IEXEC)
    return str(p)


class App(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.sway = tool(self.tmp, "swaymsg", f'echo "$1" >> {self.tmp}/sway.log\n')
        self.ddc = tool(self.tmp, "ddcutil",
                        'case "$*" in\n'
                        '  "detect --brief") printf "Display 1\\n   I2C bus:  /dev/i2c-3\\nDisplay 2\\n   I2C bus:  /dev/i2c-4\\nDisplay 3\\n   I2C bus:  /dev/i2c-5\\n";;\n'
                        '  *getvcp*) echo "VCP 10 C 75 100";;\n'
                        f'  *setvcp*) echo "$*" >> {self.tmp}/ddc.log;;\n'
                        'esac\n')
        self.saved = (V.OUTPUTS, V.BACKUPS, B.CONFIG, V.SWAY_CONFIG)
        V.OUTPUTS, V.BACKUPS, B.CONFIG = self.tmp / "outputs", self.tmp / "backups", self.tmp / "screens.toml"
        V.SWAY_CONFIG = self.tmp / "sway-config"
        V.SWAY_CONFIG.write_text("output DP-1 mode 2560x1440@144Hz\ninclude ~/.config/sway/outputs\n")
        self.real = [Path.home() / ".config/sway/outputs", Path.home() / ".config/displayforge"]
        self.real_before = [p.exists() for p in self.real]
        self.session = Session(S.parse(json.loads(DATA.read_text())), {"names": {}, "bus": {}}, main="DP-3")

    def tearDown(self):
        V.OUTPUTS, V.BACKUPS, B.CONFIG, V.SWAY_CONFIG = self.saved
        self.assertEqual([p.exists() for p in self.real], self.real_before, "a real file was touched")

    def lines(self, name):
        p = self.tmp / name
        return p.read_text().splitlines() if p.exists() else []

    def run_app(self, steps):
        app = DisplayForgeApp(self.session, swaymsg=self.sway, ddcutil=self.ddc)

        async def go():
            async with app.run_test(size=(100, 34)) as pilot:
                await pilot.pause(0.3)
                await steps(app, pilot)
        asyncio.run(go())
        return app

    def test_change_try_keep_save(self):
        async def steps(app, pilot):
            se = self.session
            await pilot.press("2")
            await pilot.pause(0.3)
            hz120 = [m for m in se.screen("DP-3").rates(2560, 1440) if m.hz == 120][0]
            se.change("DP-3", mode=hz120)
            app.query_one(SettingsView)._changed()
            await pilot.pause(0.3)
            self.assertEqual(se.changes(), [("Screen 1 · DP-3 · refresh rate", "144 Hz", "120 Hz")])
            await pilot.press("f9")
            await pilot.pause(0.6)
            await pilot.press("enter")                       # Keep it
            await pilot.pause(0.4)
            self.assertEqual(se.screen("DP-3", pending=False).mode.hz, 120)
            self.assertEqual(se.to_save(), [("Screen 1 · DP-3 · refresh rate", "144 Hz", "120 Hz")])
            await pilot.press("f10")
            await pilot.pause(0.5)
            await pilot.click("#save")
            await pilot.pause(0.6)
        self.run_app(steps)
        self.assertEqual(len(self.lines("sway.log")), 1)            # one change, kept: no undo
        self.assertIn("@120.", self.lines("sway.log")[0])
        self.assertIn("output DP-3 mode 2560x1440@120.001Hz", (self.tmp / "outputs").read_text())

    def test_save_warns_when_sway_does_not_read_the_file(self):
        V.SWAY_CONFIG.write_text("output DP-1 mode 2560x1440@144Hz\n")    # no include line
        seen = []

        async def steps(app, pilot):
            se = self.session
            se.change("DP-1", scale=0.9)
            await pilot.press("f9")
            await pilot.pause(0.6)
            await pilot.press("enter")
            await pilot.pause(0.4)
            await pilot.press("f10")
            await pilot.pause(0.5)
            await pilot.click("#save")
            await pilot.pause(0.6)
            seen.extend(n.title for n in app._notifications)
        self.run_app(steps)
        self.assertIn("One line missing", seen)

    def test_save_quiet_when_sway_reads_the_file(self):
        seen = []

        async def steps(app, pilot):
            self.session.change("DP-1", scale=0.9)
            await pilot.press("f9")
            await pilot.pause(0.6)
            await pilot.press("enter")
            await pilot.pause(0.4)
            await pilot.press("f10")
            await pilot.pause(0.5)
            await pilot.click("#save")
            await pilot.pause(0.6)
            seen.extend(n.title for n in app._notifications)
        self.run_app(steps)
        self.assertIn("Saved", seen)
        self.assertNotIn("One line missing", seen)

    def test_go_back_now_undoes(self):
        async def steps(app, pilot):
            se = self.session
            se.change("DP-1", scale=0.9)
            app.refresh_state()
            await pilot.press("f9")
            await pilot.pause(0.6)
            await pilot.press("escape")                      # Go back now
            await pilot.pause(0.4)
            self.assertEqual(se.screen("DP-1", pending=False).scale, 1.0)
        self.run_app(steps)
        sent = self.lines("sway.log")
        self.assertEqual(sent, ["output DP-1 scale 0.9", "output DP-1 scale 1"])

    def test_overlap_is_refused(self):
        async def steps(app, pilot):
            se = self.session
            se.change("DP-1", x=0)                           # on top of DP-2
            await pilot.press("f9")
            await pilot.pause(0.4)
        self.run_app(steps)
        self.assertEqual(self.lines("sway.log"), [])

    def test_arrange_moves_and_others_make_room(self):
        async def steps(app, pilot):
            await pilot.press("3")
            await pilot.pause(0.3)
            await pilot.press("right")                       # screen 2 (left) to the right of 1
            await pilot.pause(0.3)
        self.run_app(steps)
        xs = {s.name: s.x for s in self.session.pending}
        self.assertEqual(xs, {"DP-3": 0, "DP-2": 2560, "DP-1": 5120})
        self.assertEqual(S.overlaps(self.session.pending), [])

    def test_identify_remembers_and_restores_brightness(self):
        async def steps(app, pilot):
            await pilot.press("5")
            await pilot.pause(0.3)
            await pilot.click("#id-start")
            await pilot.pause(3.7)
            for name in ("DP-2", "DP-3", "DP-1"):
                await pilot.click(f"#id-is-{name}")
                await pilot.pause(3.7)
        self.run_app(steps)
        self.assertEqual(self.session.remembered["bus"], {"DP-2": 3, "DP-3": 4, "DP-1": 5})
        self.assertEqual(B.load(self.tmp / "screens.toml")["bus"], {"DP-2": 3, "DP-3": 4, "DP-1": 5})
        # each control went dark, then back to what it was (75)
        self.assertEqual(self.lines("ddc.log"), [f"--bus {b} setvcp 10 {v}" for b in (3, 4, 5) for v in (0, 75)])

    def test_no_answer_buttons_while_a_screen_is_dark(self):
        # F-2: the old buttons stayed up during the next dim; a click there skipped the restore
        async def steps(app, pilot):
            await pilot.press("5")
            await pilot.pause(0.3)
            await pilot.click("#id-start")
            await pilot.pause(3.7)
            await pilot.click("#id-is-DP-2")
            await pilot.pause(1.0)                           # the second screen is dark now
            self.assertEqual(len(app.query("#df-id-answers Button")), 0)
            await pilot.pause(3.0)
            self.assertGreater(len(app.query("#df-id-answers Button")), 0)
        self.run_app(steps)
        self.assertEqual(self.lines("ddc.log")[-1], "--bus 4 setvcp 10 75")

    def test_typing_a_screen_name(self):
        # 2026-10-06: the first letter typed closed the app (a helper named `_name` hid Textual's own)
        async def steps(app, pilot):
            await pilot.press("5")
            await pilot.pause(0.3)
            await pilot.click("#n-DP-3")
            for ch in "Main":
                await pilot.press(ch)
            await pilot.press("enter")
            await pilot.pause(0.3)
        self.run_app(steps)
        self.assertEqual(self.session.remembered["names"], {"DP-3": "Main"})
        self.assertEqual(B.load(self.tmp / "screens.toml")["names"], {"DP-3": "Main"})

    def test_the_manual_opens(self):
        # F-3: Help had no manual
        from forgekit import ManualScreen

        async def steps(app, pilot):
            await pilot.press("m")
            await pilot.pause(0.4)
            self.assertIsInstance(app.screen, ManualScreen)
        self.run_app(steps)


class NoNameClashes(unittest.TestCase):
    """No method or value of displayForge's may reuse a name Textual sets on its own objects —
    the `_name` crash, caught for good."""

    def test_none(self):
        import inspect
        import re
        from textual.app import App as TApp
        from textual.containers import Horizontal, Vertical, VerticalScroll
        from textual.widget import Widget
        import displayforge.app as A
        live = set(vars(Widget())) | set(vars(VerticalScroll())) | set(vars(Horizontal())) | set(vars(Vertical()))
        app_live = set(vars(TApp()))
        found = []
        for name, cls in inspect.getmembers(A, inspect.isclass):
            if cls.__module__ != A.__name__:
                continue
            src = inspect.getsource(cls)
            mine = set(re.findall(r"^    def ([a-zA-Z_][a-zA-Z0-9_]*)\(", src, re.M))
            for grp in re.findall(r"((?:self\.[a-zA-Z_][a-zA-Z0-9_]*\s*,\s*)*self\.[a-zA-Z_][a-zA-Z0-9_]*)\s*=(?!=)", src):
                mine |= set(re.findall(r"self\.([a-zA-Z_][a-zA-Z0-9_]*)", grp))
            found += [f"{name}.{n}" for n in sorted(mine & (app_live if issubclass(cls, TApp) else live))]
        self.assertEqual(found, [])
        self.assertIn("_name", live)        # the check really sees the name that bit us


if __name__ == "__main__":
    unittest.main()


class StartUp(unittest.TestCase):
    """1.0.1 (forge-suite #32): Sway only, said and checked at launch."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_sway_is_required_and_ddcutil_optional(self):
        from displayforge.app import needs
        ns = needs(environ={"XDG_CURRENT_DESKTOP": "KDE", "WAYLAND_DISPLAY": "w"}, swaymsg="swaymsg")
        self.assertEqual(ns[0].what, "a Sway session")
        self.assertFalse(ns[0].optional)
        self.assertTrue(ns[1].optional, "ddcutil is optional: only Brightness and Identify need it")
        met, found = ns[0].check()
        self.assertFalse(met)
        self.assertEqual(found, "KDE Plasma (Wayland)")
        self.assertIn("only Sway", ns[0].why)
        self.assertIn("Sway (hypeForge)", ns[0].instead)

    def test_sway_not_answering_is_not_sway(self):
        from displayforge.app import needs
        dead = tool(self.tmp, "swaymsg", "exit 1\n")
        met, found = needs(environ={"SWAYSOCK": "/tmp/nowhere.sock"}, swaymsg=dead)[0].check()
        self.assertFalse(met)
        self.assertEqual(found, "a Sway socket that doesn't answer")

    def test_sway_answering_is_met(self):
        from displayforge.app import needs
        live = tool(self.tmp, "swaymsg", "exit 0\n")
        met, found = needs(environ={"SWAYSOCK": "/tmp/x.sock"}, swaymsg=live)[0].check()
        self.assertTrue(met)

    def test_main_closes_without_starting_the_app_when_not_sway(self):
        import io
        from contextlib import redirect_stdout
        from unittest import mock
        import displayforge.app as A
        started = []
        with mock.patch.object(A.DisplayForgeApp, "run", lambda self: started.append(1)), \
             mock.patch.dict("os.environ", {"SWAYSOCK": ""}, clear=False):
            out = io.StringIO()
            with redirect_stdout(out):
                rc = A.main(ask=lambda name, miss: "close")
        self.assertEqual(rc, 2)
        self.assertEqual(started, [], "the app must not start")
        self.assertIn("displayForge can't run here: it needs a Sway session", out.getvalue())
        self.assertIn("Nothing was changed.", out.getvalue())
