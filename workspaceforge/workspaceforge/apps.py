"""The apps on this computer, as the launcher lists them, each with its category.

Read from the desktop entries (the standard files every app installs), the same way hypeForge's
launcher reads them; named by their launcher names (the file name without ".desktop").
"""

from __future__ import annotations

import os
from configparser import ConfigParser
from pathlib import Path

DESKTOP_NAMES = {"sway", "wlroots"}

# The standard kinds of app, in the launcher's order of priority (hypeForge D-64): an app that is
# both a setting and a system tool is a setting; a game that also says Network is a game.
CATEGORIES = [
    ("Settings", {"Settings"}), ("Games", {"Game"}), ("Multimedia", {"AudioVideo", "Audio", "Video"}),
    ("Graphics", {"Graphics"}), ("Office", {"Office"}), ("Development", {"Development"}),
    ("Education", {"Education"}), ("Science", {"Science"}), ("Internet", {"Network"}),
    ("System", {"System"}), ("Utilities", {"Utility"}),
]


def application_dirs() -> list[Path]:
    home = Path.home()
    data_home = Path(os.environ.get("XDG_DATA_HOME", home / ".local/share"))
    data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":")
    return [data_home / "applications"] + [Path(d) / "applications" for d in data_dirs if d]


def category(cats: set[str]) -> str:
    return next((name for name, these in CATEGORIES if cats & these), "Other")


def installed(dirs: list[Path] | None = None) -> dict[str, dict]:
    """{launcher name: {"name", "category"}} for every app a start menu would show."""
    found: dict[str, dict | None] = {}
    for folder in dirs if dirs is not None else application_dirs():
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*.desktop")):
            app_id = str(path.relative_to(folder))[:-len(".desktop")].replace("/", "-")
            if app_id in found:
                continue
            parser = ConfigParser(interpolation=None, strict=False)
            parser.optionxform = str
            try:
                parser.read(path, encoding="utf-8")
                entry = parser["Desktop Entry"]
            except Exception:
                continue
            found[app_id] = None  # seen: a hidden copy still hides the system one
            only = set(entry.get("OnlyShowIn", "").lower().split(";")) - {""}
            never = set(entry.get("NotShowIn", "").lower().split(";")) - {""}
            if (entry.get("Type") != "Application" or entry.get("NoDisplay") == "true"
                    or entry.get("Hidden") == "true" or not entry.get("Exec")
                    or (only and not only & DESKTOP_NAMES) or never & DESKTOP_NAMES):
                continue
            cats = set(entry.get("Categories", "").split(";")) - {""}
            found[app_id] = {"name": entry.get("Name", app_id), "category": category(cats)}
    return {k: v for k, v in found.items() if v}
