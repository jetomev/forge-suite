#!/usr/bin/env python3
"""Redraw a real Linux text console exactly, from a copy of /dev/vcsaN.

The kernel keeps every text console's contents in /dev/vcsaN: for each cell, the
glyph number it actually drew (from the console font) and its colours. Copy that
file off the machine (on a VM, for example `base64 /dev/vcsa3` through the qemu
guest agent), then:

    python tools/vcsa-shot.py vcsa3.bin console.png [font.psfu.gz]

draws it pixel for pixel with the console font's own glyphs and the console's
16 colours: the screen as the person in front of it sees it. Unlike
console-preview.py (an emulation), this is the real console's output. Used for
the v0.4.0 test on a KognogOS VM (2026-10-01).
"""
import gzip, struct, sys
from PIL import Image
data = open(sys.argv[1], "rb").read()
rows, cols = data[0], data[1]
cells = data[4:]
font = sys.argv[3] if len(sys.argv) > 3 else "/usr/share/kbd/consolefonts/default8x16.psfu.gz"
f = (gzip.open if font.endswith(".gz") else open)(font, "rb").read()
_m, _v, hs, _fl, n, bpg, gh, gw = struct.unpack("<8I", f[:32])
glyphs = [f[hs + i * bpg: hs + (i + 1) * bpg] for i in range(n)]
# VGA colour order (as stored in vcsa attributes), Linux default palette
VGA = [(0,0,0),(0,0,170),(0,170,0),(0,170,170),(170,0,0),(170,0,170),(170,85,0),(170,170,170),
       (85,85,85),(85,85,255),(85,255,85),(85,255,255),(255,85,85),(255,85,255),(255,255,85),(255,255,255)]
img = Image.new("RGB", (cols * gw, rows * gh)); px = img.load()
used = set()
for r in range(rows):
    for c in range(cols):
        ch, at = cells[(r * cols + c) * 2], cells[(r * cols + c) * 2 + 1]
        fg, bg = VGA[at & 0x0F], VGA[(at >> 4) & 0x07]
        used.add((at & 0x0F, (at >> 4) & 0x0F))
        g = glyphs[ch]
        for y in range(gh):
            bits = g[y]
            for x in range(gw):
                px[c * gw + x, r * gh + y] = fg if bits & (0x80 >> x) else bg
img = img.resize((img.width * 5 // 4, img.height * 5 // 4), Image.NEAREST)
img.save(sys.argv[2]); print(f"{cols}x{rows} console, {len(used)} colour pairs -> {sys.argv[2]}")
