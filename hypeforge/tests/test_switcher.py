"""Alt + Tab and the tucked windows' way back (Javier, 2026-10-11: on the Rice "I don't have a way to bring
back a floating window when it goes 'minimized' … and we don't have the Alt+Tab function yet").
The rules here; the keys themselves are proven on a hidden Sway by scripts/switcher-bench.py."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "applets/panels"))
sys.path.insert(0, str(HERE / "applets/panels/views"))
import switcher  # noqa: E402


def load_tuck():
    loader = importlib.machinery.SourceFileLoader("hftuck_sw", str(HERE / "applets/tuck/hypeforge-tuck"))
    spec = importlib.util.spec_from_loader("hftuck_sw", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


def win(i, app, focused=False):
    return {"id": i, "type": "con", "pid": 100 + i, "app_id": app, "name": app, "focused": focused,
            "nodes": [], "floating_nodes": [], "rect": {"x": 0, "y": 0, "width": 10, "height": 10}}


def tree(tiled, tucked=(), floating=()):
    return {"type": "root", "nodes": [
        {"type": "output", "name": "__i3", "nodes": [
            {"type": "workspace", "name": "__i3_scratch", "nodes": [], "floating_nodes": list(tucked)}]},
        {"type": "output", "name": "DP-3", "nodes": [
            {"type": "workspace", "name": "1:Daily", "nodes": list(tiled), "floating_nodes": list(floating)}]}]}


class TheOrder(unittest.TestCase):
    def test_the_window_in_use_first_then_by_last_used(self):
        wins = switcher.windows(tree([win(1, "a"), win(2, "b", focused=True), win(3, "c")]))
        got = [w["id"] for w in switcher.ordered(wins, last_used=[2, 3, 1])]
        self.assertEqual(got, [2, 3, 1])

    def test_never_used_windows_keep_the_trees_order_at_the_end(self):
        wins = switcher.windows(tree([win(1, "a"), win(2, "b", focused=True), win(3, "c"), win(4, "d")]))
        got = [w["id"] for w in switcher.ordered(wins, last_used=[2, 4])]
        self.assertEqual(got, [2, 4, 1, 3])

    def test_tucked_windows_are_there_and_marked(self):
        wins = switcher.windows(tree([win(1, "a", focused=True)], tucked=[win(9, "floaty")]))
        hidden = next(w for w in wins if w["id"] == 9)
        self.assertTrue(hidden["tucked"])
        self.assertEqual(switcher.where(hidden), "tucked away")
        self.assertEqual(switcher.where(next(w for w in wins if w["id"] == 1)), "on Daily")


class WhereItStarts(unittest.TestCase):
    def wins(self, n):
        return [{"id": i, "focused": i == 0, "tucked": False} for i in range(n)]

    def test_alt_tab_starts_on_the_window_used_before(self):
        self.assertEqual(switcher.start_at(self.wins(3), back=False, tucked_only=False), 1)

    def test_backwards_starts_at_the_end(self):
        self.assertEqual(switcher.start_at(self.wins(3), back=True, tucked_only=False), 2)

    def test_one_window_or_none(self):
        self.assertEqual(switcher.start_at(self.wins(1), back=False, tucked_only=False), 0)
        self.assertEqual(switcher.start_at([], back=False, tucked_only=False), 0)

    def test_the_bar_icons_cards_start_at_the_first_tucked_one(self):
        self.assertEqual(switcher.start_at(self.wins(3), back=False, tucked_only=True), 0)


class Picking(unittest.TestCase):
    def test_a_tucked_window_comes_back_on_top_any_other_is_focused(self):
        self.assertEqual(switcher.pick_command({"id": 7, "tucked": True}), "[con_id=7] scratchpad show")
        self.assertEqual(switcher.pick_command({"id": 7, "tucked": False}), "[con_id=7] focus")


class TheTuckApplet(unittest.TestCase):
    def setUp(self):
        self.tk = load_tuck()

    def test_the_bar_icon_hides_when_nothing_is_tucked(self):
        piece = json.loads(self.tk.tucked_text([]))
        self.assertEqual(piece["text"], "", "Waybar hides a piece with no text")

    def test_the_bar_icon_counts_and_names_them(self):
        t = tree([win(1, "a", focused=True)], tucked=[win(8, "Chrome"), win(9, "themeForge")])
        piece = json.loads(self.tk.tucked_text(self.tk.tucked(t)))
        self.assertTrue(piece["text"].endswith(" 2"))
        self.assertEqual(piece["class"], "some")
        self.assertIn("Chrome", piece["tooltip"])
        self.assertIn("themeForge", piece["tooltip"])

    def test_last_used_moves_to_the_front_once(self):
        order = self.tk.remember([3, 2, 1], 1)
        self.assertEqual(order, [1, 3, 2])
        self.assertEqual(len(self.tk.remember(list(range(100)), 500)), self.tk.KEEP_RECENT)


class TheKeysAndTheBar(unittest.TestCase):
    def test_alt_tab_is_bound_and_on_the_rice(self):
        config = (HERE / "sway/config").read_text()
        self.assertIn("bindsym Mod1+Tab exec", config)
        self.assertIn("switcher --hold --back", config)
        rice = (HERE / "styles/rice/bar/config.jsonc").read_text()
        self.assertIn('"custom/tucked"', rice, "the Rice has no taskbar: its way back is this icon")
        self.assertIn('"custom/tucked"', (HERE / "sway/waybar/modules.jsonc").read_text())


if __name__ == "__main__":
    unittest.main()
