"""displayForge · brightness through the screens' own control channel (DDC/CI, via ddcutil),
and the remembered answers of Identify: which control is which screen, and the screens' names.

No password is needed here (the control devices carry an access entry for the logged-in user).
Screens that report identical identities cannot be told apart by software (ddcutil says so),
so which bus belongs to which screen is asked once (Identify) and remembered — never guessed.
"""

from __future__ import annotations

import os
import re
import subprocess
import tomllib
from pathlib import Path

CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "displayforge/screens.toml"
STEPS = tuple(range(10, 101, 10))  # D-2: brightness in tens


def tens(value: int) -> int:
    """Round to the nearest ten, 10 … 100."""
    return min(100, max(10, int(round(value / 10.0)) * 10))


def buses(ddcutil: str = "ddcutil") -> list[int]:
    out = subprocess.run([ddcutil, "detect", "--brief"], capture_output=True, text=True).stdout
    return sorted(int(n) for n in re.findall(r"/dev/i2c-(\d+)", out))


def get(bus: int, ddcutil: str = "ddcutil") -> int | None:
    out = subprocess.run([ddcutil, "--bus", str(bus), "getvcp", "10", "--brief"],
                         capture_output=True, text=True).stdout
    m = re.search(r"VCP 10 \S+ (\d+) (\d+)", out)
    return round(int(m.group(1)) * 100 / int(m.group(2))) if m and int(m.group(2)) else None


def set_(bus: int, percent: int, ddcutil: str = "ddcutil") -> bool:
    return subprocess.run([ddcutil, "--bus", str(bus), "setvcp", "10", str(int(percent))],
                          capture_output=True).returncode == 0


# -- what Identify remembers ---------------------------------------------------------------------

def load(path: Path | None = None) -> dict:
    path = path or CONFIG
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        data = {}
    return {"names": dict(data.get("names", {})), "bus": {k: int(v) for k, v in data.get("bus", {}).items()}}


def save(data: dict, path: Path | None = None) -> None:
    path = path or CONFIG
    def q(s: str) -> str:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    lines = ["# displayForge — what Identify remembers. Edit it in displayForge (Identify).", "",
             "# Your names for the screens (shown everywhere in displayForge)", "[names]"]
    lines += [f"{q(k)} = {q(v)}" for k, v in sorted(data.get("names", {}).items())]
    lines += ["", "# Which brightness control (I2C bus) belongs to which screen — answered by you", "[bus]"]
    lines += [f"{q(k)} = {int(v)}" for k, v in sorted(data.get("bus", {}).items())]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text("\n".join(lines) + "\n")
    os.replace(tmp, path)
