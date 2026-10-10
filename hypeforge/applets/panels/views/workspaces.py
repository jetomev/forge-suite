"""The workspaces strip (Windows 11's Workspaces button, D-71): a card per workspace with its
name, the icons of what is open on it (every screen together) and how many; the one on screen
is marked; a click takes every screen there (the Workspaces applet's `go`). Sway can't draw
live pictures of windows, so the cards show which apps are where — honest, and fast.
"""

from __future__ import annotations

import shlex
import sys
import tomllib
from pathlib import Path

from gi.repository import GdkPixbuf, Gtk

import panelkit

sys.path.insert(0, str(panelkit.APPLETS / "common"))
from hfapps import Matcher, all_windows, apps  # noqa: E402
from hficons import Icons  # noqa: E402

WORKSPACES = panelkit.APPLETS / "workspaces/hypeforge-workspaces"
CONFIG = Path(panelkit.os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "hypeforge/applets/workspaces.toml"
CURRENT = panelkit.RUNTIME / "hypeforge-workspaces.current"
ICONS_SHOWN = 6
CSS = """
.hf-ws {{ min-width: 150px; min-height: 92px; padding: 10px 12px; }}
.hf-ws.on {{ border: 2px solid {accent}; background: {tile}; color: {text}; }}
.hf-ws .hf-ws-name {{ font-weight: bold; }}
.hf-ws .hf-ws-count {{ color: {dim}; font-size: {small}pt; }}
"""


def workspace_names() -> list[str]:
    try:
        with open(CONFIG, "rb") as f:
            return [w["name"] for w in tomllib.load(f).get("workspace", [])][:9]
    except (OSError, tomllib.TOMLDecodeError):
        return []


def current() -> int:
    try:
        return int(CURRENT.read_text())
    except (OSError, ValueError):
        return 1


def index_of(sway_name: str, count: int) -> int | None:
    """A Sway workspace name like "14:Gaming" → workspace 4 (screens add 10 each); shared spaces
    (101:Shared…) belong to none."""
    number = sway_name.split(":", 1)[0]
    if not number.isdigit() or int(number) >= 100:
        return None
    i = int(number) % 10
    return i if 1 <= i <= count else None


def apps_per_workspace(tree, entries: dict, matcher: Matcher, count: int) -> dict[int, list[str]]:
    """{workspace: [app ids, one per app, first opened first]}, every screen together."""
    out: dict[int, list[str]] = {i: [] for i in range(1, count + 1)}
    for output in tree.get("nodes", []):
        for ws in output.get("nodes", []):
            i = index_of(ws.get("name", ""), count)
            if i is None:
                continue
            for w in sorted(all_windows(ws), key=lambda n: n["id"]):
                app = matcher.of_window(w) or (w.get("app_id") or "window")
                if app not in out[i]:
                    out[i].append(app)
    return out


def build(look: panelkit.Look, args) -> panelkit.Panel:
    c = look.colour
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(accent=c["panel_tile_on"], tile=c["panel_tile"], text=c["panel_text"],
                                       dim=c["panel_text_dim"], small=look.size * 0.85).encode())
    Gtk.StyleContext.add_provider_for_screen(panelkit.Gdk.Screen.get_default(), provider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
    names = workspace_names()
    entries, icons = apps(), Icons()
    per = apps_per_workspace(panelkit.sway_ask(4), entries, Matcher(entries), len(names))   # GET_TREE
    here = current()
    row = Gtk.Box(spacing=12)

    def go(_b, i):
        panel.close()
        panelkit.run_command(f"{shlex.quote(str(WORKSPACES))} go {i}")

    for i, name in enumerate(names, 1):
        b = Gtk.Button()
        b.get_style_context().add_class("hf-ws")
        if i == here:
            b.get_style_context().add_class("on")
        col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        top = Gtk.Box()
        n = Gtk.Label(label=name, xalign=0)
        n.get_style_context().add_class("hf-ws-name")
        top.pack_start(n, True, True, 0)
        top.pack_end(Gtk.Label(label=str(i)), False, False, 0)
        col.pack_start(top, False, False, 0)
        strip = Gtk.Box(spacing=6)
        for app in per.get(i, [])[:ICONS_SHOWN]:
            image = Gtk.Image()
            path = icons.find(entries[app]["icon"]) if app in entries else None
            try:
                image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(path, 24, 24))
            except Exception:
                image.set_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
            image.set_tooltip_text(entries[app]["name"] if app in entries else app)
            strip.pack_start(image, False, False, 0)
        col.pack_start(strip, False, False, 0)
        k = len(per.get(i, []))
        count = Gtk.Label(label=f"{k} app{'s' if k != 1 else ''} open" if k else "empty", xalign=0)
        count.get_style_context().add_class("hf-ws-count")
        col.pack_end(count, False, False, 0)
        b.add(col)
        b.connect("clicked", go, i)
        row.pack_start(b, False, False, 0)

    edges = args.edges.split(",") if getattr(args, "edges", None) else ["bottom"]
    margins = dict(m.split("=") for m in args.margin.split(",")) if getattr(args, "margin", None) else {"bottom": 60}
    panel = panelkit.Panel("workspaces", row, look, edges=edges, margins={k: int(v) for k, v in margins.items()})
    return panel
