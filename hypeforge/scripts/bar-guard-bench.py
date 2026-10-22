#!/usr/bin/env python3
"""The hidden bench for the bar guard (D-115, 2026-10-22; bench before live).

Javier's login on 10-22: Waybar crashed three seconds after it started and the screen stayed empty.
Three screen-less screens, the KDE style. Checks, in the failing direction first:
  - with NO guard, a crashed bar stays dead (so the checks below can see a failure at all);
  - with the guard, a crashed bar comes back on every screen, its last words kept with how it ended;
  - a bar the guard itself started is known by its exit status when it dies;
  - only one guard per session;
  - a `stop` is not a crash: nothing comes back, nothing is recorded;
  - a style switch's restart (the look engine) is not a crash either;
  - a bar that keeps dying is given up on after the limit, and stays down;
  - the guard ends with Sway;
  - and the REAL desktop's bar is never touched (same process numbers at the end).

    bar-guard-bench.py      exit 0 when every check passes
"""
from __future__ import annotations

import json, os, signal, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/panels"))
import panelkit  # noqa: E402

BAR = HERE / "applets/bar/hypeforge-bar"
MAGENTA = b"\xff\x00\xff"


def main() -> int:
    ht = panelkit.theme_tool()
    real_before = subprocess.run(["pgrep", "-x", "waybar"], capture_output=True, text=True).stdout.split()
    base = Path(tempfile.mkdtemp(prefix="hfgb.", dir="/tmp"))
    run, conf, state = base / "r", base / "c", base / "s"
    run.mkdir(mode=0o700)
    (conf / "hypeforge/applets").mkdir(parents=True)
    real = Path.home() / ".config"
    for rel in ("hypeforge/applets/sections.toml", "hypeforge/bar/launcher.png"):
        if (real / rel).exists():
            (conf / rel).parent.mkdir(parents=True, exist_ok=True)
            (conf / rel).write_bytes((real / rel).read_bytes())
    place = ht.Place(conf)
    ht.apply("kde", "kognogos-mocha", place, reload=False, check_names=False, make_wallpaper=False, say=lambda *_: None)
    (base / "sway.conf").write_text("output * resolution 1280x720 bg #ff00ff solid_color\nxwayland disable\n")
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "DBUS_SESSION_BUS_ADDRESS", "HYPEFORGE_OUTPUT")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), XDG_STATE_HOME=str(state),
               XDG_DATA_HOME=str(conf / ".local-data"), WLR_BACKENDS="headless", WLR_RENDERER="pixman",
               WLR_HEADLESS_OUTPUTS="3", WLR_LIBINPUT_NO_DEVICES="1", GDK_BACKEND="wayland",
               HYPEFORGE_BAR_GUARD_EVERY="0.5", HYPEFORGE_BAR_GUARD_MAX="2", HYPEFORGE_BAR_GUARD_WINDOW="120")
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"] = bus[0]
    fakebin = base / "bin"; fakebin.mkdir()           # nothing here may ever reach the real bar
    for tool in ("pgrep", "pkill"):
        (fakebin / tool).write_text(f'#!/bin/sh\ncase "$*" in *waybar*) exit 1;; esac\nexec /usr/bin/{tool} "$@"\n')
        (fakebin / tool).chmod(0o755)
    (fakebin / "notify-send").write_text(f'#!/bin/sh\necho "$@" >> {base}/notices.log\n')   # the notices, read back
    (fakebin / "notify-send").chmod(0o755)
    env["PATH"] = f"{fakebin}:{os.environ['PATH']}"
    log = open(base / "bench.log", "w")
    crashes = state / "hypeforge/logs/bar-crashes"
    results = []

    def check(ok, what):
        results.append(bool(ok))
        print(("  ok    " if ok else "  FAIL  ") + what)

    sway = subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    guards = []
    try:
        time.sleep(2)
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        env["SWAYSOCK"] = next(str(p) for p in run.glob("sway-ipc.*.sock"))
        outs = sorted(json.loads(subprocess.run(["swaymsg", "-t", "get_outputs", "-r"], env=env,
                                                capture_output=True, text=True).stdout), key=lambda o: o["rect"]["x"])

        def bar_seen(o):
            r = o["rect"]
            p = base / "s.ppm"
            subprocess.run(["grim", "-t", "ppm", "-g", f"{r['x']},{r['y'] + r['height'] - 30} {r['width']}x1", str(p)],
                           env=env, check=True)
            row = p.read_bytes().split(b"\n", 3)[3]
            px = [row[i:i + 3] for i in range(0, len(row), 3)]
            return sum(p != MAGENTA for p in px) > len(px) * 0.5

        def bar_pid():
            try:
                return int(json.loads((run / "hypeforge-bar/pids.json").read_text())["pid"])
            except (OSError, ValueError, KeyError):
                return None

        def alive(pid):
            try:
                return Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")[0].endswith(b"waybar")
            except OSError:
                return False

        def records():
            return sorted(crashes.glob("*-waybar-*.log")) if crashes.is_dir() else []

        def back_after(old, wait=12):
            """A new bar, alive and on every screen, within `wait` seconds — or None."""
            end = time.time() + wait
            while time.time() < end:
                pid = bar_pid()
                if pid and pid != old and alive(pid) and all(bar_seen(o) for o in outs):
                    return pid
                time.sleep(0.5)
            return None

        def bar(*args):
            subprocess.run([sys.executable, str(BAR), *args], env=env, stdout=log, stderr=log, timeout=30)

        def start_guard():
            g = subprocess.Popen([sys.executable, str(BAR), "guard"], env=env, stdout=open(base / "guard.log", "a"),
                                 stderr=subprocess.STDOUT)
            guards.append(g)
            return g

        # 1 · the failing direction: no guard, a crash leaves no bar
        bar("start")
        time.sleep(4)
        first = bar_pid()
        check(alive(first) and all(bar_seen(o) for o in outs), "the bar runs on every screen (the setup took effect)")
        os.kill(first, signal.SIGSEGV)
        check(back_after(first, wait=5) is None, "with NO guard, a crashed bar stays dead (the check can fail)")

        # 2 · the guard brings it back, and keeps its last words
        bar("start")
        time.sleep(4)
        second = bar_pid()
        g = start_guard()
        time.sleep(1.5)
        os.kill(second, signal.SIGSEGV)
        third = back_after(second, wait=15)
        check(third is not None, "with the guard, a crashed bar comes back on every screen")
        rec = records()
        text = rec[-1].read_text() if rec else ""
        check(len(rec) == 1 and f"process {second}" in text and "what it said" in text,
              f"its last words are kept, with when it died ({rec[-1].name if rec else 'none'})")
        print("        how: " + next((l for l in text.splitlines() if l.startswith("How:")), "(none)"))
        check((run / "hypeforge-bar/waybar.log.prev").exists(), "the run before stays readable too (waybar.log.prev)")
        notices = (base / "notices.log").read_text() if (base / "notices.log").exists() else ""
        check("The bar came back" in notices, "a notice says the bar came back")

        # 3 · a bar the guard started: its exit status is known
        time.sleep(1.5)
        os.kill(third, signal.SIGSEGV)
        fourth = back_after(third, wait=15)
        rec = records()
        how = next((l for l in rec[-1].read_text().splitlines() if l.startswith("How:")), "") if rec else ""
        check(fourth is not None and "SIGSEGV" in how, f"the guard's own bar: back again, and how it ended is known ({how})")

        # 4 · one guard per session
        second_guard = subprocess.run([sys.executable, str(BAR), "guard"], env=env, capture_output=True, text=True, timeout=10)
        check("already guarding" in second_guard.stdout, "a second guard sees the first and leaves")

        # 5 · a stop is not a crash
        before = len(records())
        bar("stop")
        time.sleep(4)
        check(bar_pid() is None and not alive(fourth) and len(records()) == before,
              "a stop stays stopped: nothing comes back, nothing is recorded")

        # 6 · a style switch's restart (the look engine, D-115's note) is not a crash
        bar("start")
        time.sleep(4)
        before, prev = len(records()), bar_pid()
        # in its own process, which knows only the hidden desktop: a reload here must never reach the real one
        switch = ("import sys; sys.path.insert(0, %r); import panelkit; ht = panelkit.theme_tool(); "
                  "ht.apply('classic', 'kognogos-mocha', ht.Place(), reload=True, check_names=False, "
                  "make_wallpaper=False, say=print)") % str(HERE / "applets/panels")
        subprocess.run([sys.executable, "-c", switch], env=env, stdout=log, stderr=log, timeout=60)
        time.sleep(6)
        now = bar_pid()
        check(now and now != prev and alive(now) and len(records()) == before,
              "a style switch restarts the bar without a crash record")

        # 7 · a bar that keeps dying is given up on (limit 2 here)
        for _ in range(3):
            pid = bar_pid()
            if pid and alive(pid):
                os.kill(pid, signal.SIGKILL)
            time.sleep(6)
        pid = bar_pid()
        time.sleep(3)
        gl = (base / "guard.log").read_text()
        check(not (pid and alive(pid)) and "so it stays down" in gl,
              "a bar that keeps dying is given up on, and stays down")
        notices = (base / "notices.log").read_text()
        check("The bar keeps stopping" in notices, "with a notice that says so")

        # 8 · the guard ends with Sway
        sway.terminate()
        sway.wait(timeout=10)
        try:
            g.wait(timeout=10)
            ended = True
        except subprocess.TimeoutExpired:
            ended = False
        check(ended, "the guard ends with Sway")
    finally:
        for p in guards:
            if p.poll() is None:
                p.terminate()
        subprocess.run([sys.executable, str(BAR), "stop"], env=env, capture_output=True)
        if sway.poll() is None:
            sway.terminate()
        os.kill(int(bus[1]), signal.SIGTERM)
    real_after = subprocess.run(["pgrep", "-x", "waybar"], capture_output=True, text=True).stdout.split()
    check(real_before == real_after, f"the real desktop's bar untouched ({' '.join(real_before) or 'none'})")
    print(f"\nRESULT: {sum(results)}/{len(results)} passed" + ("" if all(results) else f"; see {base}"))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
