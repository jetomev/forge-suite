"""A program's run, shown inside the app (v0.6.0).

``RunWindow`` is where a Forge app hands work to a real tool (nog, a helper)
without leaving its own screen. It has two views of the same run:

* **Steps**, the calm view: a checklist of what the tool is doing and a
  progress bar. The tool announces its steps as JSON lines in a small file
  (``events_path``; nog does this through ``NOG_EVENTS``):
  ``{"ev":"steps","steps":[{"id":…,"label":…}]}``,
  ``{"ev":"step","id":…,"state":"start|done|failed|skipped","detail":…}``,
  ``{"ev":"ask","question":…}``, ``{"ev":"end","status":…}``.
* **The tool's own screen**, a ``TerminalPane``: everything it printed, as in
  a terminal. It opens by itself when the tool asks something (so the table a
  question is about is in view), when a step fails, and when the run ends
  badly; F12 opens and folds it at any time.

A question gets a bar with its words and **Yes (y)** / **No (n)** buttons;
the answer goes to the tool exactly as typed (or type it in the pane). The
password is asked by ``PasswordDialog`` through the app's ``PasswordBridge``.
Without an events file the window simply shows the tool's screen.
"""

from __future__ import annotations

import json
import os
import re
from typing import Sequence

from .console import literal as escape
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, ProgressBar, Static

from .console import glyph
from .dialogs import ForgeModal
from .flows import _STATES
from .terminal import YES_NO, TerminalPane

# pacman's "(3/12) upgrading foo" and yay's "(1/3) building" — progress inside a step
_COUNT = re.compile(r"^\((\d+)/(\d+)\)\s")


class RunWindow(ForgeModal[int]):
    """Run ``cmd`` inside the app; dismisses with its exit status."""

    BINDINGS = [
        Binding("f12", "toggle_screen", "", show=False, priority=True),
        Binding("escape", "close", "", show=False),
    ]

    def __init__(self, title: str, cmd: Sequence[str], env: dict | None = None, *,
                 events_path: str | None = None, show_screen: bool | None = None,
                 tool: str = "the program", done_words: str = "Done.") -> None:
        super().__init__()
        self._title, self._cmd, self._env = title, list(cmd), dict(env or os.environ)
        self._events = events_path
        self._events_pos = 0
        self._steps: list[list[str]] = []          # [id, label, state, detail]
        self._screen_open = show_screen if show_screen is not None else not events_path
        self._tool, self._done_words = tool, done_words
        self._question: str | None = None
        self._answered: str | None = None
        self.status: int | None = None

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel forge-run"):
            yield Static(self._title, classes="forge-panel-title", id="run-title")
            yield Static("", id="run-steps")
            yield ProgressBar(total=None, show_eta=False, show_percentage=True, id="run-progress")
            with Horizontal(id="run-question"):
                yield Static("", id="run-question-text")
                yield Button("Yes (y)", id="run-yes", variant="primary")
                yield Button("No (n)", id="run-no")
            yield TerminalPane(id="run-screen")
            yield Static("", id="run-status")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button(f"{self._tool}'s Screen (F12)", id="run-toggle")
                yield Button("Close (Esc)", id="run-close", variant="primary", disabled=True)

    async def on_mount(self) -> None:
        self.query_one("#run-question").display = False
        self.query_one("#run-steps").display = bool(self._events)
        self.query_one("#run-progress").display = bool(self._events)
        self._show_screen(self._screen_open)
        self._set_status(f"[$forge-muted]{glyph('pointer')} {escape(self._tool)} is working{glyph('ellipsis')}[/]")
        if self._events:
            self.set_interval(0.15, self._read_events)
        pane = self.query_one(TerminalPane)
        # the window's width, less its frame: the size the screen will have when opened
        cols = max(40, int(self.app.size.width * 0.9) - 8)
        lines = max(8, int(self.app.size.height * 0.9) - 14)
        self.call_after_refresh(pane.start, self._cmd, self._env, None if self._screen_open else (cols, lines))

    # ── the two views ────────────────────────────────────────────────────────
    def _show_screen(self, on: bool) -> None:
        self._screen_open = on
        pane = self.query_one(TerminalPane)
        pane.display = on
        self.set_class(on, "-screen-open")
        if on:
            pane.focus()
        elif self._question:
            self.query_one("#run-yes", Button).focus()

    def action_toggle_screen(self) -> None:
        self._show_screen(not self._screen_open)

    # ── nog's (or any tool's) steps ──────────────────────────────────────────
    def _read_events(self) -> None:
        try:
            with open(self._events, "rb") as f:
                f.seek(self._events_pos)
                chunk = f.read()
        except OSError:
            return
        if not chunk:
            return
        end = chunk.rfind(b"\n") + 1          # only whole lines
        self._events_pos += end
        for raw in chunk[:end].splitlines():
            try:
                self.event(json.loads(raw))
            except ValueError:
                continue

    def event(self, ev: dict) -> None:
        kind = ev.get("ev")
        if kind == "steps":
            known = {s[0]: s for s in self._steps}          # a step already under way keeps its state
            self._steps = [known.get(s.get("id", "")) or [s.get("id", ""), s.get("label", s.get("id", "")), "waiting", ""]
                           for s in ev.get("steps", [])]
        elif kind == "step":
            sid = ev.get("id", "")
            row = next((s for s in self._steps if s[0] == sid), None)
            if row is None:
                row = [sid, ev.get("label", sid), "waiting", ""]
                self._steps.append(row)
            if ev.get("label"):
                row[1] = ev["label"]
            row[2] = {"start": "working", "done": "done", "failed": "failed", "skipped": "skipped"}.get(
                ev.get("state", ""), row[2])
            row[3] = ev.get("detail", "") or ""
            if row[2] == "failed":
                self._show_screen(True)
        elif kind == "ask":
            self._ask(ev.get("question", ""))
        self._draw_steps()

    def _draw_steps(self) -> None:
        out = []
        for _sid, label, state, detail in self._steps:
            g, role = _STATES[state]
            line = f"  [$forge-{role}]{glyph(g)}[/] {escape(label)}"
            if state == "working":
                line += f" [$forge-muted]{glyph('ellipsis')}[/]"
            if detail:
                line += f"   [$forge-muted]{escape(detail)}[/]"
            out.append(line)
        self.query_one("#run-steps", Static).update("\n".join(out))
        self._draw_progress()

    def _draw_progress(self) -> None:
        if not self._steps:
            return
        done = sum(1 for s in self._steps if s[2] in ("done", "skipped", "failed"))
        frac = 0.0
        if any(s[2] == "working" for s in self._steps):
            for line in reversed(self.query_one(TerminalPane).lines_plain()[-6:]):
                m = _COUNT.match(line.strip())
                if m and int(m.group(2)):
                    frac = min(int(m.group(1)) / int(m.group(2)), 1.0)
                    break
        bar = self.query_one("#run-progress", ProgressBar)
        bar.update(total=len(self._steps) * 100, progress=int((done + frac) * 100))

    # ── questions ────────────────────────────────────────────────────────────
    @on(TerminalPane.Output)
    def _output(self, e: TerminalPane.Output) -> None:
        e.stop()
        if self._question and e.pane.waiting_question() != self._question:
            self._hide_question()                         # answered (here or typed in the pane)
        self._q_timer = getattr(self, "_q_timer", None)
        if self._q_timer is not None:
            self._q_timer.stop()
        # a question waits with nothing printed after it: look once output settles
        self._q_timer = self.set_timer(0.3, self._look_for_question)
        if self._steps:
            self._draw_progress()

    def _look_for_question(self) -> None:
        pane = self.query_one(TerminalPane)
        if pane.screen_vt.in_alternate:
            # a full-screen program (an editor, a pager): it has the keys, no question bar
            self._hide_question()
            if not self._screen_open:
                self._show_screen(True)
            pane.focus()
            return
        q = pane.waiting_question()
        if q and q != self._question and q != self._answered:
            self._ask(q)

    def _ask(self, question: str) -> None:
        self._question = question
        yes_no = bool(YES_NO.search(question))
        text = f"[b]{escape(question)}[/]"
        if not yes_no:
            # a menu or a number (yay's clean-build and diff menus): typed in
            # the tool's own screen, where its choices are listed
            text += f"\n[$forge-muted]Type your answer in {escape(self._tool)}'s screen below, then Enter " \
                    f"(Enter alone takes its default).[/]"
        self.query_one("#run-question-text", Static).update(text)
        self.query_one("#run-yes").display = yes_no
        self.query_one("#run-no").display = yes_no
        self.query_one("#run-question").display = True
        if not self._screen_open:
            self._show_screen(True)                       # the table the question is about
        if yes_no:
            self.query_one("#run-yes", Button).focus()
        else:
            self.query_one(TerminalPane).focus()

    def _hide_question(self) -> None:
        self._answered, self._question = self._question, None
        self.query_one("#run-question").display = False

    def answer(self, yes: bool) -> None:
        pane = self.query_one(TerminalPane)
        pane.write(b"y\r" if yes else b"n\r")
        self._hide_question()
        pane.focus()

    # ── the end ──────────────────────────────────────────────────────────────
    @on(TerminalPane.Exited)
    def _exited(self, e: TerminalPane.Exited) -> None:
        e.stop()
        if self._events:
            self._read_events()
        self.status = e.status
        self._hide_question()
        for s in self._steps:
            if s[2] in ("working", "waiting"):
                s[2] = "done" if e.status == 0 and s[2] == "working" else "skipped"
        if self._steps:
            self._draw_steps()
            bar = self.query_one("#run-progress", ProgressBar)
            if e.status == 0:
                bar.update(total=100, progress=100)
        if e.status == 0:
            self._set_status(f"[$forge-ok]{glyph('ok')}[/] {escape(self._done_words)}")
        else:
            self._set_status(f"[$forge-danger]{glyph('error')}[/] {escape(self._tool)} stopped (status {e.status}): "
                             f"its own words are on its screen above.")
            self._show_screen(True)
        close = self.query_one("#run-close", Button)
        close.disabled = False
        close.focus()

    def _set_status(self, markup: str) -> None:
        self.query_one("#run-status", Static).update(markup)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        bid = e.button.id
        if bid == "run-yes":
            self.answer(True)
        elif bid == "run-no":
            self.answer(False)
        elif bid == "run-toggle":
            self.action_toggle_screen()
        elif bid == "run-close":
            self.action_close()

    def on_key(self, event) -> None:
        # y / n answer a yes/no question when the screen isn't taking the keys
        if self._question and self.query_one("#run-yes").display and \
                not self.query_one(TerminalPane).has_focus and event.key in ("y", "n"):
            event.stop()
            self.answer(event.key == "y")

    def action_close(self) -> None:
        if self.status is not None:
            self.dismiss(self.status)
