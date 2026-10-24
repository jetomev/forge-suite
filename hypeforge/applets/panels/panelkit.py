"""hypeForge panels · the shared core of every graphical pop-up (look program step 4, D-68 Q-2).

Python + GTK 3 + gtk-layer-shell, all already on the system. A view (views/<name>.py) builds its
widgets; this core gives it:
  - the look: colours from the active theme and corners from the active style, through the theme
    engine's own roles (hypeforge-theme), so any theme on any style just works
  - a place: a layer-shell surface on the screen in use, anchored where the view asks
  - closing: Escape, a click outside (a see-through backdrop under the panel), or the same button
    again (`toggle`: a second call closes the open one)
The Forge apps stay terminal apps; only these small pop-ups from the bar are graphical (D-68).
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import signal
import socket
import struct
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gdk, GLib, Gtk, GtkLayerShell  # noqa: E402

HERE = Path(__file__).resolve().parent
APPLETS = HERE.parent
RUNTIME = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp"))
NAMESPACE = "hypeforge-panel"      # SwayFX's layer_effects can frost and round it


# ---- The look --------------------------------------------------------------------------------

def theme_tool():
    loader = importlib.machinery.SourceFileLoader("hypeforge_theme", str(APPLETS / "theme/hypeforge-theme"))
    spec = importlib.util.spec_from_loader("hypeforge_theme", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


# D-116: three widths only (Javier, 2026-10-24: "300 · 380 · 460"). Narrow: menus and lists, the small
# pop-ups from a bar icon; medium: Calendar, System; wide: Quick Settings, Clipboard, Temperature. Workspaces
# and the window switcher grow with their tiles; Power has no card.
NARROW, MEDIUM, WIDE = 300, 380, 460


class Look:
    """The active style + theme (or the ones given), resolved into colours and shapes."""

    ROLES = ("panel_bg", "panel_text", "panel_text_dim", "panel_border", "panel_tile", "panel_tile_text",
             "panel_tile_on", "panel_tile_on_text", "panel_hover", "panel_selected", "panel_selected_text",
             "panel_danger", "panel_backdrop")

    FONT, SIZE, BORDER, RADIUS = "Noto Sans", 10.5, 1, 10      # the pop-up standard (D-116)

    def __init__(self, style: str | None = None, theme: str | None = None):
        ht = theme_tool()
        st = ht.Place().read_state()
        self.style_slug = style or st.get("style", "classic")
        self.theme_slug = theme or st.get("theme", "kognogos-mocha")
        self.style = ht.with_corners(ht.styles()[self.style_slug], st.get("corners", "style"))
        self.theme = ht.themes()[self.theme_slug]
        self.straight = self.style.get("corners") == "straight"
        self.pill = 0 if self.straight else 999       # round things (buttons, sliders) follow the corners too
        self.colour = {r: ht.resolve(r, self.style, self.theme) for r in self.ROLES}
        # D-116 (Javier, 2026-10-20): ONE pop-up standard on every style for KognogOS v1.0 — one font,
        # one size, one frame; only the colours follow the theme. Corners follow the corners switch:
        # square when it says straight, else one rounding (pop-ups have no style of their own in v1.0).
        self.radius = 0 if self.straight else self.RADIUS
        self.border = self.BORDER
        self.font = self.FONT
        self.size = self.SIZE

    def rgba(self, role: str, alpha: float) -> str:
        h = self.colour[role].lstrip("#")
        return f"rgba({int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}, {alpha})"

    def css(self) -> str:
        c = self.colour
        return f"""
* {{ font-family: "{self.font}", sans-serif; font-size: {self.size}pt; }}
window.hf-backdrop {{ background: transparent; }}
window.hf-backdrop.dim {{ background: {self.rgba("panel_backdrop", 0.78)}; }}
window.hf-panel {{ background: transparent; }}
.hf-card {{ background: {c["panel_bg"]}; color: {c["panel_text"]}; border: {self.border}px solid {c["panel_border"]};
            border-radius: {self.radius}px; padding: 14px; }}
.hf-dim {{ color: {c["panel_text_dim"]}; }}
.hf-title {{ font-weight: bold; font-size: {self.size * 1.25}pt; }}
/* D-116: the one title row every pop-up wears (the tray menu's): a symbol or icon, the name in bold,
   a dim line under it when there is one, and a soft line that fades at both ends below the head */
.hf-head {{ padding: 2px 4px 2px 8px; }}
.hf-head-name {{ font-weight: bold; font-size: {self.size * 1.1}pt; }}
.hf-head-glyph {{ font-family: "Symbols Nerd Font", "{self.font}"; font-size: {self.size * 1.35}pt; color: {c["panel_tile_on"]}; }}
.hf-head-sub {{ color: {c["panel_text_dim"]}; font-size: {self.size * 0.9}pt; }}
.hf-head-line {{ min-height: 1px; margin: 5px 6px; border: none; background-color: transparent;
                 background-image: linear-gradient(to right, transparent, {c["panel_border"]} 15%, {c["panel_border"]} 85%, transparent); }}
button {{ background: {c["panel_tile"]}; color: {c["panel_tile_text"]}; border: 1px solid {c["panel_border"]};
          border-radius: {max(4, self.radius // 2)}px; box-shadow: none; background-image: none; text-shadow: none; padding: 6px 10px; }}
button:hover, button:focus {{ background: {c["panel_hover"]}; outline: none; }}
button.on {{ background: {c["panel_tile_on"]}; color: {c["panel_tile_on_text"]}; border-color: {c["panel_tile_on"]}; }}
button.danger:hover, button.danger:focus {{ background: {c["panel_danger"]}; color: {c["panel_bg"]}; }}
button.flat {{ background: transparent; border-color: transparent; }}
button.flat:hover, button.flat:focus {{ background: {c["panel_hover"]}; }}
.hf-selected {{ background: {c["panel_selected"]}; color: {c["panel_selected_text"]}; }}
entry {{ background: {c["panel_tile"]}; color: {c["panel_text"]}; border: 1px solid {c["panel_border"]};
         border-radius: {max(4, self.radius // 2)}px; padding: 6px 10px; box-shadow: none; }}
"""


def head_line() -> "Gtk.Separator":
    """The soft line under a pop-up's title row (D-116): the same on every pop-up."""
    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.get_style_context().add_class("hf-head-line")
    return sep


def titled(content: "Gtk.Widget", name: str, glyph: str = "", spacing: int = 8) -> "Gtk.Box":
    """`content` with the one title row on top (D-116): the name in bold (an optional symbol before it)
    and the soft line under it. Returns the box to give the Panel; the name label is `box.title`."""
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    head = Gtk.Box(spacing=8)
    head.get_style_context().add_class("hf-head")
    if glyph:
        g = Gtk.Label(label=glyph)
        g.get_style_context().add_class("hf-head-glyph")
        head.pack_start(g, False, False, 0)
    label = Gtk.Label(label=name, xalign=0)
    label.get_style_context().add_class("hf-head-name")
    head.pack_start(label, True, True, 0)
    box.pack_start(head, False, False, 0)
    box.pack_start(head_line(), False, False, 0)
    content.set_margin_top(spacing - 5 if spacing > 5 else 0)
    box.pack_start(content, True, True, 0)
    box.title = label
    return box


# ---- Where: the screen in use ----------------------------------------------------------------

def sway_ask(kind: int, payload: str = ""):
    path = os.environ.get("SWAYSOCK")
    if not path:
        return []
    with socket.socket(socket.AF_UNIX) as s:
        s.connect(path)
        data = payload.encode()
        s.sendall(b"i3-ipc" + struct.pack("=II", len(data), kind) + data)
        head = s.recv(14, socket.MSG_WAITALL)
        size, _ = struct.unpack("=II", head[6:])
        return json.loads(s.recv(size, socket.MSG_WAITALL))


def output_in_use(outputs: list[dict], env=os.environ) -> dict | None:
    """The screen a panel opens on: the one whose bar was clicked (HYPEFORGE_OUTPUT, set by
    hypeforge-bar on each screen's bar — Javier, 2026-10-10: they all opened on the left screen),
    else the one Sway has focus on (a key, Win + Space)."""
    active = [o for o in outputs if o.get("active")]
    named = env.get("HYPEFORGE_OUTPUT")
    return (next((o for o in active if o.get("name") == named), None) if named else None) \
        or next((o for o in active if o.get("focused")), None)


def screen_in_use():
    """The Gdk monitor of that screen (matched by position), or None."""
    focused = output_in_use(sway_ask(3))                             # GET_OUTPUTS
    if not focused:
        return None
    display = Gdk.Display.get_default()
    for i in range(display.get_n_monitors()):
        m = display.get_monitor(i)
        g = m.get_geometry()
        if (g.x, g.y) == (focused["rect"]["x"], focused["rect"]["y"]):
            return m
    return None


# ---- One panel open at a time per view; the same button again closes it -----------------------

def pidfile(view: str) -> Path:
    return RUNTIME / f"hypeforge-panel-{view}.pid"


def close_open(view: str) -> bool:
    """If this view is already open, close it and say so (the button pressed again)."""
    try:
        pid = int(pidfile(view).read_text())
        os.kill(pid, signal.SIGTERM)
        return True
    except (OSError, ValueError):
        return False


def nudge_open(view: str, back: bool = False) -> bool:
    """If this view is open, tell it to move on (Alt + Tab pressed again) instead of closing it."""
    try:
        pid = int(pidfile(view).read_text())
        if b"hypeforge-panel" not in Path(f"/proc/{pid}/cmdline").read_bytes():
            return False                                   # a reused process number: not ours
        os.kill(pid, signal.SIGUSR2 if back else signal.SIGUSR1)
        return True
    except (OSError, ValueError):
        return False


# ---- The panel ------------------------------------------------------------------------------

EDGES = {"top": GtkLayerShell.Edge.TOP, "bottom": GtkLayerShell.Edge.BOTTOM,
         "left": GtkLayerShell.Edge.LEFT, "right": GtkLayerShell.Edge.RIGHT}


class Panel:
    """A pop-up: a card of widgets anchored to `edges` (e.g. ["bottom"] = bottom centre,
    ["top", "right"] = top-right corner, [] = the middle), `margins` in pixels from those edges.
    `dim` darkens the screen around it (the Rice's power buttons). `width` is one of NARROW, MEDIUM, WIDE: the
    card's visible width, put on the outermost piece (the card, or a stack of cards) so a number means the
    same on every pop-up (D-116)."""

    def __init__(self, view: str, content: Gtk.Widget, look: Look, edges=(), margins=None,
                 dim: bool = False, card: bool = True, width: int | None = None):
        self.view, self.look = view, look
        provider = Gtk.CssProvider()
        provider.load_from_data(look.css().encode())
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        monitor = screen_in_use()

        # the backdrops: a see-through layer on EVERY screen under the panel — a click anywhere
        # else closes it (Javier, 2026-10-10); `dim` darkens the panel's own screen
        sys.path.insert(0, str(APPLETS / "common"))
        import hfbackdrop
        self.backdrops = hfbackdrop.backdrops(self.close, dim_monitor=monitor if dim else None,
                                              dim_rgba=look.rgba("panel_backdrop", 0.78) if dim else None)

        self.window = Gtk.Window()
        self.window.get_style_context().add_class("hf-panel")
        self._layer(self.window, GtkLayerShell.Layer.OVERLAY, monitor, list(edges), margins or {})
        GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        self._transparent(self.window)
        if card:
            box = Gtk.Box()
            box.get_style_context().add_class("hf-card")
            box.add(content)
            content = box
        if width:
            content.set_size_request(width, -1)
        self.window.add(content)
        self.window.connect("key-press-event", self._key)
        for w in self.backdrops + [self.window]:
            w.connect("destroy", lambda *_: self.close())

    @staticmethod
    def _transparent(window):
        visual = window.get_screen().get_rgba_visual()
        if visual:
            window.set_visual(visual)
        window.set_app_paintable(False)

    @staticmethod
    def _layer(window, layer, monitor, edges, margins):
        GtkLayerShell.init_for_window(window)
        GtkLayerShell.set_namespace(window, NAMESPACE)
        GtkLayerShell.set_layer(window, layer)
        GtkLayerShell.set_exclusive_zone(window, -1)       # over the bar too, never pushing anything
        if monitor is not None:
            GtkLayerShell.set_monitor(window, monitor)
        for name, edge in EDGES.items():
            GtkLayerShell.set_anchor(window, edge, name in edges)
            GtkLayerShell.set_margin(window, edge, int(margins.get(name, 0)))

    def _key(self, _w, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False

    def close(self, *_):
        pidfile(self.view).unlink(missing_ok=True)
        if Gtk.main_level():
            Gtk.main_quit()

    def run(self):
        pidfile(self.view).write_text(str(os.getpid()))
        signal.signal(signal.SIGTERM, lambda *_: GLib.idle_add(self.close))
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, lambda *_: (self.close(), False)[1])
        for w in self.backdrops:
            w.show_all()
        self.window.show_all()
        try:
            Gtk.main()
        finally:
            pidfile(self.view).unlink(missing_ok=True)


def run_command(command: str):
    """Start a command the way the bar does: through Sway, so it outlives the panel."""
    if os.environ.get("SWAYSOCK"):
        sway_ask(0, f"exec {command}")
    else:
        os.spawnlp(os.P_NOWAIT, "sh", "sh", "-c", command)
