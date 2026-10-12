"""The full-quality preview's sums: where the terminal's cells are, and where the picture goes.
The real thing (a real Alacritty, the real overlay, real pixels) is scripts/overlay-bench.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

from themeforge.termcell import alacritty_padding

HERE = Path(__file__).resolve().parents[1]


def overlay_module():
    try:
        spec = importlib.util.spec_from_file_location("tf_overlay", HERE / "themeforge/overlay.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    except (ImportError, ValueError) as e:            # no GTK or gtk-layer-shell: nothing to test here
        raise unittest.SkipTest(str(e))


WIN = {"rect": {"x": 300, "y": 120, "width": 1136, "height": 916},
       "window_rect": {"x": 3, "y": 3, "width": 1130, "height": 910}}


class Place(unittest.TestCase):
    def setUp(self):
        self.o = overlay_module()

    def test_alacritty_padding_puts_the_text_after_the_padding(self):
        x, y, w, h = self.o.place(WIN, (4, 10, 56, 14), (15, 15), False, (110, 40), 10, 22)
        self.assertEqual((x, y), (300 + 3 + 15 + 40, 120 + 3 + 15 + 220))
        self.assertEqual((w, h), (560, 308))

    def test_centred_padding_spreads_what_is_left(self):
        x, _, _, _ = self.o.place(WIN, (0, 0, 10, 1), (0, 0), True, (110, 40), 10, 22)
        self.assertEqual(x, 303 + (1130 - 1100) // 2)

    def test_the_screen_shape_fits_inside_and_is_centred(self):
        x, y, w, h = self.o.fitted((100, 100, 560, 308), (1280, 720))
        self.assertEqual((w, h), (547, 308))
        self.assertEqual((x, y), (100 + 6, 100))

    def test_it_finds_the_terminal_by_its_process_numbers(self):
        tree = {"type": "root", "nodes": [{"type": "output", "name": "DP-3", "nodes": [
            {"type": "workspace", "nodes": [], "floating_nodes": [{"type": "floating_con", "pid": 77, "nodes": []}]}]}]}
        win, out = self.o.find_window(tree, {5, 77})
        self.assertEqual((win["pid"], out["name"]), (77, "DP-3"))
        self.assertEqual(self.o.find_window(tree, {5}), (None, None))


class Padding(unittest.TestCase):
    def test_imports_first_the_file_itself_last(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d) / "base.toml"
            base.write_text("[window]\ndynamic_padding = true\n[window.padding]\nx = 4\ny = 4\n")
            main = Path(d) / "alacritty.toml"
            main.write_text(f'[general]\nimport = ["{base}"]\n[window.padding]\nx = 15\ny = 9\n')
            self.assertEqual(alacritty_padding(main), (15.0, 9.0, True))
            self.assertEqual(alacritty_padding(Path(d) / "missing.toml"), (0.0, 0.0, False))


if __name__ == "__main__":
    unittest.main()
