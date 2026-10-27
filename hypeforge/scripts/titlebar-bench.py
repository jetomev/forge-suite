#!/usr/bin/env python3
"""The hidden bench for title bars and the window menu (D-110, 2026-10-17; bench before live). One fake
screen on its own Sway and message bus, the Rice's look, the title-bar lines of the real sway/config, the
real watcher (applets/window/hypeforge-window watch), stand-in windows and a fake mouse:

  - the look gives floating windows the title bar, tiled ones the plain frame
  - a window made to float by a rule, or by Win + Shift + Space, gets the title bar; back in the grid it
    loses it; a window that draws its own bar never gets ours, but Alacritty (every Forge app), which
    asks to and draws none, does
  - left drag on the title bar moves the window; a middle click tucks it away (a tiled window's top
    edge does nothing); a right click opens the window menu for that window, a right click inside the
    window doesn't
  - the menu's actions: back into the grid, float, to workspace 2
  - the real desktop is untouched

    titlebar-bench.py [--keep] [--ours]

--ours (D-111): hypeForge's own Sway build (~/.local/opt/sway-hypeforge/current) with the real button lines
(sway/config-buttons): the three buttons drawn; close, minimise, maximise and back again by a click; a
drag between them still moves the window.

Writes logs/titlebar-bench.png (the window menu open) for a look.
"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/panels"))
import panelkit  # noqa: E402

WINDOW = HERE / "applets/window/hypeforge-window"
FAKE = HERE / "scripts/fake-window.py"
POINTER = HERE / "scripts/fake-pointer.py"


def title_bar_lines() -> str:
    """The real sway/config's lines for title bars and floating, so the bench clicks what Javier clicks."""
    text = (HERE / "sway/config").read_text()
    keep = [l.strip() for l in text.splitlines()
            if re.match(r"\s*(bindsym (button2|button3|\$mod\+Shift\+space)|floating_modifier)\b", l)]
    return "set $mod Mod4\n" + "\n".join(keep) + "\n"


OURS = Path.home() / ".local/opt/sway-hypeforge/current/bin/sway"


def button_lines() -> str:
    """sway/config-buttons without its include: the lines only our build reads (their colours are the
    theme's $hf_… variables, set by the look's sway.conf the bench includes first)."""
    return "\n".join(l for l in (HERE / "sway/config-buttons").read_text().splitlines()
                     if l.startswith("titlebar_button")) + "\n"


def main() -> int:
    keep = "--keep" in sys.argv
    ours = "--ours" in sys.argv
    if ours and not OURS.exists():
        print(f"no build at {OURS}: run sway-hypeforge/build.py first")
        return 1
    ht = panelkit.theme_tool()
    real_sock = os.environ.get("SWAYSOCK")
    base = Path(tempfile.mkdtemp(prefix="hftitle.", dir="/tmp"))
    run, conf = base / "r", base / "c"
    run.mkdir(mode=0o700)
    (conf / "hypeforge/applets").mkdir(parents=True)
    (conf / "hypeforge/applets/workspaces.toml").write_text(
        'enabled = true\nscreens = ["HEADLESS-1"]\n[[workspace]]\nname = "Daily"\n[[workspace]]\nname = "Work"\n')
    place = ht.Place(conf)
    ht.apply("rice", "kognogos-mocha", place, reload=False, check_names=False, make_wallpaper=False, say=lambda *_: None)
    theme_conf = conf / "hypeforge/theme/sway.conf"
    (base / "sway.conf").write_text(
        "output * resolution 1280x720 bg #ff00ff solid_color\nxwayland disable\n"
        f"include {theme_conf}\n" + title_bar_lines() + (button_lines() if ours else "") +
        'for_window [app_id="by-rule"] floating enable, move position 640 80\n'
        'for_window [app_id="own-bar"] floating enable, move position 60 420\n')
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "DBUS_SESSION_BUS_ADDRESS", "HYPEFORGE_OUTPUT")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), XDG_DATA_HOME=str(conf / ".local-data"),
               WLR_BACKENDS="headless", WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="1", WLR_LIBINPUT_NO_DEVICES="1",
               GDK_BACKEND="wayland")
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"] = bus[0]
    log = open(base / "bench.log", "w")
    results = []

    def check(ok, what):
        results.append(bool(ok))
        print(("  ok    " if ok else "  FAIL  ") + what, flush=True)

    sway = subprocess.Popen([str(OURS) if ours else "sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    procs = []
    try:
        time.sleep(2)
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        env["SWAYSOCK"] = next(str(p) for p in run.glob("sway-ipc.*.sock"))
        t = theme_conf.read_text()
        check("default_border pixel 2" in t and "default_floating_border normal 2" in t and "title_align" in t,
              "the look: tiled windows the plain frame, floating ones the title bar")

        def msg(*cmd):
            return subprocess.run(["swaymsg", *cmd], env=env, capture_output=True, text=True).stdout

        def wins():
            out = {}

            def walk(n, scratch=False):
                if n.get("app_id"):
                    out[n["app_id"]] = dict(n, scratch=scratch)
                for ch in n.get("nodes", []) + n.get("floating_nodes", []):
                    walk(ch, scratch or n.get("name") == "__i3_scratch")
            walk(json.loads(msg("-t", "get_tree")))
            return out

        def ws_of(app):
            for o in json.loads(msg("-t", "get_tree"))["nodes"]:
                for ws in o.get("nodes", []):
                    if app in json.dumps(ws):
                        return ws.get("num")

        def mouse(*args):
            subprocess.run([sys.executable, str(POINTER), *map(str, args), "--width", "1280", "--height", "720",
                            "--hold", "0.3"], env=env, stdout=log, stderr=log, timeout=20)
            time.sleep(0.6)

        def bar_of(w):                     # a spot on the window's title bar
            return w["rect"]["x"] + 120, w["rect"]["y"] - w["deco_rect"]["height"] // 2

        procs.append(subprocess.Popen([sys.executable, str(WINDOW), "watch"], env=env, stdout=log, stderr=log))
        time.sleep(0.8)
        for app, kind in (("tiled", "plain"), ("by-rule", "plain"), ("own-bar", "csd")):
            procs.append(subprocess.Popen([sys.executable, str(FAKE), app, kind], env=env, stdout=log, stderr=log))
            time.sleep(1.3)
        w = wins()
        check(w["tiled"]["border"] == "pixel", f"a tiled window: the plain frame ({w['tiled']['border']})")
        check(w["by-rule"]["border"] == "normal" and w["by-rule"]["deco_rect"]["height"] > 15,
              f"a window floated by a rule gets the title bar ({w['by-rule']['border']}, {w['by-rule']['deco_rect']['height']} px)")
        check(w["own-bar"]["border"] == "csd", f"a window with its own bar keeps it, no title bar of ours ({w['own-bar']['border']})")

        procs.append(subprocess.Popen(["alacritty", "--class", "a-forge-app", "-e", "sleep", "120"], env=env,
                                      stdout=log, stderr=log))
        time.sleep(2)
        msg('[app_id="a-forge-app"] floating toggle')
        time.sleep(0.8)
        a = wins().get("a-forge-app", {})
        check(a.get("border") == "normal", f"a Forge app in Alacritty, floated, gets our title bar ({a.get('border')}; F-55)")
        # a theme switch reloads Sway, and a reload puts every window back to the default frame (Javier,
        # 10-17: "when sway switched between them, the title bar disappeared even when it was still floating")
        msg("reload")
        time.sleep(1.5)
        check(wins()["by-rule"]["border"] == "normal", f"after a reload (a theme switch) a floating window keeps its title bar ({wins()['by-rule']['border']})")
        check(wins()["tiled"]["border"] == "pixel", f"after a reload a tiled window keeps the plain frame ({wins()['tiled']['border']})")
        check(wins()["a-forge-app"]["border"] == "normal", f"after a reload a floating Forge app (Alacritty) keeps its title bar ({wins()['a-forge-app']['border']})")
        # whatever takes a title bar away with no word from Sway (never reproduced hidden), it comes back
        msg('[app_id="by-rule"] border pixel 2')
        time.sleep(4)
        check(wins()["by-rule"]["border"] == "normal", f"a title bar taken away behind the watcher's back comes back within seconds ({wins()['by-rule']['border']})")

        # the real switch, as themeForge runs it: every style in turn, the Forge app floating through all
        lost = []
        for slug in ("windows-11", "mac-os-9", "kde", "macos", "cosmic", "classic", "rice"):
            r = subprocess.run([sys.executable, str(HERE / "applets/theme/hypeforge-theme"), "apply", slug, "kognogos-mocha"],
                               env=env, capture_output=True, text=True, timeout=120)
            time.sleep(1.5)
            w = wins()
            seen = (w.get("a-forge-app", {}).get("border"), w.get("by-rule", {}).get("border"), w.get("tiled", {}).get("border"))
            tall = (w.get("a-forge-app", {}).get("deco_rect", {}).get("height"), w.get("by-rule", {}).get("deco_rect", {}).get("height"))
            log.write(f"switch to {slug}: forge-app {seen[0]} {tall[0]} px · gtk {seen[1]} {tall[1]} px · tiled {seen[2]} (exit {r.returncode})\n")
            subprocess.run(["grim", str(base / f"switch-{slug}.png")], env=env)
            # the frame setting AND a title bar actually there (Javier saw it gone while the setting held)
            if seen[0] != "normal" or seen[1] != "normal" or seen[2] == "normal" or not all(h and h > 10 for h in tall):
                lost.append(f"{slug}: {seen} {tall}")
        check(not lost, f"through every style's switch the floating windows keep their title bar, tiled ones don't get one ({lost or 'all kept'})")
        msg('[app_id="a-forge-app"] kill')
        time.sleep(0.5)

        msg('[app_id="tiled"] focus')
        msg('[app_id="tiled"] floating toggle')            # what Win + Shift + Space runs
        time.sleep(0.6)
        check(wins()["tiled"]["border"] == "normal", f"Win + Shift + Space floats it with the title bar ({wins()['tiled']['border']})")
        msg('[app_id="tiled"] floating toggle')
        time.sleep(0.6)
        check(wins()["tiled"]["border"] == "pixel", f"back into the grid, the title bar goes ({wins()['tiled']['border']})")

        f = wins()["by-rule"]
        x, y = bar_of(f)
        mouse(x, y, "--drag", x + 140, y + 100)
        g = wins()["by-rule"]["rect"]
        check((g["x"] - f["rect"]["x"], g["y"] - f["rect"]["y"]) == (140, 100) and g["height"] == f["rect"]["height"],
              f"left drag on the title bar moves it (by {g['x'] - f['rect']['x']}, {g['y'] - f['rect']['y']})")

        f = wins()["by-rule"]
        x, y = bar_of(f)
        mouse(400, 600, "--click")                           # the focus elsewhere first
        mouse(x, y, "--click", "--button", "right")
        time.sleep(1.5)
        pid = run / "hypeforge-panel-windowmenu.pid"
        argv = Path(f"/proc/{pid.read_text()}/cmdline").read_bytes().split(b"\0") if pid.exists() else []
        check(pid.exists() and str(f["id"]).encode() in argv, f"a right click on the title bar opens the menu for that window")
        pic = HERE / ("logs/titlebar-bench-ours.png" if ours else "logs/titlebar-bench.png")
        pic.parent.mkdir(exist_ok=True)
        subprocess.run(["grim", str(pic)], env=env)
        if pid.exists():
            os.kill(int(pid.read_text()), signal.SIGTERM)
            time.sleep(0.8)
        mouse(f["rect"]["x"] + 120, f["rect"]["y"] + 120, "--click", "--button", "right")
        time.sleep(1)
        check(not pid.exists(), "a right click inside the window opens nothing")

        t0 = wins()["tiled"]
        mouse(t0["rect"]["x"] + 60, t0["rect"]["y"] + 1, "--click", "--button", "middle")
        check(not wins()["tiled"]["scratch"], "a middle click at a tiled window's top edge does nothing")
        mouse(x, y, "--click", "--button", "middle")
        check(wins()["by-rule"]["scratch"], "a middle click on the title bar tucks it away")
        msg('[app_id="by-rule"] scratchpad show')
        time.sleep(0.5)

        fid = wins()["by-rule"]["id"]
        subprocess.run([sys.executable, str(WINDOW), "tile", str(fid)], env=env, timeout=10)
        time.sleep(0.6)
        check(wins()["by-rule"]["type"] == "con" and wins()["by-rule"]["border"] == "pixel", "the menu's Back into the grid")
        subprocess.run([sys.executable, str(WINDOW), "float", str(fid)], env=env, timeout=10)
        time.sleep(0.6)
        check(wins()["by-rule"]["type"] == "floating_con" and wins()["by-rule"]["border"] == "normal", "the menu's Float, with the title bar")
        subprocess.run([sys.executable, str(WINDOW), "to", "2", str(fid)], env=env, timeout=15)
        time.sleep(0.8)
        check(ws_of("by-rule") == 2, f"the menu's Move to workspace 2 (now on {ws_of('by-rule')})")
        if ours:                         # the title bar's buttons (D-111): our own Sway build
            msg("workspace number 2")
            time.sleep(0.5)

            def slot(app, i):            # 0 minimise, 1 maximise, 2 close: the middle of its square
                n = wins()[app]
                r, h = n["rect"], n["deco_rect"]["height"]
                return int(r["x"] + r["width"] - (3 - i) * h + h / 2), int(r["y"] - h / 2)
            # the button under the pointer lights up (patch 2): the corner of its square in the theme's colour
            theme = ht.themes()["kognogos-mocha"]
            style = ht.styles()["rice"]
            want = {k: ht.resolve(k, style, theme) for k in ("titlebar_close_hover", "titlebar_button_hover", "titlebar_bg")}

            def corner(app, i):
                n = wins()[app]
                r, h = n["rect"], n["deco_rect"]["height"]
                x = int(r["x"] + r["width"] - (3 - i) * h + 2)
                y = int(r["y"] - h + 3)
                out = subprocess.run(["grim", "-g", f"{x},{y} 1x1", "-t", "ppm", "-"], env=env, capture_output=True).stdout
                return "#%02x%02x%02x" % tuple(out.split(b"\n", 3)[3][:3])
            mouse(*slot("by-rule", 2))
            lit_close = corner("by-rule", 2)
            mouse(*slot("by-rule", 0))
            lit_min, close_after = corner("by-rule", 0), corner("by-rule", 2)
            check(lit_close == want["titlebar_close_hover"], f"✕ under the pointer turns the theme's red ({lit_close}, want {want['titlebar_close_hover']})")
            check(lit_min == want["titlebar_button_hover"] and close_after != lit_close,
                  f"─ under the pointer lights up, ✕ goes back ({lit_min} want {want['titlebar_button_hover']}; ✕ now {close_after})")
            before = wins()["by-rule"]["rect"]
            mouse(*slot("by-rule", 1), "--click")
            big = wins()["by-rule"]["rect"]
            check(big["width"] > 1100 and big["height"] > 550, f"□ fills the screen's free room ({big['width']}×{big['height']})")
            mouse(*slot("by-rule", 1), "--click")
            back = wins()["by-rule"]["rect"]
            check(abs(back["x"] - before["x"]) <= 2 and abs(back["y"] - before["y"]) <= 2 and abs(back["width"] - before["width"]) <= 4,
                  f"□ again puts it back ({back['x']},{back['y']} {back['width']}×{back['height']} vs {before['x']},{before['y']} {before['width']}×{before['height']})")
            n = wins()["by-rule"]
            x, y = n["rect"]["x"] + 60, n["rect"]["y"] - n["deco_rect"]["height"] // 2
            mouse(x, y, "--drag", x + 80, y + 40)
            moved = wins()["by-rule"]["rect"]
            check((moved["x"] - n["rect"]["x"], moved["y"] - n["rect"]["y"]) == (80, 40), "a drag beside the buttons still moves it")
            mouse(*slot("by-rule", 0), "--click")
            check(wins()["by-rule"]["scratch"], "─ tucks it away")
            msg('[app_id="by-rule"] scratchpad show')
            time.sleep(0.5)
            mouse(*slot("by-rule", 2), "--click")
            time.sleep(0.5)
            check("by-rule" not in wins(), "✕ closes it")
            check(sway.poll() is None, "our Sway is still running")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        sway.terminate()
        os.kill(int(bus[1]), signal.SIGTERM)
    check(os.environ.get("SWAYSOCK") == real_sock, "the real desktop untouched")
    print(f"\nRESULT: {sum(results)}/{len(results)} passed" + ("" if all(results) else f"; see {base / 'bench.log'}"))
    if not keep and all(results):
        import shutil
        shutil.rmtree(base, ignore_errors=True)
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
