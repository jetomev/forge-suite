"""v0.7.0: the shared start-up check (forge-suite #33).

Every check is fed a known-bad input as well as a good one (the guard is tested
in the failing direction). Programs are stand-in scripts in a temp folder;
the session is a dictionary, never this machine's. The screen runs headless
through Textual's Pilot.
Run: python -m unittest discover -s tests -v
"""

from __future__ import annotations

import io
import os
import stat
import tempfile
import unittest
from pathlib import Path

from textual.widgets import Button, Static

from forgekit import (
    Finding, Need, NeedsApp, a_file, check_needs, describe_session, heading_for, lines_for, missing,
    needs_text, parse_version, program, service, start_check, sway_session,
)
from forgekit.widgets import Notice


def script(body: str, name: str = "tool") -> str:
    d = Path(tempfile.mkdtemp())
    f = d / name
    f.write_text("#!/bin/bash\n" + body)
    f.chmod(f.stat().st_mode | stat.S_IEXEC)
    return str(f)


def text_of(w) -> str:
    for attr in ("content", "renderable"):
        v = getattr(w, attr, None)
        if v is not None:
            return str(getattr(v, "plain", v))
    return str(w)


KDE = {"XDG_CURRENT_DESKTOP": "KDE", "WAYLAND_DISPLAY": "wayland-0", "TERM": "xterm-256color"}
CONSOLE = {"TERM": "linux"}


class Versions(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_version("nog 1.8.0"), (1, 8, 0))
        self.assertEqual(parse_version("sway version 1.12"), (1, 12))
        self.assertIsNone(parse_version("no numbers here"))


class ProgramNeed(unittest.TestCase):
    def test_missing_program(self):
        f = missing(check_needs([program("no-such-forge-tool-xyz", "why")]))
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0].found, "no-such-forge-tool-xyz is not installed")

    def test_old_and_new_enough(self):
        exe = script('echo "tool 1.6.1"')
        old = check_needs([program("tool", "why", min_version="1.7.0", path=exe)])[0]
        self.assertFalse(old.met)
        self.assertEqual(old.found, "tool 1.6.1, older than 1.7.0")
        self.assertEqual(old.need.what, "tool 1.7.0 or newer")
        ok = check_needs([program("tool", "why", min_version="1.6.0", path=exe)])[0]
        self.assertTrue(ok.met)
        self.assertEqual(ok.found, "tool 1.6.1")

    def test_unreadable_version(self):
        exe = script('echo "no version printed"')
        f = check_needs([program("tool", "why", min_version="1.0", path=exe)])[0]
        self.assertFalse(f.met)
        self.assertIn("could not be read", f.found)

    def test_installed_without_version_rule(self):
        exe = script("exit 0")
        f = check_needs([program("tool", "why", path=exe)])[0]
        self.assertTrue(f.met)


class SwayNeed(unittest.TestCase):
    def test_not_sway_says_what_is(self):
        f = check_needs([sway_session("why", "instead", environ=KDE)])[0]
        self.assertFalse(f.met)
        self.assertEqual(f.found, "KDE Plasma (Wayland)")

    def test_text_console(self):
        f = check_needs([sway_session("why", environ=CONSOLE)])[0]
        self.assertEqual(f.found, "a text console, no graphical session")

    def test_sway_answering(self):
        exe = script("exit 0", "swaymsg")
        f = check_needs([sway_session("why", environ={"SWAYSOCK": "/tmp/x.sock"}, swaymsg=exe)])[0]
        self.assertTrue(f.met)
        self.assertEqual(f.found, "a Sway session")

    def test_sway_socket_dead(self):
        exe = script("exit 1", "swaymsg")
        f = check_needs([sway_session("why", environ={"SWAYSOCK": "/tmp/x.sock"}, swaymsg=exe)])[0]
        self.assertFalse(f.met)
        self.assertEqual(f.found, "a Sway socket that doesn't answer")

    def test_describe_session(self):
        self.assertEqual(describe_session({"HYPRLAND_INSTANCE_SIGNATURE": "x", "WAYLAND_DISPLAY": "w"}),
                         "Hyprland (Wayland)")
        self.assertEqual(describe_session({"DISPLAY": ":0", "DESKTOP_SESSION": "i3"}), "i3 (X11)")
        self.assertEqual(describe_session({"SSH_TTY": "/dev/pts/1"}), "a terminal over SSH, no graphical session")
        self.assertEqual(describe_session({"WAYLAND_DISPLAY": "w"}), "an unknown desktop (Wayland)")


class ServiceNeed(unittest.TestCase):
    def test_active_and_inactive(self):
        up = script('echo active', "systemctl")
        down = script('echo inactive; exit 3', "systemctl")
        self.assertTrue(check_needs([service("nog.service", "why", systemctl=up)])[0].met)
        f = check_needs([service("nog.service", "why", systemctl=down)])[0]
        self.assertFalse(f.met)
        self.assertEqual(f.found, "nog.service is inactive")
        self.assertEqual(f.need.what, "the nog.service service")

    def test_user_flag_reaches_systemctl(self):
        exe = script('[ "$1" = "--user" ] && echo active || echo inactive', "systemctl")
        self.assertTrue(check_needs([service("u", "why", user=True, systemctl=exe)])[0].met)
        self.assertFalse(check_needs([service("u", "why", user=False, systemctl=exe)])[0].met)


class FileNeed(unittest.TestCase):
    def test_there_and_not(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "settings.toml"
        self.assertFalse(check_needs([a_file(p, "why")])[0].met)
        p.write_text("x")
        f = check_needs([a_file(p, "why")])[0]
        self.assertTrue(f.met)
        self.assertTrue(f.found.endswith("settings.toml is there"))


class Words(unittest.TestCase):
    def miss(self, optional=False):
        n = Need("a Sway session", lambda: (False, "KDE Plasma (Wayland)"), "It talks to Sway.",
                 "Use KDE's display settings.", optional)
        return [Finding(n, False, "KDE Plasma (Wayland)")]

    def test_a_failing_check_is_not_met(self):
        def boom():
            raise RuntimeError("x")
        f = check_needs([Need("thing", boom, "why")])[0]
        self.assertFalse(f.met)
        self.assertIn("check itself failed", f.found)

    def test_heading(self):
        self.assertEqual(heading_for("displayForge", self.miss()),
                         "displayForge can't run here: it needs a Sway session")
        self.assertEqual(heading_for("displayForge", self.miss(optional=True)),
                         "displayForge can run here, with something missing")
        two = self.miss() + self.miss()
        self.assertEqual(heading_for("x", two), "x can't run here: 2 things it needs are missing")

    def test_lines_in_order(self):
        lines = lines_for(self.miss()[0])
        self.assertEqual([l.split(":")[0] for l in lines], ["Needs", "Found", "Why", "Instead"])
        self.assertIn("KDE Plasma (Wayland)", lines[1])

    def test_terminal_record(self):
        t = needs_text("displayForge", self.miss())
        for word in ("==> displayForge can't run here", "Needs:   a Sway session", "Found:   KDE Plasma",
                     "Why:     It talks to Sway.", "Instead: Use KDE's", "Nothing was changed."):
            self.assertIn(word, t)
        self.assertIn("Continuing anyway", needs_text("x", self.miss(optional=True), decision="continue"))


class StartCheck(unittest.TestCase):
    def test_all_met_asks_nothing(self):
        asked = []
        ok = start_check("app", [Need("x", lambda: (True, "x"), "why")], ask=lambda n, m: asked.append(1))
        self.assertTrue(ok)
        self.assertEqual(asked, [])

    def test_required_missing_closes_even_if_continue_is_answered(self):
        out = io.StringIO()
        ok = start_check("app", [Need("x", lambda: (False, "not x"), "why")], ask=lambda n, m: "continue", out=out)
        self.assertFalse(ok)
        self.assertIn("Nothing was changed.", out.getvalue())

    def test_optional_missing_may_continue(self):
        out = io.StringIO()
        need = Need("x", lambda: (False, "not x"), "why", optional=True)
        self.assertTrue(start_check("app", [need], ask=lambda n, m: "continue", out=out))
        self.assertIn("Continuing anyway", out.getvalue())
        self.assertFalse(start_check("app", [need], ask=lambda n, m: "close", out=io.StringIO()))


class Screen(unittest.IsolatedAsyncioTestCase):
    def miss(self, optional=False):
        n = Need("a Sway session", lambda: (False, ""), "displayForge talks to Sway.",
                 "Use your desktop's display settings.", optional)
        return [Finding(n, False, "KDE Plasma (Wayland)")]

    async def test_shows_the_four_facts_and_closes_on_c(self):
        app = NeedsApp("displayForge", self.miss())
        async with app.run_test(size=(100, 30)) as pilot:
            head = text_of(app.query_one("#needs-head", Static))
            self.assertIn("displayForge can't run here", head)
            notice = app.query_one("#need-0", Notice)
            body = text_of(notice._body)
            for word in ("Found:", "KDE Plasma (Wayland)", "Why:", "talks to Sway", "Instead:", "display settings"):
                self.assertIn(word, body)
            self.assertEqual(len(app.query("#needs-continue")), 0, "no Continue for a required need")
            close = app.query_one("#needs-close", Button)
            self.assertTrue(close.has_focus, "Close starts focused")
            self.assertEqual(str(close.label), "Close (c)")
            await pilot.press("c")
        self.assertEqual(app.return_value, "close")

    async def test_escape_closes(self):
        app = NeedsApp("x", self.miss())
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.press("escape")
        self.assertEqual(app.return_value, "close")

    async def test_a_does_nothing_for_a_required_need(self):
        app = NeedsApp("x", self.miss())
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.press("a")
            await pilot.pause()
            self.assertIsNone(app.return_value)
            await pilot.press("c")
        self.assertEqual(app.return_value, "close")

    async def test_optional_offers_continue(self):
        app = NeedsApp("x", self.miss(optional=True))
        async with app.run_test(size=(100, 30)) as pilot:
            btn = app.query_one("#needs-continue", Button)
            self.assertEqual(str(btn.label), "Continue Anyway (a)")
            self.assertIn("with something missing", text_of(app.query_one("#needs-head", Static)))
            await pilot.press("a")
        self.assertEqual(app.return_value, "continue")

    async def test_buttons_sit_under_the_body(self):
        app = NeedsApp("x", self.miss(optional=True))
        async with app.run_test(size=(100, 30)):
            body = app.query_one("#needs-body").region
            close = app.query_one("#needs-close", Button).region
            cont = app.query_one("#needs-continue", Button).region
            self.assertGreaterEqual(close.y, body.y + body.height, "footer below the body")
            self.assertLess(cont.x, close.x, "Continue left of Close")
            self.assertTrue(cont.width > 0 and close.width > 0)


if __name__ == "__main__":
    unittest.main()
