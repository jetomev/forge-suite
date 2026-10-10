#!/usr/bin/env python3
"""The hidden bench for the SwayFX login ("hypeForge FX", D-78 step 2) — before it is offered on
the login screen. A throwaway home folder; the real desktop is never signalled.

  1. Every style's effects: the FX login's config (sway/config + fx.conf) through SwayFX's own
     check, and the normal config still through plain Sway's (it must never see an FX line).
  2. SwayFX on a screen-less output, on the GPU (SwayFX has no software renderer): a window open,
     shadows and blur on, then TEN config reloads — SwayFX #566 says reloads can freeze it with
     shadows on. After each reload it must answer within 5 seconds and keep its window.

    python3 scripts/fx-bench.py [--keep]
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FX = Path("~/.local/opt/swayfx/bin").expanduser()
WALL = "/usr/share/wallpapers/kognog/Kognog OS Semi - Logo Catpuccin Mocha.png"
RELOADS = 10

loader = importlib.machinery.SourceFileLoader("hypeforge_theme", str(REPO / "applets/theme/hypeforge-theme"))
spec = importlib.util.spec_from_loader("hypeforge_theme", loader)
ht = importlib.util.module_from_spec(spec)
loader.exec_module(ht)
results: list[tuple[bool, str]] = []


def check(ok: bool, what: str):
    results.append((ok, what))
    print(("  ok    " if ok else "  FAIL  ") + what)


def errors(stderr: str) -> list[str]:
    # sway -C exits 0 even when an included file has errors: read its error lines (theme bench, 10-10)
    return [l for l in stderr.splitlines() if "Error on line" in l or "Error(s) loading" in l]


def main():
    keep = "--keep" in sys.argv
    if not (FX / "sway").exists():
        print("SwayFX is not built yet (~/.local/opt/swayfx)"); return 1
    base = Path(tempfile.mkdtemp(prefix="hffx.", dir="/tmp"))   # short: the IPC socket path must fit
    home = base / "h"; conf = home / ".config"
    for src, dest in (("sway/config", "sway/config"), ("sway/config-fx", "sway/config-fx"),
                      ("sway/waybar/style.css", "sway/waybar/style.css"), ("sway/fuzzel/fuzzel.ini", "sway/fuzzel/fuzzel.ini"),
                      ("sway/gtklock/style.css", "gtklock/style.css")):
        (conf / dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / src, conf / dest)
    (conf / "sway/outputs").write_text("# bench\n")
    env = {k: v for k, v in os.environ.items() if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK", "DBUS_SESSION_BUS_ADDRESS")}
    env.update(HOME=str(home), XDG_CONFIG_HOME=str(conf), XDG_CACHE_HOME=str(home / ".cache"),
               WLR_BACKENDS="headless", WLR_LIBINPUT_NO_DEVICES="1")
    place = ht.Place(conf)
    try:
        print("\n1 · every style's effects, through each program's own check")
        bad_fx, bad_plain = [], []
        for style in ht.styles():
            for theme in ("kognogos-mocha", "ember", "white"):
                ht.apply(style, theme, place, wallpaper=WALL, reload=False)
                r = subprocess.run([str(FX / "sway"), "-C", "-c", str(conf / "sway/config-fx")], env=env, capture_output=True, text=True)
                if r.returncode or errors(r.stderr):
                    bad_fx.append(f"{style}/{theme}: {errors(r.stderr)[:1] or r.stderr[-160:]}")
                r = subprocess.run(["sway", "-C", "-c", str(conf / "sway/config")], env=dict(env, WLR_RENDERER="pixman"), capture_output=True, text=True)
                if r.returncode or errors(r.stderr):
                    bad_plain.append(f"{style}/{theme}: {errors(r.stderr)[:1]}")
        n = len(ht.styles()) * 3
        check(not bad_fx, f"SwayFX accepts the FX login's config for all {n} looks" + (f" — {bad_fx[:2]}" if bad_fx else ""))
        check(not bad_plain, f"plain Sway's config stays clean of FX lines for all {n}" + (f" — {bad_plain[:2]}" if bad_plain else ""))
        fxconf = conf / "hypeforge/theme/fx.conf"
        good = fxconf.read_text()
        fxconf.write_text(good + "\ncorner_radius banana\n")
        r = subprocess.run([str(FX / "sway"), "-C", "-c", str(conf / "sway/config-fx")], env=env, capture_output=True, text=True)
        check(bool(errors(r.stderr)), "a broken effects file is caught by SwayFX's check (the check is real)")
        fxconf.write_text(good)

        for style, theme in (("macos", "blue"), ("rice", "dark-purple")):
            print(f"\n2 · SwayFX running {style}/{theme} on the GPU, a window open, {RELOADS} reloads")
            ht.apply(style, theme, place, wallpaper=WALL, reload=False)
            run = base / f"r-{style}"; run.mkdir(mode=0o700)
            cfg = base / f"{style}.conf"
            cfg.write_text(f"output HEADLESS-1 resolution 1280x720\nxwayland disable\ninclude {conf}/hypeforge/theme/sway.conf\ninclude {fxconf}\n")
            e = dict(env, XDG_RUNTIME_DIR=str(run), WLR_RENDERER="gles2", WLR_HEADLESS_OUTPUTS="1")
            log = open(base / f"{style}.log", "w")
            procs = []
            try:
                sway = subprocess.Popen([str(FX / "sway"), "--unsupported-gpu", "-c", str(cfg)], env=e, stdout=log, stderr=log)
                procs.append(sway)
                sock = None
                for _ in range(100):
                    found = list(run.glob("sway-ipc.*.sock"))
                    if found:
                        sock = str(found[0]); break
                    time.sleep(0.1)
                if not sock:
                    check(False, f"{style}: SwayFX started on the GPU"); continue
                e["SWAYSOCK"] = sock
                e["WAYLAND_DISPLAY"] = next((p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock")), "wayland-1")
                win = subprocess.Popen(["alacritty", "--class", "fxbench", "-e", "sleep", "120"], env=e, stdout=log, stderr=log)
                procs.append(win)
                def ask(*words, e=e):
                    return subprocess.run([str(FX / "swaymsg"), *words], env=e, capture_output=True, text=True, timeout=5)
                seen = False
                for _ in range(50):
                    if "fxbench" in ask("-t", "get_tree").stdout:
                        seen = True; break
                    time.sleep(0.2)
                check(seen, f"{style}: a window is on screen (shadows and blur drawn around it)")
                survived = 0
                for i in range(RELOADS):
                    try:
                        ask("reload")
                        time.sleep(0.6)
                        r = ask("-t", "get_tree")
                        if sway.poll() is not None or "fxbench" not in r.stdout:
                            break
                        survived += 1
                    except subprocess.TimeoutExpired:
                        break
                check(survived == RELOADS, f"{style}: {survived} of {RELOADS} reloads answered within 5 s, window kept (SwayFX #566)")
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
