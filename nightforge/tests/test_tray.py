"""The tray icon (D-4), on a private throwaway session bus with a stand-in tray host and a stand-in
night light: it registers, shows its picture and menu, and its menu acts."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


@unittest.skipUnless(shutil.which("dbus-run-session"), "needs dbus-run-session (dbus)")
class Tray(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run(["dbus-run-session", "--", sys.executable, str(HERE / "tray_probe.py")],
                           capture_output=True, text=True, timeout=90)
        cls.out = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
        cls.err = r.stderr

    def test_it_registers_with_the_tray(self):
        self.assertTrue(self.out.get("registered"), self.err[-500:])

    def test_its_picture_and_menu(self):
        self.assertTrue(self.out["title"].startswith("Night light: "))
        self.assertEqual([p[:2] for p in self.out["pixmaps"]], [[22, 22], [32, 32], [44, 44]])
        self.assertEqual([p[2] for p in self.out["pixmaps"]], [22 * 22 * 4, 32 * 32 * 4, 44 * 44 * 4])
        self.assertEqual(self.out["menu"], "/MenuBar")
        for label in ("Automatic", "Warm Now", "Daylight Now", "Turn Off", "Open nightForge…"):
            self.assertIn(label, self.out["labels"])

    def test_warm_now_restarts_then_nudges_twice(self):
        ev = self.out["after_warm"]
        self.assertIn("stop", ev)
        self.assertEqual(ev[ev.index("stop"):].count("usr1"), 2)

    def test_turn_off_is_saved_and_shown(self):
        self.assertIn("enabled = false", self.out["settings_after_off"])
        self.assertEqual(self.out["title_after_off"], "Night light: off")


if __name__ == "__main__":
    unittest.main()
