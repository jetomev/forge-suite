"""themeForge's view of hypeForge's look, on throwaway folders (no real hypeForge, no real apply)."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from themeforge.look import Look, hypeforge_home

PALETTES = """[meta]
order = ["mocha", "white"]
[themes.mocha.meta]
name = "KognogOS Mocha"
polarity = "dark"
[themes.mocha.surface]
sunken = "#111111"
base = "#1e1e2e"
raised = "#262637"
[themes.mocha.band]
base = "#313244"
strong = "#181825"
[themes.mocha.pop]
base = "#cba6f7"
[themes.mocha.text]
primary = "#cdd6f4"
[themes.white.meta]
name = "White"
polarity = "light"
"""


def fake_home(root: Path) -> Path:
    home = root / "hypeforge"
    (home / "applets/theme").mkdir(parents=True)
    tool = home / "applets/theme/hypeforge-theme"
    tool.write_text("#!/bin/sh\n")
    tool.chmod(0o755)
    for slug, name in (("classic", "hypeForge Classic"), ("rice", "Linux rice"), ("zz-new", "A New One")):
        (home / f"styles/{slug}").mkdir(parents=True)
        (home / f"styles/{slug}/style.toml").write_text(
            f'[meta]\nname = "{name}"\nslug = "{slug}"\nsummary = "about {slug}"\n'
            f'[wallpaper]\ntopic = "t-{slug}"\nabout = "{slug} picture"\n')
    (home / "themes/colours").mkdir(parents=True)
    (home / "themes/colours/palettes.toml").write_text(PALETTES)
    return home


class Reading(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.home, self.conf = fake_home(root), root / "config"
        self.calls = []
        self.look = Look(self.home, self.conf, run=self.fake_run, log=root / "tf.log")

    def tearDown(self):
        self.tmp.cleanup()

    def fake_run(self, cmd, **kw):
        self.calls.append(cmd)
        return subprocess.CompletedProcess(cmd, self.code, self.out, self.err)

    code, out, err = 0, "  the bar restarted\n  1 file(s) changed\n", ""

    def test_the_rice_first_classic_after_the_others_unknown_last(self):
        self.assertEqual([s.slug for s in self.look.styles()], ["rice", "classic", "zz-new"])
        self.assertEqual(self.look.styles()[0].summary, "about rice")

    def test_colours_in_the_palettes_order_with_a_swatch(self):
        c = self.look.colours()
        self.assertEqual([x.slug for x in c], ["mocha", "white"])
        self.assertEqual(c[0].label, "KognogOS Mocha  ·  dark")
        self.assertEqual(c[0].swatch[:3], ["#111111", "#1e1e2e", "#262637"])
        self.assertEqual(c[1].swatch[0], "#000000", "a missing colour is black, not a crash")

    def test_the_look_in_use_comes_from_hypeforges_own_memory(self):
        self.assertEqual(self.look.current(), (None, None))
        (self.conf / "hypeforge/theme").mkdir(parents=True)
        (self.conf / "hypeforge/theme/state.toml").write_text('style = "rice"\ntheme = "mocha"\n')
        self.assertEqual(self.look.current(), ("rice", "mocha"))

    def test_apply_writes_the_look_file_then_hypeforge_applies_it(self):
        """Javier, 2026-10-11: "have already a config file for theme, and with the config file themeForge
        call to change it" — the picks go into the look file, then `hypeforge-theme look`."""
        ok, words = self.look.apply("rice", "white")
        self.assertTrue(ok)
        self.assertEqual(self.calls[-1], [str(self.home / "applets/theme/hypeforge-theme"), "look"])
        self.assertEqual(self.look.picks()["theme"], "rice")
        self.assertEqual(self.look.picks()["colors"], "white")
        self.assertEqual(self.look.picks()["elements"]["bar"], "theme", "each element follows the theme")
        self.assertIn("1 file(s) changed", words)
        self.look.undo()
        self.assertEqual(self.calls[-1][1:], ["undo"])

    def test_an_elements_pick_is_kept_when_the_theme_changes(self):
        (self.conf / "hypeforge").mkdir(parents=True, exist_ok=True)
        self.look.write_picks("rice", "mocha")
        text = self.look.look_file.read_text().replace('bar = "theme"', 'bar = "kde"')
        self.look.look_file.write_text(text)
        self.look.apply("classic", "white")
        self.assertEqual(self.look.picks()["elements"]["bar"], "kde")
        self.assertEqual(self.look.picks()["theme"], "classic")

    def test_every_run_goes_in_the_log(self):
        self.look.apply("rice", "white")
        self.code, self.err = 2, "Not done: nope\n"
        self.look.undo()
        log = self.look.log.read_text()
        self.assertIn("· look · OK", log)
        self.assertIn("· undo · NOT DONE", log)

    def test_a_refusal_says_why(self):
        self.code, self.out, self.err = 2, "", "\n  Not done: no style called nope (hypeforge-theme list shows them)\n"
        ok, words = self.look.apply("nope", "mocha")
        self.assertFalse(ok)
        self.assertEqual(words, "no style called nope (hypeforge-theme list shows them)")

    def test_hypeforge_is_found_where_it_lives(self):
        self.assertEqual(hypeforge_home([Path("/nowhere"), self.home]), self.home)
        self.assertIsNone(hypeforge_home([Path("/nowhere")]))
        self.assertFalse(Look(Path("/nowhere"), self.conf).ok)


class TheRealOne(unittest.TestCase):
    def test_every_hypeforge_style_has_a_summary_to_show(self):
        home = hypeforge_home()
        if home is None:
            self.skipTest("hypeForge isn't on this computer")
        styles = Look(home).styles()
        self.assertGreaterEqual(len(styles), 7)
        for s in styles:
            self.assertTrue(s.summary, f"{s.slug} has no summary in its style.toml")
        self.assertEqual(len(Look(home).colours()), 25)


if __name__ == "__main__":
    unittest.main()
