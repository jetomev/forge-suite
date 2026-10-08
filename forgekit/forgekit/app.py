"""``ForgeApp`` — the base application shell.

A Forge app subclasses this and supplies:

    APP_NAME, MENU, SHORTCUTS, ABOUT, LICENSE_NAME, LICENSE_NOTICE   (class attrs)
    CSS = FORGE_CSS + "…your section styles…"
    def compose_sections(self):     # yield section widgets, ids "sec-<id>"
    def on_action(self, action_id): # handle your submenu actions (add/edit/…)
    # optional: on_section_shown(id), plus BINDINGS for section accelerators

The base provides: the title + menu bar, the content switcher, dropdown
dispatch, section switching + active highlight, and the Help windows
(Shortcuts / License / About). Menu-bar order convention: main options, then
Help (id ``help``), then Quit (id ``quit``).

Console mode (issue #1): on a plain text console (``TERM=linux``, or forced with
``FORGE_ASCII=1``) the same app switches to the console colour roles, Textual's
16-colour theme, whole-cell scrollbars and a filter that swaps every character
the console font lacks. ``self.forge_console`` tells the app which mode it runs in.

v0.5.0, all opt-in so existing apps look the same:

    SHOW_HINT_BAR = True      # bottom row: the keys for what has focus
                              #   (widgets declare FORGE_HINTS; else app HINTS)
    SHOW_CHANGES_BAR = True   # row above it: unsaved work + finishing buttons
                              #   (self.changes_bar.show(...) / .hide())
    set_title_status("…")     # muted text at the right end of the title bar
    def before_quit(self) -> bool:  # False = not now (e.g. ask first, then exit)
"""

from __future__ import annotations

import signal
import sys

from collections.abc import Sequence

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.filter import LineFilter
from textual.scrollbar import ScrollBar, ScrollBarRender
from textual.widgets import ContentSwitcher, Static

from .console import ConsoleGlyphFilter, ConsoleScrollBarRender, console_mode, set_console
from .dialogs import AboutDialog, LicenseDialog, ShortcutsDialog
from .menu import MenuBar, MenuDropdown, accel
from .theme import FORGE_CSS, css_variables
from .widgets import ChangesBar, HintBar, hints_for


# 0.10.0: a hint whose key is MENU_HINT[0] shows as "1-N", N = the numbered menu entries
MENU_HINT = ("{menu}", "menu")

HYPEFORGE_FLAG = "--hypeforge"


def hypeforge_mode(argv: Sequence[str] | None = None) -> bool:
    """True when the app was started with ``--hypeforge`` (any case: ``--hypeForge`` too).

    hypeForge Settings starts every Forge app this way (0.10.0): the app is one page
    of a bigger window, so it has no Quit of its own — Settings closes it."""
    args = sys.argv[1:] if argv is None else argv
    return any(a.lower() == HYPEFORGE_FLAG for a in args)


def add_hypeforge_argument(parser) -> None:
    """Teach an app's argparse parser ``--hypeforge`` (and ``--hypeForge``), kept out of
    ``--help``: it is for hypeForge Settings, not for people."""
    import argparse
    parser.add_argument("--hypeforge", "--hypeForge", dest="hypeforge", action="store_true",
                        help=argparse.SUPPRESS)


def menu_key_clashes(menu: list[dict]) -> list[tuple[str, str, str]]:
    """Entries whose underlined letter is already taken by an earlier one:
    (letter, first entry id, clashing entry id). Each underlined letter is a
    Ctrl shortcut (0.10.0), so a clash means a dead key; apps test for none."""
    seen: dict[str, str] = {}
    out = []
    for m in menu:
        a = accel(m)
        if a in seen:
            out.append((a, seen[a], m["id"]))
        else:
            seen[a] = m["id"]
    return out


class TitleText(Static):
    """The title row: the app's name centred, an optional muted status at the
    right edge (dropped when the row is too narrow for both)."""

    def __init__(self, title: str, **kw) -> None:
        super().__init__(title, **kw)
        self._title, self._status = title, ""

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, text: str) -> None:
        self._status = text
        self.refresh()

    def render(self):
        w = self.size.width
        if not self._status or w <= 0:
            return self._title
        left = max(0, (w - len(self._title)) // 2)
        right_start = w - len(self._status) - 1
        if right_start <= left + len(self._title) + 2:
            # no room beside a centred title: title at the left, status right
            left = 1
            if right_start <= left + len(self._title) + 2:
                return self._title
        gap = right_start - left - len(self._title)
        from rich.markup import escape
        return (" " * left + escape(self._title) + " " * gap
                + f"[not bold $forge-muted]{escape(self._status)}[/] ")


class ForgeApp(App[None]):
    # ── to be overridden by the app ──────────────────────────────────────────
    APP_NAME: str = "ForgeApp"
    MENU: list[dict] = []
    SHORTCUTS: list[tuple[str, str]] = []
    ABOUT: dict = {}
    LICENSE_NAME: str = "GPL-3.0-or-later"
    LICENSE_NOTICE: str = ""
    SHOW_HINT_BAR: bool = False
    SHOW_CHANGES_BAR: bool = False
    HINTS: list[tuple[str, str]] = []
    # 0.10.0 (Javier, 2026-10-08): every menu entry gets Ctrl+<its underlined letter>
    # and a number, 1 to N in bar order, Help included, Quit not. False = the app binds its own
    MENU_KEYS: bool = True

    CSS = FORGE_CSS

    # Universal accelerators (apps add their own section bindings). Help lives
    # on Ctrl+H, Quit on Ctrl+Q by convention. F1 opens Help too (F-10): a text
    # console sends Ctrl+H as the Backspace byte, so there Ctrl+H never arrives.
    BINDINGS = [
        Binding("ctrl+h", "activate('help')", show=False, priority=True),
        Binding("f1", "activate('help')", show=False, priority=True),
        Binding("ctrl+q", "activate('quit')", show=False, priority=True),
    ]

    def __init__(self, *args, console: bool | None = None, hypeforge: bool | None = None,
                 **kwargs) -> None:
        # console: None = decide from the environment (TERM / FORGE_ASCII)
        # (not "self.console": Textual's App already uses that name for its
        # Rich console, and would overwrite the flag)
        self.forge_console = console_mode() if console is None else console
        set_console(self.forge_console)
        # set either way: the renderer is one class-wide setting
        ScrollBar.renderer = ConsoleScrollBarRender if self.forge_console else ScrollBarRender
        if self.forge_console:
            kwargs.setdefault("ansi_color", True)
        super().__init__(*args, **kwargs)
        if self.forge_console:
            self.theme = "ansi-dark"
        self._glyph_filter = ConsoleGlyphFilter()
        self.title = self.APP_NAME
        # 0.10.0 (Javier, 2026-10-08): started with --hypeforge, the app is one page of
        # hypeForge Settings. No Quit in the bar, and every way to quit (Q, Ctrl+Q, the
        # Quit entry) does nothing: Settings closes it, asking first through SIGUSR1
        self.hypeforge = hypeforge_mode() if hypeforge is None else hypeforge
        if self.hypeforge:
            self.MENU = [m for m in self.MENU if m.get("id") != "quit"]
        self._by_id = {m["id"]: m for m in self.MENU}
        self._title_status = ""
        self._menu_count = 0
        if self.MENU_KEYS:
            self._bind_menu_keys()

    def _bind_menu_keys(self) -> None:
        """Ctrl+<underlined letter> (priority: it works from any field, like Ctrl+H always
        did) and 1-9 (not priority: a field that takes digits keeps them) for each entry."""
        taken: set[str] = {"h", "q"}            # the class bindings: Help and Quit
        n = 0
        for m in self.MENU:
            if m["id"] == "quit":
                continue
            letter = accel(m)
            if letter.isalpha() and letter not in taken:
                self._bindings.bind(f"ctrl+{letter}", f"activate('{m['id']}')", show=False, priority=True)
            taken.add(letter)
            n += 1
            if n <= 9:
                self._bindings.bind(str(n), f"activate('{m['id']}')", show=False)
        self._menu_count = min(n, 9)

    # ── v0.6.0: a tool's run and its password, inside the app ────────────────
    PASSWORD_TITLE: str = "Password"

    async def password_bridge(self):
        """The app's ``PasswordBridge``: started once, the first time it's needed."""
        from .askpass import PasswordBridge, PasswordDialog
        if getattr(self, "_forge_bridge", None) is None:
            import asyncio

            async def ask(prompt: str, attempt: int) -> str | None:
                fut = asyncio.get_running_loop().create_future()
                self.push_screen(PasswordDialog(prompt, attempt, self.PASSWORD_TITLE),
                                 callback=lambda v: fut.done() or fut.set_result(v))
                return await fut
            self._forge_bridge = PasswordBridge(ask)
            await self._forge_bridge.start()
        return self._forge_bridge

    async def run_in_app(self, title: str, cmd, env: dict | None = None, *, callback=None, **window) -> None:
        """Run ``cmd`` in a ``RunWindow`` over the app, sudo's password asked in
        the app; ``callback(status)`` when the window closes."""
        import os
        from .run import RunWindow
        bridge = await self.password_bridge()
        e = dict(env if env is not None else os.environ)
        e.update(bridge.env())
        self.push_screen(RunWindow(title, cmd, e, **window), callback=callback)

    def polkit_agent(self):
        """Make this app polkit's password asker for its own process (pkexec
        then asks in the app's own box, desktop or text console). Started once;
        returns the agent (``.active`` False and ``.reason`` if it could not)."""
        if getattr(self, "_forge_polkit", None) is None:
            import asyncio
            import getpass
            from .askpass import PasswordDialog
            from .polkit_agent import InAppPolkitAgent
            who = getpass.getuser()

            async def ask(message: str, attempt: int) -> str | None:
                fut = asyncio.get_running_loop().create_future()
                words = f"{message.rstrip('.')}.\nYour password ({who})."
                self.push_screen(PasswordDialog("", attempt, self.PASSWORD_TITLE, words=words),
                                 callback=lambda v: fut.done() or fut.set_result(v))
                return await fut
            self._forge_polkit = InAppPolkitAgent(ask, self.call_from_thread)
            self._forge_polkit.start()
        return self._forge_polkit

    async def on_unmount(self) -> None:
        if self.hypeforge:
            try:
                import asyncio
                asyncio.get_running_loop().remove_signal_handler(signal.SIGUSR1)
            except (NotImplementedError, RuntimeError, ValueError):
                pass
        agent = getattr(self, "_forge_polkit", None)
        if agent is not None:
            agent.stop()
        bridge = getattr(self, "_forge_bridge", None)
        if bridge is not None:
            await bridge.close()

    # ── console mode (issue #1) ──────────────────────────────────────────────
    def get_css_variables(self) -> dict[str, str]:
        console = getattr(self, "forge_console", False)
        return {**super().get_css_variables(), **css_variables(console)}

    def get_line_filters(self) -> Sequence[LineFilter]:
        filters = list(super().get_line_filters())
        if getattr(self, "forge_console", False):
            filters.append(self._glyph_filter)
        return filters

    # ── shell composition ────────────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        with Vertical(id="forge-header"):
            yield TitleText(self.APP_NAME, id="forge-title")
            yield MenuBar(self.MENU)
        with ContentSwitcher(initial=f"sec-{self._first_section()}", id="forge-work"):
            yield from self.compose_sections()
        # after the work area, so Tab reaches the screen's own fields first and
        # the bar's buttons last (it is docked to the bottom either way)
        if self.SHOW_HINT_BAR or self.SHOW_CHANGES_BAR:
            with Vertical(id="forge-footer"):
                if self.SHOW_CHANGES_BAR:
                    yield ChangesBar()
                if self.SHOW_HINT_BAR:
                    yield HintBar()

    def compose_sections(self) -> ComposeResult:
        yield from ()

    def on_mount(self) -> None:
        self._mark_active(self._first_section())
        self.refresh_hints()
        if self.hypeforge:
            try:
                import asyncio
                asyncio.get_running_loop().add_signal_handler(signal.SIGUSR1, self.host_quit)
            except (NotImplementedError, RuntimeError, ValueError):   # not the main thread / no signals
                pass

    def host_quit(self) -> None:
        """hypeForge Settings asks the app to close (SIGUSR1 under --hypeforge). The
        app's own check runs, exactly as its Quit would: nothing unsaved closes at once;
        otherwise the app asks, and closes on that answer (or stays, and Settings with it)."""
        top = self.screen
        if isinstance(top, MenuDropdown):
            top.dismiss(None)
        if self.before_quit():
            self.exit()

    # ── v0.5.0: title status, hint bar, changes bar ──────────────────────────
    def set_title_status(self, text: str) -> None:
        """Muted text at the right end of the title bar ("" to clear)."""
        self._title_status = text
        self.query_one("#forge-title", TitleText).status = text

    @property
    def changes_bar(self) -> ChangesBar:
        return self.query_one(ChangesBar)

    def refresh_hints(self) -> None:
        """Show the keys for whatever has focus on the main screen."""
        if not self.SHOW_HINT_BAR:
            return
        try:
            bar = self.query_one(HintBar)
        except Exception:
            return
        if self.screen is not bar.screen:
            return
        # v0.5.2 (Javier, nogForge 3 Oct): the keys follow the SECTION on show.
        # Switching to a section with nothing focusable left focus in the one
        # just hidden, and the bar kept that section's keys.
        widget = self.screen.focused
        try:
            shown = self.query_one("#forge-work", ContentSwitcher).visible_content
        except Exception:
            shown = None
        if shown is not None and (widget is None or shown not in widget.ancestors_with_self):
            widget = shown
        hints = hints_for(widget, self.HINTS)
        bar.set_hints([(f"1-{self._menu_count}" if k == MENU_HINT[0] else k, d) for k, d in hints])

    def on_descendant_focus(self, event) -> None:
        self.refresh_hints()

    def before_quit(self) -> bool:
        """Hook: return False to stay (and, for example, ask first, then call
        ``self.exit()`` yourself)."""
        return True

    def _first_section(self) -> str:
        for m in self.MENU:
            if m["kind"] == "section":
                return m["id"]
        return ""

    # ── menu dispatch ────────────────────────────────────────────────────────
    def on_click(self, event) -> None:
        w = event.widget
        if w is not None and w.id and w.id.startswith("menu-"):
            self.action_activate(w.id.removeprefix("menu-"))

    def action_activate(self, entry_id: str) -> None:
        if entry_id not in self._by_id:              # e.g. Quit under --hypeforge: nothing
            return
        entry = self._by_id[entry_id]
        kind = entry["kind"]
        # 0.10.0 (#47): one dropdown at a time. The accelerators are priority bindings, so
        # they reach here while a dropdown is open; it closes first, and the same menu's
        # key pressed again stops there (a toggle) instead of stacking a second one
        top = self.screen
        if isinstance(top, MenuDropdown):
            top.dismiss(None)
            if kind == "menu" and top.menu_id == entry_id:
                return
        if kind == "section":
            self._switch_section(entry_id)
        elif kind == "action":
            self.action_act(entry["action"])
        elif kind == "menu":
            w = self.query_one(f"#menu-{entry_id}")
            self.push_screen(MenuDropdown(entry["items"], w.region.x, w.region.y + 1, entry_id),
                             self._on_menu_choice)

    def _switch_section(self, section_id: str) -> None:
        self.query_one("#forge-work", ContentSwitcher).current = f"sec-{section_id}"
        self._mark_active(section_id)
        self.on_section_shown(section_id)
        self.refresh_hints()
        self.call_after_refresh(self.refresh_hints)   # again once the section has set its focus

    def on_section_shown(self, section_id: str) -> None:
        """Hook: called after a section becomes visible."""

    def _mark_active(self, section_id: str) -> None:
        for m in self.MENU:
            self.query_one(f"#menu-{m['id']}").set_class(m["id"] == section_id, "active")

    def _on_menu_choice(self, action_id: str | None) -> None:
        if action_id:
            self.action_act(action_id)

    def action_act(self, action_id: str) -> None:
        if action_id == "quit":
            if self.hypeforge:                       # Settings closes it (host_quit)
                return
            if self.before_quit():
                self.exit()
        elif action_id == "shortcuts":
            self.push_screen(ShortcutsDialog(self.SHORTCUTS))
        elif action_id == "license":
            self.push_screen(LicenseDialog(self.LICENSE_NAME, self.LICENSE_NOTICE))
        elif action_id == "about":
            self.push_screen(AboutDialog(self.ABOUT))
        else:
            self.on_action(action_id)

    def on_action(self, action_id: str) -> None:
        """Hook: handle the app's own submenu action ids."""
