"""One bar per screen (Javier, 2026-10-10: "the launcher and all the bar popups don't open in the
screen you are in, clicking from, they open in the left screen only")."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/common"))
sys.path.insert(0, str(HERE / "applets/panels"))


def load(path, name):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


OUTS = [{"name": "DP-1", "active": True, "focused": True, "rect": {"x": 0, "y": 0}},
        {"name": "DP-2", "active": True, "focused": False, "rect": {"x": 2560, "y": 0}},
        {"name": "HDMI-A-1", "active": False, "focused": False, "rect": {"x": 0, "y": 0}}]


class TheBarTellsItsScreen(unittest.TestCase):
    def setUp(self):
        self.bar = load(HERE / "applets/bar/hypeforge-bar", "hfbar_tool")

    def test_each_copy_is_kept_to_its_screen(self):
        text = '// a comment\n{\n  "height": 44, // inline\n  "x": "https://kognogos.org"\n}\n'
        cfg = json.loads(self.bar.config_for(text, "DP-2"))
        self.assertEqual(cfg["output"], "DP-2")
        self.assertEqual(cfg["x"], "https://kognogos.org", "a // inside a string is not a comment")

    def test_every_style_bar_reads_as_one_screens_config(self):
        for path in [HERE / "sway/waybar/config.jsonc", *sorted(HERE.glob("styles/*/bar/config.jsonc"))]:
            with self.subTest(path.parent.parent.name):
                self.assertEqual(json.loads(self.bar.config_for(path.read_text(), "DP-1"))["output"], "DP-1")

    def test_login_and_the_engine_start_it(self):
        self.assertIn("applets/bar/hypeforge-bar start", (HERE / "sway/config").read_text())
        self.assertNotRegex((HERE / "sway/config").read_text(), r"(?m)^exec waybar ")


class PopupsOpenOnTheClickedScreen(unittest.TestCase):
    def setUp(self):
        import panelkit
        self.pk = panelkit

    def test_the_clicked_bars_screen_wins(self):
        self.assertEqual(self.pk.output_in_use(OUTS, {"HYPEFORGE_OUTPUT": "DP-2"})["name"], "DP-2")

    def test_a_key_uses_the_focused_screen(self):
        self.assertEqual(self.pk.output_in_use(OUTS, {})["name"], "DP-1")

    def test_a_screen_gone_falls_back_to_the_focused_one(self):
        self.assertEqual(self.pk.output_in_use(OUTS, {"HYPEFORGE_OUTPUT": "HDMI-A-1"})["name"], "DP-1")

    def test_lists_open_there_too(self):
        import hfmenu
        seen = {}

        class FakeMenu:
            pid, returncode = 1, 1

            def __init__(self, cmd, **_):
                seen["cmd"] = cmd

            def communicate(self, _):
                return b"", b""
        import tempfile
        saved = {k: os.environ.get(k) for k in ("HYPEFORGE_OUTPUT", "WAYLAND_DISPLAY")}
        old_popen, old_open = hfmenu.subprocess.Popen, hfmenu.OPEN
        hfmenu.subprocess.Popen = FakeMenu
        hfmenu.OPEN = Path(tempfile.mkdtemp(prefix="hfmenu.")) / "open"   # never the real session's
        os.environ["HYPEFORGE_OUTPUT"] = "DP-2"
        os.environ.pop("WAYLAND_DISPLAY", None)                             # no click-catcher either
        try:
            hfmenu.run("test", ["fuzzel", "--dmenu"], "a\n")
        finally:
            hfmenu.subprocess.Popen, hfmenu.OPEN = old_popen, old_open
            for k, v in saved.items():
                os.environ.pop(k, None)
                if v is not None:
                    os.environ[k] = v
        self.assertIn("--output=DP-2", seen["cmd"])


if __name__ == "__main__":
    unittest.main()
