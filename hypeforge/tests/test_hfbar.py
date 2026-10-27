"""The bar reloads only once sound has settled (F-86, Javier's logins of 2026-10-25 and 10-26: the bar was
gone a few seconds after each, until the bar guard brought it back)."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/common"))
import hfbar  # noqa: E402

PW_METADATA = """#!/bin/sh
# a stand-in: the sound service's "default" record; the chosen output appears after $SINK_AFTER looks
n=$(cat "$DIR/looks" 2>/dev/null || echo 0); n=$((n + 1)); echo $n > "$DIR/looks"
[ -n "$NO_PIPEWIRE" ] && exit 1
[ -n "$HANG" ] && sleep 5
echo 'Found "default" metadata 38'
[ "$n" -gt "$SINK_AFTER" ] && echo "update: id:0 key:'default.audio.sink' value:'{\\"name\\":\\"x\\"}'"
exit 0
"""
PW_DUMP = """#!/bin/sh
[ -z "$WP_PID" ] && { echo '[]'; exit 0; }
echo '[{"id":33,"type":"PipeWire:Interface:Client","info":{"props":{"application.name":"WirePlumber","application.process.id":"'$WP_PID'"}}}]'
"""
PGREP = """#!/bin/sh
# only the test's own stand-in bar: a signal must never reach the real one
echo "$BAR_PID"
"""
BAR = """
import os, signal, sys, time
def got(*_):
    looks = open(os.path.join(os.environ["DIR"], "looks")).read().strip() if os.path.exists(os.path.join(os.environ["DIR"], "looks")) else "0"
    open(os.path.join(os.environ["DIR"], "reloaded"), "w").write(looks)
signal.signal(signal.SIGUSR2, got)
open(os.path.join(os.environ["DIR"], "ready"), "w").write("1")
time.sleep(60)
"""


class TheBarReloadsOnlyOnceSoundSettled(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="hfbar-sound-"))
        fake = self.dir / "bin"
        fake.mkdir()
        for name, text in (("pw-metadata", PW_METADATA), ("pw-dump", PW_DUMP), ("pgrep", PGREP), ("wpctl", "#!/bin/sh\n")):
            (fake / name).write_text(text)
            (fake / name).chmod(0o755)
        self.env = dict(os.environ)
        os.environ.update(PATH=f"{fake}:{os.environ['PATH']}", DIR=str(self.dir), SINK_AFTER="0",
                          XDG_RUNTIME_DIR=str(self.dir), BAR_PID="999999999")
        for k in ("NO_PIPEWIRE", "WP_PID", "HANG"):
            os.environ.pop(k, None)
        self.young = subprocess.Popen(["sleep", "60"])       # a WirePlumber that just started
        self.procs = [self.young]

    def tearDown(self):
        import shutil
        for p in self.procs:
            p.kill()
            p.wait()
        os.environ.clear()
        os.environ.update(self.env)
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_settled_once_the_default_output_is_chosen(self):
        os.environ["WP_PID"] = str(self.young.pid)
        self.assertTrue(hfbar.sound_settled())

    def test_starting_wireplumber_is_not_settled(self):
        os.environ.update(SINK_AFTER="1000", WP_PID=str(self.young.pid))
        self.assertFalse(hfbar.sound_settled())

    def test_an_old_wireplumber_with_no_speakers_is_settled(self):
        os.environ.update(SINK_AFTER="1000", WP_PID="1")    # the first process: running since boot
        self.assertTrue(hfbar.sound_settled())

    def test_wireplumber_not_connected_yet_is_not_settled(self):
        os.environ["SINK_AFTER"] = "1000"
        self.assertFalse(hfbar.sound_settled())

    def test_no_sound_service_answering_nothing_to_wait_for(self):
        os.environ["NO_PIPEWIRE"] = "1"
        self.assertTrue(hfbar.sound_settled())

    def test_no_answer_is_busy_not_absent(self):
        """A frozen WirePlumber hangs the question instead of failing it (the bench's 10-26 catch: read as
        "no sound service", the reload went straight into the crash)."""
        os.environ["HANG"] = "1"
        self.assertFalse(hfbar.sound_settled())

    def test_never_settles_the_reload_goes_anyway(self):
        os.environ.update(SINK_AFTER="1000", WP_PID=str(self.young.pid))
        t = time.monotonic()
        self.assertFalse(hfbar.wait_for_sound(longest=0.3))
        self.assertLess(time.monotonic() - t, 2)

    def bar(self):
        p = subprocess.Popen([sys.executable, "-c", BAR])
        self.procs.append(p)
        for _ in range(100):
            if (self.dir / "ready").exists():
                break
            time.sleep(0.05)
        os.environ["BAR_PID"] = str(p.pid)
        return p

    def reloaded_after(self) -> int | None:
        for _ in range(40):
            if (self.dir / "reloaded").exists():
                return int((self.dir / "reloaded").read_text())
            time.sleep(0.05)
        return None

    def test_a_reload_waits_for_sound(self):
        os.environ.update(SINK_AFTER="3", WP_PID=str(self.young.pid))
        self.bar()
        hfbar.signal_bar(signal.SIGUSR2)
        self.assertEqual(self.reloaded_after(), 4)   # three looks said "still starting"; the fourth, the reload

    def test_a_redraw_never_waits(self):
        os.environ.update(SINK_AFTER="1000", WP_PID=str(self.young.pid))
        p = self.bar()
        sig = signal.SIGRTMIN + 9
        t = time.monotonic()
        hfbar.signal_bar(sig, wait=0.2)              # this bar doesn't catch it: signal_bar gives up, no kill
        self.assertLess(time.monotonic() - t, 1)
        self.assertIsNone(p.poll())
        self.assertFalse((self.dir / "looks").exists())   # sound never asked


if __name__ == "__main__":
    unittest.main()
