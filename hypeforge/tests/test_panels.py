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
import start  # noqa: E402
import quick  # noqa: E402
import calendar_view as hfcalendar  # noqa: E402
import workspaces as wsview  # noqa: E402


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


class ViewNames(unittest.TestCase):
    def test_no_view_module_shadows_the_standard_library(self):
        # views/ goes first on the import path: a view called calendar.py would replace Python's own
        import sys as _sys
        names = {p.stem for p in (HERE / "applets/panels/views").glob("*.py")}
        self.assertFalse(names & set(_sys.stdlib_module_names), names & set(_sys.stdlib_module_names))


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


def entry(name, cats=()):
    return {"name": name, "icon": name.lower(), "exec": name.lower(), "terminal": False, "categories": set(cats), "wmclass": ""}


START_ENTRIES = {"google-chrome": entry("Google Chrome", ["Network"]), "steam": entry("Steam", ["Game"]),
                 "chromium": entry("Chromium", ["Network"]), "gimp": entry("GIMP", ["Graphics"])}


class StartPanel(unittest.TestCase):
    def test_search_finds_every_word_and_names_starting_with_it_first(self):
        self.assertEqual(start.matches(START_ENTRIES, "chrom"), ["chromium", "google-chrome"])
        self.assertEqual(start.matches(START_ENTRIES, "google chr"), ["google-chrome"])
        self.assertEqual(start.matches(START_ENTRIES, "steam"), ["steam"])
        more = dict(START_ENTRIES, helper=entry("A Steam Helper"))
        self.assertEqual(start.matches(more, "steam"), ["steam", "helper"],
                         "Steam (starts with it) before A Steam Helper, though A sorts first")
        self.assertEqual(start.matches(START_ENTRIES, "nothing-like-it"), [])

    def test_the_groups_are_the_launchers_own_with_favorites_first_and_all_apps_last(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "sections.toml"
            cfg.write_text('favourites = ["steam", "gone"]\nclaim_order = ["Games", "Internet"]\n'
                           '[[section]]\nname = "Games"\ncategories = ["Game"]\n'
                           '[[section]]\nname = "Internet"\ncategories = ["Network"]\n')
            real = start.panelkit_launcher
            def launcher():
                mod = real()
                mod.CONFIG = cfg
                return mod
            start.panelkit_launcher = launcher
            try:
                sets = start.groups(START_ENTRIES)
            finally:
                start.panelkit_launcher = real
        names = [n for n, _ in sets]
        self.assertEqual(names, ["Favorites", "Games", "Internet", "All apps"])
        self.assertEqual(dict(sets)["Favorites"], ["steam"], "a favourite that isn't installed is left out")
        self.assertEqual(len(dict(sets)["All apps"]), 4)


class FakeRun:
    """Answers commands from a table; records what was run."""
    def __init__(self, answers):
        self.answers, self.ran = answers, []

    def __call__(self, cmd, timeout=3.0):
        self.ran.append(cmd)
        return self.answers.get(" ".join(cmd), "")


class QuickSettings(unittest.TestCase):
    def test_wifi_off_on_a_cable_says_so(self):
        be = quick.Backend(FakeRun({"nmcli -t -f WIFI radio": "disabled\n",
                                    "nmcli -t -f DEVICE,TYPE,STATE dev": "enp5s0:ethernet:connected\nwlan0:wifi:unavailable\n"}))
        self.assertEqual(be.wifi(), (False, "off · wired"))

    def test_wifi_on_shows_the_network(self):
        be = quick.Backend(FakeRun({"nmcli -t -f WIFI radio": "enabled\n", "nmcli -t -f ACTIVE,SSID dev wifi": "no:Other\nyes:tphome\n"}))
        self.assertEqual(be.wifi(), (True, "tphome"))

    def test_a_missing_program_is_a_dash_not_a_crash(self):
        be = quick.Backend(FakeRun({}))
        self.assertEqual(be.wifi(), (None, "—"))
        self.assertEqual(be.bluetooth(), (None, "—"))
        self.assertEqual(be.volume(), (None, False))

    def test_bluetooth_names_the_connected_device(self):
        be = quick.Backend(FakeRun({"bluetoothctl show": "\tName: x\n\tPowered: yes\n",
                                    "bluetoothctl devices Connected": "Device AA:BB Logitech G13\n"}))
        self.assertEqual(be.bluetooth(), (True, "Logitech G13"))

    def test_the_switches_run_the_owning_programs(self):
        run = FakeRun({})
        be = quick.Backend(run)
        be.wifi_toggle(False)
        be.bluetooth_toggle(True)
        be.dnd_toggle(False)
        be.set_volume(37.6)
        self.assertIn(["nmcli", "radio", "wifi", "on"], run.ran)
        self.assertIn(["bluetoothctl", "power", "off"], run.ran)
        self.assertTrue(run.ran[2][0].endswith("hypeforge-notifications") and run.ran[2][1] == "dnd",
                        "Do Not Disturb through the bell, so the bell redraws")
        self.assertEqual(run.ran[3][-1], "37%")

    def test_the_night_lights_sentence_is_cut_to_fit_a_tile(self):
        self.assertEqual(quick.short("warm again from 18:59"), "from 18:59")
        self.assertEqual(quick.short("4500 K since 18:46 · daylight at 07:02"), "until 07:02")
        self.assertEqual(quick.short("Warm Now, 4500 K, until you pick Automatic"), "warm now")
        self.assertEqual(quick.short("switched off"), "off")

    def test_volume_and_mute(self):
        be = quick.Backend(FakeRun({"wpctl get-volume @DEFAULT_AUDIO_SINK@": "Volume: 0.52 [MUTED]\n"}))
        self.assertEqual(be.volume(), (52, True))

    def test_updates_from_the_snapshot_never_the_network(self):
        with tempfile.TemporaryDirectory() as d:
            old = quick.SNAPSHOT
            quick.SNAPSHOT = Path(d) / "updates.json"
            try:
                self.assertEqual(quick.Backend(FakeRun({})).updates(), "Updates: not checked yet")
                quick.SNAPSHOT.write_text('{"count": 212, "ready": []}')
                self.assertEqual(quick.Backend(FakeRun({})).updates(), "212 waiting their turn · nog")
                quick.SNAPSHOT.write_text('{"count": 212, "ready": [{"pkg": "a"}, {"pkg": "b"}]}')
                self.assertEqual(quick.Backend(FakeRun({})).updates(), "2 updates ready · nog")
            finally:
                quick.SNAPSHOT = old


class CalendarPanel(unittest.TestCase):
    def test_clear_all_hides_what_was_shown_but_not_what_comes_after(self):
        notes = [{"id": "3"}, {"id": "7"}, {"id": "5"}]
        with tempfile.TemporaryDirectory() as d:
            old = hfcalendar.CLEARED
            hfcalendar.CLEARED = Path(d) / "cleared"
            try:
                self.assertEqual([n["id"] for n in hfcalendar.visible(notes)], ["7", "5", "3"], "newest first")
                hfcalendar.CLEARED.write_text("5")
                self.assertEqual([n["id"] for n in hfcalendar.visible(notes)], ["7"])
            finally:
                hfcalendar.CLEARED = old

    def test_a_notification_borrows_its_apps_icon(self):
        entries = {"steam": {"name": "Steam", "icon": "steam"}}
        self.assertEqual(hfcalendar.icon_for({"app_name": "Steam", "app_icon": "None"}, entries), "steam")
        self.assertEqual(hfcalendar.icon_for({"app_name": "nog", "app_icon": "None"}, entries), "dialog-information")
        self.assertEqual(hfcalendar.icon_for({"app_name": "x", "app_icon": "mail-unread"}, entries), "mail-unread")

    def test_makos_none_is_nothing(self):
        self.assertEqual(hfcalendar.plain("None"), "")
        self.assertEqual(hfcalendar.plain(None), "")
        self.assertEqual(hfcalendar.plain("Hi"), "Hi")


class WorkspacesStrip(unittest.TestCase):
    def test_sway_names_map_to_our_workspaces_on_every_screen(self):
        self.assertEqual(wsview.index_of("4:Gaming", 6), 4)
        self.assertEqual(wsview.index_of("14:Gaming", 6), 4, "the second screen adds 10")
        self.assertEqual(wsview.index_of("24:Gaming", 6), 4)
        self.assertIsNone(wsview.index_of("101:Shared", 6), "a shared space is no single workspace")
        self.assertIsNone(wsview.index_of("9:Extra", 6))
        self.assertIsNone(wsview.index_of("scratch", 6))

    def test_apps_are_counted_once_per_workspace_across_screens(self):
        from hfapps import Matcher
        entries = {"steam": {"name": "Steam", "icon": "steam", "exec": "steam %U", "terminal": False,
                             "categories": set(), "wmclass": ""}}
        win = lambda i, a: {"id": i, "pid": i, "type": "con", "app_id": a, "nodes": [], "floating_nodes": []}
        tree = {"nodes": [{"nodes": [{"name": "4:Gaming", "nodes": [win(1, "steam")], "floating_nodes": []}]},
                          {"nodes": [{"name": "14:Gaming", "nodes": [win(2, "steam"), win(3, "mystery")], "floating_nodes": []}]}]}
        per = wsview.apps_per_workspace(tree, entries, Matcher(entries), 6)
        self.assertEqual(per[4], ["steam", "mystery"], "two Steam windows on two screens: one app")
        self.assertEqual(per[1], [])


if __name__ == "__main__":
    unittest.main()
