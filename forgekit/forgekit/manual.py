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


class ManualView(Vertical):
    """The manual as a page in the app's work area (0.10.0, Javier 2026-10-08: "Keys and Manual
    as pages too"). Esc goes back to the page you came from; Backspace to the previous manual
    page. ``ForgeApp.show_manual`` puts it on screen; ``ManualScreen`` wraps it in a window."""

    BINDINGS = [
        Binding("escape", "close", "", show=False),
        Binding("backspace", "back", "", show=False),
    ]
    FORGE_HINTS = [("↑↓", "contents"), ("Tab", "the page"), ("Enter", "open"),
                   ("Backspace", "back"), ("Esc", "close the manual")]

    def __init__(self, title: str, pages: Sequence[tuple[str, str, str]], start: str | None = None,
                 **kw) -> None:
        super().__init__(**kw)
        self._title = title
        self._pages = {pid: (t, md) for pid, t, md in pages}
        self._order = [pid for pid, _t, _m in pages]
        self._start = start if start in self._pages else (self._order[0] if self._order else None)
        self._history: list[str] = []
        self.current: str | None = None
        # the contents list reports its own first highlight late; until the
        # requested page has settled, its highlights are not someone browsing
        self._settled = False

    def compose(self) -> ComposeResult:
        yield Static(f" {self._title}", id="forge-manual-title")
        with Horizontal(id="forge-manual-body"):
            yield OptionList(*(Option(self._pages[p][0], id=p) for p in self._order),
                             id="forge-manual-contents")
            with VerticalScroll(id="forge-manual-page"):
                yield Markdown("", id="forge-manual-md")

    def on_mount(self) -> None:
        if self._start:
            self.open_page(self._start, remember=False)
        self.query_one("#forge-manual-contents", OptionList).focus()
        self.call_after_refresh(self._settle)

    def go_to(self, page_id: str | None) -> None:
        """Show it again, at ``page_id`` (or where it was)."""
        if page_id in self._pages:
            self._settled = False
            self.open_page(page_id)
            self.call_after_refresh(self._settle)
        self.query_one("#forge-manual-contents", OptionList).focus()

    def _settle(self) -> None:
        if self.current:
            self.query_one("#forge-manual-contents", OptionList).highlighted = self._order.index(self.current)
        self.call_after_refresh(lambda: setattr(self, "_settled", True))

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
        e.stop()
        self.open_page(e.option.id)

    def on_option_list_option_highlighted(self, e: OptionList.OptionHighlighted) -> None:
        e.stop()
        # browsing the contents is not a step to go back to; links are
        if self._settled and e.option.id != self.current:
            self.open_page(e.option.id, remember=False)

    def on_key(self, event) -> None:
        from .dialogs import quiet_letters
        quiet_letters(event)

    def on_markdown_link_clicked(self, e: Markdown.LinkClicked) -> None:
        e.prevent_default()
        target = e.href.lstrip("#")
        if target in self._pages:
            self.open_page(target)

    def action_back(self) -> None:
        if self._history:
            self.open_page(self._history.pop(), remember=False)

    def action_close(self) -> None:
        if isinstance(self.screen, ManualScreen):
            self.screen.dismiss(None)
            return
        back = getattr(self.app, "action_back_from_page", None)
        if back:
            back()


class ManualScreen(ModalScreen[None]):
    """The manual in a window over the app (how it opened before 0.10.0)."""

    def __init__(self, title: str, pages: Sequence[tuple[str, str, str]], start: str | None = None) -> None:
        super().__init__()
        self.view = ManualView(title, pages, start, id="forge-manual")

    def compose(self) -> ComposeResult:
        yield self.view
        hb = HintBar()
        hb.set_hints(ManualView.FORGE_HINTS)
        yield hb

    @property
    def current(self) -> str | None:
        return self.view.current

    def open_page(self, page_id: str, remember: bool = True) -> None:
        self.view.open_page(page_id, remember)
