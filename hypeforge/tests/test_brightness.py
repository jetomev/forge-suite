"""The brightness keys (F-71, #94): a laptop's backlight through brightnessctl, desktop monitors through
their own channel (ddcutil, displayForge's way) in tens, or a notice saying why nothing moved."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parents[1]


def load():
    loader = importlib.machinery.SourceFileLoader("hfbrightness", str(HERE / "applets/brightness/hypeforge-brightness"))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hfbrightness", loader))
    loader.exec_module(m)
    return m


class FakeRun:
    """Answers ddcutil and brightnessctl like the real ones; records every command."""

    def __init__(self, levels: dict[int, int], fail_set=False, backlight_pct="47%"):
        self.levels, self.fail_set, self.backlight_pct, self.commands = levels, fail_set, backlight_pct, []

    def __call__(self, cmd, **kw):
        self.commands.append(cmd)
        if cmd[:2] == ["ddcutil", "detect"]:
            return SimpleNamespace(returncode=0, stdout="".join(f"Display {i}\n   I2C bus:  /dev/i2c-{b}\n" for i, b in enumerate(self.levels, 1)))
        if cmd[0] == "ddcutil" and "getvcp" in cmd:
            bus = int(cmd[2])
            return SimpleNamespace(returncode=0, stdout=f"VCP 10 C {self.levels[bus]} 100\n")
        if cmd[0] == "ddcutil" and "setvcp" in cmd:
            return SimpleNamespace(returncode=1 if self.fail_set else 0, stdout="")
        if cmd[0] == "brightnessctl":
            return SimpleNamespace(returncode=0, stdout=f"intel_backlight,backlight,2250,{self.backlight_pct},4794\n")
        return SimpleNamespace(returncode=0, stdout="")


class Steps(unittest.TestCase):
    def test_tens_from_wherever_the_monitor_is(self):
        m = load()
        self.assertEqual(m.next_level(70, "up"), 80)
        self.assertEqual(m.next_level(70, "down"), 60)
        self.assertEqual(m.next_level(65, "up"), 70, "the next stop above, never one skipped")
        self.assertEqual(m.next_level(65, "down"), 60)
        self.assertEqual(m.next_level(55, "down"), 50)
        self.assertEqual(m.next_level(100, "up"), 100, "never above 100")
        self.assertEqual(m.next_level(12, "down"), 10, "never below displayForge's lowest stop")


class Monitors(unittest.TestCase):
    def setUp(self):
        self.m = load()
        self.empty = Path(tempfile.mkdtemp())          # a desktop: no backlight at all

    def test_every_monitor_moves_one_stop_together(self):
        run = FakeRun({3: 70, 4: 65, 5: 100})
        done, words = self.m.change("up", run=run, which=lambda n: "/usr/bin/" + n, backlight=self.empty)
        self.assertTrue(done)
        sets = sorted(c[2:] for c in run.commands if "setvcp" in c)
        self.assertEqual(sets, [["3", "setvcp", "10", "80"], ["4", "setvcp", "10", "70"], ["5", "setvcp", "10", "100"]])
        self.assertEqual(words, "100", "the notice shows the level reached")
        self.assertFalse([c for c in run.commands if c[0] == "brightnessctl"], "no backlight: brightnessctl is never run")

    def test_without_ddcutil_the_key_says_so(self):
        run = FakeRun({3: 70})
        done, words = self.m.change("down", run=run, which=lambda n: None, backlight=self.empty)
        self.assertFalse(done)
        self.assertIn("ddcutil", words)
        self.assertEqual(run.commands, [], "nothing is tried")

    def test_a_monitor_that_refuses_is_said(self):
        run = FakeRun({3: 70}, fail_set=True)
        done, words = self.m.change("down", run=run, which=lambda n: "/usr/bin/" + n, backlight=self.empty)
        self.assertFalse(done)
        self.assertIn("did not take", words)


class Laptop(unittest.TestCase):
    def setUp(self):
        self.m = load()
        self.lap = Path(tempfile.mkdtemp()); (self.lap / "intel_backlight").mkdir()

    def test_a_backlight_goes_through_brightnessctl_not_the_monitors(self):
        run = FakeRun({})
        done, words = self.m.change("up", run=run, which=lambda n: "/usr/bin/" + n, backlight=self.lap)
        self.assertTrue(done)
        self.assertEqual(run.commands, [["brightnessctl", "-m", "set", "10%+"]])
        self.assertEqual(words, "47")

    def test_a_laptop_without_brightnessctl_says_so(self):
        run = FakeRun({})
        done, words = self.m.change("up", run=run, which=lambda n: None if n == "brightnessctl" else "/usr/bin/" + n, backlight=self.lap)
        self.assertFalse(done)
        self.assertIn("brightnessctl", words)
        self.assertEqual(run.commands, [])


class Keys(unittest.TestCase):
    def test_sways_brightness_keys_run_the_applet(self):
        cfg = (HERE / "sway/config").read_text()
        self.assertNotIn("exec brightnessctl", cfg, "the keys no longer depend on a program a desktop lacks (#94)")
        for key, way in (("XF86MonBrightnessDown", "down"), ("XF86MonBrightnessUp", "up")):
            self.assertRegex(cfg, rf"bindsym --locked {key} exec .*hypeforge-brightness {way}")


if __name__ == "__main__":
    unittest.main()
