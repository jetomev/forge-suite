#!/usr/bin/env python3
"""A stand-in window for the benches (2026-10-17): a plain GTK window that lets Sway draw its title bar,
or (`csd`) one that draws its own, like GNOME's apps and Claude Desktop.

    fake-window.py APP_ID [plain|csd]
"""

import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # noqa: E402

app_id = sys.argv[1]
own_bar = len(sys.argv) > 2 and sys.argv[2] == "csd"
GLib.set_prgname(app_id)
w = Gtk.Window(title=f"A window ({app_id})")
if own_bar:
    w.set_titlebar(Gtk.HeaderBar(title=f"Its own bar ({app_id})", show_close_button=True))
w.set_default_size(420, 260)
w.add(Gtk.Label(label=app_id))
w.show_all()
GLib.timeout_add_seconds(180, Gtk.main_quit)
Gtk.main()
