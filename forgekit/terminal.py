"""A terminal inside the app (v0.6.0).

``TerminalPane`` runs a program in a pseudo-terminal and draws its screen
inside the Textual app, so a Forge app never has to leave its own window to
show a real tool at work (Javier, 4 Oct 2026: nog running outside the UI "is
not beautiful, it is disrupting"). The program sees a real terminal: colours,
progress bars, questions and full-screen editors work as they would in a
terminal window, and the keys typed in the pane go to it.

How it works: ``pty.openpty()`` gives a pair of ends; the program gets the
inner end as its terminal (``setsid --ctty`` makes it the controlling
terminal, so Ctrl+C reaches it), the app reads the outer end on its own event
loop and feeds the bytes to pyte, a terminal emulator in pure Python, whose
screen the pane draws. ``ForgeScreen`` adds what pyte lacks: the alternate
screen (``ESC[?1049h``) that editors and pagers switch to, so the output
before them comes back when they close, and a capped scrollback.
"""

from __future__ import annotations

import fcntl
import os
import pty
import re
import signal
import struct
import subprocess
import termios
from collections import deque
from typing import Sequence

import pyte
from rich.segment import Segment
from rich.style import Style
from textual import events
from textual.geometry import Size
from textual.message import Message
from textual.scroll_view import ScrollView
from textual.strip import Strip

SCROLLBACK = 5000          # lines kept above the screen; an AUR build can print megabytes
ALT_MODES = (1049, 1047, 47)

# pyte's colour names → Rich's
_NAMES = {"brown": "yellow"}


def _colour(c: str) -> str | None:
    if not c or c == "default":
        return None
    if len(c) == 6 and all(ch in "0123456789abcdefABCDEF" for ch in c):
        return "#" + c
    c = _NAMES.get(c, c)
    if c.startswith("bright"):
        return "bright_" + _NAMES.get(c[6:], c[6:])
    return c


def _copy_line(line):
    """A copy that keeps the line's default character (a plain dict copy loses it)."""
    new = type(line)(line.default)
    new.update(line)
    return new


class ForgeScreen(pyte.HistoryScreen):
    """pyte's screen with the alternate screen and a top-only scrollback."""

    def __init__(self, columns: int, lines: int) -> None:
        super().__init__(columns, lines, history=SCROLLBACK, ratio=0.5)
        self._saved: tuple | None = None
        self.title = ""

    def set_mode(self, *modes: int, **kwargs) -> None:
        if kwargs.get("private") and any(m in ALT_MODES for m in modes) and self._saved is None:
            self._saved = ({y: _copy_line(line) for y, line in self.buffer.items()}, self.cursor.x, self.cursor.y,
                           self.cursor.attrs)
            self.buffer.clear()
            self.dirty.update(range(self.lines))
            modes = tuple(m for m in modes if m not in ALT_MODES)
        super().set_mode(*modes, **kwargs)

    def reset_mode(self, *modes: int, **kwargs) -> None:
        if kwargs.get("private") and any(m in ALT_MODES for m in modes) and self._saved is not None:
            buf, x, y, attrs = self._saved
            self._saved = None
            self.buffer.clear()
            self.buffer.update(buf)
            self.cursor.x, self.cursor.y, self.cursor.attrs = x, y, attrs
            self.dirty.update(range(self.lines))
            modes = tuple(m for m in modes if m not in ALT_MODES)
        super().reset_mode(*modes, **kwargs)

    def resize(self, lines: int | None = None, columns: int | None = None) -> None:
        # pyte cuts a shrinking screen from the top, losing what was there; a
        # terminal keeps the bottom (where the cursor is) and lets the top
        # scroll away into the scrollback
        lines = lines or self.lines
        if lines < self.lines:
            drop = max(0, self.cursor.y - (lines - 1))
            if drop:
                if not self.in_alternate:
                    for y in range(drop):
                        self.history.top.append(self.buffer[y])
                kept = {y - drop: line for y, line in self.buffer.items() if y >= drop}
                self.buffer.clear()
                self.buffer.update(kept)
                self.cursor.y -= drop
            for y in [y for y in self.buffer if y >= lines]:
                del self.buffer[y]
            self.lines = lines
            self.dirty.update(range(lines))
            self.set_margins()
        super().resize(lines, columns)

    @property
    def in_alternate(self) -> bool:
        return self._saved is not None

    def index(self) -> None:
        # Only lines leaving the main screen go to the scrollback: an editor's
        # alternate screen scrolling must not flood it.
        if self.in_alternate:
            pyte.Screen.index(self)
        else:
            super().index()

    def set_title(self, param: str) -> None:
        self.title = param


# Textual key names → the bytes a terminal sends
_KEYS = {
    "enter": b"\r", "tab": b"\t", "shift+tab": b"\x1b[Z", "backspace": b"\x7f", "escape": b"\x1b",
    "delete": b"\x1b[3~", "insert": b"\x1b[2~", "home": b"\x1b[H", "end": b"\x1b[F",
    "pageup": b"\x1b[5~", "pagedown": b"\x1b[6~", "space": b" ",
    "f1": b"\x1bOP", "f2": b"\x1bOQ", "f3": b"\x1bOR", "f4": b"\x1bOS", "f5": b"\x1b[15~",
    "f6": b"\x1b[17~", "f7": b"\x1b[18~", "f8": b"\x1b[19~", "f9": b"\x1b[20~", "f10": b"\x1b[21~",
    "f11": b"\x1b[23~",
}
_ARROWS = {"up": "A", "down": "B", "right": "C", "left": "D"}


def key_bytes(key: str, character: str | None, app_cursor: bool = False) -> bytes | None:
    """The bytes for a key press, or None for keys the pane leaves to the app."""
    if key in _ARROWS:
        return (b"\x1bO" if app_cursor else b"\x1b[") + _ARROWS[key].encode()
    if key in _KEYS:
        return _KEYS[key]
    m = re.fullmatch(r"ctrl\+([a-z])", key)
    if m:
        return bytes([ord(m.group(1)) - 96])
    if character and character.isprintable():
        return character.encode()
    return None


# A program waiting for an answer: pacman, yay, nog and sudo all end their
# question this way (checked on the last line written, with the cursor on it).
QUESTION = re.compile(
    r"(\[[Yy]/[Nn]\]|\[[Nn]/[Yy]\]|\[y/N\]|\[Y/n\]|Enter a number|Enter a selection|==> \[[^\]]*\]"
    r"|\(default=[^)]*\):|Proceed with|\?\s*$|:\s*$)")


class TerminalPane(ScrollView, can_focus=True):
    """A program in a pseudo-terminal, drawn inside the app. Keys go to it."""

    DEFAULT_CSS = """
    TerminalPane { background: $forge-bg; color: $forge-text; height: 1fr; scrollbar-size-vertical: 1; }
    """

    class Exited(Message):
        def __init__(self, pane: "TerminalPane", status: int) -> None:
            super().__init__()
            self.pane, self.status = pane, status

    class Output(Message):
        """Something new arrived (for the steps view and question spotting)."""

        def __init__(self, pane: "TerminalPane") -> None:
            super().__init__()
            self.pane = pane

    def __init__(self, *, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(id=id, classes=classes)
        self.screen_vt = ForgeScreen(80, 24)
        self._stream = pyte.ByteStream(self.screen_vt)
        self._fd: int | None = None
        self.proc: subprocess.Popen | None = None
        self.status: int | None = None
        self._follow = True
        self.transcript: deque[str] = deque(maxlen=200)   # the last lines, plain (for reasons and tests)

    # ── running ──────────────────────────────────────────────────────────────
    def start(self, cmd: Sequence[str], env: dict | None = None, size: tuple[int, int] | None = None) -> None:
        """Run ``cmd`` in a new pseudo-terminal the size of the pane (or ``size``,
        columns × lines, when the pane is folded away and has no size yet)."""
        cols, lines = size if size else self._term_size()
        self.screen_vt.resize(lines, cols)
        master, slave = pty.openpty()
        _set_size(master, lines, cols)
        e = dict(env if env is not None else os.environ)
        e["TERM"] = "xterm-256color" if not os.environ.get("TERM", "").startswith("linux") else "linux"
        e.pop("COLUMNS", None)
        e.pop("LINES", None)
        # setsid --ctty: a new session whose controlling terminal is the pane,
        # so Ctrl+C reaches the program and sudo/pacman see a real terminal
        self.proc = subprocess.Popen(["setsid", "--ctty", *cmd], stdin=slave, stdout=slave, stderr=slave,
                                     env=e, close_fds=True)
        os.close(slave)
        self._fd = master
        os.set_blocking(master, False)
        import asyncio
        asyncio.get_running_loop().add_reader(master, self._readable)

    def _readable(self) -> None:
        try:
            data = os.read(self._fd, 65536)
        except BlockingIOError:
            return
        except OSError:
            data = b""
        if not data:
            self._finish()
            return
        self.feed(data)

    def feed(self, data: bytes) -> None:
        self._stream.feed(data)
        self._sync()
        self.post_message(self.Output(self))

    def _finish(self) -> None:
        import asyncio
        if self._fd is not None:
            try:
                asyncio.get_running_loop().remove_reader(self._fd)
            except (RuntimeError, ValueError):
                pass
            os.close(self._fd)
            self._fd = None
        code = self.proc.wait() if self.proc else 0
        self.status = code
        self._sync()
        self.post_message(self.Exited(self, code))

    def on_unmount(self) -> None:
        # the window closing never leaves the program running unseen
        if self._fd is not None:
            self.terminate()
            import asyncio
            try:
                asyncio.get_running_loop().remove_reader(self._fd)
            except (RuntimeError, ValueError):
                pass
            os.close(self._fd)
            self._fd = None

    @property
    def running(self) -> bool:
        return self._fd is not None

    def write(self, data: bytes) -> None:
        if self._fd is not None:
            os.write(self._fd, data)

    def interrupt(self) -> None:
        """Ctrl+C, as the program would get it from a terminal."""
        self.write(b"\x03")

    def terminate(self) -> None:
        if self.proc and self.proc.poll() is None:
            try:
                os.killpg(self.proc.pid, signal.SIGHUP)
            except OSError:
                pass

    # ── what is on screen ────────────────────────────────────────────────────
    def lines_plain(self) -> list[str]:
        """Scrollback + screen, as plain text, trailing blank lines dropped."""
        out = [self._plain(l) for l in self.screen_vt.history.top] + [l.rstrip() for l in self.screen_vt.display]
        while out and not out[-1]:
            out.pop()
        return out

    def _plain(self, line) -> str:
        return "".join(line[x].data for x in range(self.screen_vt.columns)).rstrip()

    def last_line(self) -> str:
        """The line the cursor is on (where a question waits for its answer)."""
        y = self.screen_vt.cursor.y
        return self.screen_vt.display[y].rstrip()

    def waiting_question(self) -> str | None:
        line = self.last_line()
        if line and QUESTION.search(line) and self.screen_vt.cursor.x >= len(line.rstrip()) - 1:
            return line.strip()
        return None

    # ── drawing ──────────────────────────────────────────────────────────────
    def _term_size(self) -> tuple[int, int]:
        w, h = self.scrollable_content_region.size
        return max(w, 20), max(h, 5)

    def _sync(self) -> None:
        hist = len(self.screen_vt.history.top)
        self.virtual_size = Size(self.screen_vt.columns, hist + self.screen_vt.lines)
        if self._follow:
            self.scroll_end(animate=False, immediate=True)
        self.screen_vt.dirty.clear()
        self.refresh()

    def on_resize(self, event: events.Resize) -> None:
        if not self.display or self.size.width < 10:
            return                       # folded away: the program keeps the size it has
        cols, lines = self._term_size()
        if (cols, lines) != (self.screen_vt.columns, self.screen_vt.lines):
            self.screen_vt.resize(lines, cols)
            if self._fd is not None:
                _set_size(self._fd, lines, cols)
            self._sync()

    def render_line(self, y: int) -> Strip:
        _sx, sy = self.scroll_offset
        row = sy + y
        top = self.screen_vt.history.top
        width = self.size.width
        cursor_x = -1
        if row < len(top):
            line = top[row]
        else:
            i = row - len(top)
            if i >= self.screen_vt.lines:
                return Strip.blank(width)
            line = self.screen_vt.buffer[i]
            cur = self.screen_vt.cursor
            if i == cur.y and not cur.hidden and self.has_focus and self.running:
                cursor_x = cur.x
        segs: list[Segment] = []
        run, run_style = [], None
        for x in range(min(self.screen_vt.columns, width)):
            ch = line[x]
            style = Style(color=_colour(ch.fg), bgcolor=_colour(ch.bg), bold=ch.bold or None,
                          italic=ch.italics or None, underline=ch.underscore or None,
                          reverse=(ch.reverse != (x == cursor_x)) or None)
            if style != run_style and run:
                segs.append(Segment("".join(run), run_style))
                run = []
            run_style = style
            run.append(ch.data or " ")
        if run:
            segs.append(Segment("".join(run), run_style))
        return Strip(segs, sum(len(s.text) for s in segs)).extend_cell_length(width)

    # ── input ────────────────────────────────────────────────────────────────
    def on_key(self, event: events.Key) -> None:
        if not self.running:
            return
        app_cursor = (1 << 5) in self.screen_vt.mode          # DECCKM (private mode 1): arrows as ESC O x
        data = key_bytes(event.key, event.character, app_cursor)
        if data is None:
            return
        event.stop()
        event.prevent_default()
        self._follow = True
        self.write(data)

    def on_paste(self, event: events.Paste) -> None:
        if self.running:
            event.stop()
            self.write(event.text.encode())

    def watch_scroll_y(self, old: float, new: float) -> None:
        super().watch_scroll_y(old, new)
        self._follow = new >= self.max_scroll_y


def _set_size(fd: int, lines: int, cols: int) -> None:
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", lines, cols, 0, 0))
