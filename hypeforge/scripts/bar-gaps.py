#!/usr/bin/env python3
"""Measure the space between the pieces on a bar picture (2026-10-17, Javier: "inSync and dropbox look very
close, and all others seem like have different distances"). Finds the drawn parts (icons, numbers) along
a strip of the bar and prints each one and the gap to the next, in pixels, so spacing is checked by
numbers, not by eye.

    bar-gaps.py PICTURE [--box X,Y,W,H] [--join N]

--box: the strip to read (the island you care about); --join: drawn parts closer than N px are one piece
(an icon and its number). The background is the strip's most common colour; only the strip's middle
half is read, so an island's outline never counts.
"""

import argparse
from collections import Counter

from PIL import Image


def parts(img, join: int = 0) -> list[tuple[int, int]]:
    img = img.convert("RGB")
    w, h = img.size
    px = list(img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata())
    bg = Counter(px).most_common(1)[0][0]
    far = lambda p: sum(abs(a - b) for a, b in zip(p, bg)) > 120
    rows = range(h // 4, h - h // 4)               # the middle half: never an island's outline
    cols = [any(far(img.getpixel((x, y))) for y in rows) for x in range(w)]
    runs, x = [], 0
    while x < w:
        if cols[x]:
            s = x
            while x < w and cols[x]:
                x += 1
            runs.append((s, x - 1))
        else:
            x += 1
    out = []
    for r in runs:
        if out and r[0] - out[-1][1] - 1 <= join:
            out[-1] = (out[-1][0], r[1])
        else:
            out.append(r)
    return out


def gaps(runs) -> list[int]:
    return [b[0] - a[1] - 1 for a, b in zip(runs, runs[1:])]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("picture")
    ap.add_argument("--box")
    ap.add_argument("--join", type=int, default=0)
    a = ap.parse_args()
    img = Image.open(a.picture)
    if a.box:
        x, y, w, h = map(int, a.box.split(","))
        img = img.crop((x, y, x + w, y + h))
    r = parts(img, a.join)
    print("parts:", r)
    print("gaps: ", gaps(r))
