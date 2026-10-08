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


if __name__ == "__main__":
    unittest.main()
