#!/usr/bin/env python3
"""The hidden bench for the system pieces (2026-10-17; bench before live). Three fake screens on their own
Sway and message bus, the Rice: the sampler runs, the bar is started by hypeforge-bar, then:

  - the sampler writes a reading every two seconds, its history growing
  - the bar's config has all five pieces, each click carrying the bar's pop-up place and its screen
  - the graphics card and temperature pieces answer in Waybar's form
  - a click on screen 3's processor piece opens its pop-up there and nowhere else; the same click closes it
  - another piece's click while one is open swaps them (one system pop-up at a time)
  - the real desktop's bar is untouched

    system-bench.py [--keep]

Writes logs/system-bench-<part>.png (screen 3 with that pop-up open) for a look.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/panels"))
import panelkit  # noqa: E402

BAR = HERE / "applets/bar/hypeforge-bar"
SYSTEM = HERE / "applets/system/hypeforge-system"
PARTS = {"custom/cpu": "cpu", "custom/gpu": "gpu", "custom/temperature": "temp", "custom/memory": "memory", "custom/disk": "disk"}


def main() -> int:
    keep = "--keep" in sys.argv
    ht = panelkit.theme_tool()
    real_bars = subprocess.run(["pgrep", "-x", "waybar"], capture_output=True, text=True).stdout.split()
    base = Path(tempfile.mkdtemp(prefix="hfsys.", dir="/tmp"))
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
    (base / "sway.conf").write_text("output * resolution 1280x720 bg #ff00ff solid_color\nxwayland disable\n")
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "DBUS_SESSION_BUS_ADDRESS", "HYPEFORGE_OUTPUT",
                        "HYPEFORGE_TRAY_SLOTS", "HYPEFORGE_WAYBAR_TRAY")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), XDG_DATA_HOME=str(conf / ".local-data"),
               WLR_BACKENDS="headless", WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="3", WLR_LIBINPUT_NO_DEVICES="1",
               GDK_BACKEND="wayland")
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"] = bus[0]
    fakebin = base / "bin"; fakebin.mkdir()             # redraw signals must never reach the real bar
    for tool in ("pgrep", "pkill"):
        (fakebin / tool).write_text(f'#!/bin/sh\ncase "$*" in *waybar*) exit 1;; esac\nexec /usr/bin/{tool} "$@"\n')
        (fakebin / tool).chmod(0o755)
    env["PATH"] = f"{fakebin}:{os.environ['PATH']}"
    log = open(base / "bench.log", "w")
    results = []

    def check(ok, what):
        results.append(bool(ok))
        print(("  ok    " if ok else "  FAIL  ") + what, flush=True)

    sway = subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    procs = []
    try:
        time.sleep(2)
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        env["SWAYSOCK"] = next(str(p) for p in run.glob("sway-ipc.*.sock"))
        outs = sorted(json.loads(subprocess.run(["swaymsg", "-t", "get_outputs", "-r"], env=env,
                                                capture_output=True, text=True).stdout), key=lambda o: o["rect"]["x"])

        def shot(o, y=None, h=None, path=None):
            r = o["rect"]
            y = r["y"] if y is None else y
            p = path or base / "s.ppm"
            subprocess.run(["grim", "-t", "ppm" if path is None else "png", "-g", f"{r['x']},{y} {r['width']}x{h or r['height']}",
                            str(p)], env=env, check=True)
            return p.read_bytes().split(b"\n", 3)[3] if path is None else None

        def call(*args, timeout=10):
            return subprocess.run(list(args), env=env, capture_output=True, text=True, timeout=timeout)

        procs.append(subprocess.Popen([sys.executable, str(SYSTEM), "run"], env=env, stdout=log, stderr=log))
        time.sleep(5)
        state = json.loads((run / "hypeforge-system/now.json").read_text())
        check(len(state["history"]["cpu"]) >= 2 and state["memory"]["total"] > 0,
              f"the sampler writes readings ({len(state['history']['cpu'])} so far)")
        ht.apply("rice", "kognogos-mocha", place, reload=False, check_names=False, make_wallpaper=False, say=lambda *_: None)
        call(sys.executable, str(BAR), "start", timeout=30)
        time.sleep(4)
        bars = json.loads((run / "hypeforge-bar/config.json").read_text())
        third = outs[2]["name"]
        mine = next(b for b in bars if b["output"] == third)
        check(all(m in mine["modules-right"] for m in PARTS), f"all five pieces on the Rice bar: {[m for m in PARTS if m in mine['modules-right']]}")
        check(all("--edges" in mine[m]["on-click"] and f"HYPEFORGE_OUTPUT={third};" in mine[m]["on-click"] for m in PARTS),
              "each click carries the bar's pop-up place and its screen")
        for part in ("gpu", "temp", "disk"):
            out = call(sys.executable, str(SYSTEM), "bar", part).stdout
            piece = json.loads(out)
            check({"text", "tooltip", "class"} <= set(piece), f"the {part} piece answers in Waybar's form: {piece['text']!r}")
        # below the bar only: the bar's own numbers move every few seconds, on every screen
        below = lambda o: shot(o, o["rect"]["y"] + 70, o["rect"]["height"] - 70)
        before = [below(o) for o in outs]
        procs.append(subprocess.Popen(["sh", "-c", mine["custom/cpu"]["on-click"]], env=env, stdout=log, stderr=log))
        time.sleep(3)
        changed = [sum(a != b for a, b in zip(x, below(o))) for x, o in zip(before, outs)]
        check(changed[2] > 10000 and changed[0] < 1000 and changed[1] < 1000,
              f"screen 3's processor click opens its pop-up on screen 3 only (changed bytes: {changed})")
        pics = HERE / "logs"
        pics.mkdir(exist_ok=True)
        shot(outs[2], path=pics / "system-bench-cpu.png")
        procs.append(subprocess.Popen(["sh", "-c", mine["custom/gpu"]["on-click"]], env=env, stdout=log, stderr=log))
        time.sleep(3)
        pids = sorted(p.name for p in run.glob("hypeforge-panel-system-*.pid"))
        check(pids == ["hypeforge-panel-system-gpu.pid"], f"another piece's click swaps them: {pids}")
        shot(outs[2], path=pics / "system-bench-gpu.png")
        subprocess.run(["sh", "-c", mine["custom/gpu"]["on-click"]], env=env, stdout=log, stderr=log, timeout=10)
        time.sleep(1.5)
        after = sum(a != b for a, b in zip(before[2], below(outs[2])))
        check(after < 1000 and not list(run.glob("hypeforge-panel-system-*.pid")),
              f"the same click again closes it (changed bytes: {after})")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        subprocess.run([sys.executable, str(BAR), "stop"], env=env, capture_output=True)
        sway.terminate()
        os.kill(int(bus[1]), signal.SIGTERM)
    check(subprocess.run(["pgrep", "-x", "waybar"], capture_output=True, text=True).stdout.split() == real_bars,
          f"the real desktop's bar untouched ({' '.join(real_bars) or 'none'})")
    print(f"\nRESULT: {sum(results)}/{len(results)} passed" + ("" if all(results) else f"; see {base / 'bench.log'}"))
    if not keep and all(results):
        import shutil
        shutil.rmtree(base, ignore_errors=True)
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
