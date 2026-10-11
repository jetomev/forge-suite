#!/usr/bin/env python3
"""themeForge's bench: every theme and its colours switched the way themeForge does it, on a hidden
desktop, with an undo in between — before Javier sees it.

Javier, 2026-10-11, after the first themeForge: "only rice and macos works … Classic, it's a
disaster. … test on a virtual machine if you have to." What he hit: undo put the old files back but
only told the running bar to reload — the bar kept the other theme's layout under the new
stylesheet (F-67). The fresh-start benches never undid anything.

A screen-less Sway with THREE screens (like Javier's), its own config and runtime folders, a
private message bus, the real bar program (hypeforge-bar, one Waybar, a bar per screen) and every
helper the themes start (Sway runs them, exec_always, as at login). Then, step by step:
themeForge's own code writes the look file and runs `hypeforge-theme look`, or `undo`. After EVERY
step it checks:
  1. the bar program running, once
  2. the bar on screen is exactly the theme's layout (the per-screen config hypeforge-bar wrote
     == the theme's config.jsonc, laid out for these screens)
  3. the bar's stylesheet is the theme's
  4. a bar drawn on every screen (no magenta at the bar's row)
  5. the theme's helpers running, the others' stopped
  6. the look file and hypeForge's memory say the same theme and colours
Nothing touches the real desktop: the real bar's process number is the same at the end.

    look-bench.py            every check, every step; exit 0 when all pass
    look-bench.py --quick    four steps (a smoke test)
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import re
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent                  # themeforge/
sys.path.insert(0, str(HERE))
from themeforge.look import Look  # noqa: E402

HYPE = Path.home() / "Programs/forge-suite/hypeforge"
MAGENTA = (255, 0, 255)

# style, colours — every theme, a different colour each time, light ones too; undo after some
STEPS = [("apply", "windows-11", "blue"), ("apply", "mac-os-9", "light-gray"), ("undo",),
         ("apply", "kde", "green"), ("apply", "cosmic", "dark-purple"), ("undo",), ("undo",),
         ("apply", "macos", "white"), ("apply", "classic", "ember"), ("undo",),
         ("apply", "classic", "red"), ("apply", "rice", "pink"), ("apply", "rice", "kognogos-mocha"),
         ("apply", "windows-11", "dark-red"), ("apply", "kde", "light-blue"), ("undo",)]
QUICK = [("apply", "windows-11", "blue"), ("apply", "classic", "ember"), ("undo",), ("apply", "rice", "kognogos-mocha")]


def load(path: Path, name: str):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader))
    loader.exec_module(m)
    return m


TAG = "HYPEFORGE_OUTPUT="


def layout(bar: dict) -> str:
    """A bar as the theme draws it: its keys and its own pieces, the screen tags taken off the clicks,
    and the tag-only entries hypeforge-bar adds for pieces of the helpers' files left out (a helper
    may write its file a moment after the bar starts; those clicks don't depend on the screen)."""
    out = {}
    for k, v in bar.items():
        if isinstance(v, dict):
            v = {kk: (vv.split("export HYPEFORGE_OUTPUT; ", 1)[1] if isinstance(vv, str) and vv.startswith(TAG) else vv)
                 for kk, vv in v.items()}
            if set(v) <= {"on-click", "on-click-right", "on-click-middle"} and k not in ("group/quick",):
                continue
        out[k] = v
    return json.dumps(out, sort_keys=True)


def main() -> int:
    steps = QUICK if "--quick" in sys.argv else STEPS
    real_before = subprocess.run(["pgrep", "-x", "waybar"], capture_output=True, text=True).stdout.split()
    bar_tool = load(HYPE / "applets/bar/hypeforge-bar", "hfbar_bench")
    base = Path(tempfile.mkdtemp(prefix="tfbench.", dir="/tmp"))
    run, conf, state = base / "r", base / "c", base / "s"
    run.mkdir(mode=0o700)
    (conf / "hypeforge/applets").mkdir(parents=True)
    (conf / "hypeforge/applets/workspaces.toml").write_text(
        'enabled = true\nscreens = ["HEADLESS-1", "HEADLESS-2", "HEADLESS-3"]\n'
        + "".join(f'[[workspace]]\nname = "{n}"\n' for n in ("Daily", "Work", "Play")))
    real = Path.home() / ".config"
    for rel in ("hypeforge/applets/sections.toml", "hypeforge/applets/favourites.waybar.json",
                "hypeforge/bar/launcher.png"):
        if (real / rel).exists():
            (conf / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(real / rel, conf / rel)
    # a magenta wallpaper: a screen with no bar shows magenta at the bar's row
    from PIL import Image
    wall = base / "magenta.png"
    Image.new("RGB", (64, 64), MAGENTA).save(wall)
    (conf / "hypeforge/theme").mkdir(parents=True)
    (conf / "hypeforge/theme/state.toml").write_text(f'wallpaper = "{wall}"\n')
    (base / "sway.conf").write_text("output * resolution 1280x720\nxwayland disable\n"
                                    f"include {conf}/hypeforge/theme/sway.conf\n")
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK", "DBUS_SESSION_BUS_ADDRESS", "HYPEFORGE_OUTPUT")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), XDG_STATE_HOME=str(state),
               WLR_BACKENDS="headless", WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="3",
               WLR_LIBINPUT_NO_DEVICES="1", GDK_BACKEND="wayland")
    fakebin = base / "bin"
    fakebin.mkdir()                     # redraws and restarts must never reach the real bar
    for tool in ("pgrep", "pkill"):
        (fakebin / tool).write_text(f'#!/bin/sh\ncase "$*" in *waybar*) exit 1;; esac\nexec /usr/bin/{tool} "$@"\n')
        (fakebin / tool).chmod(0o755)
    env["PATH"] = f"{fakebin}:{os.environ['PATH']}"
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"] = bus[0]
    log = open(base / "bench.log", "w")
    results: list[bool] = []

    def check(ok, what):
        results.append(bool(ok))
        print(("  ok    " if ok else "  FAIL  ") + what, flush=True)

    tool = HYPE / "applets/theme/hypeforge-theme"
    # the first look, before Sway starts: its sway.conf is what Sway includes
    subprocess.run([str(tool), "apply", "rice", "kognogos-mocha", "--no-reload"], env=env, stdout=log, stderr=log)
    sway = subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    look = None
    try:
        for _ in range(100):
            socks = list(run.glob("sway-ipc.*.sock"))
            if socks:
                break
            time.sleep(0.1)
        env["SWAYSOCK"] = str(socks[0])
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        subprocess.run([sys.executable, str(HYPE / "applets/bar/hypeforge-bar"), "start"], env=env, stdout=log, stderr=log)
        time.sleep(4)
        outputs = json.loads(subprocess.run(["swaymsg", "-t", "get_outputs", "-r"], env=env,
                                            capture_output=True, text=True).stdout)
        names = [o["name"] for o in outputs]
        main_screen = bar_tool.main_screen(outputs)

        # themeForge's own code, pointed at the hidden desktop
        def tf_run(cmd, **kw):
            return subprocess.run(cmd, env=env, **kw)
        look = Look(HYPE, conf, run=tf_run, log=state / "themeforge.log")
        styles = {s: tomllib.loads((HYPE / f"styles/{s}/style.toml").read_text())
                  for s in [p.parent.name for p in HYPE.glob("styles/*/style.toml")]}

        def bar_pid():
            try:
                return int(json.loads((run / "hypeforge-bar/pids.json").read_text())["pid"])
            except (OSError, ValueError, KeyError):
                return None

        def alive(pid, word):
            try:
                return word.encode() in Path(f"/proc/{pid}/cmdline").read_bytes()
            except (OSError, TypeError):
                return False

        def bar_rows_seen(style):
            """For each screen: a bar drawn at the top or bottom row the theme's bar(s) use."""
            cfg = json.loads(bar_tool.strip_comments((conf / "sway/waybar/config.jsonc").read_text()))
            bars = cfg if isinstance(cfg, list) else [cfg]
            every = next(b for b in bars if "hypeforge-screens" not in b)
            seen = []
            for o in outputs:
                r = o["rect"]
                h = int(every.get("height", 30))
                top = int(every.get("margin-top", 0))
                bottom = int(every.get("margin-bottom", 0))
                y = r["y"] + (r["height"] - bottom - h // 2 if every.get("position") == "bottom" else top + h // 2)
                p = base / "row.ppm"
                subprocess.run(["grim", "-t", "ppm", "-g", f"{r['x']},{y} {r['width']}x1", str(p)], env=env, check=True)
                data = p.read_bytes().split(b"\n", 3)[3]
                px = [tuple(data[i:i + 3]) for i in range(0, len(data), 3)]
                seen.append(sum(1 for c in px if c != MAGENTA) > len(px) * 0.25)
            return seen

        history = [("rice", "kognogos-mocha")]
        for n, step in enumerate(steps, 1):
            if step[0] == "apply":
                _, st, co = step
                ok, words = look.apply(st, co)
                history.append((st, co))
                label = f"{n:>2}. apply {st} · {co}"
            else:
                ok, words = look.undo()
                history.pop()
                st, co = history[-1]
                label = f"{n:>2}. undo → {st} · {co}"
            time.sleep(5)
            print(label, flush=True)
            check(ok, f"themeForge says done ({words[:70]})")
            pid = bar_pid()
            procs = subprocess.run(["/usr/bin/pgrep", "-x", "waybar"], capture_output=True, text=True).stdout.split()
            ours = [p for p in procs if p not in real_before]
            check(alive(pid, "waybar") and len(ours) == 1, f"one bar program running ({len(ours)})")
            src = HYPE / "sway/waybar" if st == "classic" else HYPE / f"styles/{st}/bar"
            want = bar_tool.bars_for((src / "config.jsonc").read_text(), names, main_screen)
            have = json.loads((run / "hypeforge-bar/config.json").read_text())
            check(sorted(map(layout, want)) == sorted(map(layout, have)), "the bar on screen is the theme's layout")
            check((conf / "sway/waybar/style.css").read_text().replace("/* corners: straight (hypeforge-theme corners) */\n", "")
                  == (src / "style.css").read_text(), "the bar's stylesheet is the theme's")
            rows = bar_rows_seen(st)
            check(all(rows), f"a bar drawn on every screen {rows}")
            wanted = set(styles[st].get("layout", {}).get("applets", []) if isinstance(
                styles[st].get("layout", {}).get("applets", []), list) else [])
            every_applet = {a for s in styles.values() for a in (s.get("layout", {}).get("applets", [])
                                                                 if isinstance(s.get("layout", {}).get("applets", []), list) else [])}
            running = set()
            for a in every_applet:
                try:
                    if alive(int((run / f"hypeforge-{a}.pid").read_text()), f"hypeforge-{a}"):
                        running.add(a)
                except (OSError, ValueError):
                    pass
            check(running == wanted, f"helpers: {sorted(running) or 'none'} (the theme's: {sorted(wanted) or 'none'})")
            sc = (conf / "hypeforge/theme/sway.conf").read_text()
            edge = sum(int(re.search(rf"^gaps {k} (\d+)$", sc, re.M).group(1)) for k in ("inner", "outer"))
            spaces = json.loads(subprocess.run(["swaymsg", "-t", "get_workspaces", "-r"], env=env,
                                               capture_output=True, text=True).stdout)
            out_x = {o["name"]: o["rect"]["x"] for o in outputs}
            edges = sorted({w["rect"]["x"] - out_x[w["output"]] for w in spaces})
            check(edges == [edge], f"open workspaces got the theme's gaps: edge {edges} (want {edge})")
            picks = look.picks()
            mem = tomllib.loads((conf / "hypeforge/theme/state.toml").read_text())
            check((picks.get("theme"), picks.get("colors")) == (st, co) == (mem.get("style"), mem.get("theme")),
                  f"the look file and hypeForge's memory: {picks.get('theme')} · {picks.get('colors')}")
            shot = base / f"step-{n:02d}.png"
            subprocess.run(["grim", "-s", "0.25", str(shot)], env=env, stdout=log, stderr=log)
    finally:
        subprocess.run([sys.executable, str(HYPE / "applets/bar/hypeforge-bar"), "stop"], env=env, capture_output=True)
        sway.terminate()
        try:
            sway.wait(5)
        except subprocess.TimeoutExpired:
            sway.kill()
        try:
            os.kill(int(bus[1]), signal.SIGTERM)
        except (OSError, ValueError, IndexError):
            pass
    real_after = subprocess.run(["pgrep", "-x", "waybar"], capture_output=True, text=True).stdout.split()
    check(real_before == real_after, f"the real desktop's bar untouched ({' '.join(real_before) or 'none'})")
    print(f"\nRESULT: {sum(results)}/{len(results)} passed" + ("" if all(results) else f"; see {base}"))
    print(f"pictures and log: {base}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
