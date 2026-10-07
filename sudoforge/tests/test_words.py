"""The box's lines, from a fake /proc: who asks, for what, in plain words."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sudoforge.words import Procs, asker, plain_message, polkit_lines, sudo_command, sudo_lines


def fake_proc(tree: dict[int, tuple[int, list[str]]]) -> Procs:
    """{pid: (parent, argv)} → a folder shaped like /proc."""
    root = Path(tempfile.mkdtemp())
    for pid, (ppid, argv) in tree.items():
        d = root / str(pid)
        d.mkdir()
        (d / "cmdline").write_bytes(b"\0".join(a.encode() for a in argv) + b"\0")
        name = Path(argv[0]).name[:15]
        (d / "comm").write_text(name + "\n")
        (d / "stat").write_text(f"{pid} ({name}) S {ppid} 0 0\n")
    return Procs(root)


class SudoCommand(unittest.TestCase):
    def test_sudo_and_its_options_are_dropped(self):
        self.assertEqual(sudo_command(["sudo", "-A", "-k", "pacman", "-S", "--needed", "firefox"]),
                         "pacman -S --needed firefox")
        self.assertEqual(sudo_command(["sudo", "-u", "root", "-A", "ls", "-la"]), "ls -la")
        self.assertEqual(sudo_command(["/usr/bin/sudo", "--", "-weird"]), "-weird")
        self.assertEqual(sudo_command([]), "")

    def test_polkit_sentence_reads_like_the_design(self):
        self.assertEqual(plain_message("Authentication is required to mount KINGSTON"), "To mount KINGSTON.")
        self.assertEqual(plain_message("Something else."), "Something else.")


class WhoAsks(unittest.TestCase):
    def test_nog_through_sudo_names_nog_and_the_terminal(self):
        p = fake_proc({10: (1, ["alacritty"]), 11: (10, ["fish"]), 12: (11, ["nog", "install", "firefox"]),
                       13: (12, ["sudo", "-A", "pacman", "-S", "--needed", "firefox"]),
                       14: (13, ["/usr/lib/sudoforge/sudoforge-askpass", "[sudo] password for javier: "])})
        lines = sudo_lines(13, "javier", p)
        self.assertEqual(lines.heading, "nog wants to run as admin")
        self.assertEqual(lines.detail, "pacman -S --needed firefox")
        self.assertEqual(lines.note, "Started from Terminal (Alacritty) · checked by sudo")
        self.assertEqual(lines.label, "Password for javier")
        self.assertIsNone(lines.words)

    def test_a_shell_is_looked_past(self):
        p = fake_proc({20: (1, ["alacritty", "--class", "claude-terminal"]), 21: (20, ["claude"]),
                       22: (21, ["/bin/bash", "-c", "sudo -A -k true"]), 23: (22, ["sudo", "-A", "-k", "true"])})
        self.assertEqual(asker(p, 22), ("Claude", "Terminal (Alacritty)"))
        self.assertEqual(sudo_lines(23, "javier", p).heading, "Claude wants to run as admin")

    def test_a_python_program_is_named_by_its_file(self):
        p = fake_proc({30: (1, ["python3", "/usr/bin/udiskie"])})
        self.assertEqual(asker(p, 30)[0], "udiskie")

    def test_a_forge_app_run_as_main_py_is_named_by_its_folder(self):
        p = fake_proc({80: (1, ["/usr/bin/python3", "/opt/forge-suite/sudoforge/main.py", "setup"])})
        self.assertEqual(asker(p, 80)[0], "sudoForge")

    def test_nothing_known_is_still_plain(self):
        p = fake_proc({40: (1, ["bash"]), 41: (40, ["sudo", "true"])})
        self.assertEqual(sudo_lines(41, "javier", p).heading, "A command wants to run as admin")
        self.assertEqual(sudo_lines(41, "javier", p).note, "Checked by sudo")

    def test_a_vanished_process_does_not_break_it(self):
        p = fake_proc({})
        self.assertEqual(sudo_lines(999, "javier", p).heading, "A command wants to run as admin")


class PolkitLines(unittest.TestCase):
    def test_usb_drive(self):
        p = fake_proc({50: (1, ["python3", "/usr/bin/udiskie"])})
        lines = polkit_lines("org.freedesktop.udisks2.filesystem-mount", "Authentication is required to mount KINGSTON",
                             {"polkit.subject-pid": "50", "polkit.caller-pid": "50"}, "javier", p)
        self.assertEqual(lines.heading, "USB drives wants admin rights")
        self.assertEqual(lines.words, "To mount KINGSTON.")
        self.assertEqual(lines.note, "Asked by udiskie · checked by the system (polkit)")
        self.assertIsNone(lines.detail)

    def test_pkexec_shows_what_will_run(self):
        p = fake_proc({60: (1, ["alacritty"]), 61: (60, ["fish"]), 62: (61, ["grubforge"]),
                       63: (62, ["pkexec", "--disable-internal-agent", "/usr/bin/grub-mkconfig", "-o", "/boot/grub/grub.cfg"])})
        lines = polkit_lines("org.freedesktop.policykit.exec", "Authentication is needed to run `/usr/bin/grub-mkconfig' as the super user",
                             {"polkit.subject-pid": "62", "polkit.caller-pid": "63"}, "javier", p)
        self.assertEqual(lines.heading, "grubForge wants to run as admin")
        self.assertEqual(lines.detail, "/usr/bin/grub-mkconfig -o /boot/grub/grub.cfg")

    def test_unknown_kind_is_named_after_the_program(self):
        p = fake_proc({70: (1, ["someapp"])})
        lines = polkit_lines("com.example.thing", "Do it", {"polkit.subject-pid": "70"}, "javier", p)
        self.assertEqual(lines.heading, "someapp wants admin rights")


if __name__ == "__main__":
    unittest.main()
