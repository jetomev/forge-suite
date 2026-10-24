#!/usr/bin/env python3
"""displayForge on one, two and three screens, before Javier's own run (KognogOS stage 03).

For each count, a screen-less Sway with that many fake screens (2560 × 1440); the real engine reads
them, tries 80 % and 90 % sizes and a new arrangement through the keep-or-go-back countdown, and the
check reads Sway again after each answer: the change on screen while it counts down, gone after "go
back", still there after "keep". Then the app itself, 100 columns wide, photographed on its Screens
page, for a person to look at (docs/images is untouched: pictures go to logs/). Nothing touches a real screen or file: the saved
files point into a throwaway folder, brightness uses a fake ddcutil.

    PYTHONPATH=../forgekit python3 scripts/screens-bench.py [--counts 1,2,3]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
LOGS = ROOT / "logs"

results: list[tuple[bool, str]] = []


def check(ok: bool, words: str) -> None:
    results.append((ok, words))
    print(f"  {'ok  ' if ok else 'FAIL'}  {words}")


def outputs(env) -> dict:
    out = subprocess.run(["swaymsg", "-r", "-t", "get_outputs"], env=env, capture_output=True, text=True, check=True)
    return {o["name"]: o for o in json.loads(out.stdout)}


def start_sway(n: int, base: Path) -> tuple[subprocess.Popen, dict]:
    run = base / f"run{n}"
    run.mkdir(mode=0o700)
    conf = base / f"sway{n}.conf"
    conf.write_text("".join(f"output HEADLESS-{i} resolution 2560x1440 position {2560 * (i - 1)} 0\n"
                            for i in range(1, n + 1)) + "xwayland disable\n")
    env = {k: v for k, v in os.environ.items() if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK")}
    env.update(XDG_RUNTIME_DIR=str(run), WLR_BACKENDS="headless", WLR_RENDERER="pixman",
               WLR_HEADLESS_OUTPUTS=str(n), WLR_LIBINPUT_NO_DEVICES="1")
    log = open(base / f"sway{n}.log", "w")
    sway = subprocess.Popen(["sway", "-c", str(conf)], env=env, stdout=log, stderr=log)
    for _ in range(100):
        socks = list(run.glob("sway-ipc.*.sock"))
        if socks:
            env["SWAYSOCK"] = str(socks[0])
            break
        time.sleep(0.1)
    else:
        raise SystemExit(f"the hidden Sway did not start; see {base / f'sway{n}.log'}")
    time.sleep(0.5)
    return sway, env


def engine(n: int, env: dict) -> None:
    from displayforge import screens as S, trial as T
    from displayforge.session import Session
    os.environ["SWAYSOCK"] = env["SWAYSOCK"]                 # screens.read() asks the hidden Sway
    se = Session(S.read(), {"names": {}, "bus": {}})
    check(len(se.live) == n, f"{n} screen(s): displayForge reads {len(se.live)}")
    first = min(se.live, key=lambda s: s.x).name     # the leftmost: a bigger desktop pushes into the others
    # (2026-10-24: the bench resized the rightmost screen only, and missed Javier's "these screens overlap")
    for size in (0.8, 0.9):
        se.change(first, scale=size)
        check(se.problems() == [], f"{n} screen(s): {first} at {size:.0%} — nothing in the way ({se.problems()})")
        before = {k: (v["rect"]["x"], v["rect"]["y"]) for k, v in outputs(env).items()}
        t = T.Trial(se.live, se.pending, swaymsg="swaymsg")
        check(t.start(), f"{n} screen(s): Sway takes {first} at {size:.0%}")
        o = outputs(env)
        now = o[first]["scale"]
        check(abs(now - size) < 1e-6, f"{n} screen(s): while it counts down, {first} is at {now:.0%}")
        rects = sorted((v["rect"]["x"], v["rect"]["width"]) for v in o.values())
        touching = all(a[0] + a[1] == b[0] for a, b in zip(rects, rects[1:]))
        check(touching, f"{n} screen(s): side by side, no overlap and no gap {rects}")
        t.revert_now()
        after = {k: (v["rect"]["x"], v["rect"]["y"]) for k, v in outputs(env).items()}
        back = outputs(env)[first]["scale"]
        check(abs(back - 1.0) < 1e-6 and after == before,
              f"{n} screen(s): after Go Back Now, {first} is at {back:.0%} and every screen where it was")
        se.discard()
    se.change(first, scale=0.9)
    t = T.Trial(se.live, se.pending, swaymsg="swaymsg")
    t.start()
    t.keep()
    se.tried()
    kept = outputs(env)[first]["scale"]
    check(abs(kept - 0.9) < 1e-6, f"{n} screen(s): Keep It leaves {first} at {kept:.0%}")
    se.change(first, scale=1.0)
    t = T.Trial(se.live, se.pending, swaymsg="swaymsg")
    t.start()
    t.keep()
    se.tried()
    if n >= 2:
        last = next(s.name for s in reversed(se.live) if s.name != first)
        before = {k: (v["rect"]["x"], v["rect"]["y"]) for k, v in outputs(env).items()}
        side = "right" if before[last][0] < before[first][0] else "left"     # the other side from where it is
        se.arrange(last, side, first)
        t = T.Trial(se.live, se.pending, swaymsg="swaymsg")
        check(t.start(), f"{n} screens: Sway takes {last} moved to the {side} of {first}")
        o = outputs(env)
        now_left = o[last]["rect"]["x"] < o[first]["rect"]["x"]
        check(now_left == (side == "left"), f"{n} screens: {last} now sits {side} of {first}")
        t.revert_now()
        after = {k: (v["rect"]["x"], v["rect"]["y"]) for k, v in outputs(env).items()}
        check(after == before, f"{n} screens: after Go Back Now, every screen is where it was")
        se.discard()
    else:
        check(not any("left" in p for p in se.problems()), "1 screen: nothing to arrange, no problem shown")


async def app_picture(n: int, env: dict, base: Path, out: Path) -> None:
    from displayforge import brightness as B, saving as V, screens as S
    from displayforge.app import DisplayForgeApp
    from displayforge.session import Session
    V.OUTPUTS, V.BACKUPS, B.CONFIG = base / "outputs", base / "backups", base / "screens.toml"
    fake = base / "ddcutil"
    fake.write_text('#!/bin/sh\ncase "$*" in *getvcp*) echo "VCP 10 C 70 100";; esac\n')
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    se = Session(S.read(), {"names": {}, "bus": {}})
    app = DisplayForgeApp(se, swaymsg="swaymsg", ddcutil=str(fake))
    async with app.run_test(size=(100, 34)) as pilot:
        await pilot.pause(0.8)
        svg = out.with_suffix(".svg")
        app.save_screenshot(filename=svg.name, path=str(svg.parent))
    try:
        subprocess.run(["rsvg-convert", "-o", str(out), str(svg)], check=True, capture_output=True)
        print(f"        picture: {out}")
    except (OSError, subprocess.CalledProcessError):
        print(f"        picture: {svg} (no rsvg-convert for a PNG)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--counts", default="1,2,3")
    a = ap.parse_args()
    LOGS.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d")
    with tempfile.TemporaryDirectory(prefix="dfbench.") as d:
        base = Path(d)
        for n in (int(c) for c in a.counts.split(",")):
            print(f"\n== {n} screen(s)")
            sway, env = start_sway(n, base)
            try:
                engine(n, env)
                asyncio.run(app_picture(n, env, base, LOGS / f"screens-bench-{stamp}-{n}.png"))
            finally:
                subprocess.run(["swaymsg", "exit"], env=env, capture_output=True)
                try:
                    sway.wait(5)
                except subprocess.TimeoutExpired:
                    sway.kill()
    bad = [w for ok, w in results if not ok]
    print(f"\nRESULT: {len(results) - len(bad)}/{len(results)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
