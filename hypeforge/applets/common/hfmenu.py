"""hypeForge applets · our pop-up lists (fuzzel in dmenu mode), one at a time.

Shared by the launcher, the workspace dropdown, the bell and the clipboard. Pressing the same
button (or key) again closes its list; opening another list closes the one on screen first
(Javier, 2026-10-05). Python standard library only.
"""

import os
import signal
import subprocess
import sys
from pathlib import Path

BACKDROP = Path(__file__).resolve().with_name("hfbackdrop.py")   # a click anywhere else closes the list

OPEN = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "hypeforge-menu.open"  # "<pid> <name>"


def config_path(path: str) -> str:
    """A "~/.config/…" path in the config folder in use: $XDG_CONFIG_HOME when set (a hidden preview
    sets it), else ~/.config. Everything else is just ~-expanded (F-81, 2026-10-20)."""
    base = os.environ.get("XDG_CONFIG_HOME")
    if base and path.startswith("~/.config/"):
        return os.path.join(base, path[len("~/.config/"):])
    return os.path.expanduser(path)


LOOK = config_path("~/.config/sway/fuzzel/fuzzel.ini")   # every list's look (fuzzel --config)


PANEL = Path(__file__).resolve().parent.parent / "panels/hypeforge-panel"
PLACES = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "hypeforge-bar/hypeforge-popup-places.json"
LAUNCHERS = {"launcher"}    # the launcher is each theme's identity (D-116): it stays fuzzel


def ours(pid: int) -> bool:
    """A list of ours: fuzzel, or the list card (hypeforge-panel list)."""
    try:
        if Path(f"/proc/{pid}/comm").read_text().strip() == "fuzzel":
            return True
        return b"hypeforge-panel" in Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return False


def close_open(name):
    """Close our list on screen, if any. True when it was `name`'s own: that press meant 'close'."""
    try:
        pid, owner = OPEN.read_text().split(maxsplit=1)
        pid = int(pid)
        if not ours(pid):
            return False
        os.kill(pid, signal.SIGTERM)
        return owner.strip() == name
    except (OSError, ValueError):
        return False


CARDS = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "hypeforge/list-cards"


def cards_on() -> bool:
    """The list cards are on (D-116) once Javier approves them: until then only where switched on —
    HYPEFORGE_LIST_CARDS=1 (the hidden previews) or the file ~/.config/hypeforge/list-cards.
    HYPEFORGE_FUZZEL_LISTS=1 always means fuzzel."""
    if os.environ.get("HYPEFORGE_FUZZEL_LISTS") == "1":
        return False
    return os.environ.get("HYPEFORGE_LIST_CARDS") == "1" or CARDS.exists()


def option(command, flag, default=None):
    """A fuzzel option's value from its command: ["--width", "28"] or "--width=28"."""
    for i, a in enumerate(command):
        if a == flag and i + 1 < len(command):
            return command[i + 1]
        if a.startswith(flag + "="):
            return a.split("=", 1)[1]
    return default


def bar_place():
    """Where the bar's pop-ups sit, from what hypeforge-bar wrote at its start: (edge, pixels from it)."""
    try:
        import json
        words = json.loads(PLACES.read_text())["{popup}"].split()
        edge = words[words.index("--edges") + 1].split(",")[0]
        away = dict(m.split("=") for m in words[words.index("--margin") + 1].split(","))[edge]
        return edge, int(away)
    except (OSError, ValueError, KeyError, IndexError):
        return "top", 34


def card_input(command, text):
    """The list card's input (views/listcard.py) and its place, from a fuzzel command and its lines.
    The lines: "words" or "words\0icon\x1f<icon>"; a leading ● marks the current one."""
    rows = []
    for line in text.split("\n"):
        words, _, rest = line.partition("\0")
        icon = rest.split("\x1f", 1)[1] if rest.startswith("icon\x1f") else ""
        mark = words.lstrip().startswith("●")
        words = words.strip().lstrip("●").strip()
        if words:
            rows.append({"text": words, "icon": icon, "mark": mark})
    title = (option(command, "--prompt", "") or "").replace("❯", "").strip()
    data = {"title": title, "rows": rows, "index": "--index" in command,
            "selected": int(option(command, "--select-index", "0") or 0)}
    edge, away = bar_place()
    anchor = option(command, "--anchor", "top-left")
    side = "left" if "left" in anchor else "right" if "right" in anchor else None
    edges, margins = [edge], {edge: away}
    if side:
        edges.append(side)
        margins[side] = max(int(option(command, "--x-margin", "8") or 8), 8)
    return data, ",".join(edges), ",".join(f"{k}={v}" for k, v in margins.items())


def run(name, command, text):
    """Show a list; the pick (fuzzel's answer: the row's number with --index, else its words), or None
    (Esc / closed). Every list but the launcher is the list card in the pop-up standard (D-116);
    HYPEFORGE_FUZZEL_LISTS=1 is the way back to fuzzel. Opened from a bar, it shows on that bar's
    screen (HYPEFORGE_OUTPUT, set by hypeforge-bar)."""
    if name not in LAUNCHERS and cards_on() and PANEL.exists():
        return run_card(name, command, text)
    screen = os.environ.get("HYPEFORGE_OUTPUT")
    if screen and command and command[0] == "fuzzel" and not any(a.startswith(("--output", "-o")) for a in command):
        command = [command[0], f"--output={screen}", *command[1:]]
    menu = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    OPEN.write_text(f"{menu.pid} {name}")
    shade = None
    if os.environ.get("WAYLAND_DISPLAY") and BACKDROP.exists():   # Javier, 2026-10-10: close on a click elsewhere
        try:
            shade = subprocess.Popen([sys.executable, str(BACKDROP), str(menu.pid)],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            shade = None
    out, _ = menu.communicate(text.encode())
    if shade is not None:
        shade.terminate()
        try:
            shade.wait(2)
        except subprocess.TimeoutExpired:
            shade.kill()
    try:
        if OPEN.read_text().split()[0] == str(menu.pid):
            OPEN.unlink()
    except (OSError, IndexError):
        pass
    if menu.returncode != 0 or not out.strip():
        return None
    return out.decode().rstrip("\n")


def run_card(name, command, text):
    """The list card: hypeforge-panel list, its rows on stdin, the pick on stdout (it has its own backdrop)."""
    import json
    data, edges, margins = card_input(command, text)
    card = subprocess.Popen([sys.executable, str(PANEL), "list", "--edges", edges, "--margin", margins],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    OPEN.write_text(f"{card.pid} {name}")
    out, _ = card.communicate(json.dumps(data).encode())
    try:
        if OPEN.read_text().split()[0] == str(card.pid):
            OPEN.unlink()
    except (OSError, IndexError):
        pass
    out = out.decode().strip()
    return out or None
