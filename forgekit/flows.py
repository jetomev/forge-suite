"""Review and progress windows for work that changes the system (v0.5.0).

* ``ReviewDialog`` — before anything is written: every change as
  ``name   old → new``, grouped by file or area, then "what happens" as numbered
  steps and an optional note (e.g. "You'll be asked for your password once.").
  The app supplies the buttons; the pressed button's id comes back (``None``
  for Cancel or Esc).
* ``ProgressDialog`` — a long job shown step by step, in plain text (no
  spinner): each step is waiting, working, done or failed, with a detail line,
  and the last lines the job printed (``add_line``). The app drives it from a worker and calls
  ``finish()``; the window then gets a Close button.

Both use the standard Forge panel: title, scrolling body, fixed footer.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from rich.markup import escape
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Static

from .console import glyph
from .dialogs import ForgeModal


@dataclass
class ChangeGroup:
    """One area of changes, e.g. ``ChangeGroup("Settings", "/etc/default/grub", [...])``.
    ``changes`` are ``(name, old, new)`` as plain words."""
    title: str
    where: str = ""
    changes: list[tuple[str, str, str]] = field(default_factory=list)


def review_markup(groups: Sequence[ChangeGroup], steps: Sequence[str] = (), note: str = "") -> str:
    lines: list[str] = []
    width = max((len(n) for g in groups for n, _o, _n in g.changes), default=10)
    old_w = max((len(o) for g in groups for _n, o, _x in g.changes), default=6)
    for g in groups:
        head = f"[b]{escape(g.title)}[/]"
        if g.where:
            head += f"  [$forge-muted]{escape(g.where)}[/]"
        lines.append(head)
        for name, old, new in g.changes:
            lines.append(f"  {escape(name):<{width}}   [$forge-muted]{escape(old):<{old_w}}[/]"
                         f"  {glyph('arrow')}  [$forge-changed]{escape(new)}[/]")
        lines.append("")
    if steps:
        lines.append("[b]What happens[/]")
        lines += [f"  {i}  {escape(s)}" for i, s in enumerate(steps, 1)]
        lines.append("")
    if note:
        lines.append(f"[$forge-warn]{escape(note)}[/]")
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


class ReviewDialog(ForgeModal[str | None]):
    BINDINGS = [Binding("escape", "cancel", "", show=False)]

    def __init__(self, title: str, groups: Sequence[ChangeGroup], *,
                 steps: Sequence[str] = (), note: str = "",
                 buttons: Sequence[tuple[str, str, bool]] = (("Save", "save", True),)) -> None:
        super().__init__()
        self._title, self._groups, self._steps, self._note = title, list(groups), list(steps), note
        self._buttons = list(buttons)

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel forge-review"):
            yield Static(self._title, classes="forge-panel-title")
            with VerticalScroll(classes="forge-panel-body"):
                yield Static(review_markup(self._groups, self._steps, self._note), id="review-body")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                for label, bid, primary in self._buttons:
                    yield Button(label, id=bid, variant="primary" if primary else "default")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        for label, bid, primary in self._buttons:
            if primary:
                self.query_one(f"#{bid}", Button).focus()
                break

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        self.dismiss(None if e.button.id == "cancel" else e.button.id)

    def action_cancel(self) -> None:
        self.dismiss(None)


# step states → (glyph name, role)
_STATES = {
    "waiting": ("bullet", "muted"),
    # not the hourglass: it is two cells wide and pushed the line out of line
    "working": ("pointer", "warn"),
    "done": ("ok", "ok"),
    "failed": ("error", "danger"),
    "skipped": ("dash", "muted"),
}


class ProgressDialog(ForgeModal[None]):
    """Steps of a long job. Drive it with ``set_step``, ``add_line`` and ``finish``.
    Esc and the Close button only work once the job has finished."""

    BINDINGS = [Binding("escape", "close", "", show=False)]

    def __init__(self, title: str, steps: Sequence[str]) -> None:
        super().__init__()
        self._title = title
        self._steps = [[s, "waiting", ""] for s in steps]
        self._log: list[str] = []
        self.finished = False

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel forge-progress"):
            yield Static(self._title, classes="forge-panel-title")
            with VerticalScroll(classes="forge-panel-body"):
                yield Static(self._steps_markup(), id="progress-steps")
                yield Static("", id="progress-log")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Close", id="progress-close", variant="primary", disabled=True)

    def _steps_markup(self) -> str:
        out = []
        for text, state, detail in self._steps:
            g, role = _STATES[state]
            line = f"  [$forge-{role}]{glyph(g)}[/] {escape(text)}"
            if state == "working":
                line += f" [$forge-muted]{glyph('ellipsis')}[/]"
            if detail:
                line += f"   [$forge-muted]{escape(detail)}[/]"
            out.append(line)
        return "\n".join(out)

    def set_step(self, index: int, state: str, detail: str = "") -> None:
        self._steps[index][1] = state
        self._steps[index][2] = detail
        if self.is_mounted:
            self.query_one("#progress-steps", Static).update(self._steps_markup())

    def add_line(self, line: str) -> None:
        self._log.append(line)
        if self.is_mounted:
            tail = self._log[-12:]
            self.query_one("#progress-log", Static).update(
                "\n".join(f"    [$forge-muted]{escape(l)}[/]" for l in tail))

    def finish(self) -> None:
        self.finished = True
        if self.is_mounted:
            b = self.query_one("#progress-close", Button)
            b.disabled = False
            b.focus()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        self.action_close()

    def action_close(self) -> None:
        if self.finished:
            self.dismiss(None)
