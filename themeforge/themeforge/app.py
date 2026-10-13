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
from rich.markup import escape
from textual.widgets import Button, OptionList, Select, Static
from textual.widgets.option_list import Option

from forgekit import FORGE_CSS, GPL3_NOTICE, MENU_HINT, ForgeApp, a_file, load_pages, start_check
from forgekit.console import glyph

from . import __version__
from .browse import THEME_MADE, FolderPicker, tilde
from .look import FIT_ABOUT, FITS, Look
from .preview import overlay_picture, preview
from .termcell import Cells, measure, settings_shows_me

MANUAL_DIR = os.path.join(os.path.dirname(__file__), "manual")

TF_CSS = FORGE_CSS + """
/* the options: a matrix of two columns going down (Javier, 2026-10-11), compact with air between */
#tf-options { grid-size: 2; grid-gutter: 0 4; height: auto; margin: 1 2 0 2; }
.tf-cell { height: auto; }
.tf-row { height: 1; }
.tf-name { width: 10; color: $forge-accent; text-style: bold; }
.tf-row Select { width: 1fr; height: 1; }
.tf-row SelectCurrent { border: none; height: 1; padding: 0 1; background: $forge-surface; }
.tf-row Select:focus > SelectCurrent { border: none; background: $forge-focus-bg; }
.tf-under { height: auto; padding: 0 0 0 11; margin: 1 0 0 0; color: $forge-muted; }
#tf-brings-title { margin: 1 2 0 2; color: $forge-accent; text-style: bold; height: 1; }
#tf-brings { grid-size: 4; grid-columns: 14 1fr 14 1fr; grid-gutter: 0 3; height: auto; margin: 0 2 0 2; }
#tf-brings Static { height: auto; }
.tf-el { color: $forge-muted; }
#tf-foot { height: 1; margin: 1 2 0 2; }
#tf-now { width: 1fr; height: 1; }
/* the Wallpaper page (D-8): Source + Browse and Fit Style in the matrix, the Images list under them,
   the preview under the list, Apply Background in the foot */
#tf-wp-options { grid-size: 2; grid-gutter: 0 4; height: auto; margin: 1 2 0 2; }
.tf-row .tf-value { width: 1fr; height: 1; padding: 0 1; background: $forge-surface; }
#tf-wp-images-row { height: auto; margin: 1 2 0 2; }
#tf-wp-images { width: 1fr; height: 8; border: solid $forge-field-border; padding: 0; }
#tf-wp-images:focus { border: solid $forge-accent; }
#tf-wp-preview { width: auto; height: auto; margin: 1 2 0 11; border: round $forge-muted; }
#tf-wp-caption { height: 1; margin: 0 2 0 11; color: $forge-muted; }
#tf-wp-foot { height: 1; margin: 1 2 0 2; }
#tf-wp-now { width: 1fr; height: 1; }
/* the Browse window (D-10): the folders as a tree on the left, the pictures of the one under the cursor
   on the right, like a small file manager */
.tf-browse { width: 100; }
#tf-br-where { height: 1; padding: 0 1; }
#tf-br-panes { height: 18; }
#tf-br-tree { width: 42; height: 100%; border: solid $forge-field-border; background: $forge-surface; padding: 0 1; overflow-x: hidden; }
#tf-br-tree:focus { border: solid $forge-accent; }
#tf-br-tree > .tree--cursor { background: $forge-selected-bg; color: $forge-selected; text-style: $forge-strong; }
#tf-br-tree > .tree--guides { color: $forge-muted; }
#tf-br-files { width: 1fr; height: 100%; margin: 0 0 0 1; }
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
            c = self.cells
            if c.origin:                                   # inside Settings: our cells, in the terminal's grid
                cells = (cells[0] + c.origin[0], cells[1] + c.origin[1], cells[2], cells[3])
                grid = c.grid or grid
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


def made_by_theme(choice: str | None) -> bool:
    """A choice hypeForge draws (not a file of yours)."""
    return bool(choice) and (choice in ("theme", "solid") or choice.startswith("kognogos:"))


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
    """Desktop background (Javier, 2026-10-11, D-6 then D-8): every screen the same picture. **Source**
    is a folder, with Browse to walk to another (or "The theme's pictures": the theme's own, the KognogOS
    backgrounds and the solid colour, drawn in the colours picked); **Images** lists every picture in it;
    pick one and it shows below, at full quality on hypeForge; **Fit Style** says how it lies; **Apply
    Background** sets it."""

    FORGE_HINTS = [("Tab", "next"), ("Enter", "pick"), ("b", "browse"), ("F10", "apply"), ("u", "undo"), MENU_HINT]

    def __init__(self, look: Look, **kw) -> None:
        super().__init__(**kw)
        self.look = look
        self.source = THEME_MADE
        self.pick: str | None = None
        self.sync_from_desktop()

    def sync_from_desktop(self) -> None:
        """The Source and the pick follow what is on screen (hypeforge-theme's own memory)."""
        choice, _ = self.look.wallpaper_now()
        if made_by_theme(choice):
            self.source, self.pick = THEME_MADE, choice
        elif Path(choice).is_file():
            self.source, self.pick = str(Path(choice).parent), choice
        else:
            self.source, self.pick = str(self.look.folder()), None

    # ---- what can be picked ----

    def theme_entries(self) -> list[tuple[str, str]]:
        """[(value, words)] of the theme's pictures: the theme's own (the theme picked on the Theme Picker),
        the KognogOS backgrounds, the solid colour."""
        style = (self.app.picked() if hasattr(self.app, "picked") else (None, None))[0] or self.look.current()[0]
        topic = self.look.topic(style) if style else ""
        out = [("theme", "The theme's own" + (f" — {topic}" if topic else ""))]
        out += [(f"kognogos:{slug}", f"KognogOS · {name}") for slug, name in self.look.kognogos_designs()]
        out += [("solid", "Solid colour — the theme's own")]
        return out

    def entries(self) -> list[tuple[str, str]]:
        """[(value, words)]: what the Source holds."""
        if self.source == THEME_MADE:
            return self.theme_entries()
        return [(str(p), p.name) for p in self.look.pictures(Path(self.source))]

    def folder_for_file(self) -> str | None:
        """The folder the look file remembers: the Source when it is a real folder."""
        return None if self.source == THEME_MADE else self.source

    def compose(self) -> ComposeResult:
        _, fit = self.look.wallpaper_now()
        with Grid(id="tf-wp-options"):
            with Vertical(classes="tf-cell"):
                with Horizontal(classes="tf-row"):
                    yield Static("Source", classes="tf-name")
                    yield Static("", id="tf-wp-source", classes="tf-value")
                    yield Button("Browse (b)", id="tf-wp-browse", classes="tf-small")
                yield Static("", id="tf-wp-source-about", classes="tf-under")
            with Vertical(classes="tf-cell"):
                with Horizontal(classes="tf-row"):
                    yield Static("Fit Style", classes="tf-name")
                    yield Select([(words, key) for key, words in FITS.items()],
                                 value=fit if fit in FITS else "fill", allow_blank=False, id="tf-wp-fit")
                yield Static("", id="tf-wp-fit-about", classes="tf-under")
        with Horizontal(id="tf-wp-images-row"):
            yield Static("Images", classes="tf-name")
            yield OptionList(id="tf-wp-images")
        yield Static("", id="tf-wp-preview")
        yield Static("", id="tf-wp-caption")
        with Horizontal(id="tf-wp-foot"):
            yield Static("", id="tf-wp-now")
            yield Button("Make Folder (n)", id="tf-wp-mkdir", classes="tf-small")
            yield Button("Apply Background (F10)", id="tf-wp-apply", classes="tf-small")
            yield Button("Undo Last Apply (u)", id="tf-wp-undo", classes="tf-small")

    def on_mount(self) -> None:
        self.fill_list()
        self.refresh_words()

    def fill_list(self) -> None:
        """The Images list: every picture in the Source, the one in use and the one picked marked."""
        ol = self.query_one("#tf-wp-images", OptionList)
        ol.clear_options()
        in_use, _ = self.look.wallpaper_now()
        at = None
        for value, words in self.entries():
            mark = (f"[$forge-ok]{glyph('ok')}[/]" if value == in_use else
                    f"[$forge-changed]{glyph('changed')}[/]" if value == self.pick else " ")
            tail = "  [$forge-muted]· in use[/]" if value == in_use else ""
            if value == self.pick:
                at = ol.option_count
            ol.add_option(Option(f"{mark} {escape(words)}{tail}", id=value))
        if self.pick is not None and at is None:
            self.pick = None                                   # the pick isn't in this Source any more
        ol.highlighted = at if at is not None else (0 if ol.option_count else None)

    # ---- what is picked ----

    def chosen(self) -> tuple[str | None, str]:
        """(the wallpaper choice, the fit); the choice is None until a picture is picked."""
        return self.pick, str(self.query_one("#tf-wp-fit", Select).value)

    def refresh_words(self) -> None:
        made = self.source == THEME_MADE
        folder = Path(self.source).expanduser() if not made else None
        exists = made or folder.is_dir()
        n = len(self.entries()) if exists else 0
        self.show_source()
        self.query_one("#tf-wp-source-about", Static).update(
            f"{n} pictures, drawn in the colours you picked." if made else
            f"{n} picture{'s' if n != 1 else ''} here (PNG, JPEG, WebP…)." if exists else
            "This folder doesn't exist yet: Make Folder (n), then put pictures in it.")
        self.query_one("#tf-wp-mkdir", Button).display = not exists
        fit = str(self.query_one("#tf-wp-fit", Select).value)
        self.query_one("#tf-wp-fit-about", Static).update(FIT_ABOUT.get(fit, ""))
        choice, fit_now = self.look.wallpaper_now()
        self.query_one("#tf-wp-now", Static).update(
            f"[$forge-accent b]In use now: [/]{escape(plain(choice))}  ·  {FITS.get(fit_now, fit_now)}  ·  every screen")
        self.refresh_buttons()
        self.draw()

    def show_source(self) -> None:
        """The Source line: a long path keeps its end (the folder's name is what tells it apart)."""
        box = self.query_one("#tf-wp-source", Static)
        words = "The theme's pictures" if self.source == THEME_MADE else tilde(self.source)
        room = box.content_region.width or box.size.width - 2
        if 0 < room < len(words):
            words = "…" + words[-(room - 1):]
        box.update(escape(words))

    def on_resize(self) -> None:
        if self.is_mounted:
            self.show_source()

    def refresh_buttons(self) -> None:
        pending = self.app.wallpaper_pending() if hasattr(self.app, "wallpaper_pending") else False
        self.query_one("#tf-wp-apply", Button).disabled = not pending

    @work(thread=True, exclusive=True, group="tf-wp-preview")
    def draw(self) -> None:
        choice, fit = self.chosen()
        style, theme = self.app.picked() if hasattr(self.app, "picked") else self.look.current()
        style, theme = style or self.look.current()[0], theme or self.look.current()[1]
        self.app.call_from_thread(self.query_one("#tf-wp-caption", Static).update, "drawing the preview…")
        if not (choice and style and theme):
            self.app.call_from_thread(self._show, "", "Pick a picture above to see it here.")
            return
        solid = self.look.picture_path(style, theme, "solid")
        try:
            from PIL import Image
            with Image.open(solid) as im:
                bg = im.convert("RGB").getpixel((0, 0))
        except Exception:
            bg = (30, 30, 46)
        path = self.look.picture_path(style, theme, choice) if made_by_theme(choice) else Path(choice)
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
        self.app.call_from_thread(self._show, text,
                                  plain(choice) + (f", in {theme_name}" if made_by_theme(choice) else "")
                                  + f"  ·  {FITS.get(fit, fit)}")

    def _show(self, text, caption: str) -> None:
        if not text:
            self.overlay_png = None
        self.query_one("#tf-wp-preview", Static).update(text)
        self.query_one("#tf-wp-caption", Static).update(caption)

    overlay_png: str | None = None

    def overlay_spot(self) -> tuple[int, int, int, int] | None:
        """The preview's character cells on the screen, when the full picture may cover them: this page
        shown, no list open over it, no other screen (Browse, the manual, a question) on top, all of it
        in view."""
        if not (self.overlay_png and self.display and self.app.screen is self.screen):
            return None
        if any(s.expanded for s in self.query(Select)):
            return None
        if not settings_shows_me():                     # inside Settings: another page is on screen
            return None
        box = self.query_one("#tf-wp-preview", Static).content_region
        size = self.app.size
        if box.width < 4 or box.height < 2 or box.x < 0 or box.y < 0 or \
                box.right > size.width or box.bottom > size.height:
            return None
        return box.x, box.y, box.width, box.height

    # ---- the person's moves ----

    def on_option_list_option_selected(self, e: OptionList.OptionSelected) -> None:
        if e.option_list.id == "tf-wp-images":
            e.stop()
            self.pick = e.option.id
            self.fill_list()
            self.refresh_words()
            self.app.refresh_state()

    def on_select_changed(self, e: Select.Changed) -> None:
        if e.select.id == "tf-wp-fit":
            e.stop()
            self.refresh_words()
            self.app.refresh_state()

    def browse(self) -> None:
        """Browse (b): the file-manager window (D-10); the Source follows its answer, and the pick too
        when a picture was chosen there."""
        self.app.push_screen(FolderPicker(self.source, theme_entries=self.theme_entries()), self.source_picked)

    def source_picked(self, result: dict | None) -> None:
        if not result or not result.get("source"):
            return
        self.use_source(result["source"], result.get("pick"))
        self.query_one("#tf-wp-images", OptionList).focus()

    def use_source(self, source: str, pick: str | None = None) -> None:
        """A Source picked in Browse: the picture chosen there, else the one on screen if it lives here,
        else the first one (Javier, 2026-10-13: "the first image of the list should show automatically")."""
        self.source = source
        in_use, _ = self.look.wallpaper_now()
        here = [v for v, _ in self.entries()]
        self.pick = pick if pick in here else in_use if in_use in here else here[0] if here else None
        self.fill_list()
        self.refresh_words()
        self.app.refresh_state()

    def make_folder(self) -> None:
        if self.source == THEME_MADE:
            return
        folder = Path(self.source).expanduser()
        if folder.is_dir():
            return
        try:
            folder.mkdir(parents=True)
        except OSError as e:
            self.app.notify(f"The folder couldn't be made ({e.strerror}).", severity="error")
            return
        self.app.notify(f"Made {tilde(folder)}. Put your pictures in it; they show up here.", timeout=6)
        self.use_source(self.source)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "tf-wp-undo":
            e.stop()
            self.app.action_undo()
        elif e.button.id == "tf-wp-apply":
            e.stop()
            self.app.action_apply()
        elif e.button.id == "tf-wp-mkdir":
            e.stop()
            self.make_folder()
        elif e.button.id == "tf-wp-browse":
            e.stop()
            self.browse()

    def look_changed(self) -> None:
        """The Theme page picked another theme or colours: the theme's pictures are other pictures."""
        if self.source == THEME_MADE:
            self.fill_list()
        self.refresh_words()

    def rebuild(self) -> None:
        """After an apply or undo: the Source, the pick, the fit and the marks follow the desktop. In place,
        never a recompose (F-71: a rebuilt page came up with an empty Images list and nothing focused)."""
        self.sync_from_desktop()
        _, fit = self.look.wallpaper_now()
        sel = self.query_one("#tf-wp-fit", Select)
        with sel.prevent(Select.Changed):
            sel.value = fit if fit in FITS else "fill"
        self.fill_list()
        self.refresh_words()
        if self.display and self.app.screen is self.screen:
            self.query_one("#tf-wp-images", OptionList).focus()


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
        ("Enter", "Wallpaper: pick the picture under the cursor (it shows below)"),
        ("b", "Wallpaper: browse for another folder"),
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
        Binding("b", "browse", show=False),
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
            self.call_after_refresh(self.query_one("#tf-wp-images").focus)

    def action_make_folder(self) -> None:
        view = self.query_one(WallpaperView)
        if view.display:
            view.make_folder()

    def action_browse(self) -> None:
        view = self.query_one(WallpaperView)
        if view.display and self.screen is view.screen:
            view.browse()

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
        if self.theme_pending() and not self.busy:
            words = (f"{view.themes_by_slug[style].name if style in view.themes_by_slug else style} · "
                     f"{view.colours_by_slug[colour].name if colour in view.colours_by_slug else colour}")
            if self.wallpaper_pending():
                words += " and the wallpaper"
            self.changes_bar.show(f"Picked, not applied yet: {words}", "changed",
                                  [("Apply (F10)", "tf-bar-apply", True), ("Put Back", "tf-bar-back", False)])
        else:
            self.changes_bar.hide()
        for wp in self.query(WallpaperView):            # Apply Background lights up when a wallpaper is picked
            wp.refresh_buttons()

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
            wp = {"picture": choice, "fit": fit, "folder": self.query_one(WallpaperView).folder_for_file()}
        words = f"{view.themes_by_slug[style].name} · {view.colours_by_slug[colour].name}" if self.theme_pending() \
            else f"the wallpaper {plain(wp['picture'])}"
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
