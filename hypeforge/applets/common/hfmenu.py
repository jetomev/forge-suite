"""hypeForge applets · our pop-up lists (fuzzel in dmenu mode), one at a time.

Shared by the launcher, the workspace dropdown, the bell and the clipboard. Pressing the same
button (or key) again closes its list; opening another list closes the one on screen first
(Javier, 2026-10-05). Python standard library only.
"""

import os
import signal
import subprocess
import sys
from pathlib import Path

BACKDROP = Path(__file__).resolve().with_name("hfbackdrop.py")   # a click anywhere else closes the list

OPEN = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "hypeforge-menu.open"  # "<pid> <name>"


def close_open(name):
    """Close our list on screen, if any. True when it was `name`'s own: that press meant 'close'."""
    try:
        pid, owner = OPEN.read_text().split(maxsplit=1)
        pid = int(pid)
        if Path(f"/proc/{pid}/comm").read_text().strip() != "fuzzel":
            return False
        os.kill(pid, signal.SIGTERM)
        return owner.strip() == name
    except (OSError, ValueError):
        return False


def run(name, command, text):
    """Run fuzzel `command` with `text` on its input; its output, or None (Esc / closed)."""
    menu = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    OPEN.write_text(f"{menu.pid} {name}")
    shade = None
    if os.environ.get("WAYLAND_DISPLAY") and BACKDROP.exists():   # Javier, 2026-10-10: close on a click elsewhere
        try:
            shade = subprocess.Popen([sys.executable, str(BACKDROP), str(menu.pid)],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            shade = None
    out, _ = menu.communicate(text.encode())
    if shade is not None:
        shade.terminate()
        try:
            shade.wait(2)
        except subprocess.TimeoutExpired:
            shade.kill()
    try:
        if OPEN.read_text().split()[0] == str(menu.pid):
            OPEN.unlink()
    except (OSError, IndexError):
        pass
    if menu.returncode != 0 or not out.strip():
        return None
    return out.decode().rstrip("\n")
