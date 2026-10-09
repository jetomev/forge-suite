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

from forgekit import (  # noqa: E402
    FORGE_CSS, MENU_HINT, ForgeApp, add_hypeforge_argument, console_mode, css_variables, hypeforge_mode,
    menu_key_clashes,
)
from forgekit.menu import MenuDropdown  # noqa: E402
from textual.binding import Binding  # noqa: E402
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
    """--hypeforge (Javier, 2026-10-08): inside hypeForge Settings the app has no Quit at all —
    not in the bar, not on Q, not on Ctrl+Q. Settings closes it, asking first (SIGUSR1)."""

    class Tiny(ForgeApp):
        APP_NAME = "tiny"
        MENU = [{"id": "one", "title": "One", "kind": "section"},
                {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"}]
        BINDINGS = [Binding("q", "act('quit')", show=False)]
        unsaved = False

        def compose_sections(self):
            yield Static("ok", id="sec-one")

        def before_quit(self):
            return not self.unsaved

    def watch_exit(self, app):
        calls = []
        app.exit = lambda *a, **k: calls.append(1)
        return calls

    def test_the_flag_in_any_case(self):
        self.assertTrue(hypeforge_mode(["--hypeforge"]))
        self.assertTrue(hypeforge_mode(["x", "--hypeForge"]))
        self.assertFalse(hypeforge_mode([]))
        self.assertFalse(hypeforge_mode(["--hypeforgex", "hypeforge"]))

    def test_argparse_takes_both_spellings_and_hides_it(self):
        import argparse
        p = argparse.ArgumentParser()
        add_hypeforge_argument(p)
        self.assertTrue(p.parse_args(["--hypeforge"]).hypeforge)
        self.assertTrue(p.parse_args(["--hypeForge"]).hypeforge)
        self.assertFalse(p.parse_args([]).hypeforge)
        self.assertNotIn("hypeforge", p.format_help().lower())

    async def test_under_the_flag_no_way_to_quit(self):
        app = self.Tiny(hypeforge=True)
        async with app.run_test(size=(80, 20)) as pilot:
            calls = self.watch_exit(app)
            await pilot.pause()
            self.assertEqual(len(app.query("#menu-quit")), 0, "no Quit in the bar")
            for key in ("ctrl+q", "q"):
                await pilot.press(key)
                await pilot.pause()
            app.action_activate("quit")
            app.action_act("quit")
            self.assertEqual(calls, [], "Ctrl+Q, Q and the Quit action all do nothing")

    async def test_without_the_flag_quit_works(self):
        for key in ("ctrl+q", "q"):
            app = self.Tiny(hypeforge=False)
            async with app.run_test(size=(80, 20)) as pilot:
                calls = self.watch_exit(app)
                await pilot.pause()
                self.assertEqual(len(app.query("#menu-quit")), 1)
                await pilot.press(key)
                await pilot.pause()
                self.assertEqual(calls, [1], key)

    async def test_settings_asks_through_sigusr1(self):
        import signal
        for unsaved, expected in ((False, [1]), (True, [])):
            app = self.Tiny(hypeforge=True)
            app.unsaved = unsaved
            async with app.run_test(size=(80, 20)) as pilot:
                calls = self.watch_exit(app)
                await pilot.pause()
                # without a listener SIGUSR1 would end the whole test run, so check that first
                self.assertNotIn(signal.getsignal(signal.SIGUSR1), (signal.SIG_DFL, None),
                                 "the app listens for Settings' question")
                os.kill(os.getpid(), signal.SIGUSR1)
                await pilot.pause(0.1)
                self.assertEqual(calls, expected, f"unsaved={unsaved}: closes only when its own check says so")

    async def test_the_flag_from_the_command_line(self):
        old = sys.argv
        sys.argv = ["tiny", "--hypeForge"]
        try:
            app = self.Tiny()
            async with app.run_test(size=(80, 20)) as pilot:
                await pilot.pause()
                self.assertTrue(app.hypeforge)
                self.assertEqual(len(app.query("#menu-quit")), 0)
        finally:
            sys.argv = old


class MenuKeysForEveryEntry(unittest.IsolatedAsyncioTestCase):
    """Javier, 2026-10-08: every underlined letter is a Ctrl shortcut, and every entry has a
    number in bar order — Help too, Quit not. A menu's number opens its dropdown."""

    class Three(ForgeApp):
        APP_NAME = "three"
        MENU = [{"id": "one", "title": "One", "kind": "section"},
                {"id": "two", "title": "Two", "kind": "section", "acc": "w"},   # "acc" is ignored now: T
                {"id": "more", "title": "More", "kind": "menu", "items": [("Thing", "t", "thing")]},
                {"id": "help", "title": "Help", "kind": "menu", "items": [("About", "a", "about")]},
                {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"}]
        SHOW_HINT_BAR = True
        HINTS = [MENU_HINT, ("?", "all keys")]

        def compose_sections(self):
            from textual.widgets import Input
            yield Static("one", id="sec-one")
            yield Input(id="sec-two")

    def active(self, app):
        return [w.id for w in app.query(".menu-title.active")]

    async def test_ctrl_letters(self):
        app = self.Three()
        async with app.run_test(size=(80, 20)) as pilot:
            await pilot.press("ctrl+t")
            await pilot.pause()
            self.assertEqual(self.active(app), ["menu-two"])
            await pilot.press("ctrl+o")
            await pilot.pause()
            self.assertEqual(self.active(app), ["menu-one"])
            await pilot.press("ctrl+m")
            await pilot.pause()
            self.assertIsInstance(app.screen, MenuDropdown)
            self.assertEqual(app.screen.menu_id, "more")

    async def test_numbers_in_bar_order_help_included(self):
        app = self.Three()
        async with app.run_test(size=(80, 20)) as pilot:
            app.set_focus(None)                  # nothing focused: no field to type into
            await pilot.press("2")
            await pilot.pause()
            self.assertEqual(self.active(app), ["menu-two"])
            app.set_focus(None)
            await pilot.press("3")
            await pilot.pause()
            self.assertEqual(getattr(app.screen, "menu_id", None), "more", "a menu's number opens its dropdown")
            await pilot.press("escape")
            await pilot.pause()
            app.set_focus(None)                  # the field on page two took the focus back
            await pilot.press("4")
            await pilot.pause()
            self.assertEqual(getattr(app.screen, "menu_id", None), "help", "Help has a number")
            await pilot.press("escape")
            await pilot.pause()
            app.set_focus(None)
            await pilot.press("5")
            await pilot.pause()
            self.assertEqual(len(app.screen_stack), 1, "Quit has no number")

    async def test_a_field_keeps_its_digits_but_ctrl_still_moves(self):
        app = self.Three()
        async with app.run_test(size=(80, 20)) as pilot:
            await pilot.press("ctrl+t")
            await pilot.pause()
            field = app.query_one("#sec-two")
            field.focus()
            await pilot.press("1", "2")
            await pilot.pause()
            self.assertEqual(field.value, "12", "digits typed into a field stay there")
            self.assertEqual(self.active(app), ["menu-two"])
            await pilot.press("ctrl+o")
            await pilot.pause()
            self.assertEqual(self.active(app), ["menu-one"], "Ctrl+letter works from inside a field")

    async def test_the_hint_counts_the_entries(self):
        app = self.Three()
        async with app.run_test(size=(80, 20)) as pilot:
            await pilot.pause()
            from forgekit import HintBar
            text = str(app.query_one(HintBar).render())
            self.assertIn("1-4", text)
            self.assertIn("menu", text)
            self.assertNotIn("{menu}", text)

    async def test_ctrl_i_and_ctrl_m_never_steal_tab_and_enter(self):
        # Textual lists Ctrl+I as another name for Tab (and Ctrl+M for Enter), but a binding matches
        # only the key really pressed — checked 2026-10-08, so Identify can have Ctrl+I. This keeps it so.
        class Two(ForgeApp):
            APP_NAME = "two"
            MENU = [{"id": "info", "title": "Info", "kind": "section"},
                    {"id": "main", "title": "Main", "kind": "section"}]

            def compose_sections(self):
                from textual.containers import Vertical
                from textual.widgets import Button
                yield Vertical(Button("a", id="a"), Button("b", id="b"), id="sec-info")
                yield Static("main", id="sec-main")

        app = Two()
        async with app.run_test(size=(80, 20)) as pilot:
            app.query_one("#a").focus()
            await pilot.pause()
            await pilot.press("tab")
            await pilot.pause()
            self.assertEqual(app.focused.id, "b", "Tab still moves to the next button")
            self.assertEqual(self.active(app), ["menu-info"])
            pressed = []
            app.query_one("#b").press = lambda: pressed.append(1)
            await pilot.press("enter")
            await pilot.pause()
            self.assertEqual(self.active(app), ["menu-info"], "Enter did not jump to Main")
            await pilot.press("ctrl+m")
            await pilot.pause()
            self.assertEqual(self.active(app), ["menu-main"], "the real Ctrl+M still works")
            await pilot.press("ctrl+i")
            await pilot.pause()
            self.assertEqual(self.active(app), ["menu-info"], "the real Ctrl+I still works")

    async def test_a_dialog_keeps_its_keys(self):
        # found building grubForge 2.2.0: Ctrl+E in a Rename box switched the page behind it
        from textual.screen import ModalScreen
        from textual.widgets import Input

        class Box(ModalScreen):
            def compose(self):
                yield Input("hello", id="box-field")

        app = self.Three()
        async with app.run_test(size=(80, 20)) as pilot:
            await pilot.pause()
            app.push_screen(Box())
            await pilot.pause()
            field = app.screen.query_one("#box-field")
            field.focus()
            field.cursor_position = 0
            await pilot.press("ctrl+t")          # Two's key
            await pilot.press("ctrl+e")          # end of line
            await pilot.press("3")
            await pilot.pause()
            self.assertEqual(self.active(app), ["menu-one"], "nothing switched behind the box")
            self.assertEqual(field.value, "hello3", "the field got Ctrl+E and the digit")
            self.assertIsInstance(app.screen, Box)

    def test_making_apps_never_grows_the_class_key_table(self):
        class OwnKeys(self.Three):
            BINDINGS = [Binding("ctrl+w", "activate('two')", show=False), Binding("2", "activate('two')", show=False)]

        before = {k: len(v) for k, v in OwnKeys._merged_bindings.key_to_bindings.items()}
        for _ in range(5):
            OwnKeys()
        after = {k: len(v) for k, v in OwnKeys._merged_bindings.key_to_bindings.items()}
        self.assertEqual(after, before)

    async def test_keys_and_manual_are_pages_too(self):
        # Javier, 2026-10-08: "yes, Keys and Manual as pages too"
        pages = [("start", "Start", "# Start\n\nhello"), ("more", "More", "# More\n\nsee [Start](#start)")]
        app = self.Three()
        async with app.run_test(size=(80, 20)) as pilot:
            await pilot.press("ctrl+o")
            await pilot.pause()
            app.action_act("shortcuts")
            await pilot.pause()
            self.assertEqual(len(app.screen_stack), 1, "Keys: no window")
            self.assertEqual(app.query_one("#forge-work").current, "sec-forge-keys")
            self.assertEqual(self.active(app), ["menu-help"])
            await pilot.press("escape")
            await pilot.pause()
            self.assertEqual(app.query_one("#forge-work").current, "sec-one")
            app.show_manual("Three manual", pages, start="more")
            await pilot.pause(0.3)
            self.assertEqual(len(app.screen_stack), 1, "Manual: no window")
            self.assertEqual(app.query_one("#forge-work").current, "sec-forge-manual")
            self.assertEqual(app.query_one("#sec-forge-manual").current, "more", "opened at the page asked for")
            self.assertEqual(self.active(app), ["menu-help"])
            await pilot.press("escape")
            await pilot.pause()
            self.assertEqual(app.query_one("#forge-work").current, "sec-one", "Esc goes back")
            app.show_manual("Three manual", pages, start="start")     # a second time, another page
            await pilot.pause(0.3)
            self.assertEqual(app.query_one("#sec-forge-manual").current, "start")

    async def test_an_apps_letter_keys_sleep_on_reading_pages(self):
        pages = [("start", "Start", "# Start\n\nhello")]

        class Busy(self.Three):
            BINDINGS = [Binding("s", "save", show=False)]
            saved = 0

            def action_save(self):
                self.saved += 1

        app = Busy()
        async with app.run_test(size=(80, 20)) as pilot:
            await pilot.press("ctrl+o")
            await pilot.pause()
            app.set_focus(None)
            await pilot.press("s")
            await pilot.pause()
            self.assertEqual(app.saved, 1, "on an app page the letter works")
            for opener in (lambda: app.action_act("about"), lambda: app.action_act("license"),
                           lambda: app.action_act("shortcuts"), lambda: app.show_manual("M", pages)):
                opener()
                await pilot.pause(0.3)
                await pilot.press("s")
                await pilot.pause()
                self.assertEqual(app.saved, 1, f"S did nothing on {app.query_one('#forge-work').current}")
            await pilot.press("2")                 # numbers still work from a reading page
            await pilot.pause()
            self.assertEqual(self.active(app), ["menu-two"])

    async def test_hypeforge_count_is_the_same(self):
        app = self.Three(hypeforge=True)
        async with app.run_test(size=(80, 20)) as pilot:
            await pilot.pause()
            self.assertEqual(app._menu_count, 4)

    def test_javiers_rule_for_the_letters(self):
        # the first letter, unless taken; then the next letter of the title, in order (2026-10-08).
        # Help is always H and Quit always Q.
        from forgekit import assign_accels

        def menu(*titles):
            return [{"id": t.lower(), "title": t} for t in titles] + [{"id": "help", "title": "Help"},
                                                                      {"id": "quit", "title": "Quit"}]
        cases = {
            ("Screens", "Settings", "Arrange", "Brightness", "Identify"): "seabi",       # displayForge
            ("Overview", "Settings", "Themes", "Shortcuts", "Backups"): "ostrb",       # alacrittyForge
            ("Dashboard", "In-System", "Install", "Update", "History"): "dinus",       # nogForge
            ("Overview", "Settings", "Boot Menu", "Themes", "Backups"): "osbta",       # grubForge
            ("Dashboard", "Settings", "Log", "History"): "dsli",                       # bitlaForge
            ("Keys", "Start", "Workspaces", "Windows", "Apps", "Tools", "About"): "kswiatb",   # Help & Keys
        }
        for titles, want in cases.items():
            got = assign_accels(menu(*titles))
            self.assertEqual("".join(got[t.lower()] for t in titles), want, titles)
            self.assertEqual((got["help"], got["quit"]), ("h", "q"))
        self.assertEqual(assign_accels(menu("Rebuild"), {"r"})["rebuild"], "e", "an app's own Ctrl key is taken")
        self.assertEqual(menu_key_clashes(self.Three.MENU), [])
        self.assertEqual(menu_key_clashes([{"id": "a", "title": "Hq"}]), [("h", "", "a")])

    async def test_a_menus_number_again_closes_it_and_its_title_is_lit(self):
        app = self.Three()
        async with app.run_test(size=(80, 20)) as pilot:
            app.set_focus(None)
            await pilot.press("3")
            await pilot.pause()
            self.assertEqual(getattr(app.screen, "menu_id", None), "more")
            self.assertTrue(app.query_one("#menu-more").has_class("open"), "lit while open")
            await pilot.press("3")
            await pilot.pause()
            self.assertEqual(len(app.screen_stack), 1, "the same number closes it")
            self.assertFalse(app.query_one("#menu-more").has_class("open"))
            app.set_focus(None)                  # the test app's only field took the focus back
            await pilot.press("3")
            await pilot.pause()
            await pilot.press("4")
            await pilot.pause()
            self.assertEqual(getattr(app.screen, "menu_id", None), "help", "another number switches")
            self.assertTrue(app.query_one("#menu-help").has_class("open"))
            self.assertFalse(app.query_one("#menu-more").has_class("open"))

    async def test_an_open_menu_is_the_only_title_lit(self):
        # Javier, 2026-10-08: "the previous option needs to clear the color, cannot stay painted"
        app = self.Three()
        async with app.run_test(size=(80, 20)) as pilot:
            await pilot.press("ctrl+o")
            await pilot.pause()
            self.assertEqual(self.active(app), ["menu-one"])
            def lit():
                return sorted(w.id for w in app.query(".menu-title.active, .menu-title.open"))
            await pilot.press("ctrl+m")
            await pilot.pause()
            self.assertEqual(lit(), ["menu-more"], "only the open menu")
            await pilot.press("ctrl+h")              # switch to Help's menu
            await pilot.pause()
            self.assertEqual(lit(), ["menu-help"])
            await pilot.press("escape")              # closed without a choice: the page is lit again
            await pilot.pause()
            self.assertEqual(lit(), ["menu-one"])
            await pilot.press("ctrl+h")
            await pilot.pause()
            await pilot.press("a")                   # About: Help stays lit, One does not come back
            await pilot.pause()
            self.assertEqual(lit(), ["menu-help"])

    async def test_about_and_license_are_pages_not_windows(self):
        app = self.Three()
        async with app.run_test(size=(80, 20)) as pilot:
            await pilot.press("ctrl+o")
            await pilot.pause()
            for action, page in (("about", "sec-forge-about"), ("license", "sec-forge-license")):
                app.action_act(action)
                await pilot.pause()
                self.assertEqual(len(app.screen_stack), 1, f"{action}: no window")
                self.assertEqual(app.query_one("#forge-work").current, page)
                self.assertEqual(self.active(app), ["menu-help"], "Help is lit while its page shows")
            await pilot.press("escape")
            await pilot.pause()
            self.assertEqual(app.query_one("#forge-work").current, "sec-one", "Esc goes back where you were")
            self.assertEqual(self.active(app), ["menu-one"])


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
