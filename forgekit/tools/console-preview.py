#!/usr/bin/env python3
"""Show what a Forge app looks like on a plain Linux text console (tty3).

Runs a command in a pseudo-terminal with TERM=linux, the way it would run after
Ctrl+Alt+F3, feeds everything it draws to a terminal emulator (pyte), and saves
a PNG using the Linux console's own 16 colours. Every character the console font
cannot draw is painted as a red box, because on a real console it would be a
blank or a stray symbol.

    python tools/console-preview.py --out shot.png -- python examples/demo.py
    python tools/console-preview.py --keys "wait:2 ctrl+e wait:1" --out menu.png -- python examples/demo.py

It also prints a summary: the colours actually used and every character the font
lacks, with a count, and every letter drawn in its own background colour (the
console shows underline as cyan and italic as green, which can hide a letter).
Exit status 3 for undrawable characters, 4 for invisible ones, so a test fails.

Needs python-pyte (Arch: `nog install python-pyte`) and Pillow.
"""
from __future__ import annotations

import argparse
import fcntl
import gzip
import os
import pty
import select
import signal
import struct
import sys
import termios
import time
from collections import Counter

import pyte
from PIL import Image, ImageDraw, ImageFont

# The Linux console's default palette (drivers/tty/vt/vt.c, default_red/grn/blu).
CONSOLE_RGB = {
    "black": (0x00, 0x00, 0x00), "red": (0xAA, 0x00, 0x00), "green": (0x00, 0xAA, 0x00),
    "brown": (0xAA, 0x55, 0x00), "blue": (0x00, 0x00, 0xAA), "magenta": (0xAA, 0x00, 0xAA),
    "cyan": (0x00, 0xAA, 0xAA), "white": (0xAA, 0xAA, 0xAA),
    "brightblack": (0x55, 0x55, 0x55), "brightred": (0xFF, 0x55, 0x55),
    "brightgreen": (0x55, 0xFF, 0x55), "brightbrown": (0xFF, 0xFF, 0x55),
    "brightblue": (0x55, 0x55, 0xFF), "brightmagenta": (0xFF, 0x55, 0xFF),
    "brightcyan": (0x55, 0xFF, 0xFF), "brightwhite": (0xFF, 0xFF, 0xFF),
}
# pyte names the basic colours like this; "default" is the console's grey on black.
PYTE_ALIAS = {"yellow": "brown", "brightyellow": "brightbrown"}

KEYS = {
    "enter": "\r", "esc": "\x1b", "tab": "\t", "space": " ", "backspace": "\x7f",
    "up": "\x1b[A", "down": "\x1b[B", "right": "\x1b[C", "left": "\x1b[D",
    # what the Linux console sends for F1-F4 (infocmp linux: kf1=\E[[A …)
    "f1": "\x1b[[A", "f2": "\x1b[[B", "f3": "\x1b[[C", "f4": "\x1b[[D",
}

DEFAULT_FONT = "/usr/share/kbd/consolefonts/default8x16.psfu.gz"
DRAW_FONT = "/usr/share/fonts/TTF/DejaVuSansMono.ttf"


def console_font_chars(path: str) -> set[int]:
    """Every Unicode code point the console font has a glyph for (PSF1 or PSF2)."""
    data = (gzip.open if path.endswith(".gz") else open)(path, "rb").read()
    chars: set[int] = set()
    if data[:2] == b"\x36\x04":  # PSF1
        mode, size = data[2], data[3]
        count = 512 if mode & 1 else 256
        table = data[4 + count * size:]
        if not mode & 2:
            return set(range(256))
        for i in range(0, len(table) - 1, 2):
            u = struct.unpack("<H", table[i:i + 2])[0]
            if u not in (0xFFFF, 0xFFFE):
                chars.add(u)
        return chars
    _magic, _ver, header, flags, count, per_glyph, _h, _w = struct.unpack("<8I", data[:32])
    if not flags & 1:
        return set(range(count))
    table = data[header + count * per_glyph:]
    i = 0
    while i < len(table):
        b = table[i]
        if b in (0xFF, 0xFE):
            i += 1
            continue
        n = 1 if b < 0x80 else 2 if b >> 5 == 6 else 3 if b >> 4 == 14 else 4
        try:
            chars.add(ord(table[i:i + n].decode("utf-8")))
        except (UnicodeDecodeError, TypeError):
            pass
        i += n
    return chars


def key_bytes(token: str) -> bytes:
    if token.startswith("ctrl+") and len(token) == 6:
        return bytes([ord(token[5].lower()) & 0x1F])
    if token in KEYS:
        return KEYS[token].encode()
    return token.encode()


def run(cmd: list[str], cols: int, rows: int, script: list[str], settle: float) -> pyte.Screen:
    screen = pyte.Screen(cols, rows)
    stream = pyte.ByteStream(screen)
    pid, fd = pty.fork()
    if pid == 0:
        env = dict(os.environ, TERM="linux", COLUMNS=str(cols), LINES=str(rows))
        env.pop("COLORTERM", None)
        os.execvpe(cmd[0], cmd, env)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))

    def pump(seconds: float) -> None:
        end = time.time() + seconds
        while time.time() < end:
            ready, _, _ = select.select([fd], [], [], 0.05)
            if ready:
                try:
                    chunk = os.read(fd, 65536)
                except OSError:
                    return
                if not chunk:
                    return
                stream.feed(chunk)

    pump(settle)
    for token in script:
        if token.startswith("wait:"):
            pump(float(token[5:]))
        else:
            os.write(fd, key_bytes(token))
            pump(0.4)
    pump(0.5)
    try:
        os.kill(pid, signal.SIGTERM)
        os.waitpid(pid, 0)
    except (ProcessLookupError, ChildProcessError):
        pass
    return screen


def rgb(colour: str, fallback: str) -> tuple[int, int, int]:
    if colour == "default":
        colour = fallback
    colour = PYTE_ALIAS.get(colour, colour)
    if colour in CONSOLE_RGB:
        return CONSOLE_RGB[colour]
    if len(colour) == 6:  # a 256-colour or true-colour value reached the console
        return tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4))
    return CONSOLE_RGB[fallback]


def render(screen: pyte.Screen, drawable: set[int], out: str) -> tuple[Counter, Counter, Counter]:
    cw, ch = 10, 20
    img = Image.new("RGB", (screen.columns * cw, screen.lines * ch), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(DRAW_FONT, 16)
    missing, fg_used, bg_used, invisible = Counter(), Counter(), Counter(), Counter()
    for y in range(screen.lines):
        line = screen.buffer[y]
        for x in range(screen.columns):
            c = line[x]
            fg, bg = c.fg, c.bg
            if c.bold and fg in CONSOLE_RGB and not fg.startswith("bright"):
                fg = "bright" + fg  # the console shows bold as the bright colour
            # the Linux console has no underline or italic: it shows them as
            # colours (vt.c: ulcolor cyan, itcolor green), keeping brightness
            if c.underscore:
                fg = ("bright" if fg.startswith("bright") else "") + "cyan"
            elif c.italics:
                fg = ("bright" if fg.startswith("bright") else "") + "green"
            if c.reverse:
                fg, bg = bg, fg
            f, b = rgb(fg, "white"), rgb(bg, "black")
            fg_used[fg] += 1
            bg_used[bg] += 1
            x0, y0 = x * cw, y * ch
            char = c.data or " "
            if char != " " and ord(char[0]) not in drawable:
                missing[char] += 1
                draw.rectangle([x0, y0, x0 + cw - 1, y0 + ch - 1], fill=(200, 0, 0))
                draw.text((x0 + 1, y0 + 1), "?", font=font, fill=(255, 255, 255))
                continue
            draw.rectangle([x0, y0, x0 + cw - 1, y0 + ch - 1], fill=b)
            if char != " ":
                draw.text((x0, y0 + 1), char, font=font, fill=f)
                # a block in its background colour is just a fill; a letter or a
                # line in its background colour is something the reader loses
                if f == b and not "\u2580" <= char <= "\u259f":
                    invisible[char] += 1
                    draw.rectangle([x0, y0, x0 + cw - 1, y0 + ch - 1], outline=(255, 0, 255))
    img.save(out)
    return missing, fg_used, bg_used, invisible


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="console-preview.png")
    ap.add_argument("--size", default="100x30", help="columns x rows (a 1024x768 console is 128x48)")
    ap.add_argument("--keys", default="", help='e.g. "wait:2 ctrl+e down enter wait:1"')
    ap.add_argument("--settle", type=float, default=3.0, help="seconds to let the app draw first")
    ap.add_argument("--font", default=DEFAULT_FONT, help="console font whose glyphs count as drawable")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd:
        ap.error("give the command to run after --")
    cols, rows = (int(v) for v in a.size.lower().split("x"))
    screen = run(cmd, cols, rows, a.keys.split(), a.settle)
    missing, fg, bg, invisible = render(screen, console_font_chars(a.font), a.out)
    print(f"saved {a.out} ({cols}x{rows}, TERM=linux)")
    print("foreground colours:", ", ".join(f"{k} {v}" for k, v in fg.most_common()))
    print("background colours:", ", ".join(f"{k} {v}" for k, v in bg.most_common()))
    status = 0
    if missing:
        print("UNDRAWABLE on the console font:", "  ".join(f"{k!r}×{v}" for k, v in missing.most_common()))
        status = 3
    else:
        print("every character on screen is in the console font")
    if invisible:
        print("INVISIBLE (same colour as its background):", "  ".join(f"{k!r}×{v}" for k, v in invisible.most_common()))
        status = status or 4
    else:
        print("every character is visible against its background")
    return status


if __name__ == "__main__":
    sys.exit(main())
