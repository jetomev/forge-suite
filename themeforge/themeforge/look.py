"""What themeForge works on: hypeForge's styles and colour themes, the look in use, and the switch.

Read only from hypeForge's own files (D-59: apps read each other's files, never each other's
code): the styles (`styles/<slug>/style.toml`), the 25 colour themes
(`themes/colours/palettes.toml`) and what is applied now (`~/.config/hypeforge/theme/state.toml`).
The switch itself is hypeForge's own command, `hypeforge-theme apply <style> <theme>` (and `undo`):
it writes every look file, keeps a backup, and reloads what is running.
"""

from __future__ import annotations

import os
import subprocess
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# Where hypeForge lives: the test desktop's Forge Suite folder now, a package's folder later.
HYPEFORGE_PLACES = [Path.home() / "Programs/forge-suite/hypeforge", Path("/usr/share/hypeforge")]
# The order Javier sees: the KognogOS default first, then the build order of the look program (D-78)
STYLE_ORDER = ["rice", "windows-11", "mac-os-9", "kde", "cosmic", "macos", "classic"]
# A swatch strip: the theme's 60-30-10 at a glance (D-70) — neutrals, its colour, its pop, its text
SWATCH = ["surface.sunken", "surface.base", "surface.raised", "band.base", "band.strong", "pop.base", "text.primary"]


def hypeforge_home(places=None) -> Path | None:
    env = os.environ.get("THEMEFORGE_HYPEFORGE")
    for p in ([Path(env)] if env else []) + list(places or HYPEFORGE_PLACES):
        if (p / "applets/theme/hypeforge-theme").is_file():
            return p
    return None


@dataclass
class Style:
    slug: str
    name: str
    summary: str = ""


@dataclass
class Colours:
    slug: str
    name: str
    polarity: str = "dark"
    family: str = ""
    swatch: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        return f"{self.name}  ·  {self.polarity}"


def _colour(theme: dict, path: str) -> str:
    group, _, key = path.partition(".")
    return theme.get(group, {}).get(key, "#000000")


class Look:
    """hypeForge's look, as themeForge sees it. `run` is swapped out in the tests."""

    def __init__(self, home: Path | None = None, config: Path | None = None, run=subprocess.run):
        self.home = home if home is not None else hypeforge_home()
        self.config = config or Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        self.run = run

    @property
    def ok(self) -> bool:
        return self.home is not None and self.tool.is_file()

    @property
    def tool(self) -> Path:
        return (self.home or Path("/nonexistent")) / "applets/theme/hypeforge-theme"

    def styles(self) -> list[Style]:
        found = {}
        for f in sorted((self.home or Path("/nonexistent")).glob("styles/*/style.toml")):
            try:
                meta = tomllib.loads(f.read_text())["meta"]
            except (OSError, tomllib.TOMLDecodeError, KeyError):
                continue
            found[meta["slug"]] = Style(meta["slug"], meta.get("name", meta["slug"]), meta.get("summary", ""))
        rank = {s: i for i, s in enumerate(STYLE_ORDER)}
        return sorted(found.values(), key=lambda s: (rank.get(s.slug, len(rank)), s.name.lower()))

    def colours(self) -> list[Colours]:
        try:
            data = tomllib.loads(((self.home or Path("/nonexistent")) / "themes/colours/palettes.toml").read_text())
        except (OSError, tomllib.TOMLDecodeError):
            return []
        out = []
        for slug in data.get("meta", {}).get("order", []):
            t = data.get("themes", {}).get(slug)
            if not t:
                continue
            m = t.get("meta", {})
            out.append(Colours(slug, m.get("name", slug), m.get("polarity", "dark"), m.get("family", ""),
                               [_colour(t, p) for p in SWATCH]))
        return out

    def current(self) -> tuple[str | None, str | None]:
        """(style, theme) applied now, from hypeforge-theme's own memory; (None, None) if none."""
        try:
            st = tomllib.loads((self.config / "hypeforge/theme/state.toml").read_text())
        except (OSError, tomllib.TOMLDecodeError):
            return None, None
        return st.get("style"), st.get("theme")

    def _do(self, *args: str) -> tuple[bool, str]:
        try:
            r = self.run([str(self.tool), *args], capture_output=True, text=True, timeout=180)
        except (OSError, subprocess.SubprocessError) as e:
            return False, str(e)
        words = [l.strip() for l in (r.stdout + "\n" + r.stderr).splitlines() if l.strip()]
        if r.returncode:
            reason = next((l.removeprefix("Not done:").strip() for l in words if l.startswith("Not done")), "")
            return False, reason or (words[-1] if words else f"it stopped (code {r.returncode})")
        return True, "; ".join(words[-3:]) if words else "done"

    def apply(self, style: str, theme: str) -> tuple[bool, str]:
        return self._do("apply", style, theme)

    def undo(self) -> tuple[bool, str]:
        return self._do("undo")
