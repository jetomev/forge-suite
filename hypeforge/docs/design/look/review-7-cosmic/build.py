#!/usr/bin/env python3
"""Build Review 7 of the look program: the COSMIC style proposal, a live mock-up of a
hypeForge screen that any of the 23 themes can dress, with the plain-Sway and SwayFX versions
side by side. Writes index.html next to this file.

    python3 docs/design/look/review-7-cosmic/build.py
"""
from __future__ import annotations

import base64
import importlib.util
import json
import pathlib
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
LOOK = HERE.parent
ROOT = HERE.parents[3]                                     # hypeforge/

spec = importlib.util.spec_from_file_location("review1", LOOK / "review-1/build.py")
review1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review1)

ICONS = "/usr/share/icons/candy-icons/apps/scalable"       # candy-icons (GPL-3), the desktop's icons
APPS = [  # id, name, icon file — Javier's favourites (sections.toml) in his order
    ("alacritty", "Alacritty", f"{ICONS}/Alacritty.svg"),
    ("thunar", "Thunar", f"{ICONS}/system-file-manager.svg"),
    ("chrome", "Chrome", f"{ICONS}/google-chrome.svg"),
    ("claude", "Claude", "/usr/share/icons/hicolor/128x128/apps/claude-desktop.png"),
    ("onlyoffice", "ONLYOFFICE", f"{ICONS}/onlyoffice.svg"),
    ("obsidian", "Obsidian", f"{ICONS}/obsidian.svg"),
    ("whatsapp", "WhatsApp", f"{ICONS}/whatsapp.svg"),
    ("discord", "Discord", f"{ICONS}/discord.svg"),
    ("spotify", "Spotify", f"{ICONS}/spotify-client.svg"),
    ("steam", "Steam", f"{ICONS}/steam.svg"),
    ("keepassxc", "KeePassXC", f"{ICONS}/keepassxc.svg"),
    ("btop", "btop", f"{ICONS}/btop.svg"),
    ("calc", "Calculator", f"{ICONS}/accessories-calculator.svg"),
    ("settings", "hypeForge Settings", f"{ICONS}/preferences-system.svg"),
    ("downloads", "Downloads", "/usr/share/icons/candy-icons/places/48/folder-download.svg"),
    ("trash", "Trash", "/usr/share/icons/candy-icons/places/48/user-trash.svg"),
]


def data_uri(path: str) -> str:
    p = pathlib.Path(path).resolve()
    kind = "image/svg+xml" if p.suffix == ".svg" else "image/png"
    return f"data:{kind};base64," + base64.b64encode(p.read_bytes()).decode()


def main():
    order, now = review1.themes(ROOT / "docs/research/look-2026-10/palette/palettes.toml")
    lifted = {}   # Q-4 answered (D-70): middle to darker — the lighter option B is retired
    style = tomllib.loads((LOOK / "styles/cosmic/style.toml").read_text())
    data = {
        "order": order, "now": now, "lifted": lifted, "emblem": review1.emblem(),
        "apps": [{"id": i, "name": n, "icon": data_uri(f)} for i, n, f in APPS],
        "workspaces": ["Daily", "Work", "Entertainment", "Gaming", "Monitoring", "Settings"],
        "style": style,
        # one wallpaper per theme, made by our generator in the theme's colours (D-69)
        "walls": {s: f"wallpapers/{s}.jpg" for s in order if (HERE.parent / "review-5-rice/wallpapers" / f"{s}.jpg").exists()},
    }
    page = (HERE / "template.html").read_text()
    page = page.replace("/*DATA*/null", json.dumps(data, separators=(",", ":")))
    page = page.replace("<!--STYLE-->", (LOOK / "styles/cosmic/style.toml").read_text()
                        .replace("&", "&amp;").replace("<", "&lt;"))
    (HERE / "index.html").write_text(page)
    print(f"index.html: {len(order)} themes, {len(APPS)} apps, {len(page)//1024} KB")


if __name__ == "__main__":
    main()
