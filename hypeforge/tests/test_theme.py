"""hypeforge-theme (the look, D-78 step 1) on throwaway folders: roles, filters, today's look,
dry runs, names that must exist, backups and undo. Nothing here touches the desktop."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "applets/theme/hypeforge-theme"
loader = importlib.machinery.SourceFileLoader("hypeforge_theme", str(TOOL))
spec = importlib.util.spec_from_loader("hypeforge_theme", loader)
ht = importlib.util.module_from_spec(spec)
loader.exec_module(ht)

WALL = "/usr/share/wallpapers/kognog/Kognog OS Semi - Logo Catpuccin Mocha.png"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.place = ht.Place(Path(self.tmp.name))
        self.wall = Path(self.tmp.name) / "mine.png"
        self.wall.write_bytes(Path(WALL).read_bytes() if Path(WALL).exists() else b"\x89PNG fake")

    def tearDown(self):
        self.tmp.cleanup()

    def apply(self, style="classic", theme="kognogos-mocha", **kw):
        kw.setdefault("wallpaper", str(self.wall))
        kw.setdefault("reload", False)
        return ht.apply(style, theme, self.place, **kw)

    def read(self, rel):
        return (self.place.root / rel).read_text()


class Roles(Base):
    def test_the_style_wins_over_the_default(self):
        s, t = ht.styles()["classic"], ht.themes()["kognogos-mocha"]
        self.assertEqual(ht.resolve("window_focused", s, t), "#cdd6f4", "Classic: today's light border")
        rice = ht.styles()["rice"]
        self.assertEqual(ht.resolve("window_focused", rice, t), t["window"]["focused"], "a style without it: the theme's own")

    def test_filters(self):
        ctx = {"style": ht.styles()["classic"], "theme": ht.themes()["kognogos-mocha"], "names": {}, "wallpaper": "",
               "meta": {}}
        self.assertEqual(ht.fill("{{list_bg|hex8}}", ctx), "262637ff")
        self.assertEqual(ht.fill("{{lock_bg|alpha(0.85)}}", ctx), "rgba(30, 30, 46, 0.85)")
        with self.assertRaises(ht.LookError):
            ht.fill("{{no_such_role}}", ctx)

    def test_cosmic_roundness_picks_one_value(self):
        cosmic = ht.styles()["cosmic"]
        self.assertEqual(ht.shape_of(cosmic, "radius_popup"), 8, "slightly round by default (D-77)")
        self.assertEqual(ht.shape_of(ht.styles()["classic"], "border_popup"), 1)


class TodaysLook(Base):
    def test_classic_mocha_gives_back_todays_colours(self):
        self.apply()
        sway = self.read("hypeforge/theme/sway.conf")
        for line in ("set $hf_active    #cdd6f4", "set $hf_inactive  #45475a", "set $hf_titlebar  #181825",
                     "default_border pixel 2", "gaps inner 10", "gaps outer 0",
                     "seat * xcursor_theme catppuccin-mocha-dark-cursors 24"):
            self.assertIn(line, sway)
        self.assertIn(f'output * bg "{self.wall}" fill', sway, "a picture the person picked wins")
        fz = self.read("hypeforge/theme/fuzzel-colors.ini")
        for line in ("background=262637ff", "match=cba6f7ff", "selection=45475aff", "radius=0"):
            self.assertIn(line, fz)
        css = self.read("hypeforge/theme/colors.css")
        self.assertIn("@define-color hf_bar      #181825;", css)
        self.assertIn("@define-color hf_shade    #262637;", css)
        mako = self.read("mako/config")
        self.assertIn("background-color=#262637", mako)
        self.assertNotIn("{{", mako)
        self.assertIn("gtk-cursor-theme-name=catppuccin-mocha-dark-cursors", self.read("gtk-3.0/settings.ini"))

    def test_a_titlebar_style_turns_title_bars_on(self):
        self.apply("mac-os-9", "light-gray")
        sway = self.read("hypeforge/theme/sway.conf")
        self.assertIn("default_border normal 1", sway)
        self.assertIn("title_align center", sway)
        self.assertIn("font pango:Noto Sans Bold 10", sway)

    def test_classic_keeps_its_bar_shadow_off_the_windows(self):
        # Javier's FX screenshot (10-10): the bar's shadow dimmed the windows' top frame
        self.apply("classic", "kognogos-mocha", say=lambda *_: None)
        fx = self.read("hypeforge/theme/fx.conf")
        bar = fx.split('layer_effects "waybar"')[1].split("}")[0]
        lists = fx.split('layer_effects "launcher"')[1].split("}")[0]
        self.assertIn("shadows disable", bar)
        self.assertIn("shadows enable", lists, "the lists keep theirs")
        self.assertIn("corner_radius 12", fx)


class Safety(Base):
    def test_a_dry_run_writes_nothing(self):
        r = self.apply(dry=True, say=lambda *_: None)
        self.assertTrue(r["changed"])
        self.assertFalse((self.place.root / "hypeforge").exists())

    def test_a_missing_name_stops_before_writing(self):
        theme = ht.themes()["kognogos-mocha"]
        theme = {**theme, "names": {**theme["names"], "cursor": "no-such-cursors"}}
        with self.assertRaises(ht.LookError):
            ht.names_for(theme)

    def test_unknown_style_or_theme(self):
        with self.assertRaises(ht.LookError):
            self.apply("vista")
        with self.assertRaises(ht.LookError):
            self.apply(theme="beige")

    def test_undo_brings_back_the_files_and_the_state(self):
        self.apply()
        before = self.read("mako/config")
        self.apply("rice", "ember")
        self.assertNotEqual(self.read("mako/config"), before)
        ht.undo(self.place, reload=False)
        self.assertEqual(self.read("mako/config"), before)
        self.assertEqual(self.place.read_state()["theme"], "kognogos-mocha")

    def test_the_first_look_cannot_be_undone(self):
        """Undoing it would delete the files the configs include (Sway would lose its colours)."""
        self.apply()
        with self.assertRaises(ht.LookError):
            ht.undo(self.place, reload=False)
        self.assertTrue((self.place.root / "hypeforge/theme/sway.conf").exists())

    def test_only_twenty_backups(self):
        for i in range(24):
            self.apply(theme="ember" if i % 2 else "kognogos-mocha")
        self.assertEqual(len([p for p in self.place.backups.iterdir() if p.is_dir()]), 20)

    def test_every_style_with_every_theme_fills_every_template(self):
        for s in ht.styles():
            for t in ht.themes():
                files, _ = ht.render(s, t, self.place, wallpaper=str(self.wall), check_names=False)
                for path, body in files.items():
                    self.assertNotIn("{{", body, f"{s}/{t}: {path.name}")


class Terminal(Base):
    def setUp(self):
        super().setUp()
        cfg = self.place.root / "alacritty/alacritty.toml"
        cfg.parent.mkdir(parents=True)
        cfg.write_text('[general]\nimport = [\n    "~/.config/alacritty/themes/KognogOS-theme.toml",\n    "/etc/extra.toml",\n]\n\n[font]\nsize = 12\n')
        self.cfg = cfg

    def imports(self):
        import tomllib
        return tomllib.loads(self.cfg.read_text())["general"]["import"]

    def test_the_terminal_follows_the_look(self):
        self.apply(theme="ember")
        imp = self.imports()
        ours = self.place.root / "alacritty/themes/hypeForge-desktop.toml"
        self.assertEqual(Path(imp[0]).expanduser(), ours, "our theme first: alacrittyForge's rule")
        self.assertIn("/etc/extra.toml", imp, "other imports stay")
        self.assertFalse(any("KognogOS-theme" in i for i in imp), "the old theme steps aside")
        body = ours.read_text()
        self.assertIn("Do not edit", body.splitlines()[0], "alacrittyForge shows it as locked")
        import tomllib
        self.assertEqual(tomllib.loads(body)["colors"]["primary"]["background"], ht.themes()["ember"]["term"]["bg"])
        self.assertIn("size = 12", self.cfg.read_text(), "the rest of the settings untouched")

    def test_a_theme_picked_in_alacrittyforge_wins(self):
        self.apply(theme="ember")
        self.cfg.write_text('[general]\nimport = ["~/.config/alacritty/themes/dracula.toml"]\n')
        self.apply(theme="kognogos-mocha")
        self.assertEqual(self.imports(), ["~/.config/alacritty/themes/dracula.toml"])
        self.assertEqual(self.place.read_state()["terminal"], "own")

    def test_undo_puts_the_old_import_back(self):
        self.apply()
        self.apply(theme="ember")
        ht.undo(self.place, reload=False)
        self.assertTrue(any("hypeForge-desktop" in i for i in self.imports()))


if __name__ == "__main__":
    unittest.main()
