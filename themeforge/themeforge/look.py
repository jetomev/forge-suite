"""What themeForge works on: hypeForge's styles and colour themes, the look in use, and the switch.

Read only from hypeForge's own files (D-59: apps read each other's files, never each other's
code): the styles (`styles/<slug>/style.toml`), the 25 colour themes
(`themes/colours/palettes.toml`) and what is applied now (`~/.config/hypeforge/theme/state.toml`).
The switch (Javier, 2026-10-11: "have already a config file for theme, and with the config file
themeForge call to change it"): themeForge writes the picks into THE LOOK FILE,
`~/.config/hypeforge/look.toml` (the theme, its colours, each element), then runs hypeForge's own
`hypeforge-theme look`, which applies that file: every look file written, a backup kept, the bar
restarted whole when its layout changes. `undo` goes back one apply the same way. Every run is
written to themeForge's log (~/.local/state/themeforge/themeforge.log).
"""

from __future__ import annotations

import datetime as dt
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
ELEMENTS = ["bar", "launcher", "workspaces", "taskbar", "datetime", "tray", "status_icons", "popups",
            "dock", "windows", "icons", "fonts"]
LOG = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "themeforge/themeforge.log"
# the wallpaper (Javier, 2026-10-11: themeForge's Wallpaper page): where it comes from and how it lies
WALL_FOLDER = "~/Pictures/Wallpapers"
# Fit Style, in simple names (Javier, D-8: "simple names, nothing confusing"); the keys are Sway's own
FITS = {"fill": "Fill the Screen", "fit": "Whole Picture", "stretch": "Stretched", "center": "Real Size", "tile": "Repeated"}
FIT_ABOUT = {"fill": "Covers the whole screen; the edges of the picture are cropped. The usual choice.",
             "fit": "All of the picture shows, with the theme's colour around it.",
             "stretch": "The whole picture, pulled to the screen's shape.",
             "center": "The picture at its real size, in the middle of the screen.",
             "tile": "The picture repeated across the screen."}
PICTURE_TYPES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}     # what Sway's wallpaper program reads
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
    elements: dict = field(default_factory=dict)      # its version of each piece, in plain words


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

    def __init__(self, home: Path | None = None, config: Path | None = None, run=subprocess.run,
                 log: Path | None = None):
        self.home = home if home is not None else hypeforge_home()
        self.config = config or Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        self.run = run
        self.log = log or LOG

    @property
    def look_file(self) -> Path:
        return self.config / "hypeforge/look.toml"

    def picks(self) -> dict:
        """The look file: {"theme", "colors", "elements", "wallpaper"}; empty when there is none yet."""
        try:
            d = tomllib.loads(self.look_file.read_text())
        except (OSError, tomllib.TOMLDecodeError):
            return {}
        el = d.get("elements", {})
        wp = d.get("wallpaper", {})
        return {"theme": d.get("theme"), "colors": d.get("colors"),
                "elements": {k: str(el.get(k, "theme")) for k in ELEMENTS},
                "wallpaper": {"picture": wp.get("picture"), "fit": wp.get("fit"),
                              "folder": str(wp.get("folder", WALL_FOLDER))}}

    def write_picks(self, theme: str, colors: str, wallpaper: dict | None = None) -> None:
        """The look file with the new theme and colours (and wallpaper, when given); the rest is kept."""
        el = self.picks().get("elements", {})
        now = self.wallpaper_now()
        wp = {"picture": now[0], "fit": now[1], "folder": self.picks().get("wallpaper", {}).get("folder", WALL_FOLDER)}
        wp.update({k: v for k, v in (wallpaper or {}).items() if v is not None})
        q = lambda v: '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'
        body = ("# hypeForge's look: what themeForge picked. themeForge writes it and runs `hypeforge-theme look`;\n"
                "# every apply writes it too, so it always says what is on screen.\n"
                "# theme = a style (styles/<slug>/style.toml) · colors = a colour theme (themes/colours/palettes.toml)\n"
                f"theme = {q(theme)}\ncolors = {q(colors)}\n\n"
                "# Each element of the look: \"theme\" = the theme's own (its style.toml [elements] says what that is).\n"
                "# Picking one element from another theme comes with themeForge's next pages.\n"
                "[elements]\n" + "".join(f"{k} = {q(el.get(k, 'theme'))}\n" for k in ELEMENTS) +
                "\n# The wallpaper, the same on every screen: picture = \"theme\" (the theme's own), \"kognogos:tier-aware\"\n"
                "# or \"kognogos:arch-distro\" (KognogOS, in the theme's colours), \"solid\" (the theme's colour), or a\n"
                "# file; fit = fill · fit · stretch · center · tile; folder = where your pictures are.\n"
                "[wallpaper]\n" + "".join(f"{k} = {q(wp[k])}\n" for k in ("picture", "fit", "folder")))
        self.look_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.look_file.with_name("look.toml.tftmp")
        tmp.write_text(body)
        tmp.replace(self.look_file)

    def _log(self, what: str, ok: bool, out: str) -> None:
        try:
            self.log.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log, "a") as f:
                f.write(f"\n== {dt.datetime.now():%Y-%m-%d %H:%M:%S} · {what} · {'OK' if ok else 'NOT DONE'}\n{out.strip()}\n")
        except OSError:
            pass

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
            d = tomllib.loads(f.read_text())
            found[meta["slug"]] = Style(meta["slug"], meta.get("name", meta["slug"]), meta.get("summary", ""),
                                        dict(d.get("elements", {})))
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

    # ---- the wallpaper ----

    def wallpaper_now(self) -> tuple[str, str]:
        """(choice, fit) on screen now, from hypeforge-theme's own memory."""
        try:
            st = tomllib.loads((self.config / "hypeforge/theme/state.toml").read_text())
        except (OSError, tomllib.TOMLDecodeError):
            return "theme", "fill"
        return str(st.get("wallpaper", "theme")), str(st.get("fit", "fill"))

    def folder(self) -> Path:
        return Path(self.picks().get("wallpaper", {}).get("folder", WALL_FOLDER)).expanduser()

    @staticmethod
    def pictures(folder: Path) -> list[Path]:
        """The pictures in a folder (not its sub-folders), by name."""
        try:
            return sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in PICTURE_TYPES),
                          key=lambda p: p.name.lower())
        except OSError:
            return []

    def kognogos_designs(self) -> list[tuple[str, str]]:
        """[(slug, name)] of the KognogOS backgrounds hypeForge can draw in any colours."""
        out = []
        for f in sorted((self.home or Path("/nonexistent")).glob("assets/wallpaper/kognogos-*.json")):
            slug = f.stem.removeprefix("kognogos-")
            out.append((slug, " ".join(w.capitalize() for w in slug.split("-"))))
        order = {"tier-aware": 0}
        return sorted(out, key=lambda d: (order.get(d[0], 1), d[1]))

    def topic(self, style: str) -> str:
        """The style's own wallpaper, in plain words (its style.toml [wallpaper] about)."""
        try:
            d = tomllib.loads(((self.home or Path("/nonexistent")) / f"styles/{style}/style.toml").read_text())
        except (OSError, tomllib.TOMLDecodeError):
            return ""
        return str(d.get("wallpaper", {}).get("about", ""))

    def drawn_topics(self, but: str | None) -> list[tuple[str, str]]:
        """[(topic, words)] the drawn wallpapers of every style but ``but`` (its own is "the theme's own"),
        KognogOS left out (its own choices). Javier, 2026-10-17: the Rice lists them before the solid colour."""
        seen: dict[str, str] = {}
        for f in sorted((self.home or Path("/nonexistent")).glob("styles/*/style.toml")):
            if f.parent.name == but:
                continue
            try:
                w = tomllib.loads(f.read_text()).get("wallpaper", {})
            except (OSError, tomllib.TOMLDecodeError):
                continue
            if w.get("topic") and w["topic"] != "kognogos":
                seen.setdefault(str(w["topic"]), str(w.get("about") or w["topic"]).capitalize())
        return sorted(seen.items(), key=lambda kv: kv[1])

    def picture_path(self, style: str, theme: str, choice: str) -> Path | None:
        """The picture a choice gives in a look (hypeForge makes it if needed; a few seconds the first time)."""
        try:
            r = self.run([str(self.tool), "picture", style, theme, choice], capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.SubprocessError):
            return None
        out = r.stdout.strip().splitlines()
        return Path(out[-1]) if not r.returncode and out else None

    def apply_wallpaper(self, picture: str, fit: str, folder: str | None = None) -> tuple[bool, str]:
        """The wallpaper into the look file (the theme and colours in use kept), then hypeForge applies it."""
        style, theme = self.current()
        if not (style and theme):
            return False, "apply a theme first"
        try:
            self.write_picks(style, theme, {"picture": picture, "fit": fit, "folder": folder})
        except OSError as e:
            return False, f"the look file could not be written ({e})"
        return self._do("look")

    def _do(self, *args: str) -> tuple[bool, str]:
        try:
            r = self.run([str(self.tool), *args], capture_output=True, text=True, timeout=180)
        except (OSError, subprocess.SubprocessError) as e:
            return False, str(e)
        words = [l.strip() for l in (r.stdout + "\n" + r.stderr).splitlines() if l.strip()]
        self._log(" ".join(args), not r.returncode, r.stdout + "\n" + r.stderr)
        if r.returncode:
            reason = next((l.removeprefix("Not done:").strip() for l in words if l.startswith("Not done")), "")
            return False, reason or (words[-1] if words else f"it stopped (code {r.returncode})")
        return True, "; ".join(words[-3:]) if words else "done"

    def apply(self, style: str, theme: str, wallpaper: dict | None = None) -> tuple[bool, str]:
        """Write the picks into the look file, then hypeForge applies the file."""
        try:
            self.write_picks(style, theme, wallpaper)
        except OSError as e:
            return False, f"the look file could not be written ({e})"
        return self._do("look")

    def undo(self) -> tuple[bool, str]:
        return self._do("undo")
