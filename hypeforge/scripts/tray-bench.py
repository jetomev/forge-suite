#!/usr/bin/env python3
"""The hidden bench for hypeForge's tray (2026-10-17; bench before live). Three fake screens on their own
Sway, their own message bus, the Rice (top bar, the menu centred under it) and KDE (bottom bar): hypeForge's
tray takes the watcher, two stand-in tray apps register (one with a named icon, one sending pixels like
Claude), the bar is started by hypeforge-bar, then:

  - the watcher is ours and lists both apps; the slots hold a picture for each
  - the bar's config has our tray group in Waybar's place, its click carrying the bar's pop-up place
  - a click on screen 3's tray icon opens the app's menu there and nowhere else; the same click closes it
  - an entry picked reaches the app as its own "clicked"
  - an app that quits leaves the bar
  - one-colour icons are repainted in the style's tray colour; a coloured one keeps its own (2026-10-17)
  - a restart (`run --replace`) never leaves the tray without an owner, the old tray ends by itself, and
    an app that registers only once (like Dropbox) is still there after it
  - the real desktop's bar and tray are untouched

    tray-bench.py [--keep]     (--keep leaves the bench folder and its pictures)

Writes logs/tray-bench-<style>.png (screen 3 with the menu open) for a look.
"""

from __future__ import annotations

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
TRAY = HERE / "applets/tray/hypeforge-tray"
FAKE = HERE / "scripts/fake-tray-app.py"
MAGENTA = b"\xff\x00\xff"


def new_owners(log: str) -> list[str]:
    """From dbus-monitor's log: the new owner of each change of the watcher's name ("" = no owner: a gap)."""
    out = []
    for block in log.split("signal ")[1:]:
        if "member=NameOwnerChanged" in block:
            strings = [l.split('"')[1] if '"' in l else "" for l in block.splitlines() if l.strip().startswith("string")]
            if len(strings) == 3:
                out.append(strings[2])
    return out


def main() -> int:
    keep = "--keep" in sys.argv
    ht = panelkit.theme_tool()
    real_bars = subprocess.run(["pgrep", "-x", "waybar"], capture_output=True, text=True).stdout.split()
    real_tray = subprocess.run(["busctl", "--user", "status", "org.kde.StatusNotifierWatcher"],
                               capture_output=True, text=True).stdout.split("\n")[0]
    base = Path(tempfile.mkdtemp(prefix="hftray.", dir="/tmp"))
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
    place = ht.Place(conf)
    (base / "sway.conf").write_text("output * resolution 1280x720 bg #ff00ff solid_color\nxwayland disable\n")
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "DBUS_SESSION_BUS_ADDRESS", "HYPEFORGE_OUTPUT",
                        "HYPEFORGE_TRAY_SLOTS", "HYPEFORGE_WAYBAR_TRAY")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), XDG_DATA_HOME=str(conf / ".local-data"),
               WLR_BACKENDS="headless", WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="3", WLR_LIBINPUT_NO_DEVICES="1",
               GDK_BACKEND="wayland")
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"] = bus[0]
    fakebin = base / "bin"; fakebin.mkdir()             # redraw signals must never reach the real bar
    for tool in ("pgrep", "pkill"):
        (fakebin / tool).write_text(f'#!/bin/sh\ncase "$*" in *waybar*) exit 1;; esac\nexec /usr/bin/{tool} "$@"\n')
        (fakebin / tool).chmod(0o755)
    env["PATH"] = f"{fakebin}:{os.environ['PATH']}"
    log = open(base / "bench.log", "w")
    results = []

    def check(ok, what):
        results.append(bool(ok))
        print(("  ok    " if ok else "  FAIL  ") + what, flush=True)

    sway = subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    procs = []
    clicks = base / "clicks.txt"
    try:
        time.sleep(2)
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        env["SWAYSOCK"] = next(str(p) for p in run.glob("sway-ipc.*.sock"))
        outs = sorted(json.loads(subprocess.run(["swaymsg", "-t", "get_outputs", "-r"], env=env,
                                                capture_output=True, text=True).stdout), key=lambda o: o["rect"]["x"])

        def shot(o, y=None, h=None, path=None):
            r = o["rect"]
            y = r["y"] if y is None else y
            p = path or base / "s.ppm"
            subprocess.run(["grim", "-t", "ppm" if path is None else "png", "-g", f"{r['x']},{y} {r['width']}x{h or r['height']}",
                            str(p)], env=env, check=True)
            return p.read_bytes().split(b"\n", 3)[3] if path is None else None

        def call(*args, timeout=10):
            return subprocess.run(list(args), env=env, capture_output=True, text=True, timeout=timeout)

        # an app already up that never registers (Insync, 10-17), then the tray, then two apps that do: a named
        # icon (Dropbox's menu shape), and pixels (like Claude)
        shy = subprocess.Popen([sys.executable, str(FAKE), "--id", "insync-fake", "--title", "Shy App", "--never-register"],
                               env=env, stdout=log, stderr=log)
        procs.append(shy)
        time.sleep(1)
        procs.append(subprocess.Popen([sys.executable, str(TRAY), "run"], env=env, stdout=log, stderr=log))
        time.sleep(1.2)
        dropbox = subprocess.Popen([sys.executable, str(FAKE), "--clicks", str(clicks), "--icon", "folder"],
                                   env=env, stdout=log, stderr=log)
        procs.append(dropbox)
        pixels = subprocess.Popen([sys.executable, str(FAKE), "--id", "electron-fake", "--title", "Pixel App", "--pixmap"],
                                  env=env, stdout=log, stderr=log)
        procs.append(pixels)
        white = subprocess.Popen([sys.executable, str(FAKE), "--id", "white-fake", "--title", "White App", "--white"],
                                 env=env, stdout=log, stderr=log)
        procs.append(white)
        once = subprocess.Popen([sys.executable, str(FAKE), "--id", "once-fake", "--title", "Once App", "--once"],
                                env=env, stdout=log, stderr=log)
        procs.append(once)
        time.sleep(2.5)

        owner = call("busctl", "--user", "status", "org.kde.StatusNotifierWatcher").stdout
        items = call("busctl", "--user", "get-property", "org.kde.StatusNotifierWatcher", "/StatusNotifierWatcher",
                     "org.kde.StatusNotifierWatcher", "RegisteredStatusNotifierItems").stdout
        check("hypeforge-tray" in owner and items.startswith("as 5"),
              f"the watcher is hypeForge's tray and lists all five apps ({items.strip()[:60]})")
        slots = json.loads((run / "hypeforge-tray/slots.json").read_text())
        check(any(s["id"] == "insync-fake" for s in slots), "the app that never registered was taken in anyway")
        check(len(slots) == 5 and all(s.get("picture") and Path(s["picture"]).is_file() for s in slots),
              f"a picture for each: {[Path(s.get('picture') or '-').name for s in slots]}")
        px = next((s for s in slots if s["id"] == "electron-fake"), {})
        check(Path(px.get("picture", "")).name.startswith("slot-") and Path(px["picture"]).is_file(),
              "the pixel app's picture made from its pixels")
        n_drop = str(next(i for i, s in enumerate(slots, 1) if s["id"].startswith("dropbox")))
        out = call(sys.executable, str(TRAY), "icon", n_drop).stdout.splitlines()
        check(len(out) == 2 and Path(out[0]).is_file() and "Dropbox" in out[1], f"the bar's piece {n_drop} gets a path and one tooltip line: {out}")
        check(call(sys.executable, str(TRAY), "icon", "9").stdout == "", "an empty piece gets nothing (the bar hides it)")

        for style in ("rice", "kde"):
            ht.apply(style, "kognogos-mocha", place, reload=False, check_names=False, make_wallpaper=False, say=lambda *_: None)
            call(sys.executable, str(BAR), "stop")
            call(sys.executable, str(BAR), "start", timeout=30)
            time.sleep(4)
            bars = json.loads((run / "hypeforge-bar/config.json").read_text())
            mods = json.dumps([b.get("modules-left", []) + b.get("modules-center", []) + b.get("modules-right", []) for b in bars])
            check('"group/tray"' in mods and '"tray"' not in mods, f"{style}: our tray group in Waybar's tray's place")
            third = outs[2]["name"]
            click = next(b for b in bars if b["output"] == third)[f"image#tray-{n_drop}"]["on-click"]
            check("--edges" in click and f"HYPEFORGE_OUTPUT={third};" in click, f"{style}: the click carries the bar's pop-up place and its screen")
            # the screen's middle only: the bar itself redraws (a theme applied repaints the tray's icons)
            mid = lambda o: shot(o, o["rect"]["y"] + 70, o["rect"]["height"] - 140)
            before = [mid(o) for o in outs]
            procs.append(subprocess.Popen(["sh", "-c", click], env=env, stdout=log, stderr=log))
            time.sleep(3)
            changed = [sum(a != b for a, b in zip(x, mid(o))) for x, o in zip(before, outs)]
            check(changed[2] > 10000 and changed[0] < 1000 and changed[1] < 1000,
                  f"{style}: screen 3's click opens the menu on screen 3 only (changed bytes: {changed})")
            pic = HERE / "logs" / f"tray-bench-{style}.png"
            pic.parent.mkdir(exist_ok=True)
            shot(outs[2], path=pic)
            subprocess.run(["sh", "-c", click], env=env, stdout=log, stderr=log, timeout=10)   # the same click again
            time.sleep(1.5)
            after = sum(a != b for a, b in zip(before[2], mid(outs[2])))
            check(after < 1000, f"{style}: the same click again closes it (changed bytes: {after})")

        # an entry picked reaches the app (Pause Syncing is 237 in Dropbox's menu shape)
        sys.path.insert(0, str(HERE / "applets/tray"))
        import hfsni
        from gi.repository import Gio
        conn = Gio.DBusConnection.new_for_address_sync(env["DBUS_SESSION_BUS_ADDRESS"],
            Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT | Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION, None, None)
        s1 = next(s for s in json.loads((run / "hypeforge-tray/slots.json").read_text()) if s["id"].startswith("dropbox"))
        layout = hfsni.menu_layout(conn, s1["name"], s1["menu"])
        hfsni.menu_click(conn, s1["name"], s1["menu"], 237)
        time.sleep(0.5)
        check(len(layout) == 19 and clicks.exists() and "237" in clicks.read_text(), "Pause Syncing picked: the app gets its own click")

        pixels.terminate()
        time.sleep(1.5)
        left = json.loads((run / "hypeforge-tray/slots.json").read_text())
        check(len(left) == 4 and not any(s["id"] == "electron-fake" for s in left), f"an app that quits leaves the bar ({len(left)} left)")

        # the icons in the style's tray colour (the last style applied: KDE)
        sys.path.insert(0, str(HERE / "applets/tray"))
        import hftint
        from PIL import Image
        want = hftint.theme_colour(conf / "hypeforge/theme/colors.css")
        w = next(s for s in left if s["id"] == "white-fake")
        px = [p for p in hftint.pixels(Image.open(w["picture"]).convert("RGBA")) if p[3] > 200]
        got = "#%02x%02x%02x" % px[0][:3] if px else None
        check(Path(w["picture"]).name.count("-") == 2 and got == want,
              f"a white icon is repainted in the style's tray colour ({got} = {want})")
        folder = next(s for s in left if s["id"].startswith("dropbox"))
        fpx = [p[:3] for p in hftint.pixels(Image.open(folder["picture"]).convert("RGBA")) if p[3] > 200]
        check(fpx and any("#%02x%02x%02x" % p != want for p in fpx), f"a coloured icon keeps its own colours ({Path(folder['own_picture']).name})")

        # a restart with no gap: watch the watcher's owner while a new tray takes over
        watch_log = base / "owner.txt"
        mon = subprocess.Popen(["dbus-monitor", "--session", "type='signal',member='NameOwnerChanged',"
                                "arg0='org.kde.StatusNotifierWatcher'"], env=env, stdout=open(watch_log, "w"), stderr=log)
        procs.append(mon)
        time.sleep(1)
        old_tray = procs[1]
        procs.append(subprocess.Popen([sys.executable, str(TRAY), "run", "--replace"], env=env, stdout=log, stderr=log))
        time.sleep(3)
        mon.terminate()
        news = new_owners(watch_log.read_text())
        check(len(news) >= 1 and all(news), f"the restart never left the tray without an owner (new owners: {news})")
        check(old_tray.poll() is not None, "the old tray ended by itself")
        items = call("busctl", "--user", "get-property", "org.kde.StatusNotifierWatcher", "/StatusNotifierWatcher",
                     "org.kde.StatusNotifierWatcher", "RegisteredStatusNotifierItems").stdout
        after = json.loads((run / "hypeforge-tray/slots.json").read_text())
        check(any(s["id"] == "once-fake" for s in after) and items.startswith("as 4"),
              f"an app that registers only once is still there ({[s['id'] for s in after]})")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        subprocess.run([sys.executable, str(BAR), "stop"], env=env, capture_output=True)
        sway.terminate()
        os.kill(int(bus[1]), signal.SIGTERM)
    check(subprocess.run(["pgrep", "-x", "waybar"], capture_output=True, text=True).stdout.split() == real_bars,
          f"the real desktop's bar untouched ({' '.join(real_bars) or 'none'})")
    check(subprocess.run(["busctl", "--user", "status", "org.kde.StatusNotifierWatcher"], capture_output=True,
                         text=True).stdout.split("\n")[0] == real_tray, "the real desktop's tray untouched")
    print(f"\nRESULT: {sum(results)}/{len(results)} passed" + ("" if all(results) else f"; see {base / 'bench.log'}"))
    if not keep and all(results):
        import shutil
        shutil.rmtree(base, ignore_errors=True)
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
