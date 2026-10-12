#!/usr/bin/env python3
"""The hidden bench for the full-quality wallpaper preview (overlay.py): a screen-less Sway on the
graphics card (Alacritty needs it), a real Alacritty running themeForge, the real overlay, keys from
hypeForge's fake keyboard. The test picture is smooth gradients: over the real picture neighbouring
pixels differ; the half-block preview repeats one colour across each character cell. So the pixels
tell which one is on screen.

    overlay-bench.py [--keep]      exit 0 when every check passes
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
HYPE = HERE.parent / "hypeforge"
KEYS = HYPE / "scripts/fake-keyboard.py"


def main() -> int:
    from PIL import Image
    import numpy as np
    base = Path(tempfile.mkdtemp(prefix="tfov.", dir="/tmp"))
    run, conf = base / "r", base / "c"
    run.mkdir(mode=0o700)
    (conf / "hypeforge/theme").mkdir(parents=True)
    (conf / "alacritty").mkdir(parents=True)
    real_alacritty = Path.home() / ".config/alacritty/alacritty.toml"
    if real_alacritty.exists():
        shutil.copy(real_alacritty, conf / "alacritty/alacritty.toml")        # the same padding as Javier's
    pics = base / "pics"
    pics.mkdir()
    y, x = np.mgrid[0:1440, 0:2560]
    grad = np.dstack([(x * 255 // 2559), (y * 255 // 1439), np.full_like(x, 128)]).astype(np.uint8)
    Image.fromarray(grad).save(pics / "gradient.png")
    (conf / "hypeforge/theme/state.toml").write_text(
        f'style = "rice"\ntheme = "kognogos-mocha"\nwallpaper = "{pics / "gradient.png"}"\nfit = "fill"\n')
    (conf / "hypeforge/look.toml").write_text(
        f'theme = "rice"\ncolors = "kognogos-mocha"\n[wallpaper]\npicture = "{pics / "gradient.png"}"\n'
        f'fit = "fill"\nfolder = "{pics}"\n')
    (base / "sway.conf").write_text("output HEADLESS-1 resolution 1920x1080\nxwayland disable\nfocus_follows_mouse no\n"
                                    'for_window [app_id="themeforge"] floating enable, move position 300 120\n')
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK", "DBUS_SESSION_BUS_ADDRESS")}
    log_path = base / "overlay.log"
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), XDG_CACHE_HOME=str(base / "cache"),
               XDG_STATE_HOME=str(base / "state"), XDG_DATA_HOME=str(base / "data"),
               WLR_BACKENDS="headless", WLR_RENDERER="gles2", WLR_HEADLESS_OUTPUTS="1", WLR_LIBINPUT_NO_DEVICES="1",
               THEMEFORGE_OVERLAY_LOG=str(log_path))
    results = []
    log = open(base / "bench.log", "w")

    def check(ok, what):
        results.append(bool(ok))
        print(("  ok    " if ok else "  FAIL  ") + what, flush=True)

    sway = subprocess.Popen(["sway", "--unsupported-gpu", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    procs = []
    try:
        for _ in range(100):
            socks = list(run.glob("sway-ipc.*.sock"))
            if socks:
                break
            time.sleep(0.1)
        env["SWAYSOCK"] = str(socks[0])
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))

        def keys(*steps):
            subprocess.run([sys.executable, str(KEYS), *steps], env=env, stdout=log, stderr=log, timeout=30)
            time.sleep(1.5)

        def shot() -> "np.ndarray":
            p = base / "shot.png"
            subprocess.run(["grim", str(p)], env=env, check=True)
            return np.asarray(Image.open(p).convert("RGB")).astype(int)

        def events() -> list[dict]:
            try:
                return [json.loads(l) for l in log_path.read_text().splitlines()]
            except OSError:
                return []

        def last_box():
            shown = [e["shown"] for e in events() if "shown" in e]
            return shown[-1] if shown else None

        def wait_for(want: bool, seconds: float = 4.0) -> bool:
            end = time.monotonic() + seconds
            while time.monotonic() < end:
                if showing() == want:
                    return True
                time.sleep(0.1)
            return showing() == want

        def showing() -> bool:
            for e in reversed(events()):
                if "shown" in e:
                    return True
                if "hidden" in e:
                    return False
            return False

        def detail(img, box) -> float:
            """Distinct colours per 10 pixels along the middle row of the box (blocks: 1-2, a picture: many)."""
            x, y, w, h = box
            row = img[y + h // 2, x + 4:x + w - 4]
            spans = [len({tuple(px) for px in row[i:i + 10]}) for i in range(0, len(row) - 10, 10)]
            return sum(spans) / max(1, len(spans))

        procs.append(subprocess.Popen(["alacritty", "--class", "themeforge", "-o", "window.dimensions.columns=110",
                                       "-o", "window.dimensions.lines=40", "-e", sys.executable, str(HERE / "main.py")],
                                      env=env, stdout=log, stderr=log))
        time.sleep(5)
        keys("tap:2")                             # the Wallpaper page (it opens on My pictures: the gradient)
        time.sleep(2.5)
        print("1 · the page with the picture")
        box = last_box()
        check(box is not None and showing(), f"the overlay drew the picture at {box}")
        img = shot()
        shutil.copy(base / "shot.png", base / "sharp.png")      # for a person to look at
        if box:
            d = detail(img, box)
            check(d >= 5, f"full quality: {d:.1f} colours per 10 pixels (blocks would be 1–2)")
            x, y, w, h = box
            tl, br = img[y + 3, x + 3], img[y + h - 4, x + w - 4]
            check(tl[0] < 30 and tl[1] < 30 and br[0] > 225 and br[1] > 225,
                  f"the whole picture, corner to corner: top-left {tuple(tl)}, bottom-right {tuple(br)}")
            check(abs(w / h - 16 / 9) < 0.02, f"the screen's shape, {w}×{h}")

        print("2 · another window in use: the overlay steps away")
        procs.append(subprocess.Popen(["alacritty", "--class", "other", "-e", "sleep", "60"], env=env, stdout=log, stderr=log))
        time.sleep(3)
        img2 = shot()
        check(wait_for(False), "hidden while themeForge isn't the window in use")
        if box:
            d2 = detail(img2, box)
            check(d2 <= 3, f"the half-block preview shows under it: {d2:.1f} colours per 10 pixels")
            # where the blocks are: walk out from the middle of the spot until the colour jumps
            def edge(cx, cy, dx, dy):
                prev = img2[cy, cx]
                while 0 < cx < img2.shape[1] - 1 and 0 < cy < img2.shape[0] - 1:
                    nx, ny = cx + dx, cy + dy
                    if np.abs(img2[ny, nx] - prev).sum() > 60:
                        return cx
                    prev, cx, cy = img2[ny, nx], nx, ny
                return cx
            x, y, w, h = box
            mx, my = x + w // 2, y + h // 2
            left, right = edge(mx, my, -1, 0), edge(mx, my, 1, 0)        # and up and down the same way:
            cy = my
            prev = img2[cy, mx]
            while cy > 0 and np.abs(img2[cy - 1, mx] - prev).sum() <= 60:
                cy -= 1; prev = img2[cy, mx]
            top = cy
            cy = my
            prev = img2[cy, mx]
            while cy < img2.shape[0] - 1 and np.abs(img2[cy + 1, mx] - prev).sum() <= 60:
                cy += 1; prev = img2[cy, mx]
            bottom = cy
            cw = (w + 13) / 56                                # about a cell, from the spot
            check(abs(left - x) <= cw and abs(right - (x + w)) <= cw and abs(top - y) <= 3 and abs(bottom - (y + h)) <= 3,
                  f"right over the blocks: blocks {left},{top}–{right},{bottom}, picture {x},{y}–{x + w},{y + h}")

        print("3 · back to themeForge, then a list opened over the preview")
        subprocess.run(["swaymsg", '[app_id="themeforge"] focus'], env=env, capture_output=True)
        time.sleep(1.5)
        check(wait_for(True), "back on top when themeForge is in use again")
        # the keyboard stays plugged in while we look (unplugging it tells the terminal it lost focus,
        # and a list closes when the app loses focus: a bench thing, a real keyboard stays)
        held = subprocess.Popen([sys.executable, str(KEYS), "tap:enter", "wait:4", "tap:esc", "wait:1"],
                                env=env, stdout=log, stderr=log)
        time.sleep(1.0)
        check(wait_for(False, 2.5), "hidden while a list is open")
        held.wait(15)
        check(wait_for(True), "back when the list closes")

        print("4 · another page, then quitting")
        keys("tap:1")
        check(wait_for(False), "hidden on the Theme Picker")
        started = [e["started"] for e in events() if "started" in e]
        check(len(started) == 1, f"one overlay program for the whole run ({len(started)})")
        keys("tap:q")
        time.sleep(2)
        alive = started and Path(f"/proc/{started[0]}").exists()
        check(not alive, "the overlay ends with themeForge")
        subprocess.run(["grim", str(base / "last.png")], env=env)
    finally:
        for p in procs:
            if p.poll() is None:
                p.send_signal(signal.SIGTERM)
        for p in procs:
            try:
                p.wait(5)
            except subprocess.TimeoutExpired:
                p.kill()
        sway.terminate()
        try:
            sway.wait(5)
        except subprocess.TimeoutExpired:
            sway.kill()
        log.close()
    print(f"\nRESULT: {sum(results)}/{len(results)} passed")
    print(f"pictures and log: {base}")
    if "--keep" not in sys.argv and all(results):
        shutil.rmtree(base, ignore_errors=True)
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
