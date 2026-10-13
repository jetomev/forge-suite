"""themeForge's page, driven headless with a stand-in look (nothing is applied for real)."""

from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from textual.widgets import OptionList, Select

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
    """Desktop background (Javier, 2026-10-11, D-6 then D-8): Source = a folder + Browse, or the theme's
    pictures; Images = every picture in it; pick one → preview below + Apply Background; Fit Style in simple
    names; every screen the same."""

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
        (self.pics / "more").mkdir(parents=True)
        (self.pics / ".hidden").mkdir()
        from PIL import Image
        for name in ("b.png", "a.jpg", "more/c.png"):
            Image.new("RGB", (8, 8)).save(self.pics / name)
        (self.pics / "notes.txt").write_text("x")
        self.look = FakeLook(home, conf)

    def tearDown(self):
        self.tmp.cleanup()

    async def open_page(self, pilot, app):
        await pilot.pause()
        app.query_one("#sec-wallpaper").display = True
        app.query_one("#sec-picker").display = False
        app.on_section_shown("wallpaper")
        await pilot.pause()
        await pilot.pause()

    @staticmethod
    def images(app) -> list[str]:
        ol = app.query_one("#tf-wp-images", OptionList)
        return [ol.get_option_at_index(i).id for i in range(ol.option_count)]

    @staticmethod
    def pick(app, value: str) -> None:
        ol = app.query_one("#tf-wp-images", OptionList)
        ol.highlighted = WallpaperPage.images(app).index(value)
        ol.action_select()

    def test_source_images_and_fit_style_with_the_look_in_use(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(120, 40)) as pilot:
                await self.open_page(pilot, app)
                src, fit = app.query_one("#tf-wp-source").region, app.query_one("#tf-wp-fit").region
                self.assertEqual(src.y, fit.y, "Source and Fit Style side by side")
                self.assertEqual(str(app.query_one("#tf-wp-source").render()), "The theme's pictures",
                                 "the theme's own is on screen: the Source is the theme's pictures")
                self.assertEqual(self.images(app), ["theme", "kognogos:tier-aware", "kognogos:arch-distro", "solid"],
                                 "Tier Aware first (Javier's pick)")
                ol = app.query_one("#tf-wp-images", OptionList)
                self.assertIn("in use", str(ol.get_option_at_index(0).prompt))
                self.assertTrue(ol.has_focus, "the page opens on the Images list")
                self.assertEqual(app.query_one("#tf-wp-fit", Select).value, "fill")
                self.assertIn("cropped", str(app.query_one("#tf-wp-fit-about").render()), "each Fit Style explained under it")
                self.assertEqual([n for n, _ in app.query_one("#tf-wp-fit", Select)._options],
                                 ["Fill the Screen", "Whole Picture", "Stretched", "Real Size", "Repeated"], "simple names")
                self.assertTrue(app.query_one("#tf-wp-apply").disabled, "nothing picked: Apply Background is off")
                self.assertFalse(app.changes_bar.display)
                self.assertIn("the theme's own", str(app.query_one("#tf-wp-now").render()))
                for b in app.query("#sec-wallpaper Button.tf-small"):
                    if b.display:
                        self.assertEqual(b.region.height, 1, f"{b.id} is one line tall")
        run(go())

    def test_a_pick_lights_apply_background_and_f10_applies_it(self):
        """D-9: the wallpaper has its own button; the changes bar is the theme's."""
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(120, 40)) as pilot:
                await self.open_page(pilot, app)
                self.pick(app, "solid")
                app.query_one("#tf-wp-fit", Select).value = "center"
                await pilot.pause()
                self.assertFalse(app.query_one("#tf-wp-apply").disabled, "picked: Apply Background is on")
                self.assertFalse(app.changes_bar.display, "the bar is for the theme; the page has its button")
                ol = app.query_one("#tf-wp-images", OptionList)
                self.assertIn("●", str(ol.get_option_at_index(3).prompt), "the pick is marked")
                await pilot.press("f10")
                await app.workers.wait_for_complete()
                await pilot.pause()
                self.assertEqual(len(self.look.done), 1)
                what = self.look.done[0]
                self.assertEqual(what[:3], ("apply", "rice", "mocha"), "the theme in use is kept")
                self.assertEqual((what[3]["picture"], what[3]["fit"], what[3]["folder"]), ("solid", "center", None))
                await pilot.pause()
                self.assertTrue(app.query_one("#tf-wp-apply").disabled, "applied: nothing pending")
                self.assertIn("in use", str(app.query_one("#tf-wp-images", OptionList).get_option_at_index(3).prompt))
        run(go())

    def test_after_an_apply_the_images_list_is_still_there_filled_and_in_focus(self):
        """F-71 (Javier, 2026-10-13): "After I applied it, the images list disappeared. Can't select images
        from the Images box anymore." The page is updated in place; the list is the same widget, full, focused."""
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(120, 40)) as pilot:
                await self.open_page(pilot, app)
                app.query_one("#sec-wallpaper").use_source(str(self.pics))
                await pilot.pause()
                before = app.query_one("#tf-wp-images", OptionList)
                self.pick(app, str(self.pics / "a.jpg"))
                app.query_one("#tf-wp-fit", Select).value = "tile"
                await pilot.pause()
                await pilot.press("f10")
                await app.workers.wait_for_complete()
                await pilot.pause(0.5)
                after = app.query_one("#tf-wp-images", OptionList)
                self.assertIs(after, before, "the same list, not a new empty one")
                self.assertEqual([Path(v).name for v in self.images(app)], ["a.jpg", "b.png"], "still full")
                self.assertTrue(after.has_focus, "still the thing in focus")
                self.assertIn("in use", str(after.get_option_at_index(0).prompt))
                self.assertEqual(app.query_one("#tf-wp-fit", Select).value, "tile", "the fit shows what is in use")
                self.assertTrue(app.query_one("#tf-wp-apply").disabled, "nothing pending after the apply")
                await pilot.press("down")
                await pilot.press("enter")
                await pilot.pause()
                self.assertFalse(app.query_one("#tf-wp-apply").disabled, "and the next pick works")
        run(go())

    def test_browse_is_a_tree_of_folders_with_the_pictures_beside_it(self):
        """D-10 (Javier, 2026-10-13): "something like a file manager window popup … folders … tree … a
        very simplified midnight commander". Home open by default; the folder in use under the cursor."""
        from themeforge.browse import THEME_MADE, FolderPicker, FolderTree
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(120, 40)) as pilot:
                await self.open_page(pilot, app)
                app.query_one("#sec-wallpaper").use_source(str(self.pics / "more"))
                await pilot.pause()
                await pilot.press("b")
                await pilot.pause()
                self.assertIsInstance(app.screen, FolderPicker, "b opens the Browse window")
                tree = app.screen.query_one("#tf-br-tree", FolderTree)
                self.assertEqual([str(n.label) for n in tree.root.children][:2], ["The theme's pictures", "Home"])
                self.assertEqual(tree.cursor_node.data, str(self.pics / "more"), "the folder in use is under the cursor")
                self.assertIn("1 picture", str(app.screen.query_one("#tf-br-where").render()))
                files = app.screen.query_one("#tf-br-files", OptionList)
                self.assertEqual([files.get_option_at_index(i).id for i in range(files.option_count)],
                                 [str(self.pics / "more/c.png")], "its pictures on the right")
                long = self.pics / "more" / ("a-very-long-name-" * 5 + ".png")
                long.write_bytes((self.pics / "more/c.png").read_bytes())
                app.screen.show_files(tree.cursor_node)
                shown = str(files.get_option_at_index(0).prompt).split("[/] ", 1)[-1]      # after the mark
                self.assertLess(len(shown), 56, f"a long name stays one line: {shown!r}")
                self.assertIn("…", shown)
                self.assertEqual(files.get_option_at_index(0).id, str(long), "but it is still the whole file")
                await pilot.press("left")
                await pilot.pause()
                self.assertEqual(tree.cursor_node.data, str(self.pics), "← goes to the folder above")
                self.assertEqual(files.option_count, 2, "a.jpg and b.png")
                names = [str(c.label) for c in tree.cursor_node.children]
                self.assertEqual(names, ["more", "new"] if (self.pics / "new").is_dir() else ["more"], "hidden folders aren't shown")
                await pilot.press("u")
                await pilot.pause()
                self.assertNotIsInstance(app.screen, FolderPicker, "Use This Folder closes it")
                self.assertEqual(app.query_one("#sec-wallpaper").source, str(self.pics))
                self.assertEqual([Path(v).name for v in self.images(app)], ["a.jpg", "b.png"], "pictures only, by name")
                self.assertEqual(app.query_one("#sec-wallpaper").pick, str(self.pics / "a.jpg"),
                                 "the first picture shows by itself (Javier, 10-13)")
                self.assertFalse(app.query_one("#tf-wp-apply").disabled)
        run(go())

    def test_a_picture_picked_in_browse_is_the_pick_and_the_theme_s_pictures_are_a_root(self):
        from themeforge.browse import THEME_MADE, FolderPicker, FolderTree
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(120, 40)) as pilot:
                await self.open_page(pilot, app)
                app.query_one("#sec-wallpaper").use_source(str(self.pics))
                await pilot.pause()
                await pilot.press("b")
                await pilot.pause()
                await pilot.press("tab")                     # to the pictures
                await pilot.press("down")                    # b.png
                await pilot.press("enter")
                await pilot.pause()
                self.assertNotIsInstance(app.screen, FolderPicker)
                self.assertEqual(app.query_one("#sec-wallpaper").pick, str(self.pics / "b.png"), "Enter on a picture picks it")
                self.assertFalse(app.query_one("#tf-wp-apply").disabled)
                app.query_one("#tf-wp-apply").press()
                await app.workers.wait_for_complete()
                await pilot.pause()
                self.assertEqual(self.look.done[0][3], {"picture": str(self.pics / "b.png"), "fit": "fill",
                                                        "folder": str(self.pics)}, "the folder is remembered")
                await pilot.press("b")
                await pilot.pause()
                tree = app.screen.query_one("#tf-br-tree", FolderTree)
                tree.move_cursor(tree.root.children[0])
                await pilot.pause()
                files = app.screen.query_one("#tf-br-files", OptionList)
                self.assertEqual([files.get_option_at_index(i).id for i in range(files.option_count)],
                                 ["theme", "kognogos:tier-aware", "kognogos:arch-distro", "solid"], "the theme's pictures")
                await pilot.press("enter")                    # nothing to open there: Enter takes it
                await pilot.pause()
                self.assertEqual(app.query_one("#sec-wallpaper").source, THEME_MADE)
                self.assertEqual(self.images(app)[0], "theme")
        run(go())

    def test_a_folder_that_is_not_there_yet_can_be_made(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(120, 40)) as pilot:
                await self.open_page(pilot, app)
                new = self.pics / "new"
                app.query_one("#sec-wallpaper").use_source(str(new))
                await pilot.pause()
                self.assertTrue(app.query_one("#tf-wp-mkdir").display, "offer to make the missing folder")
                self.assertIn("doesn't exist", str(app.query_one("#tf-wp-source-about").render()))
                await pilot.press("n")
                await pilot.pause()
                self.assertTrue(new.is_dir(), "n made it")
                self.assertFalse(app.query_one("#tf-wp-mkdir").display)
                self.assertIn("0 pictures here", str(app.query_one("#tf-wp-source-about").render()))
        run(go())

    def test_the_theme_s_own_follows_the_theme_picked(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause()
                label = lambda: str(app.query_one("#tf-wp-images", OptionList).get_option_at_index(0).prompt)
                self.assertIn("rice picture", label())
                app.query_one("#tf-style", Select).value = "classic"
                await pilot.pause()
                self.assertIn("classic picture", label(), "the Theme page's pick, not the one in use")
                self.assertEqual(app.query_one("#sec-wallpaper").pick, "theme", "the pick is kept")
        run(go())

    def test_the_changes_bar_names_the_theme_and_the_wallpaper_together(self):
        app = ThemeForgeApp(self.look)

        async def go():
            async with app.run_test(size=(120, 40)) as pilot:
                await self.open_page(pilot, app)
                self.pick(app, "solid")
                await pilot.pause()
                self.assertFalse(app.changes_bar.display)
                app.query_one("#tf-colour", Select).value = "white"
                await pilot.pause()
                self.assertTrue(app.changes_bar.display)
                self.assertIn("and the wallpaper", app.changes_bar.query_one("#forge-changes-msg").render().plain)
                await pilot.press("f10")
                await app.workers.wait_for_complete()
                self.assertEqual(self.look.done[0][:3], ("apply", "rice", "white"))
                self.assertEqual(self.look.done[0][3]["picture"], "solid")
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
                self.assertIn("Fill the Screen", str(app.query_one("#tf-wp-caption").render()))
        run(go())


if __name__ == "__main__":
    unittest.main()
