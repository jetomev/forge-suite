"""The Mac menus (look program step 3; Mac OS 9 D-72, macOS D-74), on throwaway folders.

The menus are GTK menu files Waybar reads once: they must be valid, every action must point at a
menu item that exists, the emblem menu must carry the launcher's own groups, the Window menu the
workspaces; the app's name and icon follow the window in use.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/common"))


def load():
    loader = importlib.machinery.SourceFileLoader("hfmenubar", str(HERE / "applets/menubar/hypeforge-menubar"))
    spec = importlib.util.spec_from_loader("hfmenubar", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


def entry(name, exec_, icon, cats=()):
    return {"name": name, "icon": icon, "exec": exec_, "terminal": False, "categories": set(cats), "wmclass": ""}


ENTRIES = {
    "google-chrome": entry("Google Chrome", "google-chrome-stable %U", "google-chrome", ["Network", "WebBrowser"]),
    "gimp": entry("GIMP & Friends", "gimp %U", "gimp", ["Graphics"]),
    "steam": entry("Steam", "steam %U", "steam", ["Game"]),
}

SECTIONS = '''
favourites = ["google-chrome", "not-installed"]
claim_order = ["Games", "Graphics", "Internet"]
[[section]]
name = "Games"
categories = ["Game"]
[[section]]
name = "Graphics"
categories = ["Graphics"]
[[section]]
name = "Internet"
categories = ["Network"]
[power]
lock = "gtklock -d"
'''

WORKSPACES = '''
enabled = true
screens = ["DP-3"]
[[workspace]]
name = "Daily"
[[workspace]]
name = "Gaming"
'''


class Menus(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        d = Path(self.dir.name)
        (d / "sections.toml").write_text(SECTIONS)
        (d / "workspaces.toml").write_text(WORKSPACES)
        self.mb = load()
        self.mb.SECTIONS, self.mb.WORKSPACES = d / "sections.toml", d / "workspaces.toml"
        self.mb.MENUS, self.mb.BAR_FRAGMENT, self.mb.BAR_STYLE = d / "menubar", d / "menubar.waybar.json", d / "menubar.css"
        self.mb.STATE = d / "state"
        self.mb.signal_bar = lambda *a: None
        launcher = self.mb.load_launcher
        self.mb.load_launcher = lambda: self._launcher(launcher(), d / "sections.toml")

    def _launcher(self, mod, path):
        mod.CONFIG = path
        return mod

    def tearDown(self):
        self.dir.cleanup()

    def write(self):
        class Icons:
            def find(self, name):
                return f"/icons/{name}.svg"
        self.mb.write_bar(ENTRIES, Icons())
        return json.loads(self.mb.BAR_FRAGMENT.read_text())

    def labels(self, xml_path):
        root = ET.parse(xml_path).getroot()
        return root, [p.text for p in root.iter("property") if p.get("name") == "label"]

    def test_every_menu_is_valid_and_every_action_has_its_item(self):
        bar = self.write()
        for name in ("emblem", "window", "special", "help"):
            module = bar[f"custom/menu-{name}"]
            root, _ = self.labels(module["menu-file"])
            ids = {o.get("id") for o in root.iter("object") if o.get("id")}
            self.assertIn("menu", ids, "Waybar needs a GtkMenu with id menu")
            self.assertTrue(module["menu-actions"])
            self.assertLessEqual(set(module["menu-actions"]), ids, f"{name}: an action without its item")
            self.assertEqual(module["menu"], "on-click")

    def test_no_submenu_is_written_inside_its_item(self):
        # GTK 3 segfaults on <property name="submenu"><object …>, and Waybar with it (seen 10-10)
        bar = self.write()
        for name in ("emblem", "window"):
            text = Path(bar[f"custom/menu-{name}"]["menu-file"]).read_text()
            self.assertNotIn('<property name="submenu"><object', text)
            root = ET.fromstring(text)
            subs = {o.get("id") for o in root if o.get("class") == "GtkMenu"}
            named = {p.text for p in root.iter("property") if p.get("name") == "submenu"}
            self.assertTrue(named, f"{name} has submenus")
            self.assertLessEqual(named, subs, "every submenu an item names exists at the top")

    @unittest.skipUnless(os.environ.get("WAYLAND_DISPLAY"), "needs a display for GTK")
    def test_gtk_loads_every_menu(self):
        bar = self.write()
        probe = ("import sys, gi; gi.require_version('Gtk','3.0'); from gi.repository import Gtk; "
                 "b=Gtk.Builder(); b.add_from_file(sys.argv[1]); assert b.get_object('menu')")
        for name in ("emblem", "window", "special", "help"):
            r = subprocess.run([sys.executable, "-c", probe, bar[f"custom/menu-{name}"]["menu-file"]], capture_output=True)
            self.assertEqual(r.returncode, 0, f"GTK could not load the {name} menu ({r.returncode})")

    def test_the_emblem_menu_carries_favorites_and_the_launchers_groups(self):
        bar = self.write()
        _, labels = self.labels(bar["custom/menu-emblem"]["menu-file"])
        for lab in ("About This Computer", "Favorites", "Games", "Graphics", "Internet", "All Apps…", "hypeForge Settings"):
            self.assertIn(lab, labels)
        self.assertIn("GIMP & Friends", labels, "names are escaped, not lost")
        self.assertNotIn("not-installed", " ".join(labels))
        actions = bar["custom/menu-emblem"]["menu-actions"].values()
        self.assertTrue(any(a.endswith("launch steam") for a in actions), "apps open through the launcher")

    def test_the_window_menu_moves_to_each_workspace(self):
        bar = self.write()
        _, labels = self.labels(bar["custom/menu-window"]["menu-file"])
        self.assertIn("1. Daily", labels)
        self.assertIn("2. Gaming", labels)
        self.assertTrue(any(a.endswith("move 2") for a in bar["custom/menu-window"]["menu-actions"].values()))

    def test_special_asks_before_restarting(self):
        bar = self.write()
        acts = list(bar["custom/menu-special"]["menu-actions"].values())
        self.assertTrue(all(" power " in a for a in acts), "every Special item goes through the asking power command")

    def test_nothing_changed_means_no_reload(self):
        self.write()
        class Icons:
            def find(self, name):
                return f"/icons/{name}.svg"
        self.assertFalse(self.mb.write_bar(ENTRIES, Icons()))


class AppName(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.mb = load()
        self.mb.STATE = Path(self.dir.name) / "state"
        from hfapps import Matcher
        self.matcher = Matcher(ENTRIES)

    def tearDown(self):
        self.dir.cleanup()

    def tree(self, focused_app):
        win = {"id": 3, "pid": 9, "type": "con", "app_id": focused_app, "name": "A <b> title", "focused": True,
               "nodes": [], "floating_nodes": []}
        return {"nodes": [{"nodes": [{"name": "1:Daily", "nodes": [win], "floating_nodes": []}]}]}

    def test_the_name_and_icon_of_the_app_in_use(self):
        app_id, name, title = self.mb.focused_app(self.tree("google-chrome"), ENTRIES, self.matcher)
        self.assertEqual((app_id, name), ("google-chrome", "Google Chrome"))
        self.mb.write_state(app_id, name, title)
        app = json.loads((self.mb.STATE / "app.json").read_text())
        icon = json.loads((self.mb.STATE / "appicon.json").read_text())
        self.assertEqual(app["text"], "Google Chrome")
        self.assertEqual(app["tooltip"], "A &lt;b&gt; title", "a title can't break the bar's markup")
        self.assertIn("app-google-chrome", icon["class"])

    def test_no_window_is_the_desktop(self):
        self.assertEqual(self.mb.focused_app({"nodes": []}, ENTRIES, self.matcher)[1], "Desktop")


class TheMenusByKeyboard(unittest.TestCase):
    """Javier, 2026-10-10 on Mac OS 9: Win + Space opened the Rice's list, Window / Special / Help
    had no letter and key, and hypeForge Settings did nothing from the emblem menu."""

    def setUp(self):
        self.m = load()
        self.menus = self.m.build_menus({})

    def test_every_menu_is_also_data_for_its_keyboard_list(self):
        labels = [e[0] for e in self.menus["window"].tree if e]
        self.assertIn("Tuck Away", labels)
        self.assertEqual(len([e for e in self.menus["special"].tree if e]), 4)

    def test_settings_opens_through_its_launcher_entry(self):
        cmd = dict(e for e in self.menus["emblem"].tree if e)["hypeForge Settings"]
        self.assertIn("launch hypeforge-settings", cmd, "a bare start shows nothing: it's a terminal app")

    def test_the_titles_underline_their_key(self):
        src = (HERE / "applets/menubar/hypeforge-menubar").read_text()
        for title in ("Wind<u>o</u>w", "Spec<u>i</u>al", "Hel<u>p</u>"):
            self.assertIn(title, src)
        conf = (HERE / "sway/config").read_text()
        for key, menu in (("o", "window"), ("i", "special"), ("p", "help")):
            self.assertRegex(conf, rf"bindsym \$mod\+{key} exec \S+hypeforge-menubar open {menu}")


class WinSpaceFollowsTheStyle(unittest.TestCase):
    def run_key(self, style):
        spec = importlib.util.spec_from_loader("hfsections", importlib.machinery.SourceFileLoader(
            "hfsections", str(HERE / "applets/sections/hypeforge-sections")))
        s = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(s)
        conf = Path(tempfile.mkdtemp(prefix="hfkey."))
        (conf / "hypeforge/theme").mkdir(parents=True)
        (conf / "hypeforge/theme/state.toml").write_text(f'style = "{style}"\n')
        calls = []
        old_env, old_execv = os.environ.get("XDG_CONFIG_HOME"), os.execv
        os.environ["XDG_CONFIG_HOME"] = str(conf)
        os.execv = lambda prog, argv: calls.append(argv)
        try:
            handled = s.style_launcher()
        finally:
            os.execv = old_execv
            if old_env is None:
                os.environ.pop("XDG_CONFIG_HOME")
            else:
                os.environ["XDG_CONFIG_HOME"] = old_env
        return handled, " ".join(calls[0]) if calls else ""

    def test_windows_11_opens_start(self):
        self.assertIn("hypeforge-panel start", self.run_key("windows-11")[1])

    def test_mac_os_9_opens_the_emblem_menu(self):
        self.assertIn("hypeforge-menubar open emblem", self.run_key("mac-os-9")[1])

    def test_the_rice_keeps_its_list(self):
        self.assertEqual(self.run_key("rice"), (False, ""))


if __name__ == "__main__":
    unittest.main()
