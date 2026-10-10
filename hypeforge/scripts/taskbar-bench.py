#!/usr/bin/env python3
"""The hidden bench for the Taskbar applet (bench before live, F-51): it runs all the time on a
style that shows pinned + running apps, so it must keep up with a burst of windows without
running hot or falling over. A screen-less Sway, the real applet, 30 windows opened and closed in
quick succession; then: is it alive, how much processor time did it take, does its row match.

    taskbar-bench.py            exit 0 when every check passes
"""
from __future__ import annotations

import json, os, socket, struct, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
APPLETS = HERE / "applets"
WINDOWS = 30


def ask(sock, kind, payload=""):
    with socket.socket(socket.AF_UNIX) as s:
        s.connect(sock)
        data = payload.encode()
        s.sendall(b"i3-ipc" + struct.pack("=II", len(data), kind) + data)
        head = s.recv(14, socket.MSG_WAITALL)
        size, _ = struct.unpack("=II", head[6:])
        return json.loads(s.recv(size, socket.MSG_WAITALL))


def cpu_seconds(pid):
    f = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    return (int(f[11]) + int(f[12])) / os.sysconf("SC_CLK_TCK")


def main() -> int:
    base = Path(tempfile.mkdtemp(prefix="hftb.", dir="/tmp"))
    run, conf = base / "r", base / "c"
    run.mkdir(mode=0o700)
    (conf / "hypeforge/applets").mkdir(parents=True)
    (conf / "hypeforge/applets/sections.toml").write_text('favourites = ["thunar", "google-chrome", "steam"]\n')
    (base / "sway.conf").write_text("output HEADLESS-1 resolution 1920x1080\nxwayland disable\n")
    fakebin = base / "bin"; fakebin.mkdir()
    (fakebin / "pgrep").write_text('#!/bin/sh\n[ "$1 $2" = "-x waybar" ] && exit 1\nexec /usr/bin/pgrep "$@"\n')
    (fakebin / "pgrep").chmod(0o755)
    env = {k: v for k, v in os.environ.items() if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), WLR_BACKENDS="headless", WLR_RENDERER="pixman",
               WLR_HEADLESS_OUTPUTS="1", WLR_LIBINPUT_NO_DEVICES="1", GDK_BACKEND="wayland", PATH=f"{fakebin}:{os.environ['PATH']}")
    log = open(base / "bench.log", "w")
    procs, sock, results = [], None, []
    check = lambda ok, what: (results.append(ok), print(("  ok    " if ok else "  FAIL  ") + what))
    try:
        procs.append(subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log))
        for _ in range(100):
            found = list(run.glob("sway-ipc.*.sock"))
            if found:
                sock = str(found[0]); break
            time.sleep(0.1)
        env["SWAYSOCK"] = sock
        env["WAYLAND_DISPLAY"] = next((p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock")), "wayland-1")
        tb = subprocess.Popen([sys.executable, str(APPLETS / "taskbar/hypeforge-taskbar")], env=env, stdout=log, stderr=log)
        procs.append(tb)
        time.sleep(2)
        start = cpu_seconds(tb.pid)
        window = ("import gi, sys; gi.require_version('Gtk','3.0'); from gi.repository import Gtk, GLib; "
                  "GLib.set_prgname(sys.argv[1]); w=Gtk.Window(); w.show_all(); GLib.timeout_add(int(sys.argv[2]), Gtk.main_quit); Gtk.main()")
        names = ["thunar", "google-chrome", "gimp", "mystery-tool", "steam"]
        t0 = time.monotonic()
        burst = [subprocess.Popen([sys.executable, "-c", window, names[i % len(names)], str(1500 + 60 * i)],
                                  env=env, stdout=log, stderr=log) for i in range(WINDOWS)]
        busiest = 0
        while any(p.poll() is None for p in burst):      # watch the row while the windows come and go
            try:
                row = json.loads((run / "hypeforge-taskbar/row.json").read_text())
                busiest = max(busiest, sum(1 for it in row.values() if it["windows"]))
                windows = sum(len(it["windows"]) for it in row.values())
            except (OSError, ValueError):
                pass
            time.sleep(0.1)
        check(busiest >= 4, f"the windows really appeared: at the busiest {busiest} apps showed as running (the bench's setup took effect)")
        time.sleep(2)
        used = cpu_seconds(tb.pid) - start
        check(tb.poll() is None, f"the applet is still running after {WINDOWS} windows opened and closed in {time.monotonic() - t0:.0f} s")
        check(used < 6.0, f"it took {used:.1f} s of processor time for {WINDOWS * 2}+ window events (limit 6 s)")
        idle0 = cpu_seconds(tb.pid); time.sleep(3); idle = cpu_seconds(tb.pid) - idle0
        check(idle < 0.1, f"at rest it uses nothing ({idle:.2f} s in 3 s)")
        row = json.loads((run / "hypeforge-taskbar/row.json").read_text())
        running = [s for s, it in row.items() if it["windows"]]
        check(not running, f"with every window closed no app shows as running ({running or 'none'})")
        pins = [row[s]["id"] for s in sorted(row) if s.startswith("pin-")]
        check(pins == ["thunar", "google-chrome", "steam"], f"the pinned apps stay, in order ({pins})")
    finally:
        try:
            ask(sock, 0, "exit") if sock else None
        except Exception:
            pass
        for p in procs:
            p.terminate()
    print(f"\nRESULT: {sum(results)}/{len(results)} passed")
    return 0 if all(results) and results else 1


if __name__ == "__main__":
    sys.exit(main())
