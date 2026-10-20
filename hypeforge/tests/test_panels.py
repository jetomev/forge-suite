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

    def looks(self, corners):
        """Every style's Look with the corners switch on `corners` (not the person's own state)."""
        from unittest import mock
        ht = panelkit.theme_tool()                   # Look loads a fresh copy each time: hand it this one
        asked = []
        with mock.patch.object(ht.Place, "read_state", lambda self: asked.append(1) or {"corners": corners}), \
             mock.patch.object(panelkit, "theme_tool", lambda: ht):
            looks = {slug: panelkit.Look(slug, "kognogos-mocha") for slug in ht.styles()}
        self.assertEqual(len(asked), len(looks))     # the setup took effect: never the person's own switch
        return looks

    def test_one_pop_up_standard_on_every_style(self):
        # D-116 (Javier, 2026-10-20): the Rice was 14 px JetBrains Mono, Mac OS 9 square — now one standard
        for corners in ("style", "rounded"):
            looks = self.looks(corners)
            self.assertGreater(len(looks), 5)
            shapes = {(lk.font, lk.size, lk.border, lk.radius) for lk in looks.values()}
            self.assertEqual(shapes, {("Noto Sans", 10.5, 1, 10)}, corners)

    def test_pop_ups_follow_the_corners_switch(self):
        self.assertEqual({lk.radius for lk in self.looks("straight").values()}, {0})


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
        be = quick.Backend(FakeRun({"nmcli -t -f WIFI radio": "enabled\n", "nmcli -t -f TYPE,NAME connection show --active": "802-3-ethernet:Wired 1\n802-11-wireless:tphome\n"}))
        self.assertEqual(be.wifi(), (True, "tphome"))
        self.assertFalse(any("wifi" in c and "dev" in c for c in map(" ".join, getattr(be.run, "ran", []))),
                         "never the Wi-Fi list: it scans first, seconds long (2026-10-17)")

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


class CosmicPopups(unittest.TestCase):
    """The small pop-ups (COSMIC's C-5, D-77) and, since D-96 (Javier, 2026-10-13), the three pieces every
    style shares the same way: the status pill → Quick Settings, the date-time-bell piece → the calendar
    with the alerts, the moon → the night light's part. Defined once, in modules.jsonc."""

    def shared(self):
        import json
        loader = __import__("importlib.machinery").machinery.SourceFileLoader("hfbar_c", str(HERE / "applets/bar/hypeforge-bar"))
        bar = __import__("importlib.util").util.module_from_spec(__import__("importlib.util").util.spec_from_loader("hfbar_c", loader))
        loader.exec_module(bar)
        return json.loads(bar.strip_comments((HERE / "sway/waybar/modules.jsonc").read_text()))

    def test_the_status_pill_opens_quick_settings_from_any_of_its_icons(self):
        """Javier, 2026-10-13: Windows 11's bundle "for all themes": audio, network and Bluetooth in one
        control, with the big buttons into the Forge apps and hypeForge Settings."""
        shared = self.shared()
        self.assertEqual(shared["group/quick"]["modules"], ["bluetooth", "network", "wireplumber"])
        for module in ("bluetooth", "network", "wireplumber"):
            self.assertIn("hypeforge-panel quick {popup}", shared[module]["on-click"], module)
            self.assertIn("on-click-right", shared[module], f"{module}: right click keeps the full app")

    def test_the_rice_right_side_is_in_javiers_order(self):
        """Javier, 2026-10-11, right to left: power, the status pill (volume · network · Bluetooth), disks/USB,
        printers, clipboard, CPU, memory, night light, the programs' icons. 2026-10-17: after the processor,
        in his order, the graphics card, temperature, memory and disk; the disk piece took the USB icon's
        place ("the system disk work… shouldn't replace the mount/umount icon?")."""
        rice = self.rice()
        right_to_left = ["custom/power-panel", "group/quick", "custom/printers", "custom/clipboard",
                         "custom/cpu", "custom/gpu", "custom/temperature", "custom/memory", "custom/disk", "custom/nightlight", "tray"]
        self.assertEqual(rice["modules-right"], right_to_left[::-1])

    def test_the_bell_sits_with_the_time_and_opens_the_same_pop_up(self):
        """Javier, 2026-10-11: 'Icon alert should go here, and the alert icon should not open the alert
        popup. Clicking on the Date/Time/Alert will open … all three.' 2026-10-13: on every style."""
        rice, shared = self.rice(), self.shared()
        self.assertEqual(rice["modules-center"], ["group/datetime"])
        self.assertEqual(shared["group/datetime"]["modules"], ["clock", "custom/notifications"])
        for module in ("clock", "custom/notifications"):
            self.assertIn("hypeforge-panel calendar {popup-calendar}", shared[module]["on-click"], module)
        self.assertIn("dnd", shared["custom/notifications"]["on-click-right"])
        self.assertNotIn("custom/notifications", rice["modules-right"])

    def test_the_moon_opens_the_night_light_part(self):
        self.assertIn("hypeforge-panel quick --only night {popup}", self.shared()["custom/nightlight"]["on-click"])
        self.assertIn("night", quick.ONLY)

    def rice(self):
        import json
        loader = __import__("importlib.machinery").machinery.SourceFileLoader("hfbar_r2", str(HERE / "applets/bar/hypeforge-bar"))
        bar = __import__("importlib.util").util.module_from_spec(__import__("importlib.util").util.spec_from_loader("hfbar_r2", loader))
        loader.exec_module(bar)
        return json.loads(bar.strip_comments((HERE / "styles/rice/bar/config.jsonc").read_text()))

    def test_the_parts_name_real_tiles_and_a_settings_app(self):
        src = (HERE / "applets/panels/views/quick.py").read_text()
        for part, (title, tiles, more) in quick.ONLY.items():
            for name in tiles:
                self.assertIn(f'("{name}", lambda', src, f"{part}: {name}")
            self.assertTrue(more.split()[0] in ("alacritty", "hypeforge-nmtui"), part)

    def test_the_panel_offers_only_those_parts(self):
        out = subprocess.run([sys.executable, str(HERE / "applets/panels/hypeforge-panel"), "--help"],
                             capture_output=True, text=True).stdout
        self.assertIn("{network,sound,bluetooth,night}", out)
        self.assertIn("library", out)

    def test_the_app_library_opens_on_every_app_then_the_groups(self):
        self.assertTrue((HERE / "applets/panels/views/library.py").is_file())
        self.assertIn("sets = sets[-1:] + sets[:-1]", (HERE / "applets/panels/views/start.py").read_text())


if __name__ == "__main__":
    unittest.main()


class ClipboardPanel(unittest.TestCase):
    """Javier, 2026-10-17: the clipboard list "is horrible and without identity" → a panel like the others."""

    @classmethod
    def setUpClass(cls):
        import clipboard as clipview
        cls.v = clipview
        loader = __import__("importlib.machinery").machinery.SourceFileLoader(
            "hf_clipboard_test", str(HERE / "applets/clipboard/hypeforge-clipboard"))
        spec = __import__("importlib.util").util.spec_from_loader("hf_clipboard_test", loader)
        cls.app = __import__("importlib.util").util.module_from_spec(spec)
        loader.exec_module(cls.app)

    def test_each_copy_says_what_it_is(self):
        k = self.v.kind_of
        pic = self.app.PICTURE.match("[[ binary data 12 KiB png 640x360 ]]")
        self.assertEqual(k("https://github.com/jetomev/forge-suite/issues/54", None), "link")
        self.assertEqual(k("#cba6f7", None), "colour")
        self.assertEqual(k("~/Programs/forge-suite/hypeforge", None), "path")
        self.assertEqual(k("def copy_back(entry) -> None:", None), "code")
        self.assertEqual(k("Meeting moved to Thursday at 3 pm", None), "text")
        self.assertEqual(k("[[ binary data 12 KiB png 640x360 ]]", pic), "picture")
        self.assertEqual(self.v.what_line("picture", "[[ binary data 12 KiB png 640x360 ]]", pic), "Picture · PNG · 640 × 360")
        self.assertEqual(self.v.what_line("link", "https://www.example.com/a/b", None), "Link · example.com")
        self.assertEqual(self.v.what_line("text", "two words", None), "Text · 2 words")

    def test_it_opens_where_the_bars_pop_ups_do(self):
        with tempfile.TemporaryDirectory() as d:
            places = Path(d) / "places.json"
            places.write_text('{"{popup}": "--edges bottom,right --margin bottom=56,right=8"}')
            argv = self.app.panel_argv([], (), places)
            self.assertEqual(argv[1:], ["clipboard", "--edges", "bottom,right", "--margin", "bottom=56,right=8"],
                             "Win + C: the bar's note (Windows 11's bar is at the bottom)")
            argv = self.app.panel_argv(["--edges", "top,right", "--margin", "top=44,right=8"], ("--ask-clear",), places)
            self.assertEqual(argv[1:], ["clipboard", "--edges", "top,right", "--margin", "top=44,right=8", "--ask-clear"],
                             "a click: the bar's own words win; the right click asks to empty it")
            self.assertEqual(self.app.panel_argv([], (), Path(d) / "none.json")[1:], ["clipboard"], "no note: its own corner")

    def test_the_bar_passes_its_place_on_both_clicks(self):
        for f in ("sway/waybar/modules.jsonc", "sway/waybar/config.jsonc"):
            text = (HERE / f).read_text()
            self.assertIn("hypeforge-clipboard list {popup}", text, f)
            self.assertIn("hypeforge-clipboard clear {popup}", text, f)

    def test_the_panel_knows_the_view(self):
        self.assertIn('"clipboard": "clipboard"', (HERE / "applets/panels/hypeforge-panel").read_text())


class NotificationCards(unittest.TestCase):
    def test_closer_and_smaller(self):
        """Javier, 2026-10-17: "a little big and space between them is too much"."""
        src = (HERE / "applets/panels/views/calendar_view.py").read_text()
        self.assertIn(".hf-card.hf-note {{ padding: 6px 12px; }}", src)
        self.assertIn("root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)", src, "the blocks 4 px apart (was 10)")
        self.assertIn(".hf-card.hf-head {{ padding: 4px 6px 4px 12px; }}", src, "a slim head")
        self.assertIn("cards = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)", src)
        self.assertIn("new_from_file_at_size(path, 24, 24)", src)


class TrayMenu(unittest.TestCase):
    """2026-10-17: a tray app's menu as a hypeForge pop-up (Waybar's opened at the pointer, over the bar)."""

    @classmethod
    def setUpClass(cls):
        import traymenu
        sys.path.insert(0, str(HERE / "applets/tray"))
        import hfsni
        import json as _json
        cls.v, cls.sni = traymenu, hfsni
        cls.layout = _json.loads((HERE / "tests/fixtures/tray-menu-dropbox.json").read_text())

    def test_the_apps_spaces_become_an_indent_and_underscores_go(self):
        self.assertEqual(self.v.clean("   you@example.com"), ("you@example.com", 1))
        self.assertEqual(self.v.clean("_Preferences"), ("Preferences", 0))
        self.assertEqual(self.v.clean("Save__As"), ("Save_As", 0))

    def test_the_separators_cut_the_menu_into_cards(self):
        g = self.v.groups(self.layout)
        self.assertEqual([len(x) for x in g], [2, 4, 3, 4, 1], "Dropbox's menu: five cards, the double separator once")
        self.assertEqual(g[-1][0][1]["label"], "Quit Dropbox")

    def test_an_item_is_found_by_its_name_or_its_path(self):
        self.assertEqual(self.sni.split(":1.48/org/ayatana/NotificationItem/dropbox"),
                         (":1.48", "/org/ayatana/NotificationItem/dropbox"))
        self.assertEqual(self.sni.split("org.kde.StatusNotifierItem-5001-1"),
                         ("org.kde.StatusNotifierItem-5001-1", "/StatusNotifierItem"))
        self.assertEqual(self.sni.split("/StatusNotifierItem", ":1.9"), (":1.9", "/StatusNotifierItem"))


class OwnTray(unittest.TestCase):
    def test_every_styles_tray_becomes_ours_nested_ones_too(self):
        import importlib.machinery, importlib.util
        ld = importlib.machinery.SourceFileLoader("hb_tray_test", str(HERE / "applets/bar/hypeforge-bar"))
        sp = importlib.util.spec_from_loader("hb_tray_test", ld)
        hb = importlib.util.module_from_spec(sp)
        ld.exec_module(hb)
        self.assertEqual(hb.own_tray({"modules-right": ["tray", "clock"], "group/hidden": {"modules": ["x", "tray"]}}),
                         {"modules-right": ["group/tray", "clock"], "group/hidden": {"modules": ["x", "group/tray"]}})
        mods = (HERE / "sway/waybar/modules.jsonc").read_text()
        for n in range(1, 11):
            self.assertIn(f'"image#tray-{n}"', mods)
        self.assertIn("menu 1 {popup}", mods, "a click carries the bar's pop-up place")
        self.assertEqual(mods.count('"interval": 3600, "signal": 15'), 10,
                         "every piece has an interval: an exec without one hangs Waybar 0.15 before it draws")

    def test_the_tray_starts_at_login_under_the_watcher(self):
        self.assertIn("hypeforge-watch tray ~/Programs/forge-suite/hypeforge/applets/tray/hypeforge-tray run",
                      (HERE / "sway/config").read_text())
