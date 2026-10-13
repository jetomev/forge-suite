"""Where the terminal's character cells are, in pixels: what the picture overlay needs (overlay.py).

Asked of the terminal itself before the app starts (Textual reads the keyboard after that): the text
area in pixels (`CSI 14 t`) and the grid in characters (`CSI 18 t`), so a cell is one divided by the
other. The text starts after the terminal's padding: Alacritty's comes from its settings (a plain
`padding`, or `dynamic_padding` spreading what's left over evenly).
"""

from __future__ import annotations

import os
import re
import select
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Cells:
    width: float              # one character, in pixels
    height: float
    pad_x: float = 0.0        # where the text starts inside the window
    pad_y: float = 0.0
    centred: bool = False     # the padding is spread evenly (Alacritty's dynamic_padding)
    origin: tuple[int, int] | None = None     # inside hypeForge Settings: where our pane's cell (0, 0) sits in its grid
    grid: tuple[int, int] | None = None       # and that grid's size (the terminal's, not the pane's)


# Inside hypeForge Settings (D-97, 2026-10-13): the pane is not a terminal window, so Settings measures
# its own terminal and hands the answer down, with where the pane sits and which page we are.
ENV_CELLS, ENV_PANE_AT, ENV_PAGE = "HYPEFORGE_TERM_CELLS", "HYPEFORGE_PANE_AT", "HYPEFORGE_SETTINGS_PAGE"


def from_settings(environ=None) -> Cells | None:
    """The cells hypeForge Settings handed down, or None when this isn't running in one of its panes."""
    env = os.environ if environ is None else environ
    try:
        cw, ch, px, py, c, cols, lines = env[ENV_CELLS].split()
        ox, oy = env[ENV_PANE_AT].split()
        return Cells(float(cw), float(ch), float(px), float(py), c == "1", (int(ox), int(oy)), (int(cols), int(lines)))
    except (KeyError, ValueError):
        return None


def settings_shows_me(environ=None, runtime: Path | None = None) -> bool:
    """Inside Settings: whether our page is the one on screen (Settings writes it to a file); True outside."""
    env = os.environ if environ is None else environ
    page = env.get(ENV_PAGE)
    if page is None:
        return True
    shown = (runtime or Path(env.get("XDG_RUNTIME_DIR", "/tmp"))) / "hypeforge-settings/shown"
    try:
        return shown.read_text().strip() == page
    except OSError:
        return True


def ask_terminal(timeout: float = 0.6) -> tuple[int, int, int, int] | None:
    """(text width px, text height px, columns, lines), or None when the terminal doesn't say."""
    if not (sys.stdin.isatty() and sys.stdout.isatty()) or os.environ.get("TERM") == "linux":
        return None
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    got = b""
    try:
        tty.setraw(fd)
        os.write(sys.stdout.fileno(), b"\x1b[14t\x1b[18t")
        end = time.monotonic() + timeout
        while time.monotonic() < end and not (re.search(rb"\x1b\[4;\d+;\d+t", got) and re.search(rb"\x1b\[8;\d+;\d+t", got)):
            ready, _, _ = select.select([fd], [], [], 0.05)
            if ready:
                got += os.read(fd, 256)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    px = re.search(rb"\x1b\[4;(\d+);(\d+)t", got)
    grid = re.search(rb"\x1b\[8;(\d+);(\d+)t", got)
    if not (px and grid):
        return None
    h, w = int(px.group(1)), int(px.group(2))
    lines, cols = int(grid.group(1)), int(grid.group(2))
    return (w, h, cols, lines) if w and h and cols and lines else None


def alacritty_padding(config: Path | None = None) -> tuple[float, float, bool]:
    """Alacritty's window padding from its settings (its imports first, the file itself last)."""
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "alacritty/alacritty.toml"
    f = config or base
    x = y = 0.0
    dynamic = False

    def read(p: Path, depth=0):
        nonlocal x, y, dynamic
        try:
            d = tomllib.loads(p.read_text())
        except (OSError, tomllib.TOMLDecodeError):
            return
        imports = d.get("general", {}).get("import", d.get("import", []))
        for i in imports if depth < 3 else []:
            read(Path(os.path.expanduser(i)), depth + 1)
        w = d.get("window", {})
        pad = w.get("padding", {})
        x, y = float(pad.get("x", x)), float(pad.get("y", y))
        dynamic = bool(w.get("dynamic_padding", dynamic))
    read(f)
    return x, y, dynamic


def measure() -> Cells | None:
    """The cells of the terminal this runs in, or None (a plain console, or a terminal that doesn't say).
    Inside hypeForge Settings the answer comes from Settings (the pane can't be asked)."""
    handed = from_settings()
    if handed is not None:
        return handed
    answer = ask_terminal()
    if answer is None:
        return None
    w, h, cols, lines = answer
    cells = Cells(w / cols, h / lines)
    if os.environ.get("ALACRITTY_WINDOW_ID") or os.environ.get("ALACRITTY_SOCKET"):
        cells.pad_x, cells.pad_y, cells.centred = alacritty_padding()
    else:
        cells.centred = True         # other terminals: assume the text sits in the middle
    return cells
