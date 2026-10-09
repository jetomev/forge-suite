"""hypeForge applets · which app a window is, and which workspace it opens on (F-50, #55).

Each workspace in workspaces.toml can list its apps by their launcher names (desktop ids:
"steam", "google-chrome", "Sim Companies"…). A new window is matched to a listed app by the names
the window carries (a Wayland app_id; an older X11 app's class and instance) against the names
the app's desktop entry gives: its id, its StartupWMClass, its Name, and the program it runs.

Shared by the Workspaces applet (moves a listed app's new windows to its workspace), Window
Placement (leaves those windows to it) and the launcher (opens an app on its workspace).
Python standard library only.
"""

import os
import re
import shlex
import tomllib
from configparser import ConfigParser
from pathlib import Path

HOME = Path.home()
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config")) / "hypeforge/applets"
WORKSPACES = CONFIG_DIR / "workspaces.toml"
RUNTIME = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp"))
CURRENT = RUNTIME / "hypeforge-workspaces.current"  # the workspace on screen now (1, 2, …)
DESKTOP_NAMES = {"sway", "wlroots"}
TERMINAL = "alacritty"
ARRIVED = "_hypeforge_arrived_"   # the Workspaces applet's mark on a window it has taken over;
                                  # Sway hides marks that start with "_"
QUIET_AFTER_LOGIN = 30            # seconds: apps that start themselves don't move the screens

# Programs that only start another one: their name says nothing about the window.
WRAPPERS = {"env", "sh", "bash", "dash", "exec", "nohup", "setsid", "gtk-launch", "python", "python3",
            "wine", "dbus-launch", "sudo", "pkexec", "xdg-open", "kioclient", "kioclient5", "flatpak"}


# ---- The apps on this computer ---------------------------------------------------------------

def application_dirs():
    data_home = Path(os.environ.get("XDG_DATA_HOME", HOME / ".local/share"))
    data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":")
    return [data_home / "applications"] + [Path(d) / "applications" for d in data_dirs if d]


def apps():
    """{desktop id: {name, icon, exec, terminal, categories, wmclass}} — what a start menu shows."""
    found = {}
    for folder in application_dirs():  # the first folder wins (your own entries over the system's)
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*.desktop")):
            app_id = str(path.relative_to(folder))[:-len(".desktop")].replace("/", "-")
            if app_id in found:
                continue
            parser = ConfigParser(interpolation=None, strict=False)
            parser.optionxform = str
            try:
                parser.read(path, encoding="utf-8")
                entry = parser["Desktop Entry"]
            except Exception:
                continue
            found[app_id] = None  # seen: a hidden copy still hides the system one
            only = set(entry.get("OnlyShowIn", "").lower().split(";")) - {""}
            never = set(entry.get("NotShowIn", "").lower().split(";")) - {""}
            if (entry.get("Type") != "Application" or entry.get("NoDisplay") == "true"
                    or entry.get("Hidden") == "true" or not entry.get("Exec")
                    or (only and not only & DESKTOP_NAMES) or never & DESKTOP_NAMES):
                continue
            found[app_id] = {
                "name": entry.get("Name", app_id),
                "icon": entry.get("Icon", "application-x-executable"),
                "exec": entry.get("Exec"),
                "terminal": entry.get("Terminal") == "true",
                "categories": set(entry.get("Categories", "").split(";")) - {""},
                "wmclass": entry.get("StartupWMClass", ""),
            }
    return {k: v for k, v in found.items() if v}


def command_for(app_id, app):
    """The app's Exec line without the %f/%u… placeholders. One that runs in a terminal gets a
    terminal named after the app (Alacritty's --class), so its window can be told apart from
    any other terminal: btop opened from the launcher is "btop", not just "Alacritty"."""
    cmd = re.sub(r"\s*%[fFuUdDnNickvm]", "", app["exec"]).replace("%%", "%").strip()
    return f"{TERMINAL} --class {shlex.quote(app_id)} -e {cmd}" if app["terminal"] else cmd


# ---- An app's names, a window's names --------------------------------------------------------

def app_names(app_id, app):
    """(strong, weak): the names a window of this app may carry. Strong ones say exactly which app
    (its id, its StartupWMClass, a terminal's --class, a Steam game's number); weak ones only
    probably (its Name, the program it runs) and lose to a strong one."""
    strong = {app_id.lower()}
    weak = {app["name"].lower()}
    if app.get("wmclass"):
        strong.add(app["wmclass"].lower())
    if "." in app_id:  # org.keepassxc.KeePassXC → keepassxc
        weak.add(app_id.rsplit(".", 1)[-1].lower())
    try:
        args = shlex.split(re.sub(r"\s*%[fFuUdDnNickvm]", "", app["exec"]))
    except ValueError:
        args = []
    while args and ("=" in args[0] and not args[0].startswith("/") or os.path.basename(args[0]) in WRAPPERS):
        if os.path.basename(args[0]) == "flatpak" and "run" in args:  # flatpak run org.app.Id
            rest = [a for a in args[args.index("run") + 1:] if not a.startswith("-")]
            if rest:
                strong.add(rest[0].lower())
            args = []
            break
        args = args[1:]
    if args:
        program = os.path.basename(args[0]).lower()
        if program == "steam":
            game = next((re.search(r"rungameid/(\d+)", a) for a in args if "rungameid/" in a), None)
            if game:  # a Steam game: Steam's own name for its window is steam_app_<number>
                strong.add(f"steam_app_{game.group(1)}")
            else:
                weak.add("steam")
        elif program == TERMINAL:
            for i, a in enumerate(args):
                if a == "--class" and i + 1 < len(args):
                    strong.add(args[i + 1].split(",")[0].lower())
                elif a.startswith("--class="):
                    strong.add(a.split("=", 1)[1].split(",")[0].lower())
            if "-e" not in args and "--command" not in args:
                weak.add(TERMINAL)  # the terminal itself
        else:
            weak.add(program)
    if app.get("terminal"):
        strong.add(app_id.lower())  # the launcher opens it as `alacritty --class <id>`
    return strong, weak - strong


def window_names(node):
    """The names a window in Sway's tree carries, lower case."""
    props = node.get("window_properties") or {}
    names = {str(n).lower() for n in (node.get("app_id"), props.get("class"), props.get("instance")) if n}
    # a reverse-domain name also answers to its last part: net.code-industry.masterpdfeditor4
    # is Master PDF Editor's window, launched as "masterpdfeditor4"
    return names | {n.rsplit(".", 1)[-1] for n in names if "." in n and not n.endswith(".exe")}


# ---- The workspaces' app lists ---------------------------------------------------------------

def lists(path=WORKSPACES):
    """[(workspace name, [desktop ids])] in workspace order (Win + 1, Win + 2, …)."""
    try:
        with open(path, "rb") as f:
            cfg = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return []
    return [(w.get("name", ""), [str(a) for a in w.get("apps", [])]) for w in cfg.get("workspace", [])]


class AppIndex:
    """Which workspace (1, 2, …) a window or an app opens on, from the lists. Rebuilt by itself
    when the lists or the installed apps change."""

    def __init__(self, path=WORKSPACES, entries=None):
        self.path = Path(path)
        self.fixed_entries = entries   # tests hand their own apps in
        self.stamp = None
        self.by_app = {}
        self.strong, self.weak = {}, {}

    def _stamp(self):
        stamp = []
        for p in [self.path] + application_dirs():
            try:
                stamp.append(p.stat().st_mtime_ns)
            except OSError:
                stamp.append(None)
        return tuple(stamp)

    def _refresh(self):
        stamp = self._stamp()
        if stamp == self.stamp:
            return
        self.stamp = stamp
        entries = self.fixed_entries if self.fixed_entries is not None else apps()
        self.by_app, self.strong, self.weak = {}, {}, {}
        for index, (_, members) in enumerate(lists(self.path), 1):
            for app_id in members:
                self.by_app.setdefault(app_id, index)  # one app, one workspace: the first list wins
        for app_id, index in self.by_app.items():
            if app_id not in entries:
                self.strong.setdefault(app_id.lower(), index)
                continue
            strong, weak = app_names(app_id, entries[app_id])
            for n in strong:
                self.strong.setdefault(n, index)
            for n in weak:
                self.weak.setdefault(n, index)

    def of_app(self, app_id):
        self._refresh()
        return self.by_app.get(app_id)

    def of_window(self, node):
        self._refresh()
        names = window_names(node)
        for n in sorted(names):
            if n in self.strong:
                return self.strong[n]
        for n in sorted(names):
            if n in self.weak:
                return self.weak[n]
        return None


# ---- Small shared facts ----------------------------------------------------------------------

def current_workspace():
    try:
        return int(CURRENT.read_text())
    except (OSError, ValueError):
        return 1


def taken_over(node):
    """True when the Workspaces applet has already taken this window to its workspace."""
    return any(m.startswith(ARRIVED) for m in node.get("marks", []))


def just_logged_in(seconds=QUIET_AFTER_LOGIN):
    """True in the first seconds of the session (Sway's socket is made when Sway starts)."""
    import time
    sock = os.environ.get("SWAYSOCK")
    try:
        return time.time() - os.stat(sock).st_mtime < seconds
    except (OSError, TypeError):
        return False
