"""v0.8.0: the password field with centred dots, and sudoForge's layout (its D-2).

Layout is checked by position, not by existence: the dots are found on the
line the field actually draws, and the centred lines are measured against the
box. Every test also looks for the password itself on screen (it must never be
there). The screen runs headless through Textual's Pilot.
Run: python -m unittest discover -s tests -v
"""

from __future__ import annotations

import time
import unittest

from textual.widgets import Static

from forgekit import ForgeApp, PasswordDialog, PasswordField, glyph
from forgekit.console import GLYPHS

DOT = GLYPHS["bullet"][0]


class Host(ForgeApp):
    APP_NAME = "host"
    MENU = [{"id": "home", "title": "Home", "kind": "section"}]

    def compose_sections(self):
        yield Static("home", id="sec-home")


async def until(pilot, cond, seconds=4.0):
    end = time.time() + seconds
    while not cond() and time.time() < end:
        await pilot.pause(0.05)
    return cond()


def screen_lines(app) -> list[str]:
    """What the screen really shows, line by line (the compositor's output)."""
    return [strip.text for strip in app.screen._compositor.render_strips()]


def drawn_line(widget, y: int) -> str:
    """Line ``y`` of what is drawn where ``widget`` sits, border included."""
    r = widget.region
    return screen_lines(widget.app)[r.y + y][r.x:r.x + r.width]


def screen_text(app) -> str:
    return "\n".join(screen_lines(app))


class FieldOnItsOwn(unittest.TestCase):
    def test_repr_never_shows_the_password(self):
        f = PasswordField()
        f._chars = list("hunter22")
        self.assertNotIn("hunter22", repr(f))
        self.assertIn("length=8", repr(f))

    def test_the_dot_is_in_the_console_font(self):
        fancy, plain = GLYPHS["bullet"]
        self.assertEqual(fancy, "•")
        self.assertEqual(plain, "•", "the text console draws the same dot")


class Dialog(unittest.IsolatedAsyncioTestCase):
    async def open(self, pilot, app, **kw):
        self.result = "untouched"
        app.push_screen(PasswordDialog("[sudo] password for javier: ", **kw),
                        lambda v: setattr(self, "result", v))
        # the screen is current before its insides are built: wait for the field itself
        self.assertTrue(await until(pilot, lambda: isinstance(app.screen, PasswordDialog)
                                    and bool(app.screen.query("#pw-input"))))
        await pilot.pause()
        return app.screen.query_one("#pw-input", PasswordField)

    async def test_typed_dots_are_centred_in_the_field(self):
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            field = await self.open(pilot, app)
            self.assertTrue(field.has_focus, "the field takes the keyboard")
            await pilot.press(*"s3cret!")
            await pilot.pause()
            line = drawn_line(field, 1)
            self.assertEqual(line.count(DOT), 7, line)
            first, last = line.index(DOT), line.rindex(DOT)
            left, right = first, len(line) - 1 - last
            self.assertLessEqual(abs(left - right), 1, f"centred: {left} left, {right} right")
            self.assertGreater(left, 5, "not at the left edge")
            self.assertNotIn("s3cret", screen_text(app), "the password is never drawn")

    async def test_empty_field_shows_its_hint_centred(self):
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            field = await self.open(pilot, app)
            line = drawn_line(field, 1)
            i = line.index("password")
            self.assertLessEqual(abs(i - (len(line) - 1 - (i + 7))), 1, line)

    async def test_backspace_ctrl_u_and_paste(self):
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            field = await self.open(pilot, app)
            await pilot.press(*"abcd", "backspace")
            self.assertEqual(field.value, "abc")
            await pilot.press("ctrl+u")
            self.assertEqual(field.value, "")
            field.post_message(__import__("textual.events", fromlist=["Paste"]).Paste("pa\nss"))
            await pilot.pause()
            self.assertEqual(field.value, "pass", "a pasted line break is dropped, never sent")
            await pilot.press("backspace", "backspace", "backspace", "backspace", "backspace")
            self.assertEqual(field.value, "", "backspace on empty does nothing")

    async def test_enter_gives_the_password_and_empties_the_field(self):
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            field = await self.open(pilot, app)
            await pilot.press(*"pw 1", "enter")
            self.assertTrue(await until(pilot, lambda: self.result != "untouched"))
            self.assertEqual(self.result, "pw 1", "a space is part of the password")
            self.assertEqual(field.value, "", "nothing left behind in memory")

    async def test_ok_button_gives_the_password(self):
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            await self.open(pilot, app)
            await pilot.press(*"xyz")
            await pilot.click("#pw-ok")
            self.assertTrue(await until(pilot, lambda: self.result != "untouched"))
            self.assertEqual(self.result, "xyz")

    async def test_escape_cancels_and_empties_the_field(self):
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            field = await self.open(pilot, app)
            await pilot.press(*"secret", "escape")
            self.assertTrue(await until(pilot, lambda: self.result != "untouched"))
            self.assertIsNone(self.result)
            self.assertEqual(field.value, "")

    async def test_a_long_password_stays_inside_the_field(self):
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            field = await self.open(pilot, app)
            await pilot.press(*("x" * 120))
            await pilot.pause()
            self.assertEqual(field.value, "x" * 120, "every character kept")
            line = drawn_line(field, 1)
            self.assertLess(line.count(DOT), field.content_size.width + 1)
            self.assertNotEqual(line[0], DOT, "the border is still drawn")
            self.assertNotEqual(line[-1], DOT, "the border is still drawn")

    async def test_the_old_layout_still_reads_the_same(self):
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            await self.open(pilot, app)
            text = screen_text(app)
            self.assertIn("Your password (javier)", text)
            self.assertEqual(len(app.screen.query("#pw-heading")), 0, "no heading unless asked")

    async def test_sudoforge_layout_is_centred_and_in_order(self):
        app = Host()
        async with app.run_test(size=(100, 32)) as pilot:
            await self.open(pilot, app, title="sudoForge", heading="nog wants to run as admin",
                            detail="pacman -S --needed firefox",
                            note="Started from Terminal (Alacritty) · checked by sudo",
                            label="Password for javier")
            scr = app.screen
            box = scr.query_one(".forge-password").content_region
            order = []
            for wid, text in [("#pw-heading", "nog wants to run as admin"),
                              ("#pw-detail", "pacman -S --needed firefox"),
                              ("#pw-note", "Started from Terminal"),
                              ("#pw-label", "Password for javier")]:
                w = scr.query_one(wid)
                region = w.region
                order.append(region.y)
                row = next(y for y in range(w.region.height) if text in drawn_line(w, y))
                line = drawn_line(w, row)
                i = line.index(text)
                full = text if wid != "#pw-note" else "Started from Terminal (Alacritty) · checked by sudo"
                left, right = i, len(line) - (i + len(full))
                self.assertLessEqual(abs(left - right), 1, f"{wid} centred: {left}/{right}")
                self.assertEqual(region.width, box.width, f"{wid} as wide as the field")
            field = scr.query_one("#pw-input")
            order.append(field.region.y)
            self.assertEqual(order, sorted(order), "heading, command, note, label, field — top to bottom")
            note, label = scr.query_one("#pw-note").region, scr.query_one("#pw-label").region
            self.assertGreaterEqual(label.y - (note.y + note.height), 1, "a blank line before the label")
            self.assertEqual(field.region.width, box.width, "the heading bar matches the field's width")


if __name__ == "__main__":
    unittest.main()
