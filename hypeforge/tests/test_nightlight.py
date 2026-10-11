"""The night light's moon on the bar (hypeforge-nightlight), from nightForge's own status."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def load():
    loader = importlib.machinery.SourceFileLoader("hfnight", str(HERE / "applets/nightlight/hypeforge-nightlight"))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hfnight", loader))
    loader.exec_module(m)
    return m


class Moon(unittest.TestCase):
    def setUp(self):
        self.n = load()

    def test_warm_daylight_and_off_each_their_class(self):
        for state, words in (("warm", "warm"), ("day", "daylight"), ("off", "off")):
            line = self.n.bar_line({"state": state, "why": "because", "mode": "auto", "running": True})
            self.assertEqual(line["class"], state)
            self.assertEqual(line["text"], self.n.MOON)
            self.assertIn(words, line["tooltip"])

    def test_no_nightforge_no_moon(self):
        self.assertEqual(self.n.bar_line(None), {"text": "", "class": "none"})

    def test_the_bar_redraws_it_on_its_own_signal(self):
        modules = (HERE / "sway/waybar/modules.jsonc").read_text()
        self.assertIn('"signal": 13', modules[modules.index('"custom/nightlight"'):][:400])


if __name__ == "__main__":
    unittest.main()
