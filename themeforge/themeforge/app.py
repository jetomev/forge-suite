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
from textual.widgets import Button, Input, Select, Static

from forgekit import FORGE_CSS, GPL3_NOTICE, MENU_HINT, ForgeApp, a_file, load_pages, start_check

from . import __version__
from .look import FITS, Look
from .preview import overlay_picture, preview
from .termcell import Cells, measure

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
/* the Wallpaper page: the same two-column matrix, the preview under it */
#tf-wp-options { grid-size: 2; grid-gutter: 0 4; height: auto; margin: 1 2 0 2; }
.tf-row Input { width: 1fr; height: 1; border: none; padding: 0 1; background: $forge-surface; }
.tf-row Input:focus { border: none; background: $forge-focus-bg; }
#tf-wp-preview { width: auto; height: auto; margin: 1 2 0 4; border: round $forge-muted; }
#tf-wp-caption { height: 1; margin: 0 2 0 4; color: $forge-muted; }
#tf-wp-foot { height: 1; margin: 1 2 0 2; }
#tf-wp-now { width: 1fr; height: 1; }
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
            for view in self.app.query(WallpaperView):      # its "theme's own" and preview follow these picks
                view.look_changed()
            self.app.refresh_state()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "tf-undo":
            e.stop()
            self.app.action_undo()

    def rebuild(self) -> None:
        """After an apply or undo: the "in use" marks and the choices follow the desktop."""
        self.refresh(recompose=True)
        self.call_after_refresh(self.refresh_words)


import threading

PREVIEW_LOCK = threading.Lock()
PREVIEW_COLS = 56


class PictureOverlay:
    """The full-quality preview over the terminal (overlay.py): started when there is something to show,
    told to show or hide, ended with themeForge (its input closes). Only on Sway, in a terminal that
    told its cell size; otherwise the half-block preview is all there is."""

    def __init__(self, cells: Cells | None):
        self.cells = cells
        self.proc = None
        self.sent: str | None = None

    @property
    def possible(self) -> bool:
        return bool(self.cells and os.environ.get("SWAYSOCK") and os.environ.get("WAYLAND_DISPLAY")
                    and os.environ.get("THEMEFORGE_NO_OVERLAY") != "1")

    @staticmethod
    def ancestors() -> list[int]:
        """themeForge's process and every one above it: one of them is the terminal's window."""
        out, pid = [], os.getpid()
        while pid > 1 and len(out) < 20:
            out.append(pid)
            try:
                with open(f"/proc/{pid}/stat") as f:
                    pid = int(f.read().rsplit(")", 1)[1].split()[1])
            except (OSError, ValueError, IndexError):
                break
        return out

    def _send(self, msg: dict) -> None:
        import json
        import subprocess
        import sys
        line = json.dumps(msg)
        if line == self.sent:
            return
        if self.proc is None or self.proc.poll() is not None:
            if "hide" in msg:
                return
            c = self.cells
            cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "overlay.py"),
                   "--pids", ",".join(map(str, self.ancestors())), "--cell", str(c.width), str(c.height),
                   "--pad", str(c.pad_x), str(c.pad_y)] + (["--centred"] if c.centred else [])
            try:
                err = os.environ.get("THEMEFORGE_OVERLAY_LOG")       # the bench reads its errors too
                self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                             stderr=open(err + ".err", "a") if err else subprocess.DEVNULL, text=True)
            except OSError:
                self.cells = None
                return
        try:
            self.proc.stdin.write(line + "\n")
            self.proc.stdin.flush()
            self.sent = line
        except (OSError, ValueError):
            self.proc = None

    def show(self, png: str, cells: tuple[int, int, int, int], grid: tuple[int, int]) -> None:
        if self.possible:
            self._send({"show": {"png": png, "cells": list(cells), "grid": list(grid)}})

    def hide(self) -> None:
        self._send({"hide": True})

    def close(self) -> None:
        if self.proc is not None:
            try:
                self.proc.stdin.close()
                self.proc.wait(3)
            except Exception:
                self.proc.kill()
            self.proc = None


def plain(choice: str) -> str:
    """A wallpaper choice in plain words."""
    if choice == "theme":
        return "the theme's own"
    if choice == "solid":
        return "a solid colour"
    if choice.startswith("kognogos:"):
        return "KognogOS · " + choice.split(":", 1)[1].replace("-", " ").title()
    return Path(choice).name


class WallpaperView(VerticalScroll):
    """Desktop background 1.0 (Javier, 2026-10-11): every screen the same picture; the theme's own
    (the Rice: our KognogOS background; each other theme its topic, in the colours picked), a KognogOS
    background, a solid colour, or one of your pictures from a folder; five ways to lay it; a small
    preview drawn in the terminal."""

    FORGE_HINTS = [("Tab", "next"), ("Enter", "open the list"), ("F10", "apply"), ("u", "undo"), MENU_HINT]

    def __init__(self, look: Look, **kw) -> None:
        super().__init__(**kw)
        self.look = look

    # ---- what can be picked ----

    def sources(self, style: str | None) -> list[tuple[str, str]]:
        topic = self.look.topic(style) if style else ""
        out = [("The theme's own" + (f" — {topic}" if topic else ""), "theme")]
        out += [(f"KognogOS · {name}", f"kognogos:{slug}") for slug, name in self.look.kognogos_designs()]
        out += [("My pictures", "mine"), ("Solid colour — the theme's own", "solid")]
        return out

    def folder_pictures(self, folder: Path, also: str | None = None) -> list[tuple[str, str]]:
        pics = [(p.name, str(p)) for p in self.look.pictures(folder)]
        if also and Path(also).is_file() and also not in {v for _, v in pics}:
            pics.insert(0, (Path(also).name + "  · in use", also))
        return pics

    def compose(self) -> ComposeResult:
        choice, fit = self.look.wallpaper_now()
        source = choice if choice in ("theme", "solid") or choice.startswith("kognogos:") else "mine"
        style, _ = self.look.current()
        srcs = self.sources(style)
        folder = str(self.look.picks().get("wallpaper", {}).get("folder") or "~/Pictures/Wallpapers")
        pics = self.folder_pictures(Path(folder).expanduser(), choice if source == "mine" else None)
        with Grid(id="tf-wp-options"):
            with Vertical(classes="tf-cell"):
                with Horizontal(classes="tf-row"):
                    yield Static("Source", classes="tf-name")
                    yield Select(srcs, value=source if source in {v for _, v in srcs} else "theme",
                                 allow_blank=False, id="tf-wp-source")
                yield Static("", id="tf-wp-source-about", classes="tf-under")
            with Vertical(classes="tf-cell"):
                with Horizontal(classes="tf-row"):
                    yield Static("Fit", classes="tf-name")
                    yield Select([(words, key) for key, words in FITS.items()],
                                 value=fit if fit in FITS else "fill", allow_blank=False, id="tf-wp-fit")
                yield Static("Every screen shows the same picture.", classes="tf-under")
            with Vertical(classes="tf-cell"):
                with Horizontal(classes="tf-row"):
                    yield Static("Folder", classes="tf-name")
                    yield Input(folder, id="tf-wp-folder")
                yield Static("", id="tf-wp-folder-about", classes="tf-under")
            with Vertical(classes="tf-cell"):
                with Horizontal(classes="tf-row"):
                    yield Static("Picture", classes="tf-name")
                    yield Select(pics, value=choice if source == "mine" and choice in {v for _, v in pics} else Select.NULL,
                                 allow_blank=True, prompt="— pick a picture —", id="tf-wp-picture")
                yield Static("", id="tf-wp-picture-about", classes="tf-under")
        yield Static("", id="tf-wp-preview")
        yield Static("", id="tf-wp-caption")
        with Horizontal(id="tf-wp-foot"):
            yield Static("", id="tf-wp-now")
            yield Button("Make Folder (n)", id="tf-wp-mkdir", classes="tf-small")
            yield Button("Undo Last Apply (u)", id="tf-wp-undo", classes="tf-small")

    def on_mount(self) -> None:
        self.refresh_words()

    # ---- what is picked ----

    def folder(self) -> Path:
        return Path(self.query_one("#tf-wp-folder", Input).value.strip() or "~/Pictures/Wallpapers").expanduser()

    def chosen(self) -> tuple[str | None, str]:
        """(the wallpaper choice, the fit): a picture's path for My pictures (None until one is picked)."""
        source = str(self.query_one("#tf-wp-source", Select).value)
        fit = str(self.query_one("#tf-wp-fit", Select).value)
        if source == "mine":
            pic = self.query_one("#tf-wp-picture", Select).value
            return (None if pic is Select.NULL else str(pic)), fit
        return source, fit

    def refresh_words(self) -> None:
        source = str(self.query_one("#tf-wp-source", Select).value)
        mine = source == "mine"
        folder = self.folder()
        exists = folder.is_dir()
        n = len(self.look.pictures(folder)) if exists else 0
        self.query_one("#tf-wp-picture", Select).disabled = not mine
        self.query_one("#tf-wp-folder", Input).disabled = not mine
        self.query_one("#tf-wp-mkdir", Button).display = mine and not exists
        about = {"theme": "Changes with the theme and its colours.",
                 "solid": "No picture: the theme's own colour.",
                 "mine": "Stays when the theme or colours change."}
        self.query_one("#tf-wp-source-about", Static).update(
            about.get(source, "KognogOS, in the colours picked."))
        self.query_one("#tf-wp-folder-about", Static).update(
            ("" if not mine else f"{n} picture{'s' if n != 1 else ''} here (PNG, JPEG, WebP…)" if exists
             else "This folder doesn't exist yet: Make Folder (n), then put pictures in it."))
        self.query_one("#tf-wp-picture-about", Static).update("" if mine else "For My pictures.")
        choice, fit = self.look.wallpaper_now()
        self.query_one("#tf-wp-now", Static).update(f"[$forge-accent b]In use now: [/]{plain(choice)}  ·  {fit}")
        self.draw()

    @work(thread=True, exclusive=True, group="tf-wp-preview")
    def draw(self) -> None:
        choice, fit = self.chosen()
        style, theme = self.app.picked() if hasattr(self.app, "picked") else self.look.current()
        style, theme = style or self.look.current()[0], theme or self.look.current()[1]
        self.app.call_from_thread(self.query_one("#tf-wp-caption", Static).update, "drawing the preview…")
        if not (choice and style and theme):
            self.app.call_from_thread(self._show, "", "Pick a picture to see it here.")
            return
        solid = self.look.picture_path(style, theme, "solid")
        try:
            from PIL import Image
            with Image.open(solid) as im:
                bg = im.convert("RGB").getpixel((0, 0))
        except Exception:
            bg = (30, 30, 46)
        path = Path(choice) if choice not in ("theme", "solid") and not choice.startswith("kognogos:") \
            else self.look.picture_path(style, theme, choice)
        if path is None or not Path(path).is_file():
            self.app.call_from_thread(self._show, "", "The picture couldn't be made or read.")
            return
        try:
            text = preview(path, "fill" if choice == "solid" else fit, bg, cols=PREVIEW_COLS,
                           rows=self.app.preview_rows() if hasattr(self.app, "preview_rows") else 14)
            if self.app.overlay.possible:
                runtime = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "themeforge"
                runtime.mkdir(parents=True, exist_ok=True)
                import time
                png = overlay_picture(path, "fill" if choice == "solid" else fit, bg,
                                      runtime / f"preview-{time.monotonic_ns()}.png")
                with PREVIEW_LOCK:                              # a slow, older preview never replaces a newer one
                    if not self.overlay_png or png.name > Path(self.overlay_png).name:
                        self.overlay_png = str(png)
                    now = time.time()
                    for old in runtime.glob("preview-*.png"):    # the old ones go once nothing can still want them
                        try:
                            if str(old) != self.overlay_png and now - old.stat().st_mtime > 30:
                                old.unlink(missing_ok=True)
                        except OSError:
                            pass
        except Exception as e:
            self.app.call_from_thread(self._show, "", f"The picture couldn't be read ({e.__class__.__name__}).")
            return
        colours = self.look.colours()
        theme_name = next((c.name for c in colours if c.slug == theme), theme)
        self.app.call_from_thread(self._show, text, plain(choice) + ("" if choice not in ("theme", "solid") and
                                                                    not choice.startswith("kognogos:") else f", in {theme_name}"))

    def _show(self, text, caption: str) -> None:
        if not text:
            self.overlay_png = None
        self.query_one("#tf-wp-preview", Static).update(text)
        self.query_one("#tf-wp-caption", Static).update(caption)

    overlay_png: str | None = None

    def overlay_spot(self) -> tuple[int, int, int, int] | None:
        """The preview's character cells on the screen, when the full picture may cover them: this page
        shown, no list open over it, no other screen (the manual, a question) on top, all of it in view."""
        if not (self.overlay_png and self.display and self.app.screen is self.screen):
            return None
        if any(s.expanded for s in self.query(Select)):
            return None
        box = self.query_one("#tf-wp-preview", Static).content_region
        size = self.app.size
        if box.width < 4 or box.height < 2 or box.x < 0 or box.y < 0 or \
                box.right > size.width or box.bottom > size.height:
            return None
        return box.x, box.y, box.width, box.height

    # ---- the person's moves ----

    def on_select_changed(self, e: Select.Changed) -> None:
        if e.select.id and e.select.id.startswith("tf-wp-"):
            e.stop()
            self.refresh_words()
            self.app.refresh_state()

    def on_input_submitted(self, e: Input.Submitted) -> None:
        if e.input.id == "tf-wp-folder":
            e.stop()
            self.new_folder()

    def new_folder(self) -> None:
        pics = self.folder_pictures(self.folder())
        sel = self.query_one("#tf-wp-picture", Select)
        sel.set_options(pics)
        self.refresh_words()
        self.app.refresh_state()

    def make_folder(self) -> None:
        folder = self.folder()
        if str(self.query_one("#tf-wp-source", Select).value) != "mine" or folder.is_dir():
            return
        try:
            folder.mkdir(parents=True)
        except OSError as e:
            self.app.notify(f"The folder couldn't be made ({e.strerror}).", severity="error")
            return
        self.app.notify(f"Made {folder}. Put your pictures in it; they show up here.", timeout=6)
        self.new_folder()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "tf-wp-undo":
            e.stop()
            self.app.action_undo()
        elif e.button.id == "tf-wp-mkdir":
            e.stop()
            self.make_folder()

    def look_changed(self) -> None:
        """The Theme page picked another theme or colours: the theme's own wallpaper is another one."""
        style, _ = self.app.picked() if hasattr(self.app, "picked") else self.look.current()
        sel = self.query_one("#tf-wp-source", Select)
        keep = sel.value
        sel.set_options(self.sources(style or self.look.current()[0]))
        sel.value = keep
        self.refresh_words()

    def rebuild(self) -> None:
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
        {"id": "wallpaper", "title": "Wallpaper", "kind": "section"},
        {"id": "help", "title": "Help", "kind": "menu", "items": [
            ("Manual", "m", "manual"), ("Keys", "k", "shortcuts"), ("License", "l", "license"),
            ("About", "a", "about")]},
        {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"},
    ]
    SHORTCUTS = [
        ("1-3, Ctrl+letter", "go to a menu entry: 1 Theme Picker · 2 Wallpaper · 3 Help"),
        ("Tab / Shift+Tab", "next / previous drop-down or button"),
        ("Enter", "open a drop-down · pick in it"),
        ("F10", "apply what is picked (theme, colours, wallpaper)"),
        ("n", "Wallpaper: make the pictures folder when it doesn't exist yet"),
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
        Binding("n", "make_folder", show=False),
        Binding("question_mark", "act('shortcuts')", show=False),
        Binding("m", "act('manual')", show=False),
        Binding("q", "act('quit')", show=False),
    ]

    def __init__(self, look: Look | None = None, cells: Cells | None = None, **kw) -> None:
        self.look = look or Look()
        self.busy = False
        self.overlay = PictureOverlay(cells)
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
        yield WallpaperView(self.look, id="sec-wallpaper")

    def on_mount(self) -> None:
        super().on_mount()
        self.refresh_state()
        if self.overlay.possible:
            self.set_interval(0.2, self.follow_overlay)

    def preview_rows(self) -> int:
        """Rows for a screen-shaped preview 56 characters wide: from the real cell size when the terminal
        said it (so the blocks and the full picture cover the same spot), else a usual cell (about 1:2.2)."""
        c = self.overlay.cells
        ratio = (c.height / c.width) if c and c.width else 2.2
        return max(6, round(PREVIEW_COLS * 9 / 16 / ratio))

    def follow_overlay(self) -> None:
        views = list(self.query(WallpaperView))
        spot = views[0].overlay_spot() if views else None
        if spot:
            self.overlay.show(views[0].overlay_png, spot, (self.size.width, self.size.height))
        else:
            self.overlay.hide()

    def on_unmount(self) -> None:
        self.overlay.close()

    def on_section_shown(self, section_id: str) -> None:
        if section_id == "picker":
            self.call_after_refresh(self.query_one("#tf-style").focus)
        elif section_id == "wallpaper":
            self.call_after_refresh(self.query_one("#tf-wp-source").focus)

    def action_make_folder(self) -> None:
        self.query_one(WallpaperView).make_folder()

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

    def wallpaper_picked(self) -> tuple[str | None, str]:
        return self.query_one(WallpaperView).chosen()

    def theme_pending(self) -> bool:
        style, colour = self.picked()
        return bool(style and colour) and (style, colour) != self.look.current()

    def wallpaper_pending(self) -> bool:
        choice, fit = self.wallpaper_picked()
        return bool(choice) and (choice, fit) != self.look.wallpaper_now()

    def pending(self) -> bool:
        return self.theme_pending() or self.wallpaper_pending()

    def refresh_state(self) -> None:
        view = self.query_one(PickerView)
        style, colour = self.picked()
        s_now, t_now = self.look.current()
        self.set_title_status(f"{os.environ.get('USER', '')} · " + ("applying…" if self.busy else
                              "a new look picked" if self.pending() else "the look in use"))
        if self.pending() and not self.busy:
            parts = []
            if self.theme_pending():
                parts.append(f"{view.themes_by_slug[style].name if style in view.themes_by_slug else style} · "
                             f"{view.colours_by_slug[colour].name if colour in view.colours_by_slug else colour}")
            if self.wallpaper_pending():
                parts.append("a new wallpaper")
            self.changes_bar.show(f"Picked, not applied yet: {', '.join(parts)}", "changed",
                                  [("Apply (F10)", "tf-bar-apply", True), ("Put Back", "tf-bar-back", False)])
        else:
            self.changes_bar.hide()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "tf-bar-apply":
            self.action_apply()
        elif e.button.id == "tf-bar-back":
            self.query_one(PickerView).rebuild()
            self.query_one(WallpaperView).rebuild()
            self.call_after_refresh(self.refresh_state)

    # ---- apply and undo: hypeForge's own command, in the background ----

    def action_apply(self) -> None:
        if self.busy:
            return
        style, colour = self.picked()
        if not (style and colour):
            self.notify("Pick a theme and its colours first.", severity="warning")
            return
        if not self.pending():
            choice, _ = self.wallpaper_picked()
            self.notify("Pick a picture first." if not choice else "That's the look in use already.")
            return
        view = self.query_one(PickerView)
        wp = None
        if self.wallpaper_pending():
            choice, fit = self.wallpaper_picked()
            wp = {"picture": choice, "fit": fit, "folder": self.query_one("#tf-wp-folder", Input).value.strip() or None}
        words = f"{view.themes_by_slug[style].name} · {view.colours_by_slug[colour].name}" if self.theme_pending() \
            else "the new wallpaper"
        self._run(("apply", style, colour, wp), words)

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
        self.query_one(WallpaperView).rebuild()
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
    cells = measure()               # asked of the terminal before the app takes the keyboard
    app = ThemeForgeApp(cells=cells)
    try:
        app.run()
    finally:
        app.overlay.close()
    return 0
