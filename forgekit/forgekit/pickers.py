"""``FilterPicker`` — the long-list answer (v0.5.0, promoted from alacrittyForge).

A list that opens where a value is chosen: type to filter, arrows to move,
Enter to pick, Esc to leave unchanged. The current value is marked and
highlighted when the window opens. Optionally the typed text can be taken as a
value of its own ("Use 'nvidia' as typed"), for lists that are suggestions
rather than the only choices.

Options are ``value`` strings or ``(value, label)`` pairs; the label is what a
person reads, the value is what comes back. Returns the value, or ``None``.
"""

from __future__ import annotations

from collections.abc import Sequence

from rich.markup import escape
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, OptionList, Static
from textual.widgets.option_list import Option

from .console import glyph
from .dialogs import ForgeModal

_CUSTOM = "\x00custom"


class FilterPicker(ForgeModal[str | None]):
    BINDINGS = [Binding("escape", "cancel", "", show=False)]

    def __init__(self, title: str, options: Sequence[str | tuple[str, str]], current: str = "",
                 *, allow_custom: bool = False, hint: str = "") -> None:
        super().__init__()
        self._title, self._current, self._allow_custom, self._hint = title, current, allow_custom, hint
        self._options: list[tuple[str, str]] = [
            (o, o) if isinstance(o, str) else (o[0], o[1]) for o in options
        ]
        self._typed = ""

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel forge-picker"):
            yield Static(self._title, classes="forge-panel-title")
            if self._hint:
                yield Static(f"[$forge-muted]{escape(self._hint)}[/]", classes="forge-picker-hint")
            # select_on_focus off: typing on the list moves focus here, and a
            # selected first letter was replaced by the second
            yield Input(placeholder="Type to filter…", id="picker-filter", select_on_focus=False)
            yield Static("", id="picker-count")
            yield OptionList(id="picker-list")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Choose (Enter)", id="pick", variant="primary")
                yield Button("Cancel (Esc)", id="cancel")

    def on_mount(self) -> None:
        self._refill("")
        self.query_one("#picker-list", OptionList).focus()

    def matches(self, needle: str) -> list[tuple[str, str]]:
        n = needle.lower().strip()
        return [(v, l) for v, l in self._options if n in l.lower() or n in v.lower()]

    def _refill(self, needle: str) -> None:
        self._typed = needle.strip()
        ol = self.query_one("#picker-list", OptionList)
        ol.clear_options()
        shown = self.matches(needle)
        start = 0
        for i, (value, label) in enumerate(shown):
            mark = f"[$forge-ok]{glyph('ok')}[/] " if value == self._current else "  "
            ol.add_option(Option(f"{mark}{escape(label)}", id=value))
            if value == self._current:
                start = i
        if self._allow_custom and self._typed and all(self._typed != v for v, _ in shown):
            ol.add_option(Option(f"  [$forge-accent]Use \"{escape(self._typed)}\" as typed[/]", id=_CUSTOM))
        total = len(self._options)
        count = f"{len(shown)} of {total}" if needle.strip() else f"{total} choices"
        self.query_one("#picker-count", Static).update(f"[$forge-muted]{count}[/]")
        if ol.option_count:
            ol.highlighted = start if not needle.strip() else 0

    def on_key(self, event) -> None:
        # typing on the list goes to the filter, so "type to filter" works
        # wherever focus is
        flt = self.query_one("#picker-filter", Input)
        if not flt.has_focus and event.character and event.character.isprintable() and len(event.character) == 1:
            flt.focus()
            flt.insert_text_at_cursor(event.character)
            event.stop()

    def on_input_changed(self, e: Input.Changed) -> None:
        if e.input.id == "picker-filter":
            self._refill(e.value)

    def on_input_submitted(self, e: Input.Submitted) -> None:
        self._pick_highlighted()

    def on_option_list_option_selected(self, e: OptionList.OptionSelected) -> None:
        self._choose(e.option.id)

    def _choose(self, option_id: str | None) -> None:
        if option_id == _CUSTOM:
            self.dismiss(self._typed)
        else:
            self.dismiss(option_id)

    def _pick_highlighted(self) -> None:
        ol = self.query_one("#picker-list", OptionList)
        if ol.highlighted is not None and ol.option_count:
            self._choose(ol.get_option_at_index(ol.highlighted).id)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "pick":
            self._pick_highlighted()
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)
