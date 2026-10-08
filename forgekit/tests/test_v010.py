"""forgekit 0.10.0 — the terminal pane passes the mouse to the program inside it when that program
asks for mouse reporting; an app inside hypeForge Settings hides its Quit (forge-suite #45)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from textual.app import App  # noqa: E402
from textual.widgets import Static  # noqa: E402

from forgekit import ForgeApp, FORGE_CSS, css_variables, console_mode  # noqa: E402
from forgekit.terminal import TerminalPane  # noqa: E402

# A tiny program: turns mouse reporting on (clicks + SGR), then copies every byte it reads to a file.
ECHO = r'''
import os, sys, tty
tty.setraw(0)                     # like every real TUI: bytes arrive as they come, no waiting for Enter
sys.stdout.write("\x1b[?1000h\x1b[?1006h"); sys.stdout.flush()
out = open(sys.argv[1], "ab")
while True:
    b = os.read(0, 64)
    if not b: break
    out.write(b); out.flush()
'''


class PaneHost(App):
    CSS = FORGE_CSS + "TerminalPane { height: 20; }"

    def get_css_variables(self):
        return {**super().get_css_variables(), **css_variables(console_mode())}

    def compose(self):
        yield TerminalPane(id="pane")


class MouseIntoThePane(unittest.IsolatedAsyncioTestCase):
    async def test_a_click_reaches_the_program_as_an_sgr_mouse_report(self):
        d = Path(tempfile.mkdtemp())
        prog, got = d / "echo.py", d / "got.bin"
        prog.write_text(ECHO)
        app = PaneHost()
        async with app.run_test(size=(100, 30)) as pilot:
            pane = app.query_one("#pane", TerminalPane)
            pane.start([sys.executable, str(prog), str(got)])
            for _ in range(40):                      # until the program has switched reporting on
                await pilot.pause(0.05)
                if (1000 << 5) in pane.screen_vt.mode and (1006 << 5) in pane.screen_vt.mode:
                    break
            self.assertEqual(pane._mouse_mode(), 1000, "the program asked for clicks")
            await pilot.click("#pane", offset=(10, 4))   # column 11, row 5 in 1-based terms
            await pilot.pause(0.3)
            data = got.read_bytes() if got.exists() else b""
            self.assertIn(b"\x1b[<0;11;5M", data, f"press at the right cell; got {data!r}")
            self.assertIn(b"\x1b[<0;11;5m", data, "and its release")
            pane.terminate()

    async def test_no_report_when_the_program_did_not_ask(self):
        d = Path(tempfile.mkdtemp())
        got = d / "got.bin"
        app = PaneHost()
        async with app.run_test(size=(100, 30)) as pilot:
            pane = app.query_one("#pane", TerminalPane)
            pane.start([sys.executable, "-c", f"import os; open({str(got)!r},'ab').write(os.read(0, 64))"])
            await pilot.pause(0.3)
            self.assertEqual(pane._mouse_mode(), 0)
            await pilot.click("#pane", offset=(3, 3))
            await pilot.pause(0.3)
            self.assertFalse(got.exists() and got.read_bytes(), "a plain program gets no mouse bytes")
            pane.terminate()


class QuitHiddenInsideSettings(unittest.IsolatedAsyncioTestCase):
    class Tiny(ForgeApp):
        APP_NAME = "tiny"
        MENU = [{"id": "one", "title": "One", "kind": "section"},
                {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"}]

        def compose_sections(self):
            yield Static("ok", id="sec-one")

    async def test_quit_goes_under_the_flag_and_ctrl_q_still_closes(self):
        old = os.environ.get("HYPEFORGE_SETTINGS")
        os.environ["HYPEFORGE_SETTINGS"] = "1"
        try:
            app = self.Tiny()
            async with app.run_test(size=(80, 20)) as pilot:
                await pilot.pause()
                self.assertEqual(len(app.query("#menu-quit")), 0, "no Quit in the bar inside Settings")
                self.assertEqual(len(app.query("#menu-one")), 1)
                await pilot.press("ctrl+q")
                await pilot.pause()
            self.assertIsNotNone(app.return_code if hasattr(app, "return_code") else 0, "the app closed")
        finally:
            if old is None:
                os.environ.pop("HYPEFORGE_SETTINGS", None)
            else:
                os.environ["HYPEFORGE_SETTINGS"] = old

    async def test_quit_stays_without_the_flag(self):
        os.environ.pop("HYPEFORGE_SETTINGS", None)
        app = self.Tiny()
        async with app.run_test(size=(80, 20)) as pilot:
            await pilot.pause()
            self.assertEqual(len(app.query("#menu-quit")), 1)



class ModernKeysIntoThePane(unittest.IsolatedAsyncioTestCase):
    """Ctrl+H reaches a program that asked for the modern keyboard protocol as ESC [ 104 ; 5 u,
    and a plain program still gets the old single byte."""

    PROG = r'''
import os, sys, tty
tty.setraw(0)
if sys.argv[2] == "modern": sys.stdout.write("\x1b[>1u"); sys.stdout.flush()
out = open(sys.argv[1], "ab")
while True:
    b = os.read(0, 64)
    if not b: break
    out.write(b); out.flush()
'''

    async def run_prog(self, kind: str) -> bytes:
        d = Path(tempfile.mkdtemp())
        prog, got = d / "p.py", d / "got.bin"
        prog.write_text(self.PROG)
        app = PaneHost()
        async with app.run_test(size=(100, 30)) as pilot:
            pane = app.query_one("#pane", TerminalPane)
            pane.start([sys.executable, str(prog), str(got), kind])
            for _ in range(40):
                await pilot.pause(0.05)
                if pane.kitty_keys or kind == "plain" and pane.running:
                    break
            await pilot.pause(0.2)
            pane.focus()
            await pilot.press("ctrl+h")
            await pilot.pause(0.3)
            pane.terminate()
        return got.read_bytes() if got.exists() else b""

    async def test_modern_program_gets_ctrl_h_as_csi_u(self):
        self.assertIn(b"\x1b[104;5u", await self.run_prog("modern"))

    async def test_plain_program_gets_the_old_byte(self):
        data = await self.run_prog("plain")
        self.assertIn(b"\x08", data)
        self.assertNotIn(b"[104;5u", data)


# ── #47: a menu accelerator pressed while a dropdown is open toggles, never stacks ─────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "examples"))
import demo  # noqa: E402
from forgekit.menu import MenuDropdown  # noqa: E402


class OneDropdownAtATime(unittest.IsolatedAsyncioTestCase):
    """Found by Javier 2026-10-08 00:55: Ctrl+H, Ctrl+H stacked a second Help dropdown on the first
    (the app behind went darker each time) and Esc had to be pressed once per dropdown."""

    def dropdowns(self, app) -> list:
        return [s for s in app.screen_stack if isinstance(s, MenuDropdown)]

    async def test_the_same_accelerator_twice_closes_it(self):
        app = demo.BitlaForgeDemo(console=False)
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.press("ctrl+h")
            await pilot.pause()
            self.assertEqual(len(self.dropdowns(app)), 1, "the first press opens Help")
            await pilot.press("ctrl+h")
            await pilot.pause()
            self.assertEqual(self.dropdowns(app), [], "the second press closes it")
            self.assertEqual(len(app.screen_stack), 1)

    async def test_another_menu_replaces_the_open_one(self):
        app = demo.BitlaForgeDemo(console=False)
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.press("ctrl+h")
            await pilot.pause()
            await pilot.press("ctrl+c")
            await pilot.pause()
            open_ = self.dropdowns(app)
            self.assertEqual(len(open_), 1, "one dropdown, never two")
            self.assertEqual(open_[0].menu_id, "config")

    async def test_a_section_key_closes_the_dropdown_and_switches(self):
        app = demo.BitlaForgeDemo(console=False)
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.press("ctrl+h")
            await pilot.pause()
            await pilot.press("ctrl+l")
            await pilot.pause()
            self.assertEqual(self.dropdowns(app), [], "nothing left floating over the new page")
            self.assertTrue(app.query_one("#menu-log").has_class("active"))

    async def test_one_escape_is_always_enough(self):
        app = demo.BitlaForgeDemo(console=False)
        async with app.run_test(size=(100, 30)) as pilot:
            for key in ("ctrl+h", "ctrl+h", "ctrl+h", "ctrl+c", "ctrl+h"):
                await pilot.press(key)
                await pilot.pause()
            self.assertLessEqual(len(self.dropdowns(app)), 1)
            await pilot.press("escape")
            await pilot.pause()
            self.assertEqual(len(app.screen_stack), 1)

    async def test_clicking_titles_while_a_dropdown_is_open(self):
        app = demo.BitlaForgeDemo(console=False)
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.click("#menu-help")
            await pilot.pause()
            self.assertEqual(len(self.dropdowns(app)), 1)
            config_title = app.screen_stack[0].query_one("#menu-config").region
            await pilot.click(offset=(config_title.x + 1, config_title.y))   # another title: switch
            await pilot.pause()
            open_ = self.dropdowns(app)
            self.assertEqual([d.menu_id for d in open_], ["config"])
            config_title = app.screen_stack[0].query_one("#menu-config").region
            await pilot.click(offset=(config_title.x + 1, config_title.y))   # its own title: close
            await pilot.pause()
            self.assertEqual(self.dropdowns(app), [])


if __name__ == "__main__":
    unittest.main()
