"""displayForge · screens.py — reading screens and building commands. No Sway needed.

Fed with Javier's real three Sceptre Y27 (saved from `swaymsg -t get_outputs`, serial blanked)
and with made-up setups: one screen, four in a row, three over three, a fourth under screen 1.
"""

from __future__ import annotations

import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from displayforge import screens as S  # noqa: E402

REAL = json.loads((Path(__file__).parent / "data/three-sceptre-y27.json").read_text())


def fake(name, x=0, y=0, w=1920, h=1080, hz=60, on=True, hdr=False):
    m = {"width": w, "height": h, "refresh": hz * 1000}
    return {"name": name, "make": "Test", "model": "T", "serial": "", "active": on,
            "current_mode": m if on else None, "rect": {"x": x, "y": y, "width": w, "height": h},
            "scale": 1.0, "transform": "normal", "adaptive_sync_status": "disabled", "hdr": False,
            "features": {"adaptive_sync": False, "hdr": hdr},
            "modes": [m, {"width": 1280, "height": 720, "refresh": 60000}]}


class RealScreens(unittest.TestCase):
    def setUp(self):
        self.screens = S.parse(REAL)
        self.by = {s.name: s for s in self.screens}

    def test_three_screens_read(self):
        self.assertEqual(sorted(self.by), ["DP-1", "DP-2", "DP-3"])
        mid = self.by["DP-3"]
        self.assertTrue(mid.on)
        self.assertEqual((mid.mode.width, mid.mode.height, mid.mode.hz), (2560, 1440, 144))
        self.assertEqual((mid.x, mid.y, mid.scale, mid.rotation), (2560, 0, 1.0, "normal"))

    def test_hdr_not_offered_on_the_sceptres(self):
        # D-2: HDR only where Sway reports it — the Y27s report none
        for s in self.screens:
            self.assertFalse(s.can_hdr)
            self.assertTrue(s.can_adaptive_sync)

    def test_only_real_sizes_and_rates(self):
        mid = self.by["DP-3"]
        sizes = mid.sizes()
        self.assertEqual(sizes[0], (2560, 1440))           # the biggest first
        self.assertEqual(len(sizes), len(set(sizes)))       # no repeats
        rates = [m.hz for m in mid.rates(2560, 1440)]
        self.assertEqual(rates[0], 144)
        self.assertIn(120, rates)
        self.assertIn(60, rates)
        self.assertEqual(rates, sorted(rates, reverse=True))
        self.assertEqual(len(rates), len(set(rates)))       # one per whole Hz

    def test_no_overlaps_today(self):
        self.assertEqual(S.overlaps(self.screens), [])

    def test_nothing_changed_means_no_commands(self):
        self.assertEqual(S.all_commands(self.screens, self.screens), [])

    def test_refresh_change_is_one_command(self):
        mid = self.by["DP-3"]
        hz120 = [m for m in mid.rates(2560, 1440) if m.hz == 120][0]
        after = [replace(s, mode=hz120) if s.name == "DP-3" else s for s in self.screens]
        cmds = S.all_commands(self.screens, after)
        self.assertEqual(len(cmds), 1)
        self.assertTrue(cmds[0].startswith("output DP-3 mode 2560x1440@120."))

    def test_hdr_never_sent_to_a_screen_without_it(self):
        after = [replace(s, hdr=True) for s in self.screens]
        self.assertEqual(S.all_commands(self.screens, after), [])

    def test_switch_off_and_on(self):
        off = [replace(s, on=False) if s.name == "DP-1" else s for s in self.screens]
        self.assertEqual(S.all_commands(self.screens, off), ["output DP-1 disable"])
        self.assertIn("output DP-1 disable", S.config_lines(off))

    def test_saved_lines_describe_every_screen(self):
        lines = S.config_lines(self.screens)
        self.assertEqual(len(lines), 3)
        for line in lines:
            self.assertRegex(line, r"^output DP-\d mode 2560x1440@1\d\d\.\d{3}Hz position \d+ 0 "
                                   r"scale 1 transform normal adaptive_sync off$")
            self.assertNotIn("hdr", line)

    def test_move_left_screen_right_of_main(self):
        # The design's example: screen 2 (DP-2, left) moved right of screen 1 (DP-3)
        moved = S.place(self.screens, "DP-2", "right", "DP-3")
        by = {s.name: s for s in moved}
        self.assertEqual((by["DP-3"].x, by["DP-2"].x), (0, 2560))   # normalised to start at 0
        # DP-1 was also right of DP-3: it makes room, sliding on to the right (the design)
        self.assertEqual(by["DP-1"].x, 5120)
        self.assertEqual(S.overlaps(moved), [])


class MakeRoom(unittest.TestCase):
    def test_a_chain_of_screens_slides_along(self):
        # four in a row; the last one moved to the far left: everyone shifts right, no overlaps
        s = S.parse([fake(f"S{i}", x=1920 * i) for i in range(4)])
        moved = {x.name: x for x in S.place(s, "S3", "left", "S0")}
        self.assertEqual([moved[f"S{i}"].x for i in (3, 0, 1, 2)], [0, 1920, 3840, 5760])
        self.assertEqual(S.overlaps(list(moved.values())), [])

    def test_moving_into_an_empty_spot_moves_nobody_else(self):
        s = S.parse([fake("A"), fake("B", x=1920)])
        moved = {x.name: x for x in S.place(s, "B", "below", "A")}
        self.assertEqual((moved["A"].x, moved["A"].y), (0, 0))
        self.assertEqual((moved["B"].x, moved["B"].y), (0, 1080))


class AnyLayout(unittest.TestCase):
    """D-2: one screen, four in a row, three over three, a fourth under screen 1."""

    def test_one_screen(self):
        s = S.parse([fake("eDP-1")])
        self.assertEqual(len(s), 1)
        self.assertEqual(S.overlaps(s), [])

    def test_four_in_a_row(self):
        s = S.parse([fake(f"DP-{i}", x=1920 * i) for i in range(4)])
        self.assertEqual(S.overlaps(s), [])

    def test_three_over_three(self):
        s = S.parse([fake(f"T{i}", x=1920 * i) for i in range(3)] +
                    [fake(f"B{i}", x=1920 * i, y=1080) for i in range(3)])
        self.assertEqual(len(s), 6)
        self.assertEqual(S.overlaps(s), [])

    def test_fourth_under_screen_one(self):
        s = S.parse([fake(f"DP-{i}", x=1920 * i) for i in range(3)] + [fake("HDMI-A-1", x=5000, y=5000)])
        placed = {x.name: x for x in S.place(s, "HDMI-A-1", "below", "DP-0")}
        self.assertEqual((placed["HDMI-A-1"].x, placed["HDMI-A-1"].y), (0, 1080))
        self.assertEqual(S.overlaps(list(placed.values())), [])

    def test_centred_under_a_wider_screen(self):
        s = S.parse([fake("BIG", w=2560, h=1440), fake("SMALL", x=9000, w=1920, h=1080)])
        placed = {x.name: x for x in S.place(s, "SMALL", "below", "BIG", align="centre")}
        self.assertEqual((placed["SMALL"].x, placed["SMALL"].y), (320, 1440))

    def test_rotated_screen_takes_its_turned_room(self):
        s = S.parse([fake("A")])
        turned = replace(s[0], rotation="90")
        self.assertEqual(turned.extent, (1080, 1920))

    def test_scale_below_100_takes_more_room(self):
        s = replace(S.parse([fake("A")])[0], scale=0.8)
        self.assertEqual(s.extent, (2400, 1350))
        self.assertEqual(S.commands(S.parse([fake("A")])[0], s), ["output A scale 0.8"])

    def test_hdr_screen_gets_hdr(self):
        a = S.parse([fake("OLED", hdr=True)])[0]
        self.assertTrue(a.can_hdr)
        self.assertEqual(S.commands(a, replace(a, hdr=True)), ["output OLED hdr on"])
        self.assertIn("hdr off", S.config_lines([a])[0])


if __name__ == "__main__":
    unittest.main()
