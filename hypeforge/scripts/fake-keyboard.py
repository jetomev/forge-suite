#!/usr/bin/env python3
"""A keyboard for the hidden benches: hold, tap and let go of keys, through Sway's virtual-keyboard
support (the zwp_virtual_keyboard_v1 extension), so Sway's key bindings and the program with the
keyboard get real key presses, exactly as from a keyboard. The companion of fake-pointer.py.
Python standard library, plus `xkbcli` (libxkbcommon's tool, already on the system) for the layout.

    fake-keyboard.py STEP...     steps: down:KEY  up:KEY  tap:KEY  wait:SECONDS
    e.g. fake-keyboard.py down:alt tap:tab wait:0.6 tap:tab up:alt

Keys: alt, shift, ctrl, super, tab, esc, enter, left, right, up, down, space, f10, 0-9, a-z.
Needs WAYLAND_DISPLAY (and XDG_RUNTIME_DIR) of the Sway to type in.
"""
from __future__ import annotations

import array
import os
import socket
import struct
import subprocess
import sys
import time

# a virtual keyboard tells Sway itself which modifiers are held (Sway doesn't work it out from the
# keys): the standard masks, Shift 1, Control 4, Alt (Mod1) 8, Super (Mod4) 64
MODS = {"shift": 1, "ctrl": 4, "alt": 8, "super": 64}
KEYS = {"alt": 56, "shift": 42, "ctrl": 29, "super": 125, "tab": 15, "esc": 1, "enter": 28,
        "left": 105, "right": 106, "up": 103, "down": 108, "space": 57, "f10": 68,
        **{str(d): 2 + (d - 1) % 10 for d in range(1, 11)},            # 1…9 and 0 (the "10")
        **dict(zip("qwertyuiop", range(16, 26))), **dict(zip("asdfghjkl", range(30, 39))),
        **dict(zip("zxcvbnm", range(44, 51)))}
KEYS["0"] = KEYS.pop("10")


class Wire:
    def __init__(self, path: str):
        self.s = socket.socket(socket.AF_UNIX)
        self.s.connect(path)
        self.buf = b""

    def send(self, obj: int, op: int, *args, fd: int | None = None):
        body = b""
        for a in args:
            if isinstance(a, str):
                raw = a.encode() + b"\0"
                body += struct.pack("=I", len(raw)) + raw + b"\0" * (-len(raw) % 4)
            else:
                body += struct.pack("=I", a & 0xFFFFFFFF)
        msg = struct.pack("=II", obj, ((8 + len(body)) << 16) | op) + body
        if fd is None:
            self.s.sendall(msg)
        else:                                            # a file handle travels beside the message
            self.s.sendmsg([msg], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", [fd]))])

    def events(self):
        while True:
            while len(self.buf) < 8 or len(self.buf) < (struct.unpack("=II", self.buf[:8])[1] >> 16):
                chunk = self.s.recv(65536)
                if not chunk:
                    return
                self.buf += chunk
            obj, word = struct.unpack("=II", self.buf[:8])
            size = word >> 16
            yield obj, word & 0xFFFF, self.buf[8:size]
            self.buf = self.buf[size:]

    def roundtrip(self, callback_id: int, on_event=None):
        self.send(1, 0, callback_id)                     # wl_display.sync
        for obj, op, data in self.events():
            if obj == callback_id:
                return
            if on_event:
                on_event(obj, op, data)


def string_at(data: bytes, at: int) -> tuple[str, int]:
    n = struct.unpack("=I", data[at:at + 4])[0]
    return data[at + 4:at + 4 + n - 1].decode(), at + 4 + n + (-n % 4)


def main(steps: list[str]) -> int:
    if not steps:
        print(__doc__)
        return 2
    run = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
    w = Wire(os.path.join(run, os.environ.get("WAYLAND_DISPLAY", "wayland-1")))
    w.send(1, 1, 2)                                      # wl_display.get_registry → 2
    globs = {}

    def seen(obj, op, data):
        if obj == 2 and op == 0:
            name = struct.unpack("=I", data[:4])[0]
            iface, _ = string_at(data, 4)
            globs[iface] = name
    w.roundtrip(3, seen)
    if "zwp_virtual_keyboard_manager_v1" not in globs:
        print("fake-keyboard: this compositor offers no virtual keyboard", file=sys.stderr)
        return 1
    w.send(2, 0, globs["wl_seat"], "wl_seat", 1, 4)      # wl_registry.bind → seat 4
    w.send(2, 0, globs["zwp_virtual_keyboard_manager_v1"], "zwp_virtual_keyboard_manager_v1", 1, 5)
    w.send(5, 0, 4, 6)                                   # create_virtual_keyboard(seat) → 6
    keymap = subprocess.run(["xkbcli", "compile-keymap", "--layout", "us"], capture_output=True,
                            check=True).stdout + b"\0"
    fd = os.memfd_create("fake-keyboard-keymap")
    os.write(fd, keymap)
    w.send(6, 0, 1, len(keymap), fd=fd)                  # keymap(XKB_V1, fd, size)
    os.close(fd)
    w.roundtrip(7)
    time.sleep(0.3)                                      # the seat gains its keyboard
    ms = lambda: int(time.monotonic() * 1000) & 0xFFFFFFFF
    cb = [8]

    held = {"mask": 0}

    def key(name: str, state: int):
        if name not in KEYS:
            raise SystemExit(f"fake-keyboard: no key {name!r} (keys: {', '.join(KEYS)})")
        w.send(6, 1, ms(), KEYS[name], state)            # key(time, key, pressed/released)
        if name in MODS:
            held["mask"] = held["mask"] | MODS[name] if state else held["mask"] & ~MODS[name]
            w.send(6, 2, held["mask"], 0, 0, 0)          # modifiers(depressed, latched, locked, group)
        w.roundtrip(cb[0])
        cb[0] += 1
        time.sleep(0.05)

    for step in steps:
        what, _, arg = step.partition(":")
        if what == "wait":
            time.sleep(float(arg))
        elif what == "down":
            key(arg, 1)
        elif what == "up":
            key(arg, 0)
        elif what == "tap":
            key(arg, 1)
            key(arg, 0)
        else:
            print(f"fake-keyboard: no step {step!r}", file=sys.stderr)
            return 2
    time.sleep(0.3)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
