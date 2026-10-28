"""The Quick Search on Win + Space (D-124, Javier, 2026-10-27: "search of anything (apps, files, history,
whatnot, whatever)"; "When Win+Space is pressed what needs to appear first is just the search")."""

from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/panels"))
sys.path.insert(0, str(HERE / "applets/panels/views"))
import quicksearch as qs  # noqa: E402

APPS = {"google-chrome": {"name": "Google Chrome", "icon": "google-chrome", "comment": "Access the Internet"},
        "themeforge": {"name": "themeForge", "icon": "preferences-desktop-theme", "comment": "the look of your desktop"},
        "steam": {"name": "Steam", "icon": "steam", "comment": "Games"}}
PAGES = [{"name": "Look", "summary": "styles, colours and wallpaper"}, {"name": "Screens", "summary": "arrange"}]


def ran(stdout):
    return lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, stdout, "")


class NothingUntilYouType(unittest.TestCase):
    def test_an_empty_box_shows_nothing(self):
        self.assertEqual(qs.sections_for("", APPS, PAGES), [])
        self.assertEqual(qs.sections_for("   ", APPS, PAGES), [])


class AppsAndSettings(unittest.TestCase):
    def test_names_first_then_their_line(self):
        rows = qs.search_apps("the", APPS, PAGES)
        self.assertEqual(rows[0]["name"], "themeForge")
        self.assertIn("hypeForge Settings · Look", [r["name"] for r in qs.search_apps("look", APPS, PAGES)])

    def test_a_settings_page_opens_on_its_page(self):
        page = qs.search_apps("look", APPS, PAGES)[0]
        self.assertEqual(page["open"][-1], "Look")
        self.assertIn("hypeforge-settings", page["open"][-2])

    def test_an_app_opens_through_the_launcher_on_its_workspace(self):
        app = qs.search_apps("chrome", APPS, PAGES)[0]
        self.assertEqual(app["open"][1:], ["launch", "google-chrome"])


class Files(unittest.TestCase):
    def test_the_exact_name_then_the_shortest(self):
        home = Path("/home/x")
        out = "\n".join(str(home / p) for p in ("a/b/c/kognog", "Programs/kognog/", "Pictures/kognogos-grub-bg.png",
                                                 "One Drive/Kognog"))
        rows = qs.search_files("kognog", ran(out), home)
        self.assertEqual(rows[0]["name"], "Kognog" if rows[0]["sub"] == "/home/x/One Drive" else rows[0]["name"])
        self.assertEqual([r["name"].lower() for r in rows[:3]], ["kognog", "kognog", "kognog"])
        self.assertEqual(rows[-1]["name"], "kognogos-grub-bg.png", "a name that only starts with it comes after")

    def test_one_letter_asks_nothing(self):
        self.assertEqual(qs.search_files("k", ran("/home/x/k")), [])

    def test_fd_is_asked_for_names_inside_the_home_folder_only(self):
        seen = {}
        qs.search_files("todo", lambda cmd, **kw: (seen.update(cmd=cmd), subprocess.CompletedProcess(cmd, 0, "", ""))[1],
                        Path("/home/x"))
        cmd = seen["cmd"]
        self.assertEqual(cmd[0], "fd")
        self.assertIn("--one-file-system", cmd)
        self.assertEqual(cmd[-2:], ["todo", "/home/x"])


class BrowserHistory(unittest.TestCase):
    def setUp(self):
        self.chrome = Path(tempfile.mkdtemp())
        now_us = int((time.time() + 11_644_473_600) * 1_000_000)
        for folder, rows in (("Default", [("https://kognogos.org/", "KognogOS — the distro", now_us),
                                          ("https://example.com/?ref=kog", "Something else", now_us + 5)]),
                             ("Profile 1", [("https://github.com/jetomev/kognog", "jetomev/kognog", now_us - 86_400_000_000)])):
            (self.chrome / folder).mkdir()
            con = sqlite3.connect(self.chrome / folder / "History")
            con.execute("CREATE TABLE urls (id INTEGER PRIMARY KEY, url TEXT, title TEXT, last_visit_time INTEGER, "
                        "hidden INTEGER DEFAULT 0)")
            con.executemany("INSERT INTO urls (url, title, last_visit_time) VALUES (?, ?, ?)", rows)
            con.commit()
            con.close()
        (self.chrome / "Local State").write_text('{"profile": {"info_cache": {"Default": {"name": "Javier"}, '
                                                 '"Profile 1": {"name": "Work"}}}}')

    def test_titles_first_every_profile_named(self):
        rows = qs.search_history("kog", self.chrome)
        names = [r["name"] for r in rows]
        self.assertEqual(names[-1], "Something else", "only in the address: last")
        self.assertIn("jetomev/kognog", names)
        self.assertTrue(any(r["sub"].endswith("· Work") for r in rows), rows)
        self.assertTrue(any("visited today" in r["sub"] for r in rows))

    def test_it_opens_in_its_own_profile(self):
        row = next(r for r in qs.search_history("kog", self.chrome) if r["name"] == "jetomev/kognog")
        self.assertEqual(row["open"][:2], ["google-chrome", "--profile-directory=Profile 1"])

    def test_read_only_the_file_is_untouched(self):
        db = self.chrome / "Default/History"
        before = db.read_bytes()
        qs.search_history("kog", self.chrome)
        self.assertEqual(db.read_bytes(), before)


class Clipboard(unittest.TestCase):
    def test_what_you_copied_newest_first(self):
        out = "9\thttps://kognogos.org\n8\t[[ binary data 2 KiB png ]]\n7\tKognog notes\n"
        rows = qs.search_clipboard("kog", ran(out))
        self.assertEqual([r["name"] for r in rows], ["https://kognogos.org", "Kognog notes"])
        self.assertEqual(rows[0]["line"], "9\thttps://kognogos.org")


class Do(unittest.TestCase):
    def test_sums(self):
        self.assertEqual(qs.calculate(" (3+4)*12"), 84)
        self.assertEqual(qs.calculate("2**10"), 1024)
        self.assertEqual(qs.calculate("7 / 2"), 3.5)
        self.assertEqual(qs.calculate("12 × 7"), 84)

    def test_only_sums(self):
        for bad in ("__import__('os').system('true')", "open('/etc/passwd')", "2**10000", "1/0", "x + 1", "[1,2]"):
            self.assertIsNone(qs.calculate(bad), bad)

    def test_equals_shows_only_the_answer_and_copies_it(self):
        secs = qs.sections_for("= 6*7", APPS, PAGES)
        self.assertEqual([h for h, _ in secs], ["DO"])
        self.assertEqual(secs[0][1][0]["copy"], "42")

    def test_greater_than_runs_a_command_in_a_terminal(self):
        row = qs.sections_for("> htop", APPS, PAGES)[0][1][0]
        self.assertEqual(row["open"], ["alacritty", "--hold", "-e", "sh", "-c", "htop"])

    def test_anything_else_offers_a_web_search(self):
        row = qs.do_rows("kognog os")[0]
        self.assertEqual(row["open"], ["xdg-open", "https://www.google.com/search?q=kognog+os"])


class BestMatch(unittest.TestCase):
    def test_a_strong_app_wins(self):
        secs = qs.sections_for("steam", APPS, PAGES, {"files": [{"name": "steamapps", "score": 3}]})
        self.assertEqual(secs[0], ("BEST MATCH", [qs.search_apps("steam", APPS, PAGES)[0]]))

    def test_else_a_file_that_starts_with_it(self):
        f = {"kind": "file", "name": "kognog", "score": 3, "sub": "~/Programs", "icon": "folder-symbolic"}
        secs = qs.sections_for("kog", APPS, PAGES, {"files": [f]})
        self.assertEqual(secs[0], ("BEST MATCH", [f]))
        self.assertNotIn(f, dict(secs).get("FILES", []), "not shown twice")

    def test_the_headings_in_order(self):
        f = {"kind": "file", "name": "a-steam-thing", "score": 1}
        h = {"kind": "history", "name": "Steam store", "score": 4, "when": 1}
        heads = [x for x, _ in qs.sections_for("steam", APPS, PAGES, {"files": [f], "history": [h]})]
        self.assertEqual(heads, ["BEST MATCH", "FILES", "BROWSER HISTORY", "DO"])


class WinSpace(unittest.TestCase):
    def test_win_space_opens_the_quick_search(self):
        conf = (HERE / "sway/config").read_text()
        self.assertRegex(conf, r"bindsym \$mod\+space exec \S+hypeforge-panel search")


if __name__ == "__main__":
    unittest.main()
