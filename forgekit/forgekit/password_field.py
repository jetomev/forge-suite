"""The password field: dots, centred (v0.8.0).

Textual's ``Input`` always writes from the left and has no setting to centre
its text. Javier wanted the dots centred as they are typed (sudoForge's design,
D-2, 6 Oct 2026: *"build it into forgekit"*), so every Forge app's password box
uses this field instead.

It is deliberately small: it takes printable keys and pasted text, Backspace
removes the last character, Ctrl+U empties it, Enter sends it. There is no
cursor to move, nothing to select and nothing to copy out, and the screen only
ever holds dots: one per character, centred, the last ones shown when the
password is wider than the field. The dot comes from the glyph table, so a
plain text console draws it too.
"""

from __future__ import annotations

from rich.text import Text
from textual import events
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget

from .console import glyph


class PasswordField(Widget, can_focus=True):
    """A one-line password box that shows its dots centred."""

    COMPONENT_CLASSES = {"password-field--placeholder"}
    DEFAULT_CSS = """
    PasswordField { height: 3; width: 1fr; }
    """
    BINDINGS = [
        Binding("backspace", "delete", "", show=False),
        Binding("ctrl+u", "clear", "", show=False),
        Binding("enter", "submit", "", show=False),
    ]

    class Submitted(Message):
        """Enter was pressed. ``value`` is the password, for the dialog only."""

        def __init__(self, field: "PasswordField", value: str) -> None:
            super().__init__()
            self.field = field
            self.value = value

        @property
        def control(self) -> "PasswordField":
            return self.field

    def __init__(self, placeholder: str = "password", *, id: str | None = None,
                 classes: str | None = None) -> None:
        super().__init__(id=id, classes=classes)
        self.placeholder = placeholder
        self._chars: list[str] = []

    # the value: read by the dialog, never drawn
    @property
    def value(self) -> str:
        return "".join(self._chars)

    @value.setter
    def value(self, text: str) -> None:
        self._chars = list(text)
        self.refresh()

    def clear(self) -> None:
        self._chars.clear()
        self.refresh()

    def __repr__(self) -> str:                      # never the password in a log or traceback
        return f"PasswordField(id={self.id!r}, length={len(self._chars)})"

    # typing
    def _add(self, text: str) -> None:
        clean = [c for c in text if c.isprintable() and c not in "\r\n"]
        if clean:
            self._chars.extend(clean)
            self.refresh()

    async def _on_key(self, event: events.Key) -> None:
        if event.is_printable and event.character:
            event.stop()
            event.prevent_default()
            self._add(event.character)

    def _on_paste(self, event: events.Paste) -> None:
        event.stop()
        self._add(event.text)

    def action_delete(self) -> None:
        if self._chars:
            self._chars.pop()
            self.refresh()

    def action_clear(self) -> None:
        self.clear()

    def action_submit(self) -> None:
        self.post_message(self.Submitted(self, self.value))

    # drawing
    def render(self) -> Text:
        # centred by hand: Textual does not apply a Text's own justify here
        width = max(1, self.content_size.width)
        if not self._chars:
            shown = self.placeholder[:width]
            style = self.get_component_rich_style("password-field--placeholder")
        else:
            shown = glyph("bullet") * min(len(self._chars), max(1, width - 2))
            style = ""
        left = (width - len(shown)) // 2
        return Text(" " * left + shown, style=style, no_wrap=True, overflow="crop")
