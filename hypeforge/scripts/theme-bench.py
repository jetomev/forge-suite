#!/usr/bin/env python3
"""The hidden bench for the look (hypeforge-theme, D-78 step 1) — before anything touches the
desktop. Everything happens in a throwaway home folder; the real desktop is never signalled.

  1. Every style × every theme is written, then each file is checked by the program that reads it:
     Sway (sway -C on the real, wired sway/config) and fuzzel (--check-config). Note: sway -C
     exits 0 even when an INCLUDED file has errors (found 10-10) — its error lines are read instead.
  2. Three looks run for real on a screen-less Sway with a private message bus: Sway takes the
     generated file, Waybar loads the bar's style, mako loads the notifications, GTK 3 and GTK 4
     parse their files and the lock screen's.
  3. A theme's wallpaper is made and the lock screen's copy blurred; undo puts every file back.
  4. Classic + KognogOS Mocha against today's files: what differs is listed (it should be only the
     tiny Mocha changes Javier approved, D-73 F-4).

    python3 scripts/theme-bench.py [--keep]
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
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
OWN_WALL = "/usr/share/wallpapers/kognog/Kognog OS Semi - Logo Catpuccin Mocha.png"
LIVE = [("sway/config", "sway/config"), ("sway/waybar/style.css", "sway/waybar/style.css"),
        ("sway/waybar/config.jsonc", "sway/waybar/config.jsonc"), ("sway/fuzzel/fuzzel.ini", "sway/fuzzel/fuzzel.ini"),
        ("sway/gtklock/style.css", "gtklock/style.css")]
RUN_LOOKS = [("classic", "kognogos-mocha"), ("rice", "ember"), ("windows-11", "white")]

loader = importlib.machinery.SourceFileLoader("hypeforge_theme", str(TOOL))
spec = importlib.util.spec_from_loader("hypeforge_theme", loader)
ht = importlib.util.module_from_spec(spec)
loader.exec_module(ht)

results: list[tuple[bool, str]] = []


def check(ok: bool, what: str):
    results.append((ok, what))
    print(("  ok    " if ok else "  FAIL  ") + what)


def home_for(base: Path) -> tuple[Path, dict]:
    home = base / "home"
    conf = home / ".config"
    for src, dest in LIVE:
        (conf / dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / src, conf / dest)
    (conf / "sway/outputs").write_text("# the bench's screens\n")
    (conf / "alacritty").mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path("~/.config/alacritty/alacritty.toml").expanduser(), conf / "alacritty/alacritty.toml")
    (conf / "hypeforge/applets").mkdir(parents=True, exist_ok=True)
    (conf / "hypeforge/applets/favourites.css").write_text("/* bench */\n")
    env = {k: v for k, v in os.environ.items() if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK", "DBUS_SESSION_BUS_ADDRESS")}
    env.update(HOME=str(home), XDG_CONFIG_HOME=str(conf), XDG_CACHE_HOME=str(home / ".cache"),
               WLR_BACKENDS="headless", WLR_RENDERER="pixman")   # sway -C without asking for the real screens
    return conf, env


def static_checks(conf: Path, env: dict):
    print("\n1 · every style × every theme, checked by the program that reads it")
    place = ht.Place(conf)
    sts, ths = list(ht.styles()), list(ht.themes())
    bad_sway, bad_fuzzel, n = [], [], 0
    for s in sts:
        for t in ths:
            ht.apply(s, t, place, wallpaper=OWN_WALL, reload=False)
            n += 1
            r = subprocess.run(["sway", "-C", "-c", str(conf / "sway/config")], env=env, capture_output=True, text=True)
            if r.returncode or "Error on line" in r.stderr or "Error(s) loading" in r.stderr:
                bad_sway.append(f"{s}/{t}: {r.stderr.strip()[-160:]}")
            r = subprocess.run(["fuzzel", "--check-config", "--config", str(conf / "sway/fuzzel/fuzzel.ini")], env=env, capture_output=True, text=True)
            if r.returncode:
                bad_fuzzel.append(f"{s}/{t}: {(r.stderr or r.stdout).strip()[-160:]}")
    check(not bad_sway, f"Sway accepts the wired config with all {n} looks" + (f" — {bad_sway[:2]}" if bad_sway else ""))
    check(not bad_fuzzel, f"fuzzel accepts the lists' look with all {n}" + (f" — {bad_fuzzel[:2]}" if bad_fuzzel else ""))
    import tomllib
    term = conf / "alacritty/themes/hypeForge-desktop.toml"
    try:
        tomllib.loads(term.read_text()); tomllib.loads((conf / "alacritty/alacritty.toml").read_text())
        ok = Path(tomllib.loads((conf / "alacritty/alacritty.toml").read_text())["general"]["import"][0]).expanduser() == term
    except Exception as e:
        ok = False
    check(ok, "the terminal's theme and Alacritty's settings read back, ours first in the imports")
    # the checks really check: a broken include must fail
    inc = conf / "hypeforge/theme/sway.conf"
    good = inc.read_text()
    inc.write_text(good + "\ngaps inner banana\n")
    r = subprocess.run(["sway", "-C", "-c", str(conf / "sway/config")], env=env, capture_output=True, text=True)
    check("Error on line" in r.stderr, "a broken generated file is caught by Sway's check (the check is real)")
    inc.write_text(good)


GTK_PARSE = r"""
import sys, gi
gi.require_version("Gtk", sys.argv[1])
from gi.repository import Gtk, Gio
errors = []
p = Gtk.CssProvider()
p.connect("parsing-error", lambda prov, section, err: errors.append(err.message))
for f in sys.argv[2:]:
    if sys.argv[1] == "3.0":
        p.load_from_path(f)
    else:
        p.load_from_file(Gio.File.new_for_path(f))
print("ERRORS:", errors if errors else "none")
"""


def runtime_checks(base: Path, conf: Path, env: dict):
    print("\n2 · three looks running on a screen-less Sway (private message bus)")
    run = base / "run"
    run.mkdir(mode=0o700)
    place = ht.Place(conf)
    for style, theme in RUN_LOOKS:
        ht.apply(style, theme, place, wallpaper=OWN_WALL, reload=False)
        cfg = base / f"sway-{style}.conf"
        cfg.write_text(f"output HEADLESS-1 resolution 1280x720\ninclude {conf}/hypeforge/theme/sway.conf\n")
        e = dict(env, XDG_RUNTIME_DIR=str(run), WLR_BACKENDS="headless", WLR_RENDERER="pixman",
                 WLR_HEADLESS_OUTPUTS="1", WLR_LIBINPUT_NO_DEVICES="1")
        log = open(base / f"{style}.log", "w")
        procs = []
        try:
            bus = subprocess.Popen(["dbus-daemon", "--session", "--nofork", "--print-address=1"], env=e,
                                   stdout=subprocess.PIPE, stderr=log, text=True)
            procs.append(bus)
            e["DBUS_SESSION_BUS_ADDRESS"] = bus.stdout.readline().strip()
            sway = subprocess.Popen(["sway", "--unsupported-gpu", "-c", str(cfg)], env=e, stdout=log, stderr=log)
            procs.append(sway)
            sock = None
            for _ in range(100):
                found = list(run.glob("sway-ipc.*.sock"))
                if found:
                    sock = str(found[0]); break
                time.sleep(0.1)
            if not sock:
                check(False, f"{style}/{theme}: the bench's Sway started"); continue
            e["SWAYSOCK"] = sock
            e["WAYLAND_DISPLAY"] = next((p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock")), "wayland-1")
            r = subprocess.run(["swaymsg", "-t", "get_config"], env=e, capture_output=True, text=True)
            check(r.returncode == 0, f"{style}/{theme}: Sway runs with the generated file")
            bar = base / f"bar-{style}.jsonc"
            bar.write_text('{"layer":"top","position":"top","modules-left":["clock"]}')
            wb = subprocess.Popen(["waybar", "-c", str(bar), "-s", str(conf / "sway/waybar/style.css")], env=e,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            procs.append(wb)
            time.sleep(2.5)
            alive = wb.poll() is None
            wb.send_signal(signal.SIGTERM)
            out = wb.communicate(timeout=5)[0]
            errs = [l for l in out.splitlines() if "[error]" in l or "css" in l.lower() and "error" in l.lower()]
            check(alive and not errs, f"{style}/{theme}: the bar loads its style" + (f" — {errs[:2]}" if errs else ""))
            mk = subprocess.Popen(["mako", "--config", str(conf / "mako/config")], env=e, stdout=log, stderr=subprocess.PIPE, text=True)
            procs.append(mk)
            time.sleep(1.5)
            ok = mk.poll() is None and subprocess.run(["makoctl", "reload"], env=e, capture_output=True).returncode == 0
            mk.send_signal(signal.SIGTERM)
            err = mk.communicate(timeout=5)[1]
            check(ok, f"{style}/{theme}: notifications load their look" + (f" — {err.strip()[-160:]}" if not ok else ""))
            for ver, files in (("3.0", [conf / "gtk-3.0/gtk.css", conf / "hypeforge/theme/colors.css", conf / "gtklock/style.css"]),
                               ("4.0", [conf / "gtk-4.0/gtk.css"])):
                r = subprocess.run([sys.executable, "-c", GTK_PARSE, ver, *map(str, files)], env=e, capture_output=True, text=True, timeout=30)
                line = next((l for l in r.stdout.splitlines() if l.startswith("ERRORS:")), r.stderr.strip()[-200:])
                check(line == "ERRORS: none", f"{style}/{theme}: GTK {ver[0]} reads its files" + ("" if line == "ERRORS: none" else f" — {line}"))
        finally:
            for p in reversed(procs):
                if p.poll() is None:
                    p.send_signal(signal.SIGTERM)
            for p in procs:
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
            log.close()


def wallpaper_and_undo(conf: Path):
    print("\n3 · a theme's own wallpaper, the lock screen's copy, and undo")
    place = ht.Place(conf)
    ht.apply("classic", "kognogos-mocha", place, wallpaper=OWN_WALL, reload=False)
    before = {p: p.read_text() for p in (conf / "mako/config", conf / "hypeforge/theme/sway.conf")}
    lock_before = (conf / "gtklock/background.jpg").read_bytes()
    t0 = time.time()
    r = ht.apply("rice", "dark-green", place, wallpaper="theme", reload=False)
    took = time.time() - t0
    pic = Path(r["picture"])
    check(pic.is_file() and pic.stat().st_size > 100_000, f"Dark Green's wallpaper made ({took:.0f} s)")
    lock = conf / "gtklock/background.jpg"
    check(lock.is_file(), "the lock screen got its blurred copy")
    check(f'output * bg "{pic}" fill' in (conf / "hypeforge/theme/sway.conf").read_text(), "Sway is told to show it")
    ht.undo(place, reload=False)
    same = all(p.read_text() == body for p, body in before.items())
    check(same, "undo put Classic + Mocha back, file for file")
    check(lock.read_bytes() == lock_before, "undo put the lock screen's old picture back")
    check(place.read_state().get("theme") == "kognogos-mocha", "undo put the state back too")


def today_vs_classic(conf: Path):
    print("\n4 · Classic + KognogOS Mocha against today's look (what differs)")
    place = ht.Place(conf)
    ht.apply("classic", "kognogos-mocha", place, wallpaper=OWN_WALL, reload=False)
    hexes = lambda s: re.findall(r"#[0-9a-fA-F]{6}\b|\b[0-9a-f]{6}ff\b", s)
    old_sway = (REPO / "docs/research/look-2026-10/04-inventory.md")  # not used for values; today's values below
    today = {"window focused": "#cdd6f4", "window unfocused": "#45475a", "title bar": "#181825", "urgent": "#f38ba8",
             "bar": "#181825", "bar shade": "#262637", "list background": "#262637", "list match": "#cba6f7",
             "list selection": "#45475a", "notes background": "#262637", "lock background": "#1e1e2e"}
    gen = (conf / "hypeforge/theme/sway.conf").read_text() + (conf / "hypeforge/theme/colors.css").read_text() \
        + (conf / "hypeforge/theme/fuzzel-colors.ini").read_text() + (conf / "mako/config").read_text()
    missing = [k for k, v in today.items() if v.lstrip("#") not in gen]
    print("        today's colours not found:", ", ".join(missing) if missing else "none")
    check(set(missing) <= {"urgent"}, "everything matches today except Mocha's approved tiny changes (red → #ff99b5)")


def main():
    keep = "--keep" in sys.argv
    base = Path(tempfile.mkdtemp(prefix="hf-theme-bench-"))
    try:
        conf, env = home_for(base)
        static_checks(conf, env)
        runtime_checks(base, conf, env)
        wallpaper_and_undo(conf)
        today_vs_classic(conf)
    finally:
        if keep:
            print("\nbench folder kept:", base)
        else:
            shutil.rmtree(base, ignore_errors=True)
    bad = [w for ok, w in results if not ok]
    print(f"\nRESULT: {len(results) - len(bad)}/{len(results)} passed" + ("" if not bad else " — FAILED"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
