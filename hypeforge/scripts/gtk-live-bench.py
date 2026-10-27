#!/usr/bin/env python3
"""The hidden bench for a colour switch reaching apps that are ALREADY open (Javier, 2026-10-11:
"Google Chrome that is already opened, when I switch theme colors, the window stays with the same
color when I opened it").

A screen-less Sway with its own message bus and its own settings store (nothing reaches the real
desktop's GTK settings, the real Chrome or the real bar). A throwaway Chrome (its own profile, the
GTK look, as Javier's) is opened once, then the colours are switched under it with
`hypeforge-theme apply`. After each switch, the colour of Chrome's tab strip (the frame, which
Chrome takes from GTK's title-bar colour) must be the new theme's title-bar colour.

    python3 scripts/gtk-live-bench.py [--keep]
"""
from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
TOOL = REPO / "applets/theme/hypeforge-theme"
CHROME = shutil.which("google-chrome-stable") or shutil.which("chromium")
# dark → dark (the GTK name stayed the same before the fix), dark → light, light → dark
STEPS = ["dark-red", "light-blue", "dark-green", "kognogos-mocha"]


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def far(a, b) -> int:
    return max(abs(x - y) for x, y in zip(a, b))


def main() -> int:
    if not CHROME:
        print("no Chrome or Chromium installed — nothing to bench")
        return 1
    base = Path(tempfile.mkdtemp(prefix="gtkbench.", dir="/tmp"))
    run, conf, data, prof = base / "r", base / "c", base / "d", base / "chrome"
    run.mkdir(mode=0o700)
    for d in (conf, data, prof / "Default"):
        d.mkdir(parents=True)
    # Chrome's own setting "use the GTK look" (Javier's Chrome has it: extensions.theme.system_theme = 1)
    (prof / "Default/Preferences").write_text(json.dumps({"extensions": {"theme": {"system_theme": 1}},
                                                          "browser": {"has_seen_welcome_page": True}}))
    wall = base / "w.png"
    from PIL import Image
    Image.new("RGB", (32, 32), (40, 40, 40)).save(wall)
    (conf / "hypeforge/theme").mkdir(parents=True)
    (conf / "hypeforge/theme/state.toml").write_text(f'wallpaper = "{wall}"\n')
    (base / "sway.conf").write_text("output * resolution 1280x720\nxwayland disable\ndefault_border none\n"
                                    f"include {conf}/hypeforge/theme/sway.conf\n")
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK", "DBUS_SESSION_BUS_ADDRESS")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), XDG_DATA_HOME=str(data),
               XDG_STATE_HOME=str(base / "s"), XDG_CACHE_HOME=str(base / "cache"),
               WLR_BACKENDS="headless", WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="1",
               WLR_LIBINPUT_NO_DEVICES="1", GSETTINGS_BACKEND="dconf")
    fakebin = base / "bin"
    fakebin.mkdir()                      # the look's bar signals must never reach the real bar
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

    def apply(theme, reload=True):
        cmd = [str(TOOL), "apply", "rice", theme] + ([] if reload else ["--no-reload"])
        return subprocess.run(cmd, env=env, stdout=log, stderr=log).returncode == 0

    def header_colour() -> tuple[int, int, int]:
        css = (conf / "gtk-3.0/gtk.css").read_text()
        name = re.search(r"^gtk-theme-name=(.+)$", (conf / "gtk-3.0/settings.ini").read_text(), re.M).group(1)
        own = data / "themes" / name / "gtk-3.0/gtk.css"
        if own.is_file():
            css += own.read_text()
        found = re.findall(r"@define-color headerbar_bg_color (#[0-9a-fA-F]{6});", css)
        return hex_rgb(found[-1])

    def strip_colour() -> tuple[int, int, int]:
        p = base / "px.ppm"
        subprocess.run(["grim", "-t", "ppm", "-g", "1000,24 1x1", str(p)], env=env, check=True)
        d = p.read_bytes().split(b"\n", 3)[3]
        return d[0], d[1], d[2]

    apply("kognogos-mocha", reload=False)
    sway = subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    chrome = None
    try:
        for _ in range(100):
            socks = list(run.glob("sway-ipc.*.sock"))
            if socks:
                break
            time.sleep(0.1)
        env["SWAYSOCK"] = str(socks[0])
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        apply("kognogos-mocha")           # the settings store gets the first look's names
        chrome = subprocess.Popen([CHROME, f"--user-data-dir={prof}", "--ozone-platform=wayland", "--no-first-run",
                                   "--no-default-browser-check", "--disable-gpu", "--password-store=basic",
                                   "--disable-sync", "--disable-features=Translate", "about:blank"],
                                  env=env, stdout=log, stderr=log, start_new_session=True)
        time.sleep(8)
        first = strip_colour()
        check(far(first, header_colour()) <= 10,
              f"Chrome opens in KognogOS Mocha's colours (strip {first}, title bar {header_colour()})")
        before = first
        for theme in STEPS:
            apply(theme)
            time.sleep(4)
            now, want = strip_colour(), header_colour()
            check(far(now, want) <= 10 and (far(want, before) <= 10 or now != before),
                  f"→ {theme}: the open Chrome follows (strip {now}, title bar {want})")
            before = now
        subprocess.run(["grim", "-s", "0.5", str(base / "last.png")], env=env)
    finally:
        if chrome is not None:
            try:
                os.killpg(chrome.pid, signal.SIGTERM)     # its own process group, saved at launch
                chrome.wait(10)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(chrome.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        sway.terminate()
        try:
            sway.wait(5)
        except subprocess.TimeoutExpired:
            sway.kill()
        try:
            os.kill(int(bus[1]), signal.SIGTERM)
        except (OSError, ValueError, IndexError):
            pass
        log.close()
    print(f"\nRESULT: {sum(results)}/{len(results)} passed")
    print(f"pictures and log: {base}")
    if "--keep" not in sys.argv and all(results):
        shutil.rmtree(base, ignore_errors=True)
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
