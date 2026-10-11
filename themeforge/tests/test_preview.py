"""The terminal preview: the picture laid on a screen-shaped canvas as Sway would, drawn in half blocks."""

from __future__ import annotations

import unittest

from PIL import Image

from themeforge.preview import blocks, on_screen

RED, BG = (220, 20, 20), (0, 0, 255)


class OnScreen(unittest.TestCase):
    def test_fill_covers_the_screen(self):
        im = on_screen(Image.new("RGB", (100, 100), RED), "fill", BG)
        self.assertEqual(im.getpixel((0, 0)), RED)
        self.assertEqual(im.size, (320, 180), "the screen's shape")

    def test_fit_shows_the_theme_colour_around_a_square(self):
        im = on_screen(Image.new("RGB", (100, 100), RED), "fit", BG)
        self.assertEqual(im.getpixel((5, 90)), BG, "bars at the sides")
        self.assertEqual(im.getpixel((160, 90)), RED)

    def test_center_keeps_the_real_size(self):
        im = on_screen(Image.new("RGB", (640, 360), RED), "center", BG)    # a quarter of a 2560 screen
        self.assertEqual(im.getpixel((160, 90)), RED)
        self.assertEqual(im.getpixel((10, 10)), BG)

    def test_tile_repeats(self):
        pic = Image.new("RGB", (256, 144), BG)
        pic.putpixel((0, 0), RED)
        im = on_screen(pic.resize((256, 144)), "tile", (0, 0, 0))
        self.assertEqual(im.size, (320, 180))

    def test_stretch_and_a_wrong_fit(self):
        self.assertEqual(on_screen(Image.new("RGB", (10, 300), RED), "stretch", BG).getpixel((300, 10)), RED)
        with self.assertRaises(ValueError):
            on_screen(Image.new("RGB", (10, 10)), "sideways", BG)


class Blocks(unittest.TestCase):
    def test_two_pixels_a_character(self):
        im = Image.new("RGB", (4, 4), RED)
        im.putpixel((0, 1), BG)
        t = blocks(im, 4, 2)
        self.assertEqual(t.plain, "▀▀▀▀\n▀▀▀▀")
        first = t.spans[0].style
        self.assertEqual(first.color.triplet.hex, "#dc1414")
        self.assertEqual(first.bgcolor.triplet.hex, "#0000ff", "the lower pixel is the background colour")


if __name__ == "__main__":
    unittest.main()
