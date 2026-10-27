"""hypeForge applets · telling the top bar (Waybar) to redraw.

Shared by every applet that draws on the bar, Python standard library only.
"""

import json
import os
import signal
import re
import shutil
import subprocess
import time
from pathlib import Path

SOUND_SETTLE = 20.0        # seconds: a WirePlumber this old is settled, speakers or not
SOUND_WAIT = 20.0          # the longest a reload waits for it


def bar_listens(pid, sig):
    """True once Waybar has set up its handler for `sig`. Before that, the signal's default
    action ends the program: at login a redraw reached a bar still starting, and killed it (F-45)."""
    try:
        status = Path(f"/proc/{pid}/status").read_text()
    except OSError:
        return False
    caught = int(re.search(r"^SigCgt:\s*([0-9a-f]+)", status, re.M).group(1), 16)
    return bool(caught >> (sig - 1) & 1)


def forget_pieces(sig):
    """Throw away the kept answers of the pieces redrawn on this signal (applets/common/hfpiece), so the
    bar computes them fresh."""
    n = int(sig) - int(signal.SIGRTMIN)
    folder = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "hypeforge-pieces"
    for f in folder.glob(f"sig{n}-*"):
        if not f.name.endswith(".lock"):
            f.unlink(missing_ok=True)


NO_ANSWER = object()       # asked, and no answer in time: something is busy, not absent


def _said(cmd):
    """What a quick command printed; None when it failed; NO_ANSWER when it hung."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
    except subprocess.TimeoutExpired:
        return NO_ANSWER
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def process_age(pid):
    """Seconds since the process started, or None."""
    try:
        start = int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[19])
        up = float(Path("/proc/uptime").read_text().split()[0])
    except (OSError, ValueError, IndexError):
        return None
    return up - start / os.sysconf("SC_CLK_TCK")


def sound_settled():
    """WirePlumber is done starting. Waybar's sound piece (wireplumber) takes the WHOLE bar down when the bar
    reloads while WirePlumber is still starting (F-86: Javier's logins of 10-25 and 10-26; reproduced
    10-26 on a hidden screen with a private sound service, 4/4 dead, and 0/4 with no reload, 0/24 once
    settled). Settled = it has chosen the default output, or it has run SOUND_SETTLE s (a machine with no
    speakers never chooses one). No WirePlumber installed, or no sound service answering: nothing to race."""
    if not shutil.which("wpctl") or not shutil.which("pw-metadata"):
        return True
    said = _said(["pw-metadata", "-n", "default"])
    if said is NO_ANSWER:              # WirePlumber holds that record: a hang means it is busy starting
        return False
    if said is None:
        return True
    if "default.audio.sink" in said:
        return True
    dump = _said(["pw-dump"])
    if dump is NO_ANSWER:
        return False
    try:
        clients = json.loads(dump or "[]")
    except ValueError:
        return True
    ages = []
    for o in clients:
        props = (o.get("info") or {}).get("props") or {}
        if str(o.get("type", "")).endswith(":Client") and str(props.get("application.name", "")).startswith("WirePlumber"):
            age = process_age(props.get("application.process.id", ""))
            if age is not None:
                ages.append(age)
    return bool(ages) and max(ages) >= SOUND_SETTLE


def wait_for_sound(longest=None):
    """Hold a reload until sound has settled (at most `longest` s, then go anyway). Instant once settled."""
    longest = SOUND_WAIT if longest is None else longest
    deadline = time.monotonic() + longest
    while not sound_settled():
        if time.monotonic() > deadline:
            return False
        time.sleep(0.25)
    return True


def signal_bar(sig, wait=5.0):
    """Send `sig` to every running Waybar, each only once it listens for it (up to `wait` s). A reload
    (SIGUSR2) waits for sound to settle first (F-86)."""
    forget_pieces(sig)
    if sig == signal.SIGUSR2:
        wait_for_sound()
    for pid in (int(p) for p in os.popen("pgrep -x waybar").read().split()):
        deadline = time.monotonic() + wait
        while not bar_listens(pid, sig):
            if time.monotonic() > deadline or not Path(f"/proc/{pid}").exists():
                break
            time.sleep(0.05)
        else:
            try:
                os.kill(pid, sig)
            except ProcessLookupError:
                pass
