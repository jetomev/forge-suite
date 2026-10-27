#!/usr/bin/env python3
"""See a pop-up panel before it reaches the desktop (look program step 4).

Starts a screen-less Sway (one fake 2560×1440 screen, its own runtime and config folders, a copy
of the launcher's settings), puts a window and the theme's colour behind, opens
`hypeforge-panel <view>` in the chosen style + theme, and photographs the screen. Nothing touches
the real desktop.

    panel-preview.py <view> [--style rice] [--theme kognogos-mocha] [--out picture.png] [--keys …]

--keys sends key presses to the panel before the picture (e.g. Right Return), through the hidden
seat, to show a state such as the power menu asking "Restart?".
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import struct
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
APPLETS = HERE / "applets"


def ask(sock, kind, payload=""):
    with socket.socket(socket.AF_UNIX) as s:
        s.connect(sock)
        data = payload.encode()
        s.sendall(b"i3-ipc" + struct.pack("=II", len(data), kind) + data)
        head = s.recv(14, socket.MSG_WAITALL)
        size, _ = struct.unpack("=II", head[6:])
        return json.loads(s.recv(size, socket.MSG_WAITALL))


def panelkit_icons(theme: str) -> str:
    """The colour theme's icon set, the way the look tool names it."""
    sys.path.insert(0, str(HERE / "applets/panels"))
    import panelkit
    ht = panelkit.theme_tool()
    return ht.names_for(ht.themes()[theme], check=False)["icons"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("view")
    ap.add_argument("--style", default="rice")
    ap.add_argument("--theme", default="kognogos-mocha")
    ap.add_argument("--out")
    ap.add_argument("--scale", type=float, default=0.5, help="the picture's size against the screen")
    ap.add_argument("--panel-args", default="", help="more options for the panel, as a bar gives them "
                    "(e.g. \"--only sound --edges top,right --margin top=44,right=8\")")
    ap.add_argument("--notes", action="store_true", help="send three sample notifications first")
    ap.add_argument("--system", action="store_true", help="system: this computer's readings with three made-up minutes behind them")
    ap.add_argument("--click", action="append", default=[], metavar="X,Y[,S]",
                    help="a real left click there once the panel is up (repeat it: each click gets its own picture, "
                         "<out>-1.png, -2.png …; e.g. a Quick Settings tile's › then the page's ‹)")
    ap.add_argument("--tray", action="store_true", help="traymenu: hypeForge's tray and a stand-in tray app (Dropbox's menu shape) first")
    a = ap.parse_args()
    out = Path(a.out or HERE / f"logs/panel-preview-{a.view}-{a.style}-{a.theme}.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    base = Path(tempfile.mkdtemp(prefix="hfpan.", dir="/tmp"))
    run, conf = base / "r", base / "c"
    run.mkdir(mode=0o700)
    (conf / "hypeforge/applets").mkdir(parents=True)
    (conf / "hypeforge/applets/workspaces.toml").write_text(
        'enabled = true\nscreens = ["HEADLESS-1"]\n' + "".join(f'[[workspace]]\nname = "{n}"\n' for n in
        ("Daily", "Work", "Entertainment", "Gaming", "Monitoring", "Settings")))
    real = Path.home() / ".config/hypeforge/applets/sections.toml"      # read only: groups, power
    if real.exists():
        (conf / "hypeforge/applets/sections.toml").write_text(real.read_text())
    sys.path.insert(0, str(APPLETS / "panels"))
    import panelkit
    ht = panelkit.theme_tool()
    theme = ht.themes()[a.theme]
    wall = ht.token(theme, "surface.sunken")
    (base / "sway.conf").write_text(f"output HEADLESS-1 resolution 2560x1440 bg {wall} solid_color\n"
                                    "xwayland disable\ndefault_border pixel 2\ngaps inner 10\n")
    # the real bar is never signalled (its pgrep finds no waybar), and the bench has its own message
    # bus, so a sample notification or a mode switch never reaches the desktop's
    fakebin = base / "bin"
    fakebin.mkdir()
    (fakebin / "pgrep").write_text('#!/bin/sh\n[ "$1 $2" = "-x waybar" ] && exit 1\nexec /usr/bin/pgrep "$@"\n')
    (fakebin / "pgrep").chmod(0o755)
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK", "DBUS_SESSION_BUS_ADDRESS")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), XDG_DATA_HOME=str(conf / ".local-data"), WLR_BACKENDS="headless",
               WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="1", WLR_LIBINPUT_NO_DEVICES="1", GDK_BACKEND="wayland",
               PATH=f"{fakebin}:{os.environ['PATH']}",
               XDG_CACHE_HOME=str(conf / ".cache"), XDG_STATE_HOME=str(conf / ".state"))
    # the clipboard: made-up copies in the preview's own history — never the person's (F-80, 2026-10-20)
    for sample in ("https://kognogos.org", "Meeting moved to 3 pm", "sudo nog update",
                   "The quick brown fox jumps over the lazy dog"):
        subprocess.run(["cliphist", "store"], input=sample.encode(), env=env)
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"], bus_pid = bus[0], int(bus[1])
    # the look's icon set, as on the desktop: GTK on Wayland asks GSettings, and this bus's dconf writes into the
    # preview's own config folder, never the person's (2026-10-27: stock icons showed as blank pages)
    subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme",
                    panelkit_icons(a.theme)], env=env, capture_output=True)
    procs, log = [], open(base / "preview.log", "w")
    sock = None
    try:
        procs.append(subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log))
        for _ in range(100):
            found = list(run.glob("sway-ipc.*.sock"))
            if found:
                sock = str(found[0]); break
            time.sleep(0.1)
        if not sock:
            print("the preview's Sway did not start; see", base / "preview.log"); return 1
        env["SWAYSOCK"] = sock
        env["WAYLAND_DISPLAY"] = next((p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock")), "wayland-1")
        window = ("import gi; gi.require_version('Gtk','3.0'); from gi.repository import Gtk, GLib; "
                  "w=Gtk.Window(); w.add(Gtk.Label(label='a window behind the panel')); w.show_all(); "
                  "GLib.timeout_add_seconds(60, Gtk.main_quit); Gtk.main()")
        procs.append(subprocess.Popen([sys.executable, "-c", window], env=env, stdout=log, stderr=log))
        time.sleep(1.5)
        if a.view == "workspaces":   # the Workspaces applet, and stand-in windows of real apps on 1 and 4
            procs.append(subprocess.Popen([sys.executable, str(APPLETS / "workspaces/hypeforge-workspaces")],
                                          env=env, stdout=log, stderr=log))
            time.sleep(1.5)
            named = ("import gi, sys; gi.require_version('Gtk','3.0'); from gi.repository import Gtk, GLib; "
                     "GLib.set_prgname(sys.argv[1]); w=Gtk.Window(); w.show_all(); "
                     "GLib.timeout_add_seconds(60, Gtk.main_quit); Gtk.main()")
            for ws, apps in ((1, ("google-chrome", "thunar")), (4, ("steam",)), (1, ("discord",))):
                subprocess.run([sys.executable, str(APPLETS / "workspaces/hypeforge-workspaces"), "go", str(ws)], env=env)
                for app in apps:
                    procs.append(subprocess.Popen([sys.executable, "-c", named, app], env=env, stdout=log, stderr=log))
                    time.sleep(0.8)
        if a.notes:   # sample notifications through the bench's own mako
            procs.append(subprocess.Popen(["mako"], env=env, stdout=log, stderr=log))
            time.sleep(1)
            for app, summary, body in (("nog", "12 updates ready", "Tier 1 now; Tier 3 after its 7-day hold"),
                                       ("Steam", "Download finished", "SuperTux is ready to play"),
                                       ("nightForge", "Warm from 18:59", "4500 K until 07:02")):
                subprocess.run(["notify-send", "-a", app, summary, body], env=env)
            subprocess.run(["makoctl", "dismiss", "--all"], env=env)   # into the history, as after a while
        if a.system:  # the graphs' past, in the bench's own runtime folder
            subprocess.run([sys.executable, str(HERE / "scripts/fake-system-history.py")], env=env, stdout=log, stderr=log)
        if a.tray:    # the tray (the watcher) on the bench's own bus, then a stand-in app that registers with it
            procs.append(subprocess.Popen([sys.executable, str(APPLETS / "tray/hypeforge-tray"), "run"], env=env, stdout=log, stderr=log))
            time.sleep(1)
            procs.append(subprocess.Popen([sys.executable, str(HERE / "scripts/fake-tray-app.py")], env=env, stdout=log, stderr=log))
            time.sleep(2.5)
        procs.append(subprocess.Popen([sys.executable, str(APPLETS / "panels/hypeforge-panel"), a.view,
                                       "--style", a.style, "--theme", a.theme, *shlex.split(a.panel_args)],
                                      env=env, stdout=log, stderr=log))
        time.sleep(8 if a.view == "quick" else 5 if a.view in ("start", "kickoff", "library") else 3)   # quick asks nmcli, bluetoothctl…
        shot = base / "shot.png"
        for n, spot in enumerate(a.click, 1):     # the hidden Sway has no mouse: fake-pointer.py is one
            x, y, *wait = spot.split(",")              # a third number: seconds to wait before the picture
            subprocess.run([sys.executable, str(HERE / "scripts/fake-pointer.py"), x, y, "--click", "--hold", "0.3"],
                           env=env, stdout=log, stderr=log, timeout=30)
            time.sleep(float(wait[0]) if wait else 1.5)
            subprocess.run(["grim", "-s", str(a.scale), str(shot)], env=env, check=True)
            step = out.with_name(f"{out.stem}-{n}{out.suffix}")
            step.write_bytes(shot.read_bytes())
            print(step)
        subprocess.run(["grim", "-s", str(a.scale), str(shot)], env=env, check=True)
        out.write_bytes(shot.read_bytes())
        print(out)
        return 0
    finally:
        try:
            ask(sock, 0, "exit") if sock else None
        except Exception:
            pass
        for p in reversed(procs):
            p.terminate()
        for p in procs:
            try:
                p.wait(5)
            except subprocess.TimeoutExpired:
                p.kill()
        try:
            os.kill(bus_pid, 15)   # the bench's own message bus, by the number it gave us
        except (NameError, OSError):
            pass


if __name__ == "__main__":
    sys.exit(main())
