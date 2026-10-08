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
    FORGE_CSS, GPL3_NOTICE, MENU_HINT, ChangeGroup, Choices, ForgeApp, ForgeModal, ManualScreen, Notice, NumberPresets,
    ReviewDialog, SettingRow, Toggle, load_pages, program, start_check, sway_session,
)

from . import __version__, brightness as B, drawing, saving as V, screens as S, trial as T
from .session import Session, rotation_words

MANUAL_DIR = os.path.join(os.path.dirname(__file__), "manual")

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
                yield Button("Keep It (Enter)", id="keep", variant="primary")
                yield Button("Go Back Now (Esc)", id="back")

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



class ApplyDialog(ForgeModal[bool | None]):
    """Before quitting with something not applied (1.1.0, Javier): Yes applies it, No quits
    without it, Esc stays. True / False / None."""

    BINDINGS = [Binding("escape", "stay", "", show=False), Binding("y", "yes", "", show=False),
                Binding("n", "no", "", show=False)]

    def __init__(self, heading: str, lines: list[str]) -> None:
        super().__init__()
        self._heading, self._lines = heading, lines

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel"):
            yield Static("Apply your changes before quitting?", classes="forge-panel-title")
            yield Notice(self._heading, self._lines, level="warn", id="df-apply-msg")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Yes, Apply (y)", id="apply-yes", variant="primary")
                yield Button("No, Quit (n)", id="apply-no")
                yield Button("Stay (Esc)", id="apply-stay")

    def on_mount(self) -> None:
        self.query_one("#apply-yes", Button).focus()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        self.dismiss({"apply-yes": True, "apply-no": False}.get(e.button.id))

    def action_yes(self) -> None:
        self.dismiss(True)

    def action_no(self) -> None:
        self.dismiss(False)

    def action_stay(self) -> None:
        self.dismiss(None)

class ScreensView(VerticalScroll):
    """1 · Screens: the drawing, the picked screen, and what needs attention."""

    FORGE_HINTS = [("← →", "pick a screen"), MENU_HINT, ("?", "all keys")]

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

    # 1.1.0 (Javier, 2026-10-08): Try and Save belong to the pages that change something
    FORGE_HINTS = [("Tab", "next"), ("F9", "try"), ("F10", "save"), MENU_HINT, ("?", "all keys")]

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


class ArrangeView(VerticalScroll):
    """3 · Arrange: the layout; arrows move the picked screen (the others make room)."""

    FORGE_HINTS = [("← → ↑ ↓", "move"), ("Tab", "next screen"), ("F9", "try"), ("F10", "save"), MENU_HINT,
                   ("?", "all keys")]

    BINDINGS = [Binding("left", "move('left')", show=False), Binding("right", "move('right')", show=False),
                Binding("up", "move('above')", show=False), Binding("down", "move('below')", show=False),
                Binding("tab", "next_screen", show=False)]
    can_focus = True

    def __init__(self, session: Session, **kw) -> None:
        super().__init__(**kw)
        self.session = session
        self.picked = next((s.name for s in session.pending if s.name != session.main), session.main)

    def compose(self) -> ComposeResult:
        yield Static("[$forge-muted]Move the picked screen with the arrow keys; the others make room. "
                     "Edges snap together. Tab picks the next screen.[/]")
        d = Static("", id="df-arr-drawing")
        d.border_title = "Your screens"
        yield d
        yield Static("", id="df-arr-picked")
        yield SettingRow("Put it", Choices([("left", "left of"), ("right", "right of"), ("above", "above"),
                                            ("below", "below")], "right", id="a-where"), setting="where")
        yield SettingRow("Of", Select([], allow_blank=True, id="a-of"), setting="of")
        yield SettingRow("Line up", Choices([("start", "tops / left edges"), ("centre", "centres"),
                                             ("end", "bottoms / right edges")], "start", id="a-align"),
                         setting="align")
        yield Static("[$forge-muted]Moving a screen does not change its number: workspaces still start "
                     "on the main one (★).[/]")

    def on_mount(self) -> None:
        self.refresh_view()

    def refresh_view(self) -> None:
        se = self.session
        labels = self.app.query_one(ScreensView).labels()
        self.query_one("#df-arr-drawing", Static).update("\n".join(drawing.draw(se.pending, labels, self.picked)))
        s = se.screen(self.picked)
        self.query_one("#df-arr-picked", Static).update(
            f"[$forge-accent b]{escape(se.label(s.name))}[/]  [$forge-muted]now: [/]{se.place_words(s.name)}"
            f"   [$forge-muted]position [/]{s.x}, {s.y}")
        of = self.query_one("#a-of", Select)
        others = [(se.label(o.name), o.name) for o in se.pending if o.name != self.picked and o.on]
        keep = of.value if of.value in [v for _, v in others] else (
            se.main if any(v == se.main for _, v in others) else (others[0][1] if others else Select.BLANK))
        with of.prevent(Select.Changed):
            of.set_options(others)
            of.value = keep

    def _apply(self, where: str, of: str | None = None) -> None:
        se = self.session
        if not of:
            v = self.query_one("#a-of", Select).value
            of = None if v is Select.BLANK else str(v)
        if not of or of == self.picked:
            return
        se.arrange(self.picked, where, of, self.query_one("#a-align", Choices).value)
        self.refresh_view()
        self.app.refresh_state()

    def action_move(self, where: str) -> None:
        """Arrows: next to the neighbour in that direction (or the chosen screen)."""
        se = self.session
        me = se.screen(self.picked)
        others = [o for o in se.pending if o.on and o.name != me.name]
        if not others:
            return
        if where in ("left", "right"):
            row = sorted([o for o in others if abs(o.y - me.y) < max(1, me.extent[1])] or others, key=lambda o: o.x)
            ahead = [o for o in row if (o.x < me.x if where == "left" else o.x > me.x)]
            if not ahead:
                return
            ref = ahead[-1] if where == "left" else ahead[0]
        else:
            ref = min(others, key=lambda o: abs(o.x - me.x))
        self._apply(where, ref.name)

    def action_next_screen(self) -> None:
        names = [s.name for s in sorted(self.session.pending, key=lambda s: (s.y, s.x)) if s.on]
        if names:
            self.picked = names[(names.index(self.picked) + 1) % len(names)] if self.picked in names else names[0]
            self.refresh_view()

    def on_choices_changed(self, e: Choices.Changed) -> None:
        if (e.control.id or "") == "a-where":
            self._apply(e.value)


class BrightnessView(VerticalScroll):
    """4 · Brightness: changes at once, in tens; the screens keep it (nothing to save)."""

    def __init__(self, session: Session, ddcutil: str = "ddcutil", **kw) -> None:
        super().__init__(**kw)
        self.session, self.ddcutil = session, ddcutil

    def compose(self) -> ComposeResult:
        yield Static("[$forge-muted]Brightness changes at once and is kept by the screen itself — nothing to save.[/]")
        yield Vertical(id="df-bright-rows")
        yield SettingRow("All screens", NumberPresets(70, [(str(v), v) for v in B.STEPS], unit="%",
                                                      minimum=10, maximum=100, id="b-all"),
                         setting="all", note="the same on every screen")
        yield Static("[$forge-muted]Night light (warmer colours in the evening) comes in a later version.[/]")

    def on_mount(self) -> None:
        self.refresh_view()

    @work(exclusive=True, group="df-bright")
    async def refresh_view(self) -> None:
        box = self.query_one("#df-bright-rows", Vertical)
        await box.remove_children()
        bus = self.session.remembered["bus"]
        if not bus:
            await box.mount(Notice("Which control is which screen?",
                                   ["Your screens look identical to the computer, so brightness works for all "
                                    "screens together until Identify (5) has asked you which is which."],
                                   level="info"))
            return
        rows, readings = [], []
        for s in sorted(self.session.live, key=lambda s: (s.y, s.x)):
            if s.name in bus:
                now = B.get(bus[s.name], self.ddcutil)
                if now is not None:
                    readings.append(now)
                rows.append(SettingRow(self.session.label(s.name) + f" · {self.session.place_words(s.name, False)}",
                                       NumberPresets(B.tens(now or 70), [(str(v), v) for v in B.STEPS],
                                                     unit="%", minimum=10, maximum=100, id=f"b-{s.name}"),
                                       setting=s.name))
        await box.mount(*rows)
        if readings:
            self.query_one("#b-all", NumberPresets).value = B.tens(round(sum(readings) / len(readings)))
            self.query_one("#b-all", NumberPresets).refresh(recompose=True)

    def on_number_presets_changed(self, e: NumberPresets.Changed) -> None:
        cid = e.control.id or ""
        value = B.tens(int(e.value))
        bus = self.session.remembered["bus"]
        if cid == "b-all":
            targets = list(bus.values()) or B.buses(self.ddcutil)
        elif cid.startswith("b-") and cid[2:] in bus:
            targets = [bus[cid[2:]]]
        else:
            return
        self.set_bright(targets, value)

    @work(group="df-bright-set")
    async def set_bright(self, targets: list[int], value: int) -> None:
        import asyncio
        ok = all(await asyncio.gather(*[asyncio.to_thread(B.set_, b, value, self.ddcutil) for b in targets]))
        if not ok:
            self.app.notify("A screen did not take the new brightness.", severity="warning")


class IdentifyView(VerticalScroll):
    """5 · Identify: which brightness control is which screen (asked once), and their names."""

    def __init__(self, session: Session, ddcutil: str = "ddcutil", **kw) -> None:
        super().__init__(**kw)
        self.session, self.ddcutil = session, ddcutil
        self.todo: list[int] = []
        self.answers: dict[str, int] = {}

    def compose(self) -> ComposeResult:
        yield Static("[$forge-muted]Screens that are the same model look identical to the computer, so it "
                     "can't tell which brightness control belongs to which screen. This asks you once, and "
                     "remembers.[/]")
        yield Static("", id="df-id-step")
        yield Horizontal(id="df-id-answers", classes="df-actions")
        with Horizontal(classes="df-actions"):
            yield Button("Start", id="id-start", variant="primary")
        yield Static("\n[b]Names[/] [$forge-muted]— shown everywhere in displayForge[/]")
        yield Vertical(id="df-id-names")

    def on_mount(self) -> None:
        self.show_names()
        bus = self.session.remembered["bus"]
        self.query_one("#df-id-step", Static).update(
            "[$forge-ok]✓[/] Already done: brightness knows which screen is which. Start to ask again."
            if bus else "Press Start: one screen at a time goes dark for 3 seconds, and you say which.")

    def show_names(self) -> None:
        from textual.widgets import Input
        box = self.query_one("#df-id-names", Vertical)
        box.remove_children()
        rows = []
        for s in sorted(self.session.live, key=lambda s: (s.y, s.x)):
            rows.append(SettingRow(f"Screen {self.session.number(s.name)} · {s.name} · "
                                   f"{self.session.place_words(s.name, False)}",
                                   Input(self.session.remembered["names"].get(s.name, ""),
                                         placeholder="a name, like Main", id=f"n-{s.name}"),
                                   setting=s.name))
        box.mount(*rows)

    def on_input_submitted(self, e) -> None:
        self._set_screen_name(e.input)

    def on_input_changed(self, e) -> None:
        self._set_screen_name(e.input, save=False)

    def _set_screen_name(self, inp, save: bool = True) -> None:
        # (not `_name`: Textual uses that on every widget — it crashed on the first letter typed)
        cid = inp.id or ""
        if not cid.startswith("n-"):
            return
        name, value = cid[2:], inp.value.strip()
        names = self.session.remembered["names"]
        if value:
            names[name] = value
        else:
            names.pop(name, None)
        if save:
            B.save(self.session.remembered)
            self.app.notify(f"Named {name}: {value or '(no name)'}")
            self.app.query_one(ScreensView).refresh_view()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        bid = e.button.id or ""
        if bid == "id-start":
            e.stop()
            self.start()
        elif bid.startswith("id-is-"):
            e.stop()
            self.answer(bid[6:])

    @work(exclusive=True, group="df-identify")
    async def start(self) -> None:
        import asyncio
        self.todo = await asyncio.to_thread(B.buses, self.ddcutil)
        self.answers = {}
        if not self.todo:
            self.query_one("#df-id-step", Static).update("[$forge-warn]No screen answered on its control "
                                                        "channel (DDC/CI may be off in the screen's own menu).[/]")
            return
        await self.dim_next()

    async def dim_next(self) -> None:
        import asyncio
        box = self.query_one("#df-id-answers", Horizontal)
        # No answer buttons while a screen is dark (F-2: a click then cancelled the restore)
        await box.remove_children()
        if not self.todo:
            self.session.remembered["bus"] = dict(self.answers)
            B.save(self.session.remembered)
            self.query_one("#df-id-step", Static).update("[$forge-ok]✓ Done.[/] Brightness now knows which "
                                                        "screen is which (Brightness, 4).")
            return
        bus = self.todo[0]
        done = len(self.answers) + 1
        total = done + len(self.todo) - 1
        step = self.query_one("#df-id-step", Static)
        step.update(f"[b]{done} of {total}[/] · one screen goes [b]dark for 3 seconds[/] now… watch")
        # The dim and its restore run in their own process: nothing here can skip the restore
        proc = B.dim(bus, 3, ddcutil=self.ddcutil)
        back = await asyncio.to_thread(proc.wait)
        if back != 0:
            self.app.notify("A screen did not report its brightness back. Set it in Brightness (4).",
                            severity="warning", timeout=8)
        step.update(f"[b]{done} of {total}[/] · Which screen went dark?")
        # the screens where they physically are now — that is what the person sees go dark
        buttons = [Button(f"{self.session.place_words(s.name, False).capitalize()} "
                          f"({self.session.label(s.name).split(' · ')[0]})",
                          id=f"id-is-{s.name}") for s in sorted(self.session.live, key=lambda s: (s.y, s.x))
                   if s.name not in self.answers]
        buttons += [Button("None of Them", id="id-is-none"), Button("Dim It Again", id="id-is-again")]
        await box.mount(*buttons)

    @work(exclusive=True, group="df-identify")
    async def answer(self, name: str) -> None:
        bus = self.todo[0]
        if name == "again":
            await self.dim_next()
            return
        self.todo.pop(0)
        if name != "none":
            self.answers[name] = bus
        await self.dim_next()


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
            ("Manual", "m", "manual"), ("Keys", "k", "shortcuts"), ("License", "l", "license"),
            ("About", "a", "about")]},
        {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"},
    ]
    SHORTCUTS = [
        ("1-6, Ctrl+letter", "go to a menu entry: 1 Screens … 6 Help, or Ctrl + its underlined letter"),
        ("← →", "pick a screen (Screens)"),
        ("Tab / Shift+Tab", "next / previous field or button"),
        ("Enter / Space", "choose / flip a switch"),
        ("F9", "try the changes live, with the countdown (Settings, Arrange)"),
        ("F10", "save, with a review first (Settings, Arrange)"),
        ("Esc", "close a window · go back now (countdown)"),
        ("M", "the manual"),
        ("?", "this list"),
        ("Q or Ctrl+Q", "quit; asks to apply anything not saved (not inside hypeForge Settings)"),
    ]
    HINTS = [MENU_HINT, ("?", "all keys")]
    CHANGING = ("settings", "arrange")      # the pages where Try and Save apply (1.1.0)
    BINDINGS = [
        Binding("left", "pick(-1)", show=False), Binding("right", "pick(1)", show=False),
        Binding("f9", "try_it", show=False, priority=True),
        Binding("f10", "save", show=False, priority=True),
        Binding("question_mark", "act('shortcuts')", show=False),
        Binding("m", "act('manual')", show=False),
        Binding("q", "act('quit')", show=False),
    ]

    def __init__(self, session: Session | None = None, *, swaymsg: str = "swaymsg", ddcutil: str = "ddcutil",
                 **kw) -> None:
        self.session = session or Session.load()
        self.swaymsg, self.ddcutil = swaymsg, ddcutil
        self.ABOUT = {
            "name": "displayForge", "version": __version__,
            "tagline": "Your screens: arrange, resolution, refresh rate, size, rotation, brightness. Sway only.",
            "description": "Part of the Forge Suite for KognogOS.",
            "authors": "jetomev (Javier) · Claude (Anthropic), co-developer",
            "license": "GPL-3.0-or-later",
            "links": [("Code", "https://github.com/jetomev/forge-suite/tree/main/displayforge")],
        }
        super().__init__(**kw)

    def compose_sections(self) -> ComposeResult:
        yield ScreensView(self.session, id="sec-screens")
        yield SettingsView(self.session, id="sec-settings")
        yield ArrangeView(self.session, id="sec-arrange")
        yield BrightnessView(self.session, self.ddcutil, id="sec-brightness")
        yield IdentifyView(self.session, self.ddcutil, id="sec-identify")

    def on_mount(self) -> None:
        super().on_mount()
        user = os.environ.get("USER", "")
        self.set_title_status(f"{user} · changes apply live")
        self.refresh_state()

    def action_go(self, section: str) -> None:
        self._switch_section(section)

    def on_action(self, action_id: str) -> None:
        if action_id == "manual":
            pages = load_pages(MANUAL_DIR) if os.path.isdir(MANUAL_DIR) else []
            if not pages:
                self.notify("The manual isn't installed.", severity="warning")
                return
            self.push_screen(ManualScreen("displayForge manual", pages))

    def on_section_shown(self, section_id: str) -> None:
        self.refresh_bar(section_id)
        if section_id == "arrange":
            self.query_one(ArrangeView).refresh_view()
            self.query_one(ArrangeView).focus()
        elif section_id == "brightness":
            self.query_one(BrightnessView).refresh_view()
        elif section_id == "screens":
            self.query_one(ScreensView).refresh_view()

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

    @property
    def kept_not_saved(self) -> bool:
        """Changes tried and kept on screen, but not saved for the next login."""
        return bool(self.session.to_save())

    def refresh_bar(self, section: str | None = None) -> None:
        """The changes bar (1.1.0, Javier): Try and Save on the pages that change something;
        anywhere else, only a reminder of what is waiting and where."""
        section = section or self.current_section
        n = self.session.change_count
        here = section in self.CHANGING
        if n and here:
            self.changes_bar.show(f"{n} change{'s' if n != 1 else ''} not tried yet", "changed",
                                  [("Try It (F9)", "df-try", True), ("Discard", "df-discard", False)])
        elif n:
            self.changes_bar.show(f"{n} change{'s' if n != 1 else ''} not tried yet · "
                                  "finish them in Settings (2) or Arrange (3)", "changed")
        elif self.kept_not_saved and here:
            self.changes_bar.show("Kept on screen · not saved yet", "changed", [("Save (F10)", "df-save", True)])
        elif self.kept_not_saved:
            self.changes_bar.show("Kept on screen · not saved yet · save it in Settings (2) or Arrange (3)",
                                  "changed")
        else:
            self.changes_bar.hide()

    def refresh_state(self) -> None:
        self.refresh_bar()
        self.query_one(ScreensView).refresh_view()
        try:
            self.query_one(ArrangeView).refresh_view()
        except Exception:
            pass

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "df-try":
            self.action_try_it()
        elif e.button.id == "df-save":           # the Save button never had a handler before 1.1.0
            self.action_save()
        elif e.button.id == "df-discard":
            self.session.discard()
            self.query_one(SettingsView).build_form()
            self.refresh_state()
            self.notify("Changes discarded. Nothing was changed on your screens.")

    # -- try, keep or go back --------------------------------------------------------------------
    @work(exclusive=True, group="df-try")
    async def action_try_it(self) -> None:
        if self.current_section not in self.CHANGING:
            self._elsewhere("try")
            return
        await self._try()

    def _elsewhere(self, what: str) -> None:
        """F9 / F10 on a page that changes nothing: a reminder, not an action."""
        if self.session.change_count or self.kept_not_saved:
            self.notify(f"Changes are {'waiting' if self.session.change_count else 'kept, not saved'}: "
                        f"{what} them in Settings (2) or Arrange (3).", timeout=6)
        else:
            self.notify("Nothing to " + what + " here: this page changes nothing to save.", timeout=4)

    async def _try(self) -> bool:
        """The countdown trial; True when the change was kept."""
        self._tried_ok = False
        se = self.session
        if not se.change_count:
            self.notify("Nothing to try: no changes.")
            return False
        problems = se.problems()
        if problems:
            self.notify("\n".join(problems), title="Can't try this", severity="warning", timeout=8)
            return False
        what = "; ".join(f"{n}: {new}" for n, _o, new in se.changes())
        trial = T.Trial(se.live, se.pending, swaymsg=self.swaymsg)
        if not trial.start():
            self.notify("Sway did not accept that. Nothing changed.", title="Not tried", severity="error")
            return False
        keep = await self.push_screen_wait(KeepDialog(what))
        if keep:
            trial.keep()
            se.tried()
            self.notify("Kept. Press F10 to save it for the next login.", title="Kept", timeout=6)
            self._tried_ok = True
            self.refresh_state()
        else:
            trial.revert_now()
            self.notify("Back to how it was.")
            self.refresh_state()
        return self._tried_ok

    # -- save ------------------------------------------------------------------------------------
    @work(exclusive=True, group="df-save")
    async def action_save(self) -> None:
        if self.current_section not in self.CHANGING:
            self._elsewhere("save")
            return
        await self._save()

    async def _save(self) -> bool:
        """The save, with its review first; True when written."""
        se = self.session
        if se.change_count:
            self.notify("Try the changes first (F9): only what you kept on screen is saved.", timeout=6)
            return False
        path = str(V.OUTPUTS).replace(os.path.expanduser("~"), "~")
        rows = se.to_save()
        if not rows and V.OUTPUTS.exists() and not se.saved_differs():
            self.notify("Nothing to save: what is on screen is already saved.")
            return False
        if not rows:
            rows = [("All screens", "not saved yet", "as they are now")]
        choice = await self.push_screen_wait(ReviewDialog(
            "Save these screen settings?", [ChangeGroup("Your screens", path, rows)],
            steps=["A backup of the old file is made first (the last 20 are kept)",
                   "Sway reads it at every login",
                   "Brightness is not part of this: the screens keep it themselves"],
            buttons=[("Save", "save", True)]))
        if choice is None:
            return False
        try:
            _, backup = V.save(se.live)
        except OSError as e:
            self.notify(f"{e.strerror or e}. Nothing was written.", title="Not saved", severity="error")
            return False
        se.saved()
        self.changes_bar.hide()
        self.refresh_state()
        self.notify(f"Saved to {path}" + (" (old one backed up)." if backup else "."), title="Saved", timeout=6)
        if not V.included(V.SWAY_CONFIG):
            self.notify("Sway doesn't read this file yet, so the screens go back at your next login. "
                        f"Add this line to {V.SWAY_CONFIG}:\ninclude ~/.config/sway/outputs",
                        title="One line missing", severity="warning", timeout=20)
        return True

    def before_quit(self) -> bool:
        """1.1.0 (Javier, 2026-10-08): anything not finished gets a proper question before quitting:
        apply it now (try with the countdown, then save) or quit without it. Esc stays."""
        se = self.session
        if not (se.change_count or self.kept_not_saved):
            return True
        if se.change_count:
            n = se.change_count
            heading = f"{n} change{'s are' if n != 1 else ' is'} not applied yet"
            lines = ["Yes tries them on your screens (with the countdown), then saves them for the next login.",
                     "No quits, and your screens stay as they are now."]
        else:
            heading = "What is on your screens is not saved"
            lines = ["Yes saves it for the next login.", "No quits; at the next login the screens go back."]
        self.push_screen(ApplyDialog(heading, lines), self._after_quit_choice)
        return False

    def _after_quit_choice(self, choice: bool | None) -> None:
        if choice is None:                       # Esc / Stay
            return
        if choice is False:
            self.exit()
            return
        self.apply_then_quit()

    @work(exclusive=True, group="df-quit")
    async def apply_then_quit(self) -> None:
        if self.session.change_count and not await self._try():
            self.notify("Not applied, so displayForge stays open.", timeout=6)
            return
        if self.kept_not_saved and not await self._save():
            self.notify("Not saved, so displayForge stays open.", timeout=6)
            return
        self.exit()


def needs(*, environ=None, swaymsg: str = "swaymsg", ddcutil: str = "ddcutil") -> list:
    """What displayForge needs to run here (1.0.1, forge-suite #32): a Sway session, full
    stop; ddcutil only for Brightness and Identify, so it is optional."""
    return [
        sway_session("displayForge sets up your screens by talking to Sway, and only Sway.",
                     "Use your desktop's own display settings; on KognogOS, log in to Sway (hypeForge).",
                     environ=environ, swaymsg=swaymsg),
        program(ddcutil, "Brightness and Identify talk to the screens through ddcutil.",
                "Install it (on KognogOS: nog install ddcutil), or continue without those two views.",
                optional=True),
    ]


def main(*, ask=None) -> int:
    """2 = could not start here (the start-up screen was shown and closed); 0 = ran."""
    if not start_check("displayForge", needs(), ask=ask):
        return 2
    DisplayForgeApp().run()
    return 0
