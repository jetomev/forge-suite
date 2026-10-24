"""The window menu: a right click on a window's title bar (D-110, Javier, 2026-10-17: "Right click mouse,
window menu… should have an option to make floating window, or get it back into the greed"). One window
with soft lines between its groups, like the tray's menus (D-105), opening at the window's title bar:

  - a head: the app's icon, the window's title, the app's name
  - Float / Back into the grid · Full screen · Show on every workspace (a floating window)
  - Move to workspace ▸ (every workspace by its name; the one it is on, marked)
  - Tuck away (our minimise; the bar's tucked icon brings it back) · Close

Each entry runs `applets/window/hypeforge-window ACTION ID`, and the menu closes.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from pathlib import Path

import panelkit  # first: it picks GTK 3 before anything asks for GTK
from gi.repository import Gdk, GdkPixbuf, Gtk, Pango  # noqa: E402

sys.path.insert(0, str(panelkit.APPLETS / "common"))
from hfapps import Matcher, apps  # noqa: E402
from hficons import Icons  # noqa: E402

WINDOW = panelkit.APPLETS / "window/hypeforge-window"
CSS = """
.hf-card.hf-wm {{ padding: 8px 6px; }}
.hf-wm button {{ background: transparent; border-color: transparent; padding: 4px 10px; border-radius: {inner}px;
                color: {text}; }}
.hf-wm button:hover, .hf-wm button:focus {{ background: {hover}; }}
.hf-wm button label {{ color: {text}; }}
.hf-wm button.hf-wm-danger:hover, .hf-wm button.hf-wm-danger:focus {{ background: {danger}; }}
.hf-wm button.hf-wm-danger:hover label, .hf-wm button.hf-wm-danger:focus label {{ color: {bg}; }}
.hf-wm-mark {{ color: {accent}; min-width: 14px; }}
.hf-wm-key {{ color: {dim}; font-size: {small}pt; }}
.hf-wm-sub {{ margin-left: 14px; }}
.hf-wm button.hf-wm-here label {{ color: {dim}; }}
"""


def find(tree: dict, con_id: int) -> dict | None:
    if tree.get("id") == con_id:
        return tree
    for child in tree.get("nodes", []) + tree.get("floating_nodes", []):
        found = find(child, con_id)
        if found:
            return found
    return None


def workspace_of(tree: dict, con_id: int) -> dict | None:
    for output in tree.get("nodes", []):
        for ws in output.get("nodes", []):
            if ws.get("type") == "workspace" and find(ws, con_id):
                return ws
    return None


def workspace_names() -> list[str]:
    """The workspaces by their names (the Workspaces applet's file, D-47), else Sway's numbers 1-10."""
    base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    try:
        conf = tomllib.loads((base / "hypeforge/applets/workspaces.toml").read_text())
        names = [w.get("name") or f"Workspace {i}" for i, w in enumerate(conf.get("workspace", []), 1)]
        if conf.get("enabled", True) and names:
            return names
    except (OSError, tomllib.TOMLDecodeError):
        pass
    return [f"Workspace {i}" for i in range(1, 11)]


def build(look: panelkit.Look, args) -> panelkit.Panel:
    c = look.colour
    inner = 0 if look.straight else max(4, look.radius // 2)
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(dim=c["panel_text_dim"], small=look.size * 0.9, line=c["panel_border"],
                                       inner=inner, text=c["panel_text"], hover=c["panel_hover"],
                                       danger=c["panel_danger"], bg=c["panel_bg"], accent=c["panel_tile_on"]).encode())
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)

    tree = panelkit.sway_ask(4)                                    # GET_TREE
    con_id = int(args.con) if getattr(args, "con", None) else None
    con = find(tree, con_id) if con_id else None
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    ref = {}

    def close():
        ref["p"].close()

    def run(action: str, *extra: str):
        def clicked(_b):
            close()
            subprocess.Popen([str(WINDOW), action, *extra, str(con_id)])
        return clicked

    def line():                            # the kit's soft line, the one under every head (D-116)
        return panelkit.head_line()

    def entry(words: str, clicked, mark: str = "", key: str = "", danger: bool = False, arrow=None) -> Gtk.Button:
        row = Gtk.Box(spacing=12)
        m = Gtk.Label(label=mark)
        m.get_style_context().add_class("hf-wm-mark")
        row.pack_start(m, False, False, 0)
        row.pack_start(Gtk.Label(label=words, xalign=0), True, True, 0)
        if arrow is not None:
            row.pack_end(arrow, False, False, 0)
        if key:
            k = Gtk.Label(label=key)
            k.get_style_context().add_class("hf-wm-key")
            row.pack_end(k, False, False, 0)
        b = Gtk.Button()
        b.add(row)
        if danger:
            b.get_style_context().add_class("hf-wm-danger")
        if clicked:
            b.connect("clicked", clicked)
        return b

    # ---- the head
    head = Gtk.Box(spacing=10)
    head.get_style_context().add_class("hf-head")
    entries = apps()
    app = Matcher(entries).of_window(con) if con else None
    app_name = entries[app]["name"] if app in entries else ((con or {}).get("app_id") or "A window")
    path = Icons().find(entries[app]["icon"]) if app in entries else None
    image = Gtk.Image()
    try:
        image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(path, 24, 24))
    except Exception:
        image.set_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
    head.pack_start(image, False, False, 0)
    words = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    title = Gtk.Label(label=(con or {}).get("name") or app_name, xalign=0, ellipsize=Pango.EllipsizeMode.END,
                      max_width_chars=30)
    title.get_style_context().add_class("hf-head-name")
    words.pack_start(title, False, False, 0)
    sub = Gtk.Label(label=app_name, xalign=0, ellipsize=Pango.EllipsizeMode.END, max_width_chars=30)
    sub.get_style_context().add_class("hf-head-sub")
    words.pack_start(sub, False, False, 0)
    head.pack_start(words, True, True, 0)
    root.pack_start(head, False, False, 0)

    if con is None:
        root.pack_start(line(), False, False, 0)
        root.pack_start(Gtk.Label(label="That window has gone."), False, False, 6)
    else:
        floating = con.get("type") == "floating_con"
        # ---- how it sits
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(entry("Back into the grid" if floating else "Float", run("tile" if floating else "float"),
                             key="Win + Shift + Space"), False, False, 0)
        box.pack_start(entry("Full screen", run("fullscreen"), mark="✓" if con.get("fullscreen_mode") else "",
                             key="Win + Shift + F"), False, False, 0)
        if floating:
            box.pack_start(entry("Show on every workspace", run("sticky"), mark="✓" if con.get("sticky") else ""),
                           False, False, 0)
        root.pack_start(line(), False, False, 0)
        root.pack_start(box, False, False, 0)

        # ---- where it is
        here = workspace_of(tree, con_id)
        here_num = (here or {}).get("num")
        names = workspace_names()
        sub_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sub_box.get_style_context().add_class("hf-wm-sub")
        for n, name in enumerate(names, 1):
            b = entry(f"{n} · {name}", run("to", str(n)), mark="●" if n == here_num else "")
            if n == here_num:
                b.get_style_context().add_class("hf-wm-here")
                b.set_sensitive(False)
            sub_box.pack_start(b, False, False, 0)
        sub_box.set_no_show_all(True)
        arrow = Gtk.Label(label="▸")
        opener = entry("Move to workspace", None, key="Win + Shift + 1…9", arrow=arrow)

        def toggle(_b):
            opening = not sub_box.get_visible()
            sub_box.set_visible(opening)
            if opening:
                sub_box.show_all()
            arrow.set_label("▾" if opening else "▸")
        opener.connect("clicked", toggle)
        moves = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        moves.pack_start(opener, False, False, 0)
        moves.pack_start(sub_box, False, False, 0)
        root.pack_start(line(), False, False, 0)
        root.pack_start(moves, False, False, 0)

        # ---- away
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(entry("Tuck away", run("tuck"), key="middle click"), False, False, 0)
        box.pack_start(entry("Close", run("close"), key="Win + Shift + Q", danger=True), False, False, 0)
        root.pack_start(line(), False, False, 0)
        root.pack_start(box, False, False, 0)

    # ---- where: at the window's title bar, on its screen (kept on the screen)
    edges, margins = ["top", "left"], {"top": 60, "left": 60}
    if con:
        out = next((o for o in tree.get("nodes", []) if find(o, con_id)), None)
        if out:
            r, d = con["rect"], con.get("deco_rect") or {}
            top_of = r["y"] - (d.get("height") or 0)
            x = r["x"] + 8 - out["rect"]["x"]
            y = top_of + (d.get("height") or 0) - out["rect"]["y"]
            margins = {"left": max(8, min(x, out["rect"]["width"] - 300)),
                       "top": max(8, min(y, out["rect"]["height"] - 420))}
    panel = panelkit.Panel("windowmenu", root, look, edges=edges, margins=margins, width=panelkit.NARROW)
    frame = panel.window.get_child()
    frame.get_style_context().add_class("hf-wm")
    frame.get_style_context().add_class("hf-card")
    frame.set_child_packing(root, True, True, 0, Gtk.PackType.START)
    ref["p"] = panel
    return panel
