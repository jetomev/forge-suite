"""The Tuck applet (Javier, 2026-10-10): a click on a tiled window tucks away the floating windows
covering it — not one beside it, not one of the same app (a dialog), not a sticky one."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/common"))


def load():
    loader = importlib.machinery.SourceFileLoader("hftuck", str(HERE / "applets/tuck/hypeforge-tuck"))
    spec = importlib.util.spec_from_loader("hftuck", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


def win(i, app, x, y, w, h, focused=False, pid=None, **kw):
    return dict({"id": i, "pid": pid or 100 + i, "app_id": app, "focused": focused, "nodes": [], "floating_nodes": [],
                 "rect": {"x": x, "y": y, "width": w, "height": h}}, **kw)


def tree(tiled, floating, name="1:Daily"):
    return {"nodes": [{"nodes": [{"type": "workspace", "name": name, "nodes": tiled,
                                  "floating_nodes": [dict(f, type="floating_con") for f in floating]}]}]}


class Tuck(unittest.TestCase):
    def setUp(self):
        self.t = load()
        self.chrome = win(1, "google-chrome", 0, 0, 2560, 1400, focused=True)

    def test_a_floating_window_covering_the_one_clicked_is_tucked(self):
        term = win(2, "Alacritty", 800, 300, 900, 600)
        self.assertEqual(self.t.to_tuck(tree([self.chrome], [term])), [2])

    def test_one_beside_it_stays(self):
        half = win(1, "google-chrome", 0, 0, 1270, 1400, focused=True)
        aside = win(2, "Alacritty", 1300, 300, 900, 600)
        self.assertEqual(self.t.to_tuck(tree([half], [aside])), [])

    def test_a_dialog_of_the_same_app_stays(self):
        save_as = win(3, "google-chrome", 900, 400, 700, 500, pid=101)
        self.assertEqual(self.t.to_tuck(tree([self.chrome], [save_as])), [], "a dialog never vanishes")

    def test_sticky_and_transient_ones_stay(self):
        sticky = win(4, "mpv", 100, 100, 400, 300, sticky=True)
        x11 = win(5, None, 100, 100, 400, 300, window_properties={"class": "Steam", "transient_for": 77})
        self.assertEqual(self.t.to_tuck(tree([self.chrome], [sticky, x11])), [])

    def test_nothing_when_a_floating_window_has_the_focus(self):
        chrome = win(1, "google-chrome", 0, 0, 2560, 1400)
        term = win(2, "Alacritty", 800, 300, 900, 600, focused=True)
        self.assertEqual(self.t.to_tuck(tree([chrome], [term])), [])

    def test_the_scratchpad_itself_is_never_looked_at(self):
        self.assertEqual(self.t.to_tuck(tree([self.chrome], [win(2, "x", 0, 0, 10, 10)], name="__i3_scratch")), [])


if __name__ == "__main__":
    unittest.main()
