"""Title bars on floating windows and the window menu (D-110, Javier, 2026-10-17: "Theme title bars…
Middle mouse click for minimize… Right click mouse, window menu… an option to make floating window, or get
it back into the greed")."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


win = load("hf_window", REPO / "applets/window/hypeforge-window")
ht = load("hf_theme_w", REPO / "applets/theme/hypeforge-theme")


class Borders(unittest.TestCase):
    def test_a_floating_window_gets_the_title_bar_and_loses_it_in_the_grid(self):
        self.assertEqual(win.wanted({"pid": 1, "type": "floating_con", "border": "pixel"}, "pixel 2", "normal 2"), "normal 2")
        self.assertEqual(win.wanted({"pid": 1, "type": "con", "border": "normal"}, "pixel 2", "normal 2"), "pixel 2")
        self.assertIsNone(win.wanted({"pid": 1, "type": "floating_con", "border": "normal"}, "pixel 2", "normal 2"))

    def test_an_app_with_its_own_bar_never_gets_ours(self):
        """Javier: "if their bar is fixed, then they keep it and ours does not show"."""
        self.assertIsNone(win.wanted({"pid": 1, "type": "floating_con", "border": "csd"}, "pixel 2", "normal 2",
                                     prog="gnome-calculator"))

    def test_a_terminal_draws_no_bar_of_its_own_so_it_gets_ours(self):
        """Alacritty floated asks to draw its own bar and draws none (F-55; the bench, 10-17). Every Forge app
        runs in it."""
        con = {"pid": 1, "type": "floating_con", "border": "csd"}
        self.assertEqual(win.wanted(con, "pixel 2", "normal 2", prog="alacritty"), "normal 2")
        self.assertIsNone(win.wanted(con, "pixel 2", "normal 2", prog="gnome-calculator"))

    def test_a_style_with_title_bars_on_tiled_windows_keeps_them(self):
        self.assertIsNone(win.wanted({"pid": 1, "type": "con", "border": "normal"}, "normal 1", "normal 1"))


class EveryStyle(unittest.TestCase):
    def test_every_style_gives_floating_windows_the_title_bar(self):
        for slug, style in ht.styles().items():
            shape = style.get("shape", {})
            self.assertTrue(ht.sway_floating_border(shape).startswith("normal "), slug)
            self.assertIn("title_align", ht.sway_titlebar(style), slug)

    def test_tiled_windows_keep_what_each_style_says(self):
        """Floating windows only (Javier's pick); KDE and Mac OS 9 had title bars everywhere as approved."""
        for slug, style in ht.styles().items():
            shape = style.get("shape", {})
            want = "normal" if shape.get("titlebar") else "pixel"
            self.assertTrue(ht.sway_border(shape).startswith(want), slug)


class TheClicks(unittest.TestCase):
    def setUp(self):
        self.conf = (REPO / "sway/config").read_text()

    def test_the_title_bar_clicks(self):
        self.assertRegex(self.conf, r"\n\s*bindsym button2 move scratchpad\n")
        self.assertRegex(self.conf, r"\n\s*bindsym button3 focus, exec \S*applets/window/hypeforge-window menu\n")
        self.assertNotRegex(self.conf, r"bindsym (--whole-window|--border) button[23]",
                            "the clicks are for the title bar only, never inside a window")

    def test_the_float_key_no_longer_forces_the_plain_frame(self):
        line = re.search(r"bindsym \$mod\+Shift\+space (.+)", self.conf).group(1)
        self.assertNotIn("border pixel", line)

    def test_the_watcher_starts_at_login(self):
        self.assertIn("hypeforge-watch window ~/Programs/forge-suite/hypeforge/applets/window/hypeforge-window watch",
                      self.conf)


if __name__ == "__main__":
    unittest.main()
