"""The Browse window of the Wallpaper page (Javier, D-8 then D-10, 2026-10-13: "something like a file
manager window popup … a very simplified midnight commander"): the folders as a tree on the left, the
pictures of the folder under the cursor on the right.

The tree starts with three things: **The theme's pictures** (not a folder: the pictures hypeForge draws
in the colours picked), **Home** (open by default) and the **KognogOS wallpapers** (what the system ships
in /usr/share/wallpapers). A folder opens with Enter, Space or →, and ← closes it; its sub-folders are
read when it opens (hidden ones left out), so a big disk costs nothing until you look. The right side
shows every picture in the folder under the cursor, each with a small mark and its name. **Use This
Folder (u)** answers with the folder; Enter on a picture answers with the folder AND that picture.
Nothing is made or changed here.
"""

from __future__ import annotations

from pathlib import Path

from rich.markup import escape
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, OptionList, Static, Tree
from textual.widgets.option_list import Option
from textual.widgets.tree import TreeNode

from forgekit import ForgeModal
from forgekit.console import glyph

from .look import PICTURE_TYPES

THEME_MADE = "theme-made"          # the Source that is not a folder: the pictures hypeForge draws
KOGNOGOS_WALLS = Path("/usr/share/wallpapers")
MOST_FOLDERS = 400                 # a folder with more sub-folders than this shows the first ones and says so
MOST_NAME = 48                     # a longer picture name is shortened in the middle, so it stays one line


def tilde(p: Path | str) -> str:
    p = str(p)
    home = str(Path.home())
    return "~" + p[len(home):] if p == home or p.startswith(home + "/") else p


def pictures(folder: Path) -> list[Path]:
    """The pictures in a folder (not its sub-folders), by name; [] when it can't be read."""
    try:
        return sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in PICTURE_TYPES),
                      key=lambda p: p.name.lower())
    except OSError:
        return []


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


def roots(home: Path | None = None, start: str | None = None) -> list[tuple[str, str]]:
    """[(value, name)] at the top of the tree: the theme's pictures, Home, the KognogOS wallpapers if there;
    and, when the folder in use lies outside all of them (another drive), that folder's parent, so it can
    be reached too."""
    home = home or Path.home()
    out = [(THEME_MADE, "The theme's pictures"), (str(home), "Home")]
    if KOGNOGOS_WALLS.is_dir():
        out.append((str(KOGNOGOS_WALLS), "KognogOS wallpapers"))
    if start and start != THEME_MADE:
        here = Path(start)
        if here.is_dir() and not any(here == Path(v) or Path(v) in here.parents for v, _ in out[1:]):
            top = here.parent if here.parent != here else here
            out.append((str(top), tilde(top)))
    return out


class FolderTree(Tree[str]):
    """The folders; each node's data is its path (THEME_MADE for the theme's pictures). → opens, ← closes
    or goes up, Enter and Space as Textual's tree has them."""

    BINDINGS = [Binding("right", "open_node", "", show=False), Binding("left", "close_node", "", show=False)]

    def action_open_node(self) -> None:
        node = self.cursor_node
        if node is not None and node.allow_expand and not node.is_expanded:
            node.expand()

    def action_close_node(self) -> None:
        node = self.cursor_node
        if node is None:
            return
        if node.is_expanded:
            node.collapse()
        elif node.parent is not None and not node.parent.is_root:
            self.move_cursor(node.parent)


class FolderPicker(ForgeModal[dict | None]):
    """Answers {"source": a folder's path or THEME_MADE, "pick": a picture's value or None}, or None."""

    BINDINGS = [Binding("escape", "cancel", "", show=False), Binding("u", "use", "", show=False)]

    def __init__(self, start: str | Path, *, home: Path | None = None, theme_entries: list[tuple[str, str]] = ()) -> None:
        super().__init__()
        self.home = home or Path.home()
        self.start = str(start) if start else str(self.home)
        self.theme_entries = list(theme_entries)      # [(value, words)] of the theme's pictures
        self.loaded: set[int] = set()

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel tf-browse"):
            yield Static("Pick a folder", classes="forge-panel-title")
            yield Static("[$forge-muted]↑ ↓ move · → or Enter opens a folder · ← closes it · "
                         "Tab to the pictures, Enter picks one[/]", classes="forge-picker-hint")
            yield Static("", id="tf-br-where")
            with Horizontal(id="tf-br-panes"):
                yield FolderTree("folders", id="tf-br-tree")
                yield OptionList(id="tf-br-files")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Use This Folder (u)", id="use", variant="primary")
                yield Button("Cancel (Esc)", id="cancel")

    def on_mount(self) -> None:
        tree = self.query_one("#tf-br-tree", FolderTree)
        tree.show_root = False
        tree.guide_depth = 3
        for value, name in roots(self.home, self.start):
            if value == THEME_MADE:
                tree.root.add_leaf(name, data=value)
            else:
                tree.root.add(name, data=value, allow_expand=True)
        tree.root.expand()
        tree.focus()
        self.call_after_refresh(self.start_at, self.start)      # the tree has its lines only after a draw

    def start_at(self, target: str) -> None:
        self.reveal(target)
        self.show_files(self.query_one("#tf-br-tree", FolderTree).cursor_node)

    # ---- the tree ----

    def load(self, node: TreeNode[str]) -> None:
        """A folder's sub-folders, read once, when it opens."""
        if node.id in self.loaded or node.data in (None, THEME_MADE):
            return
        self.loaded.add(node.id)
        subs = subfolders(Path(node.data))
        for d in subs[:MOST_FOLDERS]:
            node.add(escape(d.name), data=str(d), allow_expand=True)
        if len(subs) > MOST_FOLDERS:
            node.add_leaf(f"[$forge-muted]… {len(subs) - MOST_FOLDERS} more folders[/]", data=None)
        if not subs:
            node.allow_expand = False

    def reveal(self, target: str) -> None:
        """Open the tree down to a folder and put the cursor on it; a folder outside every root lands on Home."""
        tree = self.query_one("#tf-br-tree", FolderTree)

        def land(node: TreeNode[str]) -> None:
            tree.last_line                        # a node knows its line only once the tree has built them
            tree.move_cursor(node)

        for node in tree.root.children:
            if node.data == target:
                land(node)
                return
        here = Path(target)
        for node in tree.root.children:
            if node.data in (None, THEME_MADE):
                continue
            root = Path(node.data)
            if here == root or root in here.parents:
                for part in here.relative_to(root).parts:
                    node.expand()
                    self.load(node)
                    child = next((c for c in node.children if c.data == str(Path(node.data) / part)), None)
                    if child is None:
                        break
                    node = child
                land(node)
                return
        home = next((n for n in tree.root.children if n.data == str(self.home)), None)
        if home is not None:
            land(home)

    def on_tree_node_expanded(self, e: Tree.NodeExpanded) -> None:
        self.load(e.node)

    def on_tree_node_highlighted(self, e: Tree.NodeHighlighted) -> None:
        self.show_files(e.node)

    def on_tree_node_selected(self, e: Tree.NodeSelected) -> None:
        self.show_files(e.node)
        if not e.node.allow_expand and e.node.data:          # Enter on the theme's pictures (nothing to open): take it
            self.dismiss({"source": e.node.data, "pick": None})

    def current(self) -> str | None:
        node = self.query_one("#tf-br-tree", FolderTree).cursor_node
        return node.data if node is not None else None

    # ---- the pictures on the right ----

    def entries(self, source: str | None) -> list[tuple[str, str]]:
        if source == THEME_MADE:
            return self.theme_entries
        if not source:
            return []
        return [(str(p), p.name) for p in pictures(Path(source))]

    def show_files(self, node: TreeNode[str] | None) -> None:
        ol = self.query_one("#tf-br-files", OptionList)
        ol.clear_options()
        source = node.data if node is not None else None
        rows = self.entries(source)
        mark = glyph("fixed")
        for value, words in rows:
            if len(words) > MOST_NAME:                       # a very long name keeps its start and its ending
                words = words[:MOST_NAME - 16] + "…" + words[-15:]
            ol.add_option(Option(f"[$forge-accent]{mark}[/] {escape(words)}", id=value))
        if rows:
            ol.highlighted = 0
        n = len(rows)
        if source == THEME_MADE:
            where = f"The theme's pictures · {n}, drawn in the colours you picked"
        elif source:
            where = f"{escape(tilde(source))} · " + (f"{n} picture{'s' if n != 1 else ''}" if n else "no pictures here")
        else:
            where = ""
        self.query_one("#tf-br-where", Static).update(f"[$forge-accent b]{where}[/]")

    def on_option_list_option_selected(self, e: OptionList.OptionSelected) -> None:
        if e.option_list.id == "tf-br-files":
            e.stop()
            self.dismiss({"source": self.current(), "pick": e.option.id})

    # ---- the buttons ----

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        if e.button.id == "use":
            self.action_use()
        else:
            self.dismiss(None)

    def action_use(self) -> None:
        source = self.current()
        if source:
            self.dismiss({"source": source, "pick": None})

    def action_cancel(self) -> None:
        self.dismiss(None)
