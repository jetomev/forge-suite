"""Building blocks for the screens inside a Forge app (v0.5.0).

* ``Notice`` — the designed message: a ``==>`` heading in the level's colour,
  the explanation indented under it, exactly one blank line before and after
  (Javier's rule, 2026-10-02). Use it for anything a person must notice.
* ``HintBar`` — the bottom row of keys that changes with what has focus. A
  widget (or any of its parents) declares ``FORGE_HINTS = [(key, words), ...]``;
  the nearest one wins, else the app's ``HINTS``.
* ``ChangesBar`` — the row above the hint bar that says what is not saved (or
  saved but not finished) and carries the buttons that finish it. Hidden when
  there is nothing to say.
* ``SettingRow`` — one setting in a form: a plain label, its control, a
  "changed" mark, and a muted second line ("was: …" or a hint).
* ``NumberPresets`` — a number field plus one-press preset buttons, so typing
  is optional.

Everything is coloured through the ``$forge-*`` roles and marked through
``glyph()``, so it stays readable on a text console.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from rich.markup import escape
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, Static

from .console import glyph

# level → colour role. "changed" is a value edited but not saved yet.
LEVELS = {
    "ok": "ok", "info": "info", "warn": "warn", "error": "danger",
    "changed": "changed", "muted": "muted",
}


def notice_markup(heading: str, lines: Iterable[str] = (), level: str = "info") -> str:
    """Markup for a designed notice, without the surrounding blank lines
    (``Notice`` adds those as margins). ``lines`` are markup already; escape
    any text that came from outside before passing it in."""
    role = LEVELS.get(level, "info")
    out = [f"[b $forge-{role}]==> {escape(heading)}[/]"]
    # non-breaking spaces: plain leading spaces are dropped when the line is
    # laid out, and the indent is part of the design
    out += [f"\u00a0\u00a0\u00a0\u00a0{line}" for line in lines]
    return "\n".join(out)


class Notice(Static):
    """A designed message. ``level``: ok, info, warn, error, changed, muted."""

    DEFAULT_CLASSES = "forge-notice"

    def __init__(self, heading: str = "", lines: Sequence[str] = (), level: str = "info", **kw) -> None:
        super().__init__(notice_markup(heading, lines, level) if heading else "", **kw)
        self.display = bool(heading)

    def show(self, heading: str, lines: Sequence[str] = (), level: str = "info") -> None:
        self.update(notice_markup(heading, lines, level))
        self.display = True

    def hide(self) -> None:
        self.display = False


def hints_markup(hints: Sequence[tuple[str, str]]) -> str:
    sep = f" [$forge-muted]{glyph('bullet')}[/] "
    return " " + sep.join(f"[$forge-hint-key]{escape(k)}[/] [$forge-muted]{escape(d)}[/]" for k, d in hints)


class HintBar(Static):
    """The keys that work right now. ``ForgeApp`` keeps it current; call
    ``set_hints`` to override until focus moves."""

    def __init__(self, **kw) -> None:
        super().__init__("", id="forge-hints", **kw)

    def set_hints(self, hints: Sequence[tuple[str, str]]) -> None:
        self.update(hints_markup(hints))


def hints_for(widget: Widget | None, default: Sequence[tuple[str, str]]) -> Sequence[tuple[str, str]]:
    """The ``FORGE_HINTS`` of the nearest widget up the tree that has some."""
    node = widget
    while node is not None:
        hints = getattr(node, "FORGE_HINTS", None)
        if hints:
            return hints
        node = node.parent
    return default


class ChangesBar(Horizontal):
    """State of unsaved work, with the buttons that finish it.

    ``show(message, level, actions)`` where ``actions`` is a list of
    ``(label, button_id, primary)``. Button presses bubble to the app as normal
    ``Button.Pressed`` events. ``hide()`` when there is nothing pending.
    """

    def __init__(self, **kw) -> None:
        super().__init__(id="forge-changes", **kw)
        self.display = False

    def compose(self) -> ComposeResult:
        yield Static("", id="forge-changes-msg")
        yield Horizontal(id="forge-changes-actions", classes="forge-buttons")

    def show(self, message: str, level: str = "changed",
             actions: Sequence[tuple[str, str, bool]] = ()) -> None:
        role = LEVELS.get(level, "changed")
        mark = glyph("changed") if level == "changed" else glyph("warn") if level == "warn" else glyph("ok")
        self.query_one("#forge-changes-msg", Static).update(f" [$forge-{role}]{mark} {escape(message)}[/]")
        box = self.query_one("#forge-changes-actions", Horizontal)
        box.remove_children()
        box.mount_all(Button(label, id=bid, variant="primary" if primary else "default")
                      for label, bid, primary in actions)
        self.display = True

    def hide(self) -> None:
        self.display = False


class SettingRow(Vertical):
    """One setting: ``label  [control]  ● changed`` with a muted line under it.

    ``note`` is the second line when the value is unchanged (a hint, or "");
    ``mark_changed(was)`` switches it to "was: <old value>" with the changed
    mark, ``mark_unchanged()`` switches back. ``help`` is shown by the app's help
    panel when the row has focus.
    """

    DEFAULT_CLASSES = "forge-setting"

    def __init__(self, label: str, control: Widget, *, note: str = "", help: str = "",
                 setting: str = "", **kw) -> None:
        super().__init__(**kw)
        self.label, self.control, self.note, self.help, self.setting = label, control, note, help, setting
        self.changed = False

    def compose(self) -> ComposeResult:
        with Horizontal(classes="forge-setting-line"):
            yield Static(self.label, classes="forge-setting-label")
            yield self.control
            yield Static("", classes="forge-setting-mark")
        yield Static(self._note_markup(), classes="forge-setting-note")

    def _note_markup(self) -> str:
        return f"[$forge-muted]{escape(self.note)}[/]" if self.note else ""

    def mark_changed(self, was: str) -> None:
        self.changed = True
        self.query_one(".forge-setting-mark", Static).update(f"[$forge-changed]{glyph('changed')} changed[/]")
        self.query_one(".forge-setting-note", Static).update(f"[$forge-muted]was: {escape(was)}[/]")

    def mark_unchanged(self) -> None:
        self.changed = False
        self.query_one(".forge-setting-mark", Static).update("")
        self.query_one(".forge-setting-note", Static).update(self._note_markup())


class NumberPresets(Horizontal):
    """A whole-number field with preset buttons. Posts ``NumberPresets.Changed``.

    ``presets``: list of ``(label, value)``, e.g. ``[("0", 0), ("wait forever", -1)]``.
    The preset matching the value is shown selected.
    """

    DEFAULT_CLASSES = "forge-number"

    class Changed(Message):
        def __init__(self, sender: "NumberPresets", value: int) -> None:
            super().__init__()
            self.number = sender
            self.value = value

        @property
        def control(self) -> "NumberPresets":
            return self.number

    def __init__(self, value: int, presets: Sequence[tuple[str, int]], *, unit: str = "",
                 minimum: int | None = None, maximum: int | None = None, **kw) -> None:
        super().__init__(**kw)
        self.value, self.presets, self.unit = value, list(presets), unit
        self.minimum, self.maximum = minimum, maximum

    def compose(self) -> ComposeResult:
        yield Input(str(self.value), type="integer", classes="forge-number-input")
        if self.unit:
            yield Static(self.unit, classes="forge-number-unit")
        # one Tab stop for the whole setting: the presets are clicked, or
        # stepped through with ↑/↓ in the field
        for i, (label, _v) in enumerate(self.presets):
            b = Button(label, id=f"preset-{i}", classes="forge-preset")
            b.can_focus = False
            yield b

    def on_mount(self) -> None:
        self._mark()

    def _mark(self) -> None:
        for i, (_l, v) in enumerate(self.presets):
            self.query_one(f"#preset-{i}", Button).set_class(v == self.value, "-selected")

    def set_value(self, value: int, announce: bool = True) -> None:
        self.value = value
        inp = self.query_one(Input)
        if inp.value != str(value):
            inp.value = str(value)
        self._mark()
        if announce:
            self.post_message(self.Changed(self, value))

    FORGE_HINTS = [("↑↓", "presets"), ("type", "any number"), ("Tab", "next")]

    def on_key(self, event) -> None:
        if event.key in ("up", "down") and self.presets:
            event.stop()
            values = [v for _l, v in self.presets]
            if self.value in values:
                i = values.index(self.value) + (1 if event.key == "down" else -1)
            else:
                i = 0 if event.key == "down" else len(values) - 1
            self.set_value(values[i % len(values)])

    @on(Button.Pressed, ".forge-preset")
    def _preset(self, e: Button.Pressed) -> None:
        e.stop()
        self.set_value(self.presets[int(e.button.id.removeprefix("preset-"))][1])

    @on(Input.Changed, ".forge-number-input")
    def _typed(self, e: Input.Changed) -> None:
        e.stop()
        try:
            v = int(e.value)
        except ValueError:
            return
        if (self.minimum is not None and v < self.minimum) or (self.maximum is not None and v > self.maximum):
            return
        if v != self.value:
            self.set_value(v)


class Toggle(Static, can_focus=True):
    """On/off, said in words as well as colour: ``● On`` / ``○ Off``.
    Space, Enter or a click flips it. Posts ``Toggle.Changed``."""

    DEFAULT_CLASSES = "forge-toggle"
    FORGE_HINTS = [("Space", "switch on/off"), ("Tab", "next")]

    class Changed(Message):
        def __init__(self, sender: "Toggle", value: bool) -> None:
            super().__init__()
            self.toggle = sender
            self.value = value

        @property
        def control(self) -> "Toggle":
            return self.toggle

    def __init__(self, value: bool = False, *, on_label: str = "On", off_label: str = "Off", **kw) -> None:
        super().__init__("", **kw)
        self.value, self.on_label, self.off_label = value, on_label, off_label

    def on_mount(self) -> None:
        self._draw()

    def _draw(self) -> None:
        if self.value:
            self.update(f" [$forge-ok]{glyph('on')}[/] {escape(self.on_label)} ")
        else:
            self.update(f" [$forge-muted]{glyph('off')}[/] {escape(self.off_label)} ")
        self.set_class(self.value, "-on")

    def set_value(self, value: bool, announce: bool = True) -> None:
        self.value = value
        self._draw()
        if announce:
            self.post_message(self.Changed(self, value))

    def flip(self) -> None:
        self.set_value(not self.value)

    def on_key(self, event) -> None:
        if event.key in ("space", "enter"):
            event.stop()
            self.flip()

    def on_click(self) -> None:
        self.flip()


class Choices(Static, can_focus=True):
    """A few choices in one row: ``( ) Always   (•) With a countdown   ( ) Hidden``.
    ←/→ move the choice (it is picked as it moves, like a radio dial); a click
    picks too. Posts ``Choices.Changed`` with the chosen value. For more than
    about four choices use a ``Select`` or ``FilterPicker``."""

    DEFAULT_CLASSES = "forge-choices"
    FORGE_HINTS = [("←→", "choose"), ("Tab", "next")]

    class Changed(Message):
        def __init__(self, sender: "Choices", value: str) -> None:
            super().__init__()
            self.choices = sender
            self.value = value

        @property
        def control(self) -> "Choices":
            return self.choices

    def __init__(self, options: Sequence[tuple[str, str]], value: str, **kw) -> None:
        super().__init__("", **kw)
        self.options = list(options)   # (value, label)
        self.value = value
        self._spans: list[tuple[int, int]] = []

    def on_mount(self) -> None:
        self._draw()

    def _draw(self) -> None:
        parts, pos, self._spans = [], 1, []
        for v, label in self.options:
            if v == self.value:
                piece = f"[$forge-accent]({glyph('radio-on')})[/] [b]{escape(label)}[/]"
            else:
                piece = f"[$forge-muted]( )[/] {escape(label)}"
            width = 4 + len(label)
            self._spans.append((pos, pos + width))
            pos += width + 3
            parts.append(piece)
        self.update(" " + "   ".join(parts) + " ")

    def set_value(self, value: str, announce: bool = True) -> None:
        self.value = value
        self._draw()
        if announce:
            self.post_message(self.Changed(self, value))

    def _move(self, step: int) -> None:
        values = [v for v, _l in self.options]
        i = values.index(self.value) if self.value in values else 0
        self.set_value(values[(i + step) % len(values)])

    def on_key(self, event) -> None:
        if event.key in ("left", "right"):
            event.stop()
            self._move(-1 if event.key == "left" else 1)

    def on_click(self, event) -> None:
        for (start, end), (v, _l) in zip(self._spans, self.options):
            if start <= event.x < end:
                self.set_value(v)
                return
