#!/usr/bin/env python3
"""The hidden bench for switching styles under a running bar (F-58, 2026-10-10): the other benches
start the bar fresh; a person switches while it runs. A screen-less Sway, a running Waybar, then
`apply` through every style in turn (with Sway and the bar told to reload, as on the desktop) —
after each switch the bar must still be running.

    switch-bench.py            exit 0 when the bar survives every switch
"""
from __future__ import annotations

import json, os, signal, subprocess, sys, tempfile, time
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
    (conf / "hypeforge/applets/workspaces.toml").write_text('enabled = true\nscreens = ["HEADLESS-1", "HEADLESS-2", "HEADLESS-3"]\n[[workspace]]\nname = "Daily"\n')
    place = ht.Place(conf)
    ht.apply(ORDER[0], "kognogos-mocha", place, reload=False, check_names=False, make_wallpaper=False, say=lambda *_: None)
    # a magenta background: any bar pixel is easy to tell from it
    (base / "sway.conf").write_text("output * resolution 1920x1080 bg #ff00ff solid_color\nxwayland disable\n")
    env = {k: v for k, v in os.environ.items() if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "DBUS_SESSION_BUS_ADDRESS")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), WLR_BACKENDS="headless", WLR_RENDERER="pixman",
               WLR_HEADLESS_OUTPUTS=os.environ.get("BENCH_SCREENS", "3"), WLR_LIBINPUT_NO_DEVICES="1")
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"] = bus[0]
    log = open(base / "bench.log", "w")
    results = []
    sway = subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    try:
        time.sleep(2)
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        env["SWAYSOCK"] = next(str(p) for p in run.glob("sway-ipc.*.sock"))
        fakebin = base / "bin"; fakebin.mkdir()      # its redraws must never reach the real bar
        (fakebin / "pgrep").write_text('#!/bin/sh\n[ "$1 $2" = "-x waybar" ] && exit 1\nexec /usr/bin/pgrep "$@"\n')
        (fakebin / "pgrep").chmod(0o755)
        wsenv = dict(env, PATH=f"{fakebin}:{os.environ['PATH']}")
        ws = subprocess.Popen([sys.executable, str(HERE / "applets/workspaces/hypeforge-workspaces")], env=wsenv, stdout=log, stderr=log)
        time.sleep(1.5)
        bar = subprocess.Popen(["waybar", "-c", str(conf / "sway/waybar/config.jsonc"), "-s", str(conf / "sway/waybar/style.css")],
                               env=env, stdout=log, stderr=log)
        bar_ref = bar
        time.sleep(3)
        def visible():
            """True when on EVERY screen the bar's band (top or bottom, from its config) is not the
            magenta background — a bar can vanish from some screens only."""
            cfg = json.loads("\n".join(l for l in (conf / "sway/waybar/config.jsonc").read_text().splitlines()
                                       if not l.strip().startswith("//")))
            outs = json.loads(subprocess.run(["swaymsg", "-t", "get_outputs", "-r"], env=env,
                                             capture_output=True, text=True).stdout)
            for o in outs:
                r = o["rect"]
                y = r["y"] + (r["height"] - 30 if cfg.get("position") == "bottom" else 15)
                shot = base / "shot.ppm"
                subprocess.run(["grim", "-t", "ppm", "-g", f"{r['x']},{y} {r['width']}x1", str(shot)], env=env, check=True)
                data = shot.read_bytes().split(b"\n", 3)[3]
                px = [data[i:i + 3] for i in range(0, len(data), 3)]
                if sum(1 for p in px if p != b"\xff\x00\xff") <= len(px) * 0.1:
                    return False
            return True
        def start_bar():
            return subprocess.Popen(["waybar", "-c", str(conf / "sway/waybar/config.jsonc"),
                                     "-s", str(conf / "sway/waybar/style.css")], env=env, stdout=log, stderr=log)
        mode = "reload" if "--reload-only" in sys.argv else "engine"
        helpers = []

        def strip_up():
            try:
                os.kill(int((run / "hypeforge-panel-strip.pid").read_text()), 0)
                return True
            except (OSError, ValueError):
                return False

        for style in ORDER[1:]:
            r = ht.apply(style, "kognogos-mocha", place, reload=False, check_names=False, make_wallpaper=False, say=lambda *_: None)
            layout = any(p.name in ("config.jsonc", "style.css") and "waybar" in str(p) for p in r["changed"])
            if mode == "engine" and layout and ht.BAR_RESTART:
                bar.terminate(); bar.wait(5); bar = start_bar()    # what the engine does on a new layout
            else:
                os.kill(bar.pid, signal.SIGUSR2)                    # a reload in place
            time.sleep(0.15)
            if bar.poll() is None:
                os.kill(bar.pid, signal.SIGUSR2)                    # an applet's own reload right after (F-58)
            time.sleep(3)
            # what the engine does with the style's applets: stop the old style's, start the new one's
            # (Sway's exec_always lines) — Mac OS 9's Control Strip must come and go with its style
            wanted = ht.style_applets(ht.styles()[style])
            ht.stop_other_applets(wanted, say=lambda *_: None, runtime=run)
            for name in wanted:
                helpers.append(subprocess.Popen([sys.executable, str(HERE / f"applets/{name}/hypeforge-{name}")],
                                                env=wsenv, stdout=log, stderr=log))
            time.sleep(2.5 if wanted else 0.5)
            strip_ok = strip_up() == ("strip" in wanted)
            results.append(strip_ok)
            print(("  ok    " if strip_ok else "  FAIL  ") + f"→ {style}: the Control Strip is "
                  + ("there" if strip_up() else "not there") + (" (as it should be)" if strip_ok else ""))
            alive = bar.poll() is None
            seen = alive and visible()
            results.append(seen)
            print(("  ok    " if seen else "  FAIL  ") + f"→ {style}: the bar is " + ("running and visible" if seen else "running but INVISIBLE" if alive else "GONE"))
            if not seen:
                subprocess.run(["grim", str(base / f"fail-{style}.png")], env=env)
                print(f"        picture: {base / f'fail-{style}.png'}")
                break
    finally:
        for p in [*locals().get("helpers", []), locals().get("bar"), locals().get("ws"), sway]:
            if p and p.poll() is None:
                p.terminate()
        os.kill(int(bus[1]), signal.SIGTERM)
    print(f"\nRESULT: {sum(results)}/{2 * (len(ORDER) - 1)} passed" + ("" if all(results) else f"; see {base / 'bench.log'}"))
    return 0 if len(results) == len(ORDER) - 1 and all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
