#!/usr/bin/env python3
"""The hidden bench for switching styles under a running bar (F-58, 2026-10-10): the other benches
start the bar fresh; a person switches while it runs. A screen-less Sway, a running Waybar, then
`apply` through every style in turn (with Sway and the bar told to reload, as on the desktop) —
after each switch the bar must still be running.

    switch-bench.py            exit 0 when the bar survives every switch
"""
from __future__ import annotations

import os, signal, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/panels"))
import panelkit  # noqa: E402

ORDER = ["classic", "rice", "windows-11", "mac-os-9", "kde", "cosmic", "macos", "rice", "classic"]


def main() -> int:
    ht = panelkit.theme_tool()
    base = Path(tempfile.mkdtemp(prefix="hfsw.", dir="/tmp"))
    run, conf = base / "r", base / "c"
    run.mkdir(mode=0o700)
    (conf / "hypeforge/applets").mkdir(parents=True)
    (conf / "hypeforge/applets/workspaces.toml").write_text('enabled = true\nscreens = ["HEADLESS-1"]\n[[workspace]]\nname = "Daily"\n')
    place = ht.Place(conf)
    ht.apply(ORDER[0], "kognogos-mocha", place, reload=False, check_names=False, make_wallpaper=False, say=lambda *_: None)
    (base / "sway.conf").write_text("output HEADLESS-1 resolution 1920x1080\nxwayland disable\n")
    env = {k: v for k, v in os.environ.items() if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "DBUS_SESSION_BUS_ADDRESS")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), WLR_BACKENDS="headless", WLR_RENDERER="pixman",
               WLR_HEADLESS_OUTPUTS="1", WLR_LIBINPUT_NO_DEVICES="1")
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"] = bus[0]
    log = open(base / "bench.log", "w")
    results = []
    sway = subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    try:
        time.sleep(2)
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        bar = subprocess.Popen(["waybar", "-c", str(conf / "sway/waybar/config.jsonc"), "-s", str(conf / "sway/waybar/style.css")],
                               env=env, stdout=log, stderr=log)
        time.sleep(3)
        for style in ORDER[1:]:
            ht.apply(style, "kognogos-mocha", place, reload=False, check_names=False, make_wallpaper=False, say=lambda *_: None)
            os.kill(bar.pid, signal.SIGUSR2)          # as the engine's reload does
            time.sleep(0.15)
            os.kill(bar.pid, signal.SIGUSR2)          # and an applet's own, right after (the F-58 case)
            time.sleep(3)
            alive = bar.poll() is None
            results.append(alive)
            print(("  ok    " if alive else "  FAIL  ") + f"→ {style}: the bar is {'still running' if alive else 'GONE'}")
            if not alive:
                break
    finally:
        for p in (locals().get("bar"), sway):
            if p and p.poll() is None:
                p.terminate()
        os.kill(int(bus[1]), signal.SIGTERM)
    print(f"\nRESULT: {sum(results)}/{len(ORDER) - 1} passed" + ("" if all(results) else f"; see {base / 'bench.log'}"))
    return 0 if len(results) == len(ORDER) - 1 and all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
