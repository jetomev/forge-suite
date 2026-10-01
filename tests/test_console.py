"""Console mode (issue #1): detection, character swaps, colour roles, layout, F1.

Run: python -m unittest discover -s tests -v
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from rich.cells import cell_len
from rich.console import Console
from textual.scrollbar import ScrollBar, ScrollBarRender

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "examples"))

from forgekit import ForgeApp, console_mode, console_text, css_variables, glyph  # noqa: E402
from forgekit.console import (  # noqa: E402
    FALLBACKS, GLYPHS, ConsoleGlyphFilter, ConsoleScrollBarRender, drawable, set_console,
)
from forgekit.menu import MenuDropdown  # noqa: E402
from forgekit.theme import ROLES, SHAPES  # noqa: E402

import demo  # noqa: E402

SIZE = (100, 30)


class Detection(unittest.TestCase):
    def test_term_linux_means_console(self):
        self.assertTrue(console_mode({"TERM": "linux"}))

    def test_terminal_windows_are_not_console(self):
        for term in ("xterm-256color", "alacritty", "xterm-kitty", "tmux-256color", ""):
            self.assertFalse(console_mode({"TERM": term}), term)

    def test_override_forces_on(self):
        self.assertTrue(console_mode({"TERM": "xterm-256color", "FORGE_ASCII": "1"}))

    def test_override_forces_off(self):
        self.assertFalse(console_mode({"TERM": "linux", "FORGE_ASCII": "0"}))

    def test_unknown_override_value_falls_back_to_term(self):
        self.assertTrue(console_mode({"TERM": "linux", "FORGE_ASCII": "maybe"}))


class CharacterSwaps(unittest.TestCase):
    def test_every_fallback_is_drawable_and_no_wider(self):
        for ch, rep in FALLBACKS.items():
            self.assertTrue(all(drawable(c) for c in rep), f"{ch!r} -> {rep!r} not drawable")
            self.assertLessEqual(cell_len(rep), cell_len(ch), f"{ch!r} -> {rep!r} wider")

    def test_swaps_keep_the_width(self):
        for text in ("╭─ Dashboard ─╮", "⚡ Mining ⛏ |", "⏳ staged |", "✓ ok — done…", "Ángel Ó×©"):
            out = console_text(text)
            self.assertEqual(cell_len(out), cell_len(text), text)
            self.assertTrue(all(drawable(c) for c in out), out)

    def test_rounded_corners_become_straight(self):
        self.assertEqual(console_text("╭╮╰╯"), "┌┐└┘")

    def test_accents_fall_back_to_the_letter(self):
        self.assertEqual(console_text("Ángel Ó"), "Angel O")

    def test_letters_the_font_has_are_kept(self):
        self.assertEqual(console_text("señor ñ é ü"), "señor ñ é ü")

    def test_glyph_table_follows_the_mode(self):
        try:
            set_console(True)
            for name, (_fancy, plain) in GLYPHS.items():
                self.assertEqual(glyph(name), plain)
                self.assertTrue(all(drawable(c) for c in plain), name)
            set_console(False)
            self.assertEqual(glyph("ok"), "✓")
        finally:
            set_console(False)


class ColourRoles(unittest.TestCase):
    def test_focus_colour_is_unique_on_the_console(self):
        # F-13: no other button state may share the focused button's colour
        focus = ROLES["focus-bg"][1]
        for role in ("button-bg", "primary-bg", "error-bg", "button-hover"):
            self.assertNotEqual(ROLES[role][1], focus, role)

    def test_active_item_is_not_cyan_on_the_console(self):
        # its underlined letter is drawn cyan there, and would disappear
        self.assertNotIn("cyan", ROLES["active-bg"][1])

    def test_both_modes_define_the_same_roles(self):
        self.assertEqual(set(css_variables(True)), set(css_variables(False)))

    def test_window_mode_keeps_catppuccin(self):
        v = css_variables(False)
        self.assertEqual(v["forge-bg"], "#1e1e2e")
        self.assertEqual(v["forge-accent"], "#89b4fa")
        self.assertEqual(v["forge-round"], "round")

    def test_console_uses_only_console_colours(self):
        for role, (_window, console) in ROLES.items():
            self.assertTrue(console.startswith("ansi_"), f"{role}: {console}")

    def test_console_backgrounds_are_never_bright(self):
        # bright backgrounds are not reliable on a text console
        for role, (_window, console) in ROLES.items():
            if role.endswith("-bg") or role in ("bg", "surface", "raised", "scroll-track", "scroll-thumb",
                                                 "scroll-hover", "scroll-drag", "button-bg"):
                self.assertNotIn("bright", console, role)

    def test_console_has_no_rounded_corners_or_bold_on_blocks(self):
        v = css_variables(True)
        self.assertEqual(v["forge-round"], "solid")
        self.assertEqual(v["forge-strong"], "none")

    def test_shapes_cover_both_modes(self):
        for name, pair in SHAPES.items():
            self.assertEqual(len(pair), 2, name)


def _region(app, selector):
    return app.query_one(selector).region


class AppInBothModes(unittest.IsolatedAsyncioTestCase):
    async def _layout(self, console: bool):
        app = demo.BitlaForgeDemo(console=console)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            return {
                "title": _region(app, "#forge-title"),
                "menubar": _region(app, "#forge-menubar"),
                "work": _region(app, "#forge-work"),
                "items": [(_region(app, f"#menu-{m['id']}").x, _region(app, f"#menu-{m['id']}").width)
                          for m in demo.MENU],
            }

    async def test_layout_is_the_same_in_both_modes(self):
        window, console = await self._layout(False), await self._layout(True)
        for key in ("title", "menubar", "work"):
            self.assertEqual(window[key], console[key], key)
        self.assertEqual((window["title"].y, window["menubar"].y, window["work"].y), (0, 1, 2))
        # menu items: identical up to Help; on the console Help carries " F1"
        # (F-12), 3 cells wider, and Quit moves right by those 3 cells
        ids = [m["id"] for m in demo.MENU]
        h = ids.index("help")
        self.assertEqual(window["items"][:h], console["items"][:h])
        self.assertEqual(console["items"][h][1], window["items"][h][1] + 3)
        for (wx, ww), (cx, cw) in zip(window["items"][h + 1:], console["items"][h + 1:]):
            self.assertEqual((cx, cw), (wx + 3, ww))

    async def test_help_shows_f1_on_the_console_only(self):
        # F-12: Ctrl+H never reaches an app on a text console; the bar says F1
        for console, expected in ((True, True), (False, False)):
            app = demo.BitlaForgeDemo(console=console)
            async with app.run_test(size=SIZE):
                label = str(app.query_one("#menu-help").render())
                self.assertEqual("F1" in label, expected, label)

    async def test_focus_has_its_own_colour_on_the_console(self):
        # F-13: Tab must visibly move focus; the primary button must not look focused
        from textual.app import ComposeResult
        from textual.containers import Horizontal
        from textual.widgets import Button

        class TwoButtons(ForgeApp):
            APP_NAME = "two"
            MENU = [{"id": "one", "title": "One", "kind": "section"},
                    {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"}]

            def compose_sections(self) -> ComposeResult:
                with Horizontal(id="sec-one"):
                    yield Button("Start", id="a", variant="primary")
                    yield Button("Test", id="b")

        app = TwoButtons(console=True)
        async with app.run_test(size=SIZE) as pilot:
            a, b = app.query_one("#a"), app.query_one("#b")
            a.focus()
            await pilot.pause()
            focus_colour = a.styles.background
            await pilot.press("tab")
            await pilot.pause()
            self.assertTrue(b.has_focus)
            self.assertEqual(b.styles.background, focus_colour)       # focus moved with its colour
            self.assertNotEqual(a.styles.background, focus_colour)    # and left the primary button
            self.assertNotEqual(a.styles.background, b.styles.background)

    async def test_console_app_switches_everything_on(self):
        app = demo.BitlaForgeDemo(console=True)
        async with app.run_test(size=SIZE):
            self.assertTrue(app.forge_console)
            # regression: the flag must not live in Textual's own "console" attribute
            self.assertIsInstance(app.console, Console)
            self.assertIs(ScrollBar.renderer, ConsoleScrollBarRender)
            self.assertTrue(any(isinstance(f, ConsoleGlyphFilter) for f in app.get_line_filters()))
            self.assertEqual(app.get_css_variables()["forge-bg"], "ansi_black")
            self.assertTrue(app.native_ansi_color)

    async def test_window_app_switches_nothing(self):
        app = demo.BitlaForgeDemo(console=False)
        async with app.run_test(size=SIZE):
            self.assertFalse(app.forge_console)
            self.assertIs(ScrollBar.renderer, ScrollBarRender)
            self.assertFalse(any(isinstance(f, ConsoleGlyphFilter) for f in app.get_line_filters()))
            self.assertEqual(app.screen.styles.background.hex.lower(), "#1e1e2e")

    async def test_f1_opens_help(self):
        # F-10: a text console sends Ctrl+H as Backspace, so F1 must open Help too
        for console in (False, True):
            app = demo.BitlaForgeDemo(console=console)
            async with app.run_test(size=SIZE) as pilot:
                await pilot.press("f1")
                await pilot.pause()
                self.assertIsInstance(app.screen, MenuDropdown, f"console={console}")


@unittest.skipUnless(importlib.util.find_spec("pyte") and shutil.which("python3"), "needs python-pyte")
class ConsolePreview(unittest.TestCase):
    """The real thing: the demo in a pseudo-terminal with TERM=linux."""

    def _preview(self, keys: str, tmp: str) -> subprocess.CompletedProcess:
        env = dict(os.environ, PYTHONPATH=str(ROOT))
        env.pop("FORGE_ASCII", None)
        return subprocess.run(
            [sys.executable, str(ROOT / "tools" / "console-preview.py"), "--keys", keys, "--settle", "2.5",
             "--out", tmp, "--", sys.executable, str(ROOT / "examples" / "demo.py")],
            env=env, capture_output=True, text=True, timeout=60,
        )

    def test_every_view_draws_only_console_characters(self):
        import tempfile
        views = {"shell": "wait:0.1", "menu": "ctrl+c wait:1", "edit": "ctrl+c wait:1 e wait:1.5",
                 "about": "f1 wait:1 a wait:1.5"}
        with tempfile.TemporaryDirectory() as d:
            for name, keys in views.items():
                r = self._preview(keys, os.path.join(d, f"{name}.png"))
                self.assertEqual(r.returncode, 0, f"{name}: {r.stdout}{r.stderr}")
                self.assertIn("every character on screen is in the console font", r.stdout, name)
                # the console shows underline as cyan and italic as green: no letter
                # may vanish into its background (the VM found "D" of an active item)
                self.assertIn("every character is visible against its background", r.stdout, name)


if __name__ == "__main__":
    unittest.main()
