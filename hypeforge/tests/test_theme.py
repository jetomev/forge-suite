"""hypeforge-theme (the look, D-78 step 1) on throwaway folders: roles, filters, today's look,
dry runs, names that must exist, backups and undo. Nothing here touches the desktop."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
import tempfile
import time
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

    def test_the_rices_icons_wear_its_text_colour_in_every_theme(self):
        """Javier, 2026-10-27: "Let's make the tray icons same colors as the elements of the other 2 islands…
        for all Rice themes, all the same." The right area's icons, the tray's one-colour icons and the
        bell take the areas' text colour (was the accent, pop.text)."""
        rice = ht.styles()["rice"]
        for slug, t in ht.themes().items():
            text = ht.resolve("bar_fg", rice, t)
            self.assertEqual(ht.resolve("module_icon", rice, t), text, slug)
            self.assertEqual(ht.resolve("tray_icon", rice, t), text, slug)

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

    def test_a_style_puts_its_title_bars_on_floating_windows_only(self):
        """Mac OS 9 had title bars on every window; Javier, 10-17: floating ones only (a tiled window with
        one was "not looking nice") — its look stays on the floating ones."""
        self.apply("mac-os-9", "light-gray")
        sway = self.read("hypeforge/theme/sway.conf")
        self.assertIn("default_border pixel 1", sway)
        self.assertIn("default_floating_border normal 1", sway)
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

    def test_classic_has_a_quiet_frame_in_fx(self):
        # D-80 (Javier, 10-10, look C): a quiet 2 px frame + 10 px at the screen edges + the others
        # dimmed; Mocha's focused frame is the 2:1 blend of border.subtle and border.strong
        self.apply("classic", "kognogos-mocha", say=lambda *_: None)
        fx = self.read("hypeforge/theme/fx.conf")
        self.assertIn("gaps outer 0", fx)
        self.assertIn("default_border pixel 2", fx)
        self.assertIn("client.focused          #585b70", fx)
        self.assertIn("client.unfocused        #313244", fx)
        self.assertIn("default_dim_inactive 0.12", fx)
        self.assertNotIn("bindsym", fx, "no key is redefined (SwayFX would show its config-errors bar)")
        sway = self.read("hypeforge/theme/sway.conf")
        self.assertIn("gaps outer 0", sway, "plain Sway keeps today's edges")

    def test_a_style_without_a_frame_redefines_the_float_key_quietly(self):
        st = ht.styles()["classic"]
        st = dict(st, fx=dict(st["fx"], frame=False))
        out = ht.fx_value(st, ht.themes()["kognogos-mocha"], "frame")
        self.assertIn("default_border none", out)
        self.assertIn("bindsym --no-warn $mod+Shift+space", out)

    def test_a_blend_of_two_roles(self):
        th = ht.themes()["kognogos-mocha"]
        self.assertEqual(ht.token(th, "border.subtle*2+border.strong"), "#585b70")
        self.assertEqual(ht.token(th, "surface.overlay"), "#313244")


class TheBarFollowsTheStyle(Base):
    """Look step 5: each style brings its bar's layout and stylesheet; Classic's is the hand-made
    one in sway/waybar/; all of them share modules.jsonc."""

    def test_classic_writes_todays_bar_unchanged(self):
        self.apply("classic", "kognogos-mocha", say=lambda *_: None)
        repo = Path(ht.REPO) / "sway/waybar"
        self.assertEqual(self.read("sway/waybar/config.jsonc"), (repo / "config.jsonc").read_text())
        self.assertEqual(self.read("sway/waybar/style.css"), (repo / "style.css").read_text())
        self.assertIn('"custom/cpu"', self.read("sway/waybar/modules.jsonc"))

    def test_the_rice_brings_its_own_bar(self):
        self.apply("rice", "kognogos-mocha", say=lambda *_: None)
        bar = self.read("sway/waybar/config.jsonc")
        self.assertIn('"group/workspace-pills"', bar)
        self.assertIn("${XDG_CONFIG_HOME:-$HOME/.config}/sway/waybar/modules.jsonc", bar,
                      "the bar finds its pieces wherever its config folder is (the bench, the desktop)")
        self.assertIn("background: transparent", self.read("sway/waybar/style.css"))

    def test_no_bar_places_waybars_mpris_module(self):
        # F-57 (2026-10-10): Waybar 0.15's mpris module crashed the live bar (SIGSEGV in its
        # playerctl callback) when a player started or stopped; the bench had no player to show it
        import json, re
        for bar in [Path(ht.REPO) / "sway/waybar/config.jsonc"] + sorted((Path(ht.REPO) / "styles").glob("*/bar/config.jsonc")):
            cfg = json.loads("\n".join(l for l in bar.read_text().splitlines() if not l.strip().startswith("//")))
            for one in cfg if isinstance(cfg, list) else [cfg]:
                placed = [m for k in ("modules-left", "modules-center", "modules-right") for m in one.get(k, [])]
                self.assertNotIn("mpris", placed, f"{bar}: mpris is placed again")

    def test_windows_11_starts_its_taskbar_applet_and_the_rice_none(self):
        self.apply("windows-11", "kognogos-mocha", say=lambda *_: None)
        sway = self.read("hypeforge/theme/sway.conf")
        self.assertIn("exec_always ", sway)
        self.assertIn("applets/taskbar/hypeforge-taskbar", sway)
        self.assertIn('"group/taskbar"', self.read("sway/waybar/config.jsonc"))
        self.assertIn('"position": "bottom"', self.read("sway/waybar/config.jsonc"))
        self.apply("rice", "kognogos-mocha", say=lambda *_: None)
        self.assertNotIn("exec_always", self.read("hypeforge/theme/sway.conf"))

    def test_every_file_the_bar_imports_exists_before_it_reloads(self):
        # F-58: Waybar quits on a missing @import; Windows 11 imports taskbar.css, which its
        # applet writes only once it runs — after the bar had already been told to reload
        self.apply("windows-11", "kognogos-mocha", say=lambda *_: None)
        self.assertTrue((self.place.root / "hypeforge/applets/taskbar.css").exists())
        self.assertTrue((self.place.root / "hypeforge/theme/colors.css").exists())

    def test_a_hover_never_wipes_a_buttons_picture(self):
        # Javier, 10-10: on Windows 11 the emblem vanished under the mouse — a hover rule set
        # "background:", which also clears the background picture; hovers set the colour only
        import re
        for css in sorted((Path(ht.REPO) / "styles").glob("*/bar/style.css")):
            for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css.read_text()):
                if ":hover" in sel:
                    self.assertNotRegex(body, r"(?<![-\w])background:", f"{css.parent.parent.name}: {sel.strip()}")

    def test_tray_icons_are_20_pixels_everywhere(self):
        """Javier, 2026-10-10: "the tray icons, in general, all themes … a few pixels bigger"."""
        root = Path(__file__).resolve().parent.parent
        for path in (root / "sway/waybar/modules.jsonc", root / "sway/waybar/config.jsonc"):
            with self.subTest(path.name):
                self.assertRegex(path.read_text(), r'"tray": \{\s*"icon-size": 20,')
        for path in root.glob("styles/*/bar/config.jsonc"):
            self.assertNotIn('"icon-size"', path.read_text(), f"{path}: one size for all, in modules.jsonc")

    @staticmethod
    def bar_tool():
        root = Path(__file__).resolve().parent.parent
        loader = importlib.machinery.SourceFileLoader("hfbar_order", str(root / "applets/bar/hypeforge-bar"))
        bar = importlib.util.module_from_spec(importlib.util.spec_from_loader("hfbar_order", loader))
        loader.exec_module(bar)
        return bar

    @staticmethod
    def every_bar():
        """(name, the bar's own config) for Classic and each style; COSMIC's and macOS's first bar only (the dock has none of this)."""
        import json
        root = Path(__file__).resolve().parent.parent
        bar = TheBarFollowsTheStyle.bar_tool()
        out = []
        for path in [root / "sway/waybar/config.jsonc"] + sorted(root.glob("styles/*/bar/config.jsonc")):
            cfg = json.loads(bar.strip_comments(path.read_text()))
            out.append((path.parent.parent.name if path.parent.name == "bar" else "classic", cfg[0] if isinstance(cfg, list) else cfg))
        return out

    def test_every_style_reads_volume_network_bluetooth_from_the_right(self):
        """Javier, 2026-10-10: "Volume, Network, and Bluetooth. From right to left" — the pill is one for
        every style now (D-96), so the order lives in modules.jsonc alone."""
        import json
        bar = self.bar_tool()
        shared = json.loads(bar.strip_comments((Path(ht.REPO) / "sway/waybar/modules.jsonc").read_text()))
        self.assertEqual(shared["group/quick"]["modules"], ["bluetooth", "network", "wireplumber"])
        self.assertEqual(shared["group/datetime"]["modules"], ["clock", "custom/notifications"])

    def test_every_style_places_the_three_shared_pieces_and_none_redefines_their_clicks(self):
        """D-96 (Javier, 2026-10-13): the date-time-bell piece and the Quick Settings pill on every style (the
        night light's moon too until D-117, 2026-10-25: now inside Quick Settings), defined ONCE in modules.jsonc: "when we improve on them, they work already for
        all the themes". A style may give the clock its own format; the clicks stay the shared ones."""
        bar = self.bar_tool()
        for name, cfg in self.every_bar():
            with self.subTest(name):
                shown = bar.placed(bar.merged(cfg) if "include" in cfg else cfg)
                for piece in ("group/datetime", "group/quick"):
                    self.assertIn(piece, shown, f"{name}: {piece} not placed")
                # D-117 (Javier, 2026-10-25): "remove the night light icon, outside the quick settings from all
                # themes"; the piece stays defined in modules.jsonc for the optional-icon setting
                self.assertNotIn("custom/nightlight", shown, f"{name}: the moon is back on the bar")
                self.assertNotIn("mpris", shown)
                for piece in ("clock", "custom/notifications", "network", "bluetooth", "wireplumber", "custom/nightlight",
                              "group/quick", "group/datetime"):
                    own = cfg.get(piece, {})
                    self.assertFalse({k for k in own if k.startswith("on-click")} or piece.startswith("group/") and own,
                                     f"{name}: {piece} redefines what the shared piece does ({sorted(own)})")
                self.assertIn("modules.jsonc", " ".join(cfg.get("include", [])), f"{name}: the shared pieces aren't included")

    def test_every_style_gives_the_status_icons_their_own_room(self):
        """Javier, 2026-10-10, on macOS: "They are all one over the other" — its stylesheet padded only
        "#quick > *", which never reaches the icons; each must be padded by its own name."""
        import re
        for css in sorted(Path(ht.REPO).glob("styles/*/bar/style.css")):
            rules = re.findall(r"([^{}]+)\{([^}]*)\}", re.sub(r"/\*.*?\*/", "", css.read_text(), flags=re.S))
            for icon in ("#bluetooth", "#network", "#wireplumber"):
                with self.subTest(f"{css.parent.parent.name} {icon}"):
                    padded = any(re.search(rf"{icon}(?![\w:-])", sel) and "padding" in body for sel, body in rules)
                    self.assertTrue(padded, f"{css}: no padding names {icon}")

    def test_windows_11_has_no_search_pill_and_javiers_quick_order(self):
        import json
        bar = Path(ht.REPO) / "styles/windows-11/bar/config.jsonc"
        cfg = json.loads("\n".join(l for l in bar.read_text().splitlines() if not l.strip().startswith("//")))
        self.assertNotIn("custom/search", cfg["modules-left"])
        self.assertIn("group/quick", cfg["modules-right"], "Javier's Quick Settings pill, now every style's (D-96)")

    def test_a_style_without_a_bar_leaves_the_bar_alone(self):
        st = dict(ht.styles()["rice"], meta=dict(ht.styles()["rice"]["meta"], slug="no-bar-here"))
        self.assertEqual(ht.bar_files(st), {})

    def test_undo_brings_the_old_bar_back(self):
        self.apply("classic", "kognogos-mocha", say=lambda *_: None)
        before = self.read("sway/waybar/config.jsonc")
        self.apply("rice", "kognogos-mocha", say=lambda *_: None)
        self.assertNotEqual(self.read("sway/waybar/config.jsonc"), before)
        ht.undo(self.place, reload=False, say=lambda *_: None)
        self.assertEqual(self.read("sway/waybar/config.jsonc"), before)


class Gaps(Base):
    """Javier, 2026-10-11: the space at the screen edges is the same as between windows, in every style.
    Sway adds the outer gap to the inner one at the edges, so the outer one must be 0."""

    def test_every_style_has_the_same_space_at_the_edges(self):
        for slug in ht.styles():
            with self.subTest(style=slug):
                self.apply(slug, "kognogos-mocha", say=lambda *_: None)
                conf = self.read("hypeforge/theme/sway.conf")
                self.assertIn("gaps outer 0", conf, f"{slug}: the edges would get double the gap")

    def test_open_workspaces_get_the_new_gaps_in_the_order_sway_reads_them(self):
        self.apply("rice", "kognogos-mocha", say=lambda *_: None)
        fx = self.place.root / "hypeforge/theme/fx.conf"
        fx.write_text("gaps outer 3\n")
        plain = "include ~/.config/hypeforge/theme/sway.conf\ninclude /etc/sway/config.d/*\n"
        self.assertEqual(ht.live_gaps(self.place.root, plain), ["gaps inner all set 10", "gaps outer all set 0"])
        login_fx = plain + "include ~/.config/hypeforge/theme/fx.conf\n"
        self.assertEqual(ht.live_gaps(self.place.root, login_fx), ["gaps inner all set 10", "gaps outer all set 3"],
                         "the SwayFX login reads fx.conf last, so it wins")
        self.assertEqual(ht.live_gaps(self.place.root, "include /etc/sway/config.d/*\n"), [], "no look file, nothing set")


class OpenAppsRepaint(Base):
    """F-70, Javier 2026-10-11: an open Chrome kept the colours it opened with. Open GTK apps only
    reload on a new GTK theme NAME, and ~/.config/gtk-3.0/gtk.css outranks the theme and is never
    re-read: the colours live in a named theme of the look's own."""

    def name(self):
        ini = self.read("gtk-3.0/settings.ini")
        return next(l.split("=", 1)[1] for l in ini.splitlines() if l.startswith("gtk-theme-name="))

    def test_new_colours_are_a_new_theme_name(self):
        self.apply("rice", "kognogos-mocha", say=lambda *_: None)
        first = self.name()
        self.apply("rice", "dark-red", say=lambda *_: None)
        self.assertNotEqual(self.name(), first, "same name: open apps would never repaint")
        self.assertTrue(self.name().startswith("hypeForge-rice-dark-red-"))
        self.assertIn(f"gtk-theme-name={self.name()}", self.read("gtk-4.0/settings.ini"))

    def test_the_colours_live_in_the_theme_not_the_user_file(self):
        self.apply("rice", "dark-red", say=lambda *_: None)
        self.assertNotIn("@define-color", self.read("gtk-3.0/gtk.css"), "it would outrank the theme")
        own = self.place.gtk_themes / self.name()
        css = (own / "gtk-3.0/gtk.css").read_text()
        self.assertIn("@define-color headerbar_bg_color", css)
        self.assertTrue((own / "gtk-4.0/gtk.css").is_file() and (own / "index.theme").is_file())
        if ht.gtk_base_dir("adw-gtk3-dark"):
            self.assertTrue(css.startswith('@import url("file://'), "built on the palette's GTK theme")

    def test_undo_names_a_theme_that_still_exists(self):
        self.apply("rice", "kognogos-mocha", say=lambda *_: None)
        first = self.name()
        self.apply("rice", "light-blue", say=lambda *_: None)
        ht.undo(self.place, reload=False, say=lambda *_: None)
        self.assertEqual(self.name(), first)
        self.assertTrue((self.place.gtk_themes / first / "gtk-3.0/gtk.css").is_file())

    def test_old_themes_are_pruned(self):
        for t in list(ht.themes())[:ht.GTK_KEEP + 4]:
            self.apply("rice", t, say=lambda *_: None, make_wallpaper=False)
        # the new one, the one on screen until now, and GTK_KEEP older ones
        self.assertLessEqual(len(list(self.place.gtk_themes.glob("hypeForge-*"))), ht.GTK_KEEP + 2)


class Wallpaper(Base):
    """themeForge's Wallpaper page (Javier, 2026-10-11): the Rice's KognogOS backgrounds in every colour
    theme, one topic per other style, the person's own pictures, five ways to lay them, every screen the same."""

    def sway(self):
        return self.read("hypeforge/theme/sway.conf")

    def test_every_style_names_a_topic_the_generator_or_kognogos_draws(self):
        gen = ht.WALLGEN.read_text()
        for slug, st in ht.styles().items():
            with self.subTest(style=slug):
                topic = st.get("wallpaper", {}).get("topic")
                self.assertTrue(topic, "each style has its topic")
                self.assertTrue(topic == "kognogos" or f'"{topic}": m_' in gen, f"{topic} is drawn somewhere")
        self.assertEqual(ht.styles()["rice"]["wallpaper"]["topic"], "kognogos", "the Rice: KognogOS only (Javier)")

    def test_kognogos_mocha_is_the_original_exactly(self):
        import numpy as np
        from PIL import Image
        orig = Path("/usr/share/wallpapers/kognog/Kognog OS Semi - Logo Catpuccin Mocha.png")
        if not orig.exists():
            self.skipTest("the KognogOS wallpapers aren't installed")
        made = ht.kognogos_wallpaper("tier-aware", "kognogos-mocha", ht.themes()["kognogos-mocha"], self.place.cache)
        d = np.abs(np.asarray(Image.open(orig).convert("RGB")).astype(int)
                   - np.asarray(Image.open(made).convert("RGB")).astype(int)).max()
        self.assertLessEqual(d, 4, "the lifted art laid on Mocha is the shipped picture")

    def test_the_colour_variants_differ_and_their_words_read(self):
        a = ht.wallpaper_colours("red", ht.themes()["red"])
        b = ht.wallpaper_colours("green", ht.themes()["green"])
        self.assertNotEqual(a[0], b[0], "Red is not Green: the theme's own colour band, not a neutral gray")
        for slug, t in ht.themes().items():
            bg, words = ht.wallpaper_colours(slug, t)
            self.assertGreaterEqual(ht._contrast(bg, words), 4.5, f"{slug}: the words read")

    def test_the_drawn_topics_can_be_picked_on_their_own(self):
        """Javier, 2026-10-17: on the Rice, the other styles' drawn topics too, in the colours in use (topic:<name>)."""
        topics = [t for t, _ in ht.drawn_topics()]
        self.assertEqual(sorted(topics), sorted({st["wallpaper"]["topic"] for st in ht.styles().values()} - {"kognogos"}),
                         "every style's drawn topic, KognogOS left out (it has its own choices)")
        self.assertEqual(ht.wallpaper_choice("topic:mountains"), "topic:mountains", "kept as it is, like kognogos:")
        pic = ht.picture_for("topic:mountains", "rice", "kognogos-mocha", self.place.cache)
        self.assertTrue(pic.name.startswith("mountains-kognogos-mocha-") and pic.is_file(), pic)
        with self.assertRaises(ht.LookError):
            ht.picture_for("topic:nope", "rice", "kognogos-mocha", self.place.cache)
        self.apply("rice", "dark-red", wallpaper="topic:circuit", say=lambda *_: None)
        line = next(l for l in self.sway().splitlines() if l.startswith("output"))
        self.assertIn("circuit-dark-red-", line, "the Rice keeps its style and wears the circuit board")

    def test_the_rice_shows_kognogos_and_every_screen_gets_the_same_line(self):
        self.apply("rice", "dark-red", wallpaper="theme", say=lambda *_: None)
        line = next(l for l in self.sway().splitlines() if l.startswith("output"))
        self.assertTrue(line.startswith('output * bg "') and "kognogos-tier-aware-dark-red-" in line, line)
        self.assertTrue(line.endswith(" fill " + ht.wallpaper_colours("dark-red", ht.themes()["dark-red"])[0]))

    def test_fits_and_solid(self):
        for fit in ht.FITS:
            self.apply("rice", "blue", wallpaper="kognogos:arch-distro", fit=fit, say=lambda *_: None)
            self.assertIn(f'" {fit} #', self.sway())
        self.apply("rice", "blue", wallpaper="solid", say=lambda *_: None)
        self.assertIn("output * bg #", self.sway())
        self.assertIn("solid_color", self.sway())
        with self.assertRaises(ht.LookError):
            self.apply("rice", "blue", fit="sideways", say=lambda *_: None)

    def test_a_picture_of_yours_stays_when_the_colours_change(self):
        self.apply("rice", "kognogos-mocha", wallpaper=str(self.wall), fit="center", say=lambda *_: None)
        self.apply("rice", "light-pink", wallpaper=None, say=lambda *_: None)     # no wallpaper said: keep it
        self.assertIn(f'output * bg "{self.wall}" center', self.sway())
        look = ht.read_look(self.place)["wallpaper"]
        self.assertEqual((look["picture"], look["fit"]), (str(self.wall), "center"), "the look file says so")

    def test_an_old_look_file_keeps_the_wallpaper_on_screen(self):
        self.apply("rice", "kognogos-mocha", wallpaper=str(self.wall), say=lambda *_: None)
        f = self.place.root / ht.LOOK
        f.write_text('theme = "rice"\ncolors = "blue"\n')        # written before the Wallpaper page
        want = ht.read_look(self.place)
        self.assertIsNone(want["wallpaper"]["picture"])
        self.apply(want["theme"], want["colors"], wallpaper=want["wallpaper"]["picture"], say=lambda *_: None)
        self.assertIn(f'"{self.wall}"', self.sway())

    def test_undo_brings_the_wallpaper_back_too(self):
        self.apply("rice", "kognogos-mocha", wallpaper=str(self.wall), say=lambda *_: None)
        self.apply("rice", "kognogos-mocha", wallpaper="solid", say=lambda *_: None)
        ht.undo(self.place, reload=False, say=lambda *_: None)
        self.assertIn(f'"{self.wall}"', self.sway())


class Corners(Base):
    """Javier, 2026-10-10: rounded or straight corners, for every style with every theme."""

    def test_straight_makes_every_corner_square(self):
        self.apply("rice", "kognogos-mocha", corners="straight", say=lambda *_: None)
        import re
        css = self.read("sway/waybar/style.css")
        self.assertFalse(re.findall(r"border-radius:\s*[1-9]", css), "no rounded corner left on the bar")
        self.assertIn("corner_radius 0", self.read("hypeforge/theme/fx.conf"))
        self.assertIn("radius=0", self.read("hypeforge/theme/fuzzel-colors.ini").replace(" ", ""))
        self.assertIn("border-radius=0", self.read("mako/config"))
        self.assertEqual(self.place.read_state()["corners"], "straight", "the choice is remembered")

    def test_the_choice_stays_through_the_next_apply(self):
        self.apply("rice", "kognogos-mocha", corners="straight", say=lambda *_: None)
        self.apply("windows-11", "blue", say=lambda *_: None)
        self.assertIn("corner_radius 0", self.read("hypeforge/theme/fx.conf"))

    def test_rounded_rounds_a_square_style_and_style_keeps_its_own(self):
        os9 = ht.styles()["mac-os-9"]
        self.assertEqual(ht.with_corners(os9, "rounded")["shape"]["radius_window"], 12)
        self.assertIs(ht.with_corners(os9, "style"), os9)
        cosmic = ht.with_corners(ht.styles()["cosmic"], "straight")
        self.assertEqual(ht.shape_of(cosmic, "radius_window"), 0, "COSMIC's roundness choice gives way too")

    def test_a_wrong_choice_stops_before_writing(self):
        with self.assertRaises(ht.LookError):
            ht.with_corners(ht.styles()["rice"], "wavy")


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


class ASwitchStopsTheOldStylesApplets(unittest.TestCase):
    """Windows 11's Taskbar applet has nothing to do on the Rice (2026-10-10): a switch stops the old
    style's applets by their saved process number — and only when that process is still the applet."""

    def setUp(self):
        import subprocess
        self.sp = subprocess
        self.run = Path(tempfile.mkdtemp(prefix="hfstop."))
        self.procs = []

    def tearDown(self):
        for p in self.procs:
            p.kill()
            p.wait()

    def fake(self, words: str):
        p = self.sp.Popen([sys.executable, "-c", "import time; time.sleep(30)", words])
        self.procs.append(p)
        time.sleep(0.2)
        return p

    def test_the_taskbar_stops_when_the_new_style_has_none(self):
        p = self.fake("hypeforge-taskbar")
        (self.run / "hypeforge-taskbar.pid").write_text(str(p.pid))
        self.assertEqual(ht.stop_other_applets([], say=lambda *_: None, runtime=self.run), ["taskbar"])
        p.wait(timeout=5)

    def test_it_stays_when_the_new_style_uses_it(self):
        p = self.fake("hypeforge-taskbar")
        (self.run / "hypeforge-taskbar.pid").write_text(str(p.pid))
        self.assertEqual(ht.stop_other_applets(["taskbar"], say=lambda *_: None, runtime=self.run), [])
        self.assertIsNone(p.poll())

    def test_a_reused_process_number_is_never_stopped(self):
        p = self.fake("somebody-elses-program")
        (self.run / "hypeforge-taskbar.pid").write_text(str(p.pid))
        self.assertEqual(ht.stop_other_applets([], say=lambda *_: None, runtime=self.run), [])
        self.assertIsNone(p.poll())

    def test_a_style_names_its_applets_as_a_list(self):
        self.assertEqual(ht.style_applets(ht.styles()["mac-os-9"]), ["menubar"])
        self.assertEqual(ht.style_applets(ht.styles()["cosmic"]), ["taskbar"], "the dock's apps")
        self.assertEqual(ht.style_applets({"layout": {"applets": "separate-popups"}}), [], "a word isn't a list")

    def test_no_control_strip_anywhere(self):
        """Javier, 2026-10-10: "no need to have same buttons in several places … forget about the strip"."""
        self.assertFalse((ht.REPO / "applets/strip").exists())
        for s in ht.styles().values():
            self.assertNotIn("strip", ht.style_applets(s))

class NotificationCards(Base):
    """D-116 (Javier, 2026-10-20): the notifications wear the pop-up standard on every style — before 2026-10-24
    each style gave them its own corners (KDE 8, Rice 14, Mac OS 9 square…), 420 px and no app icon."""

    def mako(self, style, corners):
        files, _pic = ht.render(style, "dark-blue", self.place, str(self.wall), False, False, corners, None)
        return files[self.place.root / "mako/config"]

    def test_every_style_every_corners_choice(self):
        t = ht.themes()["dark-blue"]
        for style in ht.styles():
            for corners in ("style", "rounded", "straight"):
                conf = self.mako(style, corners)
                s = ht.with_corners(ht.styles()[style], corners)
                why = f"{style}, corners {corners}"
                self.assertIn(f"border-radius={0 if corners == 'straight' else 10}\n", conf, why)
                self.assertIn("border-size=1\n", conf, why)
                self.assertIn("font=Noto Sans 10.5\n", conf, why)
                self.assertIn("width=460\n", conf, why)
                self.assertIn(f"background-color={ht.resolve('panel_bg', s, t)}\n", conf, why)
                self.assertIn(f"border-color={ht.resolve('panel_border', s, t)}\n", conf, why)
                self.assertNotIn("{{", conf, why)

    def test_the_title_is_bold_and_the_percent_is_mako_safe(self):
        conf = self.mako("kde", "style")
        line = next(l for l in conf.splitlines() if l.startswith("format="))
        self.assertIn("<b>", line)
        self.assertIn('size="110%%"', line, "a lone % is one of mako's fill-in codes: the whole file is refused")

    def test_mako_is_pointed_at_the_icon_map_first(self):
        conf = self.mako("kde", "style")
        path = next(l for l in conf.splitlines() if l.startswith("icon-path="))[len("icon-path="):]
        self.assertEqual(path.split(":")[0], str(self.place.note_icons))
        self.assertIn(f"max-icon-size={ht.POPUP['icon']}\n", conf)

    def test_the_icon_map_puts_a_theme_in_makos_order(self):
        base = Path(self.tmp.name) / "icons"
        for rel in ("fake/apps/scalable/drawn.svg", "fake/places/48/sized.svg", "fake/16x16/apps/already.png"):
            (base / rel).parent.mkdir(parents=True, exist_ok=True)
            (base / rel).write_text("x")
        out = Path(self.tmp.name) / "map"
        self.assertEqual(ht.note_icon_map(out, "fake", bases=(base,)), 2)
        n = ht.POPUP["icon"]
        self.assertTrue((out / f"{n}x{n}/apps/drawn.svg").exists(), "a drawing folder: named for the icon size")
        self.assertTrue((out / "48x48/places/sized.svg").exists())
        self.assertFalse((out / "16x16").exists(), "already size/kind: mako reads the theme itself")
        self.assertEqual(ht.note_icon_map(out, "fake", bases=(base,)), 2, "rebuilt, not added to")
        self.assertEqual([p.name for p in out.parent.iterdir() if p.name.startswith("map")], ["map"], "no .new or .old left")

    def test_an_apply_lays_the_map(self):
        self.apply("kde", "dark-blue", say=lambda *_: None, corners="style")
        self.assertTrue(self.place.note_icons.is_dir())


if __name__ == "__main__":
    unittest.main()
