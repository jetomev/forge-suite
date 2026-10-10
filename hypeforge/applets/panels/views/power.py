"""The power buttons (the Rice's R-5, D-75): big round buttons over a dimmed screen.

Lock · Log Out · Restart · Shut Down, from the launcher's [power] settings (sections.toml), so
the bar's ⏻ menu and this panel always run the same commands. Lock goes at once; the other three
ask by turning into "Restart?" — a second press does it, anything else cancels. Arrow keys move,
Enter presses, Escape closes.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from gi.repository import Gtk

import panelkit

SECTIONS = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "hypeforge/applets/sections.toml"
ACTIONS = [("lock", "Lock", "system-lock-screen", False),
           ("logout", "Log Out", "system-log-out", True),
           ("reboot", "Restart", "system-reboot", True),
           ("shutdown", "Shut Down", "system-shutdown", True)]
CSS = """
.hf-power button {{ border-radius: 999px; min-width: 112px; min-height: 112px; padding: 0; }}
.hf-power .hf-label {{ margin-top: 12px; color: {text}; font-size: {size}pt; font-weight: bold; }}
"""


def commands():
    try:
        with open(SECTIONS, "rb") as f:
            return tomllib.load(f).get("power", {})
    except (OSError, tomllib.TOMLDecodeError):
        return {}


class Asking:
    """The power panel's one rule: Lock goes at once; the others ask first. press() returns
    "run" (do it) or "ask" (show "Restart?"); pressing another one moves the question to it."""

    def __init__(self, confirm: dict):
        self.confirm, self.asking = confirm, None

    def press(self, key: str) -> str:
        if self.confirm.get(key) and self.asking != key:
            self.asking = key
            return "ask"
        self.asking = None
        return "run"


def build(look: panelkit.Look, args) -> panelkit.Panel:
    cmds = commands()
    row = Gtk.Box(spacing=36)
    row.get_style_context().add_class("hf-power")
    asking = Asking({key: confirm for key, _l, _i, confirm in ACTIONS})
    labels = {}

    def press(_button, key, label, _confirm):
        for lab, text in labels.values():   # only one asks at a time
            lab.set_text(text)
        if asking.press(key) == "ask":
            labels[key][0].set_text(f"{label}?")
            return
        panel.close()
        panelkit.run_command(cmds[key])

    for key, label, icon, confirm in ACTIONS:
        if not cmds.get(key):
            continue
        column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        button = Gtk.Button()
        button.add(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DIALOG))
        button.get_child().set_pixel_size(48)
        if key != "lock":
            button.get_style_context().add_class("danger")
        button.connect("clicked", press, key, label, confirm)
        text = Gtk.Label(label=label)
        text.get_style_context().add_class("hf-label")
        labels[key] = (text, label)
        column.pack_start(button, False, False, 0)
        column.pack_start(text, False, False, 0)
        row.pack_start(column, False, False, 0)
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(text=look.colour["panel_text"], size=look.size * 1.3).encode())
    Gtk.StyleContext.add_provider_for_screen(row.get_screen() or panelkit.Gdk.Screen.get_default(), provider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
    panel = panelkit.Panel("power", row, look, edges=(), dim=True, card=False)
    return panel
