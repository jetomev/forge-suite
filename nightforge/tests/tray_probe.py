"""Run inside `dbus-run-session` (a private, throwaway session bus): plays the bar's tray host,
starts nightForge's tray icon against a stand-in night light and throwaway settings, reads the
icon and its menu, clicks Warm Now and Turn Off, and prints what happened as JSON."""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import gi
gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib  # noqa: E402

HERE = Path(__file__).resolve().parent
tmp = Path(tempfile.mkdtemp())
env = dict(os.environ, NIGHTFORGE_WLSUNSET=str(HERE / "fake-wlsunset"), NIGHTFORGE_FAKE_LOG=str(tmp / "fake.log"),
           XDG_RUNTIME_DIR=str(tmp / "run"), XDG_CONFIG_HOME=str(tmp / "config"), XDG_STATE_HOME=str(tmp / "state"))
(tmp / "run").mkdir(mode=0o700)
for k in ("WAYLAND_DISPLAY", "SWAYSOCK", "DISPLAY"):
    env.pop(k, None)

WATCHER_XML = """<node><interface name="org.kde.StatusNotifierWatcher">
<method name="RegisterStatusNotifierItem"><arg type="s" direction="in"/></method>
<property name="IsStatusNotifierHostRegistered" type="b" access="read"/>
<property name="RegisteredStatusNotifierItems" type="as" access="read"/>
<property name="ProtocolVersion" type="i" access="read"/></interface></node>"""
bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
items = []


def call(conn, sender, path, iface, method, params, inv):
    items.append((params.unpack()[0], sender))
    inv.return_value(None)


import warnings; warnings.simplefilter("ignore", DeprecationWarning)
bus.register_object("/StatusNotifierWatcher", Gio.DBusNodeInfo.new_for_xml(WATCHER_XML).interfaces[0], call,
                    lambda *a: {"IsStatusNotifierHostRegistered": GLib.Variant("b", True),
                                "RegisteredStatusNotifierItems": GLib.Variant("as", []),
                                "ProtocolVersion": GLib.Variant("i", 0)}.get(a[4]), None)
Gio.bus_own_name_on_connection(bus, "org.kde.StatusNotifierWatcher", Gio.BusNameOwnerFlags.NONE, None, None)
ctx = GLib.MainContext.default()

# the night light as at login, then the tray
subprocess.run([sys.executable, str(HERE.parent / "main.py"), "start"], env=env, timeout=20)
tray_pid = int((tmp / "run/nightforge/tray.pid").read_text()) if (tmp / "run/nightforge/tray.pid").exists() else None
deadline = time.monotonic() + 10
while not items and time.monotonic() < deadline:
    ctx.iteration(False)
    time.sleep(0.05)
if not tray_pid:
    deadline = time.monotonic() + 5
    while not (tmp / "run/nightforge/tray.pid").exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    tray_pid = int((tmp / "run/nightforge/tray.pid").read_text())
out = {"registered": bool(items)}
if items:
    name, sender = items[0]
    owner = name if not name.startswith("/") else sender

    def prop(path, iface, p):
        return bus.call_sync(owner, path, "org.freedesktop.DBus.Properties", "Get", GLib.Variant("(ss)", (iface, p)),
                             None, Gio.DBusCallFlags.NONE, 3000, None).unpack()[0]

    out["title"] = prop("/StatusNotifierItem", "org.kde.StatusNotifierItem", "Title")
    pix = prop("/StatusNotifierItem", "org.kde.StatusNotifierItem", "IconPixmap")
    out["pixmaps"] = [(w, h, len(b)) for w, h, b in pix]
    out["menu"] = prop("/StatusNotifierItem", "org.kde.StatusNotifierItem", "Menu")
    layout = bus.call_sync(owner, "/MenuBar", "com.canonical.dbusmenu", "GetLayout",
                           GLib.Variant("(iias)", (0, -1, [])), None, Gio.DBusCallFlags.NONE, 3000, None).unpack()
    out["labels"] = [k[1].get("label", "—") for k in layout[1][2]]

    def click(i):
        bus.call_sync(owner, "/MenuBar", "com.canonical.dbusmenu", "Event",
                      GLib.Variant("(isvu)", (i, "clicked", GLib.Variant("s", ""), 0)), None,
                      Gio.DBusCallFlags.NONE, 3000, None)
        time.sleep(1.5)

    click(5)                                    # Warm Now
    out["after_warm"] = (tmp / "fake.log").read_text().split("\n")
    click(8)                                    # Turn Off
    out["settings_after_off"] = (tmp / "config/nightforge/settings.toml").read_text() if \
        (tmp / "config/nightforge/settings.toml").exists() else ""
    out["title_after_off"] = prop("/StatusNotifierItem", "org.kde.StatusNotifierItem", "Title")
if tray_pid:
    os.kill(tray_pid, 15)
print(json.dumps(out))
