#!/usr/bin/env python3
"""Pictures of every workspaceForge page, at 100 × 30, the size the design was drawn at.

Driven in memory on a COPY of this desktop's workspaces file and its real installed apps, with no
desktop behind it (nothing is moved, written or reloaded for real). Needs rsvg-convert (librsvg).

    python3 scripts/make-screenshots.py [OUT_DIR]      default: docs/images
"""
import asyncio
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from workspaceforge import model as M  # noqa: E402
from workspaceforge.app import WorkspaceForgeApp, WorkspacesView  # noqa: E402
from workspaceforge.live import NoDesktop  # noqa: E402

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs/images"
OUT.mkdir(parents=True, exist_ok=True)
tmp = Path(tempfile.mkdtemp())
copy = tmp / "workspaces.toml"
shutil.copy(M.CONFIG if M.CONFIG.exists() else ROOT / "../hypeforge/applets/workspaces/workspaces.toml", copy)
M.BACKUPS = tmp / "backups"


async def shots():
    live = NoDesktop()
    live.open = {"2:Work": ["Alacritty", "obsidian", "ONLYOFFICE"]}
    app = WorkspaceForgeApp(M.Session.load(copy), live=live)
    se = app.session

    def uid(name):
        return next(w.uid for w in se.pending.workspaces if w.name == name)

    async with app.run_test(size=(100, 30)) as pilot:
        async def shot(name):
            await pilot.pause(0.6)
            svg = tmp / f"{name}.svg"
            app.save_screenshot(str(svg))
            subprocess.run(["rsvg-convert", "-w", "1200", str(svg), "-o", str(OUT / f"{name}.png")], check=True)
            print("  ", OUT / f"{name}.png")

        ws = app.query_one(WorkspacesView)
        await pilot.pause(0.5)
        ws.picked = uid("Gaming")
        ws.refresh_view()
        await shot("workspaces")
        await pilot.press("n")
        await pilot.press(*"Studio")
        await shot("new")
        await pilot.press("escape")
        ws.picked = uid("Entertainment")
        ws.refresh_view()
        await pilot.press("e")
        app.query_one("#ws-name").value = "Media"
        await pilot.press("enter")
        await shot("edit")
        ws.picked = uid("Work")
        ws.refresh_view()
        await pilot.press("d")
        await shot("delete")
        await pilot.press("escape")
        se.discard()
        ws.renamed = None
        app.refresh_state()
        await pilot.press("2")
        await pilot.pause(0.5)
        app.query_one("#pool-cat").value = "Utilities"
        await pilot.pause(0.3)
        app.query_one(f"#col-{uid('Gaming')}").collapsed = False
        await pilot.pause(0.3)
        pool = app.query_one("#wf-pool")
        pool.set_tick("winetricks", True)
        await shot("apps")
        app.session.assign(["winetricks"], uid("Gaming"))
        app.refresh_state()
        await pilot.press("f10")
        await shot("save")

asyncio.run(shots())
shutil.rmtree(tmp, ignore_errors=True)
