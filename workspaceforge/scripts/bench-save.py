#!/usr/bin/env python3
"""workspaceForge's save, on a hidden bench before it ever touches the desktop (hypeForge F-51 rule).

Starts a screen-less Sway with three fake screens (its own runtime folder and settings; the real
desktop, bar and applets are never touched), runs hypeForge's Workspaces applet from the repository
against it, opens test windows on four workspaces, then saves through workspaceForge's own Session
and Live: a rename, a swap of two workspaces and a delete whose windows go to another workspace.
Afterwards every window must be on the workspace it belongs to, the applet still running, and the
workspaces must not keep switching.

    python3 scripts/bench-save.py            exit 0 = all good
"""

import json
import os
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPLET = ROOT.parent / "hypeforge/applets/workspaces/hypeforge-workspaces"
SCREENS = ["HEADLESS-1", "HEADLESS-2", "HEADLESS-3"]

FILE = f'''
enabled = true
screens = {json.dumps(SCREENS)}
[[workspace]]
name = "Daily"
[[workspace]]
name = "Work"
[[workspace]]
name = "Entertainment"
[[workspace]]
name = "Gaming"
[share]
'''

WINDOW = r'''
import gi, sys
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk
GLib.set_prgname(sys.argv[1])
w = Gtk.Window(title=sys.argv[1]); w.show_all()
GLib.timeout_add_seconds(60, Gtk.main_quit); Gtk.main()
'''


def ipc(sock, kind, payload=""):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(sock)
    body = payload.encode()
    s.sendall(b"i3-ipc" + struct.pack("=II", len(body), kind) + body)

    def read(n):
        b = b""
        while len(b) < n:
            b += s.recv(n - len(b))
        return b
    n, _ = struct.unpack("=II", read(14)[6:])
    out = json.loads(read(n))
    s.close()
    return out


def where(sock):
    found = {}

    def walk(node, ws=None):
        if node.get("type") == "workspace":
            ws = node["name"]
        if node.get("app_id", "").startswith("win-"):
            found[node["app_id"]] = ws
        for c in node.get("nodes", []) + node.get("floating_nodes", []):
            walk(c, ws)
    walk(ipc(sock, 4))
    return found


def main():
    base = Path(tempfile.mkdtemp(prefix="wf-bench-"))
    run = base / "run"
    run.mkdir(mode=0o700)
    conf = base / "config"
    (conf / "hypeforge/applets").mkdir(parents=True)
    cfgfile = conf / "hypeforge/applets/workspaces.toml"
    cfgfile.write_text(FILE)
    (base / "sway.conf").write_text("".join(f"output {s} resolution 1280x720 position {i * 1280} 0\n"
                                            for i, s in enumerate(SCREENS)))
    fakebin = base / "bin"
    fakebin.mkdir()
    (fakebin / "pgrep").write_text('#!/bin/sh\n[ "$1 $2" = "-x waybar" ] && exit 1\nexec /usr/bin/pgrep "$@"\n')
    (fakebin / "pgrep").chmod(0o755)
    env = {k: v for k, v in os.environ.items() if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), WLR_BACKENDS="headless",
               WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="3", WLR_LIBINPUT_NO_DEVICES="1",
               PATH=f"{fakebin}:{os.environ['PATH']}")
    procs, log = [], open(base / "bench.log", "w")
    ok = False
    try:
        procs.append(subprocess.Popen(["sway", "--unsupported-gpu", "-c", str(base / "sway.conf")], env=env,
                                      stdout=log, stderr=log))
        sock = None
        for _ in range(100):
            found = list(run.glob("sway-ipc.*.sock"))
            if found:
                sock = str(found[0])
                break
            time.sleep(0.1)
        if not sock:
            print("the bench's Sway did not start")
            return 1
        env["SWAYSOCK"] = sock
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        procs.append(subprocess.Popen([sys.executable, str(APPLET)], env=env, stdout=log, stderr=log))
        time.sleep(2)
        # one window on the main screen of each workspace, and one on Work's left screen
        homes = {"win-daily": "1:Daily", "win-work": "2:Work", "win-work-left": "12:Work",
                 "win-ent": "3:Entertainment", "win-game": "4:Gaming"}
        for app_id in homes:
            procs.append(subprocess.Popen([sys.executable, "-c", WINDOW, app_id], env={**env, "GDK_BACKEND": "wayland"},
                                          stdout=log, stderr=log))
        time.sleep(3)
        for app_id, ws in homes.items():
            ipc(sock, 0, f'[app_id="^{app_id}$"] move container to workspace "{ws}"')
        time.sleep(1)
        before = where(sock)
        print("before:", before)
        if before != homes:
            print("the test windows did not land where they should; see", base / "bench.log")
            return 1

        # workspaceForge's own save, pointed at the bench
        os.environ.update(SWAYSOCK=sock, XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf))
        sys.path.insert(0, str(ROOT))
        from workspaceforge import model as M
        from workspaceforge.live import Live
        M.BACKUPS = base / "backups"
        se = M.Session.load(cfgfile)
        uid = {w.name: w.uid for w in se.pending.workspaces}
        se.rename(uid["Daily"], "Home")                    # a rename
        se.move(uid["Gaming"], -1)                         # Gaming and Entertainment swap: 3 ⇄ 4
        se.delete(uid["Work"], move_to=uid["Gaming"])      # Work's windows go to Gaming
        live = Live(pidfile=run / "hypeforge-workspaces.pid")
        results = live.run([c for c, _ in se.window_moves()])
        se.write()
        reloaded = live.reload_applet()
        time.sleep(3)
        after = where(sock)
        expect = {"win-daily": "1:Home", "win-work": "2:Gaming", "win-work-left": "12:Gaming",
                  "win-ent": "3:Entertainment", "win-game": "2:Gaming"}
        print("moves:", sum(results), "of", len(results), "worked (renames of empty workspaces may not)")
        print("after: ", after)
        # no switching after the dust settles
        a = ipc(sock, 1)
        time.sleep(3)
        b = ipc(sock, 1)
        still = [w["name"] for w in a if w["visible"]] == [w["name"] for w in b if w["visible"]]
        alive = procs[1].poll() is None
        print("applet reloaded:", reloaded, "| still running:", alive, "| screens steady:", still)
        ok = after == expect and alive and still and reloaded
        print("RESULT:", "OK — every window followed its workspace" if ok else f"FAILED (expected {expect})")
        return 0 if ok else 1
    finally:
        for p in reversed(procs):
            if p.poll() is None:
                p.send_signal(signal.SIGTERM)
        for p in procs:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
        log.close()
        if ok:
            shutil.rmtree(base, ignore_errors=True)
        else:
            print("bench folder kept:", base)


if __name__ == "__main__":
    sys.exit(main())
