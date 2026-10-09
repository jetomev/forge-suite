"""defaultappsForge — the app frame, on forgekit (the workspaceForge / nightForge pattern).

Design: docs/design/v0.1.0-screens.html, approved by Javier on 9 Oct 2026 (D-4): fourteen default
apps with drop-downs under Defaults / Selection; File Types as two tables with >> / << like
workspaceForge's Apps page, aligned from the top; Save a pop-up review.
"""

from __future__ import annotations

import os

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.coordinate import Coordinate
from textual.widgets import Button, Collapsible, DataTable, Input, Select, Static

from forgekit import (
    FORGE_CSS, GPL3_NOTICE, MENU_HINT, ChangeGroup, ForgeApp, ForgeModal, ReviewDialog, load_pages, start_check,
)

from . import __version__, system as S
from .model import Session
from .roles import BY_KEY, FILE_TYPES, ROLES

MANUAL_DIR = os.path.join(os.path.dirname(__file__), "manual")

DA_CSS = FORGE_CSS + """
#da-titles { height: 1; margin: 1 0 1 0; }
#da-titles Static { text-style: bold underline; }
#da-titles #da-t1 { margin: 0 0 0 5; width: 22; }
#da-titles #da-t2 { width: auto; }
.da-row { height: 1; margin: 0 0 1 0; }
.da-name { width: 27; padding: 0 0 0 3; }
.da-row Select { width: 42; height: 1; }
.da-row SelectCurrent { border: none; height: 1; padding: 0 1; background: $forge-surface; }
.da-row Select:focus > SelectCurrent { border: none; background: $forge-focus-bg; }
.da-row Select > SelectOverlay { width: 42; }
.wf-buttons { height: auto; padding: 0 0 1 0; }
.wf-buttons Button { margin: 0 1 0 0; }
#da-head { height: auto; padding: 1 0 0 0; }
.da-side { width: 1fr; height: auto; }
#da-pool-box { padding: 0 1 0 0; }
#da-right-head { padding: 0 0 0 1; }
#da-mid-head { width: 10; }
#da-body { height: 1fr; }
#da-pool { width: 1fr; height: 1fr; }
#da-mid { width: 10; height: 1fr; align: center middle; }
#da-mid Button { width: 8; min-width: 8; margin: 1 0 0 0; }
#da-mid Static { width: 8; text-align: center; color: $forge-muted; }
#da-right { width: 1fr; height: 1fr; padding: 0 0 0 1; }
.da-role-table { height: auto; max-height: 14; }
.da-filters { height: auto; padding: 0 0 1 0; }
.da-filters Input { width: 1fr; }
"""


# ---- a table of file types with ticks (like workspaceForge's) ----------------------------------------

class TickTable(DataTable):
    BINDINGS = [Binding("space", "tick", show=False)]

    def __init__(self, **kw) -> None:
        super().__init__(zebra_stripes=True, cursor_type="row", **kw)
        self.rows_data: list[tuple[str, str]] = []           # (extension, what)
        self.ticked: set[str] = set()
        self.sort_by, self.reverse = "ext", False

    def on_mount(self) -> None:
        self.draw()

    def fill(self, rows: list[tuple[str, str]]) -> None:
        self.rows_data = rows
        self.ticked &= {r[0] for r in rows}
        self.draw()

    def draw(self) -> None:
        keep = self.current_id()
        self.clear(columns=True)
        arrow = " ▼" if self.reverse else " ▲"
        self.add_column("", key="tick", width=3)
        self.add_column("Type" + (arrow if self.sort_by == "ext" else ""), key="ext")
        self.add_column("What" + (arrow if self.sort_by == "what" else ""), key="what")
        col = 0 if self.sort_by == "ext" else 1
        for ext, what in sorted(self.rows_data, key=lambda r: (r[col].lower(), r[0]), reverse=self.reverse):
            self.add_row(Text("[x]" if ext in self.ticked else "[ ]"), ext, what, key=ext)
        ids = self.shown_ids()
        if keep in ids:
            self.move_cursor(row=ids.index(keep))

    def shown_ids(self) -> list[str]:
        return [str(rk.value) for rk in self.rows]

    def current_id(self) -> str | None:
        if not self.row_count:
            return None
        try:
            return str(self.coordinate_to_cell_key(Coordinate(self.cursor_row, 0)).row_key.value)
        except Exception:
            return None

    def set_tick(self, ext: str, value: bool) -> None:
        (self.ticked.add if value else self.ticked.discard)(ext)
        if ext in self.shown_ids():
            self.update_cell(ext, "tick", Text("[x]" if value else "[ ]"))

    def action_tick(self) -> None:
        e = self.current_id()
        if e:
            self.set_tick(e, e not in self.ticked)

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
        for e in self.shown_ids():
            self.set_tick(e, True)

    def deselect_all(self) -> None:
        for e in self.shown_ids():
            self.set_tick(e, False)


def rows_for(exts: list[str]) -> list[tuple[str, str]]:
    return [(e, FILE_TYPES[e][0]) for e in exts if e in FILE_TYPES]


# ---- 1 · Default Apps ----------------------------------------------------------------------------------

class DefaultsView(VerticalScroll):
    FORGE_HINTS = [("Tab", "next"), ("Enter", "open the list"), ("F10", "save"), MENU_HINT]

    def __init__(self, session: Session, **kw) -> None:
        super().__init__(**kw)
        self.session = session

    def compose(self) -> ComposeResult:
        with Horizontal(id="da-titles"):
            yield Static("Defaults", id="da-t1")
            yield Static("Selection", id="da-t2")
        for r in ROLES:
            cands = self.session.candidates(r.key)
            options = [(self.session.label(a, cands), a.id) for a in cands]
            now = self.session.apps_now[r.key]
            blank_words = "— none installed —" if not options else "— not chosen —"
            with Horizontal(classes="da-row"):
                yield Static(f"• {r.title}", classes="da-name")
                yield Select(options, value=now if now in {o[1] for o in options} else Select.NULL,
                             allow_blank=True, prompt=blank_words, id=f"da-{r.key}", disabled=not options)

    def on_select_changed(self, e: Select.Changed) -> None:
        key = (e.select.id or "").removeprefix("da-")
        if key in BY_KEY:
            e.stop()
            value = None if e.value is Select.NULL else str(e.value)
            self.session.choose(key, value)
            self.app.refresh_state()


# ---- 2 · File Types: two tables, >> / << (D-2), aligned from the top (D-3) ------------------------------

class TypesView(Vertical):
    FORGE_HINTS = [("Space", "tick"), (">", "assign"), ("<", "clear"), ("a / u", "select / deselect all"),
                   ("Tab", "next"), ("F10", "save"), MENU_HINT]
    BINDINGS = [Binding("greater_than_sign", "assign", show=False), Binding("less_than_sign", "clear", show=False),
                Binding("a", "all(True)", show=False), Binding("u", "all(False)", show=False)]

    def __init__(self, session: Session, **kw) -> None:
        super().__init__(**kw)
        self.session = session
        self.open_key: str | None = None
        self.built = False

    def compose(self) -> ComposeResult:
        with Horizontal(id="da-head"):
            with Vertical(id="da-pool-box", classes="da-side"):
                yield Static("", id="da-pool-title")
                with Horizontal(classes="da-filters"):
                    yield Input(placeholder="Find", id="da-find")
                with Horizontal(classes="wf-buttons"):
                    yield Button("Select All (a)", id="da-pool-all")
                    yield Button("Deselect All (u)", id="da-pool-none")
            yield Static("", id="da-mid-head")
            with Vertical(id="da-right-head", classes="da-side"):
                yield Static("[$forge-accent b]Default apps[/]  [$forge-muted]open one to see its file types[/]")
                yield Static("\n[$forge-muted]A file type assigned to a default app opens in the app you picked "
                             "for it on Default Apps.[/]")
        with Horizontal(id="da-body"):
            yield TickTable(id="da-pool")
            with Vertical(id="da-mid"):
                yield Button(">>", id="da-assign", variant="primary")
                yield Static("assign")
                yield Button("<<", id="da-clear")
                yield Static("clear")
            yield VerticalScroll(id="da-right")

    def on_mount(self) -> None:
        self.refresh_view()

    def refresh_pool(self) -> None:
        find = self.query_one("#da-find", Input).value.strip().lower()
        exts = self.session.unassigned()
        rows = [r for r in rows_for(exts) if not find or find in r[0] or find in r[1].lower()]
        self.query_one("#da-pool-title", Static).update(
            f"[$forge-accent b]File types on no default app[/]  [$forge-muted]{len(rows)} of {len(exts)}[/]")
        self.query_one("#da-pool", TickTable).fill(rows)

    def refresh_view(self) -> None:
        self.refresh_pool()
        if not self.built:
            self.run_worker(self._build_right(), exclusive=True, group="da-right")
        else:
            self._refresh_right()

    async def _build_right(self) -> None:
        right = self.query_one("#da-right", VerticalScroll)
        await right.remove_children()
        widgets = []
        for r in ROLES:
            if r.key == "terminal":
                continue                                 # a terminal opens no files
            widgets.append(Collapsible(
                Horizontal(Button("Select All (a)", id=f"da-all-{r.key}"),
                           Button("Deselect All (u)", id=f"da-none-{r.key}"), classes="wf-buttons"),
                TickTable(id=f"da-t-{r.key}", classes="da-role-table"),
                title=self._title(r.key), collapsed=True, id=f"da-c-{r.key}", classes="da-col"))
        await right.mount(*widgets)
        self.built = True
        self._refresh_right()

    def _title(self, key: str) -> str:
        n = len(self.session.pools[key])
        app = self.session.name(self.session.apps_now[key])
        return f"{BY_KEY[key].title} · {n} type{'s' if n != 1 else ''}"

    def _refresh_right(self) -> None:
        for r in ROLES:
            if r.key == "terminal":
                continue
            try:
                self.query_one(f"#da-c-{r.key}", Collapsible).title = self._title(r.key)
                self.query_one(f"#da-t-{r.key}", TickTable).fill(rows_for(self.session.pools[r.key]))
            except Exception:
                pass

    def on_collapsible_expanded(self, e: Collapsible.Expanded) -> None:
        self.open_key = (e.collapsible.id or "").removeprefix("da-c-")
        for c in self.query(".da-col"):
            if c is not e.collapsible:
                c.collapsed = True

    def on_collapsible_collapsed(self, e: Collapsible.Collapsed) -> None:
        if e.collapsible.id == f"da-c-{self.open_key}":
            self.open_key = None

    def on_input_changed(self, e: Input.Changed) -> None:
        if e.input.id == "da-find":
            self.refresh_pool()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        bid = e.button.id or ""
        if bid == "da-assign":
            self.action_assign()
        elif bid == "da-clear":
            self.action_clear()
        elif bid == "da-pool-all":
            self.query_one("#da-pool", TickTable).select_all()
        elif bid == "da-pool-none":
            self.query_one("#da-pool", TickTable).deselect_all()
        elif bid.startswith(("da-all-", "da-none-")):
            key = bid.split("-", 2)[2]
            t = self.query_one(f"#da-t-{key}", TickTable)
            t.select_all() if bid.startswith("da-all-") else t.deselect_all()
        else:
            return
        e.stop()

    def _left_has_focus(self) -> bool:
        f = self.app.focused
        return f is not None and any(self.query_one(s) in f.ancestors_with_self for s in ("#da-pool-box", "#da-pool"))

    def action_all(self, value: bool) -> None:
        if self._left_has_focus():
            t = self.query_one("#da-pool", TickTable)
        elif self.open_key:
            t = self.query_one(f"#da-t-{self.open_key}", TickTable)
        else:
            return
        t.select_all() if value else t.deselect_all()

    def action_assign(self) -> None:
        if not self.open_key:
            self.app.notify("Open a default app on the right first: the ticked types go into the open one.",
                            severity="warning", timeout=5)
            return
        pool = self.query_one("#da-pool", TickTable)
        exts = [e for e in pool.shown_ids() if e in pool.ticked]
        if not exts:
            self.app.notify("Tick some file types on the left first (Space).", timeout=4)
            return
        self.session.assign(exts, self.open_key)
        pool.ticked -= set(exts)
        self.refresh_view()
        self.app.refresh_state()

    def action_clear(self) -> None:
        if not self.open_key:
            self.app.notify("Open a default app on the right, tick its types, then << clears them.", timeout=5)
            return
        t = self.query_one(f"#da-t-{self.open_key}", TickTable)
        exts = [e for e in t.shown_ids() if e in t.ticked]
        if not exts:
            self.app.notify("Tick some of its file types first (Space).", timeout=4)
            return
        self.session.clear(exts, self.open_key)
        t.ticked -= set(exts)
        self.refresh_view()
        self.app.refresh_state()


# ---- the app ----------------------------------------------------------------------------------------

class SaveFirstDialog(ForgeModal[bool | None]):
    BINDINGS = [Binding("escape", "stay", "", show=False), Binding("y", "yes", "", show=False),
                Binding("n", "no", "", show=False)]

    def __init__(self, n: int) -> None:
        super().__init__()
        self._n = n

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel"):
            yield Static("Save your changes before quitting?", classes="forge-panel-title")
            yield Static(f"[$forge-warn b]{self._n} change{'s are' if self._n != 1 else ' is'} not saved yet.[/]\n"
                         "Yes saves them (with the review first). No quits; nothing changes.")
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


class DefaultAppsForgeApp(ForgeApp):
    APP_NAME = f"defaultappsForge {__version__} · which app opens what"
    SHOW_HINT_BAR = True
    SHOW_CHANGES_BAR = True
    CSS = DA_CSS
    LICENSE_NOTICE = GPL3_NOTICE
    MENU = [
        {"id": "defaults", "title": "Default Apps", "kind": "section"},
        {"id": "types", "title": "File Types", "kind": "section"},
        {"id": "help", "title": "Help", "kind": "menu", "items": [
            ("Manual", "m", "manual"), ("Keys", "k", "shortcuts"), ("License", "l", "license"),
            ("About", "a", "about")]},
        {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"},
    ]
    SHORTCUTS = [
        ("1-3, Ctrl+letter", "go to a menu entry: 1 Default Apps · 2 File Types · 3 Help"),
        ("Tab / Shift+Tab", "next / previous drop-down, table or button"),
        ("Enter", "open a drop-down · pick in it"),
        ("Space", "tick a file type (File Types)"),
        ("> · <", "assign the ticked types to the open default app · clear them (File Types)"),
        ("a · u", "select all · deselect all, only the rows showing (File Types)"),
        ("F10", "save, with a review first"),
        ("Esc", "close a list or a window"),
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

    def __init__(self, session: Session | None = None, *, live: bool = True, **kw) -> None:
        self.session = session or Session()
        self.live = live
        self.ABOUT = {
            "name": "defaultappsForge", "version": __version__,
            "tagline": "Which app opens what: links, folders, text, PDFs, pictures, music, video, and more.",
            "description": "Part of the Forge Suite for KognogOS. It writes the standard ~/.config/mimeapps.list "
                           "that every desktop and app reads.",
            "authors": "jetomev (Javier) · Claude (Anthropic), co-developer",
            "license": "GPL-3.0-or-later",
            "links": [("Code", "https://github.com/jetomev/forge-suite/tree/main/defaultappsforge")],
        }
        super().__init__(**kw)

    def compose_sections(self) -> ComposeResult:
        yield DefaultsView(self.session, id="sec-defaults")
        yield TypesView(self.session, id="sec-types")

    def on_mount(self) -> None:
        super().on_mount()
        self.refresh_state()

    def on_action(self, action_id: str) -> None:
        if action_id == "manual":
            pages = load_pages(MANUAL_DIR) if os.path.isdir(MANUAL_DIR) else []
            if not pages:
                self.notify("The manual isn't installed.", severity="warning")
                return
            self.show_manual("defaultappsForge manual", pages)

    def on_section_shown(self, section_id: str) -> None:
        # the keyboard moves into the page shown (its keys, like > and <, work at once)
        if section_id == "types":
            self.query_one(TypesView).refresh_view()
            self.call_after_refresh(self.query_one("#da-pool").focus)
        else:
            self.call_after_refresh(self.query_one("#da-web").focus)

    def refresh_state(self) -> None:
        n = self.session.change_count
        self.set_title_status(f"{os.environ.get('USER', '')} · " + (f"{n} change{'s' if n != 1 else ''} waiting" if n
                                                                    else "nothing changed yet"))
        if n:
            self.changes_bar.show(f"{n} change{'s' if n != 1 else ''} not saved yet", "changed",
                                  [("Save Changes (F10)", "da-save", True), ("Discard Changes", "da-discard", False)])
        else:
            self.changes_bar.hide()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "da-save":
            self.action_save()
        elif e.button.id == "da-discard":
            self.session.discard()
            self.query_one(DefaultsView).refresh(recompose=True)
            self.query_one(TypesView).refresh_view()
            self.refresh_state()
            self.notify("Changes discarded. Nothing was changed.")

    @work(exclusive=True, group="da-save")
    async def action_save(self) -> None:
        await self._save()

    async def _save(self) -> bool:
        se = self.session
        rows = se.changes()
        if not se.change_count:
            self.notify("Nothing to save: no changes.")
            return False
        path = str(S.MIMEAPPS).replace(os.path.expanduser("~"), "~")
        steps = ["A backup of the file is made first (the last 20 are kept)",
                 "At once: the next file or link you open uses it"]
        need_terminal_exec = se.terminal_changed and se.apps_now["terminal"] and not S.terminal_exec_installed()
        if need_terminal_exec:
            steps.insert(0, "Your terminal choice needs xdg-terminal-exec (small, official repository): "
                            "nog installs it, asking for your password")
        choice = await self.push_screen_wait(ReviewDialog(
            "Save your default apps?", [ChangeGroup("Default apps", path, rows)], steps=steps,
            buttons=[("Save (Enter)", "save", True)]))
        if choice is None:
            return False
        if need_terminal_exec and self.live:
            ok = await self._install_terminal_exec()
            if not ok:
                se.apps_now["terminal"] = se.saved_apps["terminal"]
                self.notify("xdg-terminal-exec wasn't installed, so the terminal choice waits; the rest is saved.",
                            severity="warning", timeout=8)
        try:
            result = se.save() if self.live else {"backup": None, "tidied": [], "terminal": None}
        except OSError as e:
            self.notify(f"{e}. Nothing was written.", title="Not saved", severity="error")
            return False
        if not self.live:
            se.saved_apps = dict(se.apps_now)
            import copy
            se.saved_pools = copy.deepcopy(se.pools)
        self.refresh_state()
        self.query_one(TypesView).refresh_view()
        self.notify(f"Saved to {path}" + (" (old one backed up)" if result["backup"] else "") +
                    ". The next file or link you open uses it.", title="Saved", timeout=6)
        return True

    async def _install_terminal_exec(self) -> bool:
        import asyncio
        fut = asyncio.get_running_loop().create_future()
        await self.run_in_app("Installing xdg-terminal-exec", ["nog", "install", "xdg-terminal-exec"],
                              callback=lambda status: fut.done() or fut.set_result(status))
        await fut
        return S.terminal_exec_installed()

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

    @work(exclusive=True, group="da-quit")
    async def save_then_quit(self) -> None:
        if await self._save():
            self.exit()
        else:
            self.notify("Not saved, so defaultappsForge stays open.", timeout=6)


def needs() -> list:
    return []           # any Linux, any desktop or none, any terminal: nothing to check


def main(*, ask=None) -> int:
    if not start_check("defaultappsForge", needs(), ask=ask):
        return 2
    DefaultAppsForgeApp().run()
    return 0
