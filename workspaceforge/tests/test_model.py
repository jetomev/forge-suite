"""workspaceForge's model: reading the applet's file, editing, the words for the changes, the
windows that follow their workspace, and writing it back safely."""

from __future__ import annotations

import os
import tempfile
import tomllib
import unittest
from pathlib import Path

from workspaceforge import model as M

FILE = '''
enabled = true
screens = ["DP-3", "DP-2", "DP-1"]
[[workspace]]
name = "Daily"
apps = ["google-chrome", "discord"]
[[workspace]]
name = "Work"
apps = ["obsidian"]
[[workspace]]
name = "Entertainment"
apps = ["spotify"]
[[workspace]]
name = "Gaming"
apps = ["steam"]
[share]
"DP-3" = []
"DP-2" = [["Daily", "Work"]]
"DP-1" = []
'''


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "workspaces.toml"
        self.path.write_text(FILE)
        self._backups = M.BACKUPS
        M.BACKUPS = Path(self.dir.name) / "backups"
        self.se = M.Session.load(self.path)

    def tearDown(self):
        M.BACKUPS = self._backups
        self.dir.cleanup()

    def uid(self, name):
        return next(w.uid for w in self.se.pending.workspaces if w.name == name)


class Reading(Base):
    def test_it_reads_the_applets_file(self):
        p = self.se.pending
        self.assertEqual([w.name for w in p.workspaces], ["Daily", "Work", "Entertainment", "Gaming"])
        self.assertEqual(p.get(self.uid("Gaming")).apps, ["steam"])
        self.assertEqual(p.shared["DP-2"], {self.uid("Daily"), self.uid("Work")})
        self.assertEqual(self.se.change_count, 0)

    def test_cells_use_the_applets_names(self):
        p = self.se.pending
        self.assertEqual(p.cell(self.uid("Gaming"), "DP-3"), "4:Gaming")
        self.assertEqual(p.cell(self.uid("Gaming"), "DP-1"), "24:Gaming")
        self.assertEqual(p.cell(self.uid("Daily"), "DP-2"), "111:Shared")
        self.assertEqual(p.cell(self.uid("Entertainment"), "DP-2"), "13:Entertainment")

    def test_a_missing_file_is_an_empty_start(self):
        se = M.Session.load(Path(self.dir.name) / "none.toml")
        self.assertEqual(se.pending.workspaces, [])


class Editing(Base):
    def test_new_rename_delete_move_said_in_words(self):
        se = self.se
        studio = se.add("Studio", after=self.uid("Gaming"))
        se.rename(self.uid("Entertainment"), "Media")
        se.delete(self.uid("Work"), move_to=self.uid("Daily"))
        se.move(studio, -1)
        rows = {r[0]: r[1:] for r in se.changes()}
        self.assertIn("New workspace", rows)
        self.assertEqual(rows["Workspace 2 · name"], ("Entertainment", "Media"))
        self.assertEqual(rows["Deleted · Work"], ("Win + 2", "its windows to Daily"))
        self.assertIn("App · obsidian", rows, "a deleted workspace's apps go back to where you are")
        self.assertEqual(rows["App · obsidian"], ("Work", "where you are"))
        self.assertEqual([w.name for w in se.pending.workspaces], ["Daily", "Media", "Studio", "Gaming"])

    def test_a_rename_is_one_change_its_apps_stay(self):
        """Found in the 0.1.0 pictures: renaming Entertainment counted each of its apps as moved."""
        self.se.rename(self.uid("Entertainment"), "Media")
        self.assertEqual(self.se.changes(), [("Workspace 3 · name", "Entertainment", "Media")])

    def test_names_are_checked(self):
        with self.assertRaises(M.Problem):
            self.se.add("  ", None)
        with self.assertRaises(M.Problem):
            self.se.add("daily", None)
        with self.assertRaises(M.Problem):
            self.se.rename(self.uid("Work"), 'Say "hi"')
        self.assertEqual(self.se.rename(self.uid("Work"), "  Deep   Work "), "Deep Work")

    def test_one_always_stays_and_nine_is_the_most(self):
        se = self.se
        for n in ("Work", "Entertainment", "Gaming"):
            se.delete(self.uid(n), move_to=self.uid("Daily"))
        with self.assertRaisesRegex(M.Problem, "always stays"):
            se.delete(self.uid("Daily"), move_to=self.uid("Daily"))
        for i in range(8):
            se.add(f"W{i}", None)
        with self.assertRaises(M.Problem):
            se.add("Tenth", None)

    def test_one_app_one_workspace(self):
        self.se.assign(["discord"], self.uid("Gaming"))
        p = self.se.pending
        self.assertNotIn("discord", p.get(self.uid("Daily")).apps)
        self.assertIn("discord", p.get(self.uid("Gaming")).apps)
        self.assertIn(("App · Discord", "Daily", "Gaming"), self.se.changes({"discord": "Discord"}))
        self.se.unassign(["discord"], self.uid("Gaming"))
        self.assertIsNone(p.where("discord"))

    def test_sharing_one_group_per_screen(self):
        se = self.se
        se.set_shared("DP-1", self.uid("Gaming"), True)
        self.assertEqual(se.change_count, 0, "one cell alone shares nothing")
        se.set_shared("DP-1", self.uid("Entertainment"), True)
        self.assertIn(("Sharing · DP-1", "not shared", "Entertainment, Gaming"), se.changes())

    def test_discard_puts_everything_back(self):
        self.se.rename(self.uid("Work"), "Job")
        self.se.discard()
        self.assertEqual(self.se.change_count, 0)


class WindowsFollow(Base):
    def test_a_rename_carries_each_screens_part(self):
        self.se.rename(self.uid("Gaming"), "Games")
        cmds = [c for c, _ in self.se.window_moves()]
        self.assertIn('rename workspace "4:Gaming" to "wf-4-0"', cmds)
        self.assertIn('rename workspace "wf-4-0" to "4:Games"', cmds)
        self.assertIn('rename workspace "wf-4-2" to "24:Games"', cmds)
        self.assertLess(cmds.index('rename workspace "4:Gaming" to "wf-4-0"'),
                        cmds.index('rename workspace "wf-4-0" to "4:Games"'))

    def test_a_swap_goes_through_temporary_names(self):
        self.se.move(self.uid("Gaming"), -1)       # Entertainment and Gaming swap numbers
        cmds = [c for c, _ in self.se.window_moves()]
        holds = [c for c in cmds if 'to "wf-' in c]
        finals = [c for c in cmds if c.startswith('rename workspace "wf-')]
        self.assertTrue(holds and finals)
        self.assertLess(max(cmds.index(c) for c in holds), min(cmds.index(c) for c in finals))
        self.assertIn('rename workspace "wf-4-0" to "3:Gaming"', cmds)
        self.assertIn('rename workspace "wf-3-0" to "4:Entertainment"', cmds)

    def test_a_deleted_workspaces_windows_go_where_you_chose(self):
        self.se.delete(self.uid("Entertainment"), move_to=self.uid("Gaming"))
        cmds = [c for c, _ in self.se.window_moves()]
        # Gaming becomes 3, so its parts are held under temporary names while the windows arrive
        self.assertIn('[workspace="^3:Entertainment$"] move container to workspace "wf-4-0"', cmds)
        self.assertIn('rename workspace "wf-4-0" to "3:Gaming"', cmds)

    def test_shared_spaces_are_left_to_the_applet(self):
        self.se.rename(self.uid("Daily"), "Home")
        cmds = [c for c, _ in self.se.window_moves()]
        self.assertFalse(any("Shared" in c for c in cmds))
        self.assertIn('rename workspace "1:Daily" to "wf-1-0"', cmds)

    def test_a_screen_starting_to_share_is_left_to_the_applet(self):
        """Found in the 0.1.0 pictures: three workspaces starting to share a screen were all
        being renamed to the same shared name."""
        for n in ("Entertainment", "Gaming"):
            self.se.set_shared("DP-1", self.uid(n), True)
        self.assertEqual(self.se.window_moves(), [])
        self.assertIn(("Sharing · Right", "not shared", "Entertainment, Gaming"),
                      self.se.changes(screen_names={"DP-1": "Right"}))

    def test_nothing_moves_when_only_apps_change(self):
        self.se.assign(["vlc"], self.uid("Entertainment"))
        self.assertEqual(self.se.window_moves(), [])


class Writing(Base):
    def test_it_writes_a_backup_first_and_reads_back(self):
        self.se.rename(self.uid("Work"), "Job")
        self.se.assign(["discord"], self.uid("Gaming"))
        backup = self.se.write()
        self.assertTrue(backup and backup.exists())
        self.assertEqual(backup.read_text(), FILE)
        cfg = tomllib.loads(self.path.read_text())
        self.assertEqual([w["name"] for w in cfg["workspace"]], ["Daily", "Job", "Entertainment", "Gaming"])
        self.assertEqual(cfg["workspace"][3]["apps"], ["steam", "discord"])
        self.assertEqual(cfg["share"]["DP-2"], [["Daily", "Job"]], "sharing follows a rename")
        self.se.saved_now()
        self.assertEqual(self.se.change_count, 0)

    def test_only_twenty_backups_are_kept(self):
        for i in range(25):
            self.se.rename(self.uid("Work") if i == 0 else self.se.pending.workspaces[1].uid, f"Job{i}")
            self.se.write()
            self.se.saved_now()
        self.assertEqual(len(list(M.BACKUPS.glob("workspaces.toml.*"))), 20)


if __name__ == "__main__":
    unittest.main()
