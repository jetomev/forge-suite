#!/usr/bin/env python3
"""Pictures of every nightForge page at 100 × 30, in memory (live=False: nothing started or saved).
Needs rsvg-convert (librsvg).    python3 scripts/make-screenshots.py [OUT_DIR]   default: docs/images"""
import asyncio
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from nightforge.app import NightForgeApp, ScheduleView  # noqa: E402
from nightforge.settings import Settings  # noqa: E402

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs/images"
OUT.mkdir(parents=True, exist_ok=True)
tmp = Path(tempfile.mkdtemp())


async def shots():
    app = NightForgeApp(Settings(), live=False)
    async with app.run_test(size=(100, 30)) as pilot:
        async def shot(name):
            await pilot.pause(0.6)
            svg = tmp / f"{name}.svg"
            app.save_screenshot(str(svg))
            subprocess.run(["rsvg-convert", "-w", "1200", str(svg), "-o", str(OUT / f"{name}.png")], check=True)
            print("  ", OUT / f"{name}.png")
        await pilot.pause(0.5)
        await shot("night-light")
        await pilot.press("2")
        await shot("schedule")
        app.session.pending.schedule = "fixed"
        app.query_one(ScheduleView).refresh(recompose=True)
        await pilot.pause(0.3)
        app.query_one(ScheduleView).refresh_view()
        app.refresh_state()
        await shot("schedule-fixed")
        await pilot.press("1")
        await pilot.press("p")
        await shot("preview")
        await pilot.press("escape")
        app.session.pending.warmth = 3500
        app.refresh_state()
        await pilot.press("f10")
        await shot("save")

asyncio.run(shots())
