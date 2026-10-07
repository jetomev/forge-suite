#!/usr/bin/env python3
"""sudoForge — one password box for every admin request on the Sway desktop.

    sudoforge service   run for the session (hypeForge starts it at login)
    sudoforge setup     tell sudo to use sudoForge for `sudo -A` (asks for your password once)
    sudoforge undo      take that back out of sudo's settings
    sudoforge status    what is running and set up, in plain words
"""

import os
import socket
import subprocess
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)

from sudoforge import __version__  # noqa: E402
from sudoforge import sudoconf  # noqa: E402

ASKPASS = os.path.join(HERE, "sudoforge-askpass")
ROOT_PART = os.path.join(HERE, "sudoforge", "sudoconf.py")


def as_admin(*args: str) -> int:
    """sudo.conf is a system file: changed through polkit, so sudoForge's own box asks."""
    return subprocess.call(["pkexec", "/usr/bin/python3", "-I", ROOT_PART, *args])


def status() -> int:
    from sudoforge.service import runtime_dir
    sock = runtime_dir() / "service.sock"
    running = False
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.connect(str(sock))
        running = True
    except OSError:
        pass
    finally:
        s.close()
    try:
        with open(sudoconf.CONF) as f:
            text = f.read()
    except OSError:
        text = ""
    print(f"sudoForge {__version__}")
    print(f"  service:  {'running in this session' if running else 'not running'}")
    other = sudoconf.current_askpass(text)
    if sudoconf.applied(text, ASKPASS):
        print("  sudo -A:  asks in sudoForge's box (set in /etc/sudo.conf)")
    elif other:
        print(f"  sudo -A:  uses another helper ({other})")
    else:
        print("  sudo -A:  not set up (run: sudoforge setup)")
    return 0


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "status"
    if cmd == "service":
        from sudoforge.service import run
        return run()
    if cmd == "setup":
        return as_admin("apply", ASKPASS)
    if cmd == "undo":
        return as_admin("undo")
    if cmd == "status":
        return status()
    if cmd in ("-V", "--version"):
        print(f"sudoForge {__version__}")
        return 0
    print(__doc__)
    return 0 if cmd in ("-h", "--help", "help") else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
