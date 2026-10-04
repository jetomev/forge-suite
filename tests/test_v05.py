"""v0.5.0 pieces: notices, hint and changes bars, form controls, the filter list,
review and progress windows, the manual, the terminal record.

Layout is checked by position, not by existence (CLAUDE.md).
Run: python -m unittest discover -s tests -v
"""
from __future__ import annotations

import datetime as dt
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "examples"))

from textual.widgets import OptionList, Static  # noqa: E402

from forgekit import (  # noqa: E402
    ChangeGroup, Choices, FilterPicker, ManualScreen, NumberPresets, ProgressDialog, ReviewDialog,
    Toggle, closing_notice, notice_markup, review_markup, runs_log_row, session_banner,
)

import gallery  # noqa: E402

SIZE = (110, 36)


class NoticeText(unittest.TestCase):
    def test_heading_and_indented_lines(self):
        m = notice_markup("Saved · 4 changes", ["one", "two"], level="ok")
        lines = m.split("\n")
        self.assertIn("==> Saved · 4 changes", lines[0])
        self.assertIn("$forge-ok", lines[0])
        # the indent survives layout only as non-breaking spaces
        self.assertEqual(lines[1], " " * 4 + "one")

    def test_outside_text_is_escaped(self):
        self.assertIn("\\[x]", notice_markup("[x] heading"))


class Review(unittest.TestCase):
    def test_every_change_reads_old_arrow_new(self):
        m = review_markup([ChangeGroup("Settings", "/etc/default/grub", [("Theme", "none", "Vimix")])],
                          steps=["Back up"], note="Password once.")
        self.assertIn("Theme", m)
        self.assertIn("none", m)
        self.assertIn("Vimix", m)
        self.assertIn("1  Back up", m)
        self.assertTrue(m.rstrip().endswith("Password once.[/]"))


class TerminalRecord(unittest.TestCase):
    def test_closing_has_one_blank_line_before_and_one_after(self):
        text = closing_notice("Closed", ["4 changes saved"], logs=["/tmp/x.csv"], thanks="Thank you!",
                              color=False)
        printed = text + "\n"          # print() adds the line end
        self.assertTrue(printed.startswith("\n==> Closed"))
        self.assertFalse(printed.startswith("\n\n"))
        self.assertTrue(printed.endswith("Thank you!\n\n"))
        self.assertFalse(printed.endswith("\n\n\n"))
        self.assertIn("    Logged in:\n      /tmp/x.csv", text)

    def test_banner_names_the_run(self):
        b = session_banner("grubForge", "2.0.0", "grubforge", dt.datetime(2026, 10, 2, 9, 31),
                           dt.datetime(2026, 10, 2, 9, 44), "javier", color=False)
        self.assertTrue(b.startswith("\n===="))
        self.assertIn("grubForge v2.0.0  ·  Session", b)
        self.assertIn("Run:   grubforge", b)
        self.assertIn("09:31 AM   →   09:44 AM", b)

    def test_runs_log_writes_the_header_once(self):
        with tempfile.TemporaryDirectory() as d:
            when = dt.datetime(2026, 10, 2, 9, 44)
            p = runs_log_row(d, "grubforge", ["a", "b", "c", "d", "e", "f"], when=when)
            runs_log_row(d, "grubforge", ["g", "h", "i", "j", "k", "l"], when=when)
            lines = p.read_text().splitlines()
            self.assertEqual(p.name, "20261002 grubforge-runs.csv")
            self.assertEqual(lines[0], "date,time,user,run,outcome,detail")
            self.assertEqual(len(lines), 3)


class Shell(unittest.IsolatedAsyncioTestCase):
    async def test_bars_sit_at_the_bottom_changes_over_hints(self):
        app = gallery.Gallery()
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            hints = app.query_one("#forge-hints").region
            changes = app.query_one("#forge-changes").region
            self.assertEqual(hints.y, SIZE[1] - 1)
            self.assertEqual(changes.y, SIZE[1] - 2)
            self.assertEqual(hints.width, SIZE[0])
            # the work area ends above the bars
            work = app.query_one("#forge-work").region
            self.assertLessEqual(work.bottom, changes.y)

    async def test_tab_reaches_the_screen_before_the_bar(self):
        app = gallery.Gallery()
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            self.assertEqual(app.focused.id, "default")   # the first setting, not Save
            order = []
            for _ in range(7):
                order.append(type(app.focused).__name__)
                await pilot.press("tab")
                await pilot.pause()
            self.assertEqual(order, ["Select", "Toggle", "Input", "Choices", "SelectionList", "Button", "Button"])

    async def test_hints_follow_focus(self):
        app = gallery.Gallery()
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.press("tab")          # → Toggle
            await pilot.pause()
            self.assertIn("switch on/off", str(app.query_one("#forge-hints").render()))
            await pilot.press("tab")          # → the number
            await pilot.pause()
            self.assertIn("presets", str(app.query_one("#forge-hints").render()))

    async def test_hints_follow_the_section_shown_even_with_nothing_to_focus(self):
        # nogForge, Javier 3 Oct: Update → Dashboard kept Update's keys, because the
        # Dashboard has nothing to focus and focus stayed in the hidden section.
        from textual.containers import Vertical
        from textual.widgets import Input
        from forgekit import ForgeApp

        class Busy(Vertical):
            FORGE_HINTS = [("x", "busy keys")]

            def compose(self):
                yield Input(id="field")

        class Quiet(Vertical):
            FORGE_HINTS = [("y", "quiet keys")]

            def compose(self):
                yield Static("nothing to focus here")

        class Two(ForgeApp):
            APP_NAME, APP_VERSION, SHOW_HINT_BAR = "Two", "0", True
            MENU = [{"id": "quiet", "title": "Quiet", "kind": "section"},
                    {"id": "busy", "title": "Busy", "kind": "section"}]

            def compose_sections(self):
                yield Quiet(id="sec-quiet")
                yield Busy(id="sec-busy")

        app = Two()
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            bar = lambda: str(app.query_one("#forge-hints").render())
            self.assertIn("quiet keys", bar())
            app._switch_section("busy")
            app.query_one("#field").focus()
            await pilot.pause()
            self.assertIn("busy keys", bar())
            app._switch_section("quiet")
            await pilot.pause()
            self.assertIn("quiet keys", bar(), "the shown section's keys, not the hidden one's")
            self.assertNotIn("busy keys", bar())

    async def test_title_status_sits_at_the_right_edge(self):
        app = gallery.Gallery()
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            from textual.content import Content
            text = Content.from_markup(str(app.query_one("#forge-title").render())).plain
            self.assertTrue(text.rstrip().endswith("password at save"))
            name = app.APP_NAME
            left = text.index(name)
            self.assertAlmostEqual(left, (SIZE[0] - len(name)) // 2, delta=1)   # centred

    async def test_hidden_changes_bar_takes_no_row(self):
        app = gallery.Gallery()
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            app.changes_bar.hide()
            await pilot.pause()
            self.assertEqual(app.query_one("#forge-hints").region.y, SIZE[1] - 1)
            self.assertEqual(app.query_one("#forge-work").region.bottom, SIZE[1] - 1)

    async def test_before_quit_can_hold_the_app(self):
        app = gallery.Gallery()
        app.before_quit = lambda: False
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            app.action_act("quit")
            await pilot.pause()
            self.assertTrue(app.is_running)


class Controls(unittest.IsolatedAsyncioTestCase):
    async def test_toggle_says_its_state_and_flips_with_space(self):
        app = gallery.Gallery()
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            t = app.query_one(Toggle)
            self.assertIn("Off", str(t.render()))
            t.focus()
            await pilot.press("space")
            await pilot.pause()
            self.assertTrue(t.value)
            self.assertIn("On", str(t.render()))

    async def test_choices_move_with_the_arrows(self):
        app = gallery.Gallery()
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            c = app.query_one(Choices)
            c.focus()
            await pilot.press("right")
            await pilot.pause()
            self.assertEqual(c.value, "hidden")
            await pilot.press("right")       # wraps round
            await pilot.pause()
            self.assertEqual(c.value, "menu")

    async def test_number_presets_step_with_the_arrows_and_accept_typing(self):
        app = gallery.Gallery()
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            n = app.query_one(NumberPresets)
            n.query_one("Input").focus()
            await pilot.press("down")
            await pilot.pause()
            self.assertEqual(n.value, 10)
            self.assertTrue(n.query_one("#preset-3").has_class("-selected"))
            n.query_one("Input").value = "7"
            await pilot.pause()
            self.assertEqual(n.value, 7)
            self.assertFalse(any(b.has_class("-selected") for b in n.query(".forge-preset")))

    async def test_changed_mark_and_was_line(self):
        app = gallery.Gallery()
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            row = app.query_one("#row-default")
            self.assertIn("changed", str(row.query_one(".forge-setting-note").render()))
            self.assertIn("was: the first entry", str(row.query_one(".forge-setting-note").render()))
            row.mark_unchanged()
            await pilot.pause()
            self.assertNotIn("changed", str(row.query_one(".forge-setting-note").render()))


class Windows(unittest.IsolatedAsyncioTestCase):
    async def test_picker_opens_on_the_current_value_and_filters(self):
        app = gallery.Gallery()
        results = []
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            app.push_screen(FilterPicker("Pick", [("a", "Alpha"), ("b", "Beta"), ("g", "Gamma")], current="b"),
                            results.append)
            await pilot.pause()
            ol = app.screen.query_one(OptionList)
            self.assertEqual(ol.highlighted, 1)
            await pilot.press("g", "a")          # typing on the list goes to the filter
            await pilot.pause()
            self.assertIn("1 of 3", str(app.screen.query_one("#picker-count").render()))
            await pilot.press("enter")
            await pilot.pause()
        self.assertEqual(results, ["g"])

    async def test_picker_can_take_a_typed_value(self):
        app = gallery.Gallery()
        results = []
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            app.push_screen(FilterPicker("Pick", ["1920x1080", "1280x720"], allow_custom=True), results.append)
            await pilot.pause()
            for ch in "1600x900":
                await pilot.press(ch)
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
        self.assertEqual(results, ["1600x900"])

    async def test_review_returns_the_button_and_none_on_escape(self):
        app = gallery.Gallery()
        results = []
        groups = [ChangeGroup("Settings", "", [("Theme", "none", "Vimix")])]
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            app.push_screen(ReviewDialog("Review", groups, buttons=[("Save", "save", True)]), results.append)
            await pilot.pause()
            self.assertEqual(app.focused.id, "save")
            await pilot.press("enter")
            await pilot.pause()
            app.push_screen(ReviewDialog("Review", groups), results.append)
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
        self.assertEqual(results, ["save", None])

    async def test_progress_cannot_close_until_finished(self):
        app = gallery.Gallery()
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            d = ProgressDialog("Job", ["one", "two"])
            app.push_screen(d)
            await pilot.pause()
            d.set_step(0, "done")
            d.set_step(1, "working")
            d.add_line("working on it")
            await pilot.press("escape")
            await pilot.pause()
            self.assertIs(app.screen, d)
            d.set_step(1, "done")
            d.finish()
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            self.assertIsNot(app.screen, d)

    async def test_manual_opens_pages_and_goes_back(self):
        app = gallery.Gallery()
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            m = ManualScreen("Manual", gallery.PAGES, start="backups")
            app.push_screen(m)
            await pilot.pause(0.3)
            # opened where asked, and stays there (the list's own first
            # highlight once sent it back to the first page)
            self.assertEqual(m.current, "backups")
            m.open_page("start", remember=False)
            await pilot.pause(0.3)
            self.assertEqual(m.current, "start")
            m.open_page("backups")
            await pilot.pause()
            self.assertEqual(m.current, "backups")
            await pilot.press("backspace")
            await pilot.pause()
            self.assertEqual(m.current, "start")
            # the manual fills the screen, its hint bar on the last row
            self.assertEqual(m.query_one("#forge-hints").region.y, SIZE[1] - 1)


class ConsoleGallery(unittest.TestCase):
    """The gallery in a pseudo-terminal with TERM=linux: every character drawable,
    every letter visible against its background."""

    def test_gallery_views_draw_only_console_characters(self):
        views = {"form": "wait:0.1", "picker": "p wait:1", "review": "r wait:1", "manual": "m wait:1.5"}
        env = dict(os.environ, PYTHONPATH=str(ROOT))
        env.pop("FORGE_ASCII", None)
        with tempfile.TemporaryDirectory() as d:
            for name, keys in views.items():
                r = subprocess.run(
                    [sys.executable, str(ROOT / "tools" / "console-preview.py"), "--keys", keys, "--settle", "2.5",
                     "--out", os.path.join(d, f"{name}.png"), "--",
                     sys.executable, str(ROOT / "examples" / "gallery.py")],
                    env=env, capture_output=True, text=True, timeout=60)
                self.assertEqual(r.returncode, 0, f"{name}: {r.stdout}{r.stderr}")
                self.assertIn("every character on screen is in the console font", r.stdout, name)
                self.assertIn("every character is visible against its background", r.stdout, name)


if __name__ == "__main__":
    unittest.main()


class NumberDecimals(unittest.IsolatedAsyncioTestCase):
    """0.5.1: alacrittyForge's font size (11.25 pt, 12.0 shown as 12)."""

    async def test_decimals_are_accepted_and_whole_numbers_stay_plain(self):
        from textual.app import App
        from textual.widgets import Input
        from forgekit import NumberPresets
        got = []

        class A(App):
            def compose(self):
                yield NumberPresets(12.0, [("11", 11), ("12", 12)], unit="pt", decimals=True)

            def on_number_presets_changed(self, e):
                got.append(e.value)

        app = A()
        async with app.run_test() as pilot:
            await pilot.pause()
            inp = app.query_one(Input)
            self.assertEqual(inp.value, "12")
            self.assertTrue(app.query_one("#preset-1").has_class("-selected"))
            inp.value = "11.25"
            await pilot.pause()
            self.assertEqual(got[-1], 11.25)

    async def test_whole_number_fields_still_refuse_decimals(self):
        from textual.app import App
        from textual.widgets import Input
        from forgekit import NumberPresets
        got = []

        class A(App):
            def compose(self):
                yield NumberPresets(5, [("5", 5)])

            def on_number_presets_changed(self, e):
                got.append(e.value)

        app = A()
        async with app.run_test() as pilot:
            await pilot.pause()
            app.query_one(Input).value = "7"
            await pilot.pause()
            self.assertEqual(got, [7])
            self.assertIsInstance(got[0], int)


class NumberWidth(unittest.IsolatedAsyncioTestCase):
    """0.5.1: the field is as wide as its longest number, plus the cursor."""

    async def test_a_long_number_fits_without_scrolling(self):
        from textual.app import App
        from textual.widgets import Input
        from forgekit import FORGE_CSS, NumberPresets, css_variables

        class A(App):
            CSS = FORGE_CSS            # where the field's width is set

            def get_css_variables(self):
                return {**super().get_css_variables(), **css_variables(False)}

            def compose(self):
                yield NumberPresets(150, [("1000", 1000), ("100000", 100000)], maximum=100000)

        app = A()
        async with app.run_test(size=(100, 10)) as pilot:
            await pilot.pause()
            inp = app.query_one(Input)
            self.assertFalse(inp.show_horizontal_scrollbar)
            inp.value = "100000"
            await pilot.pause()
            self.assertFalse(inp.show_horizontal_scrollbar)
