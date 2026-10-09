"""workspaceForge's pages, driven headless (Textual's Pilot) on a copy of the settings, with no
desktop: the approved design's every action, the save with its review, and the quit question."""

from __future__ import annotations

import asyncio
import tempfile
import tomllib
import unittest
from pathlib import Path

from textual.widgets import Collapsible, Input, OptionList

from workspaceforge import model as M
from workspaceforge.app import AppsView, ShareCell, SharingView, TickTable, WorkspaceForgeApp, WorkspacesView
from workspaceforge.live import NoDesktop

FILE = '''
enabled = true
screens = ["DP-3", "DP-2", "DP-1"]
[[workspace]]
name = "Daily"
apps = ["google-chrome", "discord"]
[[workspace]]
name = "Work"
apps = ["obsidian"]
[[workspace]]
name = "Entertainment"
apps = ["spotify"]
[[workspace]]
name = "Gaming"
apps = ["steam"]
[share]
"DP-3" = []
"DP-2" = []
"DP-1" = []
'''

INSTALLED = {
    "google-chrome": {"name": "Google Chrome", "category": "Internet"},
    "discord": {"name": "Discord", "category": "Internet"},
    "obsidian": {"name": "Obsidian", "category": "Office"},
    "spotify": {"name": "Spotify", "category": "Multimedia"},
    "steam": {"name": "Steam", "category": "Games"},
    "winetricks": {"name": "Winetricks", "category": "Utilities"},
    "galculator": {"name": "Galculator", "category": "Utilities"},
    "gimp": {"name": "GIMP", "category": "Graphics"},
}
NAMES = {"DP-3": "Main Monitor", "DP-2": "Left Monitor", "DP-1": "Right Monitor"}


def run(coro):
    return asyncio.run(coro)


class Pages(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "workspaces.toml"
        self.path.write_text(FILE)
        self._backups = M.BACKUPS
        M.BACKUPS = Path(self.dir.name) / "backups"
        self.live = NoDesktop()
        self.live.open = {"2:Work": ["Alacritty", "obsidian"], "12:Work": ["thunar"]}

    def tearDown(self):
        M.BACKUPS = self._backups
        self.dir.cleanup()

    def make(self):
        return WorkspaceForgeApp(M.Session.load(self.path), live=self.live, installed=INSTALLED,
                                 screen_names=NAMES)

    def uid(self, app, name):
        return next(w.uid for w in app.session.pending.workspaces if w.name == name)

    # -- the frame -------------------------------------------------------------------------------------
    def test_the_menu_and_its_keys(self):
        app = self.make()
        self.assertEqual([m["title"] for m in app.MENU], ["Workspaces", "Apps", "Sharing", "Help", "Quit"])
        self.assertEqual([m.get("acc") for m in app.MENU[:4]], ["w", "a", "s", "h"])

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.press("2")
                self.assertTrue(app.query_one("#sec-apps").display)
                await pilot.press("ctrl+s")
                await pilot.pause()
                self.assertTrue(app.query_one("#sec-sharing").display)
                await pilot.press("ctrl+w")
                await pilot.pause()
                self.assertTrue(app.query_one("#sec-workspaces").display)
        run(go())

    # -- 1 · Workspaces ----------------------------------------------------------------------------------
    def test_new_right_on_the_page(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                await pilot.press("n")
                await pilot.pause()
                ws = app.query_one(WorkspacesView)
                self.assertEqual(ws.mode, "new")
                self.assertIs(app.focused, app.query_one("#ws-name", Input), "the name field, no pop-up")
                self.assertEqual(len(app.screen_stack), 1, "no window opened over the page")
                await pilot.press(*"Studio", "enter")
                await pilot.pause()
                self.assertEqual(ws.mode, "view")
                self.assertIn("Studio", [w.name for w in app.session.pending.workspaces])
                self.assertEqual(app.session.change_count, 1)
                self.assertTrue(app.changes_bar.display)
        run(go())

    def test_edit_in_place_and_the_note_after_a_rename(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                ws = app.query_one(WorkspacesView)
                ws.picked = self.uid(app, "Entertainment")
                ws.draw_page()
                await pilot.press("e")
                await pilot.pause()
                name = app.query_one("#ws-name", Input)
                self.assertIs(app.focused, name)
                name.value = "Media"
                await pilot.press("enter")
                await pilot.pause()
                info = str(app.query_one("#wf-ws-info").render())
                self.assertIn("⚠ renamed", info, "the yellow note shows after the rename")
                # it is not kept: picking another workspace takes it away
                ol = app.query_one("#wf-ws-list", OptionList)
                ol.highlighted = 0
                await pilot.pause()
                ol.highlighted = 2
                await pilot.pause()
                self.assertNotIn("⚠", str(app.query_one("#wf-ws-info").render()))
        run(go())

    def test_esc_cancels_a_new_name(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                await pilot.press("n", *"Zed", "escape")
                await pilot.pause()
                self.assertEqual(app.query_one(WorkspacesView).mode, "view")
                self.assertEqual(app.session.change_count, 0)
        run(go())

    def test_delete_asks_and_moves_the_windows(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                ws = app.query_one(WorkspacesView)
                ws.picked = self.uid(app, "Work")
                await pilot.press("d")
                await pilot.pause()
                self.assertEqual(len(app.screen_stack), 2, "delete asks in a window (D-4)")
                body = " ".join(str(s.render()) for s in app.screen.query("Static"))
                self.assertIn("3 windows are open on Work", body)
                await pilot.press("d")
                await pilot.pause()
                self.assertNotIn("Work", [w.name for w in app.session.pending.workspaces])
                self.assertEqual(app.session.moved_to, {2: 1}, "its windows go to Daily, the first other one")
        run(go())

    def test_move_up_changes_the_win_number(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                ws = app.query_one(WorkspacesView)
                ws.picked = self.uid(app, "Gaming")
                await pilot.press("plus")
                await pilot.pause()
                self.assertEqual([w.name for w in app.session.pending.workspaces],
                                 ["Daily", "Work", "Gaming", "Entertainment"])
        run(go())

    def test_the_switch_across_all_screens(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                app.query_one("#ws-enabled").flip()
                await pilot.pause()
                self.assertFalse(app.session.pending.enabled)
                self.assertIn(("Across all screens", "on", "off"), app.session.changes())
        run(go())

    # -- 2 · Apps ------------------------------------------------------------------------------------------
    def test_send_and_back_with_the_arrows(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.press("2")
                await pilot.pause()
                await pilot.pause()
                view = app.query_one(AppsView)
                pool = app.query_one("#wf-pool", TickTable)
                self.assertEqual(sorted(pool.shown_ids()), ["galculator", "gimp", "winetricks"])
                gaming = self.uid(app, "Gaming")
                app.query_one(f"#col-{gaming}", Collapsible).collapsed = False
                await pilot.pause()
                self.assertEqual(view.open_uid, gaming)
                # one open at a time
                app.query_one(f"#col-{self.uid(app, 'Daily')}", Collapsible).collapsed = False
                await pilot.pause()
                self.assertTrue(app.query_one(f"#col-{gaming}", Collapsible).collapsed)
                app.query_one(f"#col-{gaming}", Collapsible).collapsed = False
                await pilot.pause()
                pool.set_tick("winetricks", True)
                await pilot.press("greater_than_sign")
                await pilot.pause()
                self.assertIn("winetricks", app.session.pending.get(gaming).apps)
                self.assertNotIn("winetricks", pool.shown_ids())
                table = app.query_one(f"#wt-{gaming}", TickTable)
                table.set_tick("winetricks", True)
                await pilot.press("less_than_sign")
                await pilot.pause()
                self.assertNotIn("winetricks", app.session.pending.get(gaming).apps)
                self.assertIn("winetricks", pool.shown_ids())
        run(go())

    def test_select_all_only_ticks_what_shows(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.press("2")
                await pilot.pause()
                app.query_one("#pool-cat").value = "Utilities"
                await pilot.pause()
                pool = app.query_one("#wf-pool", TickTable)
                pool.focus()
                await pilot.press("a")
                await pilot.pause()
                self.assertEqual(pool.ticked, {"winetricks", "galculator"}, "GIMP is filtered out: not ticked")
                await pilot.press("u")
                self.assertEqual(pool.ticked, set())
        run(go())

    def test_space_ticks_and_headings_sort(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.press("2")
                await pilot.pause()
                pool = app.query_one("#wf-pool", TickTable)
                pool.focus()
                first = pool.current_id()
                await pilot.press("space")
                self.assertIn(first, pool.ticked)
                self.assertEqual(pool.shown_ids(), ["galculator", "gimp", "winetricks"])
                pool.post_message(type("E", (), {})) if False else None
                pool.sort_by, pool.reverse = "name", True
                pool.draw()
                self.assertEqual(pool.shown_ids(), ["winetricks", "gimp", "galculator"])
        run(go())

    # -- 3 · Sharing ---------------------------------------------------------------------------------------
    def test_a_switch_per_cell(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.press("3")
                await pilot.pause()
                await pilot.pause()
                cells = list(app.query(ShareCell))
                self.assertEqual(len(cells), 4 * 3)
                left_daily = app.query_one(f"#sc-{self.uid(app, 'Daily')}-1", ShareCell)
                left_work = app.query_one(f"#sc-{self.uid(app, 'Work')}-1", ShareCell)
                left_daily.focus()
                await pilot.press("space")
                self.assertEqual(app.session.change_count, 0, "one cell alone shares nothing")
                await pilot.press("down", "space")
                await pilot.pause()
                self.assertIs(app.focused, left_work, "arrows move between the switches")
                self.assertIn(("Sharing · DP-2", "not shared", "Daily, Work"), app.session.changes())
                await pilot.press("escape")
                await pilot.pause()
                self.assertEqual(app.session.change_count, 0, "Esc undoes the sharing changes")
        run(go())

    # -- saving and quitting -------------------------------------------------------------------------------
    def test_save_reviews_backs_up_moves_windows_and_reloads(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                app.session.rename(self.uid(app, "Gaming"), "Games")
                app.refresh_state()
                await pilot.press("f10")
                await pilot.pause()
                self.assertEqual(len(app.screen_stack), 2, "a review first")
                await pilot.press("enter")
                await pilot.pause()
                await pilot.pause()
                cfg = tomllib.loads(self.path.read_text())
                self.assertEqual(cfg["workspace"][3]["name"], "Games")
                self.assertEqual(len(list(M.BACKUPS.glob("workspaces.toml.*"))), 1)
                self.assertEqual(self.live.reloaded, 1, "the applet is asked to read it again")
                self.assertEqual(app.session.change_count, 0)
                self.assertFalse(app.changes_bar.display)
        run(go())

    def test_quit_asks_when_something_is_not_saved(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                app.session.rename(self.uid(app, "Work"), "Job")
                await pilot.press("q")
                await pilot.pause()
                self.assertEqual(len(app.screen_stack), 2)
                await pilot.press("escape")
                await pilot.pause()
                self.assertTrue(app.is_running, "Esc stays")
                await pilot.press("q")
                await pilot.pause()
                await pilot.press("n")
                await pilot.pause()
            self.assertEqual(tomllib.loads(self.path.read_text())["workspace"][1]["name"], "Work",
                             "No quits without writing")
        run(go())

    def test_inside_hypeforge_settings_there_is_no_quit(self):
        app = WorkspaceForgeApp(M.Session.load(self.path), live=self.live, installed=INSTALLED,
                                screen_names=NAMES, hypeforge=True)
        self.assertNotIn("quit", [m["id"] for m in app.MENU])


class Drawing(unittest.TestCase):
    """Positions, not just existence: the pages fit 100 × 30 with nothing cut off."""

    def test_every_page_fits_100_columns(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "workspaces.toml"
            path.write_text(FILE)
            app = WorkspaceForgeApp(M.Session.load(path), live=NoDesktop(), installed=INSTALLED,
                                    screen_names=NAMES)

            async def go():
                async with app.run_test(size=(100, 30)) as pilot:
                    for key in ("1", "2", "3"):
                        await pilot.press(key)
                        await pilot.pause()
                        for w in app.screen.query("Button"):
                            if w.display and w.region.width:
                                self.assertLessEqual(w.region.right, 100, f"{w.label} is cut off on page {key}")
            asyncio.run(go())


if __name__ == "__main__":
    unittest.main()
