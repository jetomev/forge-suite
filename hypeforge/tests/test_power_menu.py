"""The power menu's four entries live in sections.toml's [power] table. F-54 (2026-10-10): a cleanup
commit deleted the table and the ⏻ menu opened empty for a day — no test noticed. This one does."""

import tomllib
import unittest
from pathlib import Path

SECTIONS = Path(__file__).resolve().parents[1] / "applets/sections/sections.toml"


class PowerMenu(unittest.TestCase):
    def test_the_four_entries_are_there(self):
        power = tomllib.loads(SECTIONS.read_text()).get("power")
        self.assertIsInstance(power, dict, "sections.toml lost its [power] table: the ⏻ menu would open empty")
        self.assertEqual(sorted(power), ["lock", "logout", "reboot", "shutdown"])
        self.assertTrue(all(isinstance(v, str) and v for v in power.values()))


if __name__ == "__main__":
    unittest.main()
