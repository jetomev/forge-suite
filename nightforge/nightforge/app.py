"""nightForge — the app frame, on forgekit (the displayForge / workspaceForge pattern).

Design: docs/design/v0.1.0-screens.html, approved by Javier on 9 Oct 2026 (D-3), with a tray icon
(D-4). On / off and Right now act at once (like the tray's menu); the evening warmth and the
schedule wait for Save. Preview and Save are both pop-ups (D-2).
"""

from __future__ import annotations

import copy
import os
from datetime import date, datetime, timedelta

from rich.markup import escape
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Static

from forgekit import (
    FORGE_CSS, GPL3_NOTICE, MENU_HINT, ChangeGroup, Choices, ForgeApp, ForgeModal, NumberPresets, ReviewDialog,
    SettingRow, Toggle, load_pages, program, start_check, sway_session,
)

from . import __version__, control as C
from .settings import CONFIG, DAY, STEPS, Settings, clock, describe
from .sun import sun_times

MANUAL_DIR = os.path.join(os.path.dirname(__file__), "manual")

NF_CSS = FORGE_CSS + """
#nf-now { height: auto; border: round $forge-border; border-title-color: $forge-accent; border-title-style: bold;
          padding: 0 1; margin: 1 1 1 0; }
#nf-now.-warm { border: round $forge-warn; border-title-color: $forge-warn; }
#nf-now.-off { border: round $forge-muted; border-title-color: $forge-muted; }
#nf-sun { height: auto; border: round $forge-border; border-title-color: $forge-accent; border-title-style: bold;
          padding: 0 1; margin: 1 1 1 0; }
.nf-note { color: $forge-muted; height: auto; padding: 0 0 0 20; }
.nf-buttons { height: auto; padding: 0 0 1 20; }
.nf-buttons Button { margin: 0 1 0 0; }
#nf-preview-body { height: auto; padding: 1 2; }
Input.nf-time { width: 14; }
"""


class Session:
    """What is saved and what you have changed (the warmth and the schedule)."""

    def __init__(self, settings: Settings) -> None:
        self.saved = settings
        self.pending = copy.deepcopy(settings)

    def changes(self) -> list[tuple[str, str, str]]:
        s, p = self.saved, self.pending
        rows = []
        if s.warmth != p.warmth:
            rows.append(("Evening warmth", f"{s.warmth} K", f"{p.warmth} K"))

        def when(x: Settings) -> str:
            return (f"by the sun, {x.place_words()}" if x.schedule == "sun"
                    else f"fixed times, {x.warm_from} → {x.day_from}, fade {x.fade_minutes} min")
        if when(s) != when(p):
            rows.append(("When", when(s), when(p)))
        return rows

    @property
    def change_count(self) -> int:
        return len(self.changes())


# ---- the pop-ups (D-2: Preview and Save are both pop-ups) --------------------------------------------

class PreviewDialog(ForgeModal[bool]):
    """A warmth on the screens for ten seconds; it goes back by itself. True = keep it."""

    BINDINGS = [Binding("escape", "back", "", show=False), Binding("enter", "keep", "", show=False)]
    SECONDS = 10

    def __init__(self, warmth: int) -> None:
        super().__init__()
        self._warmth, self._left = warmth, self.SECONDS

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel"):
            yield Static("Preview", classes="forge-panel-title")
            yield Static("", id="nf-preview-body")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button(f"Keep {self._warmth} (Enter)", id="keep", variant="primary")
                yield Button("Back Now (Esc)", id="back")

    def on_mount(self) -> None:
        self._draw()
        self.query_one("#keep", Button).focus()
        self.set_interval(1, self._tick)

    def _draw(self) -> None:
        self.query_one("#nf-preview-body", Static).update(
            f"Your screens are showing [b]{self._warmth} K[/] now — {describe(self._warmth)}.\n\n"
            f"[$forge-warn b]Back to how it was in {self._left} seconds.[/]")

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
                         "Yes saves them (with the review first). No quits; the night light stays as it is.")
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


# ---- 1 · Night Light ---------------------------------------------------------------------------------

class NightView(VerticalScroll):
    FORGE_HINTS = [("o", "on/off"), ("← →", "choose"), ("p", "preview"), ("F10", "save"), MENU_HINT]
    BINDINGS = [Binding("o", "toggle", show=False), Binding("p", "preview", show=False)]

    def __init__(self, session: Session, **kw) -> None:
        super().__init__(**kw)
        self.session = session

    def compose(self) -> ComposeResult:
        now = Static("", id="nf-now")
        now.border_title = "Right now"
        yield now
        p = self.session.pending
        yield SettingRow("Night light", Toggle(p.enabled, id="nf-enabled"), setting="enabled",
                         note="Off: no warm colours, now and at every login")
        yield SettingRow("Right now", Choices([("auto", "Automatic"), ("warm", "Warm Now"), ("day", "Daylight Now")],
                                              C.mode(), id="nf-mode"), setting="mode",
                         note="Warm Now / Daylight Now hold until you pick Automatic again, or log out")
        yield SettingRow("Evening warmth", NumberPresets(p.warmth, [(str(s), s) for s in STEPS], unit="K",
                                                          minimum=1000, maximum=6400, id="nf-warmth"),
                         setting="warmth",
                         note="3000 very warm · 3500 warm · 4000 gentle · 4500 light · 5000 just a touch")
        with Horizontal(classes="nf-buttons"):
            yield Button("Preview (p)", id="nf-preview")
        yield Static("[b]Daytime[/]           [$forge-muted]6500 K · the screens' own white (no change)[/]")

    def on_mount(self) -> None:
        self.refresh_view()

    def refresh_view(self) -> None:
        st = C.status(self.session.saved)
        box = self.query_one("#nf-now", Static)
        box.remove_class("-warm", "-off")
        mark = {"warm": "[$forge-warn b]☾ Warm   [/]", "day": "[$forge-ok b]☀ Daylight   [/]", "off": "[$forge-muted b]○ Off   [/]"}
        if st["state"] != "day":
            box.add_class("-" + st["state"])
        box.update(f"{mark[st['state']]}{escape(st['why'])}\n"
                   "[$forge-muted]On all your screens. Screenshots and what you share are not affected.[/]")
        self.query_one("#nf-enabled", Toggle).set_value(self.session.saved.enabled, announce=False)

    def on_toggle_changed(self, e: Toggle.Changed) -> None:
        if e.control.id == "nf-enabled":
            e.stop()
            self.app.set_enabled(e.value)

    def action_toggle(self) -> None:
        t = self.query_one("#nf-enabled", Toggle)
        t.flip()

    def on_choices_changed(self, e: Choices.Changed) -> None:
        if e.control.id == "nf-mode":
            e.stop()
            self.app.set_mode(e.value)

    def on_number_presets_changed(self, e: NumberPresets.Changed) -> None:
        if e.control.id == "nf-warmth":
            e.stop()
            self.session.pending.warmth = int(e.value)
            self.session.pending.checked()
            self.app.refresh_state()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "nf-preview":
            e.stop()
            self.action_preview()

    def action_preview(self) -> None:
        self.app.preview(self.session.pending.warmth)


# ---- 2 · Schedule ------------------------------------------------------------------------------------

class ScheduleView(VerticalScroll):
    FORGE_HINTS = [("← →", "choose"), ("Tab", "next field"), ("F10", "save"), MENU_HINT]

    def __init__(self, session: Session, **kw) -> None:
        super().__init__(**kw)
        self.session = session

    def compose(self) -> ComposeResult:
        p = self.session.pending
        yield SettingRow("When", Choices([("sun", "By the Sun at Your Place"), ("fixed", "Fixed Times")], p.schedule,
                                         id="nf-schedule"), setting="schedule")
        # stacked, like the fixed times: side by side, their boxes' bottom edges spilled onto the note
        # below (Javier's first run, 2026-10-09)
        yield SettingRow("Latitude", Input(f"{p.latitude:.2f}", id="nf-lat", classes="nf-time"), setting="lat")
        yield SettingRow("Longitude", Input(f"{p.longitude:.2f}", id="nf-lon", classes="nf-time"), setting="lon",
                         note="your place, as two numbers: one decimal is plenty (about 10 km); nothing is looked up online")
        sun = Static("", id="nf-sun")
        sun.border_title = "Your sun, worked out on this computer"
        yield sun
        yield SettingRow("Warm from", Input(p.warm_from, id="nf-warm-from", classes="nf-time"), setting="warm_from",
                         note="fixed times: when the evening starts (HH:MM)")
        yield SettingRow("Daylight from", Input(p.day_from, id="nf-day-from", classes="nf-time"), setting="day_from")
        yield SettingRow("Fade", Input(str(p.fade_minutes), id="nf-fade", classes="nf-time"), setting="fade",
                         note="minutes, so you never see it jump")
        yield Static("[$forge-muted]Fixed times are the same every day, whatever the season.[/]", classes="nf-note")

    def on_mount(self) -> None:
        self.refresh_view()

    def refresh_view(self) -> None:
        p = self.session.pending
        sun = self.query_one("#nf-sun", Static)
        today = date.today()
        rise_t, set_t = sun_times(today, p.latitude, p.longitude)
        rise_n = sun_times(today + timedelta(days=1), p.latitude, p.longitude)[0]
        june = sun_times(date(today.year, 6, 21), p.latitude, p.longitude)
        if set_t is None:
            lines = ["[$forge-warn]No sunset or sunrise at this place today (near the poles): "
                     "use Fixed Times.[/]"]
        else:
            lines = [f"[b]Today      [/]sunset [$forge-accent b]{set_t:%H:%M}   [/]·   sunrise tomorrow "
                     f"[$forge-accent b]{rise_n:%H:%M}[/]" if rise_n else "",
                     (f"[b]In June    [/]sunset {june[1]:%H:%M}   ·   sunrise {june[0]:%H:%M}" if june[0] else ""),
                     f"[$forge-muted]{escape(p.place_words())} · the change is gradual around sunset and sunrise[/]"]
        sun.update("\n".join(l for l in lines if l))
        sun.display = p.schedule == "sun"
        for i in ("#nf-lat", "#nf-lon"):
            self.query_one(i, Input).disabled = p.schedule != "sun"
        for i in ("#nf-warm-from", "#nf-day-from", "#nf-fade"):
            self.query_one(i, Input).disabled = p.schedule != "fixed"

    def on_choices_changed(self, e: Choices.Changed) -> None:
        if e.control.id == "nf-schedule":
            e.stop()
            self.session.pending.schedule = e.value
            self.refresh_view()
            self.app.refresh_state()

    def on_input_changed(self, e: Input.Changed) -> None:
        p = self.session.pending
        v = e.value.strip()
        try:
            if e.input.id == "nf-lat":
                p.latitude = max(-90.0, min(90.0, float(v)))
            elif e.input.id == "nf-lon":
                p.longitude = max(-180.0, min(180.0, float(v)))
            elif e.input.id == "nf-fade":
                p.fade_minutes = max(1, min(240, int(v)))
            elif e.input.id in ("nf-warm-from", "nf-day-from"):
                t = clock(v, "")
                if not t:
                    return
                setattr(p, "warm_from" if e.input.id == "nf-warm-from" else "day_from", t)
            else:
                return
        except ValueError:
            return                               # half-typed: wait for a number
        self.refresh_view()
        self.app.refresh_state()


# ---- the app ----------------------------------------------------------------------------------------

class NightForgeApp(ForgeApp):
    APP_NAME = f"nightForge {__version__} · warmer screens in the evening"
    SHOW_HINT_BAR = True
    SHOW_CHANGES_BAR = True
    CSS = NF_CSS
    LICENSE_NOTICE = GPL3_NOTICE
    MENU = [
        {"id": "night", "title": "Night Light", "kind": "section"},
        {"id": "schedule", "title": "Schedule", "kind": "section"},
        {"id": "help", "title": "Help", "kind": "menu", "items": [
            ("Manual", "m", "manual"), ("Keys", "k", "shortcuts"), ("License", "l", "license"),
            ("About", "a", "about")]},
        {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"},
    ]
    SHORTCUTS = [
        ("1-3, Ctrl+letter", "go to a menu entry: 1 Night Light · 2 Schedule · 3 Help"),
        ("o", "switch the night light on or off (at once, and saved)"),
        ("← →", "choose (Right now, warmth, When)"),
        ("p", "preview the evening warmth for 10 seconds"),
        ("Tab / Shift+Tab", "next / previous field or button"),
        ("F10", "save the warmth and the schedule, with a review first"),
        ("Esc", "close a window"),
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

    def __init__(self, settings: Settings | None = None, *, live: bool = True, **kw) -> None:
        self.session = Session(settings or Settings.load())
        self.live = live                       # False in tests: nothing is started or stopped
        self.ABOUT = {
            "name": "nightForge", "version": __version__,
            "tagline": "Warmer screens in the evening: on or off, how warm, and when.",
            "description": "Part of the Forge Suite for KognogOS. The night light itself is wlsunset, by Kenny "
                           "Levinsen; the sun times use NOAA's solar formulas.",
            "authors": "jetomev (Javier) · Claude (Anthropic), co-developer",
            "license": "GPL-3.0-or-later",
            "links": [("Code", "https://github.com/jetomev/forge-suite/tree/main/nightforge")],
        }
        super().__init__(**kw)

    def compose_sections(self) -> ComposeResult:
        yield NightView(self.session, id="sec-night")
        yield ScheduleView(self.session, id="sec-schedule")

    def on_mount(self) -> None:
        super().on_mount()
        self.refresh_state()
        self.set_interval(30, self._tick)

    def _tick(self) -> None:
        self.query_one(NightView).refresh_view()

    def on_action(self, action_id: str) -> None:
        if action_id == "manual":
            pages = load_pages(MANUAL_DIR) if os.path.isdir(MANUAL_DIR) else []
            if not pages:
                self.notify("The manual isn't installed.", severity="warning")
                return
            self.show_manual("nightForge manual", pages)

    def on_section_shown(self, section_id: str) -> None:
        if section_id == "night":
            self.query_one(NightView).refresh_view()
        else:
            self.query_one(ScheduleView).refresh_view()

    def refresh_state(self) -> None:
        n = self.session.change_count
        self.set_title_status(f"{os.environ.get('USER', '')} · " + (f"{n} change{'s' if n != 1 else ''} waiting" if n
                                                                    else "nothing changed yet"))
        if n:
            self.changes_bar.show(f"{n} change{'s' if n != 1 else ''} not saved yet", "changed",
                                  [("Save Changes (F10)", "nf-save", True), ("Discard Changes", "nf-discard", False)])
        else:
            self.changes_bar.hide()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "nf-save":
            self.action_save()
        elif e.button.id == "nf-discard":
            self.session.pending = copy.deepcopy(self.session.saved)
            self.query_one(NightView).refresh(recompose=True)
            self.query_one(ScheduleView).refresh(recompose=True)
            self.refresh_state()
            self.notify("Changes discarded. Nothing was changed.")

    # -- at once: on / off, and Right now ---------------------------------------------------------------
    def _run(self, fn, *a) -> bool:
        if not self.live:
            return True
        try:
            fn(*a)
            return True
        except C.Trouble as t:
            self.notify(str(t), title="The night light didn't start", severity="error", timeout=10)
            return False

    def set_enabled(self, value: bool) -> None:
        """On / off acts at once and is saved (like the tray's Turn Off / Turn On)."""
        s = copy.deepcopy(self.session.saved)
        s.enabled = value
        try:
            if self.live:
                s.save()
        except OSError as e:
            self.notify(f"{e}. Nothing was changed.", severity="error")
            return
        self.session.saved.enabled = value
        self.session.pending.enabled = value
        self._run(C.start, s, "auto")
        self.query_one(NightView).refresh_view()
        self.notify("Night light on." if value else "Night light off, now and at every login.", timeout=4)

    def set_mode(self, mode: str) -> None:
        self._run(C.start, self.session.saved, mode)
        self.query_one(NightView).refresh_view()

    # -- preview (a pop-up) ---------------------------------------------------------------------------
    @work(exclusive=True, group="nf-preview")
    async def preview(self, warmth: int) -> None:
        if not self.session.saved.enabled:
            self.notify("Switch the night light on first (o).", severity="warning")
            return
        before = C.mode()
        if not self._run(C.start, self.session.saved, "warm", warmth):
            return
        keep = await self.push_screen_wait(PreviewDialog(warmth))
        self._run(C.start, self.session.saved, before)
        if keep:
            self.session.pending.warmth = warmth
            self.query_one(NightView).refresh(recompose=True)
            self.refresh_state()
            self.notify("Kept. Press F10 to save it.", timeout=5)
        self.query_one(NightView).refresh_view()

    # -- save (a pop-up, D-2) -------------------------------------------------------------------------
    @work(exclusive=True, group="nf-save")
    async def action_save(self) -> None:
        await self._save()

    async def _save(self) -> bool:
        rows = self.session.changes()
        if not rows:
            self.notify("Nothing to save: no changes.")
            return False
        path = str(CONFIG).replace(os.path.expanduser("~"), "~")
        choice = await self.push_screen_wait(ReviewDialog(
            "Save the night light settings?", [ChangeGroup("Night light", path, rows)],
            steps=["A backup of the old file is made first (the last 20 are kept)",
                   "The night light restarts with them: at once, and at every login after"],
            buttons=[("Save (Enter)", "save", True)]))
        if choice is None:
            return False
        try:
            backup = self.session.pending.save() if self.live else None
        except OSError as e:
            self.notify(f"{e}. Nothing was written.", title="Not saved", severity="error")
            return False
        self.session.saved = copy.deepcopy(self.session.pending)
        self._run(C.start, self.session.saved, "auto")
        self.refresh_state()
        self.query_one(NightView).refresh_view()
        self.notify(f"Saved to {path}" + (" (old one backed up)" if backup else "") + ". The night light uses it now.",
                    title="Saved", timeout=6)
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

    @work(exclusive=True, group="nf-quit")
    async def save_then_quit(self) -> None:
        if await self._save():
            self.exit()
        else:
            self.notify("Not saved, so nightForge stays open.", timeout=6)


def needs(*, environ=None, swaymsg: str = "swaymsg") -> list:
    return [
        sway_session("The warm colours are made by wlsunset, which works on Sway and its family (wlroots).",
                     "Continue to edit the settings anyway: they take effect at your next Sway login.",
                     optional=True, environ=environ, swaymsg=swaymsg),
        program("wlsunset", "wlsunset makes the screens warmer.",
                "Install it (on KognogOS: nog install wlsunset), or continue to edit the settings.", optional=True),
    ]


def main(*, ask=None) -> int:
    if not start_check("nightForge", needs(), ask=ask):
        return 2
    NightForgeApp().run()
    return 0
