"""defaultappsForge's brain, on throwaway files: the standard file kept intact, the old choices
tidied, only what changed written, the file types moved between default apps."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from defaultappsforge import system as S
from defaultappsforge.model import Session

FILE = """[Added Associations]
image/png=pinta.desktop;
inode/directory=thunar.desktop;nemo.desktop;
x-scheme-handler/http=chrome.desktop;brave-browser.desktop;

[Default Applications]
image/png=pinta.desktop;
inode/directory=thunar.desktop;
text/markdown=io.typora.Typora.desktop;
x-scheme-handler/http=chrome.desktop
x-scheme-handler/claude=claude.desktop

[Something Else]
keep=this;
"""

APPS = {
    "chrome.desktop": S.App("chrome.desktop", "Chrome", {"x-scheme-handler/http", "x-scheme-handler/https", "application/pdf"}),
    "chrome2.desktop": S.App("chrome2.desktop", "Chrome", {"x-scheme-handler/http"}),
    "pinta.desktop": S.App("pinta.desktop", "Pinta", {"image/x-pinta"}),
    "gimp.desktop": S.App("gimp.desktop", "GIMP", {"image/png", "image/jpeg"}),
    "thunar.desktop": S.App("thunar.desktop", "Thunar", {"inode/directory"}),
    "mpdf.desktop": S.App("mpdf.desktop", "Master PDF Editor", {"application/pdf"}),
    "alacritty.desktop": S.App("alacritty.desktop", "Alacritty", set(), {"TerminalEmulator"}),
    "thunderbird.desktop": S.App("thunderbird.desktop", "Thunderbird", {"text/calendar", "x-scheme-handler/mailto"}),
    "claude.desktop": S.App("claude.desktop", "Claude", {"x-scheme-handler/claude"}),
}


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        d = Path(self.dir.name)
        self.path = d / "mimeapps.list"
        self.path.write_text(FILE)
        self.backups = d / "backups"
        self.se = Session(apps=dict(APPS), mimeapps=S.MimeApps(self.path), pools_path=d / "settings.toml",
                          terminals=d / "xdg-terminals.list", ask_system=lambda t: {"application/pdf": "chrome.desktop"}.get(t))

    def tearDown(self):
        self.dir.cleanup()


class Reading(Base):
    def test_what_opens_each_now(self):
        se = self.se
        self.assertEqual(se.saved_apps["web"], "chrome.desktop")
        self.assertEqual(se.saved_apps["image"], "pinta.desktop")
        self.assertEqual(se.saved_apps["pdf"], "chrome.desktop", "nobody chose: the system's guess")
        self.assertIsNone(se.saved_apps["phone"])
        self.assertIsNone(se.saved_apps["terminal"], "no xdg-terminals.list yet")

    def test_only_apps_that_can_do_the_job_and_the_current_one(self):
        names = [a.name for a in self.se.candidates("image")]
        self.assertEqual(names, ["GIMP", "Pinta"], "Pinta declares no PNG but opens them now, so it is offered")
        self.assertEqual([a.id for a in self.se.candidates("terminal")], ["alacritty.desktop"])
        c = self.se.candidates("web")
        self.assertEqual({self.se.label(a, c) for a in c}, {"Chrome · chrome", "Chrome · chrome2"},
                         "two entries with one name are told apart")

    def test_old_choices_for_apps_that_are_gone(self):
        gone = {d for _s, _k, d in self.se.mime.gone(self.se.apps)}
        self.assertEqual(gone, {"nemo.desktop", "brave-browser.desktop", "io.typora.Typora.desktop"})


class Saving(Base):
    def test_a_choice_writes_only_its_types_and_keeps_everything_else(self):
        self.se.choose("pdf", "mpdf.desktop")
        rows = self.se.changes()
        self.assertEqual(rows[0], ("PDF Viewer", "Chrome", "Master PDF Editor"))
        self.assertEqual(rows[-1][0], "Old choices tidied")
        result = self.se.save(self.backups)
        text = self.path.read_text()
        self.assertIn("application/pdf=mpdf.desktop;", text)
        self.assertIn("[Something Else]\nkeep=this;", text, "sections we don't touch stay")
        self.assertIn("x-scheme-handler/claude=claude.desktop", text, "lines we don't touch stay")
        self.assertNotIn("nemo.desktop", text)
        self.assertNotIn("io.typora", text)
        self.assertIn("inode/directory=thunar.desktop;", text)
        self.assertTrue(result["backup"] and result["backup"].read_text() == FILE, "a backup of the old file first")
        self.assertEqual(self.se.change_count, 0)

    def test_nothing_changed_writes_nothing(self):
        self.assertEqual(self.se.change_count, 0)
        self.assertEqual(self.se.plan(), {})

    def test_a_file_type_moved_to_a_default_app(self):
        self.se.assign([".ics"], "calendar")
        self.assertIn(("File type .ics", "no default app", "Calendar"), self.se.changes())
        self.se.choose("calendar", "thunderbird.desktop")
        self.se.save(self.backups)
        self.assertIn("text/calendar=thunderbird.desktop;", self.path.read_text())

    def test_cleared_goes_back_to_the_systems_guess(self):
        self.se.clear([".gif"], "image")
        self.assertIn(".gif", self.se.unassigned())
        self.path.write_text(self.path.read_text().replace("[Default Applications]\n", "[Default Applications]\nimage/gif=gimp.desktop;\n"))
        se2 = Session(apps=dict(APPS), mimeapps=S.MimeApps(self.path), pools_path=self.se.pools_path,
                      terminals=self.se.terminals, ask_system=lambda t: None)
        se2.clear([".gif"], "image")
        se2.save(self.backups)
        self.assertNotIn("image/gif=", self.path.read_text())

    def test_one_file_type_one_default_app(self):
        self.se.assign([".png"], "pdf")
        self.assertNotIn(".png", self.se.pools["image"])
        self.assertIn(".png", self.se.pools["pdf"])

    def test_the_terminal_goes_to_xdg_terminal_execs_list(self):
        self.se.choose("terminal", "alacritty.desktop")
        self.se.save(self.backups)
        self.assertEqual(S.terminal_now(self.se.terminals, self.se.apps), "alacritty.desktop")

    def test_file_types_survive_a_restart(self):
        self.se.assign([".csv"], "office")
        self.se.save(self.backups)
        se2 = Session(apps=dict(APPS), mimeapps=S.MimeApps(self.path), pools_path=self.se.pools_path,
                      terminals=self.se.terminals, ask_system=lambda t: None)
        self.assertIn(".csv", se2.pools["office"])

    def test_only_twenty_backups(self):
        for i in range(25):
            self.se.choose("pdf", "mpdf.desktop" if i % 2 == 0 else "chrome.desktop")
            self.se.save(self.backups)
        self.assertEqual(len(list(self.backups.glob("mimeapps.list.*"))), 20)


class Installed(unittest.TestCase):
    def test_reading_desktop_entries(self):
        with tempfile.TemporaryDirectory() as d:
            a = Path(d) / "a"
            a.mkdir()
            (a / "x.desktop").write_text("[Desktop Entry]\nType=Application\nName=X\nExec=x\nMimeType=image/png;\n")
            (a / "h.desktop").write_text("[Desktop Entry]\nType=Application\nName=H\nExec=h\nNoDisplay=true\n"
                                         "MimeType=x-scheme-handler/geo;\n")
            (a / "gone.desktop").write_text("[Desktop Entry]\nType=Application\nName=G\nExec=g\nHidden=true\n")
            apps = S.installed([a])
            self.assertEqual(set(apps), {"x.desktop", "h.desktop"}, "helpers count (map handlers); hidden ones don't")
            self.assertEqual(apps["x.desktop"].types, {"image/png"})


class NoFileYet(unittest.TestCase):
    def test_a_new_user_with_no_file_gets_one(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "mimeapps.list"
            se = Session(apps=dict(APPS), mimeapps=S.MimeApps(path), pools_path=Path(d) / "s.toml",
                         terminals=Path(d) / "t.list", ask_system=lambda t: None)
            se.choose("pdf", "mpdf.desktop")
            result = se.save(Path(d) / "backups")
            self.assertIsNone(result["backup"], "nothing to back up")
            self.assertEqual(path.read_text().splitlines()[0], "[Default Applications]")
            self.assertIn("application/pdf=mpdf.desktop;", path.read_text())


if __name__ == "__main__":
    unittest.main()
