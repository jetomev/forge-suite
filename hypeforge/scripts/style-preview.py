#!/usr/bin/env python3
"""See a whole style before it reaches the desktop (look program step 5).

Writes the chosen style + theme with hypeforge-theme into a throwaway config folder (every file:
Sway's look, the bar's layout and stylesheet, colours, notifications…), starts a screen-less Sway
with that look (one fake 2560×1440 screen), runs the Workspaces applet and the bar, opens a few
stand-in windows named like real apps, and photographs the screen. Nothing touches the real desktop.

    style-preview.py [--style rice] [--theme kognogos-mocha] [--out picture.png] [--scale 0.5]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
APPLETS = HERE / "applets"
NAMES = ("Daily", "Work", "Entertainment", "Gaming", "Monitoring", "Settings")


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
    ap.add_argument("--style", default="rice")
    ap.add_argument("--theme", default="kognogos-mocha")
    ap.add_argument("--out")
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--corners", default="style", help="straight, rounded or style (hypeforge-theme corners)")
    a = ap.parse_args()
    out = Path(a.out or HERE / f"logs/style-preview-{a.style}-{a.theme}{'' if a.corners == 'style' else '-' + a.corners}.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    base = Path(tempfile.mkdtemp(prefix="hfsty.", dir="/tmp"))
    run, conf = base / "r", base / "c"
    run.mkdir(mode=0o700)
    (conf / "hypeforge/applets").mkdir(parents=True)
    (conf / "hypeforge/applets/workspaces.toml").write_text(
        'enabled = true\nscreens = ["HEADLESS-1"]\n' + "".join(f'[[workspace]]\nname = "{n}"\n' for n in NAMES))
    real = Path.home() / ".config"
    for rel in ("hypeforge/applets/sections.toml", "hypeforge/bar/launcher.png"):   # read-only copies
        if (real / rel).exists():
            (conf / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(real / rel, conf / rel)
    sys.path.insert(0, str(APPLETS / "panels"))
    import panelkit
    ht = panelkit.theme_tool()
    ht.apply(a.style, a.theme, ht.Place(conf), reload=False, check_names=False, say=lambda *_: None, corners=a.corners)
    (base / "sway.conf").write_text(f"output HEADLESS-1 resolution 2560x1440\nxwayland disable\n"
                                    f"include {conf}/hypeforge/theme/sway.conf\n")
    fakebin = base / "bin"
    fakebin.mkdir()
    (fakebin / "pgrep").write_text('#!/bin/sh\n[ "$1 $2" = "-x waybar" ] && exit 1\nexec /usr/bin/pgrep "$@"\n')
    (fakebin / "pgrep").chmod(0o755)
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK", "DBUS_SESSION_BUS_ADDRESS")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), WLR_BACKENDS="headless", WLR_RENDERER="pixman",
               WLR_HEADLESS_OUTPUTS="1", WLR_LIBINPUT_NO_DEVICES="1", GDK_BACKEND="wayland",
               PATH=f"{fakebin}:{os.environ['PATH']}")
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"], bus_pid = bus[0], int(bus[1])
    procs, log, sock = [], open(base / "preview.log", "w"), None
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
        procs.append(subprocess.Popen([sys.executable, str(APPLETS / "workspaces/hypeforge-workspaces")], env=env, stdout=log, stderr=log))
        time.sleep(1.5)
        window = ("import gi, sys; gi.require_version('Gtk','3.0'); from gi.repository import Gtk, GLib; "
                  "GLib.set_prgname(sys.argv[1]); w=Gtk.Window(); w.add(Gtk.Label(label=sys.argv[1])); w.show_all(); "
                  "GLib.timeout_add_seconds(90, Gtk.main_quit); Gtk.main()")
        for ws, names in ((3, ("spotify",)), (1, ("google-chrome", "thunar"))):
            subprocess.run([sys.executable, str(APPLETS / "workspaces/hypeforge-workspaces"), "go", str(ws)], env=env)
            for n in names:
                procs.append(subprocess.Popen([sys.executable, "-c", window, n], env=env, stdout=log, stderr=log))
                time.sleep(0.8)
        procs.append(subprocess.Popen(["waybar", "-c", str(conf / "sway/waybar/config.jsonc"),
                                       "-s", str(conf / "sway/waybar/style.css")], env=env, stdout=log, stderr=log))
        time.sleep(4)
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
            os.kill(bus_pid, 15)
        except (NameError, OSError):
            pass


if __name__ == "__main__":
    sys.exit(main())
