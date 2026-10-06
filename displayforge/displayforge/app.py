"""displayForge — the app frame, on forgekit (the alacrittyForge pattern).

Design: docs/design/v0.1.0-screens.html, approved by Javier on 5 Oct 2026 (D-2). The screens
read and change only the Session; trying a change goes through trial.py (with the independent
safety timer), saving through saving.py (with a backup first).
"""

from __future__ import annotations

import os

from rich.markup import escape
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, OptionList, Select, Static
from textual.widgets.option_list import Option

from forgekit import (
    FORGE_CSS, GPL3_NOTICE, ChangeGroup, Choices, ForgeApp, ForgeModal, Notice, NumberPresets,
    ReviewDialog, SettingRow, Toggle,
)

from . import __version__, brightness as B, drawing, saving as V, screens as S, trial as T
from .session import Session, rotation_words

DF_CSS = FORGE_CSS + """
#df-drawing { height: auto; border: round $forge-border; border-title-color: $forge-accent;
              border-title-style: bold; padding: 0 1; margin: 0 2 1 0; }
#df-overview-row { height: auto; }
.df-box { height: auto; width: 1fr; border: round $forge-border; border-title-color: $forge-accent;
          border-title-style: bold; padding: 0 1; margin: 0 2 0 0; }
.df-ok { border: round $forge-ok; border-title-color: $forge-ok; }
.df-warn { border: round $forge-warn; border-title-color: $forge-warn; }
#df-list { width: 26; height: 1fr; border: none; border-right: solid $forge-border; background: $forge-bg; padding: 1 1 0 0; }
#df-form { width: 1fr; height: 1fr; padding: 0 0 0 2; }
#df-form-title { height: auto; margin: 0 0 1 0; }
#df-keep-body { height: auto; padding: 1 2; }
.df-actions { height: auto; padding: 1 0 0 0; }
.df-actions Button { margin: 0 2 0 0; }
"""


def _hz_text(m: S.Mode) -> str:
    return f"{m.hz} Hz"


class KeepDialog(ForgeModal[bool]):
    """"Keep these settings?" with a countdown that goes back by itself (the design)."""

    BINDINGS = [Binding("escape", "back", "", show=False), Binding("enter", "keep", "", show=False)]

    def __init__(self, what: str, seconds: int = T.SECONDS) -> None:
        super().__init__()
        self._what, self._left = what, seconds

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel"):
            yield Static("Keep these settings?", classes="forge-panel-title")
            yield Static("", id="df-keep-body")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Keep it", id="keep", variant="primary")
                yield Button("Go back now", id="back")

    def on_mount(self) -> None:
        self._draw()
        self.query_one("#keep", Button).focus()
        self.set_interval(1, self._tick)

    def _draw(self) -> None:
        self.query_one("#df-keep-body", Static).update(
            f"{escape(self._what)}\n\n[$forge-warn b]Going back in {self._left} seconds[/], unless you keep it.\n"
            f"[$forge-muted]So a screen that went black fixes itself.[/]")

    def _tick(self) -> None:
        self._left -= 1
        if self._left <= 0:
            self.dismiss(False)
        else:
            self._draw()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        self.dismiss(e.button.id == "keep")

    def action_keep(self) -> None:
        self.dismiss(True)

    def action_back(self) -> None:
        self.dismiss(False)


class ScreensView(VerticalScroll):
    """1 · Screens: the drawing, the picked screen, and what needs attention."""

    def __init__(self, session: Session, **kw) -> None:
        super().__init__(**kw)
        self.session = session
        self.picked = session.main

    def compose(self) -> ComposeResult:
        d = Static("", id="df-drawing")
        d.border_title = "Your screens"
        yield d
        with Horizontal(id="df-overview-row"):
            yield Static("", id="df-picked", classes="df-box")
            yield Static("", id="df-state", classes="df-box")

    def on_mount(self) -> None:
        self.refresh_view()

    def labels(self) -> dict[str, list[str]]:
        se = self.session
        out = {}
        for s in se.pending:
            n = se.number(s.name)
            name = se.remembered["names"].get(s.name, s.name)
            mode = [s.mode.size, _hz_text(s.mode)] if s.mode else ["off"]
            out[s.name] = [("★ " if s.name == se.main else "") + str(n), name] + mode
        return out

    def refresh_view(self) -> None:
        se = self.session
        self.query_one("#df-drawing", Static).update("\n".join(drawing.draw(se.pending, self.labels(), self.picked)))
        s = se.screen(self.picked)
        box = self.query_one("#df-picked", Static)
        box.border_title = se.label(s.name) + (" · the main one" if s.name == se.main else "")
        lines = [f"[$forge-muted]Shows     [/] " + (f"{s.mode.size} at {_hz_text(s.mode)}" if s.on and s.mode else "switched off"),
                 f"[$forge-muted]Size      [/] {s.scale:.0%} · {rotation_words(s.rotation)} rotation",
                 f"[$forge-muted]Model     [/] {escape(s.make)} {escape(s.model)}",
                 f"[$forge-muted]Workspaces[/] screen {se.number(s.name)} of {len(se.pending)}"]
        box.update("\n".join(lines))
        state = self.query_one("#df-state", Static)
        issues = se.problems()
        if se.saved_differs():
            issues.append("Your saved settings differ from what is on screen.")
        state.remove_class("df-ok", "df-warn")
        if issues:
            state.add_class("df-warn")
            state.border_title = "Needs attention"
            state.update("\n".join(f"[$forge-warn b]![/] {escape(i)}" for i in issues))
        else:
            state.add_class("df-ok")
            state.border_title = "All good"
            on = sum(1 for x in se.pending if x.on)
            state.update(f"[$forge-ok b]✓[/] [b]{on} screen{'s' if on != 1 else ''} on, nothing overlaps.[/]\n"
                         "  [$forge-muted]← → pick a screen · Enter its settings[/]")

    def pick(self, step: int) -> None:
        on = sorted(self.session.pending, key=lambda s: (s.y, s.x))
        names = [s.name for s in on]
        i = names.index(self.picked) if self.picked in names else 0
        self.picked = names[(i + step) % len(names)]
        self.refresh_view()


class SettingsView(Horizontal):
    """2 · Settings: the screens on the left, the picked one's settings on the right."""

    def __init__(self, session: Session, **kw) -> None:
        super().__init__(**kw)
        self.session = session
        self.picked = session.main

    def compose(self) -> ComposeResult:
        yield OptionList(id="df-list")
        yield VerticalScroll(id="df-form")

    def on_mount(self) -> None:
        self.fill_list()
        self.build_form()

    def fill_list(self) -> None:
        ol = self.query_one("#df-list", OptionList)
        ol.clear_options()
        for s in self.session.pending:
            ol.add_option(Option(self.session.label(s.name), id=s.name))
        names = [s.name for s in self.session.pending]
        if self.picked in names:
            ol.highlighted = names.index(self.picked)

    def on_option_list_option_highlighted(self, e: OptionList.OptionHighlighted) -> None:
        if e.option.id and e.option.id != self.picked:
            self.picked = e.option.id
            self.build_form()

    def build_form(self) -> None:
        """Rebuild the form; the old controls are removed completely before the new ones arrive
        (they share ids — found by the in-memory walk-through: DuplicateIds)."""
        self.run_worker(self._rebuild(), exclusive=True, group="df-form")

    async def _rebuild(self) -> None:
        se = self.session
        s, was = se.screen(self.picked), se.screen(self.picked, pending=False)
        form = self.query_one("#df-form", VerticalScroll)
        await form.remove_children()
        title = Static(f"[$forge-accent b]{escape(se.label(s.name))}[/]  [$forge-muted]{escape(s.make)} "
                       f"{escape(s.model)} · {se.place_words(s.name)}"
                       f"{' · the main one' if s.name == se.main else ''}[/]", id="df-form-title")
        rows = [title,
                SettingRow("On", Toggle(s.on, id="f-on"), setting="on",
                           note="switch this screen off (others stay on)")]
        if s.on and s.mode:
            sizes = s.sizes()
            rows.append(SettingRow("Resolution", Select([(f"{w} × {h}", f"{w}x{h}") for w, h in sizes],
                                                         value=f"{s.mode.width}x{s.mode.height}", allow_blank=False,
                                                         id="f-size"),
                                   setting="size", note=f"what the screen offers: {len(sizes)} sizes"))
            rates = s.rates(s.mode.width, s.mode.height)[:5]
            rows.append(SettingRow("Refresh rate", Choices([(str(m.hz), f"{m.hz} Hz") for m in rates],
                                                            str(s.mode.hz), id="f-rate"),
                                   setting="rate", note=f"at {s.mode.size}"))
            rows.append(SettingRow("Size of things", NumberPresets(round(s.scale * 100),
                                                                    [(f"{round(x * 100)}", round(x * 100)) for x in S.SCALES],
                                                                    unit="%", minimum=50, maximum=300, id="f-scale"),
                                   setting="scale", note="80–90 %: older (X11) apps look slightly blurry"))
            rows.append(SettingRow("Rotation", Choices([(r, rotation_words(r)) for r in S.ROTATIONS],
                                                        s.rotation if s.rotation in S.ROTATIONS else "normal",
                                                        id="f-rot"), setting="rotation"))
            if s.can_adaptive_sync:
                rows.append(SettingRow("Smooth motion", Toggle(s.adaptive_sync, id="f-sync"), setting="sync",
                                       note="adaptive sync (FreeSync); some screens flicker with it"))
            rows.append(SettingRow("HDR", Toggle(s.hdr, id="f-hdr"), setting="hdr") if s.can_hdr else
                        Static("[b]HDR[/]              [$forge-muted]not supported by this screen[/]"))
        await form.mount(*rows)
        self._marks(s, was)

    def _marks(self, s: S.Screen, was: S.Screen) -> None:
        for row in self.query(SettingRow):
            k = row.setting
            old = {"on": "on" if was.on else "off",
                   "size": was.mode.size if was.mode else "", "rate": _hz_text(was.mode) if was.mode else "",
                   "scale": f"{was.scale:.0%}", "rotation": rotation_words(was.rotation),
                   "sync": "on" if was.adaptive_sync else "off", "hdr": "on" if was.hdr else "off"}.get(k)
            now = {"on": "on" if s.on else "off",
                   "size": s.mode.size if s.mode else "", "rate": _hz_text(s.mode) if s.mode else "",
                   "scale": f"{s.scale:.0%}", "rotation": rotation_words(s.rotation),
                   "sync": "on" if s.adaptive_sync else "off", "hdr": "on" if s.hdr else "off"}.get(k)
            if old is not None and old != now:
                row.mark_changed(old)

    # -- the controls change the session -----------------------------------------------------
    def on_toggle_changed(self, e: Toggle.Changed) -> None:
        field = {"f-on": "on", "f-sync": "adaptive_sync", "f-hdr": "hdr"}.get(e.control.id or "")
        if field == "on":
            s = self.session.screen(self.picked)
            live = self.session.screen(self.picked, pending=False)
            self.session.change(self.picked, on=e.value, mode=(s.mode or live.mode or (s.modes[0] if s.modes else None)))
        elif field:
            self.session.change(self.picked, **{field: e.value})
        self._changed()

    def on_select_changed(self, e: Select.Changed) -> None:
        if (e.select.id or "") != "f-size" or e.value is Select.BLANK:
            return
        s = self.session.screen(self.picked)
        w, h = (int(v) for v in str(e.value).split("x"))
        if s.mode and (w, h) == (s.mode.width, s.mode.height):
            return
        rates = s.rates(w, h)
        keep = next((m for m in rates if s.mode and m.hz == s.mode.hz), rates[0] if rates else s.mode)
        self.session.change(self.picked, mode=keep)
        self._changed()

    def on_number_presets_changed(self, e: NumberPresets.Changed) -> None:
        if (e.control.id or "") == "f-scale":
            value = round(float(e.value) / 100, 2)
            if value != self.session.screen(self.picked).scale:
                self.session.change(self.picked, scale=value)
                self._changed()

    def on_choices_changed(self, e: Choices.Changed) -> None:
        s = self.session.screen(self.picked)
        cid = e.control.id or ""
        if cid == "f-rate" and s.mode:
            m = next(m for m in s.rates(s.mode.width, s.mode.height) if str(m.hz) == e.value)
            self.session.change(self.picked, mode=m)
        elif cid == "f-rot":
            self.session.change(self.picked, rotation=e.value)
        self._changed()

    def _changed(self) -> None:
        self.build_form()
        self.app.refresh_state()


class LaterView(Vertical):
    def __init__(self, what: str, **kw) -> None:
        super().__init__(**kw)
        self._what = what

    def compose(self) -> ComposeResult:
        yield Notice(self._what, ["This screen is built next, as drawn in the approved design."], level="info")


class DisplayForgeApp(ForgeApp):
    APP_NAME = f"displayForge {__version__} · screen settings"
    SHOW_HINT_BAR = True
    SHOW_CHANGES_BAR = True
    CSS = DF_CSS
    LICENSE_NOTICE = GPL3_NOTICE
    MENU = [
        {"id": "screens", "title": "Screens", "kind": "section"},
        {"id": "settings", "title": "Settings", "kind": "section", "acc": "e"},
        {"id": "arrange", "title": "Arrange", "kind": "section"},
        {"id": "brightness", "title": "Brightness", "kind": "section"},
        {"id": "identify", "title": "Identify", "kind": "section"},
        {"id": "help", "title": "Help", "kind": "menu", "items": [
            ("Keys", "k", "shortcuts"), ("License", "l", "license"), ("About", "a", "about")]},
        {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"},
    ]
    SHORTCUTS = [
        ("1-5, Ctrl+letter", "go to a screen (the underlined letter)"),
        ("← →", "pick a screen (Screens)"),
        ("Tab / Shift+Tab", "next / previous field or button"),
        ("Enter / Space", "choose / flip a switch"),
        ("F9", "try the changes live, with the countdown"),
        ("F10", "save, with a review first"),
        ("Esc", "close a window · go back now (countdown)"),
        ("?", "this list"),
        ("Q or Ctrl+Q", "quit (asks first if something isn't saved)"),
    ]
    HINTS = [("← →", "pick a screen"), ("1-5", "screens"), ("F9", "try"), ("F10", "save"), ("?", "all keys")]
    BINDINGS = [
        Binding("1", "go('screens')", show=False), Binding("2", "go('settings')", show=False),
        Binding("3", "go('arrange')", show=False), Binding("4", "go('brightness')", show=False),
        Binding("5", "go('identify')", show=False),
        Binding("left", "pick(-1)", show=False), Binding("right", "pick(1)", show=False),
        Binding("f9", "try_it", show=False, priority=True),
        Binding("f10", "save", show=False, priority=True),
        Binding("question_mark", "act('shortcuts')", show=False),
        Binding("q", "act('quit')", show=False),
    ]

    def __init__(self, session: Session | None = None, *, swaymsg: str = "swaymsg", **kw) -> None:
        self.session = session or Session.load()
        self.swaymsg = swaymsg
        self.ABOUT = {
            "name": "displayForge", "version": __version__,
            "tagline": "Your screens: arrange, resolution, refresh rate, size, rotation, brightness",
            "description": "Part of the Forge Suite for KognogOS.",
            "authors": "jetomev (Javier) · Claude (Anthropic), co-developer",
            "license": "GPL-3.0-or-later",
            "links": [("Code", "https://github.com/jetomev/forge-suite/tree/main/displayforge")],
        }
        super().__init__(**kw)

    def compose_sections(self) -> ComposeResult:
        yield ScreensView(self.session, id="sec-screens")
        yield SettingsView(self.session, id="sec-settings")
        yield LaterView("Arrange", id="sec-arrange")
        yield LaterView("Brightness", id="sec-brightness")
        yield LaterView("Identify", id="sec-identify")

    def on_mount(self) -> None:
        super().on_mount()
        user = os.environ.get("USER", "")
        self.set_title_status(f"{user} · changes apply live")
        self.refresh_state()

    def action_go(self, section: str) -> None:
        self._switch_section(section)

    def action_pick(self, step: int) -> None:
        if self.current_section == "screens":
            self.query_one(ScreensView).pick(step)

    @property
    def current_section(self) -> str:
        for sid in ("screens", "settings", "arrange", "brightness", "identify"):
            w = self.query_one(f"#sec-{sid}")
            if w.display:
                return sid
        return "screens"

    def refresh_state(self) -> None:
        n = self.session.change_count
        if n:
            self.changes_bar.show(f"{n} change{'s' if n != 1 else ''} not tried yet", "changed",
                                  [("Try it…  F9", "df-try", True), ("Discard", "df-discard", False)])
        else:
            self.changes_bar.hide()
        self.query_one(ScreensView).refresh_view()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "df-try":
            self.action_try_it()
        elif e.button.id == "df-discard":
            self.session.discard()
            self.query_one(SettingsView).build_form()
            self.refresh_state()
            self.notify("Changes discarded. Nothing was changed on your screens.")

    # -- try, keep or go back --------------------------------------------------------------------
    @work(exclusive=True, group="df-try")
    async def action_try_it(self) -> None:
        se = self.session
        if not se.change_count:
            self.notify("Nothing to try: no changes.")
            return
        problems = se.problems()
        if problems:
            self.notify("\n".join(problems), title="Can't try this", severity="warning", timeout=8)
            return
        what = "; ".join(f"{n}: {new}" for n, _o, new in se.changes())
        trial = T.Trial(se.live, se.pending, swaymsg=self.swaymsg)
        if not trial.start():
            self.notify("Sway did not accept that. Nothing changed.", title="Not tried", severity="error")
            return
        keep = await self.push_screen_wait(KeepDialog(what))
        if keep:
            trial.keep()
            se.tried()
            self.notify("Kept. Press F10 to save it for the next login.", title="Kept", timeout=6)
            self.refresh_state()
            self.changes_bar.show("Kept on screen · not saved yet", "changed", [("Save…  F10", "df-save", True)])
        else:
            trial.revert_now()
            self.notify("Back to how it was.")
            self.refresh_state()

    # -- save ------------------------------------------------------------------------------------
    @work(exclusive=True, group="df-save")
    async def action_save(self) -> None:
        se = self.session
        if se.change_count:
            self.notify("Try the changes first (F9): only what you kept on screen is saved.", timeout=6)
            return
        path = str(V.OUTPUTS).replace(os.path.expanduser("~"), "~")
        rows = se.to_save()
        if not rows and V.OUTPUTS.exists() and not se.saved_differs():
            self.notify("Nothing to save: what is on screen is already saved.")
            return
        if not rows:
            rows = [("All screens", "not saved yet", "as they are now")]
        choice = await self.push_screen_wait(ReviewDialog(
            "Save these screen settings?", [ChangeGroup("Your screens", path, rows)],
            steps=["A backup of the old file is made first (the last 20 are kept)",
                   "Sway reads it at every login",
                   "Brightness is not part of this: the screens keep it themselves"],
            buttons=[("Save", "save", True)]))
        if choice is None:
            return
        try:
            _, backup = V.save(se.live)
        except OSError as e:
            self.notify(f"{e.strerror or e}. Nothing was written.", title="Not saved", severity="error")
            return
        se.saved()
        self.changes_bar.hide()
        self.refresh_state()
        self.notify(f"Saved to {path}" + (" (old one backed up)." if backup else "."), title="Saved", timeout=6)

    def before_quit(self) -> bool:
        if self.session.change_count:
            self.notify("You have changes not tried yet. Discard them first, or press Q again to quit.",
                        severity="warning")
            if getattr(self, "_quit_warned", False):
                return True
            self._quit_warned = True
            return False
        return True


def main() -> int:
    DisplayForgeApp().run()
    return 0
