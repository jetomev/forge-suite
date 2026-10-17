#!/usr/bin/env python3
"""A stand-in tray app for the benches and the tests (2026-10-17): a StatusNotifierItem with a menu
(com.canonical.dbusmenu) read from a JSON file — by default the shape of Dropbox's real menu, with made-up
account details. It registers with whatever watcher the bus has (hypeForge's tray in a bench), answers
GetLayout, and writes every "clicked" it receives to --clicks, so a test can see which entry was picked.

    fake-tray-app.py [--layout tests/fixtures/tray-menu-dropbox.json] [--id dropbox] [--title Dropbox]
                     [--icon folder] [--clicks FILE] [--pixmap]

Only ever on a bench's own bus: never run it on the desktop's.
"""

import argparse
import json
import os
from pathlib import Path

from gi.repository import Gio, GLib

HERE = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--layout", default=str(HERE / "tests/fixtures/tray-menu-dropbox.json"))
ap.add_argument("--id", default="dropbox-client-fake")
ap.add_argument("--title", default="Dropbox")
ap.add_argument("--icon", default="folder")
ap.add_argument("--clicks")
ap.add_argument("--pixmap", action="store_true", help="send the icon as pixels instead of a name (like Electron apps)")
a = ap.parse_args()

ITEM_XML = """<node><interface name="org.kde.StatusNotifierItem">
<property name="Id" type="s" access="read"/><property name="Title" type="s" access="read"/>
<property name="Status" type="s" access="read"/><property name="IconName" type="s" access="read"/>
<property name="IconPixmap" type="a(iiay)" access="read"/><property name="Menu" type="o" access="read"/>
<property name="ItemIsMenu" type="b" access="read"/><property name="Category" type="s" access="read"/>
<method name="Activate"><arg type="i" direction="in"/><arg type="i" direction="in"/></method>
</interface></node>"""
MENU_XML = """<node><interface name="com.canonical.dbusmenu">
<method name="GetLayout"><arg type="i" direction="in"/><arg type="i" direction="in"/><arg type="as" direction="in"/>
<arg type="u" direction="out"/><arg type="(ia{sv}av)" direction="out"/></method>
<method name="Event"><arg type="i" direction="in"/><arg type="s" direction="in"/><arg type="v" direction="in"/><arg type="u" direction="in"/></method>
<method name="AboutToShow"><arg type="i" direction="in"/><arg type="b" direction="out"/></method>
</interface></node>"""

layout = json.loads(Path(a.layout).read_text())


def node(n):
    i, props, kids = n
    vprops = {k: (GLib.Variant("b", v) if isinstance(v, bool) else GLib.Variant("i", v) if isinstance(v, int)
                  else GLib.Variant("s", str(v))) for k, v in props.items()}
    return GLib.Variant("(ia{sv}av)", (i, vprops, [GLib.Variant("v", node(k)) for k in kids]))


def pixels():
    w = h = 16
    data = bytes([255, 0x89, 0xb4, 0xfa] * (w * h))      # ARGB, one blue square
    return [(w, h, data)]


def item_call(conn, _s, _p, _i, method, params, inv):
    if a.clicks:
        Path(a.clicks).open("a").write("activate\n")
    inv.return_value(None)


def item_get(_c, _s, _p, _i, prop):
    return {"Id": GLib.Variant("s", a.id), "Title": GLib.Variant("s", a.title), "Status": GLib.Variant("s", "Active"),
            "IconName": GLib.Variant("s", "" if a.pixmap else a.icon),
            "IconPixmap": GLib.Variant("a(iiay)", pixels() if a.pixmap else []),
            "Menu": GLib.Variant("o", "/MenuBar"), "ItemIsMenu": GLib.Variant("b", False),
            "Category": GLib.Variant("s", "ApplicationStatus")}[prop]


def menu_call(conn, _s, _p, _i, method, params, inv):
    if method == "GetLayout":
        inv.return_value(GLib.Variant("(u(ia{sv}av))", (1, (0, {"children-display": GLib.Variant("s", "submenu")},
                                                             [GLib.Variant("v", node(n)) for n in layout]))))
    elif method == "Event":
        eid, kind, _data, _t = params.unpack()
        if a.clicks and kind == "clicked":
            Path(a.clicks).open("a").write(f"{eid}\n")
        inv.return_value(None)
    else:
        inv.return_value(GLib.Variant("(b)", (False,)))


conn = Gio.bus_get_sync(Gio.BusType.SESSION)
conn.register_object("/StatusNotifierItem", Gio.DBusNodeInfo.new_for_xml(ITEM_XML).interfaces[0], item_call, item_get, None)
conn.register_object("/MenuBar", Gio.DBusNodeInfo.new_for_xml(MENU_XML).interfaces[0], menu_call, None, None)
name = f"org.kde.StatusNotifierItem-{os.getpid()}-1"


def register():
    try:
        conn.call_sync("org.kde.StatusNotifierWatcher", "/StatusNotifierWatcher", "org.kde.StatusNotifierWatcher",
                       "RegisterStatusNotifierItem", GLib.Variant("(s)", (name,)), None, Gio.DBusCallFlags.NONE, 2000, None)
        return False
    except GLib.Error:
        return True                                 # no watcher yet: try again


Gio.bus_own_name_on_connection(conn, name, Gio.BusNameOwnerFlags.NONE, lambda *_: GLib.timeout_add(200, register), None)
# a watcher that comes later (or comes back) is registered with again, as real tray apps do
def watcher_changed(_conn, _sender, _path, _iface, _signal, params, *_rest):
    if params.unpack()[2]:
        GLib.timeout_add(100, register)


conn.signal_subscribe("org.freedesktop.DBus", "org.freedesktop.DBus", "NameOwnerChanged", "/org/freedesktop/DBus",
                      "org.kde.StatusNotifierWatcher", Gio.DBusSignalFlags.NONE, watcher_changed)
GLib.MainLoop().run()
