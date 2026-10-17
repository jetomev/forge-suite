"""hypeForge's tray, the shared part (Javier, 2026-10-17: the Dropbox menu "is horrible, and opens on top
of the bar/icon area"). Tray apps (Dropbox, Insync, Steam, Claude…) speak the StatusNotifierItem standard
over D-Bus: they register with a *watcher*, and a *host* shows their icons and menus. Waybar's own tray
was both, and it opens their menus at the mouse pointer, over the bar, in plain GTK. hypeForge's tray is
both now: this module is the watcher and the reading; `hypeforge-tray` keeps the icons on the bar
(Waybar's image pieces), and the `traymenu` panel draws a menu the hypeForge way.

Everything here is plain Gio (GLib's D-Bus), already on the system.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from gi.repository import Gio, GLib

WATCHER = "org.kde.StatusNotifierWatcher"
WATCHER_PATH = "/StatusNotifierWatcher"
ITEM = "org.kde.StatusNotifierItem"
MENU = "com.canonical.dbusmenu"
RUNTIME = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "hypeforge-tray"
SLOTS = Path(os.environ.get("HYPEFORGE_TRAY_SLOTS") or RUNTIME / "slots.json")   # a preview may point elsewhere
MAX_SLOTS = 10

WATCHER_XML = """
<node>
  <interface name="org.kde.StatusNotifierWatcher">
    <method name="RegisterStatusNotifierItem"><arg name="service" type="s" direction="in"/></method>
    <method name="RegisterStatusNotifierHost"><arg name="service" type="s" direction="in"/></method>
    <property name="RegisteredStatusNotifierItems" type="as" access="read"/>
    <property name="IsStatusNotifierHostRegistered" type="b" access="read"/>
    <property name="ProtocolVersion" type="i" access="read"/>
    <signal name="StatusNotifierItemRegistered"><arg type="s"/></signal>
    <signal name="StatusNotifierItemUnregistered"><arg type="s"/></signal>
    <signal name="StatusNotifierHostRegistered"/>
    <signal name="StatusNotifierHostUnregistered"/>
  </interface>
</node>
"""


def bus() -> Gio.DBusConnection:
    return Gio.bus_get_sync(Gio.BusType.SESSION, None)


def split(entry: str, sender: str | None = None) -> tuple[str, str]:
    """An item as the watcher keeps it ("service/path", ":1.48/org/ayatana/…", or just a service) →
    (bus name, object path)."""
    if entry.startswith("/"):                          # registered by its path: the sender owns it
        return sender or "", entry
    if "/" in entry:
        name, _, path = entry.partition("/")
        return name, "/" + path
    return entry, "/StatusNotifierItem"


class Watcher:
    """The registry tray apps talk to. Owns org.kde.StatusNotifierWatcher; when another program holds the
    name (Waybar's own tray, during the switch), it waits in line and takes over when that one lets go."""

    def __init__(self, on_change):
        self.on_change = on_change
        self.items: list[str] = []
        self.hosts: set[str] = set()
        self.conn = bus()
        self.node = Gio.DBusNodeInfo.new_for_xml(WATCHER_XML)
        self.reg = None
        self.owner_id = Gio.bus_own_name_on_connection(
            self.conn, WATCHER, Gio.BusNameOwnerFlags.ALLOW_REPLACEMENT, self._got, self._lost)
        self.conn.signal_subscribe("org.freedesktop.DBus", "org.freedesktop.DBus", "NameOwnerChanged",
                                   "/org/freedesktop/DBus", None, Gio.DBusSignalFlags.NONE, self._owner_changed)
        self.owned = False

    def _got(self, conn, _name):
        self.owned = True
        if self.reg is None:
            self.reg = conn.register_object(WATCHER_PATH, self.node.interfaces[0], self._call, self._get, None)
        conn.emit_signal(None, WATCHER_PATH, WATCHER, "StatusNotifierHostRegistered", None)
        self.on_change()

    def _lost(self, _conn, _name):
        self.owned = False

    def _call(self, conn, sender, _path, _iface, method, params, invocation):
        (service,) = params.unpack()
        if method == "RegisterStatusNotifierItem":
            name, path = split(service, sender)
            if not name.startswith(":") and not name:
                name = sender
            entry = f"{name}{path}"
            if entry not in self.items:
                self.items.append(entry)
                conn.emit_signal(None, WATCHER_PATH, WATCHER, "StatusNotifierItemRegistered", GLib.Variant("(s)", (entry,)))
                self._watch_item(entry)
                self.on_change()
        else:
            self.hosts.add(sender)
            conn.emit_signal(None, WATCHER_PATH, WATCHER, "StatusNotifierHostRegistered", None)
        invocation.return_value(None)

    def _get(self, _conn, _sender, _path, _iface, prop):
        if prop == "RegisteredStatusNotifierItems":
            return GLib.Variant("as", self.items)
        if prop == "IsStatusNotifierHostRegistered":
            return GLib.Variant("b", True)
        return GLib.Variant("i", 0)

    def _watch_item(self, entry: str):
        name, path = split(entry)
        # a changed icon, status or tooltip: redraw (each signal is one of the item's own)
        for sig in ("NewIcon", "NewAttentionIcon", "NewStatus", "NewTitle", "NewToolTip"):
            self.conn.signal_subscribe(name, ITEM, sig, path, None, Gio.DBusSignalFlags.NONE,
                                       lambda *_a: self.on_change())

    def _owner_changed(self, _conn, _sender, _path, _iface, _sig, params):
        name, _old, new = params.unpack()
        if new:
            return
        gone = [e for e in self.items if split(e)[0] == name]
        for e in gone:
            self.items.remove(e)
            self.conn.emit_signal(None, WATCHER_PATH, WATCHER, "StatusNotifierItemUnregistered", GLib.Variant("(s)", (e,)))
        self.hosts.discard(name)
        if gone:
            self.on_change()


def prop(conn, name: str, path: str, key: str, timeout: int = 1500):
    try:
        r = conn.call_sync(name, path, "org.freedesktop.DBus.Properties", "Get", GLib.Variant("(ss)", (ITEM, key)),
                           GLib.VariantType("(v)"), Gio.DBusCallFlags.NONE, timeout, None)
        return r.unpack()[0]
    except GLib.Error:
        return None


def describe(conn, entry: str) -> dict:
    """What the bar and the menu need to know about one tray app."""
    name, path = split(entry)
    get = lambda k: prop(conn, name, path, k)
    tip = get("ToolTip")
    tip_text = ""
    if isinstance(tip, tuple) and len(tip) >= 4:
        tip_text = " — ".join(t for t in (tip[2], tip[3]) if t)
    return {"entry": entry, "name": name, "path": path, "id": get("Id") or "", "title": get("Title") or "",
            "status": get("Status") or "Active", "icon": get("IconName") or "", "theme_path": get("IconThemePath") or "",
            "attention": get("AttentionIconName") or "", "menu": get("Menu") or "", "is_menu": bool(get("ItemIsMenu")),
            "tooltip": tip_text}


def pixmap_png(conn, entry: str, out: Path, key: str = "IconPixmap") -> bool:
    """An icon sent as raw pixels (Electron apps: Claude, Discord): the biggest one, as a PNG file."""
    name, path = split(entry)
    pix = prop(conn, name, path, key)
    if not pix:
        return False
    w, h, data = max(pix, key=lambda p: p[0] * p[1])
    if not (w and h and len(data) >= w * h * 4):
        return False
    from PIL import Image
    raw = bytes(data)
    rgba = bytearray(len(raw))
    rgba[0::4], rgba[1::4], rgba[2::4], rgba[3::4] = raw[1::4], raw[2::4], raw[3::4], raw[0::4]   # ARGB → RGBA
    Image.frombytes("RGBA", (w, h), bytes(rgba)).save(out)
    return True


def menu_layout(conn, name: str, menu_path: str) -> list:
    """The app's menu: [(id, {props}, [children…]), …] (com.canonical.dbusmenu GetLayout)."""
    try:
        conn.call_sync(name, menu_path, MENU, "AboutToShow", GLib.Variant("(i)", (0,)), None,
                       Gio.DBusCallFlags.NONE, 1500, None)
    except GLib.Error:
        pass
    r = conn.call_sync(name, menu_path, MENU, "GetLayout", GLib.Variant("(iias)", (0, -1, [])),
                       GLib.VariantType("(u(ia{sv}av))"), Gio.DBusCallFlags.NONE, 3000, None)
    _rev, (_root, _props, kids) = r.unpack()
    return kids


def menu_click(conn, name: str, menu_path: str, item_id: int) -> None:
    conn.call_sync(name, menu_path, MENU, "Event",
                   GLib.Variant("(isvu)", (item_id, "clicked", GLib.Variant("i", 0), 0)), None,
                   Gio.DBusCallFlags.NONE, 3000, None)


def activate(conn, name: str, path: str) -> bool:
    try:
        conn.call_sync(name, path, ITEM, "Activate", GLib.Variant("(ii)", (0, 0)), None, Gio.DBusCallFlags.NONE, 3000, None)
        return True
    except GLib.Error:
        return False


def read_slots() -> list[dict]:
    try:
        return json.loads(SLOTS.read_text())
    except (OSError, ValueError):
        return []
