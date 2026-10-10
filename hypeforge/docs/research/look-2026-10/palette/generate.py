#!/usr/bin/env python3
"""
hypeForge palette generator — the 23 colour themes of the look program (2026-10).

What it does, in plain words:
  1. Each theme is a short RECIPE: how light the surfaces are (the "tone"), which hue
     tints them, and which colour is the accent. Recipes are in THEMES below.
  2. The recipe is turned into ~60 named colours ("tokens": surface.base, text.primary,
     accent.base, bar.fg …) using OKLCH, a colour space where "lightness" means what
     the eye sees. All the maths is here, standard library only.
  3. Every pair of colours that must be readable together (text on its background,
     a focused border against the window …) is measured with WCAG 2.2 and APCA. When a
     pair fails, the generator moves the lightness one small step at a time until it
     passes ("nudging") and writes down what it moved.
  4. It writes: palettes.toml (all 23), themes/<slug>/theme.toml (one file per theme),
     contrast-report.md, swatches.html, and render/<slug>/ example files for each
     program (Sway, Waybar, mako, fuzzel, gtklock, GTK 3/4, Alacritty, Midnight Commander).

Run:     python3 generate.py            (writes everything next to this file)
         python3 generate.py --check    (also exits 1 if any required pair fails)
         python3 generate.py --render dark-purple white blue   (which themes get example files)

Colour science credits (thank you): OKLab/OKLCH by Björn Ottosson (2020); WCAG 2.2 contrast
by the W3C; APCA (Accessible Perceptual Contrast Algorithm, APCA-W3 0.0.98G-4g constants)
by Andrew Somers / Myndex. Today's look (Catppuccin Mocha, catppuccin.com) is the reference
the Dark Purple theme is tuned to stay close to.

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
SCHEMA_VERSION = 1

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
# 2 · The brand and the recipes
# ════════════════════════════════════════════════════════════════════════════════════════

# Sampled from assets/kognogos-emblem.png (k-means over the solid pixels, 2026-10-10) and
# kognog/config/os-release (ANSI_COLOR="38;2;203;166;247"). Fixed: never nudged; for the logo
# and brand marks only, not for text.
BRAND = {
    "emblem_blue": "#0363ef",        # top layers, 35 % of the emblem
    "emblem_blue_deep": "#0048b6",   # their shaded side, 22 %
    "emblem_orange": "#d9400e",      # bottom layer, 28 %
    "emblem_orange_deep": "#b93205", # its shaded side, 14 %
    "wordmark_gray": "#969696",      # the "Kognog OS" letters in logo.png
    "kognog_mauve": "#cba6f7",       # the OS's own colour (os-release ANSI_COLOR, Plymouth ring,
                                     # kognogos.org, the prompt) — "the Kognog purple"
}

# Lightness (OKLCH L, 0 = black, 1 = white) of every surface level, per tone.
# "dark" is tuned so Dark Purple lands on today's Catppuccin Mocha values
# (mantle #181825 ≈ .216, base #1e1e2e ≈ .243, the bar's shade #262637 ≈ .27, surface0 ≈ .31,
# surface1 #45475a ≈ .40).
TONES = {
    #          sunken  bar    base   raised overlay hover  polarity (which way text goes)
    "white": dict(sunken=.925, bar=.945, base=.958, raised=.980, overlay=1.0, hover=.895, polarity="light"),
    "light": dict(sunken=.875, bar=.890, base=.925, raised=.950, overlay=.975, hover=.850, polarity="light"),
    "mid":   dict(sunken=.335, bar=.300, base=.395, raised=.425, overlay=.455, hover=.505, polarity="dark"),
    "dark":  dict(sunken=.183, bar=.216, base=.243, raised=.277, overlay=.324, hover=.404, polarity="dark"),
    "black": dict(sunken=.000, bar=.000, base=.105, raised=.175, overlay=.215, hover=.300, polarity="dark"),
}

# Where each kind of colour starts, by polarity (the nudging then makes them pass).
START = {
    "dark":  dict(primary=.880, secondary=.760, muted=.640, accent=.780, status=.800, cat=.780,
                  ansi=.760, ansi_bright=.850, subtle=.15, strong=.56, hover_step=+.05, press_step=-.06),
    "light": dict(primary=.240, secondary=.420, muted=.560, accent=.520, status=.520, cat=.560,
                  ansi=.480, ansi_bright=.400, subtle=-.13, strong=-.37, hover_step=-.05, press_step=-.10),
}

STATUS_HUES = {"success": 145, "warning": 85, "danger": 22, "info": 240}
CAT = [("red", 25), ("orange", 55), ("yellow", 95), ("green", 145),
       ("teal", 185), ("blue", 255), ("purple", 305), ("pink", 350)]
ANSI = [("red", 25), ("green", 145), ("yellow", 90), ("blue", 255), ("magenta", 330), ("cyan", 195)]

# The 23 themes. surf = (hue, chroma) of the surfaces' tint; accent = a brand hex (pinned) or
# (L, C, h). l_shift moves the whole surface ladder (Light Gray a step darker than "light").
#   cursor: installed theme names (catppuccin-mocha-*-cursors, checked in /usr/share/icons)
#   gnome: the nearest of GNOME/libadwaita's nine named accents (the portal's accent-color)
THEMES = [
    # White and Black are the HIGH-CONTRAST themes (Javier, 2026-10-10: "they are high contrast
    # themes and gray scale use for styling. Not pure."): grays only, the accent a near-black /
    # near-white gray, stronger text and borders (hc=True). Colour stays only where it means
    # something: status, urgent, the terminal's colours.
    dict(slug="white",            name="White",            family="neutral", tone="white", surf=(262, 0.0),  accent=(.25, 0.0, 0),        cursor="dark",  gnome="slate", hc=True),
    dict(slug="light-gray",       name="Light Gray",       family="neutral", tone="light", surf=(262, 0.0),  accent=BRAND["emblem_blue"],  cursor="dark",  gnome="slate", l_shift=-.025),
    dict(slug="gray",             name="Gray",             family="neutral", tone="mid",   surf=(262, 0.0),  accent=(.80, .12, 258),       cursor="dark",  gnome="slate", l_shift=+.015),
    dict(slug="dark-gray",        name="Dark Gray",        family="neutral", tone="dark",  surf=(262, 0.0),  accent=(.78, .12, 258),       cursor="dark",  gnome="slate"),
    dict(slug="black",            name="Black",            family="neutral", tone="black", surf=(262, 0.0),  accent=(.92, 0.0, 0),        cursor="light", gnome="slate", hc=True),
    dict(slug="dark-blue",        name="Dark Blue",        family="blue",    tone="dark",  surf=(262, .035), accent=(.78, .13, 258),       cursor="blue",  gnome="blue"),
    dict(slug="blue",             name="Blue",             family="blue",    tone="mid",   surf=(262, .058), accent=(.86, .12, 225),       cursor="blue",  gnome="blue"),
    dict(slug="light-blue",       name="Light Blue",       family="blue",    tone="light", surf=(250, .025), accent=BRAND["emblem_blue"],  cursor="blue",  gnome="blue"),
    dict(slug="light-purple",     name="Light Purple",     family="purple",  tone="light", surf=(300, .025), accent=(.50, .19, 302),       cursor="mauve", gnome="purple"),
    dict(slug="purple",           name="Purple",           family="purple",  tone="mid",   surf=(295, .072), accent=BRAND["kognog_mauve"], cursor="mauve", gnome="purple"),
    dict(slug="dark-purple",      name="Dark Purple",      family="purple",  tone="dark",  surf=(284, .030), accent=BRAND["kognog_mauve"], cursor="mauve", gnome="purple"),
    dict(slug="light-green",      name="Light Green",      family="green",   tone="light", surf=(150, .025), accent=(.50, .14, 150),       cursor="green", gnome="green"),
    dict(slug="green",            name="Green",            family="green",   tone="mid",   surf=(158, .060), accent=(.87, .16, 135),       cursor="green", gnome="green"),
    dict(slug="dark-green",       name="Dark Green",       family="green",   tone="dark",  surf=(155, .030), accent=(.80, .15, 145),       cursor="green", gnome="green"),
    dict(slug="light-pink",       name="Light Pink",       family="pink",    tone="light", surf=(350, .025), accent=(.55, .19, 355),       cursor="pink",  gnome="pink"),
    dict(slug="pink",             name="Pink",             family="pink",    tone="mid",   surf=(350, .052), accent=(.86, .11, 350),       cursor="pink",  gnome="pink"),
    dict(slug="dark-pink",        name="Dark Pink",        family="pink",    tone="dark",  surf=(350, .030), accent=(.80, .13, 350),       cursor="pink",  gnome="pink"),
    dict(slug="light-red",        name="Light Red",        family="red",     tone="light", surf=(25, .025),  accent=(.52, .19, 27),        cursor="red",   gnome="red"),
    dict(slug="red",              name="Red",              family="red",     tone="mid",   surf=(25, .062),  accent=(.82, .13, 36),        cursor="red",   gnome="red"),
    dict(slug="dark-red",         name="Dark Red",         family="red",     tone="dark",  surf=(25, .030),  accent=(.72, .16, 24),        cursor="red",   gnome="red"),
    dict(slug="light-multicolor", name="Light Multicolor", family="multi",   tone="light", surf=(262, 0.0),  accent=(.50, .19, 302),       cursor="dark",  gnome="purple", multi=True),
    dict(slug="multicolor",       name="Multicolor",       family="multi",   tone="mid",   surf=(262, 0.0),  accent=BRAND["kognog_mauve"], cursor="dark",  gnome="purple", multi=True, l_shift=-.03),
    dict(slug="dark-multicolor",  name="Dark Multicolor",  family="multi",   tone="dark",  surf=(262, 0.0),  accent=BRAND["kognog_mauve"], cursor="dark",  gnome="purple", multi=True),
]

# ════════════════════════════════════════════════════════════════════════════════════════
# 3 · The pairs that must pass (the contract) — (foreground, backgrounds, WCAG min, APCA |Lc| min)
# ════════════════════════════════════════════════════════════════════════════════════════
# Kinds: "text" = words people read; "ui" = icons, borders, focus marks (WCAG 1.4.11 / 2.4.13);
# "hint" = placeholder / disabled text (WCAG exempts it, we still keep it findable).
RULES = [
    ("text.primary",   ["surface.base", "surface.raised"], 7.0, 75, "text"),
    ("text.primary",   ["surface.overlay", "surface.sunken", "surface.hover"], 4.5, 60, "text"),
    ("text.secondary", ["surface.base", "surface.raised", "surface.overlay", "surface.sunken"], 4.5, 60, "text"),
    ("text.muted",     ["surface.base", "surface.raised"], 3.0, 45, "hint"),
    ("accent.text",    ["surface.base", "surface.raised", "surface.overlay"], 4.5, 60, "text"),
    ("accent.base",    ["surface.base", "surface.raised", "surface.overlay", "bar.bg"], 3.0, 30, "ui"),
    ("accent.on",      ["accent.base", "accent.hover", "accent.pressed"], 4.5, 60, "text"),
    ("accent.ring",    ["surface.base", "surface.raised"], 3.0, 30, "ui"),
    ("border.strong",  ["surface.base", "surface.raised"], 3.0, 30, "ui"),
    ("window.focused", ["surface.base", "window.unfocused"], 3.0, 30, "ui"),
    ("window.urgent",  ["surface.base"], 3.0, 30, "ui"),
    ("bar.fg",         ["bar.bg"], 7.0, 75, "text"),
    ("bar.fg",         ["bar.shade", "bar.hover"], 4.5, 60, "text"),
    ("bar.fg_dim",     ["bar.bg", "bar.shade"], 4.5, 60, "text"),
    ("bar.active_fg",  ["bar.active_bg"], 4.5, 60, "text"),
    ("bar.active_bg",  ["bar.bg", "bar.shade"], 3.0, 30, "ui"),
    ("selection.fg",   ["selection.bg"], 4.5, 60, "text"),
    *[(f"status.{s}", ["surface.base", "surface.raised"], 4.5, 60, "text") for s in STATUS_HUES],
    *[(f"status.on_{s}", [f"status.{s}"], 4.5, 60, "text") for s in STATUS_HUES],
    ("term.fg",        ["term.bg"], 7.0, 75, "text"),
    *[(f"term.{n}", ["term.bg"], 4.5, 60, "text") for n, _ in ANSI],
    *[(f"term.bright_{n}", ["term.bg"], 3.0, 45, "text") for n, _ in ANSI],
    *[(f"cat.{n}", ["surface.base", "bar.bg"], 3.0, 30, "ui") for n, _ in CAT],
]
# Advisory (reported, not required): decorative lines may be soft on purpose.
ADVISORY = [
    ("border.subtle", ["surface.base"], 1.2, 0, "decor"),
    ("window.unfocused", ["surface.base"], 1.2, 0, "decor"),
]
SEPARATION_MIN = 0.08   # OKLab ΔE: accent vs each status colour
URGENT_MIN = 0.15       # OKLab ΔE: urgent vs focused window border (a border must be noticed at a glance)
PRESSED_MIN = 0.03      # OKLab ΔE: pressed vs normal accent (the click must show)
CHROMA_BUDGET = 1.5     # accent chroma ÷ surface chroma
LADDER_MIN = 0.02       # OKLCH ΔL between neighbouring surface levels

# ════════════════════════════════════════════════════════════════════════════════════════
# 4 · Building one theme
# ════════════════════════════════════════════════════════════════════════════════════════


class Theme:
    def __init__(self, recipe: dict):
        self.r = recipe
        self.t: dict[str, str] = {}        # token → #rrggbb
        self.lch: dict[str, tuple] = {}    # token → (L, C, h) it was made from
        self.nudges: list[str] = []
        self.fails: list[str] = []
        self.tone = TONES[recipe["tone"]]
        self.pol = self.tone["polarity"]
        self.st = START[self.pol]

    # -- setting and moving colours ---------------------------------------------------
    def put(self, name: str, L: float, C: float, h: float):
        self.lch[name] = (min(1, max(0, L)), C, h % 360)
        self.t[name] = lch_to_hex(*self.lch[name])

    def alias(self, name: str, other: str):
        self.lch[name] = self.lch[other]
        self.t[name] = self.t[other]

    def _passes(self, fg: str, bg: str, w: float, lc: float) -> bool:
        return wcag(fg, bg) >= w and abs(apca(fg, bg)) >= lc

    def nudge(self, name: str, against: list[tuple[str, float, float]], move_bg: bool = True):
        """Move `name`'s lightness away from its backgrounds until every pair passes. If the
        foreground hits black or white first, move the background instead (and say so)."""
        L0, C, h = self.lch[name]
        bgs = [(b, w, lc) for b, w, lc in against]
        mean_bg = sum(self.lch[b][0] for b, _, _ in bgs) / len(bgs)
        step = 0.005 if L0 >= mean_bg else -0.005
        L = L0
        ok = lambda: all(self._passes(self.t[name], self.t[b], w, lc) for b, w, lc in bgs)
        while not ok() and 0 <= L + step <= 1:
            L += step
            self.put(name, L, C, h)
        if abs(L - L0) > 1e-9:
            self.nudges.append(f"{name}: L {L0:.3f} → {L:.3f}")
        if ok() or not move_bg:
            return
        for b, w, lc in bgs:  # foreground is at the end of its range: move the background
            if self._passes(self.t[name], self.t[b], w, lc):
                continue
            bL0, bC, bh = self.lch[b]
            bL, bstep = bL0, -step
            while not self._passes(self.t[name], self.t[b], w, lc) and 0 <= bL + bstep <= 1:
                bL += bstep
                self.put(b, bL, bC, bh)
            self.nudges.append(f"{b}: L {bL0:.3f} → {bL:.3f} (so {name} can pass)")

    def on_colour(self, bg: str, h: float) -> tuple[float, float, float]:
        """Near-white or near-black text for a filled colour: whichever reads better."""
        tint = self.lch[bg][1] >= 0.005   # a gray fill gets gray text, not a tinted one
        light, dark = (.985, .010 if tint else 0.0, h), (.200, .030 if tint else 0.0, h)
        cl, cd = lch_to_hex(*light), lch_to_hex(*dark)
        return light if wcag(cl, self.t[bg]) >= wcag(cd, self.t[bg]) else dark

    def separate(self, name: str, from_: str, keep: list[tuple[str, float, float]], min_: float = SEPARATION_MIN):
        """Rotate `name`'s hue away from `from_` until they are clearly different colours,
        keeping its contrast pairs passing (red danger in a red theme, green success in a green one)."""
        if delta_e_ok(self.t[name], self.t[from_]) >= min_:
            return
        L, C, h0 = self.lch[name]
        # hue first (keeps the colour's weight), lightness only if hue alone cannot do it
        for dL in (0, .05, -.05, .10, -.10):
            for off in (12, -12, 24, -24, 36, -36, 48, -48, 60, -60, 72, -72):
                trial = lch_to_hex(L + dL, C, h0 + off)
                if (delta_e_ok(trial, self.t[from_]) >= min_
                        and all(self._passes(trial, self.t[b], w, lc) for b, w, lc in keep)):
                    self.put(name, L + dL, C, h0 + off)
                    self.nudges.append(f"{name}: hue {h0:.0f} → {(h0 + off) % 360:.0f}"
                                       + (f", L {L:.3f} → {L + dL:.3f}" if dL else "")
                                       + f" (kept apart from {from_})")
                    return
        self.fails.append(f"{name} stays close to {from_} (ΔE {delta_e_ok(self.t[name], self.t[from_]):.3f})")

    # -- the recipe, step by step ------------------------------------------------------
    def build(self) -> "Theme":
        r, tone, st, pol = self.r, self.tone, self.st, self.pol
        sh, sc = r["surf"]
        shift = r.get("l_shift", 0.0)
        dark = pol == "dark"

        # 1. Surfaces — the ladder. The bar is a touch more tinted than the rest.
        for lvl in ("sunken", "bar", "base", "raised", "overlay", "hover"):
            c = sc * (1.15 if lvl == "bar" else 1.0)
            L = tone[lvl] + (shift if tone[lvl] > 0 else 0)
            self.put(f"surface.{lvl}", L, c, sh)

        # 2. Text — tinted a little toward the surfaces' hue.
        tc = min(0.035, sc * 0.9)
        self.put("text.primary", st["primary"], tc, sh)
        self.put("text.secondary", st["secondary"], tc, sh)
        self.put("text.muted", st["muted"], tc * 0.8, sh)
        self.nudge("text.primary", [("surface.base", 7.0, 75), ("surface.raised", 7.0, 75),
                                    ("surface.overlay", 4.5, 60), ("surface.sunken", 4.5, 60),
                                    ("surface.hover", 4.5, 60)])
        self.nudge("text.secondary", [(s, 4.5, 60) for s in ("surface.base", "surface.raised",
                                                             "surface.overlay", "surface.sunken")])
        self.nudge("text.muted", [("surface.base", 3.0, 45), ("surface.raised", 3.0, 45)], move_bg=False)
        hc = r.get("hc", False)
        if hc:   # high contrast: every text level a step further
            surfs = ("surface.base", "surface.raised", "surface.overlay", "surface.sunken", "surface.hover")
            self.nudge("text.primary", [(s, 7.0, 90) for s in surfs], move_bg=False)
            self.nudge("text.secondary", [(s, 7.0, 75) for s in surfs[:4]], move_bg=False)
            self.nudge("text.muted", [(s, 4.5, 60) for s in surfs[:2]], move_bg=False)

        # 3. Accent — pinned brand colour or a recipe; must stand out from every surface.
        acc = r["accent"]
        aL, aC, ah = hex_to_lch(acc) if isinstance(acc, str) else acc
        self.put("accent.base", aL, aC, ah)
        # (against the bar too, once the bar exists — step 7)
        self.nudge("accent.base", [(s, 3.0, 30) for s in ("surface.base", "surface.raised",
                                                          "surface.overlay")], move_bg=False)
        # text on the accent (buttons, the active workspace)
        self.put("accent.on", *self.on_colour("accent.base", ah))
        aL = self.lch["accent.base"][0]
        self.put("accent.hover", aL + st["hover_step"], aC, ah)
        # pressed: a step darker AND a quarter less colour, so it still shows when contrast
        # rules push its lightness back toward the normal accent
        self.put("accent.pressed", aL + st["press_step"], aC * 0.75, ah)
        for k in ("accent.base", "accent.hover", "accent.pressed"):
            if not self._passes(self.t["accent.on"], self.t[k], 4.5, 60):
                # move the fill away from its text, never the text (it is already black/white)
                self.nudge_away(k, "accent.on", 4.5, 60)
        # if contrast pushed "pressed" back onto the accent, take more colour out until it shows
        pL, pC, ph = self.lch["accent.pressed"]
        f = 0.75
        if aC < 0.005:   # a gray accent: the click shows by lightness alone
            step = 1 if dark else -1
            while delta_e_ok(self.t["accent.pressed"], self.t["accent.base"]) < PRESSED_MIN * 2 and 0.02 < pL < 0.98:
                pL -= 0.02 * step if dark else -0.02 * step
                self.put("accent.pressed", pL, 0.0, 0)
            f = 0.0
        while f > 0.2 and delta_e_ok(self.t["accent.pressed"], self.t["accent.base"]) < PRESSED_MIN and f > 0.2:
            f -= 0.05
            self.put("accent.pressed", pL, aC * f, ph)
            if not self._passes(self.t["accent.on"], self.t["accent.pressed"], 4.5, 60):
                self.nudge_away("accent.pressed", "accent.on", 4.5, 60)
        if 0 < f < 0.75:
            self.nudges.append(f"accent.pressed: chroma × {f:.2f} (so a click shows)")
        # accent used as words (links, the letters you typed in a list)
        self.put("accent.text", *self.lch["accent.base"])
        self.nudge("accent.text", [(s, 4.5, 60) for s in ("surface.base", "surface.raised",
                                                          "surface.overlay")], move_bg=False)
        self.alias("accent.ring", "accent.base")

        # 4. Borders
        bL = self.lch["surface.base"][0]
        self.put("border.subtle", bL + st["subtle"], sc, sh)
        self.put("border.strong", bL + st["strong"], sc, sh)
        self.nudge("border.strong", [("surface.base", 3.0, 30), ("surface.raised", 3.0, 30)], move_bg=False)
        if hc:   # high contrast: a line you can always see, and a strong one that reads like text
            self.nudge("border.subtle", [("surface.base", 3.0, 30), ("surface.raised", 3.0, 30)], move_bg=False)
            self.nudge("border.strong", [("surface.base", 7.0, 75), ("surface.raised", 7.0, 75)], move_bg=False)

        # 5. Status colours — readable as words; kept apart from the accent.
        for s, hue in STATUS_HUES.items():
            if s == "warning" and not dark:
                hue = 62   # amber, not mustard, on light surfaces
            L = st["status"] + (0.04 if r["tone"] == "mid" else 0)
            self.put(f"status.{s}", L, 0.15, hue)
            keep = [("surface.base", 4.5, 60), ("surface.raised", 4.5, 60)]
            self.nudge(f"status.{s}", keep, move_bg=False)
            self.separate(f"status.{s}", "accent.base", keep)
            self.put(f"status.on_{s}", *self.on_colour(f"status.{s}", self.lch[f"status.{s}"][2]))
            if not self._passes(self.t[f"status.on_{s}"], self.t[f"status.{s}"], 4.5, 60):
                self.nudge_away(f"status.{s}", f"status.on_{s}", 4.5, 60)

        # 6. Windows (Sway's borders): focused = accent, unfocused = the subtle line, urgent = danger
        self.alias("window.focused", "accent.base")
        self.alias("window.unfocused", "border.subtle")
        self.alias("window.urgent", "status.danger")
        if not self._passes(self.t["window.focused"], self.t["window.unfocused"], 3.0, 30):
            self.nudge_away("window.unfocused", "window.focused", 3.0, 30)
        self.separate("window.urgent", "window.focused", [("surface.base", 3.0, 30)], URGENT_MIN)

        # 7. The bar
        self.alias("bar.bg", "surface.bar")
        self.alias("bar.shade", "surface.raised")
        self.alias("bar.hover", "surface.hover")
        self.put("bar.fg", *self.lch["text.primary"])
        self.put("bar.fg_dim", *self.lch["text.secondary"])
        self.nudge("bar.fg", [("bar.bg", 7.0, 75), ("bar.shade", 4.5, 60), ("bar.hover", 4.5, 60)], move_bg=False)
        self.nudge("bar.fg_dim", [("bar.bg", 4.5, 60), ("bar.shade", 4.5, 60)], move_bg=False)
        if not all(self._passes(self.t["accent.base"], self.t[b], 3.0, 30) for b in ("bar.bg", "bar.shade")):
            self.nudge("accent.base", [("bar.bg", 3.0, 30), ("bar.shade", 3.0, 30),
                                       ("surface.base", 3.0, 30)], move_bg=False)
            self.alias("accent.ring", "accent.base")
            self.alias("window.focused", "accent.base")
        self.alias("bar.active_bg", "accent.base")
        self.alias("bar.active_fg", "accent.on")

        # 8. Selection (highlighted list row, selected text)
        sL = self.lch["surface.base"][0] + (0.14 if dark else -0.14)
        self.put("selection.bg", sL, min(0.08, aC * 0.5), ah)
        self.alias("selection.fg", "text.primary")
        if not self._passes(self.t["selection.fg"], self.t["selection.bg"], 4.5, 60):
            self.nudge_away("selection.bg", "selection.fg", 4.5, 60)

        # 9. Effects: shadow and the frosted-glass tint (SwayFX / mock-ups)
        if dark:
            self.t["effects.shadow"], self.t["effects.shadow_opacity"] = "#000000", 0.55 if r["tone"] != "mid" else 0.45
        else:
            self.put("effects.shadow", 0.25, min(0.04, sc + 0.01), sh)
            self.t["effects.shadow_opacity"] = 0.18
        self.alias("effects.blur_tint", "surface.overlay")
        self.t["effects.blur_opacity"] = 0.72 if dark else 0.80

        # 10. Categorical colours (workspaces in Multicolor, file types in mc, meters, charts)
        for n, hue in CAT:
            self.put(f"cat.{n}", st["cat"] + (0.05 if r["tone"] == "mid" else 0), 0.14, hue)
            self.nudge(f"cat.{n}", [("surface.base", 3.0, 30), ("bar.bg", 3.0, 30)], move_bg=False)

        # 11. Terminal (Alacritty): background = the window surface, 16 colours tuned to it
        self.alias("term.bg", "surface.base")
        self.alias("term.fg", "text.primary")
        self.alias("term.cursor", "accent.base")
        self.alias("term.cursor_text", "accent.on")
        self.alias("term.selection_bg", "selection.bg")
        self.alias("term.selection_fg", "selection.fg")
        base = self.lch["surface.base"][0]
        self.put("term.black", base + (0.16 if dark else -0.62), sc, sh)
        self.put("term.bright_black", base + (0.30 if dark else -0.45), sc, sh)
        self.put("term.white", .82 if dark else base - 0.12, tc, sh)
        self.put("term.bright_white", .95 if dark else base - 0.05, tc, sh)
        for n, hue in ANSI:
            boost = 0.04 if r["tone"] == "mid" else 0
            self.put(f"term.{n}", st["ansi"] + boost, 0.14, hue)
            self.put(f"term.bright_{n}", st["ansi_bright"] + boost, 0.16, hue)
            self.nudge(f"term.{n}", [("term.bg", 4.5, 60)], move_bg=False)
            self.nudge(f"term.bright_{n}", [("term.bg", 3.0, 45)], move_bg=False)
        return self

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

    # -- checking ------------------------------------------------------------------------
    def check(self):
        rows = []
        for fg, bgs, w, lc, kind in RULES + ADVISORY:
            for bg in bgs:
                cw, cl = wcag(self.t[fg], self.t[bg]), abs(apca(self.t[fg], self.t[bg]))
                ok = cw >= w and cl >= lc
                rows.append(dict(fg=fg, bg=bg, kind=kind, wcag=cw, apca=cl, need_w=w, need_lc=lc,
                                 ok=ok, required=kind != "decor"))
        self.rows = rows
        sep = []
        for s in STATUS_HUES:
            sep.append((f"status.{s}", "accent.base", delta_e_ok(self.t[f"status.{s}"], self.t["accent.base"])))
        sep.append(("window.urgent", "window.focused", delta_e_ok(self.t["window.urgent"], self.t["window.focused"])))
        self.sep = sep
        ladder = []
        order = ["surface.sunken", "surface.base", "surface.raised", "surface.overlay"]
        Lof = lambda k: hex_to_lch(self.t[k])[0]   # measured on the shipped hex, not the recipe
        for a, b in zip(order, order[1:]):
            ladder.append((a, b, Lof(b) - Lof(a)))
        self.ladder = ladder
        ac, bc = hex_to_lch(self.t["accent.base"])[1], hex_to_lch(self.t["surface.base"])[1]
        self.chroma_budget = (ac, bc)
        self.pressed_de = delta_e_ok(self.t["accent.pressed"], self.t["accent.base"])
        flags = []
        for a, b, d in ladder:
            if d < LADDER_MIN - 1e-9:
                flags.append(f"{a.split('.')[1]}→{b.split('.')[1]} only ΔL {d:.3f} (needs a border or shadow to read as a layer)")
        if bc >= 0.005 and ac / bc < CHROMA_BUDGET:
            flags.append(f"accent only {ac / bc:.1f}× the surface colour")
        for n, f, d in sep[:-1]:
            if d < SEPARATION_MIN:
                flags.append(f"{n} close to the accent (ΔE {d:.3f})")
        if sep[-1][2] < URGENT_MIN:
            flags.append(f"urgent border close to focused (ΔE {sep[-1][2]:.3f})")
        if self.pressed_de < PRESSED_MIN:
            flags.append(f"pressed accent barely differs (ΔE {self.pressed_de:.3f})")
        self.design_flags = flags
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
        cursor = {"dark": "catppuccin-mocha-dark-cursors", "light": "catppuccin-mocha-light-cursors"}.get(
            r["cursor"], f"catppuccin-mocha-{r['cursor']}-cursors")
        d = {
            "meta": dict(name=r["name"], slug=r["slug"], family=r["family"], tone=r["tone"],
                         polarity=self.pol, multi=r.get("multi", False), schema=SCHEMA_VERSION),
            **{k: tables[k] for k in ("surface", "text", "accent", "border", "window", "bar",
                                      "selection", "status", "effects")},
            "cat": tables["cat"],
            "term": tables["term"],
            "brand": dict(BRAND),
            "names": dict(
                gtk_theme="adw-gtk3-dark" if self.pol == "dark" else "adw-gtk3",
                color_scheme="prefer-dark" if self.pol == "dark" else "prefer-light",
                gnome_accent=r["gnome"],
                cursor=cursor, cursor_size=24,
                icons="candy-icons",
                icons_symbolic="Papirus-Dark" if self.pol == "dark" else "Papirus-Light",
                wallpaper_set=r["slug"],
            ),
        }
        return d


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
    L = ["# Contrast report — the 23 hypeForge themes", "",
         "*Generated by `generate.py`. Every row is measured on the final hex values (what ships), "
         "not on the recipe. WCAG = contrast ratio (4.5 is the minimum for reading text, 3 for icons "
         "and borders, 7 is the stricter level). APCA = the newer perceptual score |Lc| "
         "(75 = body text, 60 = readable text, 45 = large text or hints, 30 = icons and lines).*", "",
         "## Summary", "",
         "| Theme | Tone | Required pairs | Pass | Lowest text ratio | Lowest UI ratio | Nudges | Notes |",
         "|---|---|---|---|---|---|---|---|"]
    for t in themes:
        req = [r for r in t.rows if r["required"]]
        texts = [r["wcag"] for r in req if r["kind"] == "text"]
        uis = [r["wcag"] for r in req if r["kind"] == "ui"]
        notes = "; ".join(t.fails) or "—"
        L.append(f"| {t.r['name']} | {t.r['tone']} | {len(req)} | "
                 f"{sum(r['ok'] for r in req)}/{len(req)} | {min(texts):.2f} | {min(uis):.2f} | "
                 f"{len(t.nudges)} | {notes} |")
    total = sum(len([r for r in t.rows if r["required"]]) for t in themes)
    passed = sum(sum(r["ok"] for r in t.rows if r["required"]) for t in themes)
    L += ["", f"**All themes: {passed} of {total} required pairs pass.**", ""]
    L += ["## Design checks (not WCAG — the \"make things pop\" rules)", "",
          f"- **Ladder:** neighbouring surfaces differ by at least ΔL {LADDER_MIN} (OKLCH lightness), "
          "so a raised panel is visibly a different layer.",
          f"- **Separation:** the accent and each status colour, and the urgent and focused borders, "
          f"are at least ΔE {SEPARATION_MIN} apart (OKLab), so \"error\" never looks like \"selected\".",
          "- **Chroma budget:** the accent carries more colour than the surfaces (ratio shown), "
          "so the eye goes to it first.", "",
          f"- **Pressed shows:** the pressed accent is at least ΔE {PRESSED_MIN} from the normal one; "
          f"the urgent border at least ΔE {URGENT_MIN} from the focused one.", "",
          "| Theme | Ladder ΔL (sunken→base→raised→overlay) | Accent ÷ surface chroma | Closest status to accent (ΔE) | Urgent vs focused (ΔE) | Pressed vs accent (ΔE) | Flags |",
          "|---|---|---|---|---|---|---|"]
    for t in themes:
        lad = " · ".join(f"{d:+.3f}" for _, _, d in t.ladder)
        ac, bc = t.chroma_budget
        ratio = "∞ (neutral)" if bc < 0.005 else f"{ac / bc:.1f}×"
        st = min(t.sep[:-1], key=lambda s: s[2])
        L.append(f"| {t.r['name']} | {lad} | {ratio} | {st[0].split('.')[1]} {st[2]:.3f} | {t.sep[-1][2]:.3f} | "
                 f"{t.pressed_de:.3f} | {'; '.join(t.design_flags) or '—'} |")
    L += [""]
    for t in themes:
        L += [f"## {t.r['name']} (`{t.r['slug']}`)", ""]
        if t.nudges:
            L += ["Nudged: " + "; ".join(f"`{n}`" for n in t.nudges), ""]
        L += ["| Foreground | Background | Kind | WCAG | need | APCA Lc | need | Result |", "|---|---|---|---|---|---|---|---|"]
        for r in t.rows:
            res = "pass" if r["ok"] else ("**FAIL**" if r["required"] else "soft (decorative)")
            L.append(f"| `{r['fg']}` {t.t[r['fg']]} | `{r['bg']}` {t.t[r['bg']]} | {r['kind']} | "
                     f"{r['wcag']:.2f} | {r['need_w']} | {r['apca']:.1f} | {r['need_lc']} | {res} |")
        L.append("")
    (HERE / "contrast-report.md").write_text("\n".join(L))


def write_swatches(themes: list[Theme]):
    def card(t: Theme) -> str:
        c = t.t
        req = [r for r in t.rows if r["required"]]
        ok = sum(r["ok"] for r in req)
        low = min(r["wcag"] for r in req if r["kind"] == "text")
        cats = "".join(f'<i style="background:{c["cat." + n]}" title="cat.{n} {c["cat." + n]}"></i>' for n, _ in CAT)
        wsnums = ("".join(f'<b style="background:{c["cat." + CAT[i][0]]};color:{c["surface.bar"]}">{i + 1}</b>' for i in range(5))
                  if t.r.get("multi") else
                  f'<b style="background:{c["bar.active_bg"]};color:{c["bar.active_fg"]}">1</b>'
                  + "".join(f'<b style="color:{c["bar.fg_dim"]}">{i}</b>' for i in range(2, 6)))
        term = "".join(f'<span style="color:{c["term." + n]}">{n[:3]}</span> ' for n, _ in ANSI)
        status = "".join(
            f'<span class="chip" style="background:{c["status." + s]};color:{c["status.on_" + s]}">{s}</span>'
            for s in STATUS_HUES)
        status_text = " ".join(f'<span style="color:{c["status." + s]}">{s}</span>' for s in STATUS_HUES)
        tokens = "".join(f'<tr><td><i style="background:{v}"></i></td><td>{k}</td><td>{v}</td></tr>'
                         for k, v in t.t.items() if isinstance(v, str))
        return f"""
<article class="theme" data-tone="{t.r['tone']}" data-family="{t.r['family']}">
  <header><h3>{html.escape(t.r['name'])}</h3><span class="tag">{t.r['tone']}</span>
    <span class="score {'good' if ok == len(req) else 'bad'}">{ok}/{len(req)} pass · text ≥ {low:.1f}:1</span></header>
  <div class="desk" style="background:{c['surface.sunken']}">
    <div class="bar" style="background:{c['bar.bg']};color:{c['bar.fg']}">
      <span class="seg" style="background:{c['bar.shade']}"><em class="emb"><u style="background:{BRAND['emblem_blue']}"></u><u style="background:{BRAND['emblem_orange']}"></u></em>{wsnums}<span style="color:{c['bar.fg_dim']}">Favorites</span></span>
      <span class="seg" style="background:{c['bar.shade']}"><span class="dot" style="border-bottom:2px solid {c['bar.fg']}">●</span><span class="dot" style="color:{c['bar.fg_dim']}">●</span></span>
      <span class="seg" style="background:{c['bar.shade']}">Sat 10 Oct 12:30</span>
    </div>
    <div class="wins">
      <div class="win" style="background:{c['surface.base']};border-color:{c['window.focused']};color:{c['text.primary']}">
        <div class="panel" style="background:{c['surface.raised']};border-color:{c['border.subtle']}">
          <strong>Focused window</strong>
          <p style="color:{c['text.secondary']}">Secondary text: details.</p>
          <p style="color:{c['text.muted']}">Muted: a hint</p>
          <div class="row" style="background:{c['selection.bg']};color:{c['selection.fg']}">Selected row</div>
          <div class="btns"><span class="btn" style="background:{c['accent.base']};color:{c['accent.on']}">Apply</span>
            <span class="btn ghost" style="border-color:{c['border.strong']};color:{c['text.primary']}">Cancel</span>
            <a style="color:{c['accent.text']}">a link</a></div>
        </div>
      </div>
      <div class="win" style="background:{c['surface.base']};border-color:{c['window.unfocused']};color:{c['text.primary']}">
        <div class="statuses">{status}</div>
        <p class="small">{status_text}</p>
        <div class="term" style="background:{c['term.bg']};color:{c['term.fg']}">$ {term}</div>
      </div>
    </div>
    <div class="urgent" style="border-color:{c['window.urgent']};background:{c['surface.overlay']};color:{c['text.primary']}">urgent border · overlay</div>
  </div>
  <div class="cats">{cats}</div>
  <details><summary>All {len([v for v in t.t.values() if isinstance(v, str)])} colours</summary><table>{tokens}</table></details>
</article>"""

    families = [("neutral", "Grays"), ("blue", "Blues"), ("purple", "Purples — the Kognog colours"),
                ("green", "Greens"), ("pink", "Pinks"), ("red", "Reds"), ("multi", "Multicolor")]
    groups = ""
    for fam, title in families:
        cards = "".join(card(t) for t in themes if t.r["family"] == fam)
        groups += f'<section><h2>{title}</h2><div class="grid">{cards}</div></section>'
    brand = "".join(f'<span class="b"><i style="background:{v}"></i>{k} <code>{v}</code></span>' for k, v in BRAND.items())
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>hypeForge Theme Swatches</title>
<style>
:root{{--bg:#f4f4f6;--fg:#1d1d24;--dim:#5a5a66;--card:#ffffff;--line:#d6d6de;--good:#1f7a3a;--bad:#b3261e}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#16161c;--fg:#e6e6ee;--dim:#a2a2b0;--card:#202028;--line:#34343f;--good:#6fd08c;--bad:#ff8a80}}}}
:root[data-theme="dark"]{{--bg:#16161c;--fg:#e6e6ee;--dim:#a2a2b0;--card:#202028;--line:#34343f;--good:#6fd08c;--bad:#ff8a80}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,"Noto Sans",sans-serif;padding:24px 16px 64px}}
main{{max-width:1500px;margin:0 auto}}
h1{{font-size:26px;margin:0 0 4px}} h2{{font-size:18px;margin:32px 0 12px}}
.lead{{color:var(--dim);max-width:75ch}}
.brand{{display:flex;flex-wrap:wrap;gap:8px 16px;margin:12px 0}}
.b{{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:var(--dim)}}
.b i,.cats i,td i{{display:inline-block;width:14px;height:14px;border-radius:3px;border:1px solid rgba(127,127,127,.35)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}}
.theme{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px;min-width:0}}
.theme header{{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-bottom:8px}}
.theme h3{{margin:0;font-size:15px}}
.tag{{font-size:11px;color:var(--dim);border:1px solid var(--line);border-radius:99px;padding:0 7px}}
.score{{font-size:11px;margin-left:auto}} .good{{color:var(--good)}} .bad{{color:var(--bad);font-weight:700}}
.desk{{border-radius:6px;overflow:hidden;padding-bottom:8px}}
.bar{{display:flex;justify-content:space-between;gap:4px;font-size:11px;height:24px;align-items:stretch}}
.seg{{display:flex;align-items:center;gap:4px;padding:0 6px;white-space:nowrap}}
.seg b{{display:inline-block;min-width:16px;text-align:center;font-size:10px;line-height:16px;padding:0 2px}}
.emb{{display:inline-flex;flex-direction:column;gap:1px;margin-right:3px}} .emb u{{display:block;width:11px;height:5px}}
.dot{{font-size:10px}}
.wins{{display:grid;grid-template-columns:1.3fr 1fr;gap:8px;padding:8px 8px 0}}
.win{{border:2px solid;padding:6px;font-size:12px;min-width:0}}
.panel{{border:1px solid;padding:6px}}
.win p{{margin:2px 0;font-size:11px}} .small{{font-size:10px!important}}
.row{{padding:2px 4px;margin:4px 0;font-size:11px}}
.btns{{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-top:4px}}
.btn{{padding:2px 8px;font-size:11px;font-weight:600;border-radius:4px}} .ghost{{border:1px solid}}
.btns a{{font-size:11px;text-decoration:underline}}
.statuses{{display:flex;flex-wrap:wrap;gap:4px}} .chip{{font-size:10px;padding:1px 5px;border-radius:3px;font-weight:600}}
.term{{margin-top:6px;padding:4px;font:10px/1.4 ui-monospace,"JetBrainsMono Nerd Font",monospace;white-space:normal;word-break:break-word}}
.urgent{{margin:8px 8px 0;border:2px solid;padding:3px 6px;font-size:11px}}
.cats{{display:flex;gap:4px;margin:8px 0 4px}}
details{{font-size:12px;color:var(--dim)}} details table{{border-collapse:collapse;margin-top:6px}}
td{{padding:1px 6px 1px 0;font:11px ui-monospace,monospace}}
.filters{{display:flex;gap:6px;flex-wrap:wrap;margin:16px 0 0}}
.filters button{{background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:99px;padding:4px 12px;font:inherit;cursor:pointer}}
.filters button[aria-pressed="true"]{{border-color:var(--fg);font-weight:600}}
@media (max-width:420px){{.wins{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>hypeForge — 23 colour themes</h1>
<p class="lead">Generated by <code>generate.py</code> from OKLCH recipes; every text and border pair is measured (WCAG 2.2 and APCA) and nudged until it passes. Each card is a tiny desktop: the bar on top (its shaded areas, the workspace numbers, the clock), a focused window (accent border) and an unfocused one, the status colours, a terminal line, and the eight category colours. Open “All colours” for the hex values.</p>
<div class="brand">{brand}</div>
<div class="filters" role="group" aria-label="Show tone">
<button aria-pressed="true" data-f="all">All</button><button aria-pressed="false" data-f="white light">Light</button>
<button aria-pressed="false" data-f="mid">Mid</button><button aria-pressed="false" data-f="dark black">Dark</button></div>
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
set $hf_on_accent {c['accent.on']}

# class                 title-bar edge  title-bar     title text    next-split    window border
client.focused          $hf_active      $hf_titlebar  $hf_text      $hf_active    $hf_active
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
border-color={c['border.subtle']}
progress-color=over {c['selection.bg']}

[urgency=low]
border-color={c['surface.overlay']}
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
selection-match={hx('accent.text')}ff
border={hx('border.subtle')}ff
""")
    gtk_pairs = {
        "accent_color": "accent.text", "accent_bg_color": "accent.base", "accent_fg_color": "accent.on",
        "window_bg_color": "surface.base", "window_fg_color": "text.primary",
        "view_bg_color": "surface.base", "view_fg_color": "text.primary",
        "headerbar_bg_color": "bar.bg", "headerbar_fg_color": "bar.fg", "headerbar_border_color": "border.subtle",
        "headerbar_backdrop_color": "bar.bg", "sidebar_bg_color": "bar.bg", "sidebar_fg_color": "text.primary",
        "sidebar_backdrop_color": "bar.bg",
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
# skin already uses these names, so only this block changes per theme.
[aliases]
    Crust = {c['surface.sunken']}
    Mantle = {c['bar.bg']}
    Base = {c['surface.base']}
    Surface0 = {c['surface.raised']}
    Surface1 = {c['selection.bg']}
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
    Mauve = {c['accent.text']}
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
    Bar = Mantle
    BarFg = Subtext1
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
    ap.add_argument("--render", nargs="*", default=["dark-purple", "purple", "white"],
                    help="themes that get example program files in render/")
    a = ap.parse_args()

    themes = [Theme(r).build().check() for r in THEMES]
    assert len(themes) == 23, len(themes)
    write_toml(themes)
    write_report(themes)
    write_swatches(themes)
    for slug in a.render:
        render(next(t for t in themes if t.r["slug"] == slug))

    # read our own TOML back: a file the theme app cannot parse is worse than none
    data = tomllib.loads((HERE / "palettes.toml").read_text())
    assert len(data["themes"]) == 23
    for t in themes:
        tomllib.loads((HERE / "themes" / t.r["slug"] / "theme.toml").read_text())

    fails = [(t.r["slug"], r) for t in themes for r in t.required_fails]
    total = sum(len([r for r in t.rows if r["required"]]) for t in themes)
    print(f"23 themes · {total} required pairs · {total - len(fails)} pass · {len(fails)} fail · "
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
