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



class InsideSettings(unittest.TestCase):
    """D-97 (Javier, 2026-10-13: "the previews are showing blurry" inside hypeForge Settings): Settings
    hands its terminal's cells down; the preview's cells are offset by the pane's place."""

    def test_the_cells_come_from_settings_when_it_hands_them(self):
        from themeforge.termcell import from_settings
        c = from_settings({"HYPEFORGE_TERM_CELLS": "9.5 20 4 4 0 130 40", "HYPEFORGE_PANE_AT": "31 2"})
        self.assertEqual((c.width, c.height, c.pad_x, c.pad_y, c.centred), (9.5, 20.0, 4.0, 4.0, False))
        self.assertEqual((c.origin, c.grid), ((31, 2), (130, 40)))
        self.assertIsNone(from_settings({}), "outside Settings: ask the terminal")
        self.assertIsNone(from_settings({"HYPEFORGE_TERM_CELLS": "broken"}))

    def test_the_overlay_is_told_the_terminal_cells_not_the_panes(self):
        import os
        from themeforge.app import PictureOverlay
        from themeforge.termcell import Cells
        sent = []
        ov = PictureOverlay(Cells(9.5, 20, origin=(31, 2), grid=(130, 40)))
        ov._send = lambda msg: sent.append(msg)
        env = dict(os.environ); os.environ.update(SWAYSOCK="x", WAYLAND_DISPLAY="y"); os.environ.pop("THEMEFORGE_NO_OVERLAY", None)
        try:
            ov.show("/p.png", (10, 5, 56, 14), (100, 40))
        finally:
            os.environ.clear(); os.environ.update(env)
        self.assertEqual(sent, [{"show": {"png": "/p.png", "cells": [41, 7, 56, 14], "grid": [130, 40]}}])

    def test_the_panes_place_now_beats_the_first_guess(self):
        """Javier, 2026-10-13: the sharp preview landed top-left — Settings opened straight on the Look page
        handed "0 0". The pane-<n> file Settings keeps current wins; without it, the first guess."""
        import os
        import tempfile
        from pathlib import Path
        from themeforge.app import PictureOverlay
        from themeforge.termcell import Cells, pane_origin
        with tempfile.TemporaryDirectory() as d:
            run = Path(d); (run / "hypeforge-settings").mkdir()
            self.assertIsNone(pane_origin({"HYPEFORGE_SETTINGS_PAGE": "4"}, run), "not written yet")
            (run / "hypeforge-settings/pane-4").write_text("32 3 98 36")
            self.assertEqual(pane_origin({"HYPEFORGE_SETTINGS_PAGE": "4"}, run), (32, 3))
            self.assertIsNone(pane_origin({}, run), "outside Settings")
            sent = []
            ov = PictureOverlay(Cells(10, 22, origin=(0, 0), grid=(213, 51)))
            ov._send = lambda msg: sent.append(msg)
            env = dict(os.environ)
            os.environ.update(SWAYSOCK="x", WAYLAND_DISPLAY="y", HYPEFORGE_SETTINGS_PAGE="4", XDG_RUNTIME_DIR=d)
            os.environ.pop("THEMEFORGE_NO_OVERLAY", None)
            try:
                ov.show("/p.png", (10, 5, 56, 14), (100, 40))
            finally:
                os.environ.clear(); os.environ.update(env)
            self.assertEqual(sent[0]["show"]["cells"], [42, 8, 56, 14], "the file's place, not the 0 0 guess")

    def test_hidden_while_settings_shows_another_page(self):
        import tempfile
        from pathlib import Path
        from themeforge.termcell import settings_shows_me
        with tempfile.TemporaryDirectory() as d:
            run = Path(d); (run / "hypeforge-settings").mkdir()
            (run / "hypeforge-settings/shown").write_text("3")
            self.assertTrue(settings_shows_me({"HYPEFORGE_SETTINGS_PAGE": "3"}, run))
            self.assertFalse(settings_shows_me({"HYPEFORGE_SETTINGS_PAGE": "4"}, run))
            self.assertTrue(settings_shows_me({}, run), "outside Settings: nothing hides it")
            (run / "hypeforge-settings/shown").write_text("none")
            self.assertFalse(settings_shows_me({"HYPEFORGE_SETTINGS_PAGE": "3"}, run), "Home, the manual: not us")



if __name__ == "__main__":
    unittest.main()
