"""Reusable floating dialogs.

* ``ConfirmDialog`` — small yes/no, stacks over anything, returns bool.
* ``ForgePanelScreen`` — the standard scrolling panel (title + body + a Close
  button that scrolls with the content). Base for read-only info windows.
* ``ShortcutsDialog`` / ``LicenseDialog`` / ``AboutDialog`` — Help windows.

Apps build their own editors on ``.forge-panel`` styling + ``ConfirmDialog``
(see ``examples/demo.py``'s ``EditDialog``).
"""

from __future__ import annotations

from typing import TypeVar

from textual.app import ComposeResult

from .console import is_console
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static


ResultType = TypeVar("ResultType")


class ForgeModal(ModalScreen[ResultType]):
    """Base for app-built floating dialogs (editors, pickers, wizards).

    Carries the standard Forge modal treatment — centered on screen with the
    dimmed backdrop — so app dialogs match the kit's own windows. Subclass it
    (optionally parameterized: ``ForgeModal[dict | None]``) and compose a
    ``.forge-panel`` Vertical inside, as in ``examples/demo.py``.
    """


class ConfirmDialog(ModalScreen[bool]):
    BINDINGS = [
        Binding("escape", "no", "", show=False),
        Binding("y", "yes", "", show=False),
        Binding("n", "no", "", show=False),
    ]

    def __init__(self, message: str, confirm_label: str = "Confirm",
                 danger: bool = False, default_no: bool = False) -> None:
        super().__init__()
        self._message, self._confirm_label, self._danger = message, confirm_label, danger
        # v0.5.0: for risky steps (restore, delete) Enter means Cancel until
        # the person moves to the other button themselves
        self._default_no = default_no

    def on_mount(self) -> None:
        if self._default_no:
            self.query_one("#cancel", Button).focus()

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-confirm"):
            yield Static(self._message, classes="forge-confirm-msg")
            with Horizontal(classes="forge-buttons"):
                yield Button(self._confirm_label, id="ok",
                             variant="error" if self._danger else "primary")
                yield Button("Cancel (n)", id="cancel")

    def on_button_pressed(self, e: Button.Pressed) -> None:
        self.dismiss(e.button.id == "ok")

    def action_yes(self) -> None: self.dismiss(True)
    def action_no(self) -> None: self.dismiss(False)


class ForgePanelScreen(ModalScreen[None]):
    """A read-only panel: fixed title, scrolling body, fixed button footer.

    F-8 anatomy (field ruling, 2026-08-09): only the body scrolls; the
    button bar sits under a divider border and is ALWAYS visible, no
    matter how long the content grows. Override ``compose_footer`` to
    supply different buttons.
    """

    BINDINGS = [Binding("escape", "close", "", show=False)]
    panel_title = "forgekit"

    # Extra keys that close the panel (kit finding #5: app-level character
    # bindings don't reach through a modal, so apps declare them here
    # instead of subclassing with Binding machinery). Textual key names,
    # e.g. CLOSE_KEYS = ("question_mark", "q").
    CLOSE_KEYS: tuple[str, ...] = ()

    def on_key(self, event) -> None:
        if event.key in self.CLOSE_KEYS:
            event.stop()
            self.dismiss()

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel"):
            yield Static(self.panel_title, classes="forge-panel-title")
            with VerticalScroll(classes="forge-panel-body"):
                yield from self.compose_body()
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield from self.compose_footer()

    def compose_body(self) -> ComposeResult:
        yield from ()

    def compose_footer(self) -> ComposeResult:
        yield Button("Close (Esc)", id="forge-close", variant="primary")

    def on_button_pressed(self, e: Button.Pressed) -> None:
        self.dismiss()

    def action_close(self) -> None:
        self.dismiss()


class ShortcutsDialog(ForgePanelScreen):
    panel_title = "Keyboard shortcuts"

    def __init__(self, shortcuts: list[tuple[str, str]]) -> None:
        super().__init__()
        self._shortcuts = shortcuts

    def compose_body(self) -> ComposeResult:
        # F-6: key column sizes to the longest key, so multi-key labels
        # ("Ctrl+D or 1") keep the descriptions aligned.
        width = max((len(k) for k, _ in self._shortcuts), default=8)
        for key, desc in self._shortcuts:
            yield Static(f"[$forge-accent b]{key:<{width}}[/]  {desc}")


def license_body(notice: str) -> ComposeResult:
    yield Static(notice)


def about_body(a: dict) -> ComposeResult:
    """The About text: name and version, tagline, description, authors, license, links."""
    yield Static(f"[b $forge-title-accent]{a['name']}[/]   [$forge-muted]v{a['version']}[/]")
    if a.get("tagline"):
        # italic reads as green on a text console, so plain there
        yield Static(f"[{'' if is_console() else 'i '}$forge-muted]{a['tagline']}[/]")
    if a.get("description"):
        yield Static(f"\n{a['description']}\n")
    if a.get("authors"):
        yield Static(f"[$forge-accent b]Authors[/]   {a['authors']}")
    if a.get("license"):
        yield Static(f"[$forge-accent b]License[/]   {a['license']}")
    if a.get("links"):
        yield Static("\n[$forge-accent b]Links[/]")
        for label, url in a["links"]:
            yield Static(f"  {label}:  [u $forge-accent]{url}[/]")


class LicenseDialog(ForgePanelScreen):
    def __init__(self, license_name: str, notice: str) -> None:
        super().__init__()
        self.panel_title = f"License — {license_name}"
        self._notice = notice

    def compose_body(self) -> ComposeResult:
        yield from license_body(self._notice)


class AboutDialog(ForgePanelScreen):
    def __init__(self, about: dict) -> None:
        super().__init__()
        self.panel_title = f"About {about['name']}"
        self._a = about

    def compose_body(self) -> ComposeResult:
        yield from about_body(self._a)


class _PageView(VerticalScroll):
    """0.10.0 (Javier, 2026-10-08): About and License open in the content area, not in a window.
    Esc goes back to the page you came from."""

    BINDINGS = [Binding("escape", "back", "", show=False)]
    FORGE_HINTS = [("Esc", "back")]
    # not focusable until shown: at start Textual focuses the first focusable widget, hidden or
    # not, and a hidden page holding the focus would silence the app's letter keys
    can_focus = False
    DEFAULT_CSS = "_PageView { padding: 1 3; } _PageView > .forge-page-title { margin: 0 0 1 0; color: $forge-accent; text-style: bold; }"

    def on_key(self, event) -> None:
        quiet_letters(event)

    def action_back(self) -> None:
        back = getattr(self.app, "action_back_from_page", None)
        if back:
            back()


def quiet_letters(event) -> None:
    """On a reading page (About, License, Keys, the manual) an app's one-letter keys must not fire:
    S would save, C start a clean-up (found by the nogForge 1.4.0 build). A plain letter stops
    here, before it reaches the app; numbers, Ctrl + letter, ?, Esc and F-keys still pass."""
    ch = event.character or ""
    if len(ch) == 1 and ch.isalpha() and not event.key.startswith("ctrl+"):
        event.stop()


class AboutView(_PageView):
    def __init__(self, about: dict, **kw) -> None:
        super().__init__(**kw)
        self._a = about

    def compose(self) -> ComposeResult:
        yield Static(f"About {self._a.get('name', '')}", classes="forge-page-title")
        yield from about_body(self._a)


class LicenseView(_PageView):
    def __init__(self, license_name: str, notice: str, **kw) -> None:
        super().__init__(**kw)
        self._name, self._notice = license_name, notice

    def compose(self) -> ComposeResult:
        yield Static(f"License — {self._name}", classes="forge-page-title")
        yield from license_body(self._notice)


class ShortcutsView(_PageView):
    """The Keys list as a page in the work area (0.10.0, Javier 2026-10-08)."""

    def __init__(self, shortcuts: list[tuple[str, str]], **kw) -> None:
        super().__init__(**kw)
        self._shortcuts = shortcuts

    def compose(self) -> ComposeResult:
        yield Static("Keys", classes="forge-page-title")
        width = max((len(k) for k, _ in self._shortcuts), default=8)
        for key, desc in self._shortcuts:
            yield Static(f"[$forge-accent b]{key:<{width}}[/]  {desc}")
