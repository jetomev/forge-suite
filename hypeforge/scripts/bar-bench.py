#!/usr/bin/env python3
"""The hidden bench for one bar per screen (hypeforge-bar, 2026-10-10; bench before live).

Three screen-less screens, the KDE style applied. Checks: a bar on EVERY screen, each told its own
screen (HYPEFORGE_OUTPUT in its environment — what its clicks inherit) and visible there; a
restart replaces them all; a pop-up opened from screen 3's bar draws on screen 3 only; stop leaves
none; and the REAL desktop's bar is never touched (its process numbers are the same at the end).

    bar-bench.py            exit 0 when every check passes
"""
from __future__ import annotations

import json, os, signal, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/panels"))
import panelkit  # noqa: E402

BAR = HERE / "applets/bar/hypeforge-bar"
MAGENTA = b"\xff\x00\xff"


def main() -> int:
    ht = panelkit.theme_tool()
    real_before = subprocess.run(["pgrep", "-x", "waybar"], capture_output=True, text=True).stdout.split()
    base = Path(tempfile.mkdtemp(prefix="hfbb.", dir="/tmp"))
    run, conf = base / "r", base / "c"
    run.mkdir(mode=0o700)
    (conf / "hypeforge/applets").mkdir(parents=True)
    (conf / "hypeforge/applets/workspaces.toml").write_text(
        'enabled = true\nscreens = ["HEADLESS-1", "HEADLESS-2", "HEADLESS-3"]\n[[workspace]]\nname = "Daily"\n')
    real = Path.home() / ".config"
    for rel in ("hypeforge/applets/sections.toml", "hypeforge/bar/launcher.png"):
        if (real / rel).exists():
            (conf / rel).parent.mkdir(parents=True, exist_ok=True)
            (conf / rel).write_bytes((real / rel).read_bytes())
    place = ht.Place(conf)
    ht.apply("kde", "kognogos-mocha", place, reload=False, check_names=False, make_wallpaper=False, say=lambda *_: None)
    (base / "sway.conf").write_text("output * resolution 1280x720 bg #ff00ff solid_color\nxwayland disable\n")
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "DBUS_SESSION_BUS_ADDRESS", "HYPEFORGE_OUTPUT")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), WLR_BACKENDS="headless", WLR_RENDERER="pixman",
               WLR_HEADLESS_OUTPUTS="3", WLR_LIBINPUT_NO_DEVICES="1", GDK_BACKEND="wayland")
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"] = bus[0]
    fakebin = base / "bin"; fakebin.mkdir()           # redraw signals must never reach the real bar
    for tool in ("pgrep", "pkill"):
        (fakebin / tool).write_text(f'#!/bin/sh\ncase "$*" in *waybar*) exit 1;; esac\nexec /usr/bin/{tool} "$@"\n')
        (fakebin / tool).chmod(0o755)
    env["PATH"] = f"{fakebin}:{os.environ['PATH']}"
    log = open(base / "bench.log", "w")
    results = []

    def check(ok, what):
        results.append(bool(ok))
        print(("  ok    " if ok else "  FAIL  ") + what)

    sway = subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    procs = []
    try:
        time.sleep(2)
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        env["SWAYSOCK"] = next(str(p) for p in run.glob("sway-ipc.*.sock"))
        procs.append(subprocess.Popen([sys.executable, str(HERE / "applets/workspaces/hypeforge-workspaces")],
                                      env=env, stdout=log, stderr=log))
        procs.append(subprocess.Popen([sys.executable, str(HERE / "applets/taskbar/hypeforge-taskbar")],
                                      env=env, stdout=log, stderr=log))
        time.sleep(1.5)
        outs = sorted(json.loads(subprocess.run(["swaymsg", "-t", "get_outputs", "-r"], env=env,
                                                capture_output=True, text=True).stdout), key=lambda o: o["rect"]["x"])

        def shot(o, y=None, h=None):
            r = o["rect"]
            y = r["y"] if y is None else y
            p = base / "s.ppm"
            subprocess.run(["grim", "-t", "ppm", "-g", f"{r['x']},{y} {r['width']}x{h or r['height']}", str(p)],
                           env=env, check=True)
            return p.read_bytes().split(b"\n", 3)[3]

        def bar_seen(o):
            row = shot(o, o["rect"]["y"] + o["rect"]["height"] - 30, 1)
            px = [row[i:i + 3] for i in range(0, len(row), 3)]
            return sum(p != MAGENTA for p in px) > len(px) * 0.5

        def env_of(pid):
            try:
                return dict(x.split("=", 1) for x in Path(f"/proc/{pid}/environ").read_bytes().decode().split("\0") if "=" in x)
            except OSError:
                return {}

        subprocess.run([sys.executable, str(BAR), "start"], env=env, stdout=log, stderr=log)
        time.sleep(4)
        pids = json.loads((run / "hypeforge-bar/pids.json").read_text())
        check(sorted(pids) == [o["name"] for o in sorted(outs, key=lambda o: o["name"])], f"a bar for every screen: {', '.join(sorted(pids))}")
        check(all(env_of(p).get("HYPEFORGE_OUTPUT") == n for n, p in pids.items()), "each bar is told its own screen")
        check(all(bar_seen(o) for o in outs), "each screen shows its bar")
        subprocess.run([sys.executable, str(BAR), "restart"], env=env, stdout=log, stderr=log)
        time.sleep(4)
        again = json.loads((run / "hypeforge-bar/pids.json").read_text())
        gone = not any(Path(f"/proc/{p}").exists() and env_of(p) for p in pids.values())
        check(len(again) == 3 and gone and all(bar_seen(o) for o in outs), "a restart replaces all three, and they show")

        before = [shot(o) for o in outs]
        third = outs[2]["name"]
        panel = subprocess.Popen([sys.executable, str(HERE / "applets/panels/hypeforge-panel"), "workspaces",   # needs no outside service (the calendar waits for one)
                                  "--edges", "bottom,right", "--margin", "bottom=60,right=8"],
                                 env=dict(env, HYPEFORGE_OUTPUT=third), stdout=log, stderr=log)
        procs.append(panel)
        time.sleep(3)
        subprocess.run(["grim", str(base / "with-popup.png")], env=env)
        if panel.poll() is not None:
            print(f"        (the pop-up ended by itself, exit {panel.returncode})")
        changed = [sum(a != b for a, b in zip(x, shot(o))) for x, o in zip(before, outs)]
        check(changed[2] > 10000 and changed[0] < 1000 and changed[1] < 1000,
              f"a pop-up from screen 3's bar draws on screen 3 only (changed bytes: {changed})")
        panel.terminate()

        subprocess.run([sys.executable, str(BAR), "stop"], env=env, stdout=log, stderr=log)
        time.sleep(1)
        check(not any(Path(f"/proc/{p}").exists() and env_of(p) for p in again.values()), "stop leaves no bar")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        subprocess.run([sys.executable, str(BAR), "stop"], env=env, capture_output=True)
        sway.terminate()
        os.kill(int(bus[1]), signal.SIGTERM)
    real_after = subprocess.run(["pgrep", "-x", "waybar"], capture_output=True, text=True).stdout.split()
    check(real_before == real_after, f"the real desktop's bar untouched ({' '.join(real_before) or 'none'})")
    print(f"\nRESULT: {sum(results)}/{len(results)} passed" + ("" if all(results) else f"; see {base / 'bench.log'}"))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
