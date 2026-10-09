#!/usr/bin/env python3
"""Pictures of every defaultappsForge page at 100 × 30, in memory on a COPY of this desktop's
mimeapps.list (live=False: nothing is written). Needs rsvg-convert.
    python3 scripts/make-screenshots.py [OUT_DIR]   default: docs/images"""
import asyncio
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from defaultappsforge import system as S  # noqa: E402
from defaultappsforge.app import DefaultAppsForgeApp  # noqa: E402
from defaultappsforge.model import Session  # noqa: E402

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs/images"
OUT.mkdir(parents=True, exist_ok=True)
tmp = Path(tempfile.mkdtemp())
copy = tmp / "mimeapps.list"
if S.MIMEAPPS.exists():
    shutil.copy(S.MIMEAPPS, copy)


async def shots():
    se = Session(mimeapps=S.MimeApps(copy), pools_path=tmp / "settings.toml", terminals=tmp / "terms.list")
    app = DefaultAppsForgeApp(se, live=False)
    async with app.run_test(size=(100, 30)) as pilot:
        async def shot(name):
            await pilot.pause(0.7)
            svg = tmp / f"{name}.svg"
            app.save_screenshot(str(svg))
            subprocess.run(["rsvg-convert", "-w", "1200", str(svg), "-o", str(OUT / f"{name}.png")], check=True)
            print("  ", OUT / f"{name}.png")
        await pilot.pause(0.6)
        await shot("default-apps")
        await pilot.press("2")
        await pilot.pause(0.6)
        app.query_one("#da-c-calendar").collapsed = False
        await pilot.pause(0.3)
        app.query_one("#da-pool").set_tick(".ics", True)
        await shot("file-types")
        se.choose("pdf", "masterpdfeditor4.desktop")
        app.refresh_state()
        await pilot.press("f10")
        await shot("save")

asyncio.run(shots())
shutil.rmtree(tmp, ignore_errors=True)
