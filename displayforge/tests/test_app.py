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
        self.saved = (V.OUTPUTS, V.BACKUPS, B.CONFIG)
        V.OUTPUTS, V.BACKUPS, B.CONFIG = self.tmp / "outputs", self.tmp / "backups", self.tmp / "screens.toml"
        self.real = [Path.home() / ".config/sway/outputs", Path.home() / ".config/displayforge"]
        self.real_before = [p.exists() for p in self.real]
        self.session = Session(S.parse(json.loads(DATA.read_text())), {"names": {}, "bus": {}}, main="DP-3")

    def tearDown(self):
        V.OUTPUTS, V.BACKUPS, B.CONFIG = self.saved
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


if __name__ == "__main__":
    unittest.main()
