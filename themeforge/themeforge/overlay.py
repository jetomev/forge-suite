#!/usr/bin/env python3
"""The wallpaper preview, at full quality, drawn over the terminal (Javier, 2026-10-11: "I've seen apps
like superfile show image previews with great quality … there are other apps that do it, like w3m").

The w3m way, on Wayland: the terminal can't draw pictures, so this small program puts the picture
right over the spot where the preview's characters are. It's a see-through layer of the desktop
(gtk-layer-shell, like hypeForge's panels), not a window: Sway's window helpers never move or tuck
it, it never takes the keyboard, and clicks pass through it. It watches themeForge's window through
Sway and follows it; it hides whenever the window isn't the one in use, isn't on screen, or
themeForge says so (another page, a list open over the preview). It ends when themeForge does.

    overlay.py --pids P1,P2,… --cell W H --pad X Y [--centred]
    then, one JSON line each on its input:
      {"show": {"png": "/path.png", "cells": [col, row, cols, lines], "grid": [cols, lines]}}
      {"hide": true}
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import struct
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk, GtkLayerShell  # noqa: E402

GET_TREE = 4
LOG = os.environ.get("THEMEFORGE_OVERLAY_LOG")          # the bench reads where it drew


def sway_tree() -> dict | None:
    path = os.environ.get("SWAYSOCK")
    if not path:
        return None
    try:
        with socket.socket(socket.AF_UNIX) as s:
            s.connect(path)
            s.sendall(b"i3-ipc" + struct.pack("=II", 0, GET_TREE))
            head = s.recv(14, socket.MSG_WAITALL)
            size, _ = struct.unpack("=II", head[6:])
            return json.loads(s.recv(size, socket.MSG_WAITALL))
    except (OSError, ValueError, struct.error):
        return None


def find_window(tree: dict, pids: set[int]):
    """(the terminal's window, the output it's on), by the process numbers that lead to themeForge."""
    def walk(node, output):
        if node.get("type") == "output":
            output = node
        if node.get("pid") in pids and node.get("type") in ("con", "floating_con"):
            return node, output
        for child in node.get("nodes", []) + node.get("floating_nodes", []):
            found = walk(child, output)
            if found:
                return found
        return None
    return walk(tree, None) or (None, None)


def place(win: dict, cells, pad, centred: bool, grid, cw: float, ch: float) -> tuple[int, int, int, int]:
    """The picture's spot on the desktop: the preview's character cells, in pixels, the screen's
    shape (16:9 of the output) fitted inside them and centred."""
    rx = win["rect"]["x"] + win["window_rect"]["x"]
    ry = win["rect"]["y"] + win["window_rect"]["y"]
    if centred:
        ox = rx + (win["window_rect"]["width"] - grid[0] * cw) / 2
        oy = ry + (win["window_rect"]["height"] - grid[1] * ch) / 2
    else:
        ox, oy = rx + pad[0], ry + pad[1]
    col, row, cols, lines = cells
    x, y, w, h = ox + col * cw, oy + row * ch, cols * cw, lines * ch
    return round(x), round(y), round(w), round(h)


def fitted(box: tuple[int, int, int, int], shape: tuple[int, int]) -> tuple[int, int, int, int]:
    x, y, w, h = box
    scale = min(w / shape[0], h / shape[1])
    fw, fh = max(1, int(shape[0] * scale)), max(1, int(shape[1] * scale))
    return x + (w - fw) // 2, y + (h - fh) // 2, fw, fh


class Overlay:
    def __init__(self, pids: set[int], cell: tuple[float, float], pad: tuple[float, float], centred: bool):
        self.pids, self.cell, self.pad, self.centred = pids, cell, pad, centred
        self.want: dict | None = None
        self.drawn = None
        self.window = Gtk.Window()
        GtkLayerShell.init_for_window(self.window)
        GtkLayerShell.set_namespace(self.window, "themeforge-preview")
        GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_exclusive_zone(self.window, -1)
        GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.NONE)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.LEFT, True)
        self.image = Gtk.Image()
        self.window.add(self.image)
        self.window.connect("realize", self._click_through)
        GLib.io_add_watch(GLib.IOChannel.unix_new(sys.stdin.fileno()), GLib.PRIORITY_DEFAULT,
                          GLib.IOCondition.IN | GLib.IOCondition.HUP, self._read)
        GLib.timeout_add(150, self._tick)

    @staticmethod
    def _click_through(window):
        import cairo
        window.input_shape_combine_region(cairo.Region())       # clicks go to themeForge below

    def _read(self, channel, condition):
        line = sys.stdin.readline()
        if not line:                                             # themeForge ended
            Gtk.main_quit()
            return False
        try:
            msg = json.loads(line)
        except ValueError:
            return True
        self.want = msg.get("show") if "show" in msg else None
        self._tick()
        return True

    def _monitor(self, output: dict):
        display = Gdk.Display.get_default()
        for i in range(display.get_n_monitors()):
            m = display.get_monitor(i)
            g = m.get_geometry()
            if (g.x, g.y) == (output["rect"]["x"], output["rect"]["y"]):
                return m
        return None

    def _hide(self):
        if self.drawn is not None:
            self.window.hide()
            self.drawn = None
            self._log({"hidden": True})

    def _tick(self) -> bool:
        tree = sway_tree() if self.want else None
        win, output = find_window(tree, self.pids) if tree else (None, None)
        why = ("nothing to show" if not self.want else "no answer from Sway" if not tree else
               "themeForge's window not found" if not win else "not the window in use" if not win.get("focused") else
               "not on screen" if not win.get("visible", True) else "")
        if why != getattr(self, "why", None):
            self.why = why
            self._log({"why": why or "showing"})
        if why:
            self._hide()
            return True
        box = place(win, self.want["cells"], self.pad, self.centred, self.want["grid"], *self.cell)
        try:
            pic = GdkPixbuf.Pixbuf.new_from_file(self.want["png"])
        except GLib.Error as e:
            why = f"the picture couldn't be read: {e.message}"
            if why != self.why:
                self.why = why
                self._log({"why": why})
            self._hide()
            return True
        x, y, w, h = fitted(box, (pic.get_width(), pic.get_height()))
        key = (self.want["png"], x, y, w, h, output["name"])
        if key == self.drawn:
            return True
        monitor = self._monitor(output)
        if self.drawn is None or self.drawn[5] != output["name"]:
            self.window.hide()                                    # a layer surface changes screen unmapped
            if monitor is not None:
                GtkLayerShell.set_monitor(self.window, monitor)
        GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.LEFT, x - output["rect"]["x"])
        GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.TOP, y - output["rect"]["y"])
        self.image.set_from_pixbuf(pic.scale_simple(w, h, GdkPixbuf.InterpType.BILINEAR))
        self.window.set_size_request(w, h)
        self.window.resize(w, h)
        self.window.show_all()
        self.drawn = key
        self._log({"shown": [x, y, w, h], "output": output["name"]})
        return True

    @staticmethod
    def _log(what: dict):
        import time
        what = {**what, "t": round(time.monotonic(), 2)}
        if LOG:
            with open(LOG, "a") as f:
                f.write(json.dumps(what) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pids", required=True)
    ap.add_argument("--cell", nargs=2, type=float, required=True)
    ap.add_argument("--pad", nargs=2, type=float, default=(0, 0))
    ap.add_argument("--centred", action="store_true")
    a = ap.parse_args()
    if not GtkLayerShell.is_supported():
        return 1
    Overlay._log({"started": os.getpid()})
    Overlay({int(p) for p in a.pids.split(",") if p}, tuple(a.cell), tuple(a.pad), a.centred)
    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
