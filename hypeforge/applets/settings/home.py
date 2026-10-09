"""hypeForge Settings · the Home page's summaries (#46; Javier picked the design 2026-10-08: cards, two columns).

One small function per card. Each asks the system with a short time limit and never raises: if it
cannot tell, the card says so in plain words. Plain Python, no Textual, so each one is testable alone.
`summaries()` returns the cards in the order shown: (title, up to three lines, page) — `page` is the Settings page
a click opens, or None while that setting has no app of its own yet.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tomllib
from datetime import datetime
from pathlib import Path

HOME = Path.home()
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config"))
UNKNOWN = "can't tell right now"

# (card title, function name, the Settings page it opens — None until that setting has an app)
CARDS = [
    ("Screens", "screens", "Screens"),
    ("Workspaces", "workspaces", "Workspaces"),
    ("Network", "network", None),
    ("Sound", "sound", None),
    ("Printer", "printer", None),
    ("Night light", "night_light", "Night light"),
    ("Default apps", "default_apps", "Default apps"),
    ("Passwords", "passwords", "Passwords"),
    ("Packages", "packages", "Packages"),
    ("Boot Menu", "boot_menu", "Boot Menu"),
    ("Terminal", "terminal", "Terminal"),
]


# An icon per setting, from the Nerd Font every KognogOS terminal uses (Javier, 2026-10-08). A plain text
# console can't draw them, so Settings leaves them out there (forgekit's console mode).
ICONS = {
    "Home": "\U000F02DC", "Screens": "\U000F0379", "Workspaces": "\U000F0570", "Network": "\U000F0318",
    "Sound": "\U000F057E", "Printer": "\U000F042A", "Night light": "\U000F0594", "Default apps": "\U000F003B", "Passwords": "\U000F0306",
    "Packages": "\U000F03D7", "Boot Menu": "\U000F0425", "Terminal": "\U000F018D", "Help & Keys": "\U000F030C",
    "Manual": "\U000F05DA", "License": "\U000F05D1", "About": "\U000F02FC", "Quit": "\U000F0206",
}
OTHER_ICON = "\U000F0493"                      # a gear: any page added later without its own


def icon(name: str, console: bool = False) -> str:
    """The icon and a space, or "" on a text console."""
    return "" if console else ICONS.get(name, OTHER_ICON) + " "


def run(*cmd: str, timeout: float = 3) -> str:
    """The command's output, or "" if it is missing, fails or takes too long."""
    if not shutil.which(cmd[0]):
        return ""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def screens() -> list[str]:
    out = run("swaymsg", "-t", "get_outputs", "-r")
    try:
        on = [o for o in json.loads(out) if o.get("active")]
    except ValueError:
        return [UNKNOWN]
    if not on:
        return ["no screen switched on"]
    on.sort(key=lambda o: (o["rect"]["y"], o["rect"]["x"]))
    row = len({o["rect"]["y"] for o in on}) == 1
    n = len(on)
    first = f"{n} screen{'s' if n != 1 else ''}" + (", side by side" if row and n > 1 else "")
    modes = {(o["current_mode"]["width"], o["current_mode"]["height"], round(o["current_mode"]["refresh"] / 1000))
             for o in on}
    scales = {o.get("scale", 1.0) for o in on}
    if len(modes) == 1:
        w, h, hz = next(iter(modes))
        second = f"{w} × {h} · {hz} Hz" + (f" · size {round(next(iter(scales)) * 100)} %" if len(scales) == 1 else "")
    else:
        second = "different sizes"
    try:
        with open(CONFIG / "displayforge/screens.toml", "rb") as f:
            names = tomllib.load(f).get("names", {})
    except (OSError, ValueError):
        names = {}
    third = " · ".join(names.get(o["name"], o["name"]).replace(" Monitor", "") for o in on)
    return [first, second, third]


def workspaces() -> list[str]:
    try:
        with open(CONFIG / "hypeforge/applets/workspaces.toml", "rb") as f:
            data = tomllib.load(f)
    except (OSError, ValueError):
        return [UNKNOWN]
    names = [w.get("name", "") for w in data.get("workspace", []) if w.get("name")]
    if not names:
        return [UNKNOWN]
    now = ""
    try:
        now = next(w["name"] for w in json.loads(run("swaymsg", "-t", "get_workspaces", "-r") or "[]")
                   if w.get("focused")).split(":")[-1]
    except (StopIteration, ValueError, KeyError):
        pass
    half = (len(names) + 1) // 2
    return [f"{len(names)} workspaces" + (f" · now on {now}" if now else ""),
            " · ".join(names[:half]), " · ".join(names[half:])]


def network() -> list[str]:
    out = run("nmcli", "-t", "-f", "TYPE,NAME,DEVICE", "connection", "show", "--active")
    if not out:
        return [UNKNOWN]
    rows = [line.split(":") for line in out.splitlines() if line.count(":") >= 2]
    first, device = "not connected", ""
    for kind, name, dev in rows:
        if "ethernet" in kind:
            first, device = "Wired · connected", dev
            break
        if "wireless" in kind:
            first, device = f"Wi-Fi {name} · connected", dev
            break
    addr = re.search(r"(\d+\.\d+\.\d+\.\d+)", run("ip", "-4", "-br", "addr", "show", device)) if device else None
    vpn = [name for kind, name, dev in rows if dev.startswith("tailscale") or kind in ("vpn", "wireguard")]
    return [first, f"address {addr.group(1)}" if addr else "no address yet",
            "VPN: " + ("Tailscale on" if any(n.startswith("tailscale") for n in vpn) else vpn[0] + " on") if vpn else "no VPN"]


def _device(target: str) -> tuple[str, str]:
    desc = run("wpctl", "inspect", target)
    m = re.search(r'node\.(?:nick|description)\s*=\s*"([^"]+)"', desc)
    name = (m.group(1) if m else "").replace(" Analog Stereo", "").replace(" Controller", "")
    vol = run("wpctl", "get-volume", target)
    v = re.search(r"Volume:\s*([\d.]+)", vol)
    level = "muted" if "MUTED" in vol else (f"{round(float(v.group(1)) * 100)} %" if v else "")
    return name, level


def sound() -> list[str]:
    out_name, out_level = _device("@DEFAULT_AUDIO_SINK@")
    in_name, in_level = _device("@DEFAULT_AUDIO_SOURCE@")
    if not (out_name or out_level):
        return [UNKNOWN]
    return [f"out: {out_name or 'speakers'}", f"volume {out_level}" if out_level else "volume unknown",
            f"mic: {in_name} · {in_level}" if in_name else "no microphone"]


def printer() -> list[str]:
    default = run("lpstat", "-d")
    m = re.search(r"destination:\s*(\S+)", default)
    if not m:
        return ["none set up" if shutil.which("lpstat") else UNKNOWN]
    name = m.group(1)
    state = run("lpstat", "-p", name)
    word = "ready" if "idle" in state else "printing" if "printing" in state else "paused" if "disabled" in state else ""
    count = sum(1 for line in run("lpstat", "-p").splitlines() if line.startswith("printer"))
    jobs = sum(1 for line in run("lpstat", "-o").splitlines() if line.strip())
    return [" · ".join(x for x in (name.replace("_", " "), word) if x),
            f"the default · {count} set up",
            "nothing waiting to print" if not jobs else f"{jobs} waiting to print"]


def night_light() -> list[str]:
    args = run("ps", "-o", "args=", "-C", "wlsunset")
    if not args and not shutil.which("wlsunset"):
        return ["not installed"]
    lat = re.search(r"-l\s+(-?[\d.]+)", args)
    lon = re.search(r"-L\s+(-?[\d.]+)", args)
    cold = re.search(r"-t\s+(\d+)", args)
    place = (f"sun times for {abs(float(lat.group(1))):.1f}° {'N' if float(lat.group(1)) >= 0 else 'S'}, "
             f"{abs(float(lon.group(1))):.1f}° {'E' if float(lon.group(1)) >= 0 else 'W'}") if lat and lon else "place not set"
    return ["on now" if args else "off", f"{cold.group(1) if cold else 4000} K after sunset, back by sunrise", place]


def default_apps() -> list[str]:
    """Three of the fourteen: what opens links, folders and text now (the standard lookup)."""
    def name(mime: str) -> str:
        did = run("xdg-mime", "query", "default", mime).strip()
        if not did:
            return "not set"
        for d in (HOME / ".local/share/applications", Path("/usr/share/applications")):
            f = d / did
            if f.is_file():
                m = re.search(r"^Name=(.+)$", f.read_text(errors="replace"), re.M)
                if m:
                    return m.group(1).strip()
        return did.removesuffix(".desktop")
    return [f"links: {name('x-scheme-handler/https')}", f"folders: {name('inode/directory')}",
            f"text: {name('text/plain')}"]


def passwords() -> list[str]:
    out = run("sudoforge", "status")
    if not out:
        return ["sudoForge not installed" if not shutil.which("sudoforge") else UNKNOWN]
    ver = re.search(r"sudoForge\s+([\d.]+)", out)
    running = "running" in out
    box = "sudoForge's box" in out
    return ["asked in sudoForge's box" if box else "not set up yet",
            "admin pop-ups and sudo" if box else "run its setup to use it",
            f"sudoForge {ver.group(1) if ver else ''} · {'running' if running else 'not running'}".replace("  ", " ")]


def packages() -> list[str]:
    total = len(run("pacman", "-Qq").splitlines())
    aur = len(run("pacman", "-Qqm").splitlines())
    stamp = HOME / ".local/share/nog/last-update"
    try:
        when = datetime.fromtimestamp(stamp.stat().st_mtime)
        days = (datetime.now().date() - when.date()).days
        ago = "today" if days == 0 else "yesterday" if days == 1 else f"{days} days ago"
        updated = f"last updated {ago} · {when.strftime('%b %-d')}"
    except OSError:
        updated = "no update recorded yet"
    nog = re.search(r"nog\s+([\d.]+)", run("nog", "--version"))
    return [f"{total:,} installed · {aur} from the AUR" if total else UNKNOWN, updated,
            f"kept safe by nog {nog.group(1)}" if nog else "nog not found"]


def boot_menu() -> list[str]:
    try:
        text = Path("/etc/default/grub").read_text()
    except OSError:
        return ["GRUB not found"]
    try:
        entries = len(re.findall(r"^\s*menuentry ", Path("/boot/grub/grub.cfg").read_text(), re.M))
    except OSError:
        entries = 0
    d = re.search(r'^GRUB_DEFAULT="?([^"\n]*)', text, re.M)
    first = {"0": "starts the first one", "saved": "starts the last one used"}.get(d.group(1) if d else "0",
                                                                                   "starts a chosen one")
    t = re.search(r'^GRUB_TIMEOUT="?(-?\d+)', text, re.M)
    secs = int(t.group(1)) if t else None
    wait = UNKNOWN if secs is None else "waits until you pick" if secs < 0 else \
        "starts at once" if secs == 0 else f"waits {secs} seconds"
    theme = re.search(r'^GRUB_THEME="?([^"\n]+)', text, re.M)
    return [(f"{entries} entries · " if entries else "") + first, wait,
            f"theme: {Path(theme.group(1)).parent.name}" if theme else "no theme"]


def terminal() -> list[str]:
    try:
        with open(CONFIG / "alacritty/alacritty.toml", "rb") as f:
            cfg = tomllib.load(f)
    except (OSError, ValueError):
        return ["Alacritty · default look"]
    imports = cfg.get("general", {}).get("import") or cfg.get("import") or []
    theme = Path(imports[-1]).stem.replace("-theme", "").replace("-", " ") if imports else "default colours"
    font = cfg.get("font", {})
    family = font.get("normal", {}).get("family", "monospace").replace(" Nerd Font", "")
    size = font.get("size")
    opacity = cfg.get("window", {}).get("opacity", 1.0)
    shape = cfg.get("cursor", {}).get("style", {})
    shape = shape.get("shape", "Block") if isinstance(shape, dict) else shape
    return [f"Alacritty · {theme} theme", f"{family} {size:g}" if size else family,
            f"{round(opacity * 100)} % solid · {str(shape).lower()} cursor"]


def summaries() -> list[tuple[str, list[str], str | None]]:
    """(title, up to three lines, page) per card (Javier, 2026-10-08: three rows of what matters)."""
    out = []
    for title, fn, page in CARDS:
        try:
            lines = [x for x in globals()[fn]() if x][:3] or [UNKNOWN]
        except Exception:                            # a card never takes Settings down
            lines = [UNKNOWN]
        out.append((title, lines, page))
    return out
