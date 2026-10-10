#!/usr/bin/env python3
"""hypeForge applets · close a pop-up when you click anywhere else (Javier, 2026-10-10).

"Submenus corresponding to the bars should close when they lose focus." A see-through layer over
EVERY screen, under the pop-up: a click anywhere outside the pop-up lands on it and closes the
pop-up. Moving the mouse does nothing (Sway gives focus to the window under the mouse, which is why
the lists can't simply close on focus loss — they'd vanish as the mouse moves, 2026-10-05).

Two ways in:
  - the GTK panels call `backdrops(on_click, dim_monitor)` in their own process;
  - the fuzzel lists run `hfbackdrop.py <pid>` beside fuzzel (hfmenu.run): a click ends that pid,
    and the backdrop goes away by itself once the pid is gone.
"""

from __future__ import annotations

import os
import signal
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gdk, GLib, Gtk, GtkLayerShell  # noqa: E402

NAMESPACE = "hypeforge-backdrop"


def backdrops(on_click, dim_monitor=None, dim_rgba: str | None = None) -> list[Gtk.Window]:
    """One see-through layer per screen (the TOP layer: above windows and the bar, under pop-ups
    on the OVERLAY layer). `dim_monitor` gets `dim_rgba` instead (the Rice's power buttons)."""
    display = Gdk.Display.get_default()
    out = []
    provider = Gtk.CssProvider()
    provider.load_from_data(b"window.hf-backdrop { background: transparent; }"
                            + (f"window.hf-backdrop.dim {{ background: {dim_rgba}; }}".encode() if dim_rgba else b""))
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    for i in range(display.get_n_monitors()):
        m = display.get_monitor(i)
        w = Gtk.Window()
        w.get_style_context().add_class("hf-backdrop")
        if dim_rgba and dim_monitor is not None and m == dim_monitor:
            w.get_style_context().add_class("dim")
        visual = w.get_screen().get_rgba_visual()
        if visual:
            w.set_visual(visual)
        GtkLayerShell.init_for_window(w)
        GtkLayerShell.set_namespace(w, NAMESPACE)
        GtkLayerShell.set_layer(w, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_monitor(w, m)
        GtkLayerShell.set_exclusive_zone(w, -1)
        for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM, GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
            GtkLayerShell.set_anchor(w, edge, True)
        GtkLayerShell.set_keyboard_mode(w, GtkLayerShell.KeyboardMode.NONE)   # the keyboard stays with the pop-up
        w.connect("button-press-event", lambda *_: on_click())
        out.append(w)
    return out


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def main(argv) -> int:
    """`hfbackdrop.py <pid>`: until <pid> ends, a click anywhere outside ends it."""
    if len(argv) != 2 or not argv[1].isdigit():
        print(__doc__)
        return 2
    pid = int(argv[1])

    def close():
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
        Gtk.main_quit()

    windows = backdrops(close)
    for w in windows:
        w.show_all()
    GLib.timeout_add(150, lambda: _alive(pid) or Gtk.main_quit())
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, lambda *_: (Gtk.main_quit(), False)[1])
    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
