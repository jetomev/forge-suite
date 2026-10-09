"""nightForge's pages, driven headless (Textual's Pilot) with live=False: nothing is started,
stopped or written for real."""

from __future__ import annotations

import asyncio
import unittest

from nightforge.app import NightForgeApp, NightView, ScheduleView
from nightforge.settings import Settings


def run(coro):
    return asyncio.run(coro)


class Pages(unittest.TestCase):
    def make(self, **kw):
        return NightForgeApp(Settings(**kw), live=False)

    def test_the_menu_and_its_keys(self):
        app = self.make()
        self.assertEqual([m["title"] for m in app.MENU], ["Night Light", "Schedule", "Help", "Quit"])
        self.assertEqual([m.get("acc") for m in app.MENU[:3]], ["n", "s", "h"])

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.press("2")
                await pilot.pause()
                self.assertTrue(app.query_one("#sec-schedule").display)
                await pilot.press("ctrl+n")
                await pilot.pause()
                self.assertTrue(app.query_one("#sec-night").display)
        run(go())

    def test_warmth_waits_for_save_and_save_is_a_pop_up(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                app.query_one("#nf-warmth").post_message(type(app.query_one("#nf-warmth")).Changed(app.query_one("#nf-warmth"), 3500))
                await pilot.pause()
                self.assertEqual(app.session.changes(), [("Evening warmth", "4000 K", "3500 K")])
                self.assertTrue(app.changes_bar.display)
                await pilot.press("f10")
                await pilot.pause()
                self.assertEqual(len(app.screen_stack), 2, "Save is a pop-up (D-2)")
                await pilot.press("enter")
                await pilot.pause()
                await pilot.pause()
                self.assertEqual(app.session.change_count, 0)
                self.assertEqual(app.session.saved.warmth, 3500)
        run(go())

    def test_preview_is_a_pop_up_that_goes_back_by_itself(self):
        from nightforge.app import PreviewDialog
        PreviewDialog.SECONDS = 1
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                await pilot.press("p")
                await pilot.pause()
                self.assertEqual(len(app.screen_stack), 2, "Preview is a pop-up (D-2)")
                await pilot.pause(1.6)
                self.assertEqual(len(app.screen_stack), 1, "it closed by itself")
                self.assertEqual(app.session.change_count, 0, "and kept nothing")
        run(go())
        PreviewDialog.SECONDS = 10

    def test_schedule_fixed_times(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.press("2")
                await pilot.pause()
                view = app.query_one(ScheduleView)
                view.query_one("#nf-schedule").value = "fixed"
                view.post_message(type(view.query_one("#nf-schedule")).Changed(view.query_one("#nf-schedule"), "fixed"))
                await pilot.pause()
                self.assertFalse(view.query_one("#nf-warm-from").disabled)
                self.assertTrue(view.query_one("#nf-lat").disabled)
                view.query_one("#nf-warm-from").value = "22:30"
                await pilot.pause()
                self.assertEqual(app.session.pending.warm_from, "22:30")
                self.assertEqual(app.session.changes()[0][0], "When")
        run(go())

    def test_quit_asks_when_something_is_not_saved(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                await pilot.pause()
                app.session.pending.warmth = 3000
                await pilot.press("q")
                await pilot.pause()
                self.assertEqual(len(app.screen_stack), 2)
                await pilot.press("n")
                await pilot.pause()
        run(go())

    def test_inside_hypeforge_settings_there_is_no_quit(self):
        app = NightForgeApp(Settings(), live=False, hypeforge=True)
        self.assertNotIn("quit", [m["id"] for m in app.MENU])

    def test_buttons_fit_100_columns(self):
        app = self.make()

        async def go():
            async with app.run_test(size=(100, 30)) as pilot:
                for key in ("1", "2"):
                    await pilot.press(key)
                    await pilot.pause()
                    for w in app.screen.query("Button"):
                        if w.display and w.region.width:
                            self.assertLessEqual(w.region.right, 100)
        run(go())


if __name__ == "__main__":
    unittest.main()
