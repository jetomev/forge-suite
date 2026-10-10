"""The taskbar row (look program step 3): pinned + running apps in one, on throwaway folders.

Favorites are pinned and always shown, in their order; any other app with a window is added
after them; a window is matched to its installed app by the launcher's own names; one small file
per slot; a click on a running app goes to its windows in turn, on a pinned one that isn't
running it opens it through the launcher.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/common"))


def load():
    loader = importlib.machinery.SourceFileLoader("hftaskbar", str(HERE / "applets/taskbar/hypeforge-taskbar"))
    spec = importlib.util.spec_from_loader("hftaskbar", loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


def entry(name, exec_, icon, terminal=False, wmclass=""):
    return {"name": name, "icon": icon, "exec": exec_, "terminal": terminal, "categories": set(), "wmclass": wmclass}


ENTRIES = {
    "google-chrome": entry("Google Chrome", "/usr/bin/google-chrome-stable %U", "google-chrome"),
    "thunar": entry("Thunar", "thunar %F", "thunar"),
    "gimp": entry("GIMP", "gimp-3.0 %U", "gimp", wmclass="gimp"),
    "btop": entry("btop++", "btop", "btop", terminal=True),
}


def win(i, app_id, focused=False, floating=False, urgent=False):
    return {"id": i, "pid": 1000 + i, "type": "floating_con" if floating else "con", "app_id": app_id,
            "name": app_id, "focused": focused, "urgent": urgent, "nodes": [], "floating_nodes": []}


def tree(*windows):
    tiled = [w for w in windows if w["type"] == "con"]
    floating = [w for w in windows if w["type"] == "floating_con"]
    return {"type": "root", "nodes": [{"type": "output", "nodes": [
        {"type": "workspace", "name": "1:Daily", "nodes": tiled, "floating_nodes": floating}]}], "floating_nodes": []}


class FakeSway:
    def __init__(self, t):
        self.t, self.commands = t, []

    def ask(self, kind, payload=""):
        return self.t

    def run(self, *c):
        self.commands.extend(c)


class Row(unittest.TestCase):
    def setUp(self):
        self.tb = load()
        self.m = self.tb.Matcher(ENTRIES)

    def test_pinned_first_in_their_order_then_running_ones(self):
        t = tree(win(5, "gimp"), win(7, "google-chrome", focused=True), win(9, "btop"))
        items = self.tb.row(t, ENTRIES, self.m, ["thunar", "google-chrome"])
        self.assertEqual([i["id"] for i in items], ["thunar", "google-chrome", "gimp", "btop"])
        self.assertEqual(items[0]["windows"], [], "a pinned app shows even when it isn't running")
        self.assertTrue(items[1]["focused"])
        self.assertFalse(items[2]["pinned"])

    def test_two_windows_of_one_app_are_one_icon(self):
        t = tree(win(3, "google-chrome"), win(4, "google-chrome", floating=True))
        items = self.tb.row(t, ENTRIES, self.m, [])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["windows"], [3, 4])

    def test_a_window_of_no_installed_app_still_shows(self):
        items = self.tb.row(tree(win(8, "mystery-tool")), ENTRIES, self.m, [])
        self.assertEqual(items[0]["id"], "mystery-tool")
        self.assertTrue(items[0]["noicon"])

    def test_a_pin_that_is_not_installed_is_left_out(self):
        items = self.tb.row(tree(), ENTRIES, self.m, ["gone-app", "thunar"])
        self.assertEqual([i["id"] for i in items], ["thunar"])


class Files(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.tb = load()
        d = Path(self.dir.name)
        self.tb.STATE = d / "state"
        self.tb.BAR_FRAGMENT = d / "taskbar.waybar.json"
        self.tb.BAR_STYLE = d / "taskbar.css"
        self.tb.signal_bar = lambda *a: None
        self.m = self.tb.Matcher(ENTRIES)

    def tearDown(self):
        self.dir.cleanup()

    def slot(self, s):
        return json.loads((self.tb.STATE / f"{s}.json").read_text())

    def test_one_file_per_slot_with_its_state(self):
        pins = ["thunar", "google-chrome"]
        t = tree(win(7, "google-chrome", focused=True), win(5, "gimp", urgent=True))
        self.assertTrue(self.tb.write_state(self.tb.row(t, ENTRIES, self.m, pins), pins))
        self.assertEqual(self.slot("pin-1")["class"], ["app", "app-thunar", "idle", "pinned"])
        self.assertEqual(self.slot("pin-2")["class"], ["app", "app-google-chrome", "focused", "pinned"])
        self.assertEqual(self.slot("run-1")["class"], ["app", "app-gimp", "running", "unpinned", "urgent"])
        self.assertEqual(self.slot("run-2"), {"text": "", "class": "empty"}, "an unused slot is hidden")
        self.assertFalse(self.tb.write_state(self.tb.row(t, ENTRIES, self.m, pins), pins), "nothing changed")

    def test_the_bar_gets_a_module_per_slot_and_an_icon_rule_per_app(self):
        class Icons:
            def find(self, name):
                return f"/icons/{name}.svg"
        self.tb.write_bar(["thunar"], ENTRIES, Icons())
        bar = json.loads(self.tb.BAR_FRAGMENT.read_text())
        self.assertEqual(bar["group/taskbar"]["modules"][:2], ["custom/tb-pin-1", "custom/tb-run-1"])
        self.assertEqual(len(bar["group/taskbar"]["modules"]), 1 + self.tb.EXTRA)
        self.assertEqual(bar["custom/tb-pin-1"]["signal"], 12)
        css = self.tb.BAR_STYLE.read_text()
        self.assertIn('.app-gimp { background-image: url("file:///icons/gimp.svg"); }', css)
        self.assertNotIn("[", css.split("*/", 1)[1], "GTK's CSS has no attribute selectors")

    def test_a_click_cycles_through_an_apps_windows_and_opens_a_pin_not_running(self):
        pins = ["thunar", "google-chrome"]
        t = tree(win(3, "google-chrome", focused=True), win(4, "google-chrome"))
        self.tb.write_state(self.tb.row(t, ENTRIES, self.m, pins), pins)
        fake = FakeSway(t)
        self.tb.Sway = lambda: fake
        self.tb.click("pin-2")
        self.assertEqual(fake.commands, ["[con_id=4] focus"], "the app in use: its next window")
        launched = []
        self.tb.subprocess = type("S", (), {"run": staticmethod(lambda cmd, **k: launched.append(cmd))})
        self.tb.apps = lambda: ENTRIES
        self.tb.click("pin-1")
        self.assertEqual(launched[0][1:], ["launch", "thunar"], "not running: the launcher opens it on its workspace")


if __name__ == "__main__":
    unittest.main()
