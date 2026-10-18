"""#54 (2026-10-17): an applet that crashes at login says so, never dies silently. The watcher
Sway starts every login applet through: a crash → one notification naming it, its error and its
log; a clean end or a stop on purpose → nothing."""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WATCH = REPO / "applets/common/hypeforge-watch"


class Watcher(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        bin_ = self.dir / "bin"
        bin_.mkdir()
        self.sent = self.dir / "sent.txt"
        (bin_ / "notify-send").write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" >> {self.sent}\necho --- >> {self.sent}\n')
        (bin_ / "notify-send").chmod(0o755)
        self.env = dict(os.environ, PATH=f"{bin_}:{os.environ['PATH']}", XDG_STATE_HOME=str(self.dir / "state"))
        # a stand-in Sway socket: the watcher asks it whether the session is still on (2026-10-17)
        self.sway = socket.socket(socket.AF_UNIX)
        self.sway.bind(str(self.dir / "sway.sock"))
        self.sway.listen(8)
        self.env["SWAYSOCK"] = str(self.dir / "sway.sock")

    def tearDown(self):
        self.sway.close()

    def watch(self, *cmd, wait=True):
        p = subprocess.Popen([str(WATCH), "workspaces", *cmd], env=self.env)
        if wait:
            p.wait(timeout=60)
        return p

    def notes(self) -> str:
        return self.sent.read_text() if self.sent.exists() else ""

    def log(self) -> str:
        return (self.dir / "state/hypeforge/logs/workspaces.log").read_text()

    def test_a_crash_is_said_with_its_name_its_error_and_its_log(self):
        self.watch(sys.executable, "-c", "import sys; print('starting'); raise NameError(\"name 're' is not defined\")")
        n = self.notes()
        self.assertIn("hypeForge: Workspaces stopped", n, "named in plain words")
        self.assertIn("NameError: name 're' is not defined", n, "the error's last line")
        self.assertIn("~/.local/state/hypeforge/logs/workspaces.log" if str(self.dir) in str(Path.home()) else "workspaces.log", n)
        self.assertIn("--urgency=critical", n, "it stays until clicked")
        self.assertIn("Traceback", self.log(), "the whole error is kept in the applet's log")

    def test_an_applet_ending_with_the_session_says_nothing(self):
        """Javier, 2026-10-17: a row of sticky "stopped" alerts after logging out and in again. At a
        log-out Sway goes first and every applet ends with "Sway closed the connection"."""
        self.sway.close()
        Path(self.env["SWAYSOCK"]).unlink()
        self.watch(sys.executable, "-c", "raise ConnectionError('Sway closed the connection')")
        self.assertFalse(self.sent.exists(), "no alert when the session itself ended")
        self.assertIn("the session ended", (self.dir / "state/hypeforge/logs/workspaces.log").read_text())

    def test_a_clean_end_says_nothing(self):
        p = self.watch(sys.executable, "-c", "print('already running')")
        self.assertEqual(p.returncode, 0)
        self.assertEqual(self.notes(), "", "exit 0 (a copy already running, a job done): silence")
        self.assertIn("already running", self.log())

    def test_a_stop_on_purpose_says_nothing(self):
        pidf = self.dir / "pid"
        self.env["PIDF"] = str(pidf)
        p = self.watch(sys.executable, "-c", "import os, time; open(os.environ['PIDF'], 'w').write(str(os.getpid())); time.sleep(60)",
                       wait=False)
        for _ in range(100):
            if pidf.exists() and pidf.read_text():
                break
            time.sleep(0.05)
        os.kill(int(pidf.read_text()), signal.SIGTERM)       # how a style switch stops an applet: its own pid
        p.wait(timeout=30)
        self.assertEqual(self.notes(), "", "a style switch or a logout is not a crash")

    def test_the_watcher_stopped_stops_the_applet_quietly(self):
        p = self.watch(sys.executable, "-c", "import time; time.sleep(60)", wait=False)
        time.sleep(0.5)
        p.send_signal(signal.SIGTERM)
        p.wait(timeout=30)
        self.assertEqual(self.notes(), "")

    def test_a_crash_signal_is_said(self):
        self.watch(sys.executable, "-c", "import os, signal; os.kill(os.getpid(), signal.SIGSEGV)")
        self.assertIn("it crashed (SIGSEGV)", self.notes())


class EveryLoginAppletIsWatched(unittest.TestCase):
    def test_sways_config_starts_the_applets_through_the_watcher(self):
        conf = (REPO / "sway/config").read_text().splitlines()
        lines = [l.strip() for l in conf if l.strip().startswith(("exec ", "exec_always ")) and "/applets/" in l]
        self.assertTrue(lines, "the login applets were found")
        for l in lines:
            with self.subTest(line=l):
                self.assertIn("applets/common/hypeforge-watch ", l, "started through the watcher")

    def test_a_styles_applets_are_watched_too(self):
        import importlib.machinery, importlib.util
        loader = importlib.machinery.SourceFileLoader("ht_watch", str(REPO / "applets/theme/hypeforge-theme"))
        spec = importlib.util.spec_from_loader("ht_watch", loader)
        ht = importlib.util.module_from_spec(spec)
        loader.exec_module(ht)
        lines = [l for l in ht.sway_applets(ht.styles()["windows-11"]).splitlines() if l.startswith("exec")]
        self.assertTrue(lines, "Windows 11 starts its taskbar")
        for l in lines:
            self.assertIn("hypeforge-watch taskbar ", l)


if __name__ == "__main__":
    unittest.main()
