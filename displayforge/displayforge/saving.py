"""displayForge · saving the screens to a file Sway reads at every login, with a backup first."""

from __future__ import annotations

import os
import time
from pathlib import Path

from . import screens as S

HOME = Path.home()
OUTPUTS = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config")) / "sway/outputs"
SWAY_CONFIG = HOME / ".config/sway/config"   # where the include line has to be
BACKUPS = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config")) / "displayforge/backups"
KEEP = 20

HEADER = """# Written by displayForge — your screens: resolution, refresh rate, position, size, rotation.
# Sway reads this at every login (hypeForge's sway/config includes it). Change it with
# displayForge; edits by hand are kept until the next save there. Saved {when}.
"""


def save(screens: list[S.Screen], path: Path | None = None, backups: Path | None = None,
         now: float | None = None) -> tuple[Path, Path | None]:
    """Write the file safely: back up the old one, write a temporary file, then swap it in.
    Returns (the file, the backup or None if there was nothing to back up).

    The paths are looked up when called, not when Python reads this file: a default fixed at
    import time once sent an in-memory test's save to the real ~/.config/sway/outputs."""
    path = path or OUTPUTS
    backups = backups or BACKUPS
    stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(now))
    backup = None
    if path.exists():
        backups.mkdir(parents=True, exist_ok=True)
        backup = backups / f"outputs-{stamp}"
        n = 1
        while backup.exists():           # two saves in one second keep both
            n += 1
            backup = backups / f"outputs-{stamp}-{n}"
        backup.write_bytes(path.read_bytes())
        prune(backups)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = HEADER.format(when=time.strftime("%Y-%m-%d %H:%M", time.localtime(now))) + \
        "\n".join(S.config_lines(screens)) + "\n"
    tmp = path.with_name(path.name + ".displayforge-tmp")
    tmp.write_text(text)
    os.replace(tmp, path)                # all or nothing: never a half-written file
    return path, backup


def prune(backups: Path, keep: int = KEEP) -> None:
    files = sorted(backups.glob("outputs-*"), key=lambda p: p.stat().st_mtime)
    for old in files[:-keep]:
        old.unlink()


def included(sway_config: Path, outputs: Path | None = None) -> bool:
    """Does Sway's own config read the outputs file?"""
    outputs = outputs or OUTPUTS
    if not sway_config.exists():
        return False
    targets = {str(outputs), str(outputs).replace(str(HOME), "~"), "~/.config/sway/outputs",
               "$HOME/.config/sway/outputs"}
    for line in sway_config.read_text().splitlines():
        words = line.split()
        if len(words) >= 2 and words[0] == "include" and words[1] in targets:
            return True
    return False
