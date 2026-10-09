"""nightForge's core: the settings, the sun, and starting / nudging / stopping the night light —
with a stand-in night light (tests/fake-wlsunset) that never touches a screen."""

from __future__ import annotations

import os
import tempfile
import time
import tomllib
import unittest
from datetime import date, datetime
from pathlib import Path

from nightforge import control as C
from nightforge.settings import Settings, clock, describe
from nightforge.sun import sun_times

HERE = Path(__file__).resolve().parent
FAKE = HERE / "fake-wlsunset"


class SettingsFile(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "settings.toml"
        self.backups = Path(self.dir.name) / "backups"

    def tearDown(self):
        self.dir.cleanup()

    def test_no_file_is_todays_night_light(self):
        s = Settings.load(self.path)
        self.assertEqual((s.enabled, s.warmth, s.schedule, s.latitude, s.longitude), (True, 4000, "sun", 25.77, -80.19))
        self.assertEqual(s.wlsunset_args(), ["-t", "4000", "-T", "6500", "-l", "25.77", "-L", "-80.19"])

    def test_fixed_times_become_wlsunsets_options(self):
        s = Settings(schedule="fixed", warm_from="21:00", day_from="7:5", fade_minutes=30).checked()
        self.assertEqual(s.day_from, "07:05")
        self.assertEqual(s.wlsunset_args(), ["-t", "4000", "-T", "6500", "-s", "21:00", "-S", "07:05", "-d", "1800"])

    def test_bad_values_become_ones_wlsunset_accepts(self):
        self.path.write_text('warmth = 9000\nlatitude = 200\nwarm_from = "late"\nschedule = "moon"\n')
        s = Settings.load(self.path)
        self.assertEqual(s.warmth, 6400, "night must stay below day (wlsunset refuses otherwise)")
        self.assertEqual((s.latitude, s.warm_from, s.schedule), (90.0, "21:00", "sun"))
        self.path.write_text("this is [ not toml")
        self.assertEqual(Settings.load(self.path), Settings())

    def test_save_backs_up_first_and_reads_back(self):
        Settings(warmth=3500).save(self.path, self.backups)
        backup = Settings(warmth=3000, schedule="fixed").save(self.path, self.backups)
        self.assertTrue(backup and "warmth = 3500" in backup.read_text())
        data = tomllib.loads(self.path.read_text())
        self.assertEqual((data["warmth"], data["schedule"]), (3000, "fixed"))
        for i in range(25):
            Settings(warmth=3000 + i).save(self.path, self.backups)
        self.assertEqual(len(list(self.backups.glob("settings.toml.*"))), 20)

    def test_words(self):
        self.assertEqual(clock("9:3", ""), "09:03")
        self.assertEqual(clock("25:00", "x"), "x")
        self.assertEqual(describe(3000), "very warm")
        self.assertEqual(describe(4100), "gentle")
        self.assertEqual(Settings().place_words(), "25.8° N, 80.2° W")


class Sun(unittest.TestCase):
    def test_miami_today_june_and_the_midnight_sun(self):
        from zoneinfo import ZoneInfo
        ny = ZoneInfo("America/New_York")
        rise, sset = sun_times(date(2026, 10, 9), 25.77, -80.19, ny)
        self.assertEqual((rise.strftime("%H:%M"), sset.strftime("%H:%M")), ("07:15", "19:00"))
        rise, sset = sun_times(date(2026, 6, 21), 25.77, -80.19, ny)
        self.assertEqual((rise.strftime("%H:%M"), sset.strftime("%H:%M")), ("06:29", "20:14"))
        self.assertEqual(sun_times(date(2026, 6, 21), 78.2, 15.6), (None, None), "Svalbard in June: no sunset")


class NightLight(unittest.TestCase):
    """Start, nudge, stop — on the stand-in."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        d = Path(self.dir.name)
        self.log = d / "fake.log"
        self.saved = {k: getattr(C, k) for k in ("PROGRAM", "RUNTIME", "PIDFILE", "MODEFILE", "STATE", "LOG")}
        C.PROGRAM = str(FAKE)
        C.RUNTIME = d / "run"
        C.PIDFILE, C.MODEFILE = C.RUNTIME / "wlsunset.pid", C.RUNTIME / "mode"
        C.STATE = d / "state"
        C.LOG = C.STATE / "wlsunset.log"
        os.environ["NIGHTFORGE_FAKE_LOG"] = str(self.log)
        os.environ.pop("NIGHTFORGE_FAKE_FAIL", None)

    def tearDown(self):
        C.stop()
        for k, v in self.saved.items():
            setattr(C, k, v)
        self.dir.cleanup()

    def events(self):
        time.sleep(0.3)
        return self.log.read_text().split("\n") if self.log.exists() else []

    def test_automatic_starts_it_with_the_settings(self):
        pid = C.start(Settings(), "auto")
        self.assertTrue(pid and C.running_pid() == pid)
        ev = self.events()
        self.assertIn("start -t 4000 -T 6500 -l 25.77 -L -80.19", ev)
        self.assertNotIn("usr1", ev)
        self.assertEqual(C.mode(), "auto")

    def test_warm_now_is_two_nudges_from_a_fresh_start(self):
        C.start(Settings(), "auto")
        C.start(Settings(), "warm")
        ev = self.events()
        self.assertEqual(ev.count("stop"), 1, "the old one stopped first")
        self.assertEqual(ev[ev.index("stop"):].count("usr1"), 2, "forced day, then forced warm")
        self.assertEqual(C.mode(), "warm")

    def test_daylight_now_and_off_leave_nothing_running(self):
        C.start(Settings(), "auto")
        self.assertIsNone(C.start(Settings(), "day"))
        self.assertIsNone(C.running_pid())
        self.assertIsNone(C.start(Settings(enabled=False), "auto"))
        self.assertIsNone(C.running_pid())
        self.assertEqual(C.status(Settings(enabled=False))["state"], "off")

    def test_a_preview_uses_its_own_warmth(self):
        C.start(Settings(), "warm", warmth=3000)
        self.assertTrue(any(e.startswith("start -t 3000 ") for e in self.events()))

    def test_one_that_wont_start_says_why(self):
        os.environ["NIGHTFORGE_FAKE_FAIL"] = "1"
        with self.assertRaisesRegex(C.Trouble, "no gamma control here"):
            C.start(Settings(), "auto")
        os.environ.pop("NIGHTFORGE_FAKE_FAIL")

    def test_status_in_words(self):
        s = Settings()
        C.start(s, "auto")
        evening = datetime(2026, 10, 9, 20, 30).astimezone()
        noon = datetime(2026, 10, 9, 12, 0).astimezone()
        self.assertEqual(C.status(s, evening)["state"], "warm")
        self.assertEqual(C.status(s, noon)["state"], "day")
        C.start(s, "warm")
        self.assertIn("Warm Now", C.status(s, noon)["why"])


if __name__ == "__main__":
    unittest.main()
