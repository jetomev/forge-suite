#!/usr/bin/env python3
"""The hidden bench for Alt + Tab and the tucked windows' way back (Javier, 2026-10-11): a screen-less
Sway with the real key bindings, the real Tuck applet and three windows plus a floating one. Keys come
from scripts/fake-keyboard.py (a virtual keyboard: Sway's bindings fire and the switcher gets the
keyboard, as from a real one). Each check is on which window ends up in front.

    switcher-bench.py [--keep]        exit 0 when every check passes
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
PANEL = HERE / "applets/panels/hypeforge-panel"
KEYS = HERE / "scripts/fake-keyboard.py"
WINDOW = ("import gi, sys; gi.require_version('Gtk','3.0'); from gi.repository import Gtk, GLib; "
          "GLib.set_prgname(sys.argv[1]); w=Gtk.Window(); w.set_title(sys.argv[1]); w.show_all(); "
          "GLib.timeout_add_seconds(120, Gtk.main_quit); Gtk.main()")


def main() -> int:
    base = Path(tempfile.mkdtemp(prefix="hfsw.", dir="/tmp"))
    run, conf = base / "r", base / "c"
    run.mkdir(mode=0o700)
    conf.mkdir()
    (base / "sway.conf").write_text(
        "output HEADLESS-1 resolution 1920x1080\nxwayland disable\nfocus_follows_mouse no\n"
        'for_window [app_id="floaty"] floating enable, resize set 800 500, move position center\n'
        f"bindsym Mod1+Tab exec {PANEL} switcher --hold\n"
        f"bindsym Mod1+Shift+Tab exec {PANEL} switcher --hold --back\n")
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK", "DBUS_SESSION_BUS_ADDRESS", "HYPEFORGE_OUTPUT")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), XDG_DATA_HOME=str(conf / ".local-data"),
               WLR_BACKENDS="headless", WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="1",
               WLR_LIBINPUT_NO_DEVICES="1", GDK_BACKEND="wayland")
    fakebin = base / "bin"
    fakebin.mkdir()                      # the tucked icon's redraw must never reach the real bar
    for tool in ("pgrep", "pkill"):
        (fakebin / tool).write_text(f'#!/bin/sh\ncase "$*" in *waybar*) exit 1;; esac\nexec /usr/bin/{tool} "$@"\n')
        (fakebin / tool).chmod(0o755)
    env["PATH"] = f"{fakebin}:{os.environ['PATH']}"
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"] = bus[0]
    log = open(base / "bench.log", "w")
    procs, results = [], []

    def check(ok, what):
        results.append(bool(ok))
        print(("  ok    " if ok else "  FAIL  ") + what, flush=True)

    subprocess.run([str(HERE / "applets/theme/hypeforge-theme"), "apply", "rice", "kognogos-mocha", "--no-reload",
                    "--wallpaper", str(HERE / "assets/lock/kognogos-mocha-blurred.jpg")],
                   env=env, stdout=log, stderr=log)
    sway = subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    try:
        for _ in range(100):
            socks = list(run.glob("sway-ipc.*.sock"))
            if socks:
                break
            time.sleep(0.1)
        env["SWAYSOCK"] = str(socks[0])
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))

        def msg(cmd):
            subprocess.run(["swaymsg", cmd], env=env, capture_output=True)

        def tree():
            return json.loads(subprocess.run(["swaymsg", "-t", "get_tree", "-r"], env=env,
                                             capture_output=True, text=True).stdout)

        def front() -> str | None:
            def walk(n):
                if n.get("focused") and n.get("app_id"):
                    return n["app_id"]
                for c in n.get("nodes", []) + n.get("floating_nodes", []):
                    r = walk(c)
                    if r:
                        return r
            return walk(tree())

        def tucked_ids() -> list[str]:
            out = []

            def walk(n, ws=None):
                if n.get("type") == "workspace":
                    ws = n.get("name")
                if n.get("app_id") and ws == "__i3_scratch":
                    out.append(n["app_id"])
                for c in n.get("nodes", []) + n.get("floating_nodes", []):
                    walk(c, ws)
            walk(tree())
            return out

        def keys(*steps):
            subprocess.run([sys.executable, str(KEYS), *steps], env=env, stdout=log, stderr=log, timeout=30)
            time.sleep(1.0)

        def switcher_open() -> bool:
            try:
                return Path(f"/proc/{int((run / 'hypeforge-panel-switcher.pid').read_text())}").exists()
            except (OSError, ValueError):
                return False

        def bar_piece() -> dict:
            try:
                return json.loads((run / "hypeforge-tucked.json").read_text())
            except (OSError, ValueError):
                return {}

        procs.append(subprocess.Popen([sys.executable, str(HERE / "applets/tuck/hypeforge-tuck")], env=env,
                                      stdout=log, stderr=log))
        for app in ("one", "two", "three"):
            procs.append(subprocess.Popen([sys.executable, "-c", WINDOW, app], env=env, stdout=log, stderr=log))
            time.sleep(1.2)
        for app in ("one", "two", "three"):          # used in this order: three is in front
            msg(f'[app_id="{app}"] focus')
            time.sleep(0.4)
        check(front() == "three", f"three windows open, three in front ({front()})")
        check(bar_piece().get("text") == "", "the tucked icon hides: nothing tucked away")

        print("1 · a quick Alt + Tab: the window used before")
        keys("down:alt", "tap:tab", "up:alt")
        check(front() == "two", f"in front: two ({front()})")
        check(not switcher_open(), "the switcher closed")

        print("2 · hold Alt, Tab twice, let go: two windows back")
        keys("down:alt", "tap:tab", "wait:1.5", "tap:tab", "wait:0.5", "up:alt")
        check(front() == "one", f"in front: one ({front()})")      # order was two, three, one
        check(not switcher_open(), "the switcher closed")

        print("3 · Alt + Shift + Tab: from the end")
        keys("down:alt", "down:shift", "tap:tab", "wait:1.2", "up:shift", "up:alt")
        check(front() == "three", f"in front: three ({front()})")  # order was one, two, three

        print("4 · Escape: nothing changes")
        keys("down:alt", "tap:tab", "wait:1.2", "tap:esc", "wait:0.3", "up:alt")
        check(front() == "three" and not switcher_open(), f"still three, switcher closed ({front()})")

        print("5 · a floating window tucked away, and back with Alt + Tab")
        procs.append(subprocess.Popen([sys.executable, "-c", WINDOW, "floaty"], env=env, stdout=log, stderr=log))
        time.sleep(1.5)
        msg('[app_id="floaty"] focus')
        time.sleep(0.4)
        msg('[app_id="three"] focus')                # a click on what it covers: the Tuck applet tucks it
        time.sleep(1.0)
        check(tucked_ids() == ["floaty"], f"floaty tucked away ({tucked_ids()})")
        piece = bar_piece()
        check(piece.get("class") == "some" and piece.get("text", "").endswith(" 1"),
              f"the tucked icon shows 1 ({piece.get('text')!r})")
        keys("down:alt", "tap:tab", "up:alt")        # floaty was used just before three
        check(front() == "floaty" and not tucked_ids(), f"floaty back on top ({front()}, tucked {tucked_ids()})")
        check(bar_piece().get("text") == "", "the tucked icon hides again")

        print("6 · the bar icon's click brings a tucked window back")
        msg('[app_id="floaty"] move scratchpad')
        time.sleep(0.8)
        subprocess.run([str(HERE / "applets/tuck/hypeforge-tuck"), "back"], env=env, stdout=log, stderr=log)
        time.sleep(0.8)
        check(front() == "floaty" and not tucked_ids(), f"floaty back on top ({front()})")

        msg(f"exec {PANEL} switcher")                  # a picture of the cards, for a person to look at
        time.sleep(2.0)
        subprocess.run(["grim", str(base / "switcher.png")], env=env)
        keys("tap:esc")

        print("7 · several tucked: the click shows the cards with just those")
        procs.append(subprocess.Popen([sys.executable, "-c", WINDOW, "floaty"], env=env, stdout=log, stderr=log))
        time.sleep(1.5)
        msg('[app_id="floaty"] move scratchpad, [app_id="floaty"] move scratchpad')
        time.sleep(0.8)
        n = len(tucked_ids())
        subprocess.run([str(HERE / "applets/tuck/hypeforge-tuck"), "back"], env=env, stdout=log, stderr=log)
        time.sleep(2.0)
        check(n == 2 and switcher_open(), f"{n} tucked, the cards open")
        keys("tap:enter")
        check(front() == "floaty" and len(tucked_ids()) == 1 and not switcher_open(),
              f"Enter brought one back ({front()}, {len(tucked_ids())} still tucked)")
        subprocess.run(["grim", "-s", "0.5", str(base / "last.png")], env=env)
    finally:
        for p in procs:
            if p.poll() is None:
                p.send_signal(signal.SIGTERM)
        for p in procs:
            try:
                p.wait(5)
            except subprocess.TimeoutExpired:
                p.kill()
        try:
            pid = int((run / "hypeforge-panel-switcher.pid").read_text())
            if b"hypeforge-panel" in Path(f"/proc/{pid}/cmdline").read_bytes():
                os.kill(pid, signal.SIGTERM)
        except (OSError, ValueError):
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
