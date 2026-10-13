"""Where a terminal's character cells are, in pixels — asked of the terminal itself, before a Textual
app takes the keyboard. hypeForge Settings measures the terminal it runs in and hands the answer to
every app it opens in its panes (D-97, Javier 2026-10-13: themeForge's sharp wallpaper preview was
blurry inside Settings — the pane is not a terminal window, so themeForge could not ask one).

    HYPEFORGE_TERM_CELLS = "<cell width> <cell height> <pad x> <pad y> <centred 0|1> <columns> <lines>"
    HYPEFORGE_PANE_AT    = "<column> <row>"      where the pane's top-left cell sits in that grid
    HYPEFORGE_SETTINGS_PAGE = "<n>"              the page the app is; Settings writes the page on
                                                 screen to $XDG_RUNTIME_DIR/hypeforge-settings/shown

The text area in pixels is `CSI 14 t`, the grid in characters `CSI 18 t`; Alacritty's padding comes
from its settings (a plain `padding`, or `dynamic_padding` spreading what is left over evenly).
"""

from __future__ import annotations

import os
import re
import select
import sys
import time
import tomllib
from pathlib import Path

CELLS = "HYPEFORGE_TERM_CELLS"
PANE_AT = "HYPEFORGE_PANE_AT"
PAGE = "HYPEFORGE_SETTINGS_PAGE"


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


def measure() -> str | None:
    """The HYPEFORGE_TERM_CELLS value for the terminal this runs in, or None (a console, or a terminal
    that doesn't say)."""
    answer = ask_terminal()
    if answer is None:
        return None
    w, h, cols, lines = answer
    cw, ch = w / cols, h / lines
    if os.environ.get("ALACRITTY_WINDOW_ID") or os.environ.get("ALACRITTY_SOCKET"):
        px, py, centred = alacritty_padding()
    else:
        px, py, centred = 0.0, 0.0, True          # other terminals: assume the text sits in the middle
    return f"{cw:.4f} {ch:.4f} {px:g} {py:g} {int(centred)} {cols} {lines}"


def parse(value: str) -> dict | None:
    """The value back into numbers: {"width", "height", "pad_x", "pad_y", "centred", "cols", "lines"}."""
    try:
        cw, ch, px, py, c, cols, lines = value.split()
        return {"width": float(cw), "height": float(ch), "pad_x": float(px), "pad_y": float(py),
                "centred": c == "1", "cols": int(cols), "lines": int(lines)}
    except ValueError:
        return None
