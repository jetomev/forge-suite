#!/usr/bin/env python3
"""Lift the KognogOS "Tier Aware" wallpaper's artwork out of its originals, once, into two see-through
layers the look recolours for every colour theme (Javier, 2026-10-11: the Rice uses our KognogOS
backgrounds only, in the colour theme's variant; "Tier Aware!" is the design).

The emblem: the same art sits on black and on gray (166) in the originals, so each pixel's
see-through-ness is 1 - (gray - black) / 166 and its colour is black / that. (The White original
can't be used: its art sits about 20 pixels to the left and is slightly bigger.) The words: white on
the black original, so their brightness is how solid they are; the look paints them in the theme's
text colour.

    make-kognogos-layers.py        writes assets/wallpaper/kognogos-<design>-{emblem,words}.png + .json
                                   for both designs: tier-aware ("Semi" originals) and arch-distro ("Arch")
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path("/usr/share/wallpapers/kognog")
OUT = Path(__file__).resolve().parent.parent / "assets/wallpaper"


DESIGNS = {"tier-aware": ("Semi", "Semi-Rolling | Tier Aware"), "arch-distro": ("Arch", "Semi-Rolling Arch Distro")}


def main() -> int:
    for design, (src, words) in DESIGNS.items():
        lift(design, src, words)
    return 0


def lift(design: str, src: str, tagline: str):
    black = np.asarray(Image.open(SRC / f"Kognog OS {src} - Logo Black.png").convert("RGB")).astype(np.float64)
    gray = np.asarray(Image.open(SRC / f"Kognog OS {src} - Logo Gray.png").convert("RGB")).astype(np.float64)
    level = gray[5, 5].mean()                            # the Gray original's flat background
    h, w, _ = black.shape
    seen = np.where(np.abs(black).sum(2) > 24)
    y0, y1, x0, x1 = seen[0].min() - 4, seen[0].max() + 5, seen[1].min() - 4, seen[1].max() + 5
    # the emblem ends where the first column with no art comes after it
    cols = (np.abs(black[y0:y1, x0:x1]).sum(2) > 24).any(0)
    gap = next(i for i in range(10, len(cols)) if not cols[i] and cols[i - 1])
    split = x0 + gap + 2
    b, gr = black[y0:y1, x0:split], gray[y0:y1, x0:split]
    alpha = np.clip(1 - (gr - b).mean(2) / level, 0, 1)
    colour = np.clip(b / np.maximum(alpha, 1e-3)[..., None], 0, 255)
    emblem = np.dstack([colour, alpha * 255]).astype(np.uint8)
    words_a = np.clip(black[y0:y1, split:x1].max(2), 0, 255)
    words = np.dstack([np.full(words_a.shape + (3,), 255.0), words_a]).astype(np.uint8)
    OUT.mkdir(parents=True, exist_ok=True)
    Image.fromarray(emblem, "RGBA").save(OUT / f"kognogos-{design}-emblem.png", optimize=True)
    Image.fromarray(words, "RGBA").save(OUT / f"kognogos-{design}-words.png", optimize=True)
    (OUT / f"kognogos-{design}.json").write_text(json.dumps(
        {"canvas": [w, h], "emblem_at": [int(x0), int(y0)], "words_at": [int(split), int(y0)], "tagline": tagline,
         "from": f"Kognog OS {src} - Logo Black.png + Gray.png (KognogOS wallpapers)"}, indent=1) + "\n")
    print(f"{design}: emblem {emblem.shape[1]}x{emblem.shape[0]} at {x0},{y0}; words {words.shape[1]}x{words.shape[0]} at {split},{y0}")


if __name__ == "__main__":
    sys.exit(main())
