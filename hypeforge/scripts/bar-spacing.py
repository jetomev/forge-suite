#!/usr/bin/env python3
"""The paddings that space a bar's pieces evenly (2026-10-17, Javier: "inSync and dropbox look very close,
and all others seem like have different distances"). Every icon in a font has its own empty margin left and
right of what it draws, so the same padding on every piece looks uneven. This asks Pango — the text engine
Waybar draws with — how much empty room each piece's text has on each side, and prints each piece's padding
so the drawn parts end up exactly GAP pixels apart.

    bar-spacing.py --gap 5 [--font "JetBrainsMono Nerd Font"] [--size 14] [--write STYLESHEET]

--write puts the paddings into the stylesheet between its `bar-spacing` marks (the Rice's bar), with the
tray's own icons --tray-gap apart (pictures the tray trims: no empty sides).

The pieces and their sample text (the Rice's right island, left to right) are below; the numbers inside a
piece change, its first and last characters don't (an icon, then % or °).
"""

import argparse

import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
import cairo  # noqa: E402
from gi.repository import Pango, PangoCairo  # noqa: E402

PIECES = [  # (CSS selector, what it shows)
    ("#custom-nightlight", "\U000f0594"), ("#disk", " 48%"), ("#memory", "\U000f061a 14%"),
    ("#custom-temperature", "\U000f050f 54°"), ("#custom-gpu", "\U000f08ae 4%"), ("#cpu", "\U000f035b 3%"),
    ("#custom-clipboard", "\U000f0147"), ("#custom-printers", "\U000f042a"), ("#custom-drives", "\U000f0553"),
    ("#bluetooth", "\U000f00af"), ("#network", "\U000f0200"), ("#wireplumber", "\U000f057e"),
    ("#custom-power-panel", "\U000f0425"),
]


def sides(text: str, font: str, size: float) -> tuple[int, int]:
    """(left, right): the empty pixels between the text's box and what it draws (negative: it draws past it)."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 10)
    layout = PangoCairo.create_layout(cairo.Context(surface))
    desc = Pango.FontDescription.from_string(font)
    desc.set_absolute_size(size * Pango.SCALE)
    layout.set_font_description(desc)
    layout.set_text(text, -1)
    ink, logical = layout.get_pixel_extents()
    return ink.x - logical.x, (logical.x + logical.width) - (ink.x + ink.width)


def paddings(gap: int, font: str, size: float) -> list[tuple[str, int, int]]:
    half_l, half_r = gap // 2, gap - gap // 2
    out = []
    for sel, text in PIECES:
        left, right = sides(text, font, size)
        out.append((sel, max(half_l - left, 0), max(half_r - right, 0)))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", type=int, default=5)
    ap.add_argument("--font", default="JetBrainsMono Nerd Font")
    ap.add_argument("--size", type=float, default=14)
    ap.add_argument("--tray-gap", type=int, default=10)
    ap.add_argument("--edge", type=int, default=12, help="room at the island's two ends")
    ap.add_argument("--write")
    a = ap.parse_args()
    if a.write:
        from pathlib import Path
        sheet = Path(a.write)
        text = sheet.read_text()
        start, end = "/* bar-spacing:start", "/* bar-spacing:end */"
        rows = paddings(a.gap, a.font, a.size)
        last = rows[-1][0]
        block = [f"{start} — written by scripts/bar-spacing.py --gap {a.gap} --tray-gap {a.tray_gap}: the drawn parts "
                 f"{a.gap} px apart, whatever room each icon leaves (2026-10-17) */"]
        block.append(f"#tray {{ padding-left: {a.edge}px; padding-right: {a.gap - a.gap // 2}px; }}")
        # the room between the tray's own icons: a margin on the picture inside each piece but the first —
        # an empty piece hides its picture, so it takes no room (a margin on the piece itself still counted
        # on the empty ones: 46 px of nothing beside Dropbox), and :first-child can't be used (each picture
        # is the only child of its own piece). Tried on the bench, 10-17.
        block.append(", ".join(f"#tray .tray-{n} image" for n in range(2, 11)) + f" {{ margin-left: {a.tray_gap}px; }}")
        for sel, l, r in rows:
            block.append(f"{sel} {{ padding-left: {l}px; padding-right: {a.edge if sel == last else r}px; }}")
        block.append(end)
        if start in text:
            text = text[:text.index(start)] + "\n".join(block) + text[text.index(end) + len(end):]
        else:
            text = text.rstrip("\n") + "\n\n" + "\n".join(block) + "\n"
        sheet.write_text(text)
        print(f"{sheet}: {len(rows) + 3} rules")
        raise SystemExit(0)
    for sel, text in PIECES:
        print(f"/* {sel}: empty sides {sides(text, a.font, a.size)} */")
    for sel, l, r in paddings(a.gap, a.font, a.size):
        print(f"{sel} {{ padding-left: {l}px; padding-right: {r}px; }}")
