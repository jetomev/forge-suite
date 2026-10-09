"""workspaceForge — the app frame, on forgekit (the displayForge pattern).

Design: docs/design/v0.1.0-screens.html, approved by Javier on 9 Oct 2026 (D-5). The pages read
and change only the Session (model.py); saving goes through a review, a backup first, the open
windows carried over to their workspace's new name or place (live.py), and the Workspaces applet
asked to read its file again.
"""

from __future__ import annotations

import os

from rich.markup import escape
from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.coordinate import Coordinate
from textual.message import Message
from textual.widgets import Button, Collapsible, DataTable, Input, OptionList, Select, Static
from textual.widgets.option_list import Option

from forgekit import (
    FORGE_CSS, GPL3_NOTICE, MENU_HINT, ChangeGroup, ForgeApp, ForgeModal, Notice, ReviewDialog, SettingRow,
    Toggle, load_pages, sway_session, start_check,
)

from . import __version__, apps as A, model as M
from .live import Live

MANUAL_DIR = os.path.join(os.path.dirname(__file__), "manual")
SCREEN_NAMES = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
                            "displayforge/screens.toml")

WF_CSS = FORGE_CSS + """
.wf-buttons { height: auto; padding: 0 0 1 0; }
.wf-buttons Button { margin: 0 1 0 0; }
#wf-ws-row { height: 1fr; }
#wf-ws-left { width: 34; height: 1fr; border-right: solid $forge-border; padding: 1 1 0 0; }
#wf-ws-list { height: 1fr; border: none; background: $forge-bg; }
#wf-ws-right { width: 1fr; height: 1fr; padding: 1 0 0 2; }
#wf-ws-title { height: auto; margin: 0 0 1 0; }
#wf-ws-info { height: auto; margin: 1 0 0 0; }
#wf-ws-warn { height: auto; }
#wf-switch { height: auto; border: round $forge-border; border-title-color: $forge-accent;
             border-title-style: bold; padding: 0 1; margin: 1 1 0 0; }
#wf-switch Horizontal { height: auto; }
#wf-switch-words { width: 1fr; padding: 0 0 0 2; }
#wf-apps-head { height: auto; padding: 1 0 0 0; }
.wf-side { width: 1fr; height: auto; }
#wf-pool-box { padding: 0 1 0 0; }
#wf-right-head { padding: 0 0 0 1; }
#wf-mid-head { width: 10; }
#wf-apps-body { height: 1fr; }
#wf-mid { width: 10; height: 1fr; align: center middle; }
#wf-mid Button { width: 8; min-width: 8; margin: 1 0 0 0; }
#wf-mid Static { width: 8; text-align: center; color: $forge-muted; }
#wf-right { width: 1fr; height: 1fr; padding: 0 0 0 1; }
#wf-pool { width: 1fr; height: 1fr; }
.wf-ws-table { height: auto; max-height: 16; }
.wf-filters { height: auto; padding: 0 0 1 0; }
.wf-filters Input { width: 1fr; }
.wf-filters Select { width: 22; }
#wf-share-grid { height: auto; grid-gutter: 0 2; margin: 1 0; }
.wf-share-head { text-style: bold; }
ShareCell { width: 14; }
ShareCell:focus { background: $forge-focus-bg; }
"""


def screen_label(screen: str, names: dict[str, str]) -> str:
    """"Main Monitor · DP-3" when displayForge has a name for it, else "DP-3"."""
    return f"{names[screen]} · {screen}" if names.get(screen) else screen


def displayforge_names() -> dict[str, str]:
    """The screen names you gave in displayForge (its settings file; never its code)."""
    import tomllib
    try:
        with open(SCREEN_NAMES, "rb") as f:
            return {str(k): str(v) for k, v in tomllib.load(f).get("names", {}).items()}
    except (OSError, tomllib.TOMLDecodeError):
        return {}


# ---- a table of apps with ticks (Javier's layout, D-3) ---------------------------------------------

NAME_WIDTH = 24   # long names are cut with "…" so the category column fits at 100 columns


class TickTable(DataTable):
    """Apps with a [x] each, their category, every other row shaded, headings that sort (a click,
    again for the other way, ▲ ▼ showing which)."""

    BINDINGS = [Binding("space", "tick", show=False)]

    def __init__(self, **kw) -> None:
        super().__init__(zebra_stripes=True, cursor_type="row", **kw)
        self.rows_data: list[tuple[str, str, str]] = []       # (app id, name, category)
        self.ticked: set[str] = set()
        self.sort_by, self.reverse = "name", False

    def on_mount(self) -> None:
        self.draw()

    def fill(self, rows: list[tuple[str, str, str]]) -> None:
        self.rows_data = rows
        self.ticked &= {r[0] for r in rows}
        self.draw()

    def draw(self) -> None:
        keep = self.current_id()
        self.clear(columns=True)
        arrow = " ▼" if self.reverse else " ▲"
        self.add_column("", key="tick", width=3)
        self.add_column("App" + (arrow if self.sort_by == "name" else ""), key="name")
        self.add_column("Category" + (arrow if self.sort_by == "cat" else ""), key="cat")
        col = 1 if self.sort_by == "name" else 2
        for app_id, name, cat in sorted(self.rows_data, key=lambda r: (r[col].lower(), r[1].lower()),
                                        reverse=self.reverse):
            shown = name if len(name) <= NAME_WIDTH else name[:NAME_WIDTH - 1] + "…"   # the category stays in sight
            self.add_row(self._mark(app_id), shown, cat, key=app_id)
        ids = [r for r in self.shown_ids()]
        if keep in ids:
            self.move_cursor(row=ids.index(keep))

    def _mark(self, app_id: str) -> Text:
        return Text("[x]" if app_id in self.ticked else "[ ]")

    def shown_ids(self) -> list[str]:
        return [str(rk.value) for rk in self.rows]

    def current_id(self) -> str | None:
        if not self.row_count:
            return None
        try:
            return str(self.coordinate_to_cell_key(Coordinate(self.cursor_row, 0)).row_key.value)
        except Exception:
            return None

    def set_tick(self, app_id: str, value: bool) -> None:
        (self.ticked.add if value else self.ticked.discard)(app_id)
        if app_id in self.shown_ids():
            self.update_cell(app_id, "tick", self._mark(app_id))

    def action_tick(self) -> None:
        app_id = self.current_id()
        if app_id:
            self.set_tick(app_id, app_id not in self.ticked)

    def on_data_table_row_selected(self, e: DataTable.RowSelected) -> None:
        e.stop()
        self.set_tick(str(e.row_key.value), str(e.row_key.value) not in self.ticked)

    def on_data_table_header_selected(self, e: DataTable.HeaderSelected) -> None:
        e.stop()
        key = str(e.column_key.value)
        if key == "tick":
            return
        self.reverse = not self.reverse if self.sort_by == key else False
        self.sort_by = key
        self.draw()

    def select_all(self) -> None:
        """Only the rows showing (Javier, D-3): the filtered list, or the open workspace."""
        for app_id in self.shown_ids():
            self.set_tick(app_id, True)

    def deselect_all(self) -> None:
        for app_id in self.shown_ids():
            self.set_tick(app_id, False)


# ---- 1 · Workspaces -----------------------------------------------------------------------------------

class DeleteDialog(ForgeModal[int | None]):
    """Delete a workspace: its open windows move to the one you pick; nothing is closed."""

    BINDINGS = [Binding("escape", "stay", "", show=False), Binding("d", "delete", "", show=False)]

    def __init__(self, name: str, windows: list[str], others: list[tuple[str, int]], after: str) -> None:
        super().__init__()
        self._name, self._windows, self._others, self._after = name, windows, others, after

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel"):
            yield Static(f"Delete “{escape(self._name)}”?", classes="forge-panel-title")
            if self._windows:
                n = len(self._windows)
                yield Static(f"[b]{n} window{'s are' if n != 1 else ' is'} open on {escape(self._name)}:[/]\n"
                             f"  [$forge-muted]{escape(' · '.join(self._windows[:6]))}"
                             f"{' …' if n > 6 else ''}[/]")
            else:
                yield Static(f"[$forge-muted]Nothing is open on {escape(self._name)} right now.[/]")
            yield SettingRow("They move to", Select(self._others, value=self._others[0][1], allow_blank=False,
                                                    id="del-to"), setting="to")
            yield Static(f"[$forge-muted]{escape(self._after)}\nIts apps go back to “opens where you are” "
                         "until you place them.[/]")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Delete and Move Them (d)", id="del-yes", variant="primary")
                yield Button("Stay (Esc)", id="del-stay")

    def on_mount(self) -> None:
        self.query_one("#del-yes", Button).focus()

    def _to(self) -> int:
        return int(self.query_one("#del-to", Select).value)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        self.dismiss(self._to() if e.button.id == "del-yes" else None)

    def action_delete(self) -> None:
        self.dismiss(self._to())

    def action_stay(self) -> None:
        self.dismiss(None)


class WorkspacesView(Vertical):
    """1 · Workspaces: the list, the picked one, new and edit right on the page (D-4)."""

    FORGE_HINTS = [("↑ ↓", "pick"), ("n", "new"), ("e", "edit"), ("d", "delete"), ("+ -", "move"),
                   ("F10", "save"), MENU_HINT]
    BINDINGS = [Binding("n", "new", show=False), Binding("e", "edit", show=False),
                Binding("d", "delete", show=False), Binding("plus", "move(-1)", show=False),
                Binding("minus", "move(1)", show=False), Binding("escape", "cancel", show=False)]

    def __init__(self, session: M.Session, live: Live, **kw) -> None:
        super().__init__(**kw)
        self.session, self.live = session, live
        self.picked: int | None = session.pending.workspaces[0].uid if session.pending.workspaces else None
        self.mode = "view"                  # view · new · edit
        self.renamed: tuple[int, str] | None = None   # the ⚠ note after a rename, until you move on
        self.open_windows: dict[str, list[str]] = {}

    def compose(self) -> ComposeResult:
        with Horizontal(id="wf-ws-row"):
            with Vertical(id="wf-ws-left"):
                with Horizontal(classes="wf-buttons"):
                    yield Button("Move Up (+)", id="ws-up")
                    yield Button("Move Down (-)", id="ws-down")
                yield Static("[$forge-muted] Win  Workspace          on now[/]")
                yield OptionList(id="wf-ws-list")
            with VerticalScroll(id="wf-ws-right"):
                with Horizontal(classes="wf-buttons"):
                    yield Button("New (n)", id="ws-new")
                    yield Button("Edit (e)", id="ws-edit")
                    yield Button("Delete (d)", id="ws-del")
                yield Static("", id="wf-ws-title")
                yield SettingRow("Name", Input(id="ws-name", disabled=True), setting="name")
                opts = [(f"{i} · {w.name}", w.uid) for i, w in enumerate(self.session.pending.workspaces, 1)]
                yield SettingRow("Goes after", Select(opts, allow_blank=not opts, id="ws-after"), setting="after",
                                 id="ws-after-row")
                yield Static("", id="wf-ws-info")
                yield Static("", id="wf-ws-warn")
                with Horizontal(classes="wf-buttons", id="ws-form-buttons"):
                    yield Button("Create (Enter)", id="ws-ok", variant="primary")
                    yield Button("Cancel (Esc)", id="ws-cancel")
        box = Vertical(id="wf-switch")
        box.border_title = "Workspaces across all screens"
        with box:
            with Horizontal():
                yield Toggle(self.session.pending.enabled, id="ws-enabled")
                yield Static("[$forge-muted]On: switching a workspace switches every screen together. "
                             "Off: Sway's own way, each screen by itself.[/]", id="wf-switch-words")

    def on_mount(self) -> None:
        self.refresh_view()

    # -- drawing ---------------------------------------------------------------------------------------
    def refresh_view(self) -> None:
        self.open_windows = self.live.windows()
        p = self.session.pending
        if self.picked is not None and not p.has(self.picked):
            self.picked = p.workspaces[0].uid if p.workspaces else None
        ol = self.query_one("#wf-ws-list", OptionList)
        ol.clear_options()
        here = self._on_screen()
        for i, w in enumerate(p.workspaces, 1):
            mark = "●" if w.uid == here else " "
            ol.add_option(Option(f" {i}  {escape(w.name):<20} {mark}", id=str(w.uid)))
        if self.mode == "new":
            ol.add_option(Option(f" {len(p.workspaces) + 1}  [$forge-changed](new)[/]", id="new"))
            ol.highlighted = len(p.workspaces)
        elif self.picked is not None:
            ol.highlighted = p.index(self.picked) - 1
        self.query_one("#ws-enabled", Toggle).set_value(p.enabled, announce=False)
        self.draw_page()

    def _on_screen(self) -> int | None:
        """The workspace on screen now: the applet writes its number; the saved order says which."""
        try:
            with open(os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "hypeforge-workspaces.current")) as f:
                n = int(f.read())
        except (OSError, ValueError):
            return None
        s = self.session.saved
        return s.workspaces[n - 1].uid if 1 <= n <= len(s.workspaces) else None

    def windows_of(self, uid: int) -> list[str]:
        s = self.session.saved
        if not s.has(uid):
            return []
        cells = {s.cell(uid, sc) for sc in s.screens if not s.is_shared(uid, sc)}
        return [w for c in cells for w in self.open_windows.get(c, [])]

    def draw_page(self) -> None:
        p = self.session.pending
        name_in = self.query_one("#ws-name", Input)
        after_row = self.query_one("#ws-after-row")
        buttons = self.query_one("#ws-form-buttons")
        warn = self.query_one("#wf-ws-warn", Static)
        info = self.query_one("#wf-ws-info", Static)
        title = self.query_one("#wf-ws-title", Static)
        for b in ("ws-new", "ws-edit", "ws-del", "ws-up", "ws-down"):
            self.query_one(f"#{b}", Button).disabled = self.mode != "view"
        if self.mode == "new":
            title.update("[$forge-accent b]New workspace[/]   [$forge-muted]fill it in right here[/]")
            after = self.query_one("#ws-after", Select)
            with after.prevent(Select.Changed):
                after.set_options([(f"{i} · {w.name}", w.uid) for i, w in enumerate(p.workspaces, 1)])
                after.value = (self.picked if self.picked is not None else p.workspaces[-1].uid)
            after_row.display = True
            n = len(p.workspaces) + 1
            info.update(f"[$forge-muted]It becomes one of your workspaces: Win + its number takes every screen "
                        f"there.\nIt starts with no apps; give it some on the Apps page (Ctrl + A).[/]"
                        + ("" if n <= M.MOST else f"\n[$forge-warn]{M.MOST} is the most for now.[/]"))
            warn.update("")
            self.query_one("#ws-ok", Button).label = "Create (Enter)"
            buttons.display = True
            return
        after_row.display = False
        if self.picked is None:
            title.update("[$forge-muted]No workspaces yet: press New (n).[/]")
            info.update("")
            buttons.display = False
            return
        w = p.get(self.picked)
        i = p.index(w.uid)
        title.update(f"[$forge-accent b]{i} · {escape(w.name)}[/]   "
                     f"[$forge-muted]Win + {i} switches {'all your screens' if p.enabled else 'a screen'} here[/]")
        if self.mode != "edit":
            with name_in.prevent(Input.Changed):
                name_in.value = w.name
        names = [self.app.app_names.get(a, a) for a in w.apps]
        shared = [sc for sc in p.screens if p.is_shared(w.uid, sc)]
        open_now = self.windows_of(w.uid)
        some = ", ".join(names[:3])
        some = some if len(some) <= 40 else some[:39] + "…"
        lines = [f"[b]Apps that open[/]  [b]{len(w.apps)}[/] [$forge-muted]{escape(some)}"
                 f"{', …' if len(names) > 3 and not some.endswith('…') else ''}[/]"]
        if self.renamed and self.renamed[0] == w.uid:
            lines.append("                [$forge-warn]⚠ renamed: check its apps (Ctrl + A)[/]")
        else:
            lines.append("                [$forge-muted]change them on the Apps page (Ctrl + A)[/]")
        lines += ["", "[b]Sharing[/]         [$forge-muted]" +
                  (escape("shares " + ", ".join(self.app.screen_label(sc) for sc in shared))
                   if shared else "none: every screen has its own space here") + "[/]",
                  "", "[b]Open now[/]        [$forge-muted]" +
                  (escape(" · ".join(open_now[:5]) + (" …" if len(open_now) > 5 else "")) if open_now
                   else ("nothing" if self.session.saved.has(w.uid) else "nothing yet (not saved)")) + "[/]"]
        info.update("\n".join(lines))
        warn.update("")
        if self.mode == "edit":
            self.query_one("#ws-ok", Button).label = "Done (Enter)"
            buttons.display = True
        else:
            buttons.display = False

    # -- picking ---------------------------------------------------------------------------------------
    def on_option_list_option_highlighted(self, e: OptionList.OptionHighlighted) -> None:
        if self.mode != "view" or not e.option.id or e.option.id == "new":
            return
        uid = int(e.option.id)
        if uid != self.picked:
            self.picked = uid
            if self.renamed and self.renamed[0] != uid:
                self.renamed = None                  # the note goes once you move on (D-4)
            self.draw_page()

    # -- the buttons and keys ---------------------------------------------------------------------------
    def on_button_pressed(self, e: Button.Pressed) -> None:
        bid = e.button.id or ""
        actions = {"ws-new": self.action_new, "ws-edit": self.action_edit, "ws-del": self.action_delete,
                   "ws-up": lambda: self.action_move(-1), "ws-down": lambda: self.action_move(1),
                   "ws-ok": self.finish, "ws-cancel": self.action_cancel}
        if bid in actions:
            e.stop()
            actions[bid]()

    def action_new(self) -> None:
        if self.mode != "view":
            return
        if len(self.session.pending.workspaces) >= M.MOST:
            self.app.notify(f"{M.MOST} workspaces is the most for now: Win + 1 … {M.MOST} reach them.",
                            severity="warning")
            return
        self.mode = "new"
        self.renamed = None
        name_in = self.query_one("#ws-name", Input)
        name_in.disabled = False
        name_in.value = ""
        name_in.placeholder = "a name, like Studio"
        self.refresh_view()
        name_in.focus()

    def action_edit(self) -> None:
        if self.mode != "view" or self.picked is None:
            return
        self.mode = "edit"
        name_in = self.query_one("#ws-name", Input)
        name_in.disabled = False
        self.draw_page()
        name_in.focus()
        name_in.cursor_position = len(name_in.value)

    def action_cancel(self) -> None:
        if self.mode == "view":
            return
        self.mode = "view"
        self.query_one("#ws-name", Input).disabled = True
        self.refresh_view()
        self.query_one("#wf-ws-list", OptionList).focus()

    def on_input_submitted(self, e: Input.Submitted) -> None:
        if e.input.id == "ws-name":
            e.stop()
            self.finish()

    def finish(self) -> None:
        name = self.query_one("#ws-name", Input).value
        try:
            if self.mode == "new":
                after = self.query_one("#ws-after", Select).value
                uid = self.session.add(name, int(after) if after not in (None, Select.NULL) else None)
                self.picked = uid
                self.app.notify(f"New workspace: {name.strip()}. Press F10 to save it.", timeout=5)
            elif self.mode == "edit" and self.picked is not None:
                old = self.session.pending.get(self.picked).name
                new = self.session.rename(self.picked, name)
                if new != old:
                    self.renamed = (self.picked, old)
        except M.Problem as p:
            self.app.notify(str(p), title="Not yet", severity="warning")
            return
        self.mode = "view"
        self.query_one("#ws-name", Input).disabled = True
        self.refresh_view()
        self.query_one("#wf-ws-list", OptionList).focus()
        self.app.refresh_state()

    def action_delete(self) -> None:
        if self.mode != "view" or self.picked is None:
            return
        p = self.session.pending
        if len(p.workspaces) <= 1:
            self.app.notify("One workspace always stays. Rename it instead (e).", severity="warning")
            return
        w = p.get(self.picked)
        i = p.index(w.uid)
        others = [(f"{j} · {o.name}", o.uid) for j, o in enumerate(p.workspaces, 1) if o.uid != w.uid]
        n = len(p.workspaces)
        after = (f"Win + {i + 1} … {n} become Win + {i} … {n - 1} (the ones after it move up)."
                 if i < n else "It is the last one: no other number changes.")

        def done(to: int | None) -> None:
            if to is None:
                return
            try:
                self.session.delete(w.uid, to)
            except M.Problem as pr:
                self.app.notify(str(pr), severity="warning")
                return
            self.renamed = None
            self.app.notify(f"{w.name} deleted (not saved yet: F10).", timeout=5)
            self.refresh_view()
            self.app.refresh_state()
        self.app.push_screen(DeleteDialog(w.name, self.windows_of(w.uid), others, after), done)

    def action_move(self, step: int) -> None:
        if self.mode != "view" or self.picked is None:
            return
        self.session.move(self.picked, step)
        self.refresh_view()
        self.app.refresh_state()

    def on_toggle_changed(self, e: Toggle.Changed) -> None:
        if e.control.id == "ws-enabled":
            e.stop()
            self.session.set_enabled(e.value)
            self.draw_page()
            self.app.refresh_state()


# ---- 2 · Apps -------------------------------------------------------------------------------------------

class AppsView(Vertical):
    """2 · Apps: the apps on no workspace on the left, the workspaces on the right (one open at a
    time), >> and << between them (Javier's layout, D-3: "perfect")."""

    FORGE_HINTS = [("Space", "tick"), (">", "send"), ("<", "back"), ("a / u", "select / deselect all"),
                   ("Tab", "next"), ("F10", "save"), MENU_HINT]
    BINDINGS = [Binding("greater_than_sign", "send", show=False), Binding("less_than_sign", "back", show=False),
                Binding("a", "all(True)", show=False), Binding("u", "all(False)", show=False)]

    def __init__(self, session: M.Session, installed: dict[str, dict], **kw) -> None:
        super().__init__(**kw)
        self.session, self.installed = session, installed
        self.open_uid: int | None = None
        self.shown_uids: list[int] = []

    def compose(self) -> ComposeResult:
        # One header row across both sides, so the two tables start on the same line and end on the
        # same line (Javier's first run, 2026-10-09: "both tables should be at the same height")
        with Horizontal(id="wf-apps-head"):
            with Vertical(id="wf-pool-box", classes="wf-side"):
                yield Static("", id="wf-pool-title")
                cats = sorted({v["category"] for v in self.installed.values()})
                with Horizontal(classes="wf-filters"):
                    yield Input(placeholder="Find", id="pool-find")
                    yield Select([("All categories", "All")] + [(c, c) for c in cats], value="All",
                                 allow_blank=False, id="pool-cat")
                with Horizontal(classes="wf-buttons"):
                    yield Button("Select All (a)", id="pool-all")
                    yield Button("Deselect All (u)", id="pool-none")
            yield Static("", id="wf-mid-head")
            with Vertical(id="wf-right-head", classes="wf-side"):
                yield Static("[$forge-accent b]Workspaces[/]  [$forge-muted]open one to see its apps[/]")
                yield Static("\n[$forge-muted]When one of these apps opens, your screens go with it to its "
                             "workspace, except in the first 30 seconds after login.[/]")
        with Horizontal(id="wf-apps-body"):
            yield TickTable(id="wf-pool")
            with Vertical(id="wf-mid"):
                yield Button(">>", id="send", variant="primary")
                yield Static("send")
                yield Button("<<", id="back")
                yield Static("back")
            yield VerticalScroll(id="wf-right")

    def on_mount(self) -> None:
        self.refresh_view()

    def row(self, app_id: str) -> tuple[str, str, str]:
        v = self.installed.get(app_id)
        return (app_id, v["name"], v["category"]) if v else (app_id, app_id, "not installed")

    def pool_rows(self) -> list[tuple[str, str, str]]:
        p = self.session.pending
        listed = {a for w in p.workspaces for a in w.apps}
        find = self.query_one("#pool-find", Input).value.strip().lower()
        cat = self.query_one("#pool-cat", Select).value
        rows = [self.row(a) for a in self.installed if a not in listed]
        if find:
            rows = [r for r in rows if find in r[1].lower() or find in r[0].lower()]
        if cat not in ("All", Select.NULL, None):
            rows = [r for r in rows if r[2] == cat]
        return rows

    def refresh_pool(self) -> None:
        rows = self.pool_rows()
        total = sum(1 for a in self.installed if self.session.pending.where(a) is None)
        self.query_one("#wf-pool-title", Static).update(
            f"[$forge-accent b]Apps on no workspace[/]  [$forge-muted]{len(rows)} of {total} · they open where "
            "you are[/]")
        self.query_one("#wf-pool", TickTable).fill(rows)

    def refresh_view(self) -> None:
        self.refresh_pool()
        uids = [w.uid for w in self.session.pending.workspaces]
        if uids != self.shown_uids or not self.query(".wf-col"):
            self.run_worker(self._rebuild_right(), exclusive=True, group="wf-right")
        else:
            self._refresh_right()

    async def _rebuild_right(self) -> None:
        """The workspaces, rebuilt whole when they change (ids are reused; the old ones go first)."""
        right = self.query_one("#wf-right", VerticalScroll)
        await right.remove_children()
        p = self.session.pending
        if self.open_uid is not None and not p.has(self.open_uid):
            self.open_uid = None
        widgets = []
        for i, w in enumerate(p.workspaces, 1):
            table = TickTable(id=f"wt-{w.uid}", classes="wf-ws-table")
            col = Collapsible(Horizontal(Button("Select All (a)", id=f"wsall-{w.uid}"),
                                         Button("Deselect All (u)", id=f"wsnone-{w.uid}"), classes="wf-buttons"),
                              table, title=self._title(i, w), collapsed=w.uid != self.open_uid,
                              id=f"col-{w.uid}", classes="wf-col")
            widgets.append(col)
        await right.mount(*widgets)
        self.shown_uids = [w.uid for w in p.workspaces]
        self._refresh_right()

    def _title(self, i: int, w: M.Workspace) -> str:
        n = len(w.apps)
        return f"{i}  {w.name}   ({n} app{'s' if n != 1 else ''})"

    def _refresh_right(self) -> None:
        p = self.session.pending
        for i, w in enumerate(p.workspaces, 1):
            try:
                col = self.query_one(f"#col-{w.uid}", Collapsible)
                table = self.query_one(f"#wt-{w.uid}", TickTable)
            except Exception:
                continue
            col.title = self._title(i, w)
            table.fill([self.row(a) for a in w.apps])

    def on_collapsible_expanded(self, e: Collapsible.Expanded) -> None:
        """One open at a time: opening one closes the one before (D-3)."""
        uid = int((e.collapsible.id or "col-0").split("-", 1)[1])
        self.open_uid = uid
        for col in self.query(".wf-col"):
            if col is not e.collapsible:
                col.collapsed = True

    def on_collapsible_collapsed(self, e: Collapsible.Collapsed) -> None:
        if e.collapsible.id == f"col-{self.open_uid}":
            self.open_uid = None

    def on_input_changed(self, e: Input.Changed) -> None:
        if e.input.id == "pool-find":
            self.refresh_pool()

    def on_select_changed(self, e: Select.Changed) -> None:
        if e.select.id == "pool-cat":
            self.refresh_pool()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        bid = e.button.id or ""
        if bid == "send":
            self.action_send()
        elif bid == "back":
            self.action_back()
        elif bid == "pool-all":
            self.query_one("#wf-pool", TickTable).select_all()
        elif bid == "pool-none":
            self.query_one("#wf-pool", TickTable).deselect_all()
        elif bid.startswith(("wsall-", "wsnone-")):
            kind, uid = bid.split("-", 1)
            t = self.query_one(f"#wt-{uid}", TickTable)
            t.select_all() if kind == "wsall" else t.deselect_all()
        else:
            return
        e.stop()

    def _left_has_focus(self) -> bool:
        f = self.app.focused
        return f is not None and any(self.query_one(s) in f.ancestors_with_self for s in ("#wf-pool-box", "#wf-pool"))

    def action_all(self, value: bool) -> None:
        if self._left_has_focus():
            t = self.query_one("#wf-pool", TickTable)
        elif self.open_uid is not None:
            t = self.query_one(f"#wt-{self.open_uid}", TickTable)
        else:
            return
        t.select_all() if value else t.deselect_all()

    def action_send(self) -> None:
        if self.open_uid is None:
            self.app.notify("Open a workspace on the right first: the ticked apps go into the open one.",
                            severity="warning", timeout=5)
            return
        pool = self.query_one("#wf-pool", TickTable)
        ids = [a for a in pool.shown_ids() if a in pool.ticked]
        if not ids:
            self.app.notify("Tick some apps on the left first (Space).", timeout=4)
            return
        self.session.assign(ids, self.open_uid)
        pool.ticked -= set(ids)
        self.refresh_pool()
        self._refresh_right()
        self.app.refresh_state()

    def action_back(self) -> None:
        if self.open_uid is None:
            self.app.notify("Open a workspace on the right, tick its apps, then << sends them back.", timeout=5)
            return
        t = self.query_one(f"#wt-{self.open_uid}", TickTable)
        ids = [a for a in t.shown_ids() if a in t.ticked]
        if not ids:
            self.app.notify("Tick some of this workspace's apps first (Space).", timeout=4)
            return
        self.session.unassign(ids, self.open_uid)
        t.ticked -= set(ids)
        self.refresh_pool()
        self._refresh_right()
        self.app.refresh_state()


# ---- 3 · Sharing ---------------------------------------------------------------------------------------

class ShareCell(Static, can_focus=True):
    """One switch of the grid: ○ Own / ● Shared (Javier, D-4). Space, Enter or a click flips it."""

    class Changed(Message):
        def __init__(self, cell: "ShareCell") -> None:
            super().__init__()
            self.cell = cell

    def __init__(self, output: str, uid: int, value: bool, **kw) -> None:
        super().__init__("", **kw)
        # (not `screen`: Textual uses that name on every widget)
        self.output, self.uid, self.value = output, uid, value

    def on_mount(self) -> None:
        self.draw()

    def draw(self) -> None:
        self.update("[$forge-ok b]● Shared[/]" if self.value else "[$forge-muted]○ Own[/]")

    def flip(self) -> None:
        self.value = not self.value
        self.draw()
        self.post_message(self.Changed(self))

    def on_key(self, e) -> None:
        if e.key in ("space", "enter"):
            e.stop()
            self.flip()

    def on_click(self) -> None:
        self.flip()


class SharingView(VerticalScroll):
    """3 · Sharing: workspaces down, screens across, a switch in each cell, Save at the bottom."""

    FORGE_HINTS = [("← → ↑ ↓", "pick a cell"), ("Space", "Own / Shared"), ("F10", "save"),
                   ("Esc", "undo"), MENU_HINT]
    BINDINGS = [Binding("escape", "undo", show=False)]

    def __init__(self, session: M.Session, **kw) -> None:
        super().__init__(**kw)
        self.session = session
        self.shown: tuple = ()

    def compose(self) -> ComposeResult:
        yield Static("[$forge-accent b]Which screens keep the same apps across workspaces[/]\n"
                     "[$forge-muted]Switch a screen to Shared in the workspaces that should keep the same apps on "
                     "it: whatever is on that screen stays put when you switch between them, while the other "
                     "screens change. One cell alone shares nothing: it takes two or more in a column.[/]")
        yield Grid(id="wf-share-grid")
        yield Static("", id="wf-share-note")
        with Horizontal(classes="wf-buttons"):
            yield Button("Save (F10)", id="share-save", variant="primary")
            yield Button("Undo Changes (Esc)", id="share-undo")

    def on_mount(self) -> None:
        self.refresh_view()

    def refresh_view(self) -> None:
        p = self.session.pending
        key = (tuple((w.uid, w.name) for w in p.workspaces), tuple(p.screens),
               tuple(sorted((s, tuple(sorted(g))) for s, g in p.shared.items())))
        if key == self.shown and self.query(ShareCell):
            self._note()
            return
        self.shown = key
        self.run_worker(self._rebuild(), exclusive=True, group="wf-share")

    async def _rebuild(self) -> None:
        p = self.session.pending
        grid = self.query_one("#wf-share-grid", Grid)
        await grid.remove_children()
        grid.styles.grid_size_columns = len(p.screens) + 1
        grid.styles.grid_columns = "22 " + " ".join(["24"] * len(p.screens))
        cells = [Static("")] + [Static(escape(self.app.screen_label(s)), classes="wf-share-head")
                                for s in p.screens]
        for i, w in enumerate(p.workspaces, 1):
            cells.append(Static(f"{i}  {escape(w.name)}"))
            cells += [ShareCell(s, w.uid, w.uid in p.shared.get(s, set()), id=f"sc-{w.uid}-{j}")
                      for j, s in enumerate(p.screens)]
        grid.styles.height = len(p.workspaces) + 1
        await grid.mount(*cells)
        self._note()

    def _note(self) -> None:
        p = self.session.pending
        lone = [self.app.screen_label(s) for s in p.screens if len(p.shared.get(s, ())) == 1]
        extra = [f"{self.app.screen_label(s)} has {n} shared groups in the file; workspaceForge shows the first, "
                 "and saving keeps only that one" for s, n in self.session.saved.extra_share_groups.items()]
        lines = [f"[$forge-warn]{escape(x)}[/]" for x in extra]
        if lone:
            lines.append(f"[$forge-muted]Only one cell is Shared on {escape(', '.join(lone))}: that shares nothing "
                         "until a second one joins it.[/]")
        if not any(len(g) > 1 for g in p.shared.values()):
            lines.append("[$forge-muted]Nothing is shared now: every screen changes with the workspace.[/]")
        self.query_one("#wf-share-note", Static).update("\n".join(lines))

    def on_share_cell_changed(self, e: ShareCell.Changed) -> None:
        e.stop()
        self.session.set_shared(e.cell.output, e.cell.uid, e.cell.value)
        self.shown = ()                          # the grid is current; only the note and the bar change
        self.shown = (tuple((w.uid, w.name) for w in self.session.pending.workspaces),
                      tuple(self.session.pending.screens),
                      tuple(sorted((s, tuple(sorted(g))) for s, g in self.session.pending.shared.items())))
        self._note()
        self.app.refresh_state()

    def on_key(self, e) -> None:
        """Arrow keys move between the switches, like a grid."""
        f = self.app.focused
        if not isinstance(f, ShareCell) or e.key not in ("left", "right", "up", "down"):
            return
        p = self.session.pending
        uids = [w.uid for w in p.workspaces]
        r, c = uids.index(f.uid), p.screens.index(f.output)
        r += {"up": -1, "down": 1}.get(e.key, 0)
        c += {"left": -1, "right": 1}.get(e.key, 0)
        if 0 <= r < len(uids) and 0 <= c < len(p.screens):
            e.stop()
            self.query_one(f"#sc-{uids[r]}-{c}", ShareCell).focus()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "share-save":
            e.stop()
            self.app.action_save()
        elif e.button.id == "share-undo":
            e.stop()
            self.action_undo()

    def action_undo(self) -> None:
        """Sharing back to how it is saved (the other pages' changes stay)."""
        import copy
        self.session.pending.shared = copy.deepcopy(self.session.saved.shared)
        self.shown = ()
        self.refresh_view()
        self.app.refresh_state()


# ---- the app ----------------------------------------------------------------------------------------

class SaveFirstDialog(ForgeModal[bool | None]):
    """Before quitting with changes not saved: Yes saves, No quits without them, Esc stays."""

    BINDINGS = [Binding("escape", "stay", "", show=False), Binding("y", "yes", "", show=False),
                Binding("n", "no", "", show=False)]

    def __init__(self, n: int) -> None:
        super().__init__()
        self._n = n

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel"):
            yield Static("Save your changes before quitting?", classes="forge-panel-title")
            yield Notice(f"{self._n} change{'s are' if self._n != 1 else ' is'} not saved yet",
                         ["Yes saves them (with the review first).", "No quits; your workspaces stay as they are."],
                         level="warn")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Yes, Save (y)", id="q-yes", variant="primary")
                yield Button("No, Quit (n)", id="q-no")
                yield Button("Stay (Esc)", id="q-stay")

    def on_mount(self) -> None:
        self.query_one("#q-yes", Button).focus()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        self.dismiss({"q-yes": True, "q-no": False}.get(e.button.id))

    def action_yes(self) -> None:
        self.dismiss(True)

    def action_no(self) -> None:
        self.dismiss(False)

    def action_stay(self) -> None:
        self.dismiss(None)


class WorkspaceForgeApp(ForgeApp):
    APP_NAME = f"workspaceForge {__version__} · workspaces across your screens"
    SHOW_HINT_BAR = True
    SHOW_CHANGES_BAR = True
    CSS = WF_CSS
    LICENSE_NOTICE = GPL3_NOTICE
    MENU = [
        {"id": "workspaces", "title": "Workspaces", "kind": "section"},
        {"id": "apps", "title": "Apps", "kind": "section"},
        {"id": "help", "title": "Help", "kind": "menu", "items": [
            ("Manual", "m", "manual"), ("Keys", "k", "shortcuts"), ("License", "l", "license"),
            ("About", "a", "about")]},
        {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"},
    ]
    SHORTCUTS = [
        ("1-3, Ctrl+letter", "go to a menu entry: 1 Workspaces · 2 Apps · 3 Help"),
        ("↑ ↓", "pick a workspace (Workspaces) · move in a table (Apps)"),
        ("n · e · d", "new · edit · delete a workspace (Workspaces)"),
        ("+ · -", "move the picked workspace up · down: its Win number changes"),
        ("Space", "tick an app (Apps)"),
        ("> · <", "send the ticked apps to the open workspace · back to the list (Apps)"),
        ("a · u", "select all · deselect all, only the rows showing (Apps)"),
        ("Tab / Shift+Tab", "next / previous field, table or button"),
        ("F10", "save, with a review first"),
        ("Esc", "cancel a new name or an edit · close a window"),
        ("M", "the manual"),
        ("?", "this list"),
        ("Q or Ctrl+Q", "quit; asks to save anything not saved (not inside hypeForge Settings)"),
    ]
    HINTS = [MENU_HINT, ("F10", "save"), ("?", "all keys")]
    BINDINGS = [
        Binding("f10", "save", show=False, priority=True),
        Binding("question_mark", "act('shortcuts')", show=False),
        Binding("m", "act('manual')", show=False),
        Binding("q", "act('quit')", show=False),
    ]

    def __init__(self, session: M.Session | None = None, *, live: Live | None = None,
                 installed: dict[str, dict] | None = None, screen_names: dict[str, str] | None = None,
                 **kw) -> None:
        self.session = session or M.Session.load()
        self.live = live or Live()
        self.installed = installed if installed is not None else A.installed()
        self.app_names = {k: v["name"] for k, v in self.installed.items()}
        self.screen_names = screen_names if screen_names is not None else displayforge_names()
        self.ABOUT = {
            "name": "workspaceForge", "version": __version__,
            "tagline": "Your workspaces: names and order, the apps that open on each, and sharing.",
            "description": "Part of the Forge Suite for KognogOS. hypeForge's Workspaces applet does the work; "
                           "workspaceForge edits its settings.",
            "authors": "jetomev (Javier) · Claude (Anthropic), co-developer",
            "license": "GPL-3.0-or-later",
            "links": [("Code", "https://github.com/jetomev/forge-suite/tree/main/workspaceforge")],
        }
        super().__init__(**kw)

    def screen_label(self, screen: str) -> str:
        return screen_label(screen, self.screen_names)

    def compose_sections(self) -> ComposeResult:
        yield WorkspacesView(self.session, self.live, id="sec-workspaces")
        yield AppsView(self.session, self.installed, id="sec-apps")
        # Sharing is off the menu for now (Javier, 2026-10-09, D-7: "have to think better about this
        # section"); SharingView stays below for when it comes back. Saving keeps the file's sharing.

    def on_mount(self) -> None:
        super().on_mount()
        self.refresh_state()

    def on_action(self, action_id: str) -> None:
        if action_id == "manual":
            pages = load_pages(MANUAL_DIR) if os.path.isdir(MANUAL_DIR) else []
            if not pages:
                self.notify("The manual isn't installed.", severity="warning")
                return
            self.show_manual("workspaceForge manual", pages)

    def on_section_shown(self, section_id: str) -> None:
        ws = self.query_one(WorkspacesView)
        if section_id != "workspaces" and ws.renamed:
            ws.renamed = None                    # the rename note is not kept (D-4)
        if section_id == "workspaces":
            ws.refresh_view()
            self.call_after_refresh(self.query_one("#wf-ws-list").focus)
        elif section_id == "apps":
            self.query_one(AppsView).refresh_view()
            self.call_after_refresh(self.query_one("#wf-pool").focus)

    def refresh_state(self) -> None:
        n = self.session.change_count
        user = os.environ.get("USER", "")
        self.set_title_status(f"{user} · " + (f"{n} change{'s' if n != 1 else ''} waiting" if n
                                              else "nothing changed yet"))
        if n:
            self.changes_bar.show(f"{n} change{'s' if n != 1 else ''} not saved yet", "changed",
                                  [("Save Changes (F10)", "wf-save", True), ("Discard Changes", "wf-discard", False)])
        else:
            self.changes_bar.hide()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "wf-save":
            self.action_save()
        elif e.button.id == "wf-discard":
            self.session.discard()
            self.query_one(WorkspacesView).renamed = None
            self.query_one(WorkspacesView).refresh_view()
            self.query_one(AppsView).refresh_view()
            self.refresh_state()
            self.notify("Changes discarded. Nothing was changed.")

    # -- save ----------------------------------------------------------------------------------------------
    @work(exclusive=True, group="wf-save")
    async def action_save(self) -> None:
        await self._save()

    async def _save(self) -> bool:
        se = self.session
        rows = se.changes(self.app_names, self.screen_names)
        if not rows:
            self.notify("Nothing to save: no changes.")
            return False
        path = str(se.path).replace(os.path.expanduser("~"), "~")
        moves = se.window_moves()
        steps = ["A backup of the file is made first (the last 20 are kept)"]
        if moves:
            steps.append("Open windows go with their workspace; a deleted one's windows go where you chose")
        steps.append("The Workspaces helper reads it at once: no logout")
        choice = await self.push_screen_wait(ReviewDialog(
            "Save these workspace settings?", [ChangeGroup("Your workspaces", path, rows)], steps=steps,
            buttons=[("Save (Enter)", "save", True)]))
        if choice is None:
            return False
        if moves and self.live.here:
            self.live.run([c for c, _ in moves])
        try:
            backup = se.write()
        except OSError as e:
            self.notify(f"{e.strerror or e}. Nothing was written.", title="Not saved", severity="error")
            return False
        reloaded = self.live.reload_applet()
        se.saved_now()
        ws = self.query_one(WorkspacesView)
        ws.renamed = None
        ws.picked = se.pending.workspaces[0].uid if se.pending.workspaces and (
            ws.picked is None or not se.pending.has(ws.picked)) else ws.picked
        ws.refresh_view()
        self.query_one(AppsView).refresh_view()
        self.refresh_state()
        self.notify(f"Saved to {path}" + (" (old one backed up)" if backup else "") +
                    (". Your workspaces changed at once." if reloaded else
                     ". The Workspaces helper isn't running: it takes effect at your next login."),
                    title="Saved", timeout=7)
        return True

    def before_quit(self) -> bool:
        n = self.session.change_count
        if not n:
            return True
        self.push_screen(SaveFirstDialog(n), self._after_quit_choice)
        return False

    def _after_quit_choice(self, choice: bool | None) -> None:
        if choice is None:
            return
        if choice is False:
            self.exit()
            return
        self.save_then_quit()

    @work(exclusive=True, group="wf-quit")
    async def save_then_quit(self) -> None:
        if await self._save():
            self.exit()
        else:
            self.notify("Not saved, so workspaceForge stays open.", timeout=6)


def needs(*, environ=None, swaymsg: str = "swaymsg") -> list:
    """What workspaceForge needs: a Sway session for the windows to follow their workspace and the
    changes to happen at once. Without one it can still edit the settings for the next login."""
    return [sway_session("Open windows follow their workspace, and changes happen at once, through Sway.",
                         "Continue to edit the settings anyway: they take effect at your next Sway login.",
                         optional=True, environ=environ, swaymsg=swaymsg)]


def main(*, ask=None) -> int:
    """2 = could not start here (the start-up screen was shown and closed); 0 = ran."""
    if not start_check("workspaceForge", needs(), ask=ask):
        return 2
    WorkspaceForgeApp().run()
    return 0
