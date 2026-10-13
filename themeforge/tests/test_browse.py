"""The Browse pop-up's helpers: what a folder holds, the places, the paths in words."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from themeforge.browse import THEME_MADE, count_pictures, places, subfolders, tilde


class Folders(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for d in ("Pictures", "b-folder", "A-folder", ".hidden"):
            (self.root / d).mkdir()
        for f in ("one.PNG", "two.jpg", "three.webp", "notes.txt", "Pictures/p.png"):
            (self.root / f).write_bytes(b"x")

    def tearDown(self):
        self.tmp.cleanup()

    def test_pictures_are_counted_by_their_ending_whatever_the_case(self):
        self.assertEqual(count_pictures(self.root), 3)
        self.assertEqual(count_pictures(self.root / "A-folder"), 0)
        self.assertEqual(count_pictures(self.root / "nowhere"), -1, "unreadable says so")

    def test_subfolders_by_name_hidden_ones_left_out(self):
        self.assertEqual([p.name for p in subfolders(self.root)], ["A-folder", "b-folder", "Pictures"])
        self.assertEqual(subfolders(self.root / "nowhere"), [])

    def test_places_start_with_the_theme_s_pictures_then_the_folders_that_exist(self):
        got = places(self.root)
        self.assertEqual(got[0][0], THEME_MADE)
        self.assertEqual([name for _, name, _ in got][1:3], ["Home", "Pictures"])
        self.assertNotIn("Downloads", [name for _, name, _ in got])
        no_pictures = self.root / "b-folder"
        self.assertNotIn("Pictures", [name for _, name, _ in places(no_pictures)], "a missing Pictures is left out")

    def test_tilde_shortens_the_home_only(self):
        home = Path.home()
        self.assertEqual(tilde(home / "Pictures"), "~/Pictures")
        self.assertEqual(tilde(home), "~")
        self.assertEqual(tilde("/usr/share/wallpapers"), "/usr/share/wallpapers")
        self.assertEqual(tilde(str(home) + "stuff"), str(home) + "stuff", "a name that merely starts like home")


if __name__ == "__main__":
    unittest.main()
