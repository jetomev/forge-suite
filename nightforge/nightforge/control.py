"""Starting, stopping and nudging the night light (wlsunset), and saying what it is doing.

wlsunset takes everything when it starts and reports nothing, so nightForge keeps a small record in
the session's runtime folder: the process it started and the mode it put it in. A change restarts
it fresh; Warm Now / Daylight Now then nudge it with its own signal (SIGUSR1 cycles forced day →
forced warm → automatic), from a known start, so the count is always right. Stopping it gives the
screens their colours back (Sway restores them when wlsunset lets go).

A process is stopped by the number nightForge saved when it started it, or (once, for the
night light hypeForge started before nightForge) by its exact program name: never by searching
command lines.
"""

from __future__ import annotations

import os
import signal
import subprocess
import time
from datetime import date, datetime, timedelta
from pathlib import Path

from .settings import Settings
from .sun import sun_times

PROGRAM = os.environ.get("NIGHTFORGE_WLSUNSET", "wlsunset")
RUNTIME = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "nightforge"
PIDFILE = RUNTIME / "wlsunset.pid"
MODEFILE = RUNTIME / "mode"                     # auto · warm · day
STATE = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "nightforge"
LOG = STATE / "wlsunset.log"
NUDGES = {"auto": 0, "day": 1, "warm": 2}        # SIGUSR1s from a fresh start


class Trouble(RuntimeError):
    """The night light could not be started; the message says why in plain words."""


def _alive(pid: int) -> bool:
    """Running, and the night light (a finished process waiting to be collected doesn't count)."""
    try:
        os.waitpid(pid, os.WNOHANG)          # collect it if nightForge started it and it ended
    except ChildProcessError:
        pass
    try:
        with open(f"/proc/{pid}/stat") as f:
            if f.read().rsplit(")", 1)[1].split()[0] == "Z":
                return False
        with open(f"/proc/{pid}/comm") as f:
            return f.read().strip() == os.path.basename(PROGRAM)[:15]
    except (OSError, IndexError):
        return False


def running_pid() -> int | None:
    try:
        pid = int(PIDFILE.read_text())
    except (OSError, ValueError):
        return None
    return pid if _alive(pid) else None


def mode() -> str:
    try:
        m = MODEFILE.read_text().strip()
    except OSError:
        return "auto"
    return m if m in NUDGES else "auto"


def _others() -> list[int]:
    """Night lights nightForge didn't start (hypeForge's old login line): by exact program name,
    this user's only."""
    try:
        out = subprocess.run(["pgrep", "-x", "-u", str(os.getuid()), os.path.basename(PROGRAM)[:15]],
                             capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [int(p) for p in out.split() if p.isdigit()]


def stop() -> None:
    pids = set(_others())
    mine = running_pid()
    if mine:
        pids.add(mine)
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    deadline = time.monotonic() + 3
    while any(_alive(p) for p in pids) and time.monotonic() < deadline:
        time.sleep(0.05)
    PIDFILE.unlink(missing_ok=True)


def start(settings: Settings, want: str = "auto", warmth: int | None = None) -> int | None:
    """(Re)start the night light as `settings` say, in mode `want`. Switched off: it is stopped
    and stays stopped. Returns the new process number, or None when it is off."""
    RUNTIME.mkdir(parents=True, exist_ok=True)
    stop()
    want = want if want in NUDGES else "auto"
    MODEFILE.write_text(want)
    if not settings.enabled:
        return None
    if want == "day":
        return None                              # Daylight Now: nothing warms the screens at all
    STATE.mkdir(parents=True, exist_ok=True)
    args = settings.wlsunset_args(warmth)
    with open(LOG, "a") as log:
        log.write(f"--- {datetime.now():%Y-%m-%d %H:%M:%S} {want}: {PROGRAM} {' '.join(args)}\n")
    # Started on its own (its own session, output to the log), so it outlives nightForge:
    # the night light keeps running after the app or the tray closes.
    try:
        pid = os.posix_spawnp(PROGRAM, [PROGRAM, *args], os.environ, setsid=True, file_actions=[
            (os.POSIX_SPAWN_OPEN, 0, os.devnull, os.O_RDONLY, 0),
            (os.POSIX_SPAWN_OPEN, 1, str(LOG), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644),
            (os.POSIX_SPAWN_DUP2, 1, 2)])
    except FileNotFoundError:
        raise Trouble("wlsunset isn't installed. On KognogOS: nog install wlsunset") from None
    time.sleep(0.4)
    done, status = os.waitpid(pid, os.WNOHANG)
    if done:
        raise Trouble(f"wlsunset stopped right away: {last_line()}")
    PIDFILE.write_text(str(pid))
    for _ in range(NUDGES[want]):
        time.sleep(0.15)
        os.kill(pid, signal.SIGUSR1)
    return pid


def last_line() -> str:
    try:
        lines = [l for l in LOG.read_text().splitlines() if l and not l.startswith("---")]
        return lines[-1] if lines else "no reason given"
    except OSError:
        return "no reason given"


# -- what it is doing, in words -------------------------------------------------------------------

def _at(day: date, hhmm: str) -> datetime:
    h, m = (int(x) for x in hhmm.split(":"))
    return datetime(day.year, day.month, day.day, h, m).astimezone()


def turning_points(settings: Settings, now: datetime | None = None) -> tuple[datetime | None, datetime | None]:
    """(today's warm start, the next daylight start) around `now`; None where the sun doesn't set
    or rise (near the poles)."""
    now = now or datetime.now().astimezone()
    today = now.date()
    if settings.schedule == "fixed":
        warm, day = _at(today, settings.warm_from), _at(today, settings.day_from)
        if day <= warm:
            day += timedelta(days=1) if now >= day else timedelta()
        return warm, day
    rise, sset = sun_times(today, settings.latitude, settings.longitude)
    if rise is None:
        return None, None
    if now >= rise:
        rise = sun_times(today + timedelta(days=1), settings.latitude, settings.longitude)[0]
    return sset, rise


def is_warm_time(settings: Settings, now: datetime | None = None) -> bool:
    now = now or datetime.now().astimezone()
    today = now.date()
    if settings.schedule == "fixed":
        warm, day = _at(today, settings.warm_from), _at(today, settings.day_from)
        return (now >= warm or now < day) if warm > day else (warm <= now < day)
    rise, sset = sun_times(today, settings.latitude, settings.longitude)
    if rise is None:
        return False
    return now >= sset or now < rise


def status(settings: Settings, now: datetime | None = None) -> dict:
    """{"state": warm · day · off, "why": words, "running": bool, "mode": auto · warm · day}."""
    now = now or datetime.now().astimezone()
    m = mode()
    # its own, or one hypeForge's old login line started (before nightForge ran it)
    running = running_pid() is not None or bool(_others())
    if not settings.enabled:
        return {"state": "off", "why": "switched off", "running": running, "mode": m}
    if m == "warm" and running:
        return {"state": "warm", "why": f"Warm Now, {settings.warmth} K, until you pick Automatic", "running": True, "mode": m}
    if m == "day":
        return {"state": "day", "why": "Daylight Now, until you pick Automatic", "running": False, "mode": m}
    if not running:
        return {"state": "off", "why": "not running (it starts at login, or with Save)", "running": False, "mode": m}
    warm, day = turning_points(settings, now)
    if warm is None:
        return {"state": "day", "why": "no sunset here today", "running": True, "mode": m}
    if is_warm_time(settings, now):
        return {"state": "warm", "why": f"{settings.warmth} K since {warm:%H:%M} · daylight at {day:%H:%M}",
                "running": True, "mode": m}
    return {"state": "day", "why": f"warm again from {warm:%H:%M}", "running": True, "mode": m}
