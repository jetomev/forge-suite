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


class Look:
    """The active style + theme (or the ones given), resolved into colours and shapes."""

    ROLES = ("panel_bg", "panel_text", "panel_text_dim", "panel_border", "panel_tile", "panel_tile_text",
             "panel_tile_on", "panel_tile_on_text", "panel_hover", "panel_selected", "panel_selected_text",
             "panel_danger", "panel_backdrop")

    def __init__(self, style: str | None = None, theme: str | None = None):
        ht = theme_tool()
        st = ht.Place().read_state()
        self.style_slug = style or st.get("style", "classic")
        self.theme_slug = theme or st.get("theme", "kognogos-mocha")
        self.style = ht.styles()[self.style_slug]
        self.theme = ht.themes()[self.theme_slug]
        self.colour = {r: ht.resolve(r, self.style, self.theme) for r in self.ROLES}
        shape = self.style.get("shape", {})
        self.radius = int(shape.get("radius_popup", 0) if not isinstance(shape.get("radius_popup"), dict)
                          else ht.shape_of(self.style, "radius_popup"))
        self.border = int(shape.get("border_popup", 1))
        fonts = self.style.get("fonts", {})
        self.font = fonts.get("ui", "Noto Sans")
        self.size = float(fonts.get("ui_size", 10.5))

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


def screen_in_use():
    """The Gdk monitor of the screen Sway has focus on (matched by position), or None."""
    outputs = [o for o in sway_ask(3) if o.get("active")]          # GET_OUTPUTS
    focused = next((o for o in outputs if o.get("focused")), None)
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


# ---- The panel ------------------------------------------------------------------------------

EDGES = {"top": GtkLayerShell.Edge.TOP, "bottom": GtkLayerShell.Edge.BOTTOM,
         "left": GtkLayerShell.Edge.LEFT, "right": GtkLayerShell.Edge.RIGHT}


class Panel:
    """A pop-up: a card of widgets anchored to `edges` (e.g. ["bottom"] = bottom centre,
    ["top", "right"] = top-right corner, [] = the middle), `margins` in pixels from those edges.
    `dim` darkens the screen around it (the Rice's power buttons)."""

    def __init__(self, view: str, content: Gtk.Widget, look: Look, edges=(), margins=None,
                 dim: bool = False, card: bool = True):
        self.view, self.look = view, look
        provider = Gtk.CssProvider()
        provider.load_from_data(look.css().encode())
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        monitor = screen_in_use()

        # the backdrop: a see-through (or dimmed) layer under the panel that closes it when clicked
        self.backdrop = Gtk.Window()
        self.backdrop.get_style_context().add_class("hf-backdrop")
        if dim:
            self.backdrop.get_style_context().add_class("dim")
        self._layer(self.backdrop, GtkLayerShell.Layer.TOP, monitor, ["top", "bottom", "left", "right"], {})
        self._transparent(self.backdrop)
        self.backdrop.connect("button-press-event", lambda *_: self.close())

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
        self.window.add(content)
        self.window.connect("key-press-event", self._key)
        for w in (self.backdrop, self.window):
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
        self.backdrop.show_all()
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
