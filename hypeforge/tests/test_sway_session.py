"""The "Sway (hypeForge buttons)" login never breaks on a Sway update (Javier, 2026-10-17: "whenever sway
updates, it does not brake our system"): our build runs only when it is the system's Sway version and
starts; otherwise the system's Sway runs and the buttons are off (D-111)."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SESSION = REPO / "sway-hypeforge/hypeforge-session"


class Session(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        self.bin = self.home / "bin"
        self.bin.mkdir()
        self.ran = self.home / "ran.txt"

    def fake(self, path: Path, version: str | None):
        """A stand-in sway: prints its version, or records how it was started."""
        path.parent.mkdir(parents=True, exist_ok=True)
        answer = f'echo "sway version {version}"' if version else "exit 127"
        path.write_text(f'#!/bin/sh\nif [ "$1" = "--version" ]; then {answer}; exit; fi\n'
                        f'echo "$0 $* fallback=$HYPEFORGE_SWAY_FALLBACK" > {self.ran}\n')
        path.chmod(0o755)

    def start(self) -> str:
        env = dict(os.environ, HOME=str(self.home), PATH=f"{self.bin}:/usr/bin:/bin")
        env.pop("HYPEFORGE_SWAY_FALLBACK", None)
        subprocess.run(["sh", str(SESSION)], env=env, timeout=10)
        return self.ran.read_text()

    def ours(self):
        return self.home / ".local/opt/sway-hypeforge/current/bin/sway"

    def test_ours_runs_when_it_matches_the_system(self):
        self.fake(self.bin / "sway", "1.12")
        self.fake(self.ours(), "1.12-d474619 (Oct 17 2026, branch 'master')")
        ran = self.start()
        self.assertIn(str(self.ours()), ran)
        self.assertIn("config-buttons", ran)
        self.assertTrue(ran.rstrip().endswith("fallback="), ran)

    def test_a_sway_update_falls_back_to_the_systems_sway(self):
        self.fake(self.bin / "sway", "1.13")
        self.fake(self.ours(), "1.12")
        ran = self.start()
        self.assertTrue(ran.startswith(str(self.bin / "sway")), ran)
        self.assertNotIn("config-buttons", ran, "stock Sway would show an error on the button lines")
        self.assertIn("fallback=1.12:1.13", ran)

    def test_a_build_that_doesnt_start_falls_back_too(self):
        """wlroots updated under it: our sway can't even print its version."""
        self.fake(self.bin / "sway", "1.12")
        self.fake(self.ours(), None)
        ran = self.start()
        self.assertTrue(ran.startswith(str(self.bin / "sway")), ran)
        self.assertIn("fallback=none:1.12", ran)

    def test_no_build_at_all_falls_back(self):
        self.fake(self.bin / "sway", "1.12")
        self.assertIn("fallback=none:1.12", self.start())

    def test_stock_sways_config_never_has_the_button_lines(self):
        self.assertNotIn("titlebar_button", (REPO / "sway/config").read_text())
        self.assertIn("include ~/.config/sway/config", (REPO / "sway/config-buttons").read_text())


if __name__ == "__main__":
    unittest.main()
