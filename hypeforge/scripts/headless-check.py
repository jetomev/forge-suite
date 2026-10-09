#!/usr/bin/env python3
"""A hidden test bench for the Workspaces + Placement applets (F-50, #55; the 2026-10-09 loop).

Starts a screen-less Sway (wlroots' headless backend, three fake screens) with its own runtime
folder and its own copies of the applets' settings, runs the applets from this repository against
it, opens a test window the way a program started from a terminal would, and counts how often the
workspaces switch afterwards. Nothing touches the real desktop: not its Sway, its bar, its applets
or its settings.

    headless-check.py            the F-50 case: a listed app opened on another workspace
    headless-check.py --keep     leave the bench's folder for a look afterwards

Exit 0 when the screens settle on the app's workspace with its window there; 1 otherwise.
Javier, 2026-10-09: a window started from a terminal (`supertux2 &`) set the workspaces switching
non-stop; the desktop could only be left through a text console. This bench reproduces that kind
of fault before it can reach the desktop again.
"""

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
APPLETS = HERE / "applets"
sys.path.insert(0, str(APPLETS / "common"))
from hfsway import GET_TREE, GET_WORKSPACES, SUBSCRIBE, EVENT_WORKSPACE  # noqa: E402

SCREENS = ["HEADLESS-1", "HEADLESS-2", "HEADLESS-3"]
QUIET = 31          # the applet keeps still for 30 s after Sway starts (just_logged_in)
WATCH = 10          # seconds of switching counted after the window opens
TOO_MANY = 30       # more workspace changes than this in WATCH seconds = a loop

WORKSPACES_TOML = f'''
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
apps = ["fakegame"]
[share]
'''

WINDOW = r'''
import gi, sys
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk
GLib.set_prgname("fakegame")          # the Wayland app_id
w = Gtk.Window(title="fake game")
w.connect("destroy", Gtk.main_quit)
w.show_all()
GLib.timeout_add_seconds(int(sys.argv[1]), Gtk.main_quit)
Gtk.main()
'''


class IPC:
    """A tiny i3-IPC client on a given socket (the bench's, never the desktop's)."""

    def __init__(self, path):
        import socket
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.s.connect(path)

    def _read(self, n):
        b = b""
        while len(b) < n:
            c = self.s.recv(n - len(b))
            if not c:
                raise ConnectionError
            b += c
        return b

    def ask(self, kind, payload=""):
        import struct
        body = payload.encode()
        self.s.sendall(b"i3-ipc" + struct.pack("=II", len(body), kind) + body)
        return self.receive()[1]

    def receive(self):
        import struct
        h = self._read(14)
        n, kind = struct.unpack("=II", h[6:])
        return kind, json.loads(self._read(n))


def main():
    keep = "--keep" in sys.argv
    base = Path(tempfile.mkdtemp(prefix="hf-bench-"))
    run = base / "run"
    run.mkdir(mode=0o700)
    conf = base / "config"
    (conf / "hypeforge/applets").mkdir(parents=True)
    (conf / "hypeforge/applets/workspaces.toml").write_text(WORKSPACES_TOML)
    placement = (APPLETS / "placement/placement.toml").read_text()
    for real, fake in zip(["DP-3", "DP-2", "DP-1"], SCREENS):
        placement = placement.replace(f'"{real}"', f'"{fake}"')
    (conf / "hypeforge/applets/placement.toml").write_text(placement)
    swaycfg = base / "sway.conf"
    swaycfg.write_text("".join(f"output {s} resolution 1280x720 position {i * 1280} 0\n"
                               for i, s in enumerate(SCREENS)))
    fakebin = base / "bin"
    fakebin.mkdir()
    (fakebin / "pgrep").write_text('#!/bin/sh\n[ "$1 $2" = "-x waybar" ] && exit 1\nexec /usr/bin/pgrep "$@"\n')
    (fakebin / "pgrep").chmod(0o755)

    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), WLR_BACKENDS="headless",
               WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="3", WLR_LIBINPUT_NO_DEVICES="1",
               PATH=f"{fakebin}:{os.environ['PATH']}")
    procs = []
    log = open(base / "bench.log", "w")
    try:
        sway = subprocess.Popen(["sway", "--unsupported-gpu", "-c", str(swaycfg)], env=env,
                                stdout=log, stderr=log)
        procs.append(sway)
        sock = None
        for _ in range(100):
            found = list(run.glob("sway-ipc.*.sock"))
            if found:
                sock = str(found[0])
                break
            time.sleep(0.1)
        if not sock:
            print("the bench's Sway did not start; see", base / "bench.log")
            return 1
        env["SWAYSOCK"] = sock
        env["WAYLAND_DISPLAY"] = next((p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock")), "wayland-1")
        ipc = IPC(sock)
        outs = [o["name"] for o in ipc.ask(3)]  # GET_OUTPUTS
        if sorted(outs) != sorted(SCREENS):
            print("the bench's screens are", outs, "— expected", SCREENS)
            return 1
        for applet in ("workspaces/hypeforge-workspaces", "placement/hypeforge-placement"):
            procs.append(subprocess.Popen([sys.executable, str(APPLETS / applet)], env=env, stdout=log, stderr=log))
        print(f"bench up: 3 fake screens; waiting {QUIET} s (the applet keeps still right after login)")
        time.sleep(QUIET)
        # Like a terminal on the left screen of Daily: that screen has the keyboard
        ipc.ask(0, f"focus output {SCREENS[1]}")
        events = IPC(sock)
        events.ask(SUBSCRIBE, json.dumps(["workspace"]))
        events.s.settimeout(0.2)
        procs.append(subprocess.Popen([sys.executable, "-c", WINDOW, str(WATCH + 5)],
                                      env={**env, "GDK_BACKEND": "wayland"}, stdout=log, stderr=log))
        switches, start = 0, time.monotonic()
        while time.monotonic() - start < WATCH:
            try:
                kind, ev = events.receive()
            except (TimeoutError, OSError):
                continue
            if kind == EVENT_WORKSPACE and ev.get("change") == "focus":
                switches += 1
            if switches > TOO_MANY * 10:
                break
        shown = sorted(w["name"] for w in ipc.ask(GET_WORKSPACES) if w["visible"])

        def where(node, ws=None):
            if node.get("type") == "workspace":
                ws = node["name"]
            if node.get("app_id") == "fakegame":
                return ws
            for c in node.get("nodes", []) + node.get("floating_nodes", []):
                hit = where(c, ws)
                if hit:
                    return hit
            return None

        home = where(ipc.ask(GET_TREE))
        alive = all(p.poll() is None for p in procs[1:3])
        print(f"workspace switches in {WATCH} s: {switches}")
        print(f"screens now: {shown}")
        print(f"the window is on: {home}")
        print(f"applets still running: {alive}")
        ok = (switches <= TOO_MANY and home in ("4:Gaming", "14:Gaming", "24:Gaming")
              and shown == ["14:Gaming", "24:Gaming", "4:Gaming"] and alive)
        print("RESULT:", "OK — the screens settled on Gaming with the window there" if ok else "FAILED")
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
        if keep:
            print("bench folder kept:", base)
        else:
            shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
