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

from collections.abc import Sequence

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.filter import LineFilter
from textual.scrollbar import ScrollBar, ScrollBarRender
from textual.widgets import ContentSwitcher, Static

from .console import ConsoleGlyphFilter, ConsoleScrollBarRender, console_mode, set_console
from .dialogs import AboutDialog, LicenseDialog, ShortcutsDialog
from .menu import MenuBar, MenuDropdown
from .theme import FORGE_CSS, css_variables
from .widgets import ChangesBar, HintBar, hints_for


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

    CSS = FORGE_CSS

    # Universal accelerators (apps add their own section bindings). Help lives
    # on Ctrl+H, Quit on Ctrl+Q by convention. F1 opens Help too (F-10): a text
    # console sends Ctrl+H as the Backspace byte, so there Ctrl+H never arrives.
    BINDINGS = [
        Binding("ctrl+h", "activate('help')", show=False, priority=True),
        Binding("f1", "activate('help')", show=False, priority=True),
        Binding("ctrl+q", "activate('quit')", show=False, priority=True),
    ]

    def __init__(self, *args, console: bool | None = None, **kwargs) -> None:
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
        self._by_id = {m["id"]: m for m in self.MENU}
        self._title_status = ""

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
        bar.set_hints(hints_for(self.screen.focused, self.HINTS))

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
        entry = self._by_id[entry_id]
        kind = entry["kind"]
        if kind == "section":
            self._switch_section(entry_id)
        elif kind == "action":
            self.action_act(entry["action"])
        elif kind == "menu":
            w = self.query_one(f"#menu-{entry_id}")
            self.push_screen(MenuDropdown(entry["items"], w.region.x, w.region.y + 1),
                             self._on_menu_choice)

    def _switch_section(self, section_id: str) -> None:
        self.query_one("#forge-work", ContentSwitcher).current = f"sec-{section_id}"
        self._mark_active(section_id)
        self.on_section_shown(section_id)
        self.refresh_hints()

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
