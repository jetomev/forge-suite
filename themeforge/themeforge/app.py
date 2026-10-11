"""themeForge — the app frame, on forgekit (the defaultappsForge / nightForge pattern).

0.1.0 (Javier, 2026-10-11): "start with the first 2 options … Picker (Theme Picker), and Color
(Theme Color) … Keep it simple. Maybe both in the same page, just pick and choose options
(dropdowns)". One page: the theme (hypeForge's style) and its colours, each a drop-down, a strip of
the colours, Apply and Undo. Pop-ups, icons, fonts and the rest come later, as more pages.
"""

from __future__ import annotations

import os
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Select, Static

from forgekit import FORGE_CSS, GPL3_NOTICE, MENU_HINT, ForgeApp, a_file, load_pages, start_check

from . import __version__
from .look import Look

MANUAL_DIR = os.path.join(os.path.dirname(__file__), "manual")

TF_CSS = FORGE_CSS + """
/* the options: a matrix of two columns going down (Javier, 2026-10-11), compact with air between */
#tf-options { grid-size: 2; grid-gutter: 0 4; height: auto; margin: 1 2 0 2; }
.tf-cell { height: auto; }
.tf-row { height: 1; }
.tf-name { width: 9; color: $forge-accent; text-style: bold; }
.tf-row Select { width: 1fr; height: 1; }
.tf-row SelectCurrent { border: none; height: 1; padding: 0 1; background: $forge-surface; }
.tf-row Select:focus > SelectCurrent { border: none; background: $forge-focus-bg; }
.tf-under { height: auto; padding: 0 0 0 10; margin: 1 0 0 0; color: $forge-muted; }
#tf-brings-title { margin: 1 2 0 2; color: $forge-accent; text-style: bold; height: 1; }
#tf-brings { grid-size: 4; grid-columns: 14 1fr 14 1fr; grid-gutter: 0 3; height: auto; margin: 0 2 0 2; }
#tf-brings Static { height: auto; }
.tf-el { color: $forge-muted; }
#tf-foot { height: 1; margin: 1 2 0 2; }
#tf-now { width: 1fr; height: 1; }
/* small buttons: one line, no frame (Javier: "not the big ones, they look awful") */
Button.tf-small { height: 1; min-width: 0; width: auto; border: none; padding: 0 2; margin: 0 0 0 2; }
"""

# the pieces of a look, in the order shown (hypeForge's look file, D-90) and their plain names
ELEMENT_NAMES = {"bar": "Bar", "launcher": "Launcher", "workspaces": "Workspaces", "taskbar": "Taskbar",
                 "datetime": "Date & time", "tray": "Tray", "status_icons": "Status icons", "popups": "Pop-ups",
                 "dock": "Dock", "windows": "Windows", "icons": "Icons", "fonts": "Fonts"}


def swatch_markup(colours: list[str]) -> str:
    """One row of colour blocks: the theme at a glance (neutrals, its colour, its pop, its text)."""
    return "".join(f"[on {c}]     [/]" for c in colours)


class PickerView(VerticalScroll):
    FORGE_HINTS = [("Tab", "next"), ("Enter", "open the list"), ("F10", "apply"), ("u", "undo"), MENU_HINT]

    def __init__(self, look: Look, **kw) -> None:
        super().__init__(**kw)
        self.look = look
        self.themes_by_slug = {s.slug: s for s in look.styles()}
        self.colours_by_slug = {c.slug: c for c in look.colours()}

    def compose(self) -> ComposeResult:
        style_now, theme_now = self.look.current()
        style_opts = [(s.name + ("  · in use" if s.slug == style_now else ""), s.slug) for s in self.themes_by_slug.values()]
        colour_opts = [(c.label + ("  · in use" if c.slug == theme_now else ""), c.slug)
                       for c in self.colours_by_slug.values()]
        with Grid(id="tf-options"):
            with Vertical(classes="tf-cell"):
                with Horizontal(classes="tf-row"):
                    yield Static("Theme", classes="tf-name")
                    yield Select(style_opts, value=style_now if style_now in self.themes_by_slug else Select.NULL,
                                 allow_blank=style_now not in self.themes_by_slug, prompt="— pick a theme —",
                                 id="tf-style")
                yield Static("", id="tf-style-about", classes="tf-under")
            with Vertical(classes="tf-cell"):
                with Horizontal(classes="tf-row"):
                    yield Static("Colors", classes="tf-name")
                    yield Select(colour_opts, value=theme_now if theme_now in self.colours_by_slug else Select.NULL,
                                 allow_blank=theme_now not in self.colours_by_slug, prompt="— pick the colors —",
                                 id="tf-colour")
                yield Static("", id="tf-swatch", classes="tf-under")
        yield Static("What this theme brings", id="tf-brings-title")
        with Grid(id="tf-brings"):
            for key, name in ELEMENT_NAMES.items():
                yield Static(name)
                yield Static("", id=f"tf-el-{key}", classes="tf-el")
        with Horizontal(id="tf-foot"):
            yield Static("", id="tf-now")
            yield Button("Undo Last Apply (u)", id="tf-undo", classes="tf-small")

    def on_mount(self) -> None:
        self.refresh_words()

    def chosen(self) -> tuple[str | None, str | None]:
        s = self.query_one("#tf-style", Select).value
        c = self.query_one("#tf-colour", Select).value
        return (None if s is Select.NULL else str(s)), (None if c is Select.NULL else str(c))

    def refresh_words(self) -> None:
        style, colour = self.chosen()
        st = self.themes_by_slug.get(style)
        self.query_one("#tf-style-about", Static).update(st.summary if st else "")
        for key in ELEMENT_NAMES:
            self.query_one(f"#tf-el-{key}", Static).update((st.elements.get(key) if st else "") or "—")
        co = self.colours_by_slug.get(colour)
        self.query_one("#tf-swatch", Static).update(swatch_markup(co.swatch) if co else "")
        s_now, t_now = self.look.current()
        if s_now:
            name_s = self.themes_by_slug[s_now].name if s_now in self.themes_by_slug else s_now
            name_t = self.colours_by_slug[t_now].name if t_now in self.colours_by_slug else (t_now or "—")
            self.query_one("#tf-now", Static).update(f"[$forge-accent b]In use now:[/]  {name_s}  ·  {name_t}")
        else:
            self.query_one("#tf-now", Static).update("[$forge-muted]No look applied yet.[/]")

    def on_select_changed(self, e: Select.Changed) -> None:
        if e.select.id in ("tf-style", "tf-colour"):
            e.stop()
            self.refresh_words()
            self.app.refresh_state()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "tf-undo":
            e.stop()
            self.app.action_undo()

    def rebuild(self) -> None:
        """After an apply or undo: the "in use" marks and the choices follow the desktop."""
        self.refresh(recompose=True)
        self.call_after_refresh(self.refresh_words)


class ThemeForgeApp(ForgeApp):
    APP_NAME = f"themeForge {__version__} · the look of your desktop"
    SHOW_HINT_BAR = True
    SHOW_CHANGES_BAR = True
    CSS = TF_CSS
    LICENSE_NOTICE = GPL3_NOTICE
    MENU = [
        {"id": "picker", "title": "Theme Picker", "kind": "section"},
        {"id": "help", "title": "Help", "kind": "menu", "items": [
            ("Manual", "m", "manual"), ("Keys", "k", "shortcuts"), ("License", "l", "license"),
            ("About", "a", "about")]},
        {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"},
    ]
    SHORTCUTS = [
        ("1-2, Ctrl+letter", "go to a menu entry: 1 Theme Picker · 2 Help"),
        ("Tab / Shift+Tab", "next / previous drop-down or button"),
        ("Enter", "open a drop-down · pick in it"),
        ("F10", "apply the theme and colours picked"),
        ("u", "undo the last apply (the look from before it comes back)"),
        ("Esc", "close a list or a window"),
        ("M", "the manual"),
        ("?", "this list"),
        ("Q or Ctrl+Q", "quit (not inside hypeForge Settings)"),
    ]
    HINTS = [MENU_HINT, ("F10", "apply"), ("?", "all keys")]
    BINDINGS = [
        Binding("f10", "apply", show=False, priority=True),
        Binding("u", "undo", show=False),
        Binding("question_mark", "act('shortcuts')", show=False),
        Binding("m", "act('manual')", show=False),
        Binding("q", "act('quit')", show=False),
    ]

    def __init__(self, look: Look | None = None, **kw) -> None:
        self.look = look or Look()
        self.busy = False
        self.ABOUT = {
            "name": "themeForge", "version": __version__,
            "tagline": "The look of your desktop: pick a theme and its colours.",
            "description": "Part of the Forge Suite for KognogOS. It switches hypeForge's look — the bar, the windows, "
                           "the pop-ups, the lists, the lock screen, the terminal and the wallpaper — in one step, "
                           "with a backup to go back to.",
            "authors": "jetomev (Javier) · Claude (Anthropic), co-developer",
            "license": "GPL-3.0-or-later",
            "links": [("Code", "https://github.com/jetomev/forge-suite/tree/main/themeforge")],
        }
        super().__init__(**kw)

    def compose_sections(self) -> ComposeResult:
        yield PickerView(self.look, id="sec-picker")

    def on_mount(self) -> None:
        super().on_mount()
        self.refresh_state()

    def on_section_shown(self, section_id: str) -> None:
        if section_id == "picker":
            self.call_after_refresh(self.query_one("#tf-style").focus)

    def on_action(self, action_id: str) -> None:
        if action_id == "manual":
            pages = load_pages(MANUAL_DIR) if os.path.isdir(MANUAL_DIR) else []
            if not pages:
                self.notify("The manual isn't installed.", severity="warning")
                return
            self.show_manual("themeForge manual", pages)

    # ---- what is picked vs what is in use ----

    def picked(self) -> tuple[str | None, str | None]:
        return self.query_one(PickerView).chosen()

    def pending(self) -> bool:
        style, colour = self.picked()
        return bool(style and colour) and (style, colour) != self.look.current()

    def refresh_state(self) -> None:
        view = self.query_one(PickerView)
        style, colour = self.picked()
        s_now, t_now = self.look.current()
        self.set_title_status(f"{os.environ.get('USER', '')} · " + ("applying…" if self.busy else
                              "a new look picked" if self.pending() else "the look in use"))
        if self.pending() and not self.busy:
            names = (view.themes_by_slug[style].name if style in view.themes_by_slug else style,
                     view.colours_by_slug[colour].name if colour in view.colours_by_slug else colour)
            self.changes_bar.show(f"Picked, not applied yet: {names[0]} · {names[1]}", "changed",
                                  [("Apply (F10)", "tf-bar-apply", True), ("Put Back", "tf-bar-back", False)])
        else:
            self.changes_bar.hide()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "tf-bar-apply":
            self.action_apply()
        elif e.button.id == "tf-bar-back":
            self.query_one(PickerView).rebuild()
            self.call_after_refresh(self.refresh_state)

    # ---- apply and undo: hypeForge's own command, in the background ----

    def action_apply(self) -> None:
        if self.busy:
            return
        style, colour = self.picked()
        if not (style and colour):
            self.notify("Pick a theme and its colours first.", severity="warning")
            return
        if (style, colour) == self.look.current():
            self.notify("That's the look in use already.")
            return
        view = self.query_one(PickerView)
        self._run(("apply", style, colour),
                  f"{view.themes_by_slug[style].name} · {view.colours_by_slug[colour].name}")

    def action_undo(self) -> None:
        if not self.busy:
            self._run(("undo",), "the look from before")

    @work(thread=True, exclusive=True, group="tf-apply")
    def _run(self, what: tuple, words: str) -> None:
        self.busy = True
        self.call_from_thread(self.refresh_state)
        self.call_from_thread(self.notify, f"Switching to {words}… the bar restarts for a moment.", timeout=6)
        ok, message = self.look.apply(*what[1:]) if what[0] == "apply" else self.look.undo()
        self.busy = False
        self.call_from_thread(self._done, ok, message, words)

    def _done(self, ok: bool, message: str, words: str) -> None:
        if ok:
            self.notify(f"Now in use: {words}.", title="Applied", timeout=6)
        else:
            self.notify(f"{message}. Nothing changed.", title="Not applied", severity="error", timeout=10)
        self.query_one(PickerView).rebuild()
        self.call_after_refresh(self.refresh_state)


def needs(look: Look | None = None) -> list:
    look = look or Look()
    home = look.home or (Path.home() / "Programs/forge-suite/hypeforge")
    return [a_file(home / "applets/theme/hypeforge-theme",
                   "themeForge switches hypeForge's look with hypeForge's own look command.",
                   what="hypeForge's look command")]


def main(*, ask=None) -> int:
    if not start_check("themeForge", needs(), ask=ask):
        return 2
    ThemeForgeApp().run()
    return 0
