"""Readable in every theme: text and icons stand out from what they sit on, for every style × all 25
colour themes (WCAG contrast: 4.5 for text, 3 for icons and dimmed text).

F-68 (Javier, 2026-10-11, themeForge's first run: "colors, only mocha and 'red'"): in light themes
the Rice drew the band's near-white text on its near-white areas, Classic dark text on its dark
band, macOS's Dock near-white icons on white. Each picked a text colour made for another background.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
loader = importlib.machinery.SourceFileLoader("ht_contrast", str(HERE / "applets/theme/hypeforge-theme"))
ht = importlib.util.module_from_spec(importlib.util.spec_from_loader("ht_contrast", loader))
loader.exec_module(ht)
VAR = {m.group(1): m.group(2) for m in
       re.finditer(r"@define-color\s+(\w+)\s+\{\{\s*(\w+)", (HERE / "themes/templates/colors.css.tmpl").read_text())}

# what each style's bar stylesheet puts on what (background, text, the least contrast)
BAR_PAIRS = {
    "rice": [("hf_island", "hf_text", 4.5), ("hf_island", "hf_icon", 3), ("hf_island", "hf_subtext", 3),
             ("hf_pill_active", "hf_pill_active_text", 4.5), ("hf_island", "hf_pill_busy", 3)],
    "windows-11": [("hf_bar", "hf_text", 4.5)],
    "kde": [("hf_bar", "hf_text", 4.5)],
    "cosmic": [("hf_bar", "hf_text", 4.5), ("hf_island", "hf_text", 4.5)],
    "macos": [("hf_menubar_bg", "hf_menubar_text", 4.5), ("hf_island", "hf_menubar_text", 3)],
    "mac-os-9": [("hf_menubar_bg", "hf_menubar_text", 4.5)],
    "classic": [("hf_bar", "hf_text", 4.5)],
}
# every place the templates put a text colour on a background
ROLE_PAIRS = [("bar_bg", "bar_fg", 4.5), ("list_bg", "list_text", 4.5), ("list_selection", "list_selection_text", 4.5),
              ("panel_bg", "panel_text", 4.5), ("panel_bg", "panel_text_dim", 3),
              ("panel_tile", "panel_tile_text", 4.5), ("panel_tile_on", "panel_tile_on_text", 4.5),
              ("panel_selected", "panel_selected_text", 4.5), ("menu_background", "menubar_text", 4.5),
              ("menu_highlight", "menu_highlight_text", 4.5), ("menubar_background", "menubar_text", 4.5),
              ("titlebar_bg", "title_text", 4.5), ("lock_bg", "lock_text", 4.5), ("gtk_window_bg", "gtk_fg", 4.5),
              ("gtk_accent", "gtk_accent_fg", 4.5), ("gtk_header_bg", "gtk_header_fg", 4.5),
              ("gtk_sidebar_bg", "gtk_sidebar_fg", 4.5), ("pill_active", "pill_active_text", 4.5)]


def luminance(h: str) -> float:
    c = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


class Readable(unittest.TestCase):
    def failures(self, styles=None):
        out = []
        for slug, style in ht.styles().items():
            if styles and slug not in styles:
                continue
            for name, theme in ht.themes().items():
                for bg, fg, need in BAR_PAIRS.get(slug, []):
                    b, f = ht.resolve(VAR[bg], style, theme), ht.resolve(VAR[fg], style, theme)
                    if contrast(b, f) < need:
                        out.append(f"{slug} · {name}: bar {fg} on {bg} {contrast(b, f):.2f}")
                for bg, fg, need in ROLE_PAIRS:
                    b, f = ht.resolve(bg, style, theme), ht.resolve(fg, style, theme)
                    if contrast(b, f) < need:
                        out.append(f"{slug} · {name}: {fg} on {bg} {contrast(b, f):.2f}")
        return out

    def test_every_style_in_every_theme_is_readable(self):
        bad = self.failures()
        self.assertEqual(bad, [], f"{len(bad)} unreadable pairs, e.g. {bad[:5]}")

    def test_the_check_catches_text_made_for_another_background(self):
        """In the failing direction: the Rice's old pairing (the band's text on its areas) is caught."""
        rice = dict(ht.styles()["rice"])
        rice["roles"] = {k: v for k, v in rice["roles"].items() if k not in ("bar_fg", "bar_fg_dim")}
        light = ht.themes()["light-pink"]
        self.assertLess(contrast(ht.resolve("island_background", rice, light), ht.resolve("bar_fg", rice, light)), 4.5)

    def test_every_style_has_its_bar_pairs_listed(self):
        self.assertEqual(set(BAR_PAIRS), set(ht.styles()), "a new style needs its bar's pairs here")


if __name__ == "__main__":
    unittest.main()
