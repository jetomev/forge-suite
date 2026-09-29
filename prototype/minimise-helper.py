#!/usr/bin/env python3
"""hypeForge prototype: park a window when the taskbar asks to minimise it (D-31).

Hyprland 0.56 has no minimise of its own. When a taskbar (Waybar's wlr/taskbar) asks to
minimise a window, Hyprland only announces it on its event socket as
    minimized>>ADDRESS,1
This helper listens for that and moves the window to the hidden workspace
"special:minimized". minimise.lua brings it back when it is activated again.
Hyprland 0.57 adds a Lua "minimize" event (hyprwm/Hyprland#16071); then this helper can go.
"""

import os
import socket
import subprocess
import sys

PARK = "special:minimized"


def socket_path() -> str:
    runtime = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if not sig:
        sig = sorted(os.listdir(os.path.join(runtime, "hypr")))[-1]
    return os.path.join(runtime, "hypr", sig, ".socket2.sock")


def park(address: str) -> None:
    lua = (f'hl.dispatch(hl.dsp.window.move({{ workspace = "{PARK}", follow = false, '
           f'window = "address:0x{address}" }}))')
    subprocess.run(["hyprctl", "eval", lua], check=False, capture_output=True)


def main() -> int:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(socket_path())
        buf = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                return 1  # Hyprland went away
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                event, _, data = line.decode(errors="replace").partition(">>")
                if event == "minimized":
                    address, _, state = data.partition(",")
                    if state == "1" and all(c in "0123456789abcdef" for c in address):
                        park(address)


if __name__ == "__main__":
    sys.exit(main())
