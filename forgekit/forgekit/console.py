"""Console mode: Forge apps stay readable on a plain Linux text console (issue #1).

The promise (2026-10-01): every Forge app is readable and usable on a plain text
console (``TERM=linux``, the screen after Ctrl+Alt+F3). It does not have to look
the same as in a terminal window.

A text console has 16 colours (only the 8 basic ones reliably as backgrounds)
and a font of about 256 characters: straight box lines, a few blocks and
arrows, Latin-1. So console mode does three things, all decided once at start:

* colours come from per-role values chosen for the console (see ``theme.py``);
* every character the console font lacks is swapped for one it has, just
  before it reaches the screen (``ConsoleGlyphFilter``), keeping the same width
  so columns stay aligned;
* scrollbars are drawn as whole cells, without the thin partial blocks.

``console_mode()`` decides: ``FORGE_ASCII=1`` forces it on (for terminals that
claim more than they can draw), ``FORGE_ASCII=0`` forces it off, otherwise it is
on exactly when ``TERM=linux``.
"""

from __future__ import annotations

import os
import unicodedata
from collections import Counter
from collections.abc import Mapping

from rich.cells import cell_len
from rich.segment import Segment
from textual.color import Color
from textual.filter import LineFilter
from textual.scrollbar import ScrollBarRender

_ON = {"1", "yes", "true", "on"}
_OFF = {"0", "no", "false", "off"}


def console_mode(environ: Mapping[str, str] | None = None) -> bool:
    """True when the app should draw for a plain text console."""
    env = os.environ if environ is None else environ
    forced = env.get("FORGE_ASCII", "").strip().lower()
    if forced in _ON:
        return True
    if forced in _OFF:
        return False
    return env.get("TERM", "") == "linux"


# Every character above ASCII that the Linux console's default font
# (default8x16, 256 glyphs) can draw, read from the font file on 2026-10-01.
# Note: not all of Latin-1 (Á Ó Ú À ©  × … are missing). Larger console fonts
# (Terminus) draw more; this is the floor every console reaches.
_DRAWABLE = frozenset(
    "\u00a0¡¢£¥§ª«¬°±²µ¶·º»¼½¿ÄÅÆÇÉÑÖÜßàáâäåæçèéêëìíîïñòóôö÷ùúûüÿ"
    "ƒΓΘΣΦΩαβδεμπστφ\u2000\u2001\u2002\u2003\u2004\u2005\u2006"
    "\u2007\u2008\u2009\u200a•\u202f‼ⁿ₧ΩÅ←↑→↓↔↕↨∅∈∎∙√∞∟∩≈≡≤≥⋅⌀⌂⌐⌙"
    "⌠⌡─│┌┐└┘├┤┬┴┼═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬▀▄█▌▐░▒▓■▬▲▶►▼◀◄○◘"
    "◙☺☻☼♀♂♠♣♥♦♪♫♬"
)


def drawable(ch: str) -> bool:
    """Can the console's default font draw this character?"""
    return " " <= ch < "\x7f" or ch in _DRAWABLE


# What the console shows instead. Same width on screen: a wide character (most
# emoji) is replaced by two cells, so tables and menus keep their columns.
FALLBACKS: dict[str, str] = {
    # rounded and heavy box lines → the straight light ones
    "╭": "┌", "╮": "┐", "╰": "└", "╯": "┘",
    "━": "─", "┃": "│", "┏": "┌", "┓": "┐", "┗": "└", "┛": "┘",
    "┣": "├", "┫": "┤", "┳": "┬", "┻": "┴", "╋": "┼",
    "╴": "─", "╶": "─", "╵": "│", "╷": "│", "┄": "─", "┅": "─", "┆": "│", "┈": "─",
    # v0.6.0: the progress bar's half-line ends (it showed "?" on the console)
    "╸": "─", "╺": "─", "╹": "│", "╻": "│",
    # thin edge and partial blocks (Textual's "tall"/"wide" borders, sparklines)
    "▔": "▀", "▁": "▄", "▂": "▄", "▃": "▄", "▅": "▄", "▆": "█", "▇": "█",
    "▏": "▌", "▎": "▌", "▍": "▌", "▋": "▌", "▊": "█", "▉": "█", "▕": "▐",
    # marks and punctuation
    "●": "*", "◉": "*", "◎": "o", "◯": "o", "□": "o", "▪": "■", "▫": "o",
    "✓": "+", "✔": "+", "✗": "x", "✘": "x", "×": "x",
    "©": "c", "®": "r", "¦": "|", "¨": '"', "´": "'", "¸": ",", "¯": "-", "\xad": "-",
    "⚠": "!", "❗": "!", "❌": "x", "ℹ": "i",
    "▸": ">", "▹": ">", "▾": "v", "▿": "v", "◂": "<", "◃": "<", "❯": ">", "❮": "<",
    "…": ".", "—": "-", "–": "-", "‒": "-", "‘": "'", "’": "'", "“": '"', "”": '"',
    "⏳": "~", "⌛": "~", "⌨": "k", "⚙": "*", "⚡": "!", "⛏": "*",
}

def literal(text: str) -> str:
    """Text from outside the app (a tool's question, polkit's message) shown as
    it is: every "[" escaped. Rich's and Textual's own escapes leave "[N]one
    [A]ll" alone, and the markup then swallowed yay's choices (VM, 4 Oct 2026)."""
    return text.replace("\\", "\\\\").replace("[", "\\[")


UNKNOWN = "?"
# Characters swapped by the generic fallback ("?" or blanks) since start-up.
# Tests and the console preview read it; an app adds a FALLBACKS entry or a
# glyph-table name for anything that shows up here.
unmapped: Counter[str] = Counter()


def console_text(text: str) -> str:
    """``text`` with every undrawable character swapped for a drawable one."""
    out = []
    for ch in text:
        if drawable(ch):
            out.append(ch)
        elif ch in FALLBACKS:
            rep = FALLBACKS[ch]  # padded to the original width: columns stay put
            out.append(rep + " " * (cell_len(ch) - cell_len(rep)))
        elif ch in "\ufe0f\u200d":  # emoji modifiers: nothing to draw
            continue
        elif (base := unicodedata.normalize("NFD", ch)[0]) != ch and drawable(base):
            out.append(base)  # Á → A, Ó → O: the letter without its accent
        else:
            unmapped[ch] += 1
            out.append(UNKNOWN if cell_len(ch) == 1 else "  ")
    return "".join(out)


class ConsoleGlyphFilter(LineFilter):
    """Swaps every character the console font cannot draw, as lines are output."""

    def apply(self, segments: list[Segment], background: Color) -> list[Segment]:
        result = []
        for seg in segments:
            text = seg.text
            if text and not all(drawable(ch) for ch in text):
                seg = Segment(console_text(text), seg.style, seg.control)
            result.append(seg)
        return result


class ConsoleScrollBarRender(ScrollBarRender):
    """Scrollbars in whole cells: Textual skips the partial blocks when they are blank."""

    VERTICAL_BARS = [" "] * 8
    HORIZONTAL_BARS = [" "] * 8


# Named marks for apps, with their console stand-ins. ``glyph("ok")`` returns the
# right one for the mode the app runs in.
GLYPHS: dict[str, tuple[str, str]] = {
    "ok": ("✓", "+"),
    "error": ("✗", "x"),
    "warn": ("⚠", "!"),
    "busy": ("⏳", "~"),
    "on": ("●", "*"),
    "off": ("○", "o"),
    "bullet": ("•", "•"),
    "pointer": ("▸", ">"),
    "dash": ("—", "-"),
    "ellipsis": ("…", "..."),
    "arrow": ("→", "→"),
    # v0.5.0 — marks for settings and lists (every plain form is in the
    # console font, and both forms are one cell wide)
    "changed": ("●", "*"),
    "new": ("+", "+"),
    "fixed": ("■", "■"),
    "info": ("i", "i"),
    "default": ("★", "*"),
    "down": ("▾", "v"),
    "check-on": ("x", "x"),
    "radio-on": ("•", "*"),
}

_console = console_mode()


def glyph(name: str) -> str:
    """The mark called ``name``, as the current mode draws it."""
    fancy, plain = GLYPHS[name]
    return plain if _console else fancy


def is_console() -> bool:
    """Is the running app in console mode? (The console shows italic as green
    and underline as cyan, so kit text avoids italic there.)"""
    return _console


def set_console(on: bool) -> None:
    """Switch the glyph table's mode (``ForgeApp`` calls this at start)."""
    global _console
    _console = on
