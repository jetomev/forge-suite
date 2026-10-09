"""The launcher's groups (Javier, 2026-10-08, D-64): the standard kinds of app every desktop uses.
An app goes where its own Categories say, by a fixed priority; apps with no category are placed by
hand; empty groups are hidden; where an app opens is separate from its group."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import tomllib
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
APP = HERE / "applets/sections/hypeforge-sections"
CONF = HERE / "applets/sections/sections.toml"


def load():
    spec = importlib.util.spec_from_loader("hfsections", importlib.machinery.SourceFileLoader("hfsections", str(APP)))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def app(name, *cats):
    return {"name": name, "icon": "", "exec": "true", "terminal": False, "categories": set(cats)}


class Groups(unittest.TestCase):
    def setUp(self):
        self.m = load()
        self.cfg = tomllib.loads(CONF.read_text())
        self.apps = {
            "settingsapp": app("A Settings App", "Settings", "System"),
            "steam": app("Steam", "FileTransfer", "Game", "Network"),
            "okular": app("Okular", "Graphics", "Office", "Viewer"),
            "chrome": app("Chrome", "Network", "WebBrowser"),
            "alacritty": app("Alacritty", "System", "TerminalEmulator"),
            "btop": app("btop", "Monitor", "System", "ConsoleOnly"),
            "calc": app("Calculator", "Utility"),
            "World_of_Warcraft_Pi5": app("World of Warcraft Pi5"),
            "hypeforge-settings": app("hypeForge Settings", "Settings"),
            "mystery": app("Mystery"),
            "nmdmenu": app("NetworkManager Dmenu", "Network", "Settings"),
        }
        self.groups = {s["name"]: ids for s, ids in self.m.sort_into_sections(self.cfg, self.apps)}

    def test_the_standard_names(self):
        names = [s["name"] for s in self.cfg["section"]]
        self.assertEqual(names, ["Development", "Education", "Games", "Graphics", "Internet", "Multimedia",
                                 "Office", "Science", "Settings", "System", "Utilities", "Other"])

    def test_an_app_goes_where_its_categories_say_by_priority(self):
        where = {a: g for g, ids in self.groups.items() for a in ids}
        self.assertEqual(where["settingsapp"], "Settings", "Settings beats System")
        self.assertEqual(where["steam"], "Games", "Game beats Network")
        self.assertEqual(where["okular"], "Graphics", "Graphics beats Office")
        self.assertEqual(where["chrome"], "Internet")
        self.assertEqual(where["alacritty"], "System")
        self.assertEqual(where["calc"], "Utilities")
        self.assertEqual(where["World_of_Warcraft_Pi5"], "Games", "placed by hand: it declares nothing")
        self.assertEqual(where["mystery"], "Other", "nothing else claims it")
        self.assertEqual(where["nmdmenu"], "Settings", "Settings beats Network, though Internet comes first on screen")

    def test_every_app_once_and_empty_groups_hidden(self):
        placed = [a for ids in self.groups.values() for a in ids]
        self.assertEqual(sorted(placed), sorted(self.apps))
        self.assertNotIn("Education", self.groups)
        self.assertNotIn("Science", self.groups)

    def test_hypeforge_settings_comes_first_in_settings(self):
        self.assertEqual(self.groups["Settings"][0], "hypeforge-settings")

    def test_groups_no_longer_say_where_an_app_opens(self):
        """F-50 (#55): where an app opens is its workspace's list in workspaces.toml, the one place
        it is set (workspaceForge D-5). The launcher's file must not keep a second answer."""
        self.assertFalse(any("workspace" in s for s in self.cfg["section"]))
        self.assertNotIn("workspaces", self.cfg)
        self.assertFalse(hasattr(self.m, "workspace_for"))

if __name__ == "__main__":
    unittest.main()
