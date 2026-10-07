"""The real box (not a stand-in): drawn headless, typed into, answering over a socket.

Added after the first live test, where the box crashed on start (forgekit's
colours were not loaded) and the stand-in box in test_service could not see it.
"""

from __future__ import annotations

import json
import socket
import time
import unittest

from forgekit import PasswordDialog, PasswordField

from sudoforge.box import BoxApp

QUESTION = {"heading": "Claude wants to run as admin", "words": None, "detail": "true",
            "note": "Started from Terminal (Alacritty) · checked by sudo",
            "label": "Password for javier", "attempt": 1}


async def until(pilot, cond, seconds=5.0):
    end = time.time() + seconds
    while not cond() and time.time() < end:
        await pilot.pause(0.05)
    return cond()


class RealBox(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ours, self.theirs = socket.socketpair()

    def tearDown(self):
        for s in (self.ours, self.theirs):
            s.close()

    def reply(self) -> dict:
        self.ours.settimeout(5)
        data = b""
        while not data.endswith(b"\n"):
            data += self.ours.recv(4096)
        return json.loads(data)

    async def open(self, pilot, app):
        self.assertTrue(await until(pilot, lambda: isinstance(app.screen, PasswordDialog)
                                    and bool(app.screen.query("#pw-input"))))
        await pilot.pause()

    async def test_it_draws_the_question_and_sends_the_password(self):
        app = BoxApp(dict(QUESTION), self.theirs)
        async with app.run_test(size=(66, 24)) as pilot:
            await self.open(pilot, app)
            lines = [s.text for s in app.screen._compositor.render_strips()]
            text = "\n".join(lines)
            for part in ("Claude wants to run as admin", "true", "Started from Terminal", "Password for javier"):
                self.assertIn(part, text)
            self.assertTrue(app.screen.query_one("#pw-input", PasswordField).has_focus)
            await pilot.press(*"pw 42", "enter")
        self.assertEqual(self.reply(), {"ok": True, "password": "pw 42"})

    async def test_escape_sends_no(self):
        app = BoxApp(dict(QUESTION), self.theirs)
        async with app.run_test(size=(66, 24)) as pilot:
            await self.open(pilot, app)
            await pilot.press("escape")
        self.assertEqual(self.reply(), {"ok": False})

    async def test_a_second_try_says_so(self):
        app = BoxApp(dict(QUESTION, attempt=2), self.theirs)
        async with app.run_test(size=(66, 24)) as pilot:
            await self.open(pilot, app)
            text = "\n".join(s.text for s in app.screen._compositor.render_strips())
            self.assertIn("try 2 of 3", text)
            self.assertIn("didn't work", text)
            await pilot.press("escape")

    async def test_the_service_closing_closes_the_box(self):
        app = BoxApp(dict(QUESTION), self.theirs)
        async with app.run_test(size=(66, 24)) as pilot:
            await self.open(pilot, app)
            self.ours.shutdown(socket.SHUT_RDWR)
            self.assertTrue(await until(pilot, lambda: app._exit_renderables is not None or not app.is_running, 5))

    async def test_it_fits_its_window(self):
        app = BoxApp(dict(QUESTION), self.theirs)
        async with app.run_test(size=(66, 24)) as pilot:
            await self.open(pilot, app)
            box = app.screen.query_one(".forge-password").region
            self.assertLessEqual(box.right, 66)
            self.assertLessEqual(box.bottom, 24, f"the box fits the 66×24 window: {box}")
            await pilot.press("escape")


if __name__ == "__main__":
    unittest.main()
