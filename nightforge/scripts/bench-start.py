#!/usr/bin/env python3
"""nightForge at login, on a hidden bench before the desktop (hypeForge F-51 rule).

Starts a screen-less Sway (three fake screens; its own runtime folder, settings and private session
bus), runs the REAL wlsunset under another name ("wlsunset-bench", so a night light on the real
desktop is never matched or stopped), and checks: hypeForge's old login line first, then
`nightforge start` takes over with exactly one night light and one tray icon; a second start
doesn't double them; Warm Now / Daylight Now / Automatic / Off / On do what they say; nothing
crashes. Run it inside a private bus:

    dbus-run-session -- python3 scripts/bench-start.py        exit 0 = all good
"""

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCREENS = ["HEADLESS-1", "HEADLESS-2", "HEADLESS-3"]


def main() -> int:
    if not os.environ.get("DBUS_SESSION_BUS_ADDRESS", "").startswith("unix:path=/tmp") and "--any-bus" not in sys.argv:
        print("run it inside `dbus-run-session -- …`, so its tray icon stays off the real bar")
        return 2
    base = Path(tempfile.mkdtemp(prefix="nf-bench-"))
    run, conf, state, bin_ = base / "run", base / "config", base / "state", base / "bin"
    run.mkdir(mode=0o700)
    bin_.mkdir()
    (bin_ / "wlsunset-bench").symlink_to(shutil.which("wlsunset"))
    (base / "sway.conf").write_text("".join(f"output {s} resolution 1280x720 position {i * 1280} 0\n"
                                            for i, s in enumerate(SCREENS)))
    env = {k: v for k, v in os.environ.items() if k not in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "I3SOCK")}
    env.update(XDG_RUNTIME_DIR=str(run), XDG_CONFIG_HOME=str(conf), XDG_STATE_HOME=str(state),
               WLR_BACKENDS="headless", WLR_RENDERER="pixman", WLR_HEADLESS_OUTPUTS="3", WLR_LIBINPUT_NO_DEVICES="1",
               NIGHTFORGE_WLSUNSET=str(bin_ / "wlsunset-bench"), PATH=f"{bin_}:{os.environ['PATH']}")
    log = open(base / "bench.log", "w")
    sway = subprocess.Popen(["sway", "--unsupported-gpu", "-c", str(base / "sway.conf")], env=env, stdout=log, stderr=log)
    ok, notes = True, []

    def check(cond, what):
        nonlocal ok
        print(("  ok    " if cond else "  FAIL  ") + what)
        ok = ok and cond

    def lights():
        out = subprocess.run(["pgrep", "-x", "wlsunset-bench"], capture_output=True, text=True).stdout.split()
        return [int(p) for p in out]

    def trays():
        p = run / "nightforge/tray.pid"
        try:
            pid = int(p.read_text())
            os.kill(pid, 0)
            return [pid]
        except (OSError, ValueError):
            return []

    def nf(*args):
        return subprocess.run([sys.executable, str(ROOT / "main.py"), *args], env=env, capture_output=True,
                              text=True, timeout=30)

    def ctl(code):
        return subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r)\n" % str(ROOT) + code],
                              env=env, capture_output=True, text=True, timeout=30)
    try:
        for _ in range(100):
            if list(run.glob("wayland-*")):
                break
            time.sleep(0.1)
        env["WAYLAND_DISPLAY"] = next(p.name for p in run.glob("wayland-*") if not p.name.endswith(".lock"))
        env["SWAYSOCK"] = str(next(run.glob("sway-ipc.*.sock")))
        # 1. hypeForge's old login line: a night light nightForge didn't start
        old = subprocess.Popen([str(bin_ / "wlsunset-bench"), "-l", "25.77", "-L", "-80.19"], env=env,
                               stdout=log, stderr=log, start_new_session=True)
        time.sleep(1)
        check(old.poll() is None, "the real wlsunset runs on the bench's screens (gamma control works headless)")
        # 2. nightForge takes over
        r = nf("start")
        time.sleep(2)
        check(r.returncode == 0, f"`nightforge start` at login: exit {r.returncode} {r.stderr.strip()[-120:]}")
        check(old.poll() is not None, "the old night light was stopped")
        check(len(lights()) == 1, f"exactly one night light ({len(lights())})")
        check(len(trays()) == 1, f"one tray icon ({len(trays())})")
        # 3. a second start doesn't double anything
        nf("start")
        time.sleep(2)
        check(len(lights()) == 1 and len(trays()) == 1, f"a second start: still one of each ({len(lights())}, {len(trays())})")
        # 4. the modes, through nightForge's own code
        for want, n in (("warm", 1), ("day", 0), ("auto", 1)):
            r = ctl(f"from nightforge import control as C\nfrom nightforge.settings import Settings\nC.start(Settings.load(), {want!r})")
            time.sleep(1)
            check(r.returncode == 0 and len(lights()) == n, f"{want}: {n} night light running ({len(lights())}) {r.stderr.strip()[-120:]}")
        # 5. off and on, as the tray's Turn Off / Turn On do it
        ctl("from nightforge import control as C\nfrom nightforge.settings import Settings\ns=Settings.load(); s.enabled=False; s.save(); C.start(s)")
        time.sleep(1)
        check(not lights(), "Turn Off: nothing running")
        check("enabled = false" in (conf / "nightforge/settings.toml").read_text(), "Turn Off: saved for the next login")
        r = nf("start")
        time.sleep(1)
        check(not lights(), "a login while off: still off")
        ctl("from nightforge import control as C\nfrom nightforge.settings import Settings\ns=Settings.load(); s.enabled=True; s.save(); C.start(s)")
        time.sleep(1)
        check(len(lights()) == 1, "Turn On: running again")
        print("  status:", nf("status").stdout.strip())
        check(len(trays()) == 1 and sway.poll() is None, "the tray icon and the bench's Sway still running")
    finally:
        for pid in lights() + trays():
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
        sway.send_signal(signal.SIGTERM)
        try:
            sway.wait(timeout=5)
        except subprocess.TimeoutExpired:
            sway.kill()
        log.close()
    print("RESULT:", "OK — nightForge takes over the night light cleanly" if ok else f"FAILED (bench folder kept: {base})")
    if ok:
        shutil.rmtree(base, ignore_errors=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
