#!/usr/bin/env python3
"""Regenerates docs/images/*.png for the README: displayForge driven in memory on Javier's three
Sceptres (tests/data, serial blanked), with a fake swaymsg and ddcutil — nothing touches a real
screen or file. Needs rsvg-convert (librsvg). Run from anywhere:
    PYTHONPATH=<forgekit> python3 scripts/make-screenshots.py
"""
import asyncio, json, stat, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from displayforge import brightness as B, saving as V, screens as S  # noqa: E402
from displayforge.app import DisplayForgeApp, SettingsView  # noqa: E402
from displayforge.session import Session  # noqa: E402

tmp = Path(tempfile.mkdtemp())
V.OUTPUTS, V.BACKUPS, B.CONFIG = tmp / "outputs", tmp / "backups", tmp / "screens.toml"
fake = tmp / "fake"
fake.write_text('#!/bin/sh\ncase "$*" in *getvcp*) echo "VCP 10 C 70 100";; esac\n')
fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
OUT = ROOT / "docs/images"


async def shots():
    data = json.loads((ROOT / "tests/data/three-sceptre-y27.json").read_text())
    se = Session(S.parse(data), {"names": {"DP-3": "Main"}, "bus": {"DP-2": 3, "DP-3": 4, "DP-1": 5}}, main="DP-3")
    app = DisplayForgeApp(se, swaymsg=str(fake), ddcutil=str(fake))
    async with app.run_test(size=(110, 34)) as pilot:
        async def shot(name):
            await pilot.pause(0.6)
            svg = tmp / f"{name}.svg"
            app.save_screenshot(str(svg))
            subprocess.run(["rsvg-convert", "-w", "1200", str(svg), "-o", str(OUT / f"{name}.png")], check=True)
            print("  ", name)
        await pilot.pause(0.5)
        await shot("screens")
        await pilot.press("2")
        hz120 = [m for m in se.screen("DP-3").rates(2560, 1440) if m.hz == 120][0]
        se.change("DP-3", mode=hz120)
        app.query_one(SettingsView)._changed()
        await shot("settings")
        await pilot.press("f9")
        await shot("keep-or-go-back")
        await pilot.press("escape")
        await pilot.press("3")
        await shot("arrange")
        await pilot.press("4")
        await shot("brightness")

asyncio.run(shots())
