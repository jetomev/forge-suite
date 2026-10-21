"""D-116 (2026-10-20): the bar's short lists become the list card (views/listcard.py) through
common/hfmenu.run, the applets unchanged; the launcher stays fuzzel; off until Javier approves."""

import importlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/common"))
sys.path.insert(0, str(HERE / "applets/panels"))
sys.path.insert(0, str(HERE / "applets/panels/views"))

WORKSPACES = ["fuzzel", "--dmenu", "--index", "--no-sort", "--prompt", "Workspaces  ", "--anchor", "top-left",
              "--x-margin", "44", "--y-margin", "4", "--width", "28", "--lines", "3", "--select-index", "1"]


class CardInput(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"XDG_RUNTIME_DIR": self.tmp.name, "XDG_CONFIG_HOME": self.tmp.name})
        self.env.start()
        import hfmenu
        self.h = importlib.reload(hfmenu)

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def places(self, corner):
        (Path(self.tmp.name) / "hypeforge-bar").mkdir(exist_ok=True)
        self.h.PLACES.write_text(json.dumps({"{popup}": corner}))

    def test_rows_marks_icons_and_answers(self):
        data, _, _ = self.h.card_input(WORKSPACES, "●  1. Daily\n   2. Work\nGimp\0icon\x1fgimp\n")
        self.assertEqual([r["text"] for r in data["rows"]], ["1. Daily", "2. Work", "Gimp"])
        self.assertEqual([r["mark"] for r in data["rows"]], [True, False, False])
        self.assertEqual(data["rows"][2]["icon"], "gimp")
        self.assertEqual((data["title"], data["index"], data["selected"]), ("Workspaces", True, 1))
        import listcard
        self.assertEqual(listcard.answer(listcard.parse(json.dumps(data)), 2), "2")       # --index: the number
        data["index"] = False
        self.assertEqual(listcard.answer(listcard.parse(json.dumps(data)), 2), "Gimp")    # else the words

    def test_placed_from_the_bar_it_opens_from(self):
        self.places("--edges top,right --margin top=34,right=8")       # a top bar, 26 px + 8
        _, edges, margins = self.h.card_input(WORKSPACES, "a")
        self.assertEqual((edges, margins), ("top,left", "top=34,left=44"))
        self.places("--edges bottom,right --margin bottom=56,right=8")  # Windows 11's taskbar
        _, edges, margins = self.h.card_input(["fuzzel", "--anchor", "top-right", "--x-margin", "2"], "a")
        self.assertEqual((edges, margins), ("bottom,right", "bottom=56,right=8"))   # never closer than 8 px

    def test_off_until_switched_on_and_the_launcher_stays_fuzzel(self):
        with mock.patch.dict(os.environ, {"HYPEFORGE_LIST_CARDS": ""}):
            self.assertFalse(self.h.cards_on())
            self.h.CARDS.parent.mkdir(parents=True, exist_ok=True)
            self.h.CARDS.write_text("")
            self.assertTrue(self.h.cards_on())
            with mock.patch.dict(os.environ, {"HYPEFORGE_FUZZEL_LISTS": "1"}):
                self.assertFalse(self.h.cards_on())
        calls = []
        with mock.patch.object(self.h, "run_card", lambda *a: calls.append(a[0]) or "0"), \
             mock.patch.object(self.h, "cards_on", lambda: True), \
             mock.patch.object(self.h.subprocess, "Popen", side_effect=OSError("fuzzel")):
            self.h.run("workspaces", WORKSPACES, "a")
            with self.assertRaises(OSError):                           # the launcher went to fuzzel
                self.h.run("launcher", WORKSPACES, "a")
        self.assertEqual(calls, ["workspaces"])


if __name__ == "__main__":
    unittest.main()
