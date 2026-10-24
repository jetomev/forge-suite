#!/usr/bin/env python3
"""A mouse for the hidden benches: move to a spot and click, through Sway's virtual-pointer support.

The screen-less Sway the benches start has no mouse, so `swaymsg seat - cursor press` reaches no
program (10-10: a click on macOS's menu bar opened nothing on the hidden screen). This speaks the
Wayland protocol directly (the zwlr_virtual_pointer_v1 extension, which Sway offers), so the bar
and the panels get a real pointer, exactly as from a mouse. Python standard library only.

    fake-pointer.py X Y [--click] [--button left|middle|right] [--drag X2 Y2] [--hold S] [--rest S] [--width W --height H]
                                                                       (X, Y in the screens' layout, pixels)

--drag presses at X Y, moves to X2 Y2 in small steps and lets go there (a window dragged by its title
bar, 2026-10-17).

Needs WAYLAND_DISPLAY (and XDG_RUNTIME_DIR) of the Sway to click in.
"""
from __future__ import annotations

import argparse
import os
import socket
import struct
import sys
import time

BTN_LEFT = 0x110
BUTTONS = {"left": 0x110, "right": 0x111, "middle": 0x112}


class Wire:
    def __init__(self, path: str):
        self.s = socket.socket(socket.AF_UNIX)
        self.s.connect(path)
        self.buf = b""

    def send(self, obj: int, op: int, *args):
        body = b""
        for a in args:
            if isinstance(a, str):
                raw = a.encode() + b"\0"
                body += struct.pack("=I", len(raw)) + raw + b"\0" * (-len(raw) % 4)
            else:
                body += struct.pack("=I", a & 0xFFFFFFFF)
        self.s.sendall(struct.pack("=II", obj, ((8 + len(body)) << 16) | op) + body)

    def events(self):
        """(object, opcode, payload) as they come."""
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("x", type=int)
    ap.add_argument("y", type=int)
    ap.add_argument("--click", action="store_true")
    ap.add_argument("--button", choices=list(BUTTONS), default="left")
    ap.add_argument("--drag", type=int, nargs=2, metavar=("X2", "Y2"))
    ap.add_argument("--width", type=int, default=2560, help="the screens' layout, all screens together")
    ap.add_argument("--height", type=int, default=1440)
    ap.add_argument("--hold", type=float, default=0.5, help="seconds the mouse stays plugged in afterwards")
    ap.add_argument("--rest", type=float, default=0.3, help="seconds the mouse rests before the click (a hover tip shows)")
    a = ap.parse_args()
    run = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
    w = Wire(os.path.join(run, os.environ.get("WAYLAND_DISPLAY", "wayland-1")))
    w.send(1, 1, 2)                                      # wl_display.get_registry → 2
    globs = {}

    def seen(obj, op, data):
        if obj == 2 and op == 0:                         # wl_registry.global(name, interface, version)
            name = struct.unpack("=I", data[:4])[0]
            iface, _ = string_at(data, 4)
            globs[iface] = name
    w.roundtrip(3, seen)
    if "zwlr_virtual_pointer_manager_v1" not in globs:
        print("fake-pointer: this compositor offers no virtual pointer", file=sys.stderr)
        return 1
    w.send(2, 0, globs["wl_seat"], "wl_seat", 1, 4)      # wl_registry.bind → seat 4
    w.send(2, 0, globs["zwlr_virtual_pointer_manager_v1"], "zwlr_virtual_pointer_manager_v1", 1, 5)
    w.send(5, 0, 4, 6)                                   # create_virtual_pointer(seat) → 6
    w.roundtrip(7)
    time.sleep(0.3)                                      # the seat gains its pointer
    ms = lambda: int(time.monotonic() * 1000) & 0xFFFFFFFF
    sync = iter(range(8, 10000))                         # a new callback id for every round trip

    def move(x, y):
        w.send(6, 1, ms(), x, y, a.width, a.height)      # motion_absolute
        w.send(6, 4)                                     # frame
        w.roundtrip(next(sync))

    def button(state):
        w.send(6, 2, ms(), BUTTONS[a.button], state)     # 1 press, 0 let go
        w.send(6, 4)
        w.roundtrip(next(sync))

    move(a.x, a.y)
    if a.click or a.drag:
        time.sleep(a.rest)
        button(1)
        time.sleep(0.15)
        if a.drag:
            steps = 12
            for i in range(1, steps + 1):
                move(a.x + (a.drag[0] - a.x) * i // steps, a.y + (a.drag[1] - a.y) * i // steps)
                time.sleep(0.03)
            time.sleep(0.15)
        button(0)
        time.sleep(0.15)
    time.sleep(a.hold)                                   # unplugged when this ends; a menu may close with it
    return 0


if __name__ == "__main__":
    sys.exit(main())
