"""The Control Strip (Mac OS 9, D-72): a row of small buttons that STAYS in the bottom-left corner,
over the windows, folding to a tab with its handle. Each button opens what already does the job:
the clipboard's list, the USB drives' menu, the network menu, Quick Settings (sound, Bluetooth,
night light…), the night light now, displayForge, the calendar with the notifications. It never
takes the keyboard and never closes on a click elsewhere.
"""

from __future__ import annotations

import shlex
import sys

from gi.repository import Gtk

import panelkit

A = panelkit.APPLETS
PANEL = f"{shlex.quote(sys.executable)} {shlex.quote(str(panelkit.HERE / 'hypeforge-panel'))}"
NEAR = "--edges bottom,left --margin bottom=40,left=8"
TILES = [  # glyph (Symbols Nerd Font), what it is, what a click runs
    ("󰅌", "Clipboard", f"{A / 'clipboard/hypeforge-clipboard'} list"),
    ("󰕓", "USB drives", f"{A / 'drives/hypeforge-drives'} menu"),
    ("󰤨", "Network", "networkmanager_dmenu"),
    ("󰕾", "Sound, Bluetooth, night light… (Quick Settings)", f"{PANEL} quick {NEAR}"),
    ("󰖔", "Night light (nightForge)", "alacritty --class nightforge -e nightforge"),
    ("󰍹", "Screens (displayForge)", "alacritty --class displayforge -e displayforge"),
    ("󰂚", "Notifications and the calendar", f"{PANEL} calendar {NEAR}"),
]
CSS = """
.hf-strip {{ background: {bg}; border: 1px solid {line}; border-left: none; padding: 2px; }}
.hf-strip button {{ min-width: 30px; min-height: 26px; padding: 0 4px; border: none; background: transparent;
                    font-family: "Symbols Nerd Font", "JetBrainsMono Nerd Font"; font-size: 14px; color: {text}; }}
.hf-strip button:hover {{ background-color: {hover}; }}
.hf-strip button.hf-handle {{ min-width: 12px; font-size: 10px; color: {dim}; }}
"""


def build(look: panelkit.Look, args) -> panelkit.Panel:
    c = look.colour
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(bg=c["panel_bg"], line=c["panel_border"], text=c["panel_text"],
                                       hover=c["panel_hover"], dim=c["panel_text_dim"]).encode())
    Gtk.StyleContext.add_provider_for_screen(panelkit.Gdk.Screen.get_default(), provider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
    row = Gtk.Box(spacing=0)
    row.get_style_context().add_class("hf-strip")
    tiles = []
    for glyph, what, cmd in TILES:
        b = Gtk.Button(label=glyph)
        b.set_tooltip_text(what)
        b.connect("clicked", lambda _b, cmd=cmd: panelkit.run_command(cmd))
        tiles.append(b)
        row.pack_start(b, False, False, 0)
    handle = Gtk.Button(label="◀")
    handle.get_style_context().add_class("hf-handle")
    handle.set_tooltip_text("Fold the Control Strip")

    def fold(_b):
        folded = tiles[0].get_visible()
        for t in tiles:
            t.set_visible(not folded)
        handle.set_label("▶" if folded else "◀")
        handle.set_tooltip_text("Open the Control Strip" if folded else "Fold the Control Strip")
    handle.connect("clicked", fold)
    row.pack_start(handle, False, False, 0)
    return panelkit.Panel("strip", row, look, edges=["bottom", "left"], margins={"bottom": 6, "left": 0},
                          card=False, stays=True)
