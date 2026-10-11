"""A picture in the terminal (Javier, 2026-10-11: "Can we show in terminal a small preview of the images?
… not super quality, but that doesn't matter").

Every terminal can draw "▀": the top half of a character in one colour and the bottom half in another.
So each character is two pixels, one above the other, and a picture becomes rows of them. No extra
program, any terminal with colours (a plain text console shows it in its few colours).

The picture is first laid on a screen-shaped canvas the way Sway will lay it (fill, fit, stretch,
center, tile), so the preview shows what the screen will.
"""

from __future__ import annotations

from pathlib import Path

from rich.style import Style
from rich.text import Text

SCREEN = (2560, 1440)


def on_screen(picture, fit: str, bg: tuple[int, int, int], screen=SCREEN):
    """The picture as one screen shows it, as a Pillow image the size of the screen (scaled down)."""
    from PIL import Image, ImageOps
    sw, sh = screen
    scale = 320 / sw                                   # work small: a preview needs few pixels
    w, h = max(1, round(sw * scale)), max(1, round(sh * scale))
    im = picture.convert("RGB")
    canvas = Image.new("RGB", (w, h), bg)
    if fit == "fill":
        return ImageOps.fit(im, (w, h), Image.BILINEAR)
    if fit == "stretch":
        return im.resize((w, h), Image.BILINEAR)
    if fit == "fit":
        small = ImageOps.contain(im, (w, h), Image.BILINEAR)
        canvas.paste(small, ((w - small.width) // 2, (h - small.height) // 2))
        return canvas
    real = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.BILINEAR)
    if fit == "center":
        canvas.paste(real, ((w - real.width) // 2, (h - real.height) // 2))
        return canvas
    if fit == "tile":
        for y in range(0, h, real.height):
            for x in range(0, w, real.width):
                canvas.paste(real, (x, y))
        return canvas
    raise ValueError(f"no fit called {fit}")


def blocks(image, cols: int, rows: int) -> Text:
    """An image as `rows` lines of `cols` half blocks (two pixels each, one above the other)."""
    from PIL import Image
    small = image.convert("RGB").resize((cols, rows * 2), Image.LANCZOS)
    px = small.load()
    out = Text()
    for r in range(rows):
        for c in range(cols):
            top, bottom = px[c, 2 * r], px[c, 2 * r + 1]
            out.append("▀", Style(color="#%02x%02x%02x" % top, bgcolor="#%02x%02x%02x" % bottom))
        if r < rows - 1:
            out.append("\n")
    return out


def preview(path: Path | str, fit: str, bg: tuple[int, int, int], cols: int = 56, rows: int = 16,
            screen=SCREEN) -> Text:
    from PIL import Image
    with Image.open(path) as im:
        return blocks(on_screen(im, fit, bg, screen), cols, rows)
