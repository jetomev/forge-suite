"""v0.6.0: a tool's run and its password, inside the app.

Every test runs a small stand-in script in a real pseudo-terminal, headless
through Textual's Pilot. Nothing is installed and no real password is used:
the stand-in for sudo calls $SUDO_ASKPASS exactly as sudo -A does.
Run: python -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import os
import stat
import tempfile
import time
import unittest
from pathlib import Path

from textual.widgets import Button, Input, Static

from forgekit import ForgeApp, PasswordDialog, PasswordField, RunWindow, TerminalPane
from forgekit.terminal import ForgeScreen, key_bytes
import pyte


class Host(ForgeApp):
    APP_NAME = "host"
    MENU = [{"id": "home", "title": "Home", "kind": "section"}]

    def compose_sections(self):
        yield Static("home", id="sec-home")


def script(body: str) -> list[str]:
    d = Path(tempfile.mkdtemp())
    f = d / "tool.sh"
    f.write_text("#!/bin/bash\n" + body)
    f.chmod(f.stat().st_mode | stat.S_IEXEC)
    return [str(f)]


async def until(pilot, cond, seconds=6.0):
    end = time.time() + seconds
    while not cond() and time.time() < end:
        await pilot.pause(0.05)
    return cond()


class Keys(unittest.TestCase):
    def test_key_bytes(self):
        self.assertEqual(key_bytes("enter", None), b"\r")
        self.assertEqual(key_bytes("up", None), b"\x1b[A")
        self.assertEqual(key_bytes("up", None, app_cursor=True), b"\x1bOA")
        self.assertEqual(key_bytes("ctrl+c", None), b"\x03")
        self.assertEqual(key_bytes("y", "y"), b"y")
        self.assertIsNone(key_bytes("f12", None), "F12 belongs to the window (folds the screen)")

    def test_alternate_screen_gives_the_output_back(self):
        # an editor or pager (yay's PKGBUILD review) must not wipe what came before
        s = ForgeScreen(40, 5)
        st = pyte.ByteStream(s)
        st.feed(b"before the editor\r\n")
        st.feed(b"\x1b[?1049h\x1b[2J\x1b[Hinside the editor")
        self.assertIn("inside the editor", s.display[0])
        st.feed(b"\x1b[?1049l")
        self.assertIn("before the editor", s.display[0])
        self.assertFalse(any("inside" in l for l in s.display))

    def test_scrollback_keeps_what_scrolled_away(self):
        s = ForgeScreen(20, 3)
        st = pyte.ByteStream(s)
        for i in range(10):
            st.feed(f"line {i}\r\n".encode())
        self.assertGreaterEqual(len(s.history.top), 6)


class InTheApp(unittest.IsolatedAsyncioTestCase):
    async def run_window(self, pilot, app, cmd, **kw):
        result = []
        await app.run_in_app("Working", cmd, callback=result.append, **kw)
        win = lambda: next((s for s in app.screen_stack if isinstance(s, RunWindow)), None)
        # the password window may already be on top of it
        self.assertTrue(await until(pilot, lambda: win() is not None and bool(win().query(TerminalPane))))
        return win(), result

    async def test_colours_progress_and_a_question_answered_with_a_button(self):
        cmd = script(r'''for i in 10 50 100; do printf "\033[1;34m::\033[0m downloading %3s%%\r" $i; sleep 0.05; done
echo; printf ":: Proceed with installation? [Y/n] "; read a; echo "answer=$a"; exit 0''')
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            win, result = await self.run_window(pilot, app, cmd, tool="pacman")
            self.assertTrue(await until(pilot, lambda: win.query_one("#run-question").display))
            self.assertIn("Proceed with installation", str(win.query_one("#run-question-text", Static).render()))
            pane = win.query_one(TerminalPane)
            self.assertTrue(pane.display, "the screen opens for a question: the table is in view")
            self.assertIn(":: downloading 100%", pane.lines_plain(), "a \\r progress line ends as one line")
            await pilot.click("#run-yes")
            self.assertTrue(await until(pilot, lambda: win.status is not None))
            self.assertIn("answer=y", pane.lines_plain())
            self.assertEqual(win.status, 0)
            self.assertFalse(win.query_one("#run-close", Button).disabled)
            await pilot.press("enter")
            self.assertTrue(await until(pilot, lambda: result == [0]))

    async def test_a_menu_question_is_typed_in_the_tools_screen(self):
        # yay asks on the lines above and waits at a bare "==>" (VM, 4 Oct)
        cmd = script(r'''echo "  1 pfetch-git    (Build Files Exist)"; echo "==> Packages to cleanBuild?"
echo "==> [N]one [A]ll [Ab]ort [I]nstalled [No]tInstalled or (1 2 3, 1-3, ^4)"; printf "==> "; read a; echo "got=[$a]"''')
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            win, _ = await self.run_window(pilot, app, cmd, tool="nog")
            self.assertTrue(await until(pilot, lambda: win.query_one("#run-question").display))
            text = str(win.query_one("#run-question-text", Static).render())
            self.assertIn("Packages to cleanBuild?", text)
            self.assertIn("[N]one [A]ll [Ab]ort", text, "yay's choices keep their brackets")
            self.assertIn("Type your answer in nog's screen", text)
            self.assertFalse(win.query_one("#run-yes").display, "not a yes/no question: no Yes/No buttons")
            self.assertTrue(win.query_one(TerminalPane).has_focus, "the keys go to the screen")
            await pilot.press("N", "enter")
            self.assertTrue(await until(pilot, lambda: win.status is not None))
            self.assertIn("got=[N]", win.query_one(TerminalPane).lines_plain())

    async def test_the_password_is_asked_in_the_app(self):
        out = Path(tempfile.mkdtemp()) / "got"
        # a stand-in for sudo -A: runs the helper sudo would, with sudo's prompt
        cmd = script(f'''pw=$("$SUDO_ASKPASS" "[sudo] password for javier: ") || {{ echo cancelled; exit 1; }}
printf %s "$pw" > {out}; echo ok''')
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            win, result = await self.run_window(pilot, app, cmd)
            self.assertTrue(await until(pilot, lambda: isinstance(app.screen, PasswordDialog)))
            text = " ".join(str(s.render()) for s in app.screen.query(Static))
            self.assertIn("Your password (javier)", text)
            self.assertIsInstance(app.screen.query_one("#pw-input"), PasswordField, "typed as dots")
            await pilot.press(*"s3cret!", "enter")
            self.assertTrue(await until(pilot, lambda: win.status is not None))
            self.assertEqual(out.read_text(), "s3cret!")
            bridge = await app.password_bridge()
            env = win._env
            self.assertEqual(env["SUDO_ASKPASS"], bridge.helper)
            self.assertEqual(stat.S_IMODE(os.stat(bridge.dir).st_mode), 0o700, "only this user")
            self.assertEqual(stat.S_IMODE(os.stat(bridge.sock).st_mode), 0o600)
            self.assertNotIn("s3cret", " ".join(win.query_one(TerminalPane).lines_plain()), "never on screen")
        self.assertFalse(os.path.exists(bridge.dir), "removed when the app closes")

    async def test_a_cancelled_password_reaches_the_tool_as_no_password(self):
        cmd = script('''"$SUDO_ASKPASS" "[sudo] password for javier: " >/dev/null || { echo "no password given"; exit 1; }''')
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            win, _ = await self.run_window(pilot, app, cmd)
            self.assertTrue(await until(pilot, lambda: isinstance(app.screen, PasswordDialog)))
            await pilot.press("escape")
            self.assertTrue(await until(pilot, lambda: win.status is not None))
            self.assertEqual(win.status, 1)
            self.assertIn("no password given", win.query_one(TerminalPane).lines_plain())
            self.assertIn("stopped (status 1)", str(win.query_one("#run-status", Static).render()))

    async def test_a_wrong_password_says_try_again(self):
        cmd = script('''"$SUDO_ASKPASS" "[sudo] password for javier: " >/dev/null; sleep 0.2
"$SUDO_ASKPASS" "[sudo] password for javier: " >/dev/null; echo done''')
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            win, _ = await self.run_window(pilot, app, cmd)
            self.assertTrue(await until(pilot, lambda: isinstance(app.screen, PasswordDialog)))
            self.assertFalse(app.screen.query("#pw-again"))
            await pilot.press("x", "enter")
            self.assertTrue(await until(pilot, lambda: isinstance(app.screen, PasswordDialog)
                                        and bool(app.screen.query("#pw-again"))))
            await pilot.press("y", "enter")
            self.assertTrue(await until(pilot, lambda: win.status is not None))

    async def test_steps_from_the_events_file(self):
        ev = Path(tempfile.mkdtemp()) / "events"
        ev.write_text("")
        def line(d):
            return "echo '" + json.dumps(d) + f"' >> {ev}"
        cmd = script("\n".join([
            line({"ev": "steps", "steps": [{"id": "keys", "label": "New keys"}, {"id": "pacman", "label": "Official packages"}]}),
            line({"ev": "step", "id": "keys", "state": "start"}), "sleep 0.2",
            line({"ev": "step", "id": "keys", "state": "done"}),
            line({"ev": "step", "id": "pacman", "state": "start"}),
            "echo '(1/2) upgrading foo'", "sleep 0.3", "echo '(2/2) upgrading bar'",
            line({"ev": "step", "id": "pacman", "state": "done", "detail": "2 packages"}), "sleep 0.3", "exit 0"]))
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            win, _ = await self.run_window(pilot, app, cmd, events_path=str(ev), tool="nog")
            self.assertFalse(win.query_one(TerminalPane).display, "steps view: the screen starts folded")
            self.assertTrue(await until(pilot, lambda: win.status is not None))
            text = str(win.query_one("#run-steps", Static).render())
            self.assertIn("New keys", text)
            self.assertIn("Official packages", text)
            self.assertIn("2 packages", text)
            self.assertEqual([s[2] for s in win._steps], ["done", "done"])
            self.assertFalse(win.query_one(TerminalPane).display, "a good run never needs the screen")
            await pilot.press("f12")
            self.assertTrue(win.query_one(TerminalPane).display, "F12 shows it anyway")

    async def test_a_failed_run_opens_the_screen(self):
        ev = Path(tempfile.mkdtemp()) / "events"
        ev.write_text("")
        cmd = script(f'''echo '{{"ev":"step","id":"pacman","label":"Official packages","state":"start"}}' >> {ev}
echo "error: failed to commit transaction"; exit 1''')
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            win, _ = await self.run_window(pilot, app, cmd, events_path=str(ev), tool="nog")
            self.assertTrue(await until(pilot, lambda: win.status is not None))
            self.assertTrue(win.query_one(TerminalPane).display)
            self.assertIn("nog stopped (status 1)", str(win.query_one("#run-status", Static).render()))

    async def test_ctrl_c_reaches_the_tool(self):
        cmd = script('''trap 'echo interrupted; exit 130' INT; echo ready; while true; do sleep 0.1; done''')
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            win, _ = await self.run_window(pilot, app, cmd)
            pane = win.query_one(TerminalPane)
            self.assertTrue(await until(pilot, lambda: "ready" in pane.lines_plain()))
            pane.focus()
            await pilot.press("ctrl+c")
            self.assertTrue(await until(pilot, lambda: win.status is not None))
            self.assertEqual(win.status, 130)
            self.assertTrue(any("interrupted" in l for l in pane.lines_plain()), "^C, then the tool's own words")

    async def test_the_tool_sees_a_terminal_of_the_panes_size(self):
        cmd = script('''[ -t 0 ] && echo "is a terminal"; echo "cols=$(tput cols) term=$TERM"''')
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            win, _ = await self.run_window(pilot, app, cmd, show_screen=True)
            pane = win.query_one(TerminalPane)
            self.assertTrue(await until(pilot, lambda: win.status is not None))
            lines = pane.lines_plain()
            self.assertIn("is a terminal", lines)
            cols = next(l for l in lines if l.startswith("cols="))
            self.assertEqual(int(cols.split()[0].split("=")[1]), pane.screen_vt.columns)

    async def test_fits_a_text_console(self):
        cmd = script('''printf ":: Proceed with installation? [Y/n] "; read a''')
        app = Host(console=True)
        async with app.run_test(size=(80, 25)) as pilot:
            win, _ = await self.run_window(pilot, app, cmd, tool="pacman")
            self.assertTrue(await until(pilot, lambda: win.query_one("#run-question").display))
            yes = win.query_one("#run-yes", Button)
            self.assertLessEqual(yes.region.right, 80, "the Yes button is on screen at 80 columns")
            await pilot.press("y")
            self.assertTrue(await until(pilot, lambda: win.status is not None))


class ReviewKeys(unittest.IsolatedAsyncioTestCase):
    async def test_the_key_in_a_buttons_label_presses_it(self):
        # nogForge on a text console, 4 Oct: "Install (i)" did nothing on i
        from forgekit import ChangeGroup, ReviewDialog
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            got = []
            app.push_screen(ReviewDialog("Review", [ChangeGroup("Install", "", [("botsay", "-", "1.4.4")])],
                                         buttons=[("Install (i)", "go", True)]), callback=got.append)
            await pilot.pause(0.3)
            await pilot.press("i")
            self.assertTrue(await until(pilot, lambda: got == ["go"]))


class ConsoleGlyphs(unittest.TestCase):
    def test_the_progress_bar_draws_on_the_console(self):
        from forgekit.console import FALLBACKS
        for ch in "╸╺━":
            self.assertIn(ch, FALLBACKS, f"{ch!r} has no console fallback (it showed as ?)")


if __name__ == "__main__":
    unittest.main()
