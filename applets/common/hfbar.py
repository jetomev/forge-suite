"""hypeForge applets · telling the top bar (Waybar) to redraw.

Shared by every applet that draws on the bar, Python standard library only.
"""

import os
import re
import time
from pathlib import Path


def bar_listens(pid, sig):
    """True once Waybar has set up its handler for `sig`. Before that, the signal's default
    action ends the program: at login a redraw reached a bar still starting, and killed it (F-45)."""
    try:
        status = Path(f"/proc/{pid}/status").read_text()
    except OSError:
        return False
    caught = int(re.search(r"^SigCgt:\s*([0-9a-f]+)", status, re.M).group(1), 16)
    return bool(caught >> (sig - 1) & 1)


def signal_bar(sig, wait=5.0):
    """Send `sig` to every running Waybar, each only once it listens for it (up to `wait` s)."""
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
