"""Tray icons in the style's own icon colour (Javier, 2026-10-17: "most icons are yellow, because of the
theme, with the exception of night-light, dropbox, and inSync"), and the restart with no gap."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "applets/tray"))
import hftint  # noqa: E402


def theme_tool():
    loader = importlib.machinery.SourceFileLoader("ht_tray", str(REPO / "applets/theme/hypeforge-theme"))
    spec = importlib.util.spec_from_loader("ht_tray", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def picture(colour, size=40, shape=True) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for x in range(8, 32):
        for y in range(8, 32):
            img.putpixel((x, y), (*colour, 255))
    return img


class Repaint(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def save(self, img, name):
        p = self.dir / name
        img.save(p)
        return str(p)

    def test_white_grey_and_black_pictures_are_one_colour_a_logo_is_not(self):
        self.assertTrue(hftint.one_colour(picture((255, 255, 255))))
        self.assertTrue(hftint.one_colour(picture((120, 120, 120))))
        self.assertTrue(hftint.one_colour(picture((10, 10, 10))))
        self.assertFalse(hftint.one_colour(picture((0, 97, 254))), "Dropbox blue is a colour of its own")

    def test_a_white_picture_takes_the_colour_and_keeps_its_shape(self):
        out = hftint.tinted(picture((255, 255, 255)), "#ffae33")
        self.assertEqual(out.getpixel((20, 20)), (0xff, 0xae, 0x33, 255))
        self.assertEqual(out.getpixel((2, 2))[3], 0, "outside the shape stays see-through")

    def test_a_black_picture_too(self):
        out = hftint.tinted(picture((0, 0, 0)), "#89b4fa")
        self.assertEqual(out.getpixel((20, 20)), (0x89, 0xb4, 0xfa, 255))

    def test_a_coloured_picture_is_shown_as_the_app_sent_it(self):
        own = self.save(picture((0, 97, 254)), "logo.png")
        self.assertEqual(hftint.themed(own, "#ffae33", self.dir, 1), own)

    def test_a_new_theme_gives_a_new_file_so_the_bar_loads_it(self):
        own = self.save(picture((255, 255, 255)), "white.png")
        a = hftint.themed(own, "#ffae33", self.dir, 1)
        b = hftint.themed(own, "#89b4fa", self.dir, 1)
        self.assertNotEqual(a, b)
        self.assertNotEqual(a, own)
        hftint.tidy(self.dir, {b})
        self.assertFalse(Path(a).exists(), "the old theme's copy is cleared away")
        self.assertTrue(Path(b).exists())

    def test_no_theme_colour_leaves_the_picture_alone(self):
        own = self.save(picture((255, 255, 255)), "white.png")
        self.assertEqual(hftint.themed(own, None, self.dir, 1), own)

    def test_the_colour_is_read_from_the_looks_file(self):
        css = self.dir / "colors.css"
        css.write_text("@define-color hf_icon          #ffae33;\n@define-color hf_tray_icon     #d4d8dd;\n")
        self.assertEqual(hftint.theme_colour(css), "#d4d8dd")
        css.write_text("@define-color hf_icon #FFAE33;\n")          # a look written before 10-17
        self.assertEqual(hftint.theme_colour(css), "#ffae33")


class EachStyle(unittest.TestCase):
    def test_every_style_paints_the_tray_like_its_other_icons(self):
        """The Rice's icons are the theme's icon colour, the Macs' the menu bar's text, Classic's its dim
        text, the others the bar's text: the tray matches each, on every theme."""
        ht = theme_tool()
        same_as = {"rice": "module_icon", "macos": "menubar_text", "mac-os-9": "menubar_text", "classic": "bar_fg_dim"}
        for theme_slug, theme in list(ht.themes().items())[:6]:
            for slug, style in ht.styles().items():
                self.assertEqual(ht.resolve("tray_icon", style, theme),
                                 ht.resolve(same_as.get(slug, "bar_fg"), style, theme), f"{slug} on {theme_slug}")

    def test_a_role_naming_itself_is_refused(self):
        ht = theme_tool()
        style = {"roles": {"tray_icon": "role:tray_icon"}}
        with self.assertRaises(ht.LookError):
            ht.resolve("tray_icon", style, next(iter(ht.themes().values())))

    def test_no_style_greys_the_moon_by_day(self):
        """Javier, 10-17: by day the moon wears the other icons' colour (only warm and off have their own)."""
        for css in list((REPO / "styles").glob("*/bar/style.css")) + [REPO / "sway/waybar/style.css"]:
            self.assertNotIn("#custom-nightlight.day", css.read_text(), css.parent.parent.name)


if __name__ == "__main__":
    unittest.main()
