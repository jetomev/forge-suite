"""forgekit example: the password box (v0.8.0) — dots centred, and sudoForge's layout.

    PYTHONPATH=. python examples/password.py          # sudoForge's layout
    PYTHONPATH=. python examples/password.py plain    # the box every Forge app shows

Type anything: only dots appear, centred. Enter or OK closes it and says how
many characters were typed (never what they were); Esc cancels.
"""

from __future__ import annotations

import sys

from textual.widgets import Static

from forgekit import ForgeApp, PasswordDialog


class PasswordExample(ForgeApp):
    APP_NAME = "password example"
    MENU = [{"id": "home", "title": "Home", "kind": "section"}]

    def compose_sections(self):
        yield Static("The password box opens on start. Quit with Ctrl+Q.", id="sec-home")

    def on_mount(self) -> None:
        super().on_mount()
        if "plain" in sys.argv[1:]:
            box = PasswordDialog("[sudo] password for javier: ")
        else:
            box = PasswordDialog("", title="sudoForge", heading="USB drives wants admin rights",
                                 words='To mount the USB stick "KINGSTON".',
                                 note="Asked by udiskie · checked by the system (polkit)",
                                 label="Password for javier")
        self.push_screen(box, self.answered)

    def answered(self, value: str | None) -> None:
        said = "Cancelled." if value is None else f"Got {len(value)} characters (not shown)."
        self.query_one("#sec-home", Static).update(said)


if __name__ == "__main__":
    PasswordExample().run()
