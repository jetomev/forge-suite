#!/usr/bin/env python3
"""The bar and a sound service that is still starting (F-86). Javier's logins of 2026-10-25 and 10-26: an
applet reloaded the bar ~1 s after it started, while WirePlumber was still starting, and Waybar's sound piece
took the whole bar down (the guard brought it back). Replayed here on a hidden screen with a PRIVATE sound
service (its own PipeWire + WirePlumber, no speakers or microphones opened: a null output only), so the real
desktop's sound and bar are never touched.

WirePlumber is frozen for 2 s to play a slow start (the real one scans devices for ~4 s), two ways: before it
posts anything, and right after its first record. Each way runs twice:
  - with NO wait before the reload: the bar must die at least once (it is a race: 3/3 or 4/4 most runs, 1/3 seen;
    a death proves the replay reproduces the crash)
  - with hfbar's wait (what every applet's reload and the look's restyle go through): the bar must live
And the control: a bar that starts during the slow start with no reload lives.

    sound-reload-bench.py [--runs 3]      logs: logs/sound-reload-bench-latest.log
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
COMMON = HERE / "applets/common"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    a = ap.parse_args()
    base = Path(tempfile.mkdtemp(prefix="hfsnd.", dir="/tmp"))     # short: Sway's socket path must fit
    run, conf = base / "r", base / "c"
    run.mkdir(mode=0o700)
    (conf / "wireplumber/wireplumber.conf.d").mkdir(parents=True)
    (conf / "wireplumber/wireplumber.conf.d/no-hardware.conf").write_text(
        "wireplumber.profiles = {\n  main = {\n" + "".join(f"    monitor.{m} = disabled\n" for m in
        ("alsa", "alsa-midi", "bluez", "bluez-midi", "v4l2", "libcamera")) + "  }\n}\n")
    (conf / "pipewire/pipewire.conf.d").mkdir(parents=True)
    (conf / "pipewire/pipewire.conf.d/null-output.conf").write_text(
        'context.objects = [\n  { factory = adapter args = { factory.name = support.null-audio-sink '
        'node.name = "bench-output" media.class = Audio/Sink audio.position = [ FL FR ] } }\n]\n')
    (base / "sway.conf").write_text("output * resolution 1280x720\nxwayland disable\n")
    (base / "bar.json").write_text(json.dumps({"modules-right": ["wireplumber", "clock"], "height": 30}))
    (base / "style.css").write_text("* { font-size: 12px; }\n")
    env = {k: v for k, v in os.environ.items()
           if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "DBUS_SESSION_BUS_ADDRESS", "PIPEWIRE_RUNTIME_DIR")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), WLR_BACKENDS="headless", WLR_RENDERER="pixman",
               WLR_HEADLESS_OUTPUTS="1", WLR_LIBINPUT_NO_DEVICES="1", GDK_BACKEND="wayland")
    bus = subprocess.run(["dbus-daemon", "--session", "--fork", "--print-address=1", "--print-pid=1"],
                         capture_output=True, text=True, env=env).stdout.split()
    env["DBUS_SESSION_BUS_ADDRESS"] = bus[0]
    logs = HERE / "logs"
    logs.mkdir(exist_ok=True)
    out = open(logs / f"sound-reload-bench-{time.strftime('%Y%m%d-%H%M%S')}.log", "w")
    latest = logs / "sound-reload-bench-latest.log"
    latest.unlink(missing_ok=True)
    latest.symlink_to(Path(out.name).name)
    results = []

    def say(words: str):
        print(words, flush=True)
        out.write(words + "\n")
        out.flush()

    def record_there() -> bool:
        try:
            r = subprocess.run(["pw-metadata", "-n", "default"], env=env, capture_output=True, text=True, timeout=2)
        except subprocess.TimeoutExpired:
            return False
        return "Found" in r.stdout

    def one(freeze: str, reload: str) -> bool:
        """True when the bar is still running 5 s after the reload."""
        noise = open(base / "sound.log", "a")
        pw = subprocess.Popen(["pipewire"], env=env, stdout=noise, stderr=noise)
        wp = subprocess.Popen(["wireplumber"], env=env, stdout=noise, stderr=noise)
        t0 = time.monotonic()
        if freeze == "after its first record":
            while not record_there() and time.monotonic() - t0 < 10:
                time.sleep(0.02)
        else:
            time.sleep(0.05)
        wp.send_signal(signal.SIGSTOP)
        wake = threading.Timer(2.0, lambda: wp.send_signal(signal.SIGCONT))
        wake.start()
        bar = subprocess.Popen(["waybar", "-c", str(base / "bar.json"), "-s", str(base / "style.css")],
                               env=env, stdout=noise, stderr=noise)
        time.sleep(0.9)
        if reload == "with the wait":
            subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import hfbar; "
                            "hfbar.wait_for_sound()", str(COMMON)], env=env, timeout=30)
        if reload != "no reload":
            bar.send_signal(signal.SIGUSR2)          # this bench's own bar only, by its process number
        time.sleep(5)
        alive = bar.poll() is None
        wake.cancel()
        wp.send_signal(signal.SIGCONT)
        for p in (bar, wp, pw):
            if p.poll() is None:
                p.terminate()
                p.wait(5)
        time.sleep(0.3)
        return alive

    sway = subprocess.Popen(["sway", "-c", str(base / "sway.conf")], env=env, stdout=open(base / "sway.log", "w"),
                            stderr=subprocess.STDOUT)
    try:
        time.sleep(2)
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        say(f"sound-reload-bench · {time.strftime('%Y-%m-%d %H:%M:%S')} · WirePlumber frozen 2 s, the reload 0.9 s "
            f"after the bar starts · {a.runs} runs each")
        for freeze, reload, want in (("before it posts anything", "no reload", True),
                                     ("before it posts anything", "no wait", False),
                                     ("before it posts anything", "with the wait", True),
                                     ("after its first record", "no wait", False),
                                     ("after its first record", "with the wait", True)):
            lived = sum(one(freeze, reload) for _ in range(a.runs))
            ok = lived == a.runs if want else lived < a.runs     # a race: one death proves the crash
            results.append(ok)
            say(f"  {'ok  ' if ok else 'FAIL'}  frozen {freeze}, {reload}: the bar lived {lived}/{a.runs} "
                f"(must {'all live' if want else 'die at least once: the replay reproduces the crash'})")
    finally:
        sway.terminate()
        sway.wait(10)
        os.kill(int(bus[1]), signal.SIGTERM)
        time.sleep(1)
        if (run / "doc").is_mount():            # the document portal, started on the bench's own bus
            subprocess.run(["fusermount3", "-u", str(run / "doc")], capture_output=True)
        subprocess.run(["rm", "-rf", "--one-file-system", str(base)])
    say(f"\nRESULT: {sum(results)}/{len(results)} passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
