#!/usr/bin/env python3
"""How fast the bar is (2026-10-17, Javier: "timing and speed is everything, specially considering our UI is
sway... light, not as complicated, everything should render, recover, appear, fast!"). Three hidden screens,
a style's bar, real pieces (the real printer, CUPS; the system readings), then, in milliseconds:

  - every custom piece's command, one run each (the bar waits for them)
  - a cold start: `hypeforge-bar start` until a bar is drawn on every screen
  - a restyle (the look's in-place reload): from the signal until every bar is back

    bar-timing.py [--style rice] [--runs 3] [--keep]

Prints the numbers and writes them to logs/bar-timing-latest.log. A bar is "drawn" when its row on the
screen is no longer the bench's magenta.
"""

from __future__ import annotations

import argparse
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


def bar_tool():
    import importlib.machinery
    import importlib.util
    loader = importlib.machinery.SourceFileLoader("hb_timing", str(BAR))
    spec = importlib.util.spec_from_loader("hb_timing", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


MAGENTA = b"\xff\x00\xff"
START_BUDGET, RESTYLE_BUDGET = 1.0, 0.8        # seconds


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", default="rice")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    ht = panelkit.theme_tool()
    base = Path(tempfile.mkdtemp(prefix="hftime.", dir="/tmp"))
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
    ht.apply(a.style, "kognogos-mocha", ht.Place(conf), reload=False, check_names=False, make_wallpaper=False,
             say=lambda *_: None)
    (base / "sway.conf").write_text("output * resolution 1280x720 bg #ff00ff solid_color\nxwayland disable\n")
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "DBUS_SESSION_BUS_ADDRESS", "HYPEFORGE_OUTPUT")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), XDG_DATA_HOME=str(conf / ".local-data"),
               WLR_BACKENDS="headless", WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="3", WLR_LIBINPUT_NO_DEVICES="1",
               GDK_BACKEND="wayland")
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"] = bus[0]
    fakebin = base / "bin"
    fakebin.mkdir()                                     # redraw signals must never reach the real bar
    for tool in ("pgrep", "pkill"):
        (fakebin / tool).write_text(f'#!/bin/sh\ncase "$*" in *waybar*) exit 1;; esac\nexec /usr/bin/{tool} "$@"\n')
        (fakebin / tool).chmod(0o755)
    env["PATH"] = f"{fakebin}:{os.environ['PATH']}"
    log = open(base / "bench.log", "w")
    report = []

    def say(words: str):
        print(words, flush=True)
        report.append(words)

    sway = subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    procs = []
    try:
        time.sleep(2)
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        env["SWAYSOCK"] = next(str(p) for p in run.glob("sway-ipc.*.sock"))
        procs.append(subprocess.Popen([sys.executable, str(HERE / "applets/system/hypeforge-system"), "run"],
                                      env=env, stdout=log, stderr=log))
        procs.append(subprocess.Popen([sys.executable, str(HERE / "applets/workspaces/hypeforge-workspaces")],
                                      env=env, stdout=log, stderr=log))
        time.sleep(3)
        outs = sorted(json.loads(subprocess.run(["swaymsg", "-t", "get_outputs", "-r"], env=env,
                                                capture_output=True, text=True).stdout), key=lambda o: o["rect"]["x"])
        hb = bar_tool()
        bar = json.loads(hb.strip_comments((conf / "sway/waybar/config.jsonc").read_text()))
        top = (bar[0] if isinstance(bar, list) else bar or {}).get("position", "top") != "bottom"

        def drawn() -> bool:
            for o in outs:
                r = o["rect"]
                y = r["y"] + (20 if top else r["height"] - 20)
                out = subprocess.run(["grim", "-t", "ppm", "-g", f"{r['x']},{y} {r['width']}x1", "-"], env=env,
                                     capture_output=True).stdout.split(b"\n", 3)[3]
                px = [out[i:i + 3] for i in range(0, len(out), 3)]
                if sum(p != MAGENTA for p in px) < len(px) * 0.3:
                    return False
            return True

        def wait(gone_first: bool, limit: float = 15.0) -> float | None:
            t0 = time.perf_counter()
            if gone_first:                              # a restyle: the bars go, then come back
                while drawn() and time.perf_counter() - t0 < 2:
                    time.sleep(0.01)
            while time.perf_counter() - t0 < limit:
                if drawn():
                    return time.perf_counter() - t0
                time.sleep(0.02)
            return None

        say(f"\nThe bar's timing · style {a.style} · three hidden screens\n")
        mods = json.loads(hb.strip_comments((conf / "sway/waybar/modules.jsonc").read_text()))
        rows = []
        for name, m in mods.items():
            if isinstance(m, dict) and m.get("exec") and not name.startswith("image#tray-"):
                t0 = time.perf_counter()
                subprocess.run(["sh", "-c", os.path.expanduser(m["exec"])], env=env, capture_output=True, timeout=30)
                rows.append((time.perf_counter() - t0, name))
        say("  each piece's command:")
        for t, name in sorted(rows, reverse=True):
            say(f"    {t * 1000:6.0f} ms  {name}" + ("   ← slow" if t > 0.2 else ""))

        starts, restyles = [], []
        for i in range(a.runs):
            subprocess.run([sys.executable, str(BAR), "stop"], env=env, capture_output=True)
            time.sleep(1)
            t0 = time.perf_counter()
            subprocess.run([sys.executable, str(BAR), "start"], env=env, stdout=log, stderr=log)
            t = wait(False)
            starts.append(None if t is None else time.perf_counter() - t0)
            time.sleep(2)
            pid = int(json.loads((run / "hypeforge-bar/pids.json").read_text())["pid"])
            os.kill(pid, signal.SIGUSR2)
            restyles.append(wait(True))
            time.sleep(1)
        fmt = lambda xs: " · ".join("—" if x is None else f"{x * 1000:.0f} ms" for x in xs)
        say(f"\n  cold start, until a bar on every screen: {fmt(starts)}")
        say(f"  a restyle, until every bar is back:      {fmt(restyles)}")
        # the budget (2026-10-17: 1.8 s and 1.7 s before; "everything should render, recover, appear, fast!")
        ok = all(x is not None and x < START_BUDGET for x in starts) and all(x is not None and x < RESTYLE_BUDGET for x in restyles)
        say(f"\n  budget: a start under {START_BUDGET * 1000:.0f} ms, a restyle under {RESTYLE_BUDGET * 1000:.0f} ms — {'OK' if ok else 'FAIL'}")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        subprocess.run([sys.executable, str(BAR), "stop"], env=env, capture_output=True)
        sway.terminate()
        os.kill(int(bus[1]), signal.SIGTERM)
    logs = HERE / "logs"
    logs.mkdir(exist_ok=True)
    (logs / "bar-timing-latest.log").write_text("\n".join(report) + "\n")
    if not a.keep:
        import shutil
        shutil.rmtree(base, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
