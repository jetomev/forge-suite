"""Tray icons in the theme's colour (Javier, 2026-10-17: "most icons are yellow, because of the theme, with
the exception of night-light, dropbox, and inSync"). Every other piece on the bar is a Symbols Nerd Font
glyph drawn in the theme's icon colour (`@hf_icon`); a tray app sends a picture of its own, usually white.

So the tray repaints the pictures that are one colour — white, grey or black, the panel icons most apps
send — in the theme's icon colour, keeping their shape and shading. A picture in full colour (a logo in
its own colours) is left as it is, so it can still be told apart.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

SIZE = 40              # drawn at twice the bar's 20 px: sharp, and Waybar scales it down
GREY = 0.22            # a pixel this far from grey is "coloured"
COLOURED = 0.12        # a picture with this share of coloured pixels keeps its own colours


def colors_css() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "hypeforge/theme/colors.css"


def theme_colour(path: Path | None = None) -> str | None:
    """The tray's icon colour from the look's colors.css (`hf_tray_icon`: the style's own icon colour; older
    files have only `hf_icon`)."""
    try:
        text = (path or colors_css()).read_text()
    except OSError:
        return None
    for name in ("hf_tray_icon", "hf_icon"):
        m = re.search(rf"@define-color\s+{name}\s+(#[0-9a-fA-F]{{6}})\s*;", text)
        if m:
            return m.group(1).lower()
    return None


def load(path: str):
    """The picture as a PIL image, SVG included (through GdkPixbuf, already on the system)."""
    from PIL import Image
    if path.endswith(".svg"):
        import gi
        gi.require_version("GdkPixbuf", "2.0")
        from gi.repository import GdkPixbuf
        pb = GdkPixbuf.Pixbuf.new_from_file_at_size(path, SIZE, SIZE)
        if not pb.get_has_alpha():
            pb = pb.add_alpha(False, 0, 0, 0)
        img = Image.frombytes("RGBA", (pb.get_width(), pb.get_height()), pb.get_pixels(), "raw", "RGBA",
                              pb.get_rowstride())
    else:
        img = Image.open(path).convert("RGBA")
    if img.size != (SIZE, SIZE):
        img.thumbnail((SIZE, SIZE), Image.LANCZOS)
    return img


def pixels(img) -> list:
    """Every pixel's (r, g, b, a) (Pillow 12 renamed getdata; both work)."""
    return list(img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata())


def one_colour(img) -> bool:
    """Is the picture white / grey / black (shading allowed), or does it carry colours of its own?"""
    seen = coloured = 0
    for r, g, b, a in pixels(img):
        if a < 60:
            continue
        seen += 1
        if (max(r, g, b) - min(r, g, b)) / 255 > GREY:
            coloured += 1
    return seen > 0 and coloured / seen < COLOURED


def tinted(img, colour: str):
    """The same shape in the theme's colour: a light picture's light parts (or a dark one's dark parts) carry
    the colour, its shading kept as see-through."""
    from PIL import Image
    tr, tg, tb = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
    px = pixels(img)
    lums = [(0.299 * r + 0.587 * g + 0.114 * b) / 255 for r, g, b, a in px]
    solid = [l for l, (_r, _g, _b, a) in zip(lums, px) if a >= 60]
    light = (sum(solid) / len(solid) if solid else 1.0) >= 0.5
    shade = [l if light else 1 - l for l in lums]
    top = max((s for s, (*_c, a) in zip(shade, px) if a >= 60), default=1.0) or 1.0
    out = Image.new("RGBA", img.size)
    out.putdata([(tr, tg, tb, round(a * min(s / top, 1.0))) for s, (_r, _g, _b, a) in zip(shade, px)])
    return out


def themed(path: str, colour: str | None, folder: Path, n: int) -> str:
    """The picture to show for tray slot n: the repainted copy, or the app's own when it is in colour (or
    nothing could be read). The copy's name carries what it was made from, so a new theme or a new icon
    gives a new file — the bar then loads it fresh."""
    if not colour or not path:
        return path
    try:
        stamp = f"{path}:{os.path.getmtime(path)}:{colour}"
    except OSError:
        return path
    out = folder / f"slot-{n}-{hashlib.sha1(stamp.encode()).hexdigest()[:10]}.png"
    if out.is_file():
        return str(out)
    try:
        img = load(path)
        if not one_colour(img):
            return path
        folder.mkdir(parents=True, exist_ok=True)
        tinted(img, colour).save(out)
    except Exception:          # an odd picture: the app's own, never a missing icon
        return path
    return str(out)


def tidy(folder: Path, keep: set[str]):
    """Repainted copies no slot shows any more."""
    for f in folder.glob("slot-*-*.png"):
        if str(f) not in keep:
            f.unlink(missing_ok=True)
