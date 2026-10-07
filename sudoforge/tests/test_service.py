"""The service end to end, with a stand-in sudo and a stand-in box.

The stand-in sudo is a Python process whose name is "sudo" (so the service's
"is the helper's parent sudo?" check sees what it sees with the real one). It
runs the real ``sudoforge-askpass`` and records what it was given. The stand-in
box speaks the real box's protocol and answers as each test tells it to. A live
polkit check runs at the end (it always answers Cancel; nothing runs as admin).
"""

from __future__ import annotations

import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sudoforge.service import Service

ROOT = Path(__file__).resolve().parent.parent
ASKPASS = str(ROOT / "sudoforge-askpass")

BOX = r'''
import json, os, socket, sys, time
out = os.environ["FAKE_BOX_LOG"]
c = socket.socket(socket.AF_UNIX); c.connect(os.environ["SUDOFORGE_BOX_SOCK"])
c.sendall((json.dumps({"token": os.environ.get("FAKE_BOX_TOKEN", os.environ["SUDOFORGE_BOX_TOKEN"])}) + "\n").encode())
q = b""
while not q.endswith(b"\n"):
    ch = c.recv(4096)
    if not ch: sys.exit(0)
    q += ch
q = json.loads(q)
start = time.time(); time.sleep(float(os.environ.get("FAKE_BOX_WAIT", "0")))
answer = os.environ.get("FAKE_BOX_ANSWER")
with open(out, "a") as f:
    f.write(json.dumps({"q": q, "start": start, "end": time.time(),
                        "env_has_token": "SUDOFORGE_BOX_TOKEN" in os.environ}) + "\n")
if answer == "HANG":
    time.sleep(30)
c.sendall((json.dumps({"ok": True, "password": answer} if answer else {"ok": False}) + "\n").encode())
'''

FAKE_SUDO = r'''
import subprocess, sys, os
askpass, out = sys.argv[1], sys.argv[2]
r = subprocess.run([askpass, "[sudo] password for javier: "], capture_output=True, text=True)
with open(out, "w") as f:
    f.write(r.stdout); f.write("\x00" + str(r.returncode) + "\x00" + r.stderr)
'''


class ServiceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.box_log = self.tmp / "box.log"
        box = self.tmp / "box.py"
        box.write_text(BOX)
        (self.tmp / "sudo.py").write_text(FAKE_SUDO)
        self.env_before = dict(os.environ)
        os.environ["SUDOFORGE_BOX_COMMAND"] = f"{sys.executable} {box}"
        os.environ["FAKE_BOX_LOG"] = str(self.box_log)
        os.environ["XDG_RUNTIME_DIR"] = str(self.tmp / "run")
        (self.tmp / "run").mkdir(mode=0o700)
        self.log = io.StringIO()
        self.svc = Service()
        with redirect_stdout(self.log):
            self.svc.prepare()
            self.svc.open_sudo_door()

    def tearDown(self):
        with redirect_stdout(self.log):
            self.svc.stop()
        os.environ.clear()
        os.environ.update(self.env_before)

    def sudo(self, name="sudo", args=("-A", "-k", "pacman", "-S", "--needed", "firefox"), wait=True):
        """A stand-in sudo: process name "sudo", runs the real helper."""
        out = self.tmp / f"sudo-{time.monotonic_ns()}.out"
        # Python started with argv[0] = "sudo": /proc shows a process called sudo
        p = subprocess.Popen([name, "-c", FAKE_SUDO, ASKPASS, str(out), *args], executable=sys.executable,
                             stdin=subprocess.DEVNULL)
        if not wait:
            return p, out
        p.wait(20)
        return self.result(out)

    def result(self, out):
        stdout, code, stderr = out.read_text().split("\x00")
        return stdout, int(code), stderr

    def questions(self):
        return [json.loads(l) for l in self.box_log.read_text().splitlines()] if self.box_log.exists() else []

    # ── sudo ────────────────────────────────────────────────────────────────
    def test_the_password_reaches_sudo_and_the_box_shows_the_command(self):
        os.environ["FAKE_BOX_ANSWER"] = "s3cret pw!"
        stdout, code, _ = self.sudo()
        self.assertEqual((stdout, code), ("s3cret pw!\n", 0))
        q = self.questions()[0]["q"]
        # the stand-in's own command line carries its script; real sudo's is clean
        # (sudo_command on real sudo lines: test_words)
        self.assertTrue(q["detail"].endswith("-A -k pacman -S --needed firefox"), q["detail"])
        self.assertTrue(q["heading"].endswith("wants to run as admin"))
        self.assertTrue(q["label"].startswith("Password for "))
        self.assertEqual(q["attempt"], 1)
        self.assertNotIn("s3cret", self.log.getvalue(), "never in the service's record")

    def test_cancel_means_no_password(self):
        os.environ.pop("FAKE_BOX_ANSWER", None)
        stdout, code, _ = self.sudo()
        self.assertEqual((stdout, code), ("", 1))

    def test_only_sudo_may_ask(self):
        os.environ["FAKE_BOX_ANSWER"] = "should-not-leak"
        stdout, code, err = self.sudo(name="notsudo")
        self.assertEqual((stdout, code), ("", 1))
        self.assertIn("only sudo may ask here", err)
        self.assertEqual(self.questions(), [], "no box opened")

    def test_a_box_with_the_wrong_token_gets_nothing(self):
        os.environ["FAKE_BOX_ANSWER"] = "pw"
        os.environ["FAKE_BOX_TOKEN"] = "not-the-token"
        stdout, code, _ = self.sudo()
        self.assertEqual((stdout, code), ("", 1))

    def test_one_box_at_a_time(self):
        os.environ["FAKE_BOX_ANSWER"] = "pw"
        os.environ["FAKE_BOX_WAIT"] = "0.6"
        a = self.sudo(wait=False)
        b = self.sudo(wait=False)
        for p, _ in (a, b):
            p.wait(20)
        self.assertEqual([self.result(o)[1] for _, o in (a, b)], [0, 0])
        first, second = sorted(self.questions(), key=lambda r: r["start"])
        self.assertGreaterEqual(second["start"], first["end"] - 0.05, "the second box waited for the first")

    def test_no_service_says_so_in_plain_words(self):
        with redirect_stdout(self.log):
            self.svc.stop()
        stdout, code, err = self.sudo()
        self.assertEqual((stdout, code), ("", 1))
        self.assertIn("no password box here", err)
        self.assertIn("without -A", err)

    def test_private_folder_and_cleanup(self):
        folder = self.svc.folder
        self.assertEqual(stat.S_IMODE(folder.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE((folder / "service.sock").stat().st_mode), 0o600)
        os.environ["FAKE_BOX_ANSWER"] = "pw"
        self.sudo()
        self.assertEqual(sorted(p.name for p in folder.iterdir()), ["service.sock"], "box sockets removed")
        with redirect_stdout(self.log):
            self.svc.stop()
        self.assertFalse(folder.exists())

    def test_a_cancel_closes_an_open_box(self):
        os.environ["FAKE_BOX_ANSWER"] = "HANG"
        cancelled = {"v": False}
        from sudoforge.words import Lines
        got = {}

        def ask():
            got["pw"] = self.svc.ask(Lines("h", None, None, "n", "l"), 1, lambda: cancelled["v"])
        t = threading.Thread(target=ask)
        t.start()
        end = time.time() + 10
        while self.svc._current is None and time.time() < end:
            time.sleep(0.05)
        time.sleep(0.5)
        self.svc._current.cancel()
        t.join(10)
        self.assertFalse(t.is_alive(), "ask() returned after the cancel")
        self.assertIsNone(got["pw"])


@unittest.skipUnless(os.environ.get("XDG_SESSION_ID") and os.path.exists("/usr/bin/pkexec")
                     and os.environ.get("SUDOFORGE_LIVE_POLKIT") == "1",
                     "live polkit check: set SUDOFORGE_LIVE_POLKIT=1 on a desktop session")
class LivePolkit(unittest.TestCase):
    """The real polkit, the real session; the stand-in box always says Cancel."""

    def test_another_programs_request_reaches_the_box(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "box.py").write_text(BOX)
        env_before = dict(os.environ)
        os.environ.update(SUDOFORGE_BOX_COMMAND=f"{sys.executable} {tmp / 'box.py'}",
                          FAKE_BOX_LOG=str(tmp / "box.log"), XDG_RUNTIME_DIR=str(tmp))
        os.environ.pop("FAKE_BOX_ANSWER", None)
        from gi.repository import GLib
        log = io.StringIO()
        svc = Service()
        try:
            with redirect_stdout(log):
                svc.prepare()
                why = svc.start_agent()
            self.assertIsNone(why, why)
            loop = GLib.MainLoop()
            result = {}

            def other():
                r = subprocess.run(["setsid", "pkexec", "--disable-internal-agent", "/usr/bin/true"],
                                   stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30)
                result["code"] = r.returncode
                GLib.idle_add(loop.quit)
            threading.Thread(target=other, daemon=True).start()
            with redirect_stdout(log):
                loop.run()
            self.assertEqual(result["code"], 126, "cancelled: nothing ran as admin")
            q = json.loads((tmp / "box.log").read_text().splitlines()[0])["q"]
            self.assertTrue(q["heading"].endswith("wants to run as admin"), q)
            self.assertEqual(q["detail"], "/usr/bin/true")
            self.assertIn("checked by the system (polkit)", q["note"])
        finally:
            with redirect_stdout(log):
                svc.stop()
            os.environ.clear()
            os.environ.update(env_before)


if __name__ == "__main__":
    unittest.main()
