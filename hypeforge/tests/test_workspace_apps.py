"""F-50 (#55): apps open on their own workspace however they are started (Javier, 2026-10-09).

Each workspace lists its apps in workspaces.toml. A new window is matched to a listed app by its
names; the Workspaces applet takes it to its workspace with every screen following (not in the
first seconds after login), and Window Placement leaves such a window to it. The launcher opens a
listed app on its workspace however it is picked. Every test was seen failing with its piece of
the engine taken out.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/common"))
import hfapps  # noqa: E402
import hfplace  # noqa: E402


def load(path, name):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


def entry(name, exec_, terminal=False, wmclass=""):
    return {"name": name, "icon": "", "exec": exec_, "terminal": terminal, "categories": set(), "wmclass": wmclass}


ENTRIES = {
    "steam": entry("Steam", "/usr/bin/steam %U"),
    "Sim Companies": entry("Sim Companies", "steam steam://rungameid/2253720"),
    "google-chrome": entry("Google Chrome", "/usr/bin/google-chrome-stable %U"),
    "Alacritty": entry("Alacritty", "alacritty"),
    "fresh": entry("Fresh", "alacritty --class fresh -e fresh %F", wmclass="fresh"),
    "btop": entry("btop++", "btop", terminal=True),
    "masterpdfeditor4": entry("Master PDF Editor", "/opt/master-pdf-editor-4/masterpdfeditor4 %f"),
    "com.spotify.Client": entry("Spotify", "/usr/bin/flatpak run --branch=stable com.spotify.Client"),
    "envapp": entry("Env App", "env GDK_BACKEND=x11 /usr/bin/realprog --flag"),
}

LISTS = '''
enabled = true
screens = ["DP-3", "DP-2", "DP-1"]
[[workspace]]
name = "Daily"
apps = ["google-chrome", "steam"]
[[workspace]]
name = "Work"
apps = ["Alacritty", "fresh", "masterpdfeditor4", "envapp"]
[[workspace]]
name = "Entertainment"
apps = ["com.spotify.Client"]
[[workspace]]
name = "Gaming"
apps = ["steam", "Sim Companies"]
[[workspace]]
name = "Monitoring"
apps = ["btop"]
'''


class Names(unittest.TestCase):
    def test_a_steam_game_is_its_own_window_not_steam(self):
        strong, weak = hfapps.app_names("Sim Companies", ENTRIES["Sim Companies"])
        self.assertIn("steam_app_2253720", strong)
        self.assertNotIn("steam", strong | weak, "a game must never be taken for the Steam client")

    def test_a_terminal_app_carries_its_own_name(self):
        self.assertIn("fresh", hfapps.app_names("fresh", ENTRIES["fresh"])[0])
        self.assertIn("btop", hfapps.app_names("btop", ENTRIES["btop"])[0])
        cmd = hfapps.command_for("btop", ENTRIES["btop"])
        self.assertTrue(cmd.startswith("alacritty --class btop -e "), cmd)

    def test_wrappers_are_looked_through(self):
        self.assertIn("realprog", hfapps.app_names("envapp", ENTRIES["envapp"])[1], "env and its settings skipped")
        self.assertIn("com.spotify.client", hfapps.app_names("com.spotify.Client", ENTRIES["com.spotify.Client"])[0])


class Matching(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "workspaces.toml"
        self.path.write_text(LISTS)
        self.index = hfapps.AppIndex(self.path, entries=ENTRIES)

    def tearDown(self):
        self.dir.cleanup()

    def of(self, app_id=None, cls=None, instance=None):
        return self.index.of_window({"app_id": app_id, "window_properties": {"class": cls, "instance": instance}})

    def test_windows_go_to_their_lists(self):
        self.assertEqual(self.of("google-chrome"), 1)
        self.assertEqual(self.of("Alacritty"), 2)
        self.assertEqual(self.of("fresh"), 2)
        self.assertEqual(self.of(cls="Sim Companies", instance="sim companies"), 4, "by the game's Name")
        self.assertEqual(self.of(cls="steam_app_2253720"), 4, "by Steam's own game window name")
        self.assertEqual(self.of("btop"), 5)
        self.assertEqual(self.of(cls="Spotify"), 3)

    def test_one_app_one_workspace_the_first_list_wins(self):
        self.assertEqual(self.of(cls="steam"), 1, "steam is on Daily first, then Gaming")
        self.assertEqual(self.index.of_app("steam"), 1)

    def test_a_reverse_domain_window_answers_to_its_last_part(self):
        self.assertEqual(self.of("net.code-industry.masterpdfeditor4"), 2)

    def test_apps_on_no_list_stay_where_they_open(self):
        self.assertIsNone(self.of("thunar"))
        self.assertIsNone(self.of(cls="Wow.exe"))
        self.assertIsNone(self.index.of_app("thunar"))

    def test_a_missing_or_broken_file_means_no_lists(self):
        self.path.write_text("this is [ not toml")
        self.assertIsNone(hfapps.AppIndex(self.path, entries=ENTRIES).of_window({"app_id": "google-chrome"}))
        self.assertIsNone(hfapps.AppIndex(Path(self.dir.name) / "none.toml", entries=ENTRIES).of_app("steam"))

    def test_the_lists_are_read_again_when_they_change(self):
        self.assertEqual(self.of("btop"), 5)
        self.path.write_text(LISTS.replace('apps = ["btop"]', 'apps = []'))
        os.utime(self.path, ns=(1, 1))  # a different time stamp, even within the same tick
        self.assertIsNone(self.of("btop"))


class FakeSway:
    """Records the commands; answers the tree and the workspaces it was given."""

    def __init__(self, tree, workspaces):
        self.tree, self.workspaces, self.commands = tree, workspaces, []

    def ask(self, kind, payload=""):
        from hfsway import GET_TREE
        return self.tree if kind == GET_TREE else self.workspaces

    def run(self, *commands):
        self.commands.extend(commands)
        return [{"success": True}]


def tree_with(window_id, on_workspace, app_id="steam"):
    win = {"id": window_id, "type": "con", "app_id": app_id, "nodes": [], "floating_nodes": [], "marks": []}
    wss = [{"id": i + 100, "type": "workspace", "name": n, "nodes": [win] if n == on_workspace else [],
            "floating_nodes": []} for i, n in enumerate(["1:Daily", "11:Daily", "21:Daily", "4:Gaming"])]
    return {"id": 1, "type": "root", "nodes": wss, "floating_nodes": []}, win


class Arrive(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        cfg = Path(self.dir.name) / "workspaces.toml"
        cfg.write_text(LISTS.replace('apps = ["google-chrome", "steam"]', 'apps = ["google-chrome"]'))
        self.ws = load(HERE / "applets/workspaces/hypeforge-workspaces", "hfworkspaces")
        self.ws.CONFIG = cfg
        self.ws.CURRENT = Path(self.dir.name) / "current"
        self.ws.signal_bar = lambda *a: None
        self.ws.just_logged_in = lambda: False
        self.placed = []
        self.ws.placement = lambda: (True, ["DP-3", "DP-2", "DP-1"], [(0, "fill")])
        self.ws.hfplace = type("P", (), {"place": staticmethod(lambda *a, **k: self.placed.append((a, k)))})
        self.grid = self.ws.Grid()
        self.index = hfapps.AppIndex(cfg, entries=ENTRIES)
        self.shown = [{"output": o, "name": n, "visible": True, "focused": o == "DP-3"}
                      for o, n in (("DP-3", "1:Daily"), ("DP-2", "11:Daily"), ("DP-1", "21:Daily"))]

    def tearDown(self):
        self.dir.cleanup()

    def test_a_game_opened_on_daily_is_taken_to_gaming_and_the_screens_follow(self):
        tree, win = tree_with(42, "1:Daily")
        sway = FakeSway(tree, self.shown)
        self.ws.arrive(sway, self.grid, self.index, win)
        self.assertIn(f"[con_id=42] mark --add {hfapps.ARRIVED}42", sway.commands, "marked first")
        self.assertIn('workspace "4:Gaming"', sway.commands, "the screens switch to Gaming")
        self.assertIn('[con_id=42] move container to workspace "4:Gaming"', sway.commands)
        self.assertLess(sway.commands.index(f"[con_id=42] mark --add {hfapps.ARRIVED}42"),
                        sway.commands.index('[con_id=42] move container to workspace "4:Gaming"'))
        self.assertEqual(len(self.placed), 1, "and Placement's order gives it its spot")
        self.assertEqual(self.placed[0][1], {"handed_over": True})
        self.assertEqual(self.ws.CURRENT.read_text(), "4")

    def test_already_on_its_workspace_nothing_happens(self):
        tree, win = tree_with(43, "4:Gaming")
        sway = FakeSway(tree, self.shown)
        self.ws.arrive(sway, self.grid, self.index, win)
        self.assertEqual(sway.commands, [])
        self.assertEqual(self.placed, [])

    def test_an_app_on_no_list_is_left_alone(self):
        tree, win = tree_with(44, "1:Daily", app_id="thunar")
        sway = FakeSway(tree, self.shown)
        self.ws.arrive(sway, self.grid, self.index, win)
        self.assertEqual(sway.commands, [])

    def test_right_after_login_it_goes_quietly(self):
        self.ws.just_logged_in = lambda: True
        tree, win = tree_with(45, "1:Daily")
        sway = FakeSway(tree, self.shown)
        self.ws.arrive(sway, self.grid, self.index, win)
        self.assertIn('[con_id=45] move container to workspace "4:Gaming"', sway.commands)
        self.assertNotIn('workspace "4:Gaming"', sway.commands, "the screens stay put")
        self.assertEqual(self.placed, [])


class PlacementLeavesTakenWindows(unittest.TestCase):
    def test_a_window_the_workspaces_applet_took_is_not_placed_twice(self):
        tree, win = tree_with(46, "1:Daily")
        win["marks"] = [f"{hfapps.ARRIVED}46"]
        sway = FakeSway(tree, [{"output": "DP-3", "name": "1:Daily", "visible": True}])
        hfplace.place(sway, ["DP-3"], [(0, "fill")], 46)
        self.assertEqual(sway.commands, [], "Placement's own watcher leaves it")
        hfplace.place(sway, ["DP-3"], [(0, "fill")], 46, handed_over=True)
        self.assertTrue(sway.commands, "but places it when the Workspaces applet hands it over")


class Launcher(unittest.TestCase):
    def test_a_listed_app_opens_on_its_workspace_however_it_is_picked(self):
        m = load(HERE / "applets/sections/hypeforge-sections", "hfsections")
        calls = []
        m.subprocess = type("S", (), {"run": staticmethod(lambda cmd, **k: calls.append(cmd))})
        m.AppIndex = lambda: type("I", (), {"of_app": staticmethod(lambda a: {"steam": 4}.get(a))})()
        m.launch("steam", ENTRIES["steam"])  # typed, Favorites or All apps: launch() is the one door
        self.assertEqual(calls[0][1:], ["go", "4"])
        self.assertEqual(calls[1][:2], ["swaymsg", "exec"])
        calls.clear()
        m.launch("thunar", entry("Thunar", "thunar"))
        self.assertEqual(len(calls), 1, "an app on no list: no switch, just open it")


class Seeding(unittest.TestCase):
    def test_the_shipped_lists_read_back_and_name_each_app_once(self):
        cfg = tomllib.loads((HERE / "applets/workspaces/workspaces.toml").read_text())
        names = [a for w in cfg["workspace"] for a in w.get("apps", [])]
        self.assertTrue(names, "the default file ships with lists")
        self.assertEqual(len(names), len(set(names)), "one app, one workspace")

    def test_seeding_refuses_to_overwrite_lists(self):
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d) / "workspaces.toml"
            ws.write_text(LISTS)
            out = subprocess.run([sys.executable, str(HERE / "scripts/seed-workspace-apps.py"),
                                  str(HERE / "applets/sections/sections.toml"), str(ws), "--write"],
                                 capture_output=True, text=True)
            self.assertNotEqual(out.returncode, 0)
            self.assertEqual(ws.read_text(), LISTS, "nothing changed")


class Breaker(unittest.TestCase):
    """The safety valve (2026-10-09): never again a desktop locked by switching."""

    def setUp(self):
        self.ws = load(HERE / "applets/workspaces/hypeforge-workspaces", "hfworkspaces_b")
        self.now = [100.0]
        self.b = self.ws.Breaker(clock=lambda: self.now[0])

    def test_it_trips_after_too_many_switches_and_stands_still(self):
        results = []
        for _ in range(self.b.LIMIT + 1):
            results.append(self.b.tripped())
            self.now[0] += 0.05
        self.assertEqual(results[:self.b.LIMIT], [False] * self.b.LIMIT, "normal switching is never stopped")
        self.assertTrue(results[-1], "one more within the window trips it")
        self.now[0] += 1
        self.assertTrue(self.b.tripped(), "it stands still during the pause")

    def test_it_comes_back_after_the_pause(self):
        for _ in range(self.b.LIMIT + 1):
            self.b.tripped()
        self.now[0] += self.b.PAUSE + 0.1
        self.assertFalse(self.b.tripped())

    def test_slow_switching_never_trips_it(self):
        for _ in range(100):
            self.assertFalse(self.b.tripped())
            self.now[0] += self.b.WINDOW / self.b.LIMIT + 0.01


if __name__ == "__main__":
    unittest.main()


class Pills(unittest.TestCase):
    """The workspace pills (look step 3, the Rice's R-2): numbers, the active one wide with its
    name, busy ones marked; one small file per pill so the bar redraws them with `cat`."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        cfg = Path(self.dir.name) / "workspaces.toml"
        cfg.write_text(LISTS)
        self.ws = load(HERE / "applets/workspaces/hypeforge-workspaces", "hfworkspaces_pills")
        self.ws.CONFIG = cfg
        self.ws.PILLS = Path(self.dir.name) / "pills"
        self.ws.BAR_FRAGMENT = Path(self.dir.name) / "workspaces.waybar.json"
        self.ws.signal_bar = lambda *a: None
        self.grid = self.ws.Grid()

    def tearDown(self):
        self.dir.cleanup()

    def pill(self, i):
        import json
        return json.loads((self.ws.PILLS / f"{i}.json").read_text())

    def test_the_active_pill_is_named_the_others_are_numbers(self):
        self.ws.write_pills(self.grid, 4, busy={1, 4})
        self.assertEqual(self.pill(4), {"text": "4  Gaming", "class": ["pill", "active"], "tooltip": "4. Gaming"})
        self.assertEqual(self.pill(1)["text"], "1")
        self.assertEqual(self.pill(1)["class"], ["pill", "busy"])
        self.assertEqual(self.pill(2)["class"], ["pill", "empty"])

    def test_nothing_changed_writes_nothing_new(self):
        self.assertTrue(self.ws.write_pills(self.grid, 1, busy=set()))
        self.assertFalse(self.ws.write_pills(self.grid, 1, busy=set()), "the bar is only told when a pill changed")
        self.assertTrue(self.ws.write_pills(self.grid, 1, busy={3}))

    def test_busy_counts_every_screen(self):
        win = {"id": 7, "pid": 99, "nodes": [], "floating_nodes": []}
        tree = {"nodes": [{"name": "DP-3", "nodes": [{"name": "1:Daily", "nodes": [], "floating_nodes": []}]},
                          {"name": "DP-2", "nodes": [{"name": "13:Entertainment", "nodes": [], "floating_nodes": [win]}]}]}
        self.assertEqual(self.ws.busy_workspaces(FakeSway(tree, []), self.grid), {3},
                         "a floating window on screen 2 makes workspace 3 busy")

    def test_the_bar_gets_a_pill_per_workspace_that_reads_its_file(self):
        import json
        self.ws.write_bar(self.grid)
        bar = json.loads(self.ws.BAR_FRAGMENT.read_text())
        self.assertEqual(bar["group/workspace-pills"]["modules"], [f"custom/pill-{i}" for i in range(1, 6)])
        self.assertIn("cat ", bar["custom/pill-2"]["exec"])
        self.assertTrue(bar["custom/pill-2"]["exec"].endswith("2.json"))
        self.assertTrue(bar["custom/pill-2"]["on-click"].endswith(" go 2"))
        self.assertEqual(bar["custom/pill-2"]["signal"], self.ws.BAR_SIGNAL)

    def test_the_pager_shows_each_workspaces_windows_as_dots(self):
        self.ws.write_pills(self.grid, 2, busy={1: 2, 3: 6})
        import json
        pager = lambda i: json.loads((self.ws.PILLS / f"pager-{i}.json").read_text())
        self.assertEqual(pager(1)["text"], "● ●")
        self.assertEqual(pager(1)["class"], ["pager", "busy"])
        self.assertEqual(pager(3)["text"], "● ● ● ● +", "more than four: a +")
        self.assertEqual(pager(2)["class"], ["pager", "active"])
        self.assertEqual(pager(2)["text"], " ", "an empty workspace keeps its box")
        self.assertIn("6 windows", pager(3)["tooltip"])

    def test_window_counts_add_up_every_screen(self):
        a, b, c = ({"id": n, "pid": n, "nodes": [], "floating_nodes": []} for n in (1, 2, 3))
        tree = {"nodes": [{"name": "DP-3", "nodes": [{"name": "1:Daily", "nodes": [a, b], "floating_nodes": []}]},
                          {"name": "DP-2", "nodes": [{"name": "11:Daily", "nodes": [], "floating_nodes": [c]}]}]}
        self.assertEqual(self.ws.window_counts(FakeSway(tree, []), self.grid), {1: 3})

    def test_the_bar_gets_a_pager_box_per_workspace(self):
        import json
        self.ws.write_bar(self.grid)
        bar = json.loads(self.ws.BAR_FRAGMENT.read_text())
        self.assertEqual(bar["group/pager"]["modules"], [f"custom/pager-{i}" for i in range(1, 6)])
        self.assertTrue(bar["custom/pager-3"]["exec"].endswith("pager-3.json"))
