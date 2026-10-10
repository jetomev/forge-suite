#!/usr/bin/env python3
"""
hypeForge palette generator v2 — the 25 colour themes of the look program (2026-10).

What it does, in plain words:
  1. Every theme is built the 60-30-10 way (interior design's rule, used in UI design):
       60 % FOUNDATION — windows, panels, pop-ups, the terminal: true grays, near-black or
                          off-white, with at most a whisper of the theme's hue;
       30 % BAND       — the theme colour at real strength on big secondary areas: the bar,
                          panel headers, side panels, the selected row, the focused border;
       10 % POP        — a HARMONY colour (complementary / split / analogous) for small
                          important things: typed letters, toggles that are on, badges, links.
     Javier, 2026-10-10: "More contrast … that way they aren't monotone and boring";
     "we can use white, black, and grays inside our color themes".
  2. Each theme is a short RECIPE (THEMES below): its tone, its band hue and strength, its pop.
     The recipe is turned into ~80 named colours ("tokens") in OKLCH, a colour space where
     "lightness" means what the eye sees. All the maths is here, standard library only.
  3. KognogOS Mocha is not generated: it is Catppuccin Mocha placed into our roles the way
     Catppuccin's own style guide places them. It is today's look and the default.
  4. Every pair of colours that must be readable together is measured with WCAG 2.2 and APCA.
     When a pair fails, the generator moves the lightness in small steps until it passes
     ("nudging") and writes down what it moved. Design checks (band vs foundation, pop vs
     band, colour share) are reported next to the contrast results.
  5. It writes: palettes.toml (all 25), themes/<slug>/theme.toml, contrast-report.md,
     swatches.html, and render/<slug>/ example files for each program.

Run:     python3 generate.py            (writes everything next to this file)
         python3 generate.py --check    (also exits 1 if any required pair fails)
         python3 generate.py --render kognogos-mocha ember   (which themes get example files)

Credits (thank you): OKLab/OKLCH by Björn Ottosson (2020); WCAG 2.2 by the W3C; APCA-W3
0.0.98G-4g by Andrew Somers / Myndex; Catppuccin (catppuccin.com: palette v1.8.0 and its
style guide) for KognogOS Mocha.

SPDX-FileCopyrightText: 2026 Javier
SPDX-License-Identifier: GPL-3.0-or-later
"""

from __future__ import annotations

import argparse
import html
import math
import pathlib
import sys
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
SCHEMA_VERSION = 2

# ════════════════════════════════════════════════════════════════════════════════════════
# 1 · Colour maths (sRGB ⇄ OKLab ⇄ OKLCH, WCAG, APCA, gamut mapping)
# ════════════════════════════════════════════════════════════════════════════════════════


def _to_linear(c: float) -> float:
    """One sRGB channel (0..1) to linear light."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _to_srgb(c: float) -> float:
    """One linear channel to sRGB (0..1)."""
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def _cbrt(x: float) -> float:
    return math.copysign(abs(x) ** (1 / 3), x)


def hex_to_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def rgb_to_hex(rgb) -> str:
    return "#" + "".join(f"{round(min(1, max(0, c)) * 255):02x}" for c in rgb)


def rgb_to_oklab(rgb):
    r, g, b = (_to_linear(c) for c in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = _cbrt(l), _cbrt(m), _cbrt(s)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def oklab_to_linear(lab):
    L, a, b = lab
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def lch_to_lab(L, C, h):
    return (L, C * math.cos(math.radians(h)), C * math.sin(math.radians(h)))


def hex_to_lch(hx: str) -> tuple[float, float, float]:
    L, a, b = rgb_to_oklab(hex_to_rgb(hx))
    C = math.hypot(a, b)
    h = math.degrees(math.atan2(b, a)) % 360
    return (L, C, h)


def _in_gamut(lin, eps=1e-6) -> bool:
    return all(-eps <= c <= 1 + eps for c in lin)


def lch_to_hex(L: float, C: float, h: float) -> str:
    """OKLCH → #rrggbb. Out-of-screen colours keep their lightness and hue and lose chroma
    (a binary search, the CSS Color 4 idea without the ΔE refinement)."""
    L = min(1.0, max(0.0, L))
    lin = oklab_to_linear(lch_to_lab(L, C, h))
    if not _in_gamut(lin):
        lo, hi = 0.0, C
        for _ in range(30):
            mid = (lo + hi) / 2
            if _in_gamut(oklab_to_linear(lch_to_lab(L, mid, h))):
                lo = mid
            else:
                hi = mid
        lin = oklab_to_linear(lch_to_lab(L, lo, h))
    return rgb_to_hex(_to_srgb(min(1, max(0, c))) for c in lin)


def luminance(hx: str) -> float:
    """WCAG relative luminance."""
    r, g, b = (_to_linear(c) for c in hex_to_rgb(hx))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def wcag(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def apca(text: str, bg: str) -> float:
    """APCA Lc (APCA-W3 0.0.98G-4g). Positive = dark text on light, negative = light on dark.
    We use the size |Lc|."""
    def y(hx):
        r, g, b = hex_to_rgb(hx)
        v = 0.2126729 * r ** 2.4 + 0.7151522 * g ** 2.4 + 0.0721750 * b ** 2.4
        return v + (0.022 - v) ** 1.414 if v < 0.022 else v
    yt, yb = y(text), y(bg)
    if abs(yb - yt) < 0.0005:
        return 0.0
    if yb > yt:
        s = (yb ** 0.56 - yt ** 0.57) * 1.14
        return 0.0 if s < 0.1 else (s - 0.027) * 100
    s = (yb ** 0.65 - yt ** 0.62) * 1.14
    return 0.0 if s > -0.1 else (s + 0.027) * 100


def delta_e_ok(a: str, b: str) -> float:
    """Distance between two colours in OKLab (0.02 ≈ just noticeable, 0.1 = clearly different)."""
    la, lb = rgb_to_oklab(hex_to_rgb(a)), rgb_to_oklab(hex_to_rgb(b))
    return math.dist(la, lb)



# ════════════════════════════════════════════════════════════════════════════════════════
# 2 · The brand, Catppuccin Mocha, and the recipes
# ════════════════════════════════════════════════════════════════════════════════════════

# Sampled from assets/kognogos-emblem.png (k-means over the solid pixels, 2026-10-10) and
# kognog/config/os-release (ANSI_COLOR="38;2;203;166;247"). Fixed: never nudged; for the logo
# and brand marks — except the emblem orange, which is also the Ember theme's band (Javier, Q-5).
BRAND = {
    "emblem_blue": "#0363ef",        # top layers, 35 % of the emblem
    "emblem_blue_deep": "#0048b6",   # their shaded side, 22 %
    "emblem_orange": "#d9400e",      # bottom layer, 28 %
    "emblem_orange_deep": "#b93205", # its shaded side, 14 %
    "wordmark_gray": "#969696",      # the "Kognog OS" letters in logo.png
    "kognog_mauve": "#cba6f7",       # the OS's own colour (os-release ANSI_COLOR, Plymouth ring)
}

# Catppuccin Mocha, palette.json v1.8.0 (github.com/catppuccin/palette), and its ANSI table.
MOCHA = {
    "rosewater": "#f5e0dc", "flamingo": "#f2cdcd", "pink": "#f5c2e7", "mauve": "#cba6f7",
    "red": "#f38ba8", "maroon": "#eba0ac", "peach": "#fab387", "yellow": "#f9e2af",
    "green": "#a6e3a1", "teal": "#94e2d5", "sky": "#89dceb", "sapphire": "#74c7ec",
    "blue": "#89b4fa", "lavender": "#b4befe", "text": "#cdd6f4", "subtext1": "#bac2de",
    "subtext0": "#a6adc8", "overlay2": "#9399b2", "overlay1": "#7f849c", "overlay0": "#6c7086",
    "surface2": "#585b70", "surface1": "#45475a", "surface0": "#313244", "base": "#1e1e2e",
    "mantle": "#181825", "crust": "#11111b",
    "shade": "#262637",   # NOT Catppuccin: hypeForge's own bar shade (docs/THEME.md), kept as today's look
}
MOCHA_ANSI_BRIGHT = {"red": "#f37799", "green": "#89d88b", "yellow": "#ebd391", "blue": "#74a8fc",
                     "magenta": "#f2aede", "cyan": "#6bd7ca"}

# FOUNDATION (60 %): OKLCH lightness of each neutral level, per tone.
#   white / black  — the high-contrast grayscale themes (hc=True)
#   light          — off-white
#   mid            — graphite ("middle to darker", Javier): base ≈ 0.30
#   dark           — charcoal / near-black: base ≈ 0.185
FOUND = {
    #          sunken  bar    base   raised overlay hover  polarity (which way text goes)
    "white": dict(sunken=.925, bar=.945, base=.958, raised=.980, overlay=1.0, hover=.895, polarity="light"),
    "light": dict(sunken=.925, bar=.940, base=.955, raised=.978, overlay=1.0, hover=.895, polarity="light"),
    "mid":   dict(sunken=.245, bar=.262, base=.300, raised=.330, overlay=.362, hover=.425, polarity="dark"),
    "dark":  dict(sunken=.150, bar=.165, base=.185, raised=.215, overlay=.250, hover=.320, polarity="dark"),
    "black": dict(sunken=.000, bar=.000, base=.105, raised=.175, overlay=.215, hover=.300, polarity="dark"),
}
FOUND_CHROMA_MAX = 0.012   # "a whisper of the theme hue at most"

# BAND (30 %): lightness of the band levels, per tone. base = the bar's segments, panel headers,
# the selected row · strong = the bar behind them, pressed band · soft = side panels, quiet
# selection (normal text on it) · text = the band colour as a line or words on the foundation
# (the focused window border, section titles).
BAND = {
    "white": dict(base=.850, strong=.730, soft=.915, text=.300),
    "light": dict(base=.550, strong=.270, soft=.925, text=.480),
    "mid":   dict(base=.470, strong=.380, soft=.375, text=.800),
    "dark":  dict(base=.360, strong=.290, soft=.250, text=.780),
    "black": dict(base=.270, strong=.220, soft=.215, text=.880),
}

# Multicolor's band: neutral and dark in every tone, so eight category colours can sit on it
MULTI_BAND = {"light": dict(base=.300, strong=.220), "mid": dict(base=.180, strong=.130),
              "dark": dict(base=.300, strong=.240)}

# Where text, pop and the rest start, by polarity (the nudging then makes them pass).
START = {
    "dark":  dict(primary=.880, secondary=.760, muted=.640, pop=.810, status=.800, cat=.780,
                  ansi=.760, ansi_bright=.850, subtle=.15, strong=.56, hover_step=+.05, press_step=-.06),
    "light": dict(primary=.240, secondary=.420, muted=.560, pop=.560, status=.520, cat=.580,
                  ansi=.480, ansi_bright=.400, subtle=-.13, strong=-.37, hover_step=-.05, press_step=-.10),
}

STATUS_HUES = {"success": 145, "warning": 85, "danger": 22, "info": 240}
CAT = [("red", 25), ("orange", 55), ("yellow", 95), ("green", 145),
       ("teal", 185), ("blue", 255), ("purple", 305), ("pink", 350)]
ANSI = [("red", 25), ("green", 145), ("yellow", 90), ("blue", 255), ("magenta", 330), ("cyan", 195)]

# Harmony picks for the POP (OKLCH hues; the reasoning is in 03b-colour-design.md):
POP = {
    "neutral": ("emblem blue", 260, .15),    # the logo's main colour on grays
    "blue":    ("amber", 72, .16),           # complementary (blue ↔ amber)
    "purple":  ("mint", 165, .13),           # near-complementary (violet ↔ green-mint)
    "green":   ("gold", 85, .15),            # analogous-warm (leaf + sun)
    "pink":    ("teal", 190, .12),           # complementary (pink ↔ teal)
    "red":     ("gold", 85, .15),            # analogous-warm, with charcoal + cream
    "orange":  ("cream", 85, .05),           # Ember: a warm off-white highlight
    "multi":   ("mauve", 305, .16),          # buttons; the rest rotates through CAT
    "hc":      ("gray", 0, 0.0),             # high contrast: no colour where it is not meaning
}

# The 25 themes, in the order the theme app lists them (KognogOS Mocha first: the default).
#   hue: the band's hue · band_c: its chroma (colourfulness) · band: a pinned hex instead
#   pop: a family from POP, or a pinned hex · on_tint: (hue, chroma) for text on the band
#   cursor: installed catppuccin-mocha-*-cursors · gnome: libadwaita's nearest named accent
THEMES = [
    dict(slug="kognogos-mocha",   name="KognogOS Mocha",   family="kognog",  tone="dark",  mocha=True, cursor="mauve", gnome="purple", default=True),
    # White and Black: the HIGH-CONTRAST grayscale themes (Javier, 2026-10-10), kept.
    dict(slug="white",            name="White",            family="neutral", tone="white", hue=262, band_c=0.0, pop="hc", pop_l=.25, bar_bg="foundation", cursor="dark",  gnome="slate", hc=True),
    dict(slug="light-gray",       name="Light Gray",       family="neutral", tone="light", hue=262, band_c=0.0, pop=BRAND["emblem_blue"], cursor="dark", gnome="blue", l_shift=-.05),
    dict(slug="gray",             name="Gray",             family="neutral", tone="mid",   hue=262, band_c=0.0, pop="neutral", cursor="dark",  gnome="blue"),
    dict(slug="dark-gray",        name="Dark Gray",        family="neutral", tone="dark",  hue=262, band_c=0.0, pop="neutral", cursor="dark",  gnome="blue"),
    dict(slug="black",            name="Black",            family="neutral", tone="black", hue=262, band_c=0.0, pop="hc", pop_l=.92, cursor="light", gnome="slate", hc=True),
    dict(slug="ember",            name="Ember",            family="orange",  tone="dark",  hue=36,  band=BRAND["emblem_orange"], pop="orange", bar_bg="foundation", cursor="peach", gnome="orange"),
    dict(slug="light-blue",       name="Light Blue",       family="blue",    tone="light", hue=258, band_c=.17, pop=("orange", 50, .18), cursor="blue", gnome="blue"),
    dict(slug="blue",             name="Blue",             family="blue",    tone="mid",   hue=258, band_c=.17, pop="blue",   cursor="blue",  gnome="blue"),
    dict(slug="dark-blue",        name="Dark Blue",        family="blue",    tone="dark",  hue=258, band_c=.15, pop="blue",   cursor="blue",  gnome="blue"),
    dict(slug="light-purple",     name="Light Purple",     family="purple",  tone="light", hue=302, band_c=.18, pop="purple", cursor="mauve", gnome="purple"),
    dict(slug="purple",           name="Purple",           family="purple",  tone="mid",   hue=302, band_c=.17, pop="purple", cursor="mauve", gnome="purple"),
    dict(slug="dark-purple",      name="Dark Purple",      family="purple",  tone="dark",  hue=302, band_c=.15, pop="purple", cursor="mauve", gnome="purple"),
    dict(slug="light-green",      name="Light Green",      family="green",   tone="light", hue=150, band_c=.14, pop=("raspberry", 355, .19), cursor="green", gnome="green"),
    dict(slug="green",            name="Green",            family="green",   tone="mid",   hue=150, band_c=.13, pop="green",  cursor="green", gnome="green"),
    dict(slug="dark-green",       name="Dark Green",       family="green",   tone="dark",  hue=150, band_c=.12, pop="green",  cursor="green", gnome="green"),
    dict(slug="light-pink",       name="Light Pink",       family="pink",    tone="light", hue=352, band_c=.17, pop="pink",   cursor="pink",  gnome="pink"),
    dict(slug="pink",             name="Pink",             family="pink",    tone="mid",   hue=352, band_c=.15, pop="pink",   cursor="pink",  gnome="pink"),
    dict(slug="dark-pink",        name="Dark Pink",        family="pink",    tone="dark",  hue=352, band_c=.13, pop="pink",   cursor="pink",  gnome="pink"),
    dict(slug="light-red",        name="Light Red",        family="red",     tone="light", hue=26,  band_c=.18, pop=("deep teal", 200, .12), on_tint=(85, .02), cursor="red", gnome="red"),
    dict(slug="red",              name="Red",              family="red",     tone="mid",   hue=26,  band_c=.16, pop="red",    pop_l=.88,    on_tint=(85, .02), cursor="red", gnome="red"),
    dict(slug="dark-red",         name="Dark Red",         family="red",     tone="dark",  hue=26,  band_c=.14, pop="red",    pop_l=.88,    on_tint=(85, .02), cursor="red", gnome="red"),
    dict(slug="light-multicolor", name="Light Multicolor", family="multi",   tone="light", hue=262, band_c=0.0, pop="multi",  multi=True, cursor="dark", gnome="purple"),
    dict(slug="multicolor",       name="Multicolor",       family="multi",   tone="mid",   hue=262, band_c=0.0, pop="multi",  multi=True, cursor="dark", gnome="purple"),
    dict(slug="dark-multicolor",  name="Dark Multicolor",  family="multi",   tone="dark",  hue=262, band_c=0.0, pop="multi",  multi=True, cursor="dark", gnome="purple"),
]

# Which role each part of the desktop wears (the doc's table is written from this).
WEARS = [
    ("The bar (behind)", "bar.bg", "band.strong (Ember: the near-black foundation)"),
    ("The bar's areas (emblem · workspaces · apps · clock)", "bar.shade", "band.base"),
    ("Text on the bar", "bar.fg / bar.fg_dim", "band.on"),
    ("The active workspace", "bar.active_bg / _fg", "band.on with band.strong numbers (an inverted chip); Multicolor: its own category colour"),
    ("The bell's dot, the clipboard's 'new' mark", "bar.pop", "pop (lifted to stand out on the band)"),
    ("Focused window border", "window.focused", "band.text"),
    ("Unfocused border", "window.unfocused", "border.subtle (neutral)"),
    ("Urgent border", "window.urgent", "status.danger (moved off red in red/pink themes)"),
    ("Panel header, title strip", "band.base / band.on", "band"),
    ("Side panel (Start's list of places, settings sidebar)", "band.soft", "band, quiet"),
    ("Selected row (lists, the launcher)", "selection.bg / fg", "band.base / band.on"),
    ("Window content, pop-up lists, notifications, terminal", "surface.* / term.bg", "foundation"),
    ("Buttons", "accent.base / accent.on", "pop"),
    ("Toggles that are on, sliders, progress", "accent.base", "pop"),
    ("Links, the letters you typed in a list", "accent.text", "pop"),
    ("Badges, counters", "pop.base / pop.on", "pop"),
    ("Keyboard focus ring", "accent.ring", "pop"),
]

# ════════════════════════════════════════════════════════════════════════════════════════
# 3 · The pairs that must pass (the contract) — (foreground, backgrounds, WCAG min, APCA |Lc| min)
# ════════════════════════════════════════════════════════════════════════════════════════
# Kinds: "text" = words people read; "ui" = icons, borders, focus marks (WCAG 1.4.11 / 2.4.13);
# "hint" = placeholder / disabled text (WCAG exempts it, we still keep it findable).
RULES = [
    ("text.primary",   ["surface.base", "surface.raised"], 7.0, 75, "text"),
    ("text.primary",   ["surface.overlay", "surface.sunken", "surface.hover", "band.soft"], 4.5, 60, "text"),
    ("text.secondary", ["surface.base", "surface.raised", "surface.overlay", "surface.sunken"], 4.5, 60, "text"),
    ("text.muted",     ["surface.base", "surface.raised"], 3.0, 45, "hint"),
    # band (30 %)
    ("band.on",        ["band.base"], 4.5, 60, "text"),
    ("band.on",        ["band.strong"], 7.0, 75, "text"),
    ("band.text",      ["surface.base", "surface.raised"], 4.5, 60, "text"),
    # pop (10 %) — accent.* is the pop
    ("pop.base",       ["surface.base", "surface.raised", "surface.overlay"], 3.0, 30, "ui"),
    ("pop.on",         ["pop.base"], 4.5, 60, "text"),
    ("pop.text",       ["surface.base", "surface.raised", "surface.overlay"], 4.5, 60, "text"),
    ("accent.on",      ["accent.hover", "accent.pressed"], 4.5, 60, "text"),
    ("accent.ring",    ["surface.base", "surface.raised"], 3.0, 30, "ui"),
    ("border.strong",  ["surface.base", "surface.raised"], 3.0, 30, "ui"),
    ("window.focused", ["surface.base", "window.unfocused"], 3.0, 30, "ui"),
    ("window.urgent",  ["surface.base"], 3.0, 30, "ui"),
    ("bar.fg",         ["bar.bg"], 7.0, 75, "text"),
    ("bar.fg",         ["bar.shade", "bar.hover"], 4.5, 60, "text"),
    ("bar.fg_dim",     ["bar.bg", "bar.shade"], 4.5, 60, "text"),
    ("bar.active_fg",  ["bar.active_bg"], 4.5, 60, "text"),
    ("bar.active_bg",  ["bar.bg", "bar.shade"], 3.0, 30, "ui"),
    ("bar.pop",        ["bar.bg", "bar.shade"], 3.0, 30, "ui"),
    ("selection.fg",   ["selection.bg"], 4.5, 60, "text"),
    *[(f"status.{s}", ["surface.base", "surface.raised"], 4.5, 60, "text") for s in STATUS_HUES],
    *[(f"status.on_{s}", [f"status.{s}"], 4.5, 60, "text") for s in STATUS_HUES],
    ("term.fg",        ["term.bg"], 7.0, 75, "text"),
    *[(f"term.{n}", ["term.bg"], 4.5, 60, "text") for n, _ in ANSI],
    *[(f"term.bright_{n}", ["term.bg"], 3.0, 45, "text") for n, _ in ANSI],
    *[(f"cat.{n}", ["surface.base", "bar.bg"], 3.0, 30, "ui") for n, _ in CAT],
]
ADVISORY = [
    ("border.subtle", ["surface.base"], 1.2, 0, "decor"),
    ("window.unfocused", ["surface.base"], 1.2, 0, "decor"),
]
SEPARATION_MIN = 0.08   # OKLab ΔE: each status colour vs the pop and the band
URGENT_MIN = 0.15       # urgent vs focused window border
PRESSED_MIN = 0.03      # pressed vs normal accent
POP_BAND_MIN = 0.15     # pop vs band: two different colours, not two shades of one
BAND_DL_MIN = 0.10      # band vs foundation lightness ("connected, not fused")
BAND_DC_MIN = 0.06      # band vs foundation colourfulness (coloured families)
LADDER_MIN = 0.02       # foundation levels
# A typical screen, as shares of its area (for the colour-share sanity line).
AREA = {
    "foundation": [("surface.base", .40), ("surface.raised", .12), ("surface.sunken", .05), ("surface.overlay", .03)],
    "band": [("bar.bg", .02), ("bar.shade", .04), ("band.base", .11), ("band.soft", .10),
             ("band.text", .02), ("window.focused", .01)],
    "pop": [("pop.base", .06), ("pop.text", .03), ("bar.pop", .01)],
}

# ════════════════════════════════════════════════════════════════════════════════════════
# 4 · Building one theme
# ════════════════════════════════════════════════════════════════════════════════════════


class Theme:
    def __init__(self, recipe: dict):
        self.r = recipe
        self.t: dict[str, object] = {}     # token → #rrggbb (or a number for opacities)
        self.lch: dict[str, tuple] = {}    # token → (L, C, h) it was made from
        self.nudges: list[str] = []
        self.fails: list[str] = []
        self.found = FOUND[recipe["tone"]]
        self.pol = self.found["polarity"]
        self.st = START[self.pol]

    # -- setting and moving colours ---------------------------------------------------
    def put(self, name: str, L: float, C: float, h: float):
        self.lch[name] = (min(1, max(0, L)), max(0.0, C), h % 360)
        self.t[name] = lch_to_hex(*self.lch[name])

    def seth(self, name: str, hx: str):
        self.t[name] = hx
        self.lch[name] = hex_to_lch(hx)

    def alias(self, name: str, other: str):
        self.lch[name] = self.lch[other]
        self.t[name] = self.t[other]

    def _passes(self, fg: str, bg: str, w: float, lc: float) -> bool:
        return wcag(fg, bg) >= w and abs(apca(fg, bg)) >= lc

    def nudge(self, name: str, against: list[tuple[str, float, float]], move_bg: bool = True):
        """Move `name`'s lightness away from its backgrounds until every pair passes. If the
        foreground hits black or white first, move the background instead (and say so)."""
        L0, C, h = self.lch[name]
        bgs = list(against)
        mean_bg = sum(self.lch[b][0] for b, _, _ in bgs) / len(bgs)
        step = 0.005 if L0 >= mean_bg else -0.005
        L = L0
        ok = lambda: all(self._passes(self.t[name], self.t[b], w, lc) for b, w, lc in bgs)
        bLs = [self.lch[b][0] for b, _, _ in bgs]
        if not ok() and min(bLs) < L0 < max(bLs):
            # the colour sits BETWEEN its backgrounds (a category colour on a white window and a
            # deep bar): search both ways, keep the smallest move that passes
            for k in range(1, 201):
                for sgn in (1, -1):
                    Lt = L0 + sgn * k * 0.005
                    if 0 <= Lt <= 1 and all(self._passes(lch_to_hex(Lt, C, h), self.t[b], w, lc) for b, w, lc in bgs):
                        self.put(name, Lt, C, h)
                        self.nudges.append(f"{name}: L {L0:.3f} → {Lt:.3f} (between its backgrounds)")
                        return
            self.put(name, L0, C, h)
        while not ok() and 0 <= L + step <= 1:
            L += step
            self.put(name, L, C, h)
        if abs(L - L0) > 1e-9:
            self.nudges.append(f"{name}: L {L0:.3f} → {L:.3f}")
        if ok() or not move_bg:
            return
        for b, w, lc in bgs:
            if self._passes(self.t[name], self.t[b], w, lc):
                continue
            bL0, bC, bh = self.lch[b]
            bL, bstep = bL0, -step
            while not self._passes(self.t[name], self.t[b], w, lc) and 0 <= bL + bstep <= 1:
                bL += bstep
                self.put(b, bL, bC, bh)
            self.nudges.append(f"{b}: L {bL0:.3f} → {bL:.3f} (so {name} can pass)")

    def nudge_away(self, name: str, from_: str, w: float, lc: float):
        """Move `name` (a fill) away from `from_` (its text) until they pass."""
        L0, C, h = self.lch[name]
        step = 0.005 if L0 >= self.lch[from_][0] else -0.005
        L = L0
        while not self._passes(self.t[from_], self.t[name], w, lc) and 0 <= L + step <= 1:
            L += step
            self.put(name, L, C, h)
        if abs(L - L0) > 1e-9:
            self.nudges.append(f"{name}: L {L0:.3f} → {L:.3f} (for {from_})")

    def on_colour(self, bg: str, h: float, tint=None) -> tuple[float, float, float]:
        """Near-white or near-black text for a filled colour: whichever reads better.
        `tint` = (hue, chroma) for the light option (cream on red)."""
        coloured = self.lch[bg][1] >= 0.005
        lh, lcc = tint if tint else (h, .010 if coloured else 0.0)
        light, dark = (.985, lcc, lh), (.190, .030 if coloured else 0.0, h)
        cl, cd = lch_to_hex(*light), lch_to_hex(*dark)
        return light if wcag(cl, self.t[bg]) >= wcag(cd, self.t[bg]) else dark

    def separate(self, name: str, froms: list[str], keep: list[tuple[str, float, float]],
                 min_: float = SEPARATION_MIN, prefer: str = "hue"):
        """Turn `name`'s hue away from every colour in `froms` until they are clearly different,
        keeping its contrast pairs passing. Hue first; lightness only if hue alone cannot do it."""
        far = lambda hx: all(delta_e_ok(hx, self.t[f]) >= min_ for f in froms)
        if far(self.t[name]):
            return
        L, C, h0 = self.lch[name]
        dLs, offs = (0, .05, -.05, .10, -.10), (0, 12, -12, 24, -24, 36, -36, 48, -48, 60, -60, 72, -72, 90, -90)
        # "hue": turn the colour first (status colours keep their weight); "light": keep the hue,
        # change lightness first (a pop keeps its harmony: gold stays gold)
        order = ([(dL, o) for dL in dLs for o in offs] if prefer == "hue" else [(dL, o) for o in offs for dL in dLs])
        for dL, off in order:
            if dL == 0 and off == 0:
                continue
            if True:
                trial = lch_to_hex(L + dL, C, h0 + off)
                if far(trial) and all(self._passes(trial, self.t[b], w, lc) for b, w, lc in keep):
                    self.put(name, L + dL, C, h0 + off)
                    self.nudges.append(f"{name}: hue {h0:.0f} → {(h0 + off) % 360:.0f}"
                                       + (f", L {L:.3f} → {L + dL:.3f}" if dL else "")
                                       + f" (kept apart from {', '.join(froms)})")
                    return
        self.fails.append(f"{name} stays close to {', '.join(froms)}")

    # -- the recipe, step by step ------------------------------------------------------
    def build(self) -> "Theme":
        if self.r.get("mocha"):
            return self.build_mocha()
        r, F, st, pol = self.r, self.found, self.st, self.pol
        dark, hc, tone = pol == "dark", r.get("hc", False), r["tone"]
        h = r["hue"]
        shift = r.get("l_shift", 0.0)
        pinned_band = r.get("band")
        band_c = hex_to_lch(pinned_band)[1] if pinned_band else r["band_c"]
        fc = 0.0 if band_c < 0.005 else min(FOUND_CHROMA_MAX, 0.008)

        # 1. FOUNDATION (60 %) — neutral levels, a whisper of the hue at most
        for lvl in ("sunken", "bar", "base", "raised", "overlay", "hover"):
            L = F[lvl] + (shift if F[lvl] > 0 else 0)
            self.put(f"surface.{lvl}", L, fc, h)

        # 2. Text on the foundation — neutral
        self.put("text.primary", st["primary"], fc, h)
        self.put("text.secondary", st["secondary"], fc, h)
        self.put("text.muted", st["muted"], 0.0, h)
        self.nudge("text.primary", [("surface.base", 7.0, 75), ("surface.raised", 7.0, 75),
                                    ("surface.overlay", 4.5, 60), ("surface.sunken", 4.5, 60),
                                    ("surface.hover", 4.5, 60)])
        self.nudge("text.secondary", [(s, 4.5, 60) for s in ("surface.base", "surface.raised",
                                                             "surface.overlay", "surface.sunken")])
        self.nudge("text.muted", [("surface.base", 3.0, 45), ("surface.raised", 3.0, 45)], move_bg=False)
        if hc:   # high contrast: every text level a step further
            surfs = ("surface.base", "surface.raised", "surface.overlay", "surface.sunken", "surface.hover")
            self.nudge("text.primary", [(s, 7.0, 90) for s in surfs], move_bg=False)
            self.nudge("text.secondary", [(s, 7.0, 75) for s in surfs[:4]], move_bg=False)
            self.nudge("text.muted", [(s, 4.5, 60) for s in surfs[:2]], move_bg=False)

        # 3. BAND (30 %) — the theme colour at real strength
        B = BAND[tone]
        if pinned_band:
            bL, bC, bh = hex_to_lch(pinned_band)
            self.put("band.base", bL, bC, bh)
            self.put("band.strong", bL - 0.10, bC * 0.95, bh)
        else:
            bh = h
            if r.get("multi"):   # the band stays neutral-dark; the colour lives in the pop + categories
                B = dict(B, **MULTI_BAND[tone])
            self.put("band.base", B["base"], band_c, h)
            self.put("band.strong", B["strong"], band_c, h)
        self.put("band.on", *self.on_colour("band.base", bh, r.get("on_tint")))
        if not self._passes(self.t["band.on"], self.t["band.base"], 4.5, 60):
            self.nudge_away("band.base", "band.on", 4.5, 60)
        if not self._passes(self.t["band.on"], self.t["band.strong"], 7.0, 75):
            self.nudge_away("band.strong", "band.on", 7.0, 75)
        soft_c = min(band_c * 0.30, 0.045)
        self.put("band.soft", B["soft"] + (shift if dark is False else 0), soft_c, bh)
        if not self._passes(self.t["text.primary"], self.t["band.soft"], 4.5, 60):
            self.nudge_away("band.soft", "text.primary", 4.5, 60)
        self.put("band.text", B["text"], max(band_c, 0.0), bh)
        self.nudge("band.text", [("surface.base", 4.5, 60), ("surface.raised", 4.5, 60)], move_bg=False)

        # 4. POP (10 %) — the harmony colour; accent.* is the pop
        pop = r["pop"]
        if isinstance(pop, tuple):          # a per-theme harmony: (name, hue, chroma)
            _, ph, pC = pop
            pL = st["pop"]
        elif isinstance(pop, str) and pop.startswith("#"):
            pL, pC, ph = hex_to_lch(pop)
        else:
            _, ph, pC = POP[pop]
            pL = r.get("pop_l", st["pop"])
            if pop == "orange":   # Ember's cream is light on a dark foundation
                pL = 0.93
        self.put("pop.base", pL, pC, ph)
        self.nudge("pop.base", [(s, 3.0, 30) for s in ("surface.base", "surface.raised", "surface.overlay")], move_bg=False)
        # keep the pop away from the band; on a gray band only the band itself counts (its light
        # gray line is not a colour the pop can be confused with)
        if pC >= 0.005:
            self.separate("pop.base", ["band.base"] + (["band.text"] if band_c >= 0.005 else []),
                          [(s, 3.0, 30) for s in ("surface.base", "surface.raised", "surface.overlay")], POP_BAND_MIN,
                          prefer="light")
        pL, pC, ph = self.lch["pop.base"]
        if r.get("pop") == "hc":
            self.put("pop.on", *self.on_colour("pop.base", ph))
        else:   # darker pop + white words in light themes; lighter pop + dark words otherwise
            self.put("pop.on", *((.985, .010, ph) if not dark else (.190, .030, ph)))
        if not self._passes(self.t["pop.on"], self.t["pop.base"], 4.5, 60):
            self.nudge_away("pop.base", "pop.on", 4.5, 60)
        self.put("pop.text", *self.lch["pop.base"])
        self.nudge("pop.text", [(s, 4.5, 60) for s in ("surface.base", "surface.raised", "surface.overlay")], move_bg=False)
        self._accent_from_pop()

        # 5. Borders (neutral)
        bL = self.lch["surface.base"][0]
        self.put("border.subtle", bL + st["subtle"], fc, h)
        self.put("border.strong", bL + st["strong"], fc, h)
        self.nudge("border.strong", [("surface.base", 3.0, 30), ("surface.raised", 3.0, 30)], move_bg=False)
        if hc:
            self.nudge("border.subtle", [("surface.base", 3.0, 30), ("surface.raised", 3.0, 30)], move_bg=False)
            self.nudge("border.strong", [("surface.base", 7.0, 75), ("surface.raised", 7.0, 75)], move_bg=False)

        # 6. Status colours — readable as words; kept apart from the pop and the band
        for s, hue in STATUS_HUES.items():
            if s == "warning" and not dark:
                hue = 62
            L = st["status"] + (0.04 if tone == "mid" else 0)
            self.put(f"status.{s}", L, 0.15, hue)
            keep = [("surface.base", 4.5, 60), ("surface.raised", 4.5, 60)]
            self.nudge(f"status.{s}", keep, move_bg=False)
            froms = ["accent.base"] + (["band.text"] if band_c >= 0.005 else [])
            self.separate(f"status.{s}", froms, keep)
            self.put(f"status.on_{s}", *self.on_colour(f"status.{s}", self.lch[f"status.{s}"][2]))
            if not self._passes(self.t[f"status.on_{s}"], self.t[f"status.{s}"], 4.5, 60):
                self.nudge_away(f"status.{s}", f"status.on_{s}", 4.5, 60)

        # 7. Windows: focused = the band colour as a line; urgent moves off the band
        self.alias("window.focused", "band.text")
        self.alias("window.unfocused", "border.subtle")
        self.alias("window.urgent", "status.danger")
        if not self._passes(self.t["window.focused"], self.t["window.unfocused"], 3.0, 30):
            self.nudge_away("window.unfocused", "window.focused", 3.0, 30)
        self.separate("window.urgent", ["window.focused", "accent.base"], [("surface.base", 3.0, 30)], URGENT_MIN)

        # 8. The bar wears the band
        if r.get("bar_bg") == "foundation":
            self.alias("bar.bg", "surface.sunken")
        else:
            self.alias("bar.bg", "band.strong")
        self.alias("bar.shade", "band.base")
        onL = self.lch["band.on"][0]
        hL = self.lch["band.base"][0] + (-0.05 if onL > 0.5 else 0.05)
        self.put("bar.hover", hL, self.lch["band.base"][1], bh)
        self.alias("bar.fg", "band.on")
        self.nudge("bar.fg", [("bar.bg", 7.0, 75), ("bar.shade", 4.5, 60), ("bar.hover", 4.5, 60)], move_bg=False)
        mix = onL * 0.72 + self.lch["band.base"][0] * 0.28
        self.put("bar.fg_dim", mix, min(0.04, self.lch["band.base"][1] * 0.4), bh)
        self.nudge("bar.fg_dim", [("bar.bg", 4.5, 60), ("bar.shade", 4.5, 60)], move_bg=False)
        self.alias("bar.active_bg", "band.on")
        self.alias("bar.active_fg", "band.strong" if r.get("bar_bg") != "foundation" else "surface.sunken")
        self.put("bar.pop", *self.lch["pop.base"])
        self.nudge("bar.pop", [("bar.bg", 3.0, 30), ("bar.shade", 3.0, 30)], move_bg=False)

        # 9. Selection = the band
        self.alias("selection.bg", "band.base")
        self.alias("selection.fg", "band.on")

        # 10. Effects
        if dark:
            self.t["effects.shadow"], self.t["effects.shadow_opacity"] = "#000000", 0.55 if tone != "mid" else 0.45
        else:
            self.put("effects.shadow", 0.25, 0.02, h)
            self.t["effects.shadow_opacity"] = 0.18
        self.alias("effects.blur_tint", "surface.overlay")
        self.t["effects.blur_opacity"] = 0.72 if dark else 0.80

        # 11. Category colours (Multicolor's workspaces, file types, meters)
        for n, hue in CAT:
            self.put(f"cat.{n}", st["cat"] + (0.04 if tone == "mid" else 0), 0.14, hue)
            on_bar = [("bar.shade", 3.0, 30)] if r.get("multi") else []   # Multicolor's workspace numbers
            self.nudge(f"cat.{n}", [("surface.base", 3.0, 30), ("bar.bg", 3.0, 30)] + on_bar, move_bg=False)

        # 12. Terminal: the foundation, 16 colours tuned to it
        self._terminal(fc, h)
        return self

    def _accent_from_pop(self):
        st, dark = self.st, self.pol == "dark"
        self.alias("accent.base", "pop.base")
        self.alias("accent.on", "pop.on")
        self.alias("accent.text", "pop.text")
        self.alias("accent.ring", "pop.base")
        aL, aC, ah = self.lch["accent.base"]
        self.put("accent.hover", aL + st["hover_step"], aC, ah)
        self.put("accent.pressed", aL + st["press_step"], aC * 0.75, ah)
        for k in ("accent.hover", "accent.pressed"):
            if not self._passes(self.t["accent.on"], self.t[k], 4.5, 60):
                self.nudge_away(k, "accent.on", 4.5, 60)
        pL, _, ph = self.lch["accent.pressed"]
        if aC < 0.005:   # a gray pop: the click shows by lightness alone
            while delta_e_ok(self.t["accent.pressed"], self.t["accent.base"]) < PRESSED_MIN * 2 and 0.02 < pL < 0.98:
                pL += 0.02 if self.lch["accent.on"][0] < pL else -0.02
                self.put("accent.pressed", pL, 0.0, 0)
            return
        f = 0.75
        while f > 0.2 and delta_e_ok(self.t["accent.pressed"], self.t["accent.base"]) < PRESSED_MIN:
            f -= 0.05
            self.put("accent.pressed", pL, aC * f, ph)
            if not self._passes(self.t["accent.on"], self.t["accent.pressed"], 4.5, 60):
                self.nudge_away("accent.pressed", "accent.on", 4.5, 60)
        if f < 0.75:
            self.nudges.append(f"accent.pressed: chroma × {f:.2f} (so a click shows)")

    def _terminal(self, fc, h):
        st, dark, tone = self.st, self.pol == "dark", self.r["tone"]
        self.alias("term.bg", "surface.base")
        self.alias("term.fg", "text.primary")
        self.alias("term.cursor", "accent.base")
        self.alias("term.cursor_text", "accent.on")
        self.alias("term.selection_bg", "selection.bg")
        self.alias("term.selection_fg", "selection.fg")
        base = self.lch["surface.base"][0]
        self.put("term.black", base + (0.16 if dark else -0.62), fc, h)
        self.put("term.bright_black", base + (0.30 if dark else -0.45), fc, h)
        self.put("term.white", .82 if dark else base - 0.12, fc, h)
        self.put("term.bright_white", .95 if dark else base - 0.05, fc, h)
        for n, hue in ANSI:
            boost = 0.04 if tone == "mid" else 0
            self.put(f"term.{n}", st["ansi"] + boost, 0.14, hue)
            self.put(f"term.bright_{n}", st["ansi_bright"] + boost, 0.16, hue)
            self.nudge(f"term.{n}", [("term.bg", 4.5, 60)], move_bg=False)
            self.nudge(f"term.bright_{n}", [("term.bg", 3.0, 45)], move_bg=False)

    def build_mocha(self) -> "Theme":
        """Catppuccin Mocha in our roles, the way Catppuccin's style guide assigns them
        (github.com/catppuccin/catppuccin docs/style-guide.md). Mocha's 30 % is its stack of
        panes (mantle, crust, surface0–2); its 10 % is many accents, each with one job."""
        M = MOCHA
        m = lambda tok, name: self.seth(tok, M[name])
        # foundation — "Background pane: Base · Secondary panes: Crust, Mantle · Surfaces: Surface 0–2"
        m("surface.sunken", "crust"); m("surface.bar", "mantle"); m("surface.base", "base")
        m("surface.raised", "shade"); m("surface.overlay", "surface0"); m("surface.hover", "surface1")
        # text — "Body copy: Text · Sub-headlines, labels: Subtext 0/1 · Subtle: Overlay 1"
        # (Subtext 1 and Overlay 2 rather than Subtext 0 / Overlay 1: the same guide entries, the
        #  brighter member, because the dimmer one misses APCA on our raised surfaces)
        m("text.primary", "text"); m("text.secondary", "subtext1"); m("text.muted", "overlay2")
        # band — the panes and the lavender line ("Active border: Lavender")
        m("band.base", "surface0"); m("band.strong", "mantle"); m("band.soft", "surface1")
        m("band.on", "text"); m("band.text", "lavender")
        # pop — mauve, Mocha's signature accent; "text on accent: Base"
        m("pop.base", "mauve"); m("pop.on", "base"); m("pop.text", "mauve")
        self._accent_from_pop()
        # borders — inactive: Overlay 0 per the guide; our list border today: Surface 1
        m("border.subtle", "surface1"); m("border.strong", "overlay1")
        # status — "Success: Green · Warnings: Yellow · Errors: Red · Information: Teal"
        for s, name in (("success", "green"), ("warning", "yellow"), ("danger", "red"), ("info", "teal")):
            m(f"status.{s}", name); m(f"status.on_{s}", "base")
        # windows — "Active border: Lavender · Bell border: Yellow"
        m("window.focused", "lavender"); m("window.unfocused", "surface1"); m("window.urgent", "yellow")
        # the bar — today's: mantle, the shade, text, subtext0; the bell yellow
        m("bar.bg", "mantle"); m("bar.shade", "shade"); m("bar.hover", "surface1")
        m("bar.fg", "text"); m("bar.fg_dim", "subtext1")
        m("bar.active_bg", "mauve"); m("bar.active_fg", "base"); m("bar.pop", "yellow")
        # selection — "Overlay 2 at 20–30 % opacity" (25 % over Base, flattened)
        sel = tuple(a * 0.75 + b * 0.25 for a, b in zip(hex_to_rgb(M["base"]), hex_to_rgb(M["overlay2"])))
        self.seth("selection.bg", rgb_to_hex(sel)); m("selection.fg", "text")
        self.seth("effects.shadow", M["crust"]); self.t["effects.shadow_opacity"] = 0.60
        m("effects.blur_tint", "surface0"); self.t["effects.blur_opacity"] = 0.72
        for n, name in (("red", "red"), ("orange", "peach"), ("yellow", "yellow"), ("green", "green"),
                        ("teal", "teal"), ("blue", "blue"), ("purple", "mauve"), ("pink", "pink")):
            m(f"cat.{n}", name)
        # terminal — the guide's table: cursor Rosewater, cursor text Crust, color0 Surface 1 …
        m("term.bg", "base"); m("term.fg", "text"); m("term.cursor", "rosewater"); m("term.cursor_text", "crust")
        self.alias("term.selection_bg", "selection.bg"); m("term.selection_fg", "text")
        m("term.black", "surface1"); m("term.bright_black", "surface2")
        m("term.white", "subtext0"); m("term.bright_white", "subtext1")
        for n, name in (("red", "red"), ("green", "green"), ("yellow", "yellow"), ("blue", "blue"),
                        ("magenta", "pink"), ("cyan", "teal")):
            m(f"term.{n}", name)
            self.seth(f"term.bright_{n}", MOCHA_ANSI_BRIGHT[n])
        # Faithful means: Catppuccin's own colours first. Where none fits a rule, the smallest
        # lightness nudge — each one listed in the report as a deviation from Catppuccin.
        self.deviations = []
        for fg, bgs, w, lc, kind in RULES:
            if not all(self._passes(self.t[fg], self.t[b], w, lc) for b in bgs):
                before = self.t[fg]
                self.nudge(fg, [(b, w, lc) for b in bgs], move_bg=False)
                self.deviations.append(f"{fg} {before} → {self.t[fg]}")
        self.alias("accent.text", "pop.text")
        return self

    # -- checking ------------------------------------------------------------------------
    def check(self):
        rows = []
        extra = [(f"cat.{n}", ["bar.shade"], 3.0, 30, "ui") for n, _ in CAT] if self.r.get("multi") else []
        for fg, bgs, w, lc, kind in RULES + extra + ADVISORY:
            for bg in bgs:
                cw, cl = wcag(self.t[fg], self.t[bg]), abs(apca(self.t[fg], self.t[bg]))
                ok = cw >= w and cl >= lc
                rows.append(dict(fg=fg, bg=bg, kind=kind, wcag=cw, apca=cl, need_w=w, need_lc=lc,
                                 ok=ok, required=kind != "decor"))
        self.rows = rows
        X = lambda k: hex_to_lch(self.t[k])     # measured on the shipped hex, not the recipe
        coloured = self.r["family"] not in ("neutral", "multi")
        mocha = self.r.get("mocha", False)
        flags, info = [], []
        # foundation ladder and whisper
        order = ["surface.sunken", "surface.base", "surface.raised", "surface.overlay"]
        self.ladder = [(a, b, X(b)[0] - X(a)[0]) for a, b in zip(order, order[1:])]
        for a, b, d in self.ladder:
            if d < LADDER_MIN - 1e-9:
                flags.append(f"foundation {a.split('.')[1]}→{b.split('.')[1]} only ΔL {d:.3f}")
        self.found_c = max(X(k)[1] for k in order)
        # band vs foundation
        self.band_dl = abs(X("band.base")[0] - X("surface.base")[0])
        self.band_dc = X("band.base")[1] - X("surface.base")[1]
        self.pop_band = min([delta_e_ok(self.t["pop.base"], self.t["band.base"])]
                            + ([delta_e_ok(self.t["pop.base"], self.t["band.text"])] if coloured or mocha else []))
        if mocha:
            info.append("faithful Catppuccin: the foundation keeps Mocha's blue-violet tint, the band is its "
                        f"pane stack, the pop is its many accents; {len(self.deviations)} tiny deviations")
        else:
            if self.found_c > FOUND_CHROMA_MAX + 0.004:
                flags.append(f"foundation too colourful (C {self.found_c:.3f})")
            if self.band_dl < BAND_DL_MIN:
                flags.append(f"band too close to the foundation (ΔL {self.band_dl:.3f})")
            if coloured and self.band_dc < BAND_DC_MIN:
                flags.append(f"band not colourful enough vs foundation (ΔC {self.band_dc:.3f})")
            if self.r.get("pop") != "hc" and self.pop_band < POP_BAND_MIN:
                flags.append(f"pop too close to the band (ΔE {self.pop_band:.3f})")
        self.sep = [(f"status.{s}", delta_e_ok(self.t[f"status.{s}"], self.t["accent.base"])) for s in STATUS_HUES]
        self.urgent = delta_e_ok(self.t["window.urgent"], self.t["window.focused"])
        self.pressed_de = delta_e_ok(self.t["accent.pressed"], self.t["accent.base"])
        if self.r.get("pop") != "hc":
            for n, d in self.sep:
                if d < SEPARATION_MIN:
                    flags.append(f"{n} close to the pop (ΔE {d:.3f})")
        if self.urgent < URGENT_MIN:
            flags.append(f"urgent close to focused (ΔE {self.urgent:.3f})")
        if self.pressed_de < PRESSED_MIN:
            flags.append(f"pressed barely differs (ΔE {self.pressed_de:.3f})")
        # colour share: of all the colour (chroma × area) on a typical screen, where does it live?
        share = {g: sum(a * X(k)[1] for k, a in parts) for g, parts in AREA.items()}
        tot = sum(share.values())
        self.share = {g: v / tot for g, v in share.items()} if tot > 0.004 else None
        if coloured and not mocha and self.share and self.share["foundation"] > 0.25:
            flags.append(f"foundation carries {self.share['foundation']:.0%} of the colour")
        self.design_flags, self.design_info = flags, info
        return self

    @property
    def required_fails(self):
        return [r for r in self.rows if r["required"] and not r["ok"]]

    # -- output ---------------------------------------------------------------------------
    def as_dict(self) -> dict:
        r = self.r
        tables: dict[str, dict] = {}
        for k, v in self.t.items():
            tab, key = k.split(".", 1)
            tables.setdefault(tab, {})[key] = v
        cur = r["cursor"]
        cursor = f"catppuccin-mocha-{cur}-cursors"
        pop = r.get("pop")
        harmony = ("Catppuccin's many accents" if r.get("mocha") else pop[0] if isinstance(pop, tuple)
                   else "emblem blue" if isinstance(pop, str) and pop.startswith("#") else POP[pop][0])
        return {
            "meta": dict(name=r["name"], slug=r["slug"], family=r["family"], tone=r["tone"],
                         polarity=self.pol, multi=r.get("multi", False), hc=r.get("hc", False),
                         default=r.get("default", False), design="60-30-10", pop_harmony=harmony,
                         schema=SCHEMA_VERSION),
            **{k: tables[k] for k in ("surface", "text", "band", "pop", "accent", "border", "window",
                                      "bar", "selection", "status", "effects", "cat", "term")},
            "brand": dict(BRAND),
            "names": dict(
                gtk_theme="adw-gtk3-dark" if self.pol == "dark" else "adw-gtk3",
                color_scheme="prefer-dark" if self.pol == "dark" else "prefer-light",
                gnome_accent=r["gnome"], cursor=cursor, cursor_size=24, icons="candy-icons",
                icons_symbolic="Papirus-Dark" if self.pol == "dark" else "Papirus-Light",
                wallpaper_set=r["slug"],
            ),
        }

# ════════════════════════════════════════════════════════════════════════════════════════
# 5 · Writers: TOML, report, swatch sheet, per-program examples
# ════════════════════════════════════════════════════════════════════════════════════════


def toml_value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, list):
        return "[" + ", ".join(toml_value(x) for x in v) + "]"
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'


def toml_tables(d: dict, prefix: str = "") -> str:
    out, scalars = [], {k: v for k, v in d.items() if not isinstance(v, dict)}
    if scalars and prefix:
        out.append(f"[{prefix}]")
    out += [f"{k} = {toml_value(v)}" for k, v in scalars.items()]
    if scalars:
        out.append("")
    for k, v in d.items():
        if isinstance(v, dict):
            out.append(toml_tables(v, f"{prefix}.{k}" if prefix else k))
    return "\n".join(out)


HEADER = """# hypeForge colour theme{plural} — generated by docs/research/look-2026-10/palette/generate.py
# Do not edit by hand: change the recipe in generate.py and run it again.
# A THEME is colours only. Shapes (corners, shadows' size, gaps, border widths) belong to a STYLE.
# Token meanings: docs/research/look-2026-10/03-theme-system.md
"""


def write_toml(themes: list[Theme]):
    body = HEADER.format(plural="s") + "\n" + toml_tables(
        {"meta": dict(schema=SCHEMA_VERSION, count=len(themes), order=[t.r["slug"] for t in themes])}) + "\n"
    for t in themes:
        body += toml_tables({"themes": {t.r["slug"]: t.as_dict()}}) + "\n"
    (HERE / "palettes.toml").write_text(body)
    for t in themes:
        p = HERE / "themes" / t.r["slug"] / "theme.toml"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(HEADER.format(plural="") + "\n" + toml_tables(t.as_dict()))


def write_report(themes: list[Theme]):
    n = len(themes)
    L = [f"# Contrast report — the {n} hypeForge themes (v2, 60-30-10)", "",
         "*Generated by `generate.py`. Every row is measured on the final hex values (what ships). "
         "WCAG = contrast ratio (4.5 reading text, 3 icons and borders, 7 the stricter level). "
         "APCA = the newer perceptual score |Lc| (75 body text, 60 readable text, 45 hints, 30 icons and lines).*", "",
         "## Summary", "",
         "| Theme | Tone | Required pairs | Pass | Lowest text ratio | Lowest UI ratio | Nudges | Notes |",
         "|---|---|---|---|---|---|---|---|"]
    for t in themes:
        req = [r for r in t.rows if r["required"]]
        texts = [r["wcag"] for r in req if r["kind"] == "text"]
        uis = [r["wcag"] for r in req if r["kind"] == "ui"]
        L.append(f"| {t.r['name']} | {t.r['tone']} | {len(req)} | {sum(r['ok'] for r in req)}/{len(req)} | "
                 f"{min(texts):.2f} | {min(uis):.2f} | {len(t.nudges)} | {'; '.join(t.fails) or '—'} |")
    total = sum(len([r for r in t.rows if r["required"]]) for t in themes)
    passed = sum(sum(r["ok"] for r in t.rows if r["required"]) for t in themes)
    L += ["", f"**All themes: {passed} of {total} required pairs pass.**", "",
          "## Design checks — the 60-30-10 rules", "",
          f"- **Foundation** (60 %): neutral; its most colourful level stays at chroma ≤ {FOUND_CHROMA_MAX} (+ rounding); neighbouring levels ΔL ≥ {LADDER_MIN}.",
          f"- **Band** (30 %): at least ΔL {BAND_DL_MIN} from the foundation and, in coloured families, ΔC ≥ {BAND_DC_MIN}: connected, not fused.",
          f"- **Pop** (10 %): at least ΔE {POP_BAND_MIN} from the band (a second colour, not a shade of the first); status colours ΔE ≥ {SEPARATION_MIN} from the pop; urgent ΔE ≥ {URGENT_MIN} from focused; pressed ΔE ≥ {PRESSED_MIN}.",
          "- **Colour share**: on a typical screen (60 % foundation, 30 % band, 10 % pop by area), how much of the *colour* (chroma × area) each part carries. A coloured theme whose foundation carries more than 25 % reads monotone.", "",
          "| Theme | Foundation C max | Band ΔL / ΔC | Pop vs band ΔE | Urgent vs focused | Colour share F · B · P | Flags |",
          "|---|---|---|---|---|---|---|"]
    for t in themes:
        s = t.share
        share = f"{s['foundation']:.0%} · {s['band']:.0%} · {s['pop']:.0%}" if s else "grayscale (no colour)"
        flags = "; ".join(t.design_flags) or ("ℹ " + "; ".join(t.design_info) if t.design_info else "—")
        L.append(f"| {t.r['name']} | {t.found_c:.3f} | {t.band_dl:.2f} / {t.band_dc:+.3f} | {t.pop_band:.3f} | "
                 f"{t.urgent:.3f} | {share} | {flags} |")
    L += [""]
    for t in themes:
        L += [f"## {t.r['name']} (`{t.r['slug']}`)", ""]
        if getattr(t, "deviations", None):
            L += ["**Deviations from Catppuccin** (no Catppuccin colour passed the rule, so the smallest "
                  "lightness nudge): " + "; ".join(f"`{x}`" for x in t.deviations), ""]
        if t.nudges:
            L += ["Nudged: " + "; ".join(f"`{x}`" for x in t.nudges), ""]
        L += ["| Foreground | Background | Kind | WCAG | need | APCA Lc | need | Result |", "|---|---|---|---|---|---|---|---|"]
        for r in t.rows:
            res = "pass" if r["ok"] else ("**FAIL**" if r["required"] else "soft (decorative)")
            L.append(f"| `{r['fg']}` {t.t[r['fg']]} | `{r['bg']}` {t.t[r['bg']]} | {r['kind']} | "
                     f"{r['wcag']:.2f} | {r['need_w']} | {r['apca']:.1f} | {r['need_lc']} | {res} |")
        L.append("")
    (HERE / "contrast-report.md").write_text("\n".join(L))


def _on(hx: str) -> str:
    """Black-ish or white-ish text for a sample chip."""
    return "#111111" if wcag("#111111", hx) >= wcag("#fafafa", hx) else "#fafafa"


def write_swatches(themes: list[Theme]):
    def card(t: Theme) -> str:
        c = t.t
        req = [r for r in t.rows if r["required"]]
        ok = sum(r["ok"] for r in req)
        multi = t.r.get("multi")
        ws = ""
        for i in range(5):
            if multi:
                col = c["cat." + CAT[[5, 6, 3, 1, 7][i]][0]]
                ws += (f'<b class="ws on" style="background:{col};color:{_on(col)}">{i + 1}</b>' if i == 0 else
                       f'<b class="ws" style="color:{col}">{i + 1}</b>')
            else:
                ws += (f'<b class="ws on" style="background:{c["bar.active_bg"]};color:{c["bar.active_fg"]}">1</b>' if i == 0
                       else f'<b class="ws" style="color:{c["bar.fg_dim"]}">{i + 1}</b>')
        term = "".join(f'<span style="color:{c["term." + n]}">{n[:3]}</span> ' for n, _ in ANSI)
        status = "".join(f'<span class="chip" style="background:{c["status." + s]};color:{c["status.on_" + s]}">{s}</span>'
                         for s in STATUS_HUES)
        tokens = "".join(f'<tr><td><i style="background:{v}"></i></td><td>{k}</td><td>{v}</td></tr>'
                         for k, v in t.t.items() if isinstance(v, str))
        harmony = t.as_dict()["meta"]["pop_harmony"]
        f_, b_, p_ = c["surface.base"], c["band.base"], c["pop.base"]
        flag = "" if not t.design_flags else f'<p class="flag">⚠ {html.escape("; ".join(t.design_flags))}</p>'
        def sw(label, hx, sub):
            return f'<span class="key"><i style="background:{hx}"></i><span><b>{label}</b> {sub}<code>{hx}</code></span></span>'
        return f"""
<article class="theme" data-tone="{t.r['tone']}">
  <header><h3>{html.escape(t.r['name'])}</h3>{'<span class="tag def">default</span>' if t.r.get('default') else ''}{'<span class="tag">high contrast</span>' if t.r.get('hc') else ''}<span class="tag">{t.r['tone']}</span>
    <span class="score {'good' if ok == len(req) else 'bad'}">{ok}/{len(req)} pass</span></header>
  <div class="split" title="60 · 30 · 10"><span style="flex:6;background:{f_}"></span><span style="flex:3;background:{b_}"></span><span style="flex:1;background:{p_}"></span></div>
  <div class="keys">{sw('60 Foundation', f_, '')}{sw('30 Band', b_, '')}{sw('10 Pop', p_, html.escape(harmony))}</div>
  <div class="desk" style="background:{c['surface.sunken']}">
    <div class="bar" style="background:{c['bar.bg']};color:{c['bar.fg']}">
      <span class="seg" style="background:{c['bar.shade']}"><em class="emb"><u style="background:{BRAND['emblem_blue']}"></u><u style="background:{BRAND['emblem_orange']}"></u></em>{ws}<span class="menu" style="color:{c['bar.fg_dim']}">Favorites</span></span>
      <span class="seg" style="background:{c['bar.shade']}"><span class="app" style="border-color:{c['bar.fg']}"></span><span class="app dim" style="border-color:transparent;background:{c['bar.fg_dim']}"></span></span>
      <span class="seg" style="background:{c['bar.shade']}"><span class="bell" style="color:{c['bar.fg_dim']}">🔔<i style="background:{c['bar.pop']}"></i></span>12:30</span>
    </div>
    <div class="wins">
      <div class="win" style="background:{c['surface.base']};border-color:{c['window.focused']};color:{c['text.primary']}">
        <div class="head" style="background:{c['band.base']};color:{c['band.on']}">Settings <span>✕</span></div>
        <div class="body">
          <div class="side" style="background:{c['band.soft']};color:{c['text.primary']}">
            <span class="cur" style="border-color:{c['band.text']}">Look</span><span>Sound</span><span>Network</span></div>
          <div class="main">
            <div class="search" style="background:{c['surface.sunken']};border-color:{c['border.strong']}">fir<span style="color:{c['accent.text']}">▏</span></div>
            <div class="res"><b style="color:{c['accent.text']}">Fir</b>efox</div>
            <div class="res sel" style="background:{c['selection.bg']};color:{c['selection.fg']}"><b>Fi</b>les</div>
            <div class="tog-row" style="color:{c['text.secondary']}">Night light <span class="tog" style="background:{c['accent.base']}"><i style="background:{c['accent.on']}"></i></span></div>
            <div class="tog-row" style="color:{c['text.secondary']}">Do not disturb <span class="tog off" style="background:{c['surface.hover']}"><i style="background:{c['text.secondary']}"></i></span></div>
            <div class="btns"><span class="btn" style="background:{c['accent.base']};color:{c['accent.on']}">Apply</span>
              <span class="btn ghost" style="border-color:{c['border.strong']};color:{c['text.primary']}">Cancel</span>
              <span class="badge" style="background:{c['pop.base']};color:{c['pop.on']}">3 new</span></div>
            <p class="small" style="color:{c['text.muted']}">a hint · <a style="color:{c['accent.text']}">a link</a></p>
          </div>
        </div>
      </div>
      <div class="win" style="background:{c['surface.base']};border-color:{c['window.unfocused']};color:{c['text.primary']}">
        <div class="head quiet" style="background:{c['surface.raised']};color:{c['text.secondary']}">Terminal</div>
        <div class="pad">
          <div class="statuses">{status}</div>
          <div class="term" style="background:{c['term.bg']};color:{c['term.fg']}">$ {term}<span style="background:{c['term.cursor']}">&nbsp;</span></div>
          <div class="urgent" style="border-color:{c['window.urgent']};color:{c['text.secondary']}">urgent window</div>
        </div>
      </div>
    </div>
  </div>
  {flag}
  <details><summary>All {len([v for v in t.t.values() if isinstance(v, str)])} colours</summary><table>{tokens}</table></details>
</article>"""

    families = [("kognog", "KognogOS Mocha — today's look, the default"), ("neutral", "Grays (White and Black: high contrast)"),
                ("orange", "Ember — black, white, gray and the emblem orange"), ("blue", "Blues"), ("purple", "Purples"),
                ("green", "Greens"), ("pink", "Pinks"), ("red", "Reds"), ("multi", "Multicolor")]
    groups = ""
    for fam, title in families:
        cards = "".join(card(t) for t in themes if t.r["family"] == fam)
        groups += f'<section><h2>{title}</h2><div class="grid">{cards}</div></section>'
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>hypeForge Theme Swatches</title>
<style>
:root{{--bg:#eeeef1;--fg:#1b1b20;--dim:#5b5b66;--card:#ffffff;--line:#d8d8de;--good:#1f7a3a;--bad:#b3261e}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#121216;--fg:#e8e8ee;--dim:#a0a0ad;--card:#1c1c22;--line:#2f2f38;--good:#6fd08c;--bad:#ff8a80}}}}
:root[data-theme="dark"]{{--bg:#121216;--fg:#e8e8ee;--dim:#a0a0ad;--card:#1c1c22;--line:#2f2f38;--good:#6fd08c;--bad:#ff8a80}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,"Noto Sans",sans-serif;padding:28px 16px 64px}}
main{{max-width:1560px;margin:0 auto}}
h1{{font-size:28px;margin:0 0 6px;letter-spacing:-.01em}} h2{{font-size:17px;margin:36px 0 12px}}
.lead{{color:var(--dim);max-width:80ch;margin:0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:18px}}
.theme{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;min-width:0}}
.theme header{{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:10px}}
.theme h3{{margin:0 4px 0 0;font-size:15px}}
.tag{{font-size:11px;color:var(--dim);border:1px solid var(--line);border-radius:99px;padding:0 7px}}
.tag.def{{color:var(--fg);border-color:var(--fg)}}
.score{{font-size:11px;margin-left:auto}} .good{{color:var(--good)}} .bad{{color:var(--bad);font-weight:700}}
.split{{display:flex;height:10px;border-radius:5px;overflow:hidden;border:1px solid var(--line);margin-bottom:8px}}
.keys{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:10px}}
.key{{display:flex;gap:6px;align-items:flex-start;font-size:11px;color:var(--dim);min-width:0}}
.key i{{flex:none;width:18px;height:18px;border-radius:5px;border:1px solid rgba(127,127,127,.35)}}
.key b{{color:var(--fg);font-weight:600;display:block}} .key code{{display:block;font-size:10px}}
.desk{{border-radius:8px;overflow:hidden;padding-bottom:10px}}
.bar{{display:flex;justify-content:space-between;gap:5px;font-size:11px;height:26px;align-items:stretch;padding:0 0}}
.seg{{display:flex;align-items:center;gap:3px;padding:0 7px;white-space:nowrap}}
.ws{{display:inline-block;min-width:17px;text-align:center;font-size:10px;line-height:17px;font-weight:700}}
.ws.on{{border-radius:3px}}
.menu{{margin-left:4px}}
.emb{{display:inline-flex;flex-direction:column;gap:1px;margin-right:4px}} .emb u{{display:block;width:11px;height:5px}}
.app{{display:inline-block;width:12px;height:12px;border-radius:3px;border-bottom:2px solid;opacity:.9;background:currentColor}}
.app.dim{{opacity:.6}}
.bell{{position:relative;font-size:10px;margin-right:6px;filter:grayscale(1)}}
.bell i{{position:absolute;right:-3px;top:-1px;width:7px;height:7px;border-radius:50%;filter:none}}
.wins{{display:grid;grid-template-columns:1.45fr 1fr;gap:10px;padding:10px 10px 0}}
.win{{border:2px solid;font-size:12px;min-width:0;display:flex;flex-direction:column}}
.head{{display:flex;justify-content:space-between;padding:3px 7px;font-weight:600;font-size:11px}}
.head.quiet{{font-weight:500}}
.body{{display:grid;grid-template-columns:64px 1fr;flex:1}}
.side{{display:flex;flex-direction:column;gap:2px;padding:6px 0;font-size:10px}}
.side span{{padding:1px 6px;border-left:2px solid transparent}} .side .cur{{font-weight:700}}
.main{{padding:6px;min-width:0}}
.search{{border:1px solid;padding:1px 5px;font-size:10px;margin-bottom:3px}}
.res{{font-size:10px;padding:1px 5px}} .res.sel{{font-weight:500}}
.tog-row{{display:flex;justify-content:space-between;align-items:center;font-size:10px;margin-top:4px}}
.tog{{width:24px;height:13px;border-radius:7px;position:relative;display:inline-block}}
.tog i{{position:absolute;right:2px;top:2px;width:9px;height:9px;border-radius:50%}}
.tog.off i{{left:2px;right:auto}}
.btns{{display:flex;gap:5px;align-items:center;flex-wrap:wrap;margin-top:6px}}
.btn{{padding:2px 8px;font-size:10px;font-weight:700;border-radius:4px}} .ghost{{border:1px solid;font-weight:500}}
.badge{{font-size:9px;font-weight:700;padding:1px 6px;border-radius:99px}}
.small{{font-size:10px;margin:5px 0 0}} .small a{{text-decoration:underline}}
.pad{{padding:6px}}
.statuses{{display:flex;flex-wrap:wrap;gap:3px}} .chip{{font-size:9px;padding:1px 5px;border-radius:3px;font-weight:700}}
.term{{margin-top:6px;padding:4px;font:10px/1.4 ui-monospace,"JetBrainsMono Nerd Font",monospace;word-break:break-word}}
.urgent{{margin-top:6px;border:2px solid;padding:2px 5px;font-size:10px}}
.flag{{color:var(--bad);font-size:11px;margin:8px 0 0}}
details{{font-size:12px;color:var(--dim);margin-top:8px}} details table{{border-collapse:collapse;margin-top:6px}}
td{{padding:1px 6px 1px 0;font:11px ui-monospace,monospace}} td i{{display:inline-block;width:14px;height:14px;border-radius:3px;border:1px solid rgba(127,127,127,.35)}}
.filters{{display:flex;gap:6px;flex-wrap:wrap;margin:18px 0 0}}
.filters button{{background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:99px;padding:4px 12px;font:inherit;cursor:pointer}}
.filters button[aria-pressed="true"]{{border-color:var(--fg);font-weight:600}}
@media (max-width:440px){{.wins{{grid-template-columns:1fr}} .keys{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>hypeForge — {len(themes)} colour themes · v2</h1>
<p class="lead">Every theme is built the 60-30-10 way: a neutral <b>foundation</b> (windows, panels, the terminal), the theme colour as a strong <b>band</b> (the bar, panel headers, the side panel, the selected row, the focused border), and a <b>pop</b> in a harmony colour for small important things (the letters you typed, toggles, badges, buttons, the bell's dot). The strip under each name shows the split. Every text and border pair is measured with WCAG 2.2 and APCA.</p>
<div class="filters" role="group" aria-label="Show tone">
<button aria-pressed="true" data-f="all">All</button><button aria-pressed="false" data-f="white light">Light</button>
<button aria-pressed="false" data-f="mid">Middle</button><button aria-pressed="false" data-f="dark black">Dark</button></div>
{groups}
</main>
<script>
document.querySelectorAll('.filters button').forEach(b=>b.addEventListener('click',()=>{{
  document.querySelectorAll('.filters button').forEach(x=>x.setAttribute('aria-pressed',x===b));
  const f=b.dataset.f.split(' ');
  document.querySelectorAll('.theme').forEach(c=>c.style.display=(f[0]==='all'||f.includes(c.dataset.tone))?'':'none');
}}));
</script></body></html>
"""
    (HERE / "swatches.html").write_text(page)


def render(t: Theme):
    """Example files each program would read — proof that the token names map onto every consumer.
    The real apply step (Phase 4) writes these to ~/.config/hypeforge/theme/."""
    c, d = t.t, t.as_dict()
    out = HERE / "render" / t.r["slug"]
    out.mkdir(parents=True, exist_ok=True)
    head = f"theme {t.r['name']} ({t.r['slug']}), generated — do not edit"
    hx = lambda k: c[k].lstrip("#")
    (out / "sway-colors.conf").write_text(f"""# hypeForge {head}
# include ~/.config/hypeforge/theme/sway-colors.conf   (near the top of sway/config)
set $hf_active    {c['window.focused']}
set $hf_inactive  {c['window.unfocused']}
set $hf_titlebar  {c['bar.bg']}
set $hf_text      {c['text.primary']}
set $hf_subtext   {c['text.secondary']}
set $hf_urgent    {c['window.urgent']}
set $hf_band      {c['band.base']}
set $hf_band_on   {c['band.on']}
set $hf_pop       {c['pop.base']}

# class                 title-bar edge  title-bar     title text    next-split    window border
client.focused          $hf_active      $hf_band      $hf_band_on   $hf_active    $hf_active
client.focused_inactive $hf_inactive    $hf_titlebar  $hf_subtext   $hf_inactive  $hf_inactive
client.unfocused        $hf_inactive    $hf_titlebar  $hf_subtext   $hf_inactive  $hf_inactive
client.urgent           $hf_urgent      $hf_titlebar  $hf_text      $hf_urgent    $hf_urgent
client.background       {c['surface.base']}
seat * xcursor_theme {d['names']['cursor']} {d['names']['cursor_size']}
""")
    defs = "\n".join(f"@define-color hf_{k.replace('.', '_')} {v};" for k, v in c.items() if isinstance(v, str))
    (out / "colors.css").write_text(f"/* hypeForge {head}.\n   Waybar: @import url(\"../../hypeforge/theme/colors.css\"); as the first line of style.css.\n   gtklock: @import url(\"file:///home/USER/.config/hypeforge/theme/colors.css\"); */\n{defs}\n")
    (out / "mako-colors.conf").write_text(f"""# hypeForge {head}
# mako: include=~/.config/hypeforge/theme/mako-colors.conf  (first line of ~/.config/mako/config)
background-color={c['surface.raised']}
text-color={c['text.primary']}
border-color={c['band.base']}
progress-color=over {c['accent.base']}

[urgency=low]
border-color={c['border.subtle']}
text-color={c['text.secondary']}

[urgency=critical]
border-color={c['status.danger']}
""")
    (out / "fuzzel-colors.ini").write_text(f"""# hypeForge {head}
# fuzzel: include=~/.config/hypeforge/theme/fuzzel-colors.ini  (in [main]; this file has its own section)
[colors]
background={hx('surface.raised')}ff
text={hx('text.primary')}ff
prompt={hx('text.secondary')}ff
placeholder={hx('text.muted')}ff
input={hx('text.primary')}ff
match={hx('accent.text')}ff
selection={hx('selection.bg')}ff
selection-text={hx('selection.fg')}ff
selection-match={hx('selection.fg')}ff
border={hx('band.base')}ff
""")
    gtk_pairs = {
        "accent_color": "accent.text", "accent_bg_color": "accent.base", "accent_fg_color": "accent.on",
        "window_bg_color": "surface.base", "window_fg_color": "text.primary",
        "view_bg_color": "surface.base", "view_fg_color": "text.primary",
        "headerbar_bg_color": "band.base", "headerbar_fg_color": "band.on", "headerbar_border_color": "band.strong",
        "headerbar_backdrop_color": "surface.raised", "sidebar_bg_color": "band.soft", "sidebar_fg_color": "text.primary",
        "sidebar_backdrop_color": "band.soft",
        "card_bg_color": "surface.raised", "card_fg_color": "text.primary",
        "popover_bg_color": "surface.raised", "popover_fg_color": "text.primary",
        "dialog_bg_color": "surface.raised", "dialog_fg_color": "text.primary",
        "thumbnail_bg_color": "surface.raised", "thumbnail_fg_color": "text.primary",
        "destructive_color": "status.danger", "destructive_bg_color": "status.danger", "destructive_fg_color": "status.on_danger",
        "success_color": "status.success", "success_bg_color": "status.success", "success_fg_color": "status.on_success",
        "warning_color": "status.warning", "warning_bg_color": "status.warning", "warning_fg_color": "status.on_warning",
        "error_color": "status.danger", "error_bg_color": "status.danger", "error_fg_color": "status.on_danger",
        "borders": "border.subtle",
    }
    shade = "rgba(0, 0, 0, 0.36)" if t.pol == "dark" else "rgba(0, 0, 0, 0.07)"
    gtk = "\n".join(f"@define-color {k} {c[v]};" for k, v in gtk_pairs.items())
    gtk += "".join(f"\n@define-color {k} {shade};" for k in ("headerbar_shade_color", "sidebar_shade_color",
                                                           "card_shade_color", "popover_shade_color", "shade_color"))
    css_vars = "\n".join(f"  --{k.replace('_', '-')}: {c[v]};" for k, v in gtk_pairs.items() if k != "borders")
    (out / "gtk.css").write_text(f"""/* hypeForge {head}.
   GTK 3 (adw-gtk3) reads the @define-color names; GTK 4 / libadwaita 1.6+ reads the :root
   variables (and still accepts the old names). Copied to ~/.config/gtk-3.0/ and gtk-4.0/.
   Title bars wear the band; side panels the quiet band; content the foundation; buttons the pop.
   Theme name for gsettings: {d['names']['gtk_theme']}; color-scheme {d['names']['color_scheme']};
   accent-color {d['names']['gnome_accent']}. */
{gtk}

:root {{
{css_vars}
  --border-color: {c['border.subtle']};
}}
""")
    (out / "alacritty-colors.toml").write_text(f"""# hypeForge {head}
# Alacritty: [general] import = ["~/.config/hypeforge/theme/alacritty-colors.toml"]
[colors.primary]
background = "{c['term.bg']}"
foreground = "{c['term.fg']}"

[colors.cursor]
text = "{c['term.cursor_text']}"
cursor = "{c['term.cursor']}"

[colors.selection]
text = "{c['term.selection_fg']}"
background = "{c['term.selection_bg']}"

[colors.normal]
black = "{c['term.black']}"
""" + "".join(f'{n} = "{c["term." + n]}"\n' for n, _ in ANSI) + f"""white = "{c['term.white']}"

[colors.bright]
black = "{c['term.bright_black']}"
""" + "".join(f'{n} = "{c["term.bright_" + n]}"\n' for n, _ in ANSI) + f"""white = "{c['term.bright_white']}"
""")
    (out / "mc-aliases.ini").write_text(f"""# hypeForge {head}
# Midnight Commander: replaces the [aliases] block of themes/mc/kognogos-mocha.ini; the rest of the
# skin already uses these names, so only this block changes per theme. The skin draws normal text
# on "Selected", so the quiet band (band.soft) is the selection here, not the full band.
[aliases]
    Crust = {c['surface.sunken']}
    Mantle = {c['band.strong']}
    Base = {c['surface.base']}
    Surface0 = {c['surface.raised']}
    Surface1 = {c['band.soft']}
    Surface2 = {c['border.subtle']}
    Overlay0 = {c['text.muted']}
    Overlay1 = {c['text.muted']}
    Subtext0 = {c['text.secondary']}
    Subtext1 = {c['text.secondary']}
    Text = {c['text.primary']}
    Lavender = {c['cat.purple']}
    Blue = {c['cat.blue']}
    Sapphire = {c['cat.blue']}
    Sky = {c['cat.teal']}
    Teal = {c['cat.teal']}
    Green = {c['cat.green']}
    Yellow = {c['cat.yellow']}
    Peach = {c['cat.orange']}
    Maroon = {c['cat.red']}
    Red = {c['status.danger']}
    Mauve = {c['band.text']}
    Pink = {c['cat.pink']}
    Flamingo = {c['cat.pink']}
    Main = Base
    MainFg = Text
    Selected = Surface1
    MarkedFg = Peach
    HeaderFg = Mauve
    Dialog = Surface0
    DialogFg = Text
    DialogFocus = {c['accent.base']}
    DialogFocusFg = {c['accent.on']}
    Input = Base
    InputFg = Text
    PaleFg = Overlay0
    Bar = {c['band.base']}
    BarFg = {c['band.on']}
    Accent = {c['accent.base']}
    AccentFg = {c['accent.on']}
    Error = {c['status.danger']}
    ErrorFg = {c['status.on_danger']}
    ErrorFocus = Maroon
""")


# ════════════════════════════════════════════════════════════════════════════════════════


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if any required pair fails")
    ap.add_argument("--render", nargs="*", default=["kognogos-mocha", "purple", "white", "ember"],
                    help="themes that get example program files in render/")
    a = ap.parse_args()

    themes = [Theme(r).build().check() for r in THEMES]
    assert len(themes) == 25, len(themes)
    assert len({t.r["slug"] for t in themes}) == 25
    write_toml(themes)
    write_report(themes)
    write_swatches(themes)
    for slug in a.render:
        render(next(t for t in themes if t.r["slug"] == slug))

    # read our own TOML back: a file the theme app cannot parse is worse than none
    data = tomllib.loads((HERE / "palettes.toml").read_text())
    assert len(data["themes"]) == 25 and data["meta"]["order"][0] == "kognogos-mocha"
    for t in themes:
        tomllib.loads((HERE / "themes" / t.r["slug"] / "theme.toml").read_text())

    fails = [(t.r["slug"], r) for t in themes for r in t.required_fails]
    total = sum(len([r for r in t.rows if r["required"]]) for t in themes)
    print(f"{len(themes)} themes · {total} required pairs · {total - len(fails)} pass · {len(fails)} fail · "
          f"{sum(len(t.nudges) for t in themes)} nudges")
    for slug, r in fails:
        print(f"  FAIL {slug}: {r['fg']} on {r['bg']}  WCAG {r['wcag']:.2f}/{r['need_w']}  APCA {r['apca']:.1f}/{r['need_lc']}")
    for t in themes:
        for f in t.fails + t.design_flags:
            print(f"  NOTE {t.r['slug']}: {f}")
    print(f"wrote palettes.toml, themes/*/theme.toml, contrast-report.md, swatches.html, render/{{{','.join(a.render)}}}/")
    return 1 if (a.check and fails) else 0


if __name__ == "__main__":
    sys.exit(main())
