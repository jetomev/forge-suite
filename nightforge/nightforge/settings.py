"""nightForge's settings: what you chose, read and written with a backup, and turned into wlsunset's
options (wlsunset has no settings file of its own: everything is passed when it starts)."""

from __future__ import annotations

import os
import shutil
import time
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "nightforge"
CONFIG = CONFIG_DIR / "settings.toml"
BACKUPS = CONFIG_DIR / "backups"
KEEP_BACKUPS = 20
STEPS = [3000, 3500, 4000, 4500, 5000]          # the evening warmth's five steps (K)
WORDS = {3000: "very warm", 3500: "warm", 4000: "gentle", 4500: "light", 5000: "just a touch"}
DAY = 6500                                      # the screens' own white (D-3: no setting)
LOWEST, HIGHEST = 1000, 6400                    # a typed warmth; wlsunset needs night < day


@dataclass
class Settings:
    enabled: bool = True
    warmth: int = 4000              # K in the evening
    schedule: str = "sun"           # "sun" (by the sun at the place) or "fixed"
    latitude: float = 25.77         # Miami: where hypeForge's night light started (2026-10-07)
    longitude: float = -80.19
    warm_from: str = "21:00"        # fixed times
    day_from: str = "07:00"
    fade_minutes: int = 30

    # -- reading and writing ---------------------------------------------------------------------
    @classmethod
    def load(cls, path: Path = CONFIG) -> "Settings":
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except FileNotFoundError:
            return cls()
        except tomllib.TOMLDecodeError:
            return cls()                         # a broken file: the defaults, and saving fixes it
        s = cls()
        for k, v in data.items():
            if hasattr(s, k):
                setattr(s, k, type(getattr(s, k))(v))
        return s.checked()

    def checked(self) -> "Settings":
        """Values wlsunset will accept, whatever the file said."""
        self.warmth = max(LOWEST, min(HIGHEST, int(self.warmth)))
        self.schedule = self.schedule if self.schedule in ("sun", "fixed") else "sun"
        self.latitude = max(-90.0, min(90.0, float(self.latitude)))
        self.longitude = max(-180.0, min(180.0, float(self.longitude)))
        self.warm_from = clock(self.warm_from, "21:00")
        self.day_from = clock(self.day_from, "07:00")
        self.fade_minutes = max(1, min(240, int(self.fade_minutes)))
        return self

    def to_toml(self) -> str:
        def v(x):
            return ("true" if x else "false") if isinstance(x, bool) else (f'"{x}"' if isinstance(x, str) else str(x))
        d = asdict(self)
        return "\n".join([
            "# nightForge — the night light's settings. Change them in nightForge (or here, then",
            "# `nightforge start` applies them).",
            "",
            "# false = no warm colours, now and at every login.",
            f"enabled = {v(d['enabled'])}",
            "# How warm the evening gets, in kelvin (lower = warmer). Daytime stays 6500, the screens' own white.",
            f"warmth = {v(d['warmth'])}",
            '# "sun": by the sun at your place; "fixed": the same times every day.',
            f"schedule = {v(d['schedule'])}",
            f"latitude = {d['latitude']}",
            f"longitude = {d['longitude']}",
            f"warm_from = {v(d['warm_from'])}",
            f"day_from = {v(d['day_from'])}",
            f"fade_minutes = {d['fade_minutes']}",
        ]) + "\n"

    def save(self, path: Path = CONFIG, backups: Path = BACKUPS) -> Path | None:
        """Write, a backup of the old file first (the last 20 kept); it must read back the same."""
        backup = None
        if path.exists():
            backups.mkdir(parents=True, exist_ok=True)
            backup = backups / f"settings.toml.{time.strftime('%Y%m%d-%H%M%S')}"
            n = 1
            while backup.exists():
                backup = backups / f"settings.toml.{time.strftime('%Y%m%d-%H%M%S')}-{n}"
                n += 1
            shutil.copy2(path, backup)
            for old in sorted(backups.glob("settings.toml.*"))[:-KEEP_BACKUPS]:
                old.unlink(missing_ok=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(self.to_toml())
        if Settings.load(tmp) != self:
            tmp.unlink(missing_ok=True)
            raise OSError("the new file did not read back the same; nothing was changed")
        os.replace(tmp, path)
        return backup

    # -- for wlsunset ------------------------------------------------------------------------------
    def wlsunset_args(self, warmth: int | None = None) -> list[str]:
        w = max(LOWEST, min(HIGHEST, int(warmth or self.warmth)))
        args = ["-t", str(w), "-T", str(DAY)]
        if self.schedule == "fixed":
            args += ["-s", self.warm_from, "-S", self.day_from, "-d", str(self.fade_minutes * 60)]
        else:
            args += ["-l", f"{self.latitude:.2f}", "-L", f"{self.longitude:.2f}"]
        return args

    def place_words(self) -> str:
        ns = "N" if self.latitude >= 0 else "S"
        ew = "E" if self.longitude >= 0 else "W"
        return f"{abs(self.latitude):.1f}° {ns}, {abs(self.longitude):.1f}° {ew}"


def clock(value: str, default: str) -> str:
    """HH:MM, or the default if it isn't a time."""
    try:
        h, m = (int(x) for x in str(value).strip().split(":"))
        if 0 <= h < 24 and 0 <= m < 60:
            return f"{h:02d}:{m:02d}"
    except ValueError:
        pass
    return default


def describe(warmth: int) -> str:
    near = min(STEPS, key=lambda s: abs(s - warmth))
    return WORDS[near] if abs(near - warmth) < 250 else ("very warm" if warmth < 3000 else "just a touch")
