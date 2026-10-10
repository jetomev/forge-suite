"""The pop-up panels' core (look program step 4), without opening any window: the look of every
style × theme, one panel per view (a second press closes it), the power panel's asking rule."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/panels"))
sys.path.insert(0, str(HERE / "applets/panels/views"))
import panelkit  # noqa: E402
import power  # noqa: E402


class Look(unittest.TestCase):
    def test_every_style_with_every_theme_gives_a_whole_look(self):
        ht = panelkit.theme_tool()
        for style in ht.styles():
            for theme in ht.themes():
                look = panelkit.Look(style, theme)
                self.assertEqual(set(look.colour), set(panelkit.Look.ROLES))
                for role, value in look.colour.items():
                    self.assertRegex(value, r"^#[0-9a-f]{6}$", f"{style}/{theme}: {role}")
                self.assertIsInstance(look.radius, int)
                css = look.css()
                self.assertIn(look.colour["panel_bg"], css)

    def test_the_rice_is_round_and_mac_os_9_is_square(self):
        self.assertEqual(panelkit.Look("rice", "kognogos-mocha").radius, 14)
        self.assertEqual(panelkit.Look("mac-os-9", "light-gray").radius, 0)


class OnePanelPerView(unittest.TestCase):
    def test_the_same_button_again_closes_the_open_panel(self):
        with tempfile.TemporaryDirectory() as d:
            old = panelkit.RUNTIME
            panelkit.RUNTIME = Path(d)
            try:
                self.assertFalse(panelkit.close_open("power"), "nothing open: open it")
                sleeper = subprocess.Popen(["sleep", "30"])
                panelkit.pidfile("power").write_text(str(sleeper.pid))
                self.assertTrue(panelkit.close_open("power"))
                self.assertEqual(sleeper.wait(5), -15, "the open one got the close request")
                panelkit.pidfile("power").write_text("999999")
                self.assertFalse(panelkit.close_open("power"), "a stale file means nothing is open")
            finally:
                panelkit.RUNTIME = old


class PowerAsks(unittest.TestCase):
    def setUp(self):
        self.a = power.Asking({key: confirm for key, _l, _i, confirm in power.ACTIONS})

    def test_lock_goes_at_once(self):
        self.assertEqual(self.a.press("lock"), "run")

    def test_restart_asks_then_runs(self):
        self.assertEqual(self.a.press("reboot"), "ask")
        self.assertEqual(self.a.press("reboot"), "run")

    def test_pressing_another_moves_the_question(self):
        self.assertEqual(self.a.press("reboot"), "ask")
        self.assertEqual(self.a.press("shutdown"), "ask", "Shut Down asks too; it doesn't inherit Restart's yes")
        self.assertEqual(self.a.press("shutdown"), "run")

    def test_the_commands_come_from_the_launchers_power_settings(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "sections.toml"
            f.write_text('[power]\nreboot = "systemctl reboot"\n')
            old = power.SECTIONS
            power.SECTIONS = f
            try:
                self.assertEqual(power.commands(), {"reboot": "systemctl reboot"})
            finally:
                power.SECTIONS = old


if __name__ == "__main__":
    unittest.main()
