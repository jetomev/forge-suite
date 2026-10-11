"""themeForge's page, driven headless with a stand-in look (nothing is applied for real)."""

from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from textual.widgets import Select

from themeforge.app import ThemeForgeApp, swatch_markup
from themeforge.look import Look
from tests.test_look import fake_home


def run(c):
    return asyncio.run(c)


class FakeLook(Look):
    def __init__(self, home, conf):
        super().__init__(home, conf, log=conf / "tf.log")
        self.done = []

    def apply(self, style, theme, wallpaper=None):
        self.done.append(("apply", style, theme) + ((wallpaper,) if wallpaper else ()))
        pic, fit = (wallpaper or {}).get("picture") or self.wallpaper_now()[0], (wallpaper or {}).get("fit") or "fill"
        (self.config / "hypeforge/theme/state.toml").write_text(
            f'style = "{style}"\ntheme = "{theme}"\nwallpaper = "{pic}"\nfit = "{fit}"\n')
        return True, "the bar restarted"

    def picture_path(self, style, theme, choice):
        """A small stand-in picture: red for the theme's own, the theme's colour for solid."""
        from PIL import Image
        out = self.config / f"pic-{choice.replace(':', '-')}.png"
        Image.new("RGB", (64, 36), (200, 30, 30) if choice != "solid" else (10, 20, 30)).save(out)
        return out

    def undo(self):
        self.done.append(("undo",))
        return True, "back"


class Page(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        home, conf = fake_home(root), root / "config"
        (conf / "hypeforge/theme").mkdir(parents=True)
        (conf / "hypeforge/theme/state.toml").write_text('style = "rice"\ntheme = "mocha"\n')
        self.look = FakeLook(home, conf)

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_menu(self):
        app = ThemeForgeApp(self.look)
        self.assertEqual([m["title"] for m in app.MENU], ["Theme Picker", "Wallpaper", "Help", "Quit"])

    def test_two_drop_downs_showing_the_look_in_use(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                self.assertEqual(len(list(app.query("#sec-picker Select"))), 2)
                self.assertEqual(app.query_one("#tf-style", Select).value, "rice")
                self.assertEqual(app.query_one("#tf-colour", Select).value, "mocha")
                self.assertIn("Linux rice", str(app.query_one("#tf-now").render()))
                self.assertEqual(str(app.query_one("#tf-style-about").render()), "about rice")
                self.assertFalse(app.changes_bar.display, "nothing picked yet")
        run(go())

    def test_picking_shows_the_bar_and_f10_applies_through_hypeforge(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                app.query_one("#tf-colour", Select).value = "white"
                await pilot.pause()
                self.assertTrue(app.changes_bar.display, "picked, not applied: the bar says so")
                await pilot.press("f10")
                await app.workers.wait_for_complete()
                await pilot.pause()
                self.assertEqual(self.look.done, [("apply", "rice", "white")])
                self.assertEqual(app.look.current(), ("rice", "white"))
                self.assertFalse(app.changes_bar.display, "applied: nothing pending")
        run(go())

    def test_the_same_look_again_does_nothing(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                await pilot.press("f10")
                await pilot.pause()
                self.assertEqual(self.look.done, [])
        run(go())

    def test_undo_runs_hypeforges_undo(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                app.action_undo()
                await app.workers.wait_for_complete()
                await pilot.pause()
                self.assertEqual(self.look.done, [("undo",)])
        run(go())

    def test_put_back_returns_the_drop_downs_to_the_look_in_use(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                app.query_one("#tf-style", Select).value = "classic"
                await pilot.pause()
                app.query_one("#tf-bar-back").press()
                await pilot.pause()
                await pilot.pause()
                self.assertEqual(app.query_one("#tf-style", Select).value, "rice")
                self.assertFalse(app.changes_bar.display)
        run(go())

    def test_the_options_are_a_two_column_matrix_with_small_buttons(self):
        """Javier, 2026-10-11: "a matrix of 2 x number of options going down … Button sizes, please, not
        the big ones"."""
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(110, 32)) as pilot:
                await pilot.pause()
                theme, colours = app.query_one("#tf-style").region, app.query_one("#tf-colour").region
                self.assertEqual(theme.y, colours.y, "Theme and Colors side by side")
                self.assertGreater(colours.x, theme.x + theme.width)
                for b in app.query("#sec-picker Button.tf-small"):
                    self.assertEqual(b.region.height, 1, f"{b.id} is one line tall")
                self.assertEqual(str(app.query_one("#tf-el-bar").render()), "—", "the fake theme brings no elements")
        run(go())

    def test_the_swatch_is_coloured_blocks(self):
        self.assertIn("[on #123456]", swatch_markup(["#123456", "#abcdef"]))


class WallpaperPage(unittest.TestCase):
    """Desktop background 1.0 (Javier, 2026-10-11): the theme's own, KognogOS, solid or your pictures from a
    folder; Fill, Fit, Stretch, Center, Tile; a small preview in the terminal; every screen the same."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        home, conf = fake_home(root), root / "config"
        (home / "assets/wallpaper").mkdir(parents=True)
        for d in ("tier-aware", "arch-distro"):
            (home / f"assets/wallpaper/kognogos-{d}.json").write_text("{}")
        (conf / "hypeforge/theme").mkdir(parents=True)
        (conf / "hypeforge/theme/state.toml").write_text('style = "rice"\ntheme = "mocha"\nwallpaper = "theme"\nfit = "fill"\n')
        self.pics = root / "walls"
        self.look = FakeLook(home, conf)

    def tearDown(self):
        self.tmp.cleanup()

    async def open_page(self, pilot, app):
        await pilot.pause()
        app.query_one("#sec-wallpaper").display = True
        app.query_one("#sec-picker").display = False
        await pilot.pause()

    def test_four_drop_downs_in_two_columns_and_the_look_in_use(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(120, 40)) as pilot:
                await self.open_page(pilot, app)
                src, fit = app.query_one("#tf-wp-source").region, app.query_one("#tf-wp-fit").region
                self.assertEqual(src.y, fit.y, "Source and Fit side by side")
                self.assertEqual(app.query_one("#tf-wp-source", Select).value, "theme")
                self.assertEqual(app.query_one("#tf-wp-fit", Select).value, "fill")
                values = [v for _, v in app.query_one("#tf-wp-source", Select)._options if v is not Select.NULL]
                self.assertEqual(values, ["theme", "kognogos:tier-aware", "kognogos:arch-distro", "mine", "solid"],
                                 "Tier Aware first (Javier's pick)")
                self.assertFalse(app.changes_bar.display, "nothing picked yet")
                for b in app.query("#sec-wallpaper Button.tf-small"):
                    if b.display:
                        self.assertEqual(b.region.height, 1, f"{b.id} is one line tall")
        run(go())

    def test_a_pick_shows_the_bar_and_f10_applies_the_wallpaper(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(120, 40)) as pilot:
                await self.open_page(pilot, app)
                app.query_one("#tf-wp-source", Select).value = "solid"
                app.query_one("#tf-wp-fit", Select).value = "center"
                await pilot.pause()
                self.assertTrue(app.changes_bar.display)
                await pilot.press("f10")
                await app.workers.wait_for_complete()
                await pilot.pause()
                self.assertEqual(len(self.look.done), 1)
                what = self.look.done[0]
                self.assertEqual(what[:3], ("apply", "rice", "mocha"), "the theme in use is kept")
                self.assertEqual((what[3]["picture"], what[3]["fit"]), ("solid", "center"))
        run(go())

    def test_my_pictures_from_a_folder_and_making_the_folder(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(120, 40)) as pilot:
                await self.open_page(pilot, app)
                app.query_one("#tf-wp-source", Select).value = "mine"
                app.query_one("#tf-wp-folder").value = str(self.pics)
                app.query_one("#sec-wallpaper").new_folder()
                await pilot.pause()
                self.assertTrue(app.query_one("#tf-wp-mkdir").display, "offer to make the missing folder")
                self.assertIn("doesn't exist", str(app.query_one("#tf-wp-folder-about").render()))
                app.query_one("#tf-wp-source").focus()
                await pilot.press("n")
                await pilot.pause()
                self.assertTrue(self.pics.is_dir(), "n made it")
                from PIL import Image
                for name in ("b.png", "a.jpg", "notes.txt"):
                    (Image.new("RGB", (8, 8)).save(self.pics / name) if name != "notes.txt"
                     else (self.pics / name).write_text("x"))
                app.query_one("#sec-wallpaper").new_folder()
                await pilot.pause()
                names = [n for n, v in app.query_one("#tf-wp-picture", Select)._options if v is not Select.NULL]
                self.assertEqual(names, ["a.jpg", "b.png"], "pictures only, by name")
                self.assertFalse(app.changes_bar.display, "no picture picked yet: nothing to apply")
                app.query_one("#tf-wp-picture", Select).value = str(self.pics / "b.png")
                await pilot.pause()
                self.assertTrue(app.changes_bar.display)
        run(go())

    def test_the_theme_s_own_follows_the_theme_picked(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause()
                label = lambda: dict((v, n) for n, v in app.query_one("#tf-wp-source", Select)._options)["theme"]
                self.assertIn("rice picture", label())
                app.query_one("#tf-style", Select).value = "classic"
                await pilot.pause()
                self.assertIn("classic picture", label(), "the Theme page's pick, not the one in use")
                self.assertEqual(app.query_one("#tf-wp-source", Select).value, "theme", "the choice is kept")
        run(go())

    def test_the_preview_is_drawn_in_the_terminal(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(120, 40)) as pilot:
                await self.open_page(pilot, app)
                await app.workers.wait_for_complete()
                await pilot.pause()
                text = str(app.query_one("#tf-wp-preview").render())
                self.assertGreater(text.count("▀"), 500, "rows of half blocks")
        run(go())


if __name__ == "__main__":
    unittest.main()
