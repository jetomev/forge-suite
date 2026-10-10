"""hypeForge applets · finding an app's icon file (for the bar parts that draw icons, look step 3).

Python standard library only. An app names its icon ("google-chrome", or a full path); this finds
the file in the icon theme first (candy-icons, the desktop's), then the fallbacks every system
has (hicolor, pixmaps). Scalable pictures win; among sized ones, the largest.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

THEMES = ("candy-icons", "Papirus-Dark", "Papirus", "hicolor", "Adwaita")
EXTS = (".svg", ".png")


def icon_dirs():
    home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    dirs = [home / "icons", Path.home() / ".icons"]
    for d in os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":"):
        if d:
            dirs.append(Path(d) / "icons")
    return dirs


def _rank(path: Path) -> int:
    """Bigger is better: scalable first, then the largest size, apps/ before other kinds."""
    s = str(path)
    if "scalable" in s:
        score = 10000
    else:
        m = re.search(r"/(\d+)x\d+", s)
        score = int(m.group(1)) if m else 1
    return score + (5 if "/apps/" in s else 0)


class Icons:
    """Looks a name up only where an icon theme says its pictures are (its index.theme lists
    the folders), so nothing is read ahead: a few hundred quick checks per name at most."""

    def __init__(self, themes=THEMES, dirs=None):
        self.roots: list[tuple[Path, list[str]]] = []
        for theme in themes:
            for base in (dirs or icon_dirs()):
                root = base / theme
                index = root / "index.theme"
                if not index.is_file():
                    continue
                folders = []
                for line in index.read_text(errors="replace").splitlines():
                    if line.startswith(("Directories=", "ScaledDirectories=")):
                        folders += [f for f in line.split("=", 1)[1].split(",") if f]
                self.roots.append((root, list(dict.fromkeys(folders))))
        self.pixmaps = Path("/usr/share/pixmaps")
        self.cache: dict[str, str | None] = {}

    def find(self, name: str) -> str | None:
        """The best file for an icon name, or None."""
        if not name:
            return None
        if name.startswith("/"):
            return name if os.path.isfile(name) else None
        if name in self.cache:
            return self.cache[name]
        found = None
        for root, folders in self.roots:
            hits = [root / f / f"{name}{ext}" for f in folders for ext in EXTS]
            hits = [h for h in hits if h.is_file()]
            if hits:
                found = str(max(hits, key=_rank))
                break
        if not found:
            found = next((str(self.pixmaps / f"{name}{e}") for e in EXTS if (self.pixmaps / f"{name}{e}").is_file()), None)
        self.cache[name] = found
        return found


def safe(app_id: str) -> str:
    """An app id as a CSS class name: lower case, anything else a dash."""
    return re.sub(r"[^a-z0-9]+", "-", app_id.lower()).strip("-") or "app"


def icon_rules(entries: dict, icons: "Icons") -> list[str]:
    """A stylesheet rule per installed app, `.app-<id> { background-image: … }`, so a bar module
    can show any app's icon by its class without the bar reloading; `.noicon` for the rest."""
    css = [".app { background-repeat: no-repeat; background-position: center; background-size: 24px 24px; }"]
    for app_id, app in sorted(entries.items()):
        path = icons.find(app["icon"])
        if path:
            css.append(f'.app-{safe(app_id)} {{ background-image: url("file://{path}"); }}')
    fallback = icons.find("application-x-executable")
    if fallback:  # a window of no installed app (GTK's CSS has no attribute selectors: a class)
        css.append(f'.app.noicon {{ background-image: url("file://{fallback}"); }}')
    return css
