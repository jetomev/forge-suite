#!/usr/bin/env python3
"""One look for a bar's status pieces, written into a style's stylesheet (2026-10-17, Javier: "inSync and
dropbox look very close, and all others seem like have different distances"; then, for the other styles:
"the icons look terrible. Some are over the others, they aren't consistent with icon size, separation,
colors").

Every icon in a font has its own empty room left and right of what it draws (most Nerd Font icons draw
PAST their right edge), so the same padding on every piece looks uneven. This asks Pango — the text engine
Waybar draws with — how much room each piece's text leaves on each side, and writes, between the
stylesheet's `bar-spacing` marks:

  - every status piece in one font, one icon size and the style's icon colour (its states — warm, muted,
    new… — keep their own colours: their rules name a class, so they win)
  - each piece's padding, so the drawn parts end up exactly `gap` pixels apart
  - the system pieces' warm and hot colours, the disk piece lit while a USB drive is mounted
  - the tray's own icons `tray_gap` apart (pictures the tray trims; their size is the bar's, `tray_size`)

    bar-spacing.py --style rice            (one style, from its style.toml [bar])
    bar-spacing.py --all                   (every style that has a [bar] table)
    bar-spacing.py --style kde --print     (show, don't write)

The pieces and their sample text are below; the numbers inside a piece change, its first and last
characters don't (an icon, then % or °). Check the result with scripts/bar-gaps.py on a bar picture.
"""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path

import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
import cairo  # noqa: E402
from gi.repository import Pango, PangoCairo  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
FIG = " "
PIECES = [  # (CSS selector, what it shows) — every status piece a style may place
    ("#custom-nightlight", "\U000f0594"), ("#custom-disk", f" 48%"), ("#memory", f"\U000f061a 14%"),
    ("#custom-temperature", "\U000f050f 54°"), ("#custom-gpu", f"\U000f08ae {FIG}4%"), ("#cpu", f"\U000f035b {FIG}3%"),
    ("#custom-clipboard", "\U000f0147"), ("#custom-drives", "\U000f0553"), ("#custom-printers", "\U000f042a"),
    ("#bluetooth", "\U000f00af"), ("#network", "\U000f0200"), ("#wireplumber", "\U000f057e"),
    ("#custom-power-panel", "\U000f0425"),
]
SYSTEM = ("#cpu", "#memory", "#custom-disk", "#custom-gpu", "#custom-temperature")
START, END = "/* bar-spacing:start", "/* bar-spacing:end */"


def sides(text: str, font: str, size: float) -> tuple[int, int]:
    """(left, right): the empty pixels between the text's box and what it draws (negative: it draws past it)."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 10)
    layout = PangoCairo.create_layout(cairo.Context(surface))
    desc = Pango.FontDescription.from_string(f"{font}, Symbols Nerd Font")
    desc.set_absolute_size(size * Pango.SCALE)
    layout.set_font_description(desc)
    layout.set_text(text, -1)
    ink, logical = layout.get_pixel_extents()
    return ink.x - logical.x, (logical.x + logical.width) - (ink.x + ink.width)


def stylesheet(slug: str) -> Path:
    return HERE / ("sway/waybar/style.css" if slug == "classic" else f"styles/{slug}/bar/style.css")


def settings(slug: str) -> dict:
    return tomllib.loads((HERE / f"styles/{slug}/style.toml").read_text()).get("bar", {})


def block(slug: str) -> list[str]:
    b = settings(slug)
    font, size, gap = b["font"], int(b["icon_size"]), int(b.get("gap", 10))
    tray_gap, edge, colour = int(b.get("tray_gap", gap)), int(b.get("edge", 0)), b["icon_colour"]
    half_l, half_r = gap // 2, gap - gap // 2
    names = ", ".join(sel for sel, _ in PIECES)
    out = [f"{START} — written by scripts/bar-spacing.py --style {slug} from its style.toml [bar]: one font, "
           f"{size} px icons, the drawn parts {gap} px apart (2026-10-17) */",
           f'{names} {{ font-family: "{font}", "Symbols Nerd Font", sans-serif; font-size: {size}px; color: {colour}; }}',
           # the gap is ours alone: no side margins on the pieces, no side padding on the status pill (COSMIC's
           # 10 px pill and 1 px margins doubled the printer → Bluetooth gap, 10-17); top and bottom stay
           f"{names} {{ margin-left: 0; margin-right: 0; }}",
           "#quick { padding-left: 0; padding-right: 0; margin-left: 0; margin-right: 0; }",
           f"#tray {{ padding-left: {edge or half_l}px; padding-right: {half_r}px; }}",
           # each tray picture is the only child of its piece (:first-child matches them all), and an empty
           # piece hides its picture: a margin on the picture, pieces 2-10 (bench, 10-17)
           ", ".join(f"#tray .tray-{n} image" for n in range(2, 11)) + f" {{ margin-left: {tray_gap}px; }}"]
    for sel, text in PIECES:
        left, right = sides(text, font, size)
        r = edge if (edge and sel == "#custom-power-panel") else max(half_r - right, 0)
        out.append(f"{sel} {{ padding-left: {max(half_l - left, 0)}px; padding-right: {r}px; }}")
    out += [", ".join(f"{s}.warning" for s in SYSTEM) + " { color: @hf_bell; }",
            ", ".join(f"{s}.critical" for s in SYSTEM) + " { color: @hf_alert; }",
            "#custom-disk.has { color: @hf_new; }",
            END]
    return out


def write(slug: str) -> Path:
    sheet = stylesheet(slug)
    text = sheet.read_text()
    rules = "\n".join(block(slug))
    if START in text:
        text = text[:text.index(START)] + rules + text[text.index(END) + len(END):]
    else:
        text = text.rstrip("\n") + "\n\n" + rules + "\n"
    sheet.write_text(text)
    return sheet


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--style")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--print", action="store_true")
    a = ap.parse_args()
    slugs = sorted(p.parent.name for p in (HERE / "styles").glob("*/style.toml") if settings(p.parent.name)) \
        if a.all else [a.style]
    for slug in slugs:
        if a.print:
            print("\n".join(block(slug)))
        else:
            print(f"{write(slug).relative_to(HERE)}: {len(block(slug)) - 2} rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
