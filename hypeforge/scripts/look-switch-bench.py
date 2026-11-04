#!/usr/bin/env python3
"""The hidden bench for a look switch done the way themeForge does it (2026-11-04: Javier switched to
Windows 11, then KDE, and no bar came up; the bar's own log showed it running, drawing nothing, for 79 s).

switch-bench.py starts and stops a bare Waybar itself; this one runs the real path end to end, on a
screen-less Sway with its own runtime folder, settings and home:

  * login as on the desktop: the bar through `hypeforge-bar start` and its guard, the Workspaces, tray
    and system applets, each under hypeforge-watch; the style's applets from the look's sway.conf
  * every switch through `apply(..., reload=True)`: Sway reloaded (its exec_always starts the new
    style's applets), the old ones stopped, the bar stopped and started by its own tool
  * after each switch the bar must be DRAWN on every screen within a time limit — a bar that runs and
    shows nothing is a failure (the visible check reads the bar's band off a magenta background).

pkill/pgrep/makoctl/gsettings are stand-ins that only ever see this bench's own processes, so the real
bar is never signalled.

    look-switch-bench.py [styles…]     default: every style, each reached from a different one
      --busy-title                     a window retitled 20 times a second is open the whole time (F-89)
      --my-pins                        the Taskbar pins a copy of your Favorites (more pieces on the bar)
    BENCH_LIMIT=8 BENCH_SCREENS=3      seconds a bar may take to show; how many screens
"""
from __future__ import annotations

import json, os, shutil, signal, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
LIMIT = float(os.environ.get("BENCH_LIMIT", "8"))
THEME = "kognogos-mocha"
BAR = "benchwaybar"        # ends in "waybar": hypeforge-bar's own check still knows it
# Javier's order of 2026-11-04 first (rice → windows-11 → kde → classic → macos → cosmic → kde), then the
# pairs it missed, so every style is reached from a bar of another layout
ORDER = ["rice", "windows-11", "kde", "classic", "macos", "cosmic", "kde", "mac-os-9", "windows-11",
         "cosmic", "rice", "macos", "mac-os-9", "classic", "windows-11"]

# A stand-in for pgrep/pkill: the real one, limited to processes started inside this bench (their
# XDG_RUNTIME_DIR is the bench's). The engine stops the bar with `pkill -x waybar`; without this the
# bench would stop the desktop's own bar.
STAND_IN = r'''#!/usr/bin/env python3
import os, subprocess, sys
run = os.environ["HF_BENCH_RUN"].encode()
args = sys.argv[1:]
sig = None
if os.path.basename(sys.argv[0]) == "pkill" and args and args[0].startswith("-") and args[0] not in ("-x", "-f"):
    sig, args = args[0][1:], args[1:]
args = ["BENCHBAR" if a == "waybar" else a for a in args]       # the bench's bar runs under its own name
pids = subprocess.run(["/usr/bin/pgrep", *args], capture_output=True, text=True).stdout.split()
mine = []
for p in pids:
    try:
        env = open(f"/proc/{p}/environ", "rb").read().split(b"\0")
    except OSError:
        continue
    if b"XDG_RUNTIME_DIR=" + run in env:
        mine.append(p)
if os.path.basename(sys.argv[0]) == "pgrep":
    print("\n".join(mine))
else:
    for p in mine:
        subprocess.run(["/usr/bin/kill", "-" + (sig or "TERM"), p])
sys.exit(0 if mine else 1)
'''


def main() -> int:
    stand_in = STAND_IN.replace("BENCHBAR", BAR)
    order = [a for a in sys.argv[1:] if not a.startswith("--")] or ORDER
    base = Path(tempfile.mkdtemp(prefix="hfls.", dir="/tmp"))
    run, conf, home = base / "r", base / "c", base / "h"
    run.mkdir(mode=0o700)
    (conf / "hypeforge/applets").mkdir(parents=True)
    (home / ".local/share").mkdir(parents=True)
    real = Path.home() / ".local/share"
    for d in ("fonts", "icons", "applications"):       # read only: the bar's fonts, icons and apps, as on the desktop
        if (real / d).is_dir():
            (home / ".local/share" / d).symlink_to(real / d)
    # the shared bar pieces name ~/Programs/forge-suite/…: in this home, that is the code under test
    (home / "Programs").mkdir()
    (home / "Programs/forge-suite").symlink_to(HERE.parent)
    if "--my-pins" in sys.argv:                        # a copy of the person's Favorites: the Taskbar's pinned apps
        mine = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "hypeforge/applets/sections.toml"
        if mine.is_file():
            shutil.copy(mine, conf / "hypeforge/applets/sections.toml")
    (conf / "hypeforge/applets/workspaces.toml").write_text(
        'enabled = true\nscreens = ["HEADLESS-1", "HEADLESS-2", "HEADLESS-3"]\n[[workspace]]\nname = "Daily"\n')
    fakebin = base / "bin"
    fakebin.mkdir()
    for name in ("pgrep", "pkill"):
        (fakebin / name).write_text(stand_in)
        (fakebin / name).chmod(0o755)
    # the bar under its own name: the desktop's applets signal every program called "waybar" (pgrep -x waybar),
    # so a bench bar named so took the desktop's redraws too; this one only hears the bench's (stand-ins above)
    (fakebin / BAR).symlink_to(shutil.which("waybar"))
    (fakebin / "waybar").write_text(f'#!/bin/sh\nexec "{fakebin / BAR}" "$@"\n')
    (fakebin / "waybar").chmod(0o755)
    for name in ("makoctl", "gsettings", "notify-send"):
        (fakebin / name).write_text("#!/bin/sh\nexit 0\n")
        (fakebin / name).chmod(0o755)

    env = {k: v for k, v in os.environ.items() if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "DBUS_SESSION_BUS_ADDRESS")}
    env.update(HOME=str(home), XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), XDG_DATA_HOME=str(home / ".local/share"),
               XDG_STATE_HOME=str(home / ".local/state"), XDG_CACHE_HOME=str(home / ".cache"), HF_BENCH_RUN=str(run),
               PATH=f"{fakebin}:{os.environ['PATH']}", WLR_BACKENDS="headless", WLR_RENDERER="pixman",
               WLR_HEADLESS_OUTPUTS=os.environ.get("BENCH_SCREENS", "3"), WLR_LIBINPUT_NO_DEVICES="1")
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"] = bus[0]
    os.environ.clear()
    os.environ.update(env)                             # apply() below talks to THIS Sway and THIS bar only

    sys.path.insert(0, str(HERE / "applets/panels"))
    import panelkit  # noqa: E402
    ht = panelkit.theme_tool()
    place = ht.Place(conf)
    quiet = lambda *_: None
    ht.apply(order[0], THEME, place, reload=False, check_names=False, make_wallpaper=False, say=quiet)

    a = HERE / "applets"
    watch = a / "common/hypeforge-watch"
    login = [f"exec {watch} tray {a / 'tray/hypeforge-tray'} run",
             f"exec {watch} system {a / 'system/hypeforge-system'} run",
             f"exec {watch} bar {a / 'bar/hypeforge-bar'} start",
             f"exec {watch} bar-guard {a / 'bar/hypeforge-bar'} guard",
             f"exec {watch} workspaces {a / 'workspaces/hypeforge-workspaces'}"]
    (base / "sway.conf").write_text("xwayland disable\n"
                                    f"include {conf}/hypeforge/theme/sway.conf\n"
                                    "output * bg #ff00ff solid_color\n"   # after the look: magenta, easy to tell a bar from
                                    + "\n".join(login) + "\n")
    log = open(base / "bench.log", "w")
    sway = subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    results = []
    try:
        for _ in range(50):
            if any(run.glob("sway-ipc.*.sock")):
                break
            time.sleep(0.1)
        time.sleep(0.5)
        os.environ["WAYLAND_DISPLAY"] = env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        os.environ["SWAYSOCK"] = env["SWAYSOCK"] = next(str(p) for p in run.glob("sway-ipc.*.sock"))

        def bars_cfg() -> list[dict]:
            try:
                cfg = json.loads((run / "hypeforge-bar/config.json").read_text())
            except (OSError, ValueError):
                return []
            return cfg if isinstance(cfg, list) else [cfg]

        def visible() -> bool:
            """Every screen shows its bar's band (top or bottom, from the bar per screen hypeforge-bar wrote)."""
            outs = json.loads(subprocess.run(["swaymsg", "-t", "get_outputs", "-r"], env=env,
                                             capture_output=True, text=True).stdout or "[]")
            cfg = bars_cfg()
            if not outs or not cfg:
                return False
            for o in outs:
                mine = [c for c in cfg if c.get("output") == o["name"]]
                if not mine:
                    continue                 # a main-screen-only bar (COSMIC's dock) has another bar on this screen
                r = o["rect"]
                bottom = mine[0].get("position") == "bottom"
                h = int(mine[0].get("height", 30))
                y = r["y"] + (r["height"] - h // 2 - int(mine[0].get("margin-bottom", 0)) if bottom
                              else h // 2 + int(mine[0].get("margin-top", 0)))
                shot = base / "shot.ppm"
                if subprocess.run(["grim", "-t", "ppm", "-g", f"{r['x']},{y} {r['width']}x1", str(shot)], env=env,
                                  capture_output=True).returncode:
                    return False
                data = shot.read_bytes().split(b"\n", 3)[3]
                px = [data[i:i + 3] for i in range(0, len(data), 3)]
                if sum(1 for p in px if p != b"\xff\x00\xff") <= len(px) * 0.1:
                    return False
            return True

        def wait_shown(limit: float) -> float | None:
            t0 = time.monotonic()
            while time.monotonic() - t0 < limit:
                if visible():
                    return time.monotonic() - t0
                time.sleep(0.25)
            return None

        if "--busy-title" in sys.argv:
            # a window of no installed app that renames itself 20 times a second, like Godot's movie writer
            # (Javier's desktop, 2026-11-04: "MovieWriter: Frame 1403 …")
            subprocess.Popen([sys.executable, str(HERE / "scripts/fake-window.py"), "busy-recorder", "busy-title"],
                             env=env, stdout=log, stderr=log)
        took = wait_shown(30)
        print(f"  {'ok  ' if took is not None else 'FAIL'}  login on {order[0]}: the bar "
              + (f"shown in {took:.1f} s" if took is not None else "never shown"))
        results.append(took is not None)
        time.sleep(3)                                  # the login applets settle (the Taskbar's own reload)
        prev = order[0]
        for style in order[1:]:
            t0 = time.monotonic()
            ht.apply(style, THEME, place, reload=True, check_names=False, make_wallpaper=False, say=quiet)
            spent = time.monotonic() - t0
            took = wait_shown(LIMIT)
            ok = took is not None
            results.append(ok)
            pid = None
            try:
                pid = json.loads((run / "hypeforge-bar/pids.json").read_text())["pid"]
            except (OSError, ValueError, KeyError):
                pass
            alive = bool(pid) and Path(f"/proc/{pid}").exists()
            print(f"  {'ok  ' if ok else 'FAIL'}  {prev} → {style}: apply {spent:.1f} s, the bar "
                  + (f"shown {took:.1f} s later" if ok else
                     f"NOT shown after {LIMIT:g} s ({'running, drawing nothing' if alive else 'not running'})"))
            if not ok:
                subprocess.run(["grim", str(base / f"fail-{prev}-to-{style}.png")], env=env, capture_output=True)
                shutil.copy(run / "hypeforge-bar/waybar.log", base / f"fail-{prev}-to-{style}.waybar.log")
                later = wait_shown(90)
                print(f"        picture and bar log: {base}/fail-{prev}-to-{style}.*; "
                      + (f"it showed up {LIMIT + later:.0f} s after the switch" if later is not None else "still nothing after 90 s more"))
            prev = style
            time.sleep(2)
        # the bar at rest on the last style: how much it works (F-89: 1.5 cores on Javier's desktop, 2026-11-04)
        if pid and Path(f"/proc/{pid}").exists():
            def ticks():
                return sum(sum(int(x) for x in (t / "stat").read_text().rsplit(")", 1)[1].split()[11:13])
                           for t in Path(f"/proc/{pid}/task").iterdir())
            t0 = ticks(); time.sleep(5); used = (ticks() - t0) / os.sysconf("SC_CLK_TCK") / 5
            ok = used < 0.10
            results.append(ok)
            print(f"  {'ok  ' if ok else 'FAIL'}  the bar at rest on {prev}: {used * 100:.0f} % of one core")
    finally:
        try:
            subprocess.run(["swaymsg", "exit"], env=env, capture_output=True, timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            pass
        try:
            sway.wait(5)
        except subprocess.TimeoutExpired:
            sway.terminate()
        # whatever the session left (applets, the bar): only processes carrying this bench's runtime folder
        mark = b"HF_BENCH_RUN=" + str(run).encode()
        for p in Path("/proc").iterdir():
            if not p.name.isdigit() or int(p.name) == os.getpid():
                continue
            try:
                if mark in (p / "environ").read_bytes().split(b"\0"):
                    os.kill(int(p.name), signal.SIGTERM)
            except OSError:
                pass
        try:
            os.kill(int(bus[1]), signal.SIGTERM)    # the sweep above may have ended it already
        except ProcessLookupError:
            pass
    n = len(results)
    print(f"\nRESULT: {sum(results)}/{n} passed" + ("" if all(results) else f"; log: {base / 'bench.log'}, "
                                                    f"applet logs: {home}/.local/state/hypeforge/logs/"))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
