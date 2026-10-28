#!/usr/bin/env python3
"""Win alone opens the launcher; Win + anything else never does (Javier, 2026-10-27: "launcher was always
opening when pressing Win+ComboKey plus whatever was being executed").

A hidden Sway with Win (Super_L) bound on release and a few Win combos bound, each writing its name to a
file; a fake keyboard and a fake mouse press them; each case must write exactly what it should. Sway already
cancels a release shortcut when another key joins in; the mouse (Win + click, Win + drag: moving a window)
needs our build's patch 5. Nothing touches the real desktop.

    winkey-bench.py [--sway PATH]       default: hypeForge's build (~/.local/opt/sway-hypeforge/current)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
KEYS = HERE / "scripts/fake-keyboard.py"
MOUSE = HERE / "scripts/fake-pointer.py"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sway", default=str(Path.home() / ".local/opt/sway-hypeforge/current/bin/sway"))
    a = ap.parse_args()
    base = Path(tempfile.mkdtemp(prefix="hfwk.", dir="/tmp"))     # short: Sway's socket path must fit
    run, fired = base / "r", base / "fired"
    run.mkdir(mode=0o700)
    (base / "config").write_text(f"""output HEADLESS-1 resolution 800x600
xwayland disable
set $mod Mod4
floating_modifier $mod normal
bindsym --release Super_L exec echo launcher >> {fired}
bindsym $mod+Return exec echo terminal >> {fired}
bindsym $mod+1 exec echo workspace >> {fired}
bindsym $mod+Shift+q exec echo close >> {fired}
bindsym $mod+space exec echo search >> {fired}
""")
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "DBUS_SESSION_BUS_ADDRESS")}
    env.update(XDG_RUNTIME_DIR=str(run), WLR_BACKENDS="headless", WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="1",
               WLR_LIBINPUT_NO_DEVICES="1")
    sway = subprocess.Popen([a.sway, "-c", str(base / "config")], env=env, stdout=open(base / "log", "w"),
                            stderr=subprocess.STDOUT)
    results = []
    try:
        time.sleep(2)
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))

        def keys(*steps):
            subprocess.run([sys.executable, str(KEYS), *steps], env=env, capture_output=True, timeout=20)

        def with_mouse(*mouse):
            """Win held while the mouse does something, then Win let go."""
            kb = subprocess.Popen([sys.executable, str(KEYS), "down:super", "wait:2.5", "up:super"], env=env,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.8)
            subprocess.Popen([sys.executable, str(MOUSE), *mouse, "--width", "800", "--height", "600", "--hold", "3"],
                             env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            kb.wait(20)

        cases = [("Win alone", lambda: keys("tap:super"), ["launcher"]),
                 ("Win held a second, then let go", lambda: keys("down:super", "wait:1", "up:super"), ["launcher"]),
                 ("Win + Enter", lambda: keys("down:super", "tap:enter", "up:super"), ["terminal"]),
                 ("Win + 1", lambda: keys("down:super", "tap:1", "up:super"), ["workspace"]),
                 ("Win + Shift + Q", lambda: keys("down:super", "down:shift", "tap:q", "up:shift", "up:super"), ["close"]),
                 ("Win + Space", lambda: keys("down:super", "tap:space", "up:super"), ["search"]),
                 ("Win + a click", lambda: with_mouse("400", "300", "--click"), []),
                 ("Win + a drag (moving a window)", lambda: with_mouse("300", "300", "--drag", "500", "400"), [])]
        for name, press, want in cases:
            fired.write_text("")
            press()
            time.sleep(0.7)
            got = fired.read_text().split()
            ok = got == want
            results.append(ok)
            print(f"  {'ok  ' if ok else 'FAIL'}  {name:32} -> {', '.join(got) or 'nothing'}"
                  + ("" if ok else f" (wanted {', '.join(want) or 'nothing'})"), flush=True)
    finally:
        sway.terminate()
        sway.wait(10)
        subprocess.run(["rm", "-rf", "--one-file-system", str(base)])
    print(f"\nRESULT: {sum(results)}/{len(results)} passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
