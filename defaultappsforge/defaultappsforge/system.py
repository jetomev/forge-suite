"""What the computer has and says: the installed apps and what each can open, the standard file
(~/.config/mimeapps.list) read and written without losing anything we don't touch, the system's
answer for a type, and the default terminal (xdg-terminal-exec's list)."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from configparser import ConfigParser
from dataclasses import dataclass, field
from pathlib import Path

HOME = Path.home()
CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config"))
MIMEAPPS = CONFIG_HOME / "mimeapps.list"
TERMINALS = CONFIG_HOME / "xdg-terminals.list"
BACKUPS = CONFIG_HOME / "defaultappsforge/backups"
KEEP_BACKUPS = 20
DEFAULTS = "Default Applications"
ADDED = "Added Associations"


@dataclass
class App:
    id: str                                  # the desktop id, e.g. "google-chrome.desktop"
    name: str
    types: set[str] = field(default_factory=set)
    categories: set[str] = field(default_factory=set)
    hidden: bool = False                     # NoDisplay: a helper (map handlers) — still a valid choice


def application_dirs() -> list[Path]:
    data_home = Path(os.environ.get("XDG_DATA_HOME", HOME / ".local/share"))
    data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":")
    return [data_home / "applications"] + [Path(d) / "applications" for d in data_dirs if d]


def installed(dirs: list[Path] | None = None) -> dict[str, App]:
    """{desktop id: App} — the first folder wins (your own entries over the system's)."""
    found: dict[str, App | None] = {}
    for folder in dirs if dirs is not None else application_dirs():
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*.desktop")):
            did = str(path.relative_to(folder)).replace("/", "-")
            if did in found:
                continue
            parser = ConfigParser(interpolation=None, strict=False)
            parser.optionxform = str
            try:
                parser.read(path, encoding="utf-8")
                e = parser["Desktop Entry"]
            except Exception:
                continue
            found[did] = None
            if e.get("Type") != "Application" or e.get("Hidden") == "true" or not e.get("Exec"):
                continue
            found[did] = App(did, e.get("Name", did), set(e.get("MimeType", "").split(";")) - {""},
                             set(e.get("Categories", "").split(";")) - {""}, e.get("NoDisplay") == "true")
    return {k: v for k, v in found.items() if v}


# ---- the standard file ------------------------------------------------------------------------------

class MimeApps:
    """~/.config/mimeapps.list as lines, so every section and line we don't change stays as it was."""

    def __init__(self, path: Path = MIMEAPPS) -> None:
        self.path = path
        try:
            self.lines = path.read_text().splitlines()
        except FileNotFoundError:
            self.lines = []

    def _section(self, name: str) -> tuple[int, int] | None:
        start = next((i for i, l in enumerate(self.lines) if l.strip() == f"[{name}]"), None)
        if start is None:
            return None
        end = next((i for i in range(start + 1, len(self.lines)) if self.lines[i].strip().startswith("[")),
                   len(self.lines))
        return start, end

    def get(self, section: str) -> dict[str, list[str]]:
        span = self._section(section)
        out: dict[str, list[str]] = {}
        if not span:
            return out
        for l in self.lines[span[0] + 1:span[1]]:
            if "=" in l and not l.lstrip().startswith(("#", ";")):
                k, v = l.split("=", 1)
                out[k.strip()] = [x for x in v.strip().split(";") if x]
        return out

    def set(self, section: str, key: str, apps: list[str] | None) -> None:
        """Set (or, with None / [], remove) one line, in place."""
        span = self._section(section)
        if span is None:
            if not apps:
                return
            if self.lines and self.lines[-1].strip():
                self.lines.append("")
            self.lines += [f"[{section}]"]
            span = (len(self.lines) - 1, len(self.lines))
        for i in range(span[0] + 1, span[1]):
            l = self.lines[i]
            if "=" in l and l.split("=", 1)[0].strip() == key:
                if apps:
                    self.lines[i] = f"{key}={';'.join(apps)};"
                else:
                    del self.lines[i]
                return
        if apps:
            at = span[1]
            while at > span[0] + 1 and not self.lines[at - 1].strip():
                at -= 1
            self.lines.insert(at, f"{key}={';'.join(apps)};")

    def gone(self, apps: dict[str, App]) -> list[tuple[str, str, str]]:
        """(section, type, desktop id) for choices that name an app that isn't installed."""
        out = []
        for section in (DEFAULTS, ADDED):
            for key, ids in self.get(section).items():
                out += [(section, key, d) for d in ids if d not in apps]
        return out

    def tidy(self, apps: dict[str, App]) -> list[str]:
        """Remove the apps that are gone from every line; the names removed."""
        removed = []
        for section in (DEFAULTS, ADDED):
            for key, ids in self.get(section).items():
                keep = [d for d in ids if d in apps]
                if keep != ids:
                    removed += [d for d in ids if d not in apps]
                    self.set(section, key, keep)
        return sorted(set(removed))

    def text(self) -> str:
        return "\n".join(self.lines) + "\n"

    def write(self, backups: Path = BACKUPS) -> Path | None:
        return _write_with_backup(self.path, self.text(), backups, "mimeapps.list")


def _write_with_backup(path: Path, text: str, backups: Path, stem: str) -> Path | None:
    backup = None
    if path.exists():
        backups.mkdir(parents=True, exist_ok=True)
        backup = backups / f"{stem}.{time.strftime('%Y%m%d-%H%M%S')}"
        n = 1
        while backup.exists():
            backup = backups / f"{stem}.{time.strftime('%Y%m%d-%H%M%S')}-{n}"
            n += 1
        shutil.copy2(path, backup)
        for old in sorted(backups.glob(f"{stem}.*"))[:-KEEP_BACKUPS]:
            old.unlink(missing_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text)
    if tmp.read_text() != text:
        tmp.unlink(missing_ok=True)
        raise OSError("the new file did not read back the same; nothing was changed")
    os.replace(tmp, path)
    return backup


# ---- the system's answer, and the terminal ----------------------------------------------------------

def system_default(mime: str) -> str | None:
    """What opens this type now, as the standard lookup answers (xdg-mime), or None."""
    exe = shutil.which("xdg-mime")
    if not exe:
        return None
    try:
        out = subprocess.run([exe, "query", "default", mime], capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out or None


def terminal_now(path: Path = TERMINALS, apps: dict[str, App] | None = None) -> str | None:
    """The chosen terminal (xdg-terminal-exec's list: first line that names an installed one)."""
    try:
        for l in path.read_text().splitlines():
            l = l.strip()
            if l and not l.startswith("#") and (apps is None or l in apps):
                return l
    except FileNotFoundError:
        pass
    return None


def write_terminal(desktop_id: str, path: Path = TERMINALS, backups: Path = BACKUPS) -> Path | None:
    text = ("# Your terminal, first (written by defaultappsForge; read by xdg-terminal-exec).\n"
            f"{desktop_id}\n")
    return _write_with_backup(path, text, backups, "xdg-terminals.list")


def terminal_exec_installed() -> bool:
    return shutil.which("xdg-terminal-exec") is not None
