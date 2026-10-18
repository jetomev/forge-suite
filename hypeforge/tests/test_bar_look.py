"""One look for the status pieces on every style's bar (Javier, 2026-10-17: on the other styles "the icons look
terrible. Some are over the others, they aren't consistent with icon size, separation, colors… Let's add the
icons drives, cpu, gpu, memory that we are using here in rice")."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import tomllib
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STYLES = sorted(p.parent.name for p in (REPO / "styles").glob("*/style.toml"))
SYSTEM = ["custom/disk", "custom/memory", "custom/temperature", "custom/gpu", "custom/cpu"]


def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


spacing = load("bar_spacing", REPO / "scripts/bar-spacing.py")
hb = load("hb_look", REPO / "applets/bar/hypeforge-bar")


def layout(slug: str) -> list[str]:
    path = REPO / ("sway/waybar/config.jsonc" if slug == "classic" else f"styles/{slug}/bar/config.jsonc")
    cfg = json.loads(hb.strip_comments(path.read_text()))
    found = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ("modules-left", "modules-center", "modules-right", "modules") and isinstance(v, list):
                    found.extend(v)
                else:
                    walk(v)
        elif isinstance(node, list):
            for n in node:
                walk(n)
    walk(cfg)
    return found


class EveryStyle(unittest.TestCase):
    def test_every_style_has_its_bar_settings(self):
        for slug in STYLES:
            bar = tomllib.loads((REPO / f"styles/{slug}/style.toml").read_text()).get("bar", {})
            for key in ("font", "icon_size", "tray_size", "gap", "icon_colour"):
                self.assertIn(key, bar, f"{slug}: [bar] {key}")

    def test_every_style_shows_the_system_pieces_in_the_rice_order_and_no_usb_icon(self):
        for slug in STYLES:
            mods = layout(slug)
            where = [mods.index(m) for m in SYSTEM if m in mods]
            self.assertEqual(len(where), 5, f"{slug}: all five system pieces")
            self.assertEqual(where, sorted(where), f"{slug}: disk · memory · temperature · graphics card · processor")
            self.assertNotIn("custom/drives", mods, f"{slug}: the disk piece took the USB icon's job (D-109)")

    def test_every_stylesheet_carries_its_rules_as_the_script_writes_them(self):
        """A hand edit, or a [bar] change without running the script, shows up here."""
        for slug in STYLES:
            text = spacing.stylesheet(slug).read_text()
            self.assertIn("\n".join(spacing.block(slug)), text, f"{slug}: run scripts/bar-spacing.py --style {slug}")


class Fast(unittest.TestCase):
    def test_no_piece_starts_a_program_straight_from_the_bar(self):
        """2026-10-17, the bar's timing (1.8 s → 0.35 s): every screen's bar runs its pieces itself, and the tray's
        ten picture pieces held each bar's start back while ten Python programs started. A piece reads an answer
        kept ready (`cat`), or goes through applets/common/hfpiece (one run for every screen)."""
        mods = json.loads(hb.strip_comments((REPO / "sway/waybar/modules.jsonc").read_text()))
        for name, m in mods.items():
            if isinstance(m, dict) and m.get("exec"):
                cmd = m["exec"]
                self.assertTrue(cmd.startswith("cat ") or "/common/hfpiece " in cmd, f"{name}: {cmd[:70]}")


if __name__ == "__main__":
    unittest.main()
