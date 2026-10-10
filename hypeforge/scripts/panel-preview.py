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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("view")
    ap.add_argument("--style", default="rice")
    ap.add_argument("--theme", default="kognogos-mocha")
    ap.add_argument("--out")
    ap.add_argument("--scale", type=float, default=0.5, help="the picture's size against the screen")
    ap.add_argument("--notes", action="store_true", help="send three sample notifications first")
    a = ap.parse_args()
    out = Path(a.out or HERE / f"logs/panel-preview-{a.view}-{a.style}-{a.theme}.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    base = Path(tempfile.mkdtemp(prefix="hfpan.", dir="/tmp"))
    run, conf = base / "r", base / "c"
    run.mkdir(mode=0o700)
    (conf / "hypeforge/applets").mkdir(parents=True)
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
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), WLR_BACKENDS="headless",
               WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="1", WLR_LIBINPUT_NO_DEVICES="1", GDK_BACKEND="wayland",
               PATH=f"{fakebin}:{os.environ['PATH']}")
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"], bus_pid = bus[0], int(bus[1])
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
        if a.notes:   # sample notifications through the bench's own mako
            procs.append(subprocess.Popen(["mako"], env=env, stdout=log, stderr=log))
            time.sleep(1)
            for app, summary, body in (("nog", "12 updates ready", "Tier 1 now; Tier 3 after its 7-day hold"),
                                       ("Steam", "Download finished", "SuperTux is ready to play"),
                                       ("nightForge", "Warm from 18:59", "4500 K until 07:02")):
                subprocess.run(["notify-send", "-a", app, summary, body], env=env)
            subprocess.run(["makoctl", "dismiss", "--all"], env=env)   # into the history, as after a while
        procs.append(subprocess.Popen([sys.executable, str(APPLETS / "panels/hypeforge-panel"), a.view,
                                       "--style", a.style, "--theme", a.theme], env=env, stdout=log, stderr=log))
        time.sleep(3 if a.view != "start" else 5)
        shot = base / "shot.png"
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
