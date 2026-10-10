#!/usr/bin/env python3
"""Build Review 1 of the look program (the foundation): the 23 colour themes on a small
hypeForge desktop, the wallpapers, and Javier's questions. Reads the generated palettes,
writes index.html next to this file plus wallpapers/ (copies of the previews).

    python3 docs/design/look/review-1/build.py
"""
from __future__ import annotations

import base64
import io
import json
import pathlib
import shutil
import tomllib

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]                                  # hypeforge/
RES = ROOT / "docs/research/look-2026-10"
WALL = RES / "wallpapers/samples"

KEEP = {
    "surface": ["sunken", "bar", "base", "raised", "overlay", "hover"],
    "text": ["primary", "secondary", "muted"],
    "accent": ["base", "on", "hover", "text"],
    "border": ["subtle", "strong"],
    "window": ["focused", "unfocused", "urgent"],
    "bar": ["bg", "shade", "hover", "fg", "fg_dim", "active_bg", "active_fg"],
    "selection": ["bg", "fg"],
    "status": ["success", "on_success", "warning", "on_warning", "danger", "on_danger", "info", "on_info"],
    "term": ["bg", "fg", "red", "green", "yellow", "blue", "magenta", "cyan", "bright_black"],
}


def slim(theme: dict) -> dict:
    out = {"name": theme["meta"]["name"], "family": theme["meta"]["family"], "tone": theme["meta"]["tone"]}
    for group, keys in KEEP.items():
        for k in keys:
            out[f"{group}.{k}"] = theme[group][k]
    return out


def themes(path: pathlib.Path) -> tuple[list[str], dict]:
    d = tomllib.loads(path.read_text())
    return d["meta"]["order"], {s: slim(d["themes"][s]) for s in d["meta"]["order"]}


def emblem() -> str:
    im = Image.open(ROOT / "assets/kognogos-emblem.png").convert("RGBA").resize((40, 40), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    order, now = themes(RES / "palette/palettes.toml")
    _, lifted = themes(HERE / "data/mid-lifted.toml")
    lifted = {s: t for s, t in lifted.items() if t["tone"] == "mid"}
    (HERE / "wallpapers").mkdir(exist_ok=True)
    walls = []
    for f in sorted(WALL.glob("*.preview.png")):
        set_, mood = f.name.removesuffix(".preview.png").split("-", 1)
        shutil.copy(f, HERE / "wallpapers" / f.name)
        walls.append({"set": set_, "mood": mood, "src": f"wallpapers/{f.name}"})
    data = {"order": order, "now": now, "lifted": lifted, "walls": walls, "emblem": emblem()}
    page = (HERE / "template.html").read_text().replace("/*DATA*/null", json.dumps(data, separators=(",", ":")))
    (HERE / "index.html").write_text(page)
    print(f"index.html: {len(order)} themes, {len(lifted)} lifted, {len(walls)} wallpapers, {len(page)//1024} KB")


if __name__ == "__main__":
    main()
