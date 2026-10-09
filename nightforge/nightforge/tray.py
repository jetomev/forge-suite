"""nightForge's tray icon (D-4): ☀ by day, ☾ while warm, ○ when off, with its menu.

A StatusNotifierItem — the standard way apps put an icon in a bar's tray (Waybar's tray speaks
it) — and its menu in the matching com.canonical.dbusmenu form, over the session's D-Bus with
Gio (python-gobject). The pictures are drawn here, so they look the same in any icon theme.

    nightforge tray     run it (one copy per session; `nightforge start` starts it at login)
"""

from __future__ import annotations

import math
import os
import shutil
import subprocess
import sys

from . import control
from .settings import Settings

WATCHER = "org.kde.StatusNotifierWatcher"
ITEM_PATH = "/StatusNotifierItem"
MENU_PATH = "/MenuBar"
PIDFILE = control.RUNTIME / "tray.pid"

SNI_XML = """
<node><interface name="org.kde.StatusNotifierItem">
  <property name="Category" type="s" access="read"/><property name="Id" type="s" access="read"/>
  <property name="Title" type="s" access="read"/><property name="Status" type="s" access="read"/>
  <property name="WindowId" type="i" access="read"/><property name="IconName" type="s" access="read"/>
  <property name="IconPixmap" type="a(iiay)" access="read"/><property name="OverlayIconName" type="s" access="read"/>
  <property name="AttentionIconName" type="s" access="read"/><property name="ToolTip" type="(sa(iiay)ss)" access="read"/>
  <property name="ItemIsMenu" type="b" access="read"/><property name="Menu" type="o" access="read"/>
  <method name="ContextMenu"><arg type="i" direction="in"/><arg type="i" direction="in"/></method>
  <method name="Activate"><arg type="i" direction="in"/><arg type="i" direction="in"/></method>
  <method name="SecondaryActivate"><arg type="i" direction="in"/><arg type="i" direction="in"/></method>
  <method name="Scroll"><arg type="i" direction="in"/><arg type="s" direction="in"/></method>
  <signal name="NewIcon"/><signal name="NewToolTip"/><signal name="NewTitle"/>
  <signal name="NewStatus"><arg type="s"/></signal>
</interface></node>"""

MENU_XML = """
<node><interface name="com.canonical.dbusmenu">
  <property name="Version" type="u" access="read"/><property name="TextDirection" type="s" access="read"/>
  <property name="Status" type="s" access="read"/><property name="IconThemePath" type="as" access="read"/>
  <method name="GetLayout"><arg type="i" direction="in"/><arg type="i" direction="in"/><arg type="as" direction="in"/>
    <arg type="u" direction="out"/><arg type="(ia{sv}av)" direction="out"/></method>
  <method name="GetGroupProperties"><arg type="ai" direction="in"/><arg type="as" direction="in"/>
    <arg type="a(ia{sv})" direction="out"/></method>
  <method name="GetProperty"><arg type="i" direction="in"/><arg type="s" direction="in"/><arg type="v" direction="out"/></method>
  <method name="Event"><arg type="i" direction="in"/><arg type="s" direction="in"/><arg type="v" direction="in"/>
    <arg type="u" direction="in"/></method>
  <method name="EventGroup"><arg type="a(isvu)" direction="in"/><arg type="ai" direction="out"/></method>
  <method name="AboutToShow"><arg type="i" direction="in"/><arg type="b" direction="out"/></method>
  <method name="AboutToShowGroup"><arg type="ai" direction="in"/><arg type="ai" direction="out"/>
    <arg type="ai" direction="out"/></method>
  <signal name="ItemsPropertiesUpdated"><arg type="a(ia{sv})"/><arg type="a(ias)"/></signal>
  <signal name="LayoutUpdated"><arg type="u"/><arg type="i"/></signal>
  <signal name="ItemActivationRequested"><arg type="i"/><arg type="u"/></signal>
</interface></node>"""


# ---- the pictures --------------------------------------------------------------------------------

def picture(kind: str, size: int) -> bytes:
    """ARGB32 (network order) for ☀ sun · ☾ moon · ○ off, drawn with soft edges."""
    c = (size - 1) / 2
    r = size * 0.27
    out = bytearray()
    # Javier (2026-10-09): "muted during the day, mustard color when night light activates"
    colour = {"day": (166, 173, 200), "warm": (225, 173, 1), "off": (108, 112, 134)}[kind]

    def cover(x, y):
        d = math.hypot(x - c, y - c)
        if kind == "off":                          # a ring
            return max(0.0, min(1.0, 1 - abs(d - r) / (size * 0.06)))
        disc = max(0.0, min(1.0, r + 0.5 - d))
        if kind == "warm":                         # a crescent: the disc minus a shifted disc
            d2 = math.hypot(x - (c + r * 0.55), y - (c - r * 0.35))
            return max(0.0, disc - max(0.0, min(1.0, r * 0.85 + 0.5 - d2)))
        rays = 0.0                                 # the sun: a disc and eight short rays
        if r * 1.35 < d < r * 1.75:
            a = math.atan2(y - c, x - c)
            rays = max(0.0, 1 - abs(math.sin(4 * a)) * 2.6)
        return max(disc, rays)

    for y in range(size):
        for x in range(size):
            a = int(255 * cover(x, y))
            out += bytes((a, *colour))
    return bytes(out)


# ---- the tray item ------------------------------------------------------------------------------

class Tray:
    def __init__(self) -> None:
        import gi
        gi.require_version("Gio", "2.0")
        from gi.repository import Gio, GLib
        self.Gio, self.GLib = Gio, GLib
        self.revision = 1
        self.state = None
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.name = f"org.kde.StatusNotifierItem-{os.getpid()}-1"
        self.bus.register_object(ITEM_PATH, Gio.DBusNodeInfo.new_for_xml(SNI_XML).interfaces[0],
                                 self._item_call, self._item_get, None)
        self.bus.register_object(MENU_PATH, Gio.DBusNodeInfo.new_for_xml(MENU_XML).interfaces[0],
                                 self._menu_call, self._menu_get, None)
        Gio.bus_own_name_on_connection(self.bus, self.name, Gio.BusNameOwnerFlags.NONE, None, None)
        Gio.bus_watch_name_on_connection(self.bus, WATCHER, Gio.BusNameWatcherFlags.NONE,
                                         self._watcher_up, None)
        self.refresh()
        GLib.timeout_add_seconds(20, self._tick)

    # -- what it shows ---------------------------------------------------------------------------
    def settings(self) -> Settings:
        return Settings.load()

    def refresh(self) -> None:
        st = control.status(self.settings())
        if st != self.state:
            self.state = st
            for sig in ("NewIcon", "NewToolTip", "NewTitle"):
                self._emit(ITEM_PATH, "org.kde.StatusNotifierItem", sig, None)
            self.revision += 1
            self._emit(MENU_PATH, "com.canonical.dbusmenu", "LayoutUpdated",
                       self.GLib.Variant("(ui)", (self.revision, 0)))

    def _tick(self) -> bool:
        self.refresh()
        return True

    def _emit(self, path, iface, name, params) -> None:
        try:
            self.bus.emit_signal(None, path, iface, name, params)
        except Exception:
            pass

    def _watcher_up(self, *_a) -> None:
        self.bus.call(WATCHER, "/StatusNotifierWatcher", WATCHER, "RegisterStatusNotifierItem",
                      self.GLib.Variant("(s)", (self.name,)), None, self.Gio.DBusCallFlags.NONE, -1, None, None, None)

    # -- the item's properties and clicks -----------------------------------------------------------
    def _item_get(self, conn, sender, path, iface, prop):
        V = self.GLib.Variant
        kind = self.state["state"] if self.state else "off"
        words = {"warm": "Night light: warm", "day": "Night light: daylight", "off": "Night light: off"}[kind]
        icons = [(s, s, picture(kind, s)) for s in (22, 32, 44)]
        return {
            "Category": V("s", "Hardware"), "Id": V("s", "nightforge"), "Title": V("s", words),
            "Status": V("s", "Active"), "WindowId": V("i", 0), "IconName": V("s", ""),
            "IconPixmap": V("a(iiay)", icons), "OverlayIconName": V("s", ""), "AttentionIconName": V("s", ""),
            "ToolTip": V("(sa(iiay)ss)", ("", [], words, self.state["why"] if self.state else "")),
            "ItemIsMenu": V("b", False), "Menu": V("o", MENU_PATH),
        }.get(prop)

    def _item_call(self, conn, sender, path, iface, method, params, invocation):
        if method == "Activate":
            self.open_app()
        invocation.return_value(None)

    # -- the menu ---------------------------------------------------------------------------------------
    def items(self) -> list[tuple[int, dict]]:
        s = self.settings()
        st = self.state or control.status(s)
        m = st["mode"]
        V = self.GLib.Variant
        head = {"warm": "warm", "day": "daylight", "off": "off"}[st["state"]]
        rows = [(1, {"label": V("s", f"Night light · {head}"), "enabled": V("b", False)}),
                (2, {"label": V("s", st["why"]), "enabled": V("b", False)}),
                (3, {"type": V("s", "separator")})]
        if s.enabled:
            for i, (key, label) in enumerate([("auto", "Automatic"), ("warm", "Warm Now"), ("day", "Daylight Now")], 4):
                rows.append((i, {"label": V("s", label), "toggle-type": V("s", "radio"),
                                 "toggle-state": V("i", 1 if m == key else 0)}))
            rows.append((7, {"type": V("s", "separator")}))
        rows.append((8, {"label": V("s", "Turn Off" if s.enabled else "Turn On")}))
        rows.append((9, {"label": V("s", "Open nightForge…")}))
        return rows

    def _layout(self):
        V = self.GLib.Variant
        kids = [V("(ia{sv}av)", (i, props, [])) for i, props in self.items()]
        return (0, {"children-display": V("s", "submenu")}, kids)

    def _menu_get(self, conn, sender, path, iface, prop):
        V = self.GLib.Variant
        return {"Version": V("u", 3), "TextDirection": V("s", "ltr"), "Status": V("s", "normal"),
                "IconThemePath": V("as", [])}.get(prop)

    def _menu_call(self, conn, sender, path, iface, method, params, invocation):
        V = self.GLib.Variant
        if method == "GetLayout":
            invocation.return_value(V("(u(ia{sv}av))", (self.revision, self._layout())))
        elif method == "GetGroupProperties":
            ids = params.unpack()[0]
            rows = [(i, p) for i, p in self.items() if not ids or i in ids]
            invocation.return_value(V("(a(ia{sv}))", (rows,)))
        elif method == "GetProperty":
            i, name = params.unpack()
            props = dict(self.items()).get(i, {})
            invocation.return_value(V("(v)", (props.get(name, V("s", "")),)))
        elif method == "Event":
            i, event, _data, _ts = params.unpack()
            invocation.return_value(None)
            if event == "clicked":
                self.GLib.idle_add(self.clicked, i)
        elif method == "EventGroup":
            events = params.unpack()[0]
            invocation.return_value(V("(ai)", ([],)))
            for i, event, _d, _t in events:
                if event == "clicked":
                    self.GLib.idle_add(self.clicked, i)
        elif method == "AboutToShow":
            invocation.return_value(V("(b)", (True,)))
        elif method == "AboutToShowGroup":
            invocation.return_value(V("(aiai)", ([], [])))
        else:
            invocation.return_value(None)

    def clicked(self, i: int) -> bool:
        s = self.settings()
        try:
            if i in (4, 5, 6):
                control.start(s, {4: "auto", 5: "warm", 6: "day"}[i])
            elif i == 8:
                s.enabled = not s.enabled
                s.save()
                control.start(s, "auto")
            elif i == 9:
                self.open_app()
        except (control.Trouble, OSError) as e:
            self.notify(str(e))
        self.refresh()
        return False

    def open_app(self) -> None:
        """nightForge in its own terminal window (hypeForge floats it, like the other Forge apps)."""
        me = [sys.executable, os.path.abspath(sys.argv[0])] if sys.argv[0].endswith(".py") else [shutil.which("nightforge") or "nightforge"]
        try:
            subprocess.Popen(["alacritty", "--class", "nightforge", "-e", *me], start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            self.notify("Couldn't open a terminal for nightForge (Alacritty isn't installed).")

    def notify(self, text: str) -> None:
        try:
            subprocess.Popen(["notify-send", "-a", "nightForge", "Night light", text],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            pass

    def run(self) -> None:
        self.GLib.MainLoop().run()


def already_running() -> bool:
    try:
        pid = int(PIDFILE.read_text())
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            return b"tray" in f.read()
    except (OSError, ValueError):
        return False


def main() -> int:
    if already_running():
        print("nightforge tray: already running")
        return 0
    control.RUNTIME.mkdir(parents=True, exist_ok=True)
    PIDFILE.write_text(str(os.getpid()))
    try:
        Tray().run()
    finally:
        PIDFILE.unlink(missing_ok=True)
    return 0
