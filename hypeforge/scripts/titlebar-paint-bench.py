#!/usr/bin/env python3
"""Is a floating window's title bar painted edge to edge? (hypeForge's Sway build, patch 4, 2026-10-27.)

Javier: "there is like a transparent border inside the top of the window". Our title bar buttons (patch 1)
cut the title bar's background into more pieces than Sway makes, and the extra pieces were never drawn: a
see-through strip under the title bar and right of the close button. This starts a hidden Sway (one screen,
a magenta background), floats a stand-in window with the real button symbols, and counts magenta pixels
inside its title bar. Any is a failure. Nothing touches the real desktop.

    titlebar-paint-bench.py [--sway PATH]       default: hypeForge's build (~/.local/opt/sway-hypeforge/current)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
MAGENTA = (255, 0, 255)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sway", default=str(Path.home() / ".local/opt/sway-hypeforge/current/bin/sway"))
    a = ap.parse_args()
    from PIL import Image
    results = []
    for label, buttons in (("buttons on", True), ("buttons off", False)):
        base = Path(tempfile.mkdtemp(prefix="hftbp.", dir="/tmp"))     # short: Sway's socket path must fit
        run = base / "r"
        run.mkdir(mode=0o700)
        conf = ("output HEADLESS-1 resolution 800x600 bg #ff00ff solid_color\nxwayland disable\n"
                "default_floating_border normal 2\ntitlebar_padding 6 4\nfont pango:JetBrainsMono Nerd Font 10.5\n"
                "client.focused #bebebe #353535 #ffffff #bebebe #bebebe\n"
                'for_window [app_id="hf-paint"] floating enable, resize set 400 300, move position 100 100\n')
        if buttons:   # the symbols the desktop uses (sway/config-buttons)
            conf += ("titlebar_buttons floating\ntitlebar_button minimize \U000f05b0 move scratchpad\n"
                     "titlebar_button maximize \U000f05af fullscreen toggle\ntitlebar_button close \U000f05ad kill\n")
        (base / "config").write_text(conf)
        env = {k: v for k, v in os.environ.items()
               if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "DBUS_SESSION_BUS_ADDRESS")}
        env.update(XDG_RUNTIME_DIR=str(run), WLR_BACKENDS="headless", WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="1",
                   WLR_LIBINPUT_NO_DEVICES="1", GDK_BACKEND="wayland")
        log = open(base / "log", "w")
        sway = subprocess.Popen([a.sway, "-c", str(base / "config")], env=env, stdout=log, stderr=log)
        try:
            time.sleep(2)
            env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
            env["SWAYSOCK"] = next(str(p) for p in run.glob("sway-ipc.*.sock"))
            win = subprocess.Popen([sys.executable, str(HERE / "scripts/fake-window.py"), "hf-paint", "plain"],
                                   env=env, stdout=log, stderr=log)
            time.sleep(2.5)
            tree = json.loads(subprocess.run(["swaymsg", "-t", "get_tree", "-r"], env=env, capture_output=True,
                                             text=True).stdout)

            def walk(n):
                for k in ("nodes", "floating_nodes"):
                    for c in n.get(k, []):
                        yield c
                        yield from walk(c)
            con = next(c for c in walk(tree) if c.get("app_id") == "hf-paint")
            r = con["rect"]
            subprocess.run(["grim", str(base / "shot.png")], env=env, check=True)
            im = Image.open(base / "shot.png").convert("RGB")
            # the title bar: a floating window's sits right above its rect, deco_rect high (Sway's IPC)
            top, bottom = r["y"] - (con.get("deco_rect") or {}).get("height", 0), r["y"]
            if bottom <= top:
                print(f"  FAIL  {label}: no title bar found ({r}, {con.get('deco_rect')})")
                results.append(False)
                continue
            box = (r["x"] + 2, top + 1, r["x"] + r["width"] - 2, bottom)
            holes = sum(1 for x in range(box[0], box[2]) for y in range(box[1], box[3]) if im.getpixel((x, y)) == MAGENTA)
            ok = holes == 0
            results.append(ok)
            print(f"  {'ok  ' if ok else 'FAIL'}  {label}: {holes} see-through pixel(s) in the title bar {box}", flush=True)
            win.terminate()
        finally:
            sway.terminate()
            sway.wait(10)
            subprocess.run(["rm", "-rf", "--one-file-system", str(base)])
    print(f"\nRESULT: {sum(results)}/{len(results)} passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
