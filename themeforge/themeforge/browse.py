"""The Browse pop-up of the Wallpaper page (Javier, D-8: "Source folders for background picker should
be browsable"): walk the folders and pick one.

A small window over the page: the folder you are in (type another and press Enter), how many
pictures it holds, a list of the places worth a jump (the theme's own pictures, Home, Pictures, the
KognogOS wallpapers) and of the folders inside, each with its count of pictures. Enter goes into a
folder, Backspace goes up, **Use This Folder (u)** picks the one you are in. Nothing is made or
changed here: it only answers "which folder".

The theme's pictures (the theme's own, KognogOS Tier Aware and Arch Distro, the solid colour) are
not files in a folder: hypeForge draws them in the colours picked. They are listed as the first
place, so the Wallpaper page's Images list shows them the same way it shows a folder (D-9).
"""

from __future__ import annotations

from pathlib import Path

from rich.markup import escape
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, OptionList, Static
from textual.widgets.option_list import Option

from forgekit import ForgeModal
from forgekit.console import glyph

from .look import PICTURE_TYPES

THEME_MADE = "theme-made"          # the Source that is not a folder: the pictures hypeForge draws
MOST_FOLDERS = 400                 # /usr/share has hundreds; the list stops there and says so


def tilde(p: Path | str) -> str:
    p = str(p)
    home = str(Path.home())
    return "~" + p[len(home):] if p == home or p.startswith(home + "/") else p


def count_pictures(folder: Path) -> int:
    """How many pictures a folder holds (not its sub-folders); -1 when it can't be read."""
    try:
        return sum(1 for p in folder.iterdir() if p.is_file() and p.suffix.lower() in PICTURE_TYPES)
    except OSError:
        return -1


def subfolders(folder: Path) -> list[Path]:
    """The folders inside, by name; hidden ones (a dot first) left out."""
    try:
        return sorted((p for p in folder.iterdir() if p.is_dir() and not p.name.startswith(".")),
                      key=lambda p: p.name.lower())
    except OSError:
        return []


def places(home: Path | None = None) -> list[tuple[str, str, str]]:
    """[(value, name, where)]: the theme's pictures first, then the folders worth a jump that exist."""
    home = home or Path.home()
    out = [(THEME_MADE, "The theme's pictures", "drawn in the colours you picked")]
    for name, p in (("Home", home), ("Pictures", home / "Pictures"), ("KognogOS wallpapers", Path("/usr/share/wallpapers"))):
        if p.is_dir():
            out.append((str(p), name, tilde(p)))
    return out


class FolderPicker(ForgeModal[str | None]):
    """Returns the folder picked (a path), THEME_MADE for the theme's pictures, or None for Cancel."""

    BINDINGS = [Binding("escape", "cancel", "", show=False), Binding("backspace", "up", "", show=False),
                Binding("u", "use", "", show=False)]

    def __init__(self, start: str | Path, *, home: Path | None = None) -> None:
        super().__init__()
        self.home = home or Path.home()
        s = Path(start).expanduser() if start and start != THEME_MADE else self.home / "Pictures"
        self.folder = s if s.is_dir() else (s.parent if s.parent.is_dir() else self.home)
        self.came_from: Path | None = None

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel forge-picker tf-browse"):
            yield Static("Pick a folder", classes="forge-panel-title")
            yield Static("[$forge-muted]Enter goes into a folder · Backspace goes up · "
                         "or type a folder and press Enter[/]", classes="forge-picker-hint")
            yield Input(str(self.folder), id="tf-br-path", placeholder="a folder", select_on_focus=False)
            yield Static("", id="tf-br-count")
            yield OptionList(id="tf-br-list")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Use This Folder (u)", id="use", variant="primary")
                yield Button("Cancel (Esc)", id="cancel")

    def on_mount(self) -> None:
        self.fill()
        self.query_one("#tf-br-list", OptionList).focus()

    # ---- the list ----

    def fill(self) -> None:
        ol = self.query_one("#tf-br-list", OptionList)
        ol.clear_options()
        star = glyph("default")
        for value, name, where in places(self.home):
            ol.add_option(Option(f"{star} {escape(name):<22}[$forge-muted]{escape(where)}[/]", id=f"place:{value}"))
        ol.add_option(None)
        back_to, first = None, ol.option_count                 # the first entry after the places
        if self.folder.parent != self.folder:
            ol.add_option(Option(f"{glyph('arrow')} up to {escape(tilde(self.folder.parent))}", id="up"))
        subs = subfolders(self.folder)
        for d in subs[:MOST_FOLDERS]:
            n = count_pictures(d)
            words = f"{n} picture{'s' if n != 1 else ''}" if n > 0 else ""
            if self.came_from == d:
                back_to = ol.option_count
            ol.add_option(Option(f"  {escape(d.name)}/  [$forge-muted]{words}[/]", id=f"dir:{d}"))
        if len(subs) > MOST_FOLDERS:
            ol.add_option(Option(f"  [$forge-muted]… and {len(subs) - MOST_FOLDERS} more: type the folder above[/]",
                                 id="more", disabled=True))
        n = count_pictures(self.folder)
        here = ("This folder can't be read." if n < 0 else "No pictures here" + (", but folders inside." if subs else ".")
                if n == 0 else f"{n} picture{'s' if n != 1 else ''} here (PNG, JPEG, WebP…)")
        self.query_one("#tf-br-count", Static).update(f"[$forge-muted]{escape(here)}[/]")
        self.query_one("#tf-br-path", Input).value = str(self.folder)
        ol.highlighted = back_to if back_to is not None else first if ol.option_count > first else 0

    def go(self, folder: Path) -> None:
        if not folder.is_dir():
            self.query_one("#tf-br-count", Static).update(f"[$forge-warn]There's no folder called {escape(str(folder))}.[/]")
            return
        self.came_from = self.folder if folder == self.folder.parent else None
        self.folder = folder
        self.fill()

    # ---- the person's moves ----

    def on_option_list_option_selected(self, e: OptionList.OptionSelected) -> None:
        oid = e.option.id or ""
        if oid == "up":
            self.action_up()
        elif oid == f"place:{THEME_MADE}":
            self.dismiss(THEME_MADE)
        elif oid.startswith("place:"):
            self.go(Path(oid[6:]))
        elif oid.startswith("dir:"):
            self.go(Path(oid[4:]))

    def on_input_submitted(self, e: Input.Submitted) -> None:
        if e.input.id == "tf-br-path":
            e.stop()
            self.go(Path(e.value.strip() or "~").expanduser())
            self.query_one("#tf-br-list", OptionList).focus()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        if e.button.id == "use":
            self.action_use()
        else:
            self.dismiss(None)

    def action_up(self) -> None:
        if self.folder.parent != self.folder:
            self.go(self.folder.parent)

    def action_use(self) -> None:
        typed = Path(self.query_one("#tf-br-path", Input).value.strip() or str(self.folder)).expanduser()
        if typed.is_dir():
            self.dismiss(str(typed))
        else:
            self.go(typed)                      # says there's no such folder

    def action_cancel(self) -> None:
        self.dismiss(None)
