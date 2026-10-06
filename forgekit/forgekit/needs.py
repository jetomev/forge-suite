"""The shared start-up check (0.7.0, forge-suite #33).

Javier's rule (2026-10-06, from displayForge): an app that cannot do its job
here must say so in plain words and close, instead of crashing with an error
dump. So every Forge app declares what it needs, and one standard screen
explains what is missing:

    NEEDS = [sway_session("displayForge arranges your screens by talking to Sway.",
                          "Use your desktop's own display settings instead.")]

    def main() -> int:
        if not start_check("displayForge", NEEDS):
            return 2
        DisplayForgeApp().run()
        return 0

``start_check`` returns True when the app may go on: nothing is missing, or
only optional needs are, and the person chose **Continue anyway**. When it
returns False the screen was shown and closed, and the same words were printed
to the terminal (the run's record, like ``closing_notice``). Nothing is touched.

Four kinds of need come ready-made (``sway_session``, ``program``, ``service``,
``a_file``); anything else is a ``Need`` with its own ``check`` callable.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

Check = Callable[[], tuple[bool, str]]   # -> (met, what was found, in words)


@dataclass
class Need:
    """One thing the app needs, in words a person reads on the screen.

    ``what``: "a Sway session", "nog 1.7.0 or newer" (completes "Needs …").
    ``why``: one sentence on why the app needs it.
    ``instead``: what to do or use instead (may be empty).
    ``optional``: the app still works without it; the screen offers
    **Continue anyway** when every missing need is optional.
    """
    what: str
    check: Check
    why: str
    instead: str = ""
    optional: bool = False


@dataclass
class Finding:
    need: Need
    met: bool
    found: str


def check_needs(needs: Sequence[Need]) -> list[Finding]:
    """Run every check; a check that raises counts as not met."""
    out = []
    for n in needs:
        try:
            met, found = n.check()
        except Exception as e:                       # noqa: BLE001 — the screen must appear anyway
            met, found = False, f"the check itself failed ({e.__class__.__name__})"
        out.append(Finding(n, bool(met), found))
    return out


def missing(findings: Sequence[Finding]) -> list[Finding]:
    return [f for f in findings if not f.met]


# ── what is running here, in words ───────────────────────────────────────────

_DESKTOP_NAMES = {
    "kde": "KDE Plasma", "gnome": "GNOME", "hyprland": "Hyprland", "sway": "Sway",
    "x-cinnamon": "Cinnamon", "xfce": "Xfce", "lxqt": "LXQt", "mate": "MATE",
    "niri": "niri", "i3": "i3", "river": "river", "cosmic": "COSMIC",
}


def describe_session(environ: Mapping[str, str] | None = None) -> str:
    """"KDE Plasma (Wayland)", "an X11 session (i3)", "a text console"…"""
    env = os.environ if environ is None else environ
    if env.get("HYPRLAND_INSTANCE_SIGNATURE"):
        desk = "hyprland"
    else:
        desk = (env.get("XDG_CURRENT_DESKTOP") or env.get("XDG_SESSION_DESKTOP")
                or env.get("DESKTOP_SESSION") or "")
        desk = desk.split(":")[0].strip().lower()
    if env.get("WAYLAND_DISPLAY"):
        kind = "Wayland"
    elif env.get("DISPLAY"):
        kind = "X11"
    else:
        if env.get("TERM", "") == "linux":
            return "a text console, no graphical session"
        if env.get("SSH_CONNECTION") or env.get("SSH_TTY"):
            return "a terminal over SSH, no graphical session"
        return "no graphical session"
    if not desk:
        return f"an unknown desktop ({kind})"
    return f"{_DESKTOP_NAMES.get(desk, desk)} ({kind})"


# ── the ready-made needs ─────────────────────────────────────────────────────

def sway_session(why: str, instead: str = "", *, optional: bool = False,
                 environ: Mapping[str, str] | None = None, swaymsg: str = "swaymsg",
                 timeout: float = 3.0) -> Need:
    """Sway is running and answering: ``SWAYSOCK`` is set and ``swaymsg`` replies."""
    def check() -> tuple[bool, str]:
        env = os.environ if environ is None else environ
        sock = env.get("SWAYSOCK", "")
        if not sock:
            here = describe_session(env)
            if here.startswith("Sway "):
                # inside Sway, but started without its environment (a service, a bare tty)
                return False, "a Sway desktop, but no way to reach it (SWAYSOCK isn't set)"
            return False, here
        exe = shutil.which(swaymsg) if not os.path.sep in swaymsg else swaymsg
        if not exe:
            return False, f"a Sway socket, but no `{swaymsg}` program to talk to it"
        try:
            r = subprocess.run([exe, "-t", "get_version"], capture_output=True, text=True,
                               timeout=timeout, env={**os.environ, "SWAYSOCK": sock})
        except (OSError, subprocess.TimeoutExpired):
            return False, "a Sway socket that doesn't answer"
        if r.returncode != 0:
            return False, "a Sway socket that doesn't answer"
        return True, "a Sway session"
    return Need("a Sway session", check, why, instead, optional)


_VERSION_RE = re.compile(r"(\d+)\.(\d+)(?:\.(\d+))?")


def parse_version(text: str) -> tuple[int, ...] | None:
    """The first X.Y[.Z] in ``text`` as a tuple, or None."""
    m = _VERSION_RE.search(text)
    if not m:
        return None
    return tuple(int(g) for g in m.groups() if g is not None)


def program(name: str, why: str, instead: str = "", *, min_version: str | None = None,
            version_args: Sequence[str] = ("--version",), optional: bool = False,
            path: str | None = None, timeout: float = 5.0) -> Need:
    """``name`` is installed (``path`` to test a specific file), and at least
    ``min_version`` when one is given (read from ``<name> --version``)."""
    what = f"{name} {min_version} or newer" if min_version else name

    def check() -> tuple[bool, str]:
        exe = path or shutil.which(name)
        if not exe or not os.path.exists(exe):
            return False, f"{name} is not installed"
        if not min_version:
            return True, f"{name} is installed"
        try:
            r = subprocess.run([exe, *version_args], capture_output=True, text=True, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired):
            return False, f"{name} is installed, but its version could not be read"
        have = parse_version(r.stdout + r.stderr)
        if have is None:
            return False, f"{name} is installed, but its version could not be read"
        want = parse_version(min_version) or ()
        words = f"{name} {'.'.join(map(str, have))}"
        if _pad(have) < _pad(want):
            return False, f"{words}, older than {min_version}"
        return True, words
    return Need(what, check, why, instead, optional)


def _pad(v: tuple[int, ...], n: int = 3) -> tuple[int, ...]:
    return tuple(v) + (0,) * (n - len(v))


def service(unit: str, why: str, instead: str = "", *, user: bool = False,
            optional: bool = False, systemctl: str = "systemctl", timeout: float = 5.0) -> Need:
    """The systemd unit ``unit`` is active (``user=True`` for a user service)."""
    label = f"the {unit} service" + (" (user)" if user else "")

    def check() -> tuple[bool, str]:
        exe = shutil.which(systemctl) if not os.path.sep in systemctl else systemctl
        if not exe:
            return False, "no systemd here, so no services to ask"
        cmd = [exe] + (["--user"] if user else []) + ["is-active", unit]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired):
            return False, f"{unit}: systemd did not answer"
        state = (r.stdout.strip().splitlines() or ["unknown"])[0]
        return state == "active", f"{unit} is {state}"
    return Need(label, check, why, instead, optional)


def a_file(path: str | os.PathLike, why: str, instead: str = "", *, optional: bool = False,
           what: str | None = None) -> Need:
    """A file (or folder) exists."""
    p = Path(os.path.expanduser(str(path)))

    def check() -> tuple[bool, str]:
        if p.exists():
            return True, f"{_tilde(p)} is there"
        return False, f"there is no {_tilde(p)}"
    return Need(what or f"the file {_tilde(p)}", check, why, instead, optional)


def _tilde(p: Path) -> str:
    home = str(Path.home())
    s = str(p)
    return "~" + s[len(home):] if s.startswith(home) else s


# ── the words, for the screen and for the terminal ───────────────────────────

def heading_for(app_name: str, miss: Sequence[Finding]) -> str:
    if all(f.need.optional for f in miss):
        return f"{app_name} can run here, with something missing"
    if len(miss) == 1:
        return f"{app_name} can't run here: it needs {miss[0].need.what}"
    return f"{app_name} can't run here: {len(miss)} things it needs are missing"


def lines_for(f: Finding) -> list[str]:
    """The four facts about one missing need, in order."""
    out = [f"Needs:   {f.need.what}" + (" (optional)" if f.need.optional else ""),
           f"Found:   {f.found}",
           f"Why:     {f.need.why}"]
    if f.need.instead:
        out.append(f"Instead: {f.need.instead}")
    return out


def needs_text(app_name: str, miss: Sequence[Finding], *, decision: str = "closed") -> str:
    """The terminal record: the same words as the screen, as a closing notice."""
    from .closing import closing_notice
    lines: list[str] = []
    for i, f in enumerate(miss):
        if i:
            lines.append("")
        lines += lines_for(f)
    level = "warn" if all(f.need.optional for f in miss) else "error"
    tail = {"closed": "Nothing was changed.", "continue": "Continuing anyway (your choice)."}[decision]
    return closing_notice(heading_for(app_name, miss), [*lines, "", tail], level=level)


# ── the screen ───────────────────────────────────────────────────────────────

def _needs_app_class():
    # imported lazily: the check itself must work without a terminal
    from textual.app import ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical, VerticalScroll
    from textual.widgets import Button, Static
    from rich.markup import escape

    from .app import ForgeApp
    from .widgets import Notice

    class NeedsApp(ForgeApp):
        """One plain screen: what is missing, what was found instead, why, and
        what to use. **Close (c)**, or **Continue anyway (a)** when everything
        missing is optional. Returns "close" or "continue"."""

        CSS = ForgeApp.CSS + """
        #needs-body { height: 1fr; padding: 1 2; }
        #needs-head { text-style: bold; color: $forge-accent; margin: 0 0 1 0; }
        #needs-body Notice { margin: 0 0 1 0; }
        #needs-foot { height: 2; padding: 0 2; border-top: solid $forge-border; }
        """
        BINDINGS = ForgeApp.BINDINGS + [
            Binding("escape", "act('quit')", show=False, priority=True),
            Binding("c", "act('quit')", show=False),
            Binding("q", "act('quit')", show=False),
            Binding("a", "continue_anyway", show=False),
        ]

        def __init__(self, app_name: str, miss: Sequence[Finding], **kw) -> None:
            self.app_name, self.miss = app_name, list(miss)
            self.can_continue = all(f.need.optional for f in self.miss)
            self.APP_NAME = f"{app_name} · start-up check"
            self.MENU = [{"id": "needs", "title": "What's missing", "kind": "section"},
                         {"id": "quit", "title": "Close", "kind": "action", "action": "quit"}]
            super().__init__(**kw)

        def compose_sections(self) -> ComposeResult:
            with Vertical(id="sec-needs"):
                with VerticalScroll(id="needs-body"):
                    yield Static(escape(heading_for(self.app_name, self.miss)), id="needs-head")
                    for i, f in enumerate(self.miss):
                        level = "warn" if f.need.optional else "error"
                        yield Notice(f"Needs {f.need.what}", [escape(l) for l in lines_for(f)[1:]],
                                     level=level, id=f"need-{i}")
                    yield Static(escape("Nothing has been changed." if not self.can_continue else
                                        "You can continue without it, or close."), id="needs-tail")
                with Horizontal(id="needs-foot", classes="forge-buttons"):
                    if self.can_continue:
                        yield Button("Continue Anyway (a)", id="needs-continue")
                    yield Button("Close (c)", id="needs-close", variant="primary")

        def on_mount(self) -> None:
            super().on_mount()
            self.query_one("#needs-close", Button).focus()

        def on_button_pressed(self, e: Button.Pressed) -> None:
            if e.button.id == "needs-continue":
                self.action_continue_anyway()
            elif e.button.id == "needs-close":
                self.exit("close")

        def action_continue_anyway(self) -> None:
            if self.can_continue:
                self.exit("continue")

        def before_quit(self) -> bool:
            self.exit("close")
            return False

    return NeedsApp


def NeedsApp(app_name: str, miss: Sequence[Finding], **kw):
    """The start-up screen as an app (``.run()`` returns "close" or "continue")."""
    return _needs_app_class()(app_name, miss, **kw)


def start_check(app_name: str, needs: Sequence[Need], *, console: bool | None = None,
                ask: Callable[[str, Sequence[Finding]], str | None] | None = None,
                out=None) -> bool:
    """Check ``needs``; when something is missing, show the screen and print the
    record. True = the app may go on. ``ask`` replaces the screen (tests)."""
    import sys
    miss = missing(check_needs(needs))
    if not miss:
        return True
    if ask is None:
        def ask(name: str, m: Sequence[Finding]) -> str | None:
            return NeedsApp(name, m, console=console).run()
    choice = ask(app_name, miss)
    decision = "continue" if (choice == "continue" and all(f.need.optional for f in miss)) else "closed"
    print(needs_text(app_name, miss, decision=decision), file=out or sys.stdout)
    return decision == "continue"
