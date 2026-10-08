"""Menu bar + dropdown submenu.

Menu model (a plain list of dicts the app owns):

    {"id": "config", "title": "Config", "kind": "menu", "items": [
        ("New entry", "n", "add"), ...]}          # kind: section | menu | action

Main options use their first letter as the accelerator (Ctrl+<letter>); submenu
items carry a per-item letter that selects them (no Ctrl) while the menu is open.
"""

from __future__ import annotations

from rich.cells import cell_len
from rich.text import Text

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from .console import is_console


def accel(entry: dict) -> str:
    """The main-option accelerator letter (defaults to the title's first)."""
    return entry.get("acc", entry["title"][0]).lower()


def underline_label(label: str, acc_letter: str) -> Text:
    """Render ``label`` with ``acc_letter`` underlined (first match)."""
    t = Text(" ")
    i = label.lower().find(acc_letter.lower())
    if i < 0:
        t.append(label)
    else:
        t.append(label[:i])
        t.append(label[i], style="underline")
        t.append(label[i + 1:])
    return t


class MenuBar(Vertical):
    """The top menu bar: one clickable title per entry, its accelerator letter
    underlined, each title with id ``menu-<entry id>``.

    The titles are laid out in **as many rows as the window needs** (0.9.0,
    forge-suite #40): on a narrow window the ones that no longer fit move to a
    second row instead of being cut off, so every section stays reachable by
    mouse and key. The bar's height follows; the header is ``height: auto``.
    """

    def __init__(self, menu: list[dict], **kwargs) -> None:
        super().__init__(id="forge-menubar", **kwargs)
        self._menu = menu
        self._rows: list[list[dict]] = []

    # ---- what each title shows -------------------------------------------------------------
    @staticmethod
    def _markup(m: dict) -> str:
        title, a = m["title"], accel(m)
        i = title.lower().find(a)
        markup = f"{title[:i]}[u]{title[i]}[/u]{title[i+1:]}" if i >= 0 else title
        # F-12: a text console sends Ctrl+H as Backspace, so Help is on F1
        # there, and the bar says so (console mode only)
        if m["id"] == "help" and is_console():
            markup += " [$forge-accent]F1[/]"
        return f" {markup} "

    @staticmethod
    def _width(m: dict) -> int:
        """Cells a title takes on screen: a space, the title, a space — and " F1"
        after Help on a text console (plain arithmetic; the markup carries Textual
        variables Rich's parser does not know)."""
        extra = 3 if m["id"] == "help" and is_console() else 0
        return cell_len(f" {m['title']} ") + extra

    def layout_rows(self, width: int) -> list[list[dict]]:
        """Split the entries into rows that fit ``width`` cells, in order. A title
        wider than the whole window gets a row of its own (it is cut, nothing
        else is)."""
        rows: list[list[dict]] = [[]]
        used = 0
        for m in self._menu:
            w = self._width(m)
            if rows[-1] and used + w > width:
                rows.append([])
                used = 0
            rows[-1].append(m)
            used += w
        return rows

    # ---- building and rebuilding -------------------------------------------------------------
    def _row_widgets(self, row: list[dict], active: set[str] = frozenset()) -> Horizontal:
        """One row of titles; the ones in ``active`` are born marked, so a reflow
        never loses the mark (mount and remove are not instant)."""
        return Horizontal(
            *(Static(self._markup(m), id=f"menu-{m['id']}",
                     classes="menu-title active" if f"menu-{m['id']}" in active else "menu-title")
              for m in row),
            classes="menu-row",
        )

    def compose(self) -> ComposeResult:
        self._rows = [list(self._menu)]
        yield self._row_widgets(self._menu)

    def on_resize(self, event) -> None:
        self.relayout(event.size.width)

    def relayout(self, width: int) -> None:
        """Re-flow the titles for ``width``; keeps the active mark. Does nothing
        when the row split is unchanged, so a same-size redraw costs nothing."""
        if width <= 0:
            return
        rows = self.layout_rows(width)
        if rows == self._rows:
            return
        active = {w.id for w in self.query(".menu-title.active")}
        self._rows = rows
        self.remove_children()
        for row in rows:
            self.mount(self._row_widgets(row, active))


class MenuDropdown(ModalScreen[str | None]):
    """Transient dropdown anchored under a menu title. Returns the chosen
    action id, or None on escape / click-away. ``items`` is a list of
    (label, accel_letter, action_id)."""

    BINDINGS = [Binding("escape", "dismiss_none", "", show=False)]

    def __init__(self, items: list[tuple[str, str, str]], x: int, y: int) -> None:
        super().__init__()
        self._items = items
        self._x, self._y = x, y
        self._accels = {a.lower(): act for _l, a, act in items}

    def compose(self) -> ComposeResult:
        # +6 = leading space + option padding + round border → longest name
        # always fits on one line (no wrapping).
        width = max((len(l) for l, _a, _ in self._items), default=8) + 6
        ol = OptionList(
            *(Option(underline_label(l, a), id=act) for l, a, act in self._items),
            classes="forge-dropdown",
        )
        ol.styles.width = width
        yield ol

    def on_mount(self) -> None:
        ol = self.query_one(OptionList)
        ol.styles.offset = (self._x, self._y)
        ol.focus()

    def on_key(self, event) -> None:
        ch = (event.character or "").lower()
        if ch in self._accels:
            event.stop()
            self.dismiss(self._accels[ch])

    def on_option_list_option_selected(self, e: OptionList.OptionSelected) -> None:
        self.dismiss(e.option.id)

    def action_dismiss_none(self) -> None:
        self.dismiss(None)

    def on_click(self, event) -> None:
        if self.get_widget_at(event.screen_x, event.screen_y)[0] is self:
            self.dismiss(None)
