"""``ManualScreen`` — an app's manual inside the app (v0.5.0).

A contents list on the left, the page on the right, rendered from Markdown.
Pages are ``(page_id, title, markdown)``; an app usually loads them from a
folder of ``.md`` files shipped with it (``load_pages``), so the same files are
readable on GitHub and without the app. Links between pages are written
``[Backups](#backups)`` with the page id. Backspace goes back to the previous
page, Esc closes the manual.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Markdown, OptionList, Static
from textual.widgets.option_list import Option

from .widgets import HintBar


def load_pages(folder: str | Path) -> list[tuple[str, str, str]]:
    """Pages from ``NN-page-id.md`` files, in file-name order. The title is the
    file's first ``# heading``; the id is the name without the number."""
    pages = []
    for p in sorted(Path(folder).glob("*.md")):
        text = p.read_text(encoding="utf-8")
        title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), p.stem)
        page_id = p.stem.split("-", 1)[1] if p.stem[:2].isdigit() and "-" in p.stem else p.stem
        pages.append((page_id, title, text))
    return pages


class ManualScreen(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "close", "", show=False),
        Binding("backspace", "back", "", show=False),
    ]
    FORGE_HINTS = [("↑↓", "contents"), ("Tab", "the page"), ("Enter", "open"),
                   ("Backspace", "back"), ("Esc", "close the manual")]

    def __init__(self, title: str, pages: Sequence[tuple[str, str, str]], start: str | None = None) -> None:
        super().__init__()
        self._title = title
        self._pages = {pid: (t, md) for pid, t, md in pages}
        self._order = [pid for pid, _t, _m in pages]
        self._start = start if start in self._pages else (self._order[0] if self._order else None)
        self._history: list[str] = []
        self.current: str | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="forge-manual"):
            yield Static(f" {self._title}", id="forge-manual-title")
            with Horizontal(id="forge-manual-body"):
                yield OptionList(*(Option(self._pages[p][0], id=p) for p in self._order),
                                 id="forge-manual-contents")
                with VerticalScroll(id="forge-manual-page"):
                    yield Markdown("", id="forge-manual-md")
            hb = HintBar()
            hb.set_hints(self.FORGE_HINTS)
            yield hb

    def on_mount(self) -> None:
        if self._start:
            self.open_page(self._start, remember=False)
        self.query_one("#forge-manual-contents", OptionList).focus()

    def open_page(self, page_id: str, remember: bool = True) -> None:
        if page_id not in self._pages:
            return
        if remember and self.current and self.current != page_id:
            self._history.append(self.current)
        self.current = page_id
        self.query_one("#forge-manual-md", Markdown).update(self._pages[page_id][1])
        self.query_one("#forge-manual-page", VerticalScroll).scroll_home(animate=False)
        ol = self.query_one("#forge-manual-contents", OptionList)
        ol.highlighted = self._order.index(page_id)

    def on_option_list_option_selected(self, e: OptionList.OptionSelected) -> None:
        self.open_page(e.option.id)

    def on_option_list_option_highlighted(self, e: OptionList.OptionHighlighted) -> None:
        # browsing the contents is not a step to go back to; links are
        if e.option.id != self.current:
            self.open_page(e.option.id, remember=False)

    def on_markdown_link_clicked(self, e: Markdown.LinkClicked) -> None:
        e.prevent_default()
        target = e.href.lstrip("#")
        if target in self._pages:
            self.open_page(target)

    def action_back(self) -> None:
        if self._history:
            self.open_page(self._history.pop(), remember=False)

    def action_close(self) -> None:
        self.dismiss(None)
