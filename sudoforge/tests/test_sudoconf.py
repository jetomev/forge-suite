"""sudo's settings file (D-3): text changes, and the admin part on throwaway files."""

from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path

from sudoforge.sudoconf import MARK, Refused, applied, apply_text, current_askpass, root_main, undo_text

STOCK = "# Sudo askpass:\n#   Path askpass /path/to/askpass\n#Path askpass /usr/X11R6/bin/ssh-askpass\n"
HELPER = "/usr/lib/sudoforge/sudoforge-askpass"


class Text(unittest.TestCase):
    def test_stock_file_has_no_active_helper(self):
        self.assertIsNone(current_askpass(STOCK), "commented lines are not active")

    def test_apply_adds_two_marked_lines_and_keeps_the_rest(self):
        new = apply_text(STOCK, HELPER)
        self.assertTrue(new.startswith(STOCK))
        self.assertTrue(new.endswith(f"{MARK}\nPath askpass {HELPER}\n"))
        self.assertTrue(applied(new, HELPER))

    def test_apply_twice_changes_nothing_more(self):
        once = apply_text(STOCK, HELPER)
        self.assertEqual(apply_text(once, HELPER), once)

    def test_another_helper_is_left_alone(self):
        theirs = STOCK + "Path askpass /usr/bin/ksshaskpass\n"
        with self.assertRaises(Refused) as e:
            apply_text(theirs, HELPER)
        self.assertIn("ksshaskpass", str(e.exception))

    def test_bad_helper_paths_are_refused(self):
        for bad in ("relative/path", "/with space", "/with\nnewline"):
            with self.assertRaises(Refused):
                apply_text(STOCK, bad)

    def test_undo_removes_only_our_lines(self):
        later = apply_text(STOCK, HELPER) + "Set disable_coredump false\n"
        self.assertEqual(undo_text(later), STOCK + "Set disable_coredump false\n")
        self.assertEqual(undo_text(STOCK), STOCK, "nothing of ours, nothing changed")

    def test_a_file_without_a_final_newline(self):
        new = apply_text("Set x y", HELPER)
        self.assertIn("Set x y\n" + MARK, new)


class AsAdmin(unittest.TestCase):
    """root_main on throwaway files (it is the same code pkexec runs on /etc/sudo.conf)."""

    def setUp(self):
        d = Path(tempfile.mkdtemp())
        self.conf, self.backup = d / "sudo.conf", d / "sudo.conf.sudoforge-backup"
        self.conf.write_text(STOCK)
        os.chmod(self.conf, 0o644)

    def run_root(self, *args):
        return root_main(list(args), conf=str(self.conf), backup=str(self.backup))

    def test_apply_then_undo(self):
        self.assertEqual(self.run_root("apply", HELPER), 0)
        self.assertTrue(applied(self.conf.read_text(), HELPER))
        self.assertEqual(self.backup.read_text(), STOCK, "backup taken before the change")
        self.assertEqual(stat.S_IMODE(self.conf.stat().st_mode), 0o644, "same permissions")
        self.assertEqual(self.run_root("undo"), 0)
        self.assertEqual(self.conf.read_text(), STOCK)

    def test_a_second_setup_keeps_the_original_backup(self):
        """F-2 (#37): setup from the repo, then again from the package — the backup stays the original."""
        self.assertEqual(self.run_root("apply", "/home/someone/forge-suite/sudoforge/sudoforge-askpass"), 0)
        self.assertEqual(self.run_root("apply", HELPER), 0)
        self.assertTrue(applied(self.conf.read_text(), HELPER), "the new helper is in place")
        self.assertEqual(self.backup.read_text(), STOCK, "the backup is still the file from before sudoForge")

    def test_setup_after_undo_backs_up_the_file_as_it_is_then(self):
        """After an undo the file has no sudoForge mark, so the next setup may back it up afresh."""
        self.run_root("apply", HELPER)
        self.run_root("undo")
        self.conf.write_text(STOCK + "Set disable_coredump false\n")
        self.assertEqual(self.run_root("apply", HELPER), 0)
        self.assertEqual(self.backup.read_text(), STOCK + "Set disable_coredump false\n")

    def test_refused_changes_nothing(self):
        self.conf.write_text(STOCK + "Path askpass /usr/bin/other\n")
        self.assertEqual(self.run_root("apply", HELPER), 3)
        self.assertEqual(self.conf.read_text(), STOCK + "Path askpass /usr/bin/other\n")
        self.assertFalse(self.backup.exists(), "no backup when nothing changes")

    def test_wrong_words_change_nothing(self):
        self.assertEqual(self.run_root("delete-everything"), 2)
        self.assertEqual(self.conf.read_text(), STOCK)

    def test_no_temp_files_left_behind(self):
        self.run_root("apply", HELPER)
        self.run_root("undo")
        self.assertEqual(sorted(p.name for p in self.conf.parent.iterdir()),
                         ["sudo.conf", "sudo.conf.sudoforge-backup"])


if __name__ == "__main__":
    unittest.main()
