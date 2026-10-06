"""displayForge · engine step 2: trying a change (and undoing it by itself), saving, brightness.

No Sway, no screens touched: a fake `swaymsg` writes every command it gets into a log, and a
fake `ddcutil` answers like Javier's Sceptres. The safety timer is tested in the failing
direction — untouched it must undo, and it must undo even when displayForge itself has died.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from displayforge import screens as S, trial as T, saving as V, brightness as B  # noqa: E402

REAL = json.loads((Path(__file__).parent / "data/three-sceptre-y27.json").read_text())


def fake_tool(folder: Path, name: str, body: str) -> str:
    p = folder / name
    p.write_text("#!/bin/sh\n" + body)
    p.chmod(p.stat().st_mode | stat.S_IEXEC)
    return str(p)


class Trying(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.log = self.tmp / "sway.log"
        # the fake swaymsg: logs its message; refuses anything containing REFUSE
        self.sway = fake_tool(self.tmp, "swaymsg",
                              f'echo "$1" >> {self.log}\ncase "$1" in *REFUSE*) exit 1;; esac\n')
        self.before = S.parse(REAL)
        mid = [s for s in self.before if s.name == "DP-3"][0]
        hz120 = [m for m in mid.rates(2560, 1440) if m.hz == 120][0]
        self.after = [replace(s, mode=hz120) if s.name == "DP-3" else s for s in self.before]

    def sent(self):
        return self.log.read_text().splitlines() if self.log.exists() else []

    def test_untouched_it_goes_back_by_itself(self):
        t = T.Trial(self.before, self.after, seconds=1, swaymsg=self.sway, runtime=str(self.tmp))
        self.assertTrue(t.start())
        self.assertEqual(len(self.sent()), 1)                      # the change went out
        self.assertIn("@120.", self.sent()[0])
        t.settle()                                                 # waits for the safety timer
        self.assertEqual(len(self.sent()), 2)                      # …and came back by itself
        self.assertIn("@144.", self.sent()[1])

    def test_keep_it_stops_the_undo(self):
        t = T.Trial(self.before, self.after, seconds=1, swaymsg=self.sway, runtime=str(self.tmp))
        t.start()
        t.keep()
        time.sleep(1.8)
        self.assertEqual(len(self.sent()), 1)                      # no undo

    def test_go_back_now_undoes_once(self):
        t = T.Trial(self.before, self.after, seconds=1, swaymsg=self.sway, runtime=str(self.tmp))
        t.start()
        t.revert_now()
        time.sleep(1.8)
        sent = self.sent()
        self.assertEqual(len(sent), 2)                             # change + one undo, not two
        self.assertIn("@144.", sent[1])

    def test_a_refused_change_is_undone_at_once(self):
        t = T.Trial(self.before, self.after, seconds=5, swaymsg=self.sway, runtime=str(self.tmp))
        t.forward = [c + " REFUSE" for c in t.forward]
        self.assertFalse(t.start())
        self.assertIn("@144.", self.sent()[-1])
        self.assertIsNone(t.watchdog)

    def test_it_comes_back_even_when_displayforge_dies(self):
        # A separate Python process tries the change and dies at once (no keep, no undo of its own)
        code = (f"import sys; sys.path.insert(0, {str(Path(__file__).resolve().parent.parent)!r})\n"
                "import json, os\nfrom dataclasses import replace\n"
                "from displayforge import screens as S, trial as T\n"
                f"b = S.parse(json.loads(open({str(Path(__file__).parent / 'data/three-sceptre-y27.json')!r}).read()))\n"
                "m = [s for s in b if s.name == 'DP-3'][0]\n"
                "h = [x for x in m.rates(2560, 1440) if x.hz == 120][0]\n"
                "a = [replace(s, mode=h) if s.name == 'DP-3' else s for s in b]\n"
                f"t = T.Trial(b, a, seconds=1, swaymsg={self.sway!r}, runtime={str(self.tmp)!r}); t.start()\n"
                "os._exit(0)\n")
        subprocess.run([sys.executable, "-c", code], check=True)
        self.assertEqual(len(self.sent()), 1)                      # it changed, then the app was gone
        time.sleep(1.8)
        self.assertEqual(len(self.sent()), 2)                      # the safety timer still undid it
        self.assertIn("@144.", self.sent()[1])

    def test_nothing_to_change_starts_no_timer(self):
        t = T.Trial(self.before, self.before, seconds=1, swaymsg=self.sway, runtime=str(self.tmp))
        self.assertTrue(t.start())
        self.assertIsNone(t.watchdog)
        self.assertEqual(self.sent(), [])


class Saving(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.out = self.tmp / "sway/outputs"
        self.bk = self.tmp / "backups"
        self.screens = S.parse(REAL)

    def test_first_save_needs_no_backup(self):
        path, backup = V.save(self.screens, self.out, self.bk)
        self.assertIsNone(backup)
        text = path.read_text()
        self.assertTrue(text.startswith("# Written by displayForge"))
        self.assertEqual(sum(1 for l in text.splitlines() if l.startswith("output DP-")), 3)

    def test_a_second_save_backs_up_the_first(self):
        V.save(self.screens, self.out, self.bk, now=1000)
        first = self.out.read_text()
        _, backup = V.save(self.screens, self.out, self.bk, now=2000)
        self.assertEqual(backup.read_text(), first)

    def test_only_twenty_backups_kept(self):
        for i in range(25):
            V.save(self.screens, self.out, self.bk, now=1000 + i)
        self.assertEqual(len(list(self.bk.glob("outputs-*"))), 20)

    def test_no_half_written_file_left_behind(self):
        V.save(self.screens, self.out, self.bk)
        self.assertEqual([p.name for p in self.out.parent.iterdir()], ["outputs"])

    def test_redirected_save_never_touches_the_real_file(self):
        # 2026-10-06: a default path fixed at import time sent a test's save to the real
        # ~/.config/sway/outputs. Redirecting the module's paths must be enough.
        real = Path.home() / ".config/sway/outputs"
        existed = real.exists()
        before = real.stat().st_mtime if existed else None
        old_out, old_bk = V.OUTPUTS, V.BACKUPS
        V.OUTPUTS, V.BACKUPS = self.out, self.bk
        try:
            path, _ = V.save(self.screens)
        finally:
            V.OUTPUTS, V.BACKUPS = old_out, old_bk
        self.assertEqual(path, self.out)
        self.assertTrue(self.out.exists())
        self.assertEqual(real.exists(), existed)
        if existed:
            self.assertEqual(real.stat().st_mtime, before)

    def test_included_finds_the_include_line(self):
        cfg = self.tmp / "config"
        cfg.write_text("output * bg x fill\n")
        self.assertFalse(V.included(cfg, self.out))
        cfg.write_text("output * bg x fill\ninclude ~/.config/sway/outputs\n")
        self.assertTrue(V.included(cfg, self.out))
        cfg.write_text("# include ~/.config/sway/outputs\n")
        self.assertFalse(V.included(cfg, self.out))


class Brightness(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.ddc = fake_tool(self.tmp, "ddcutil",
                             'case "$*" in\n'
                             '  "detect --brief") printf "Display 1\\n   I2C bus:  /dev/i2c-3\\nDisplay 2\\n   I2C bus:  /dev/i2c-5\\nDisplay 3\\n   I2C bus:  /dev/i2c-4\\n";;\n'
                             '  *getvcp*) echo "VCP 10 C 75 100";;\n'
                             f'  *setvcp*) echo "$*" >> {self.tmp}/set.log;;\n'
                             'esac\n')

    def test_steps_are_tens(self):
        self.assertEqual(B.STEPS, (10, 20, 30, 40, 50, 60, 70, 80, 90, 100))
        self.assertEqual([B.tens(v) for v in (0, 4, 75, 76, 99, 140)], [10, 10, 80, 80, 100, 100])

    def test_buses_and_reading(self):
        self.assertEqual(B.buses(self.ddc), [3, 4, 5])
        self.assertEqual(B.get(3, self.ddc), 75)

    def test_setting(self):
        self.assertTrue(B.set_(4, 70, self.ddc))
        self.assertIn("--bus 4 setvcp 10 70", (self.tmp / "set.log").read_text())

    def test_dim_comes_back_even_if_the_app_step_is_cancelled(self):
        # F-2: a click during the dim cancelled the app's step and the screen stayed dark.
        # Now the dim + restore is its own process: we start it and walk away (no wait).
        log = self.tmp / "set.log"
        proc = B.dim(4, seconds=1, before=75, ddcutil=self.ddc)
        time.sleep(0.3)
        self.assertEqual(log.read_text().splitlines(), ["--bus 4 setvcp 10 0"])      # dark
        time.sleep(1.6)
        self.assertEqual(log.read_text().splitlines()[-1], "--bus 4 setvcp 10 75")   # back
        proc.wait(timeout=5)                         # only now collected: the restore never needed us

    def test_dim_retries_until_the_screen_reports_it(self):
        # a screen that ignores the first two restore commands
        flaky = fake_tool(self.tmp, "ddcutil-flaky",
                          f'echo "$*" >> {self.tmp}/flaky.log\n'
                          'case "$*" in\n'
                          f'  *getvcp*) n=$(grep -c "setvcp 10 75" {self.tmp}/flaky.log); '
                          '[ "$n" -ge 3 ] && echo "VCP 10 C 75 100" || echo "VCP 10 C 0 100";;\n'
                          'esac\n')
        p = B.dim(4, seconds=0, before=75, ddcutil=flaky)
        self.assertEqual(p.wait(timeout=15), 0)
        sets = [l for l in (self.tmp / "flaky.log").read_text().splitlines() if "setvcp 10 75" in l]
        self.assertEqual(len(sets), 3)

    def test_dim_reports_failure_when_it_never_comes_back(self):
        dead = fake_tool(self.tmp, "ddcutil-dead", 'case "$*" in *getvcp*) echo "VCP 10 C 0 100";; esac\n')
        p = B.dim(4, seconds=0, before=75, ddcutil=dead, tries=2)
        self.assertEqual(p.wait(timeout=15), 1)

    def test_names_and_buses_remembered(self):
        cfg = self.tmp / "screens.toml"
        self.assertEqual(B.load(cfg), {"names": {}, "bus": {}})
        data = {"names": {"DP-3": "Main", "DP-2": 'Left "desk"'}, "bus": {"DP-3": 4, "DP-2": 5, "DP-1": 3}}
        B.save(data, cfg)
        self.assertEqual(B.load(cfg), data)


if __name__ == "__main__":
    unittest.main()
