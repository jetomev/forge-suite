"""Web apps as default apps (D-5, Javier, 2026-10-27: "I cannot select among the apps, for email or calendar,
chrome (gmail.com apps) which should be available").

A web app is offered for a job only where it can do that job from a link: an email link (mailto:) for Gmail
or Outlook, a calendar invite or hypeForge's "click a day" for Google Calendar or Outlook's calendar, an
address (geo:) for the maps, a phone number (tel:) for Google Voice. Picking one writes a small launcher,
`~/.local/share/applications/kognogos-web-<name>.desktop`, that runs `webapp-open <name> <link>`: the link
made into the web app's address and opened in its own window of the browser (Chrome, Chromium, Brave, Edge,
Vivaldi: `--app=`), or in a plain tab of any other browser. YouTube Music and Google Docs can't open a file
on the computer, so they're never a file default (LIBRARY_ONLY: App Library launchers).

Python standard library only: the launcher's opener runs without the app.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
OPENER = HERE / "webapp-open"
PREFIX = "kognogos-web-"
CHROMIUMS = {"google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "brave", "brave-browser",
             "microsoft-edge", "microsoft-edge-stable", "vivaldi", "vivaldi-stable"}


@dataclass(frozen=True)
class WebApp:
    key: str
    name: str
    role: str | None              # the default app it can be (roles.py), None: App Library only
    home: str                     # its address with nothing to open
    handles: tuple[str, ...]      # the links it takes (MIME types / URL schemes)
    icon: str
    comment: str


WEB_APPS = [
    WebApp("gmail", "Gmail", "email", "https://mail.google.com/mail/", ("x-scheme-handler/mailto",), "gmail",
           "Your Gmail, in its own window; email links open a new message"),
    WebApp("outlook-mail", "Outlook", "email", "https://outlook.office.com/mail/", ("x-scheme-handler/mailto",),
           "ms-outlook", "Outlook's mail, in its own window; email links open a new message"),
    WebApp("google-calendar", "Google Calendar", "calendar", "https://calendar.google.com/calendar/r",
           ("text/calendar", "x-scheme-handler/webcal"), "calendar", "Your Google Calendar, in its own window"),
    WebApp("outlook-calendar", "Outlook Calendar", "calendar", "https://outlook.office.com/calendar/view/month",
           ("text/calendar", "x-scheme-handler/webcal"), "ms-outlook", "Outlook's calendar, in its own window"),
    WebApp("google-maps", "Google Maps", "map", "https://www.google.com/maps", ("x-scheme-handler/geo",), "maps",
           "Places and addresses on Google Maps"),
    WebApp("openstreetmap", "OpenStreetMap", "map", "https://www.openstreetmap.org", ("x-scheme-handler/geo",), "maps",
           "Places and addresses on OpenStreetMap"),
    WebApp("google-voice", "Google Voice", "phone", "https://voice.google.com/u/0/calls",
           ("x-scheme-handler/tel", "x-scheme-handler/callto"), "phone", "Call a number with Google Voice"),
]
LIBRARY_ONLY = [
    WebApp("youtube-music", "YouTube Music", None, "https://music.youtube.com", (), "youtube-music",
           "YouTube Music, in its own window"),
    WebApp("google-docs", "Google Docs", None, "https://docs.google.com", (), "google-docs",
           "Google Docs, in its own window"),
]
BY_KEY = {w.key: w for w in WEB_APPS + LIBRARY_ONLY}


def launcher_id(w: WebApp) -> str:
    return f"{PREFIX}{w.key}.desktop"


def is_web(desktop_id: str | None) -> bool:
    return bool(desktop_id) and desktop_id.startswith(PREFIX)


def for_role(role: str) -> list[WebApp]:
    return [w for w in WEB_APPS if w.role == role]


def launcher_text(w: WebApp, opener: Path = OPENER) -> str:
    """The desktop entry: what the App Library shows, and what the system runs for a link."""
    lines = ["[Desktop Entry]", "Type=Application", f"Name={w.name}", f"Comment={w.comment}",
             f"Exec={shlex.quote(sys.executable)} {shlex.quote(str(opener))} {w.key} %u", f"Icon={w.icon}",
             "Categories=Network;", "StartupNotify=true",
             "X-KognogOS-WebApp=" + w.key]
    if w.handles:
        lines.append("MimeType=" + ";".join(w.handles) + ";")
    return "\n".join(lines) + "\n"


def write_launcher(w: WebApp, apps_dir: Path, opener: Path = OPENER) -> Path:
    apps_dir.mkdir(parents=True, exist_ok=True)
    path = apps_dir / launcher_id(w)
    tmp = path.with_name("." + path.name + ".tmp")
    tmp.write_text(launcher_text(w, opener))
    os.replace(tmp, path)
    return path


def address(w: WebApp, link: str = "", day: str = "") -> str:
    """The web app's address for what was opened: an email link, an invite, a place, a number, a day."""
    link = link.strip()
    if w.key == "gmail" and link.startswith("mailto:"):
        return "https://mail.google.com/mail/?extsrc=mailto&url=" + quote(link, safe="")
    if w.key == "outlook-mail" and link.startswith("mailto:"):
        return "https://outlook.office.com/mail/deeplink/compose?mailtouri=" + quote(link, safe="")
    if w.key == "google-calendar":
        if day:
            y, m, d = (int(x) for x in day.split("-"))
            return f"https://calendar.google.com/calendar/r/day/{y}/{m}/{d}"
        if link.startswith(("webcal:", "http")):
            return "https://calendar.google.com/calendar/r?cid=" + quote(link, safe="")
    if w.key == "outlook-calendar" and day:
        y, m, d = (int(x) for x in day.split("-"))
        return f"https://outlook.office.com/calendar/view/day/{y}/{m}/{d}"
    if w.key in ("google-maps", "openstreetmap") and link.startswith("geo:"):
        place = link[4:]
        q = place.split("?q=", 1)[1] if "?q=" in place else place.split("?", 1)[0]
        return ("https://www.google.com/maps/search/?api=1&query=" if w.key == "google-maps"
                else "https://www.openstreetmap.org/search?query=") + quote(q, safe=",")
    if w.key == "google-voice" and link.startswith(("tel:", "callto:")):
        return "https://voice.google.com/u/0/calls?a=nc," + quote(link.split(":", 1)[1], safe="+")
    return w.home


def browser_command(url: str, which=shutil.which, ask=None) -> list[str]:
    """The default browser's own window for it (`--app=`) when it can make one, else a tab (xdg-open)."""
    if ask is None:
        def ask():
            try:
                return subprocess.run(["xdg-settings", "get", "default-web-browser"], capture_output=True,
                                      text=True, timeout=3).stdout.strip()
            except (OSError, subprocess.SubprocessError):
                return ""
    entry = ask().removesuffix(".desktop")
    for name in [entry] + sorted(CHROMIUMS):
        if name in CHROMIUMS and which(name):
            return [name, f"--app={url}"]
    return ["xdg-open", url]


def apps_dir() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "applications"


def to_library(keys: list[str], where: Path, remove: bool = False) -> list[str]:
    """YouTube Music, Google Docs…: put in (or taken out of) the App Library, never anyone's default."""
    done = []
    for key in keys:
        path = where / launcher_id(BY_KEY[key])
        if remove:
            if path.exists():
                path.unlink()
                done.append(key)
        else:
            write_launcher(BY_KEY[key], where)
            done.append(key)
    return done


def main(argv: list[str]) -> int:
    """webapp-open <name> [link] [--day=YYYY-MM-DD] · webapp-open --add|--remove <name>…"""
    if argv and argv[0] in ("--add", "--remove"):
        keys = argv[1:]
        wrong = [k for k in keys if k not in BY_KEY]
        if not keys or wrong:
            print(f"webapp-open {argv[0]} <" + "|".join(BY_KEY) + ">…", file=sys.stderr)
            return 2
        done = to_library(keys, apps_dir(), remove=argv[0] == "--remove")
        verb = "Added to" if argv[0] == "--add" else "Taken out of"
        print(f"{verb} the App Library: " + (", ".join(BY_KEY[k].name for k in done) or "nothing to do"))
        return 0
    if not argv or argv[0] not in BY_KEY:
        print("webapp-open <" + "|".join(BY_KEY) + "> [link] [--day=YYYY-MM-DD]", file=sys.stderr)
        return 2
    w = BY_KEY[argv[0]]
    day = next((a.split("=", 1)[1] for a in argv[1:] if a.startswith("--day=")), "")
    link = next((a for a in argv[1:] if not a.startswith("--day=")), "")
    subprocess.Popen(browser_command(address(w, link, day)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    return 0
