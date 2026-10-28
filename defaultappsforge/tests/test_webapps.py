"""Web apps as default apps (D-5, Javier, 2026-10-27: "I cannot select among the apps, for email or calendar,
chrome (gmail.com apps) which should be available")."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from defaultappsforge import system as S  # noqa: E402
from defaultappsforge import webapps as W  # noqa: E402
from defaultappsforge.model import Session  # noqa: E402

APPS = {"org.mozilla.Thunderbird.desktop": S.App("org.mozilla.Thunderbird.desktop", "Thunderbird",
                                                 {"x-scheme-handler/mailto", "message/rfc822", "text/calendar"}),
        "google-chrome.desktop": S.App("google-chrome.desktop", "Google Chrome",
                                       {"x-scheme-handler/http", "x-scheme-handler/https", "text/html"})}


class Choices(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        d = Path(self.dir.name)
        (d / "mimeapps.list").write_text("[Default Applications]\nx-scheme-handler/mailto=org.mozilla.Thunderbird.desktop\n")
        self.d = d
        self.se = Session(apps=dict(APPS), mimeapps=S.MimeApps(d / "mimeapps.list"), pools_path=d / "s.toml",
                          terminals=d / "t.list", ask_system=lambda t: None, apps_dir=d / "applications")

    def tearDown(self):
        self.dir.cleanup()

    def test_gmail_and_outlook_are_email_choices(self):
        names = [a.name for a in self.se.candidates("email")]
        self.assertIn("Gmail · web app", names)
        self.assertIn("Outlook · web app", names)
        self.assertIn("Thunderbird", names)

    def test_calendar_maps_and_phone_get_theirs(self):
        self.assertIn("Google Calendar · web app", [a.name for a in self.se.candidates("calendar")])
        self.assertIn("OpenStreetMap · web app", [a.name for a in self.se.candidates("map")])
        self.assertIn("Google Voice · web app", [a.name for a in self.se.candidates("phone")])

    def test_never_for_files(self):
        for key in ("music", "office", "image", "pdf", "video", "text"):
            self.assertFalse([a for a in self.se.candidates(key) if W.is_web(a.id)], key)

    def test_choosing_gmail_writes_its_launcher_and_takes_email_links_only(self):
        self.se.choose("email", "kognogos-web-gmail.desktop")
        plan = self.se.plan()
        self.assertEqual(plan["x-scheme-handler/mailto"], ["kognogos-web-gmail.desktop"])
        self.assertNotIn("message/rfc822", plan, "an .eml file never goes to a web page")
        self.se.save(backups=self.d / "b")
        launcher = self.d / "applications/kognogos-web-gmail.desktop"
        self.assertTrue(launcher.exists())
        text = launcher.read_text()
        self.assertIn("MimeType=x-scheme-handler/mailto;", text)
        self.assertIn("webapp-open gmail %u", text)
        self.assertIn("x-scheme-handler/mailto=kognogos-web-gmail.desktop", (self.d / "mimeapps.list").read_text())


class AppLibrary(unittest.TestCase):
    """YouTube Music and Google Docs: in the App Library, never a default (they can't open your files)."""
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.d = Path(self.dir.name) / "applications"

    def tearDown(self):
        self.dir.cleanup()

    def test_added_with_no_links_to_take(self):
        self.assertEqual(W.to_library(["youtube-music", "google-docs"], self.d), ["youtube-music", "google-docs"])
        for key in ("youtube-music", "google-docs"):
            text = (self.d / f"kognogos-web-{key}.desktop").read_text()
            self.assertNotIn("MimeType=", text)
            self.assertIn(f"webapp-open {key} %u", text)

    def test_taken_out_again(self):
        W.to_library(["youtube-music"], self.d)
        self.assertEqual(W.to_library(["youtube-music", "google-docs"], self.d, remove=True), ["youtube-music"])
        self.assertFalse(list(self.d.iterdir()))

    def test_a_wrong_name_changes_nothing(self):
        self.assertEqual(W.main(["--add", "youtube-music", "nope"]), 2)
        self.assertEqual(W.main(["--add"]), 2)

    def test_never_a_choice_for_any_job(self):
        for w in W.LIBRARY_ONLY:
            self.assertIsNone(w.role)
            self.assertNotIn(w, W.WEB_APPS)


class Addresses(unittest.TestCase):
    def test_an_email_link_opens_a_new_message(self):
        self.assertEqual(W.address(W.BY_KEY["gmail"], "mailto:ana@example.com?subject=Hi"),
                         "https://mail.google.com/mail/?extsrc=mailto&url=mailto%3Aana%40example.com%3Fsubject%3DHi")

    def test_a_day_opens_that_day(self):
        self.assertEqual(W.address(W.BY_KEY["google-calendar"], day="2026-10-30"),
                         "https://calendar.google.com/calendar/r/day/2026/10/30")
        self.assertEqual(W.address(W.BY_KEY["outlook-calendar"], day="2026-10-30"),
                         "https://outlook.office.com/calendar/view/day/2026/10/30")

    def test_places_and_numbers(self):
        self.assertEqual(W.address(W.BY_KEY["openstreetmap"], "geo:25.77,-80.19"),
                         "https://www.openstreetmap.org/search?query=25.77,-80.19")
        self.assertEqual(W.address(W.BY_KEY["google-voice"], "tel:+13055551234"),
                         "https://voice.google.com/u/0/calls?a=nc,+13055551234")

    def test_nothing_to_open_its_home(self):
        self.assertEqual(W.address(W.BY_KEY["gmail"]), "https://mail.google.com/mail/")


class Browser(unittest.TestCase):
    def test_its_own_window_in_a_chromium_browser(self):
        self.assertEqual(W.browser_command("https://x", which=lambda n: n == "brave", ask=lambda: "brave-browser.desktop"),
                         ["brave", "--app=https://x"])

    def test_a_tab_in_any_other(self):
        self.assertEqual(W.browser_command("https://x", which=lambda n: False, ask=lambda: "firefox.desktop"),
                         ["xdg-open", "https://x"])


if __name__ == "__main__":
    unittest.main()
