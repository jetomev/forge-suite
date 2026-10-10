"""Start, KDE-style (Windows 11 W-2, D-71): search on top, your groups on the left, the apps on
the right, you and the power buttons at the bottom.

The groups are the launcher's own (sections.toml: Favorites first, then the standard groups,
D-64), so the bar's launcher and this panel always agree; an app opens on its own workspace
through the launcher (`hypeforge-sections launch`). Typing searches every app; Enter opens the
first one shown; Escape closes.
"""

from __future__ import annotations

import getpass
import os
import pwd
import shlex
import sys
from pathlib import Path

from gi.repository import GdkPixbuf, Gtk, Pango

import panelkit

sys.path.insert(0, str(panelkit.APPLETS / "common"))
from hfapps import apps  # noqa: E402
from hficons import Icons  # noqa: E402

LAUNCHER = panelkit.APPLETS / "sections/hypeforge-sections"
COLUMNS = 4
ICON = 40
CELL_W, CELL_H = 124, 96
CSS = """
.hf-start {{ min-width: 700px; }}
.hf-start .hf-side button {{ padding: 7px 12px; }}
.hf-start .hf-side button label {{ font-weight: normal; }}
.hf-start .hf-side button.hf-selected label {{ font-weight: bold; }}
.hf-start .hf-app {{ padding: 10px 4px; min-width: 120px; }}
.hf-start .hf-app label {{ font-size: {small}pt; }}
.hf-start .hf-foot {{ border-top: 1px solid {line}; padding-top: 10px; margin-top: 6px; }}
.hf-start .hf-avatar {{ background: {accent}; color: {on_accent}; border-radius: {pill}px; min-width: 30px; min-height: 30px;
                        font-weight: bold; }}
.hf-start .hf-count {{ color: {dim}; font-size: {small}pt; }}
"""


def display_name() -> str:
    try:
        return pwd.getpwnam(getpass.getuser()).pw_gecos.split(",")[0] or getpass.getuser()
    except KeyError:
        return getpass.getuser()


def groups(entries: dict) -> list[tuple[str, list[str]]]:
    """[(group name, [app ids])]: Favorites, every non-empty launcher group, All apps."""
    sections = panelkit_launcher()
    cfg = sections.load()
    out = []
    favourites = [a for a in cfg.get("favourites", []) if a in entries]
    if favourites:
        out.append(("Favorites", favourites))
    for section, members in sections.sort_into_sections(cfg, entries):
        out.append((section["name"], members))
    out.append(("All apps", sorted(entries, key=lambda a: entries[a]["name"].lower())))
    return out


def panelkit_launcher():
    import importlib.machinery
    import importlib.util
    loader = importlib.machinery.SourceFileLoader("hfsections_start", str(LAUNCHER))
    spec = importlib.util.spec_from_loader("hfsections_start", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def matches(entries: dict, words: str) -> list[str]:
    """Apps whose name (or id) holds every word typed; names that start with it first."""
    terms = words.lower().split()
    hits = [a for a in entries if all(t in (entries[a]["name"] + " " + a).lower() for t in terms)]
    return sorted(hits, key=lambda a: (not entries[a]["name"].lower().startswith(terms[0]) if terms else 0,
                                       entries[a]["name"].lower()))


def build(look: panelkit.Look, args) -> panelkit.Panel:
    entries, icons = apps(), Icons()
    sets = groups(entries)
    c = look.colour
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(small=look.size * 0.92, line=c["panel_border"], accent=c["panel_tile_on"],
                                       on_accent=c["panel_tile_on_text"], dim=c["panel_text_dim"], pill=look.pill).encode())
    Gtk.StyleContext.add_provider_for_screen(panelkit.Gdk.Screen.get_default(), provider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)

    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    root.get_style_context().add_class("hf-start")
    search = Gtk.SearchEntry()
    search.set_placeholder_text("Search apps")
    root.pack_start(search, False, False, 0)

    body = Gtk.Box(spacing=14)
    side = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    side.get_style_context().add_class("hf-side")
    main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    heading = Gtk.Label(xalign=0)
    heading.get_style_context().add_class("hf-title")
    # Packed from the top-left, every icon the same size, empty space left BELOW (Javier, 10-10:
    # "icons should be always arranged top to bottom, left to right, and its area of occupancy
    # always the same"): no stretching to fill the page
    grid = Gtk.FlowBox(max_children_per_line=COLUMNS, min_children_per_line=COLUMNS, homogeneous=True,
                       selection_mode=Gtk.SelectionMode.NONE, column_spacing=4, row_spacing=4,
                       valign=Gtk.Align.START, halign=Gtk.Align.START, vexpand=False)
    scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
    scroll.set_min_content_height(420)
    scroll.set_propagate_natural_width(True)
    scroll.add(grid)
    main.pack_start(heading, False, False, 0)
    main.pack_start(scroll, True, True, 0)
    body.pack_start(side, False, False, 0)
    body.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)
    body.pack_start(main, True, True, 0)
    root.pack_start(body, True, True, 0)

    shown: list[str] = []

    def open_app(_b, app_id):
        panel.close()
        panelkit.run_command(f"{shlex.quote(str(LAUNCHER))} launch {shlex.quote(app_id)}")

    def fill(title, ids):
        heading.set_text(title)
        for child in grid.get_children():
            grid.remove(child)
        shown[:] = ids
        for app_id in ids:
            app = entries[app_id]
            button = Gtk.Button()
            button.get_style_context().add_class("flat")
            button.get_style_context().add_class("hf-app")
            col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            path = icons.find(app["icon"])
            image = Gtk.Image()
            if path:
                try:
                    image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(path, ICON, ICON))
                except Exception:  # an unreadable picture: the theme's own icon by name
                    image.set_from_icon_name(app["icon"], Gtk.IconSize.DIALOG)
            else:
                image.set_from_icon_name("application-x-executable", Gtk.IconSize.DIALOG)
            name = Gtk.Label(label=app["name"], justify=Gtk.Justification.CENTER, max_width_chars=14,
                             ellipsize=Pango.EllipsizeMode.END, lines=2)
            name.set_line_wrap(True)
            col.pack_start(image, False, False, 0)
            col.pack_start(name, False, False, 0)
            button.add(col)
            button.set_tooltip_text(app["name"])
            button.connect("clicked", open_app, app_id)
            button.set_size_request(CELL_W, CELL_H)            # one size for every icon, however many
            button.set_valign(Gtk.Align.START)
            grid.add(button)
        grid.show_all()

    side_buttons = []

    def pick(_b, index):
        search.set_text("")
        for i, b in enumerate(side_buttons):
            ctx = b.get_style_context()
            (ctx.add_class if i == index else ctx.remove_class)("hf-selected")
        fill(*sets[index])

    for i, (name, ids) in enumerate(sets):
        b = Gtk.Button()
        b.get_style_context().add_class("flat")
        row = Gtk.Box(spacing=16)
        row.pack_start(Gtk.Label(label=name, xalign=0), True, True, 0)
        count = Gtk.Label(label=str(len(ids)))
        count.get_style_context().add_class("hf-count")
        row.pack_end(count, False, False, 0)
        b.add(row)
        b.connect("clicked", pick, i)
        side.pack_start(b, False, False, 0)
        side_buttons.append(b)

    def searched(entry):
        words = entry.get_text().strip()
        if words:
            fill(f"Results for “{words}”", matches(entries, words))
        else:
            pick(None, 0)

    search.connect("search-changed", searched)
    search.connect("activate", lambda *_: shown and open_app(None, shown[0]))

    foot = Gtk.Box(spacing=8)
    foot.get_style_context().add_class("hf-foot")
    me = display_name()
    avatar = Gtk.Label(label=me[:1].upper())
    avatar.get_style_context().add_class("hf-avatar")
    foot.pack_start(avatar, False, False, 0)
    foot.pack_start(Gtk.Label(label=me), False, False, 0)
    for key, icon, tip in (("shutdown", "system-shutdown", "Power"), ("logout", "system-log-out", "Log Out"),
                           ("lock", "system-lock-screen", "Lock")):
        b = Gtk.Button.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
        b.get_style_context().add_class("flat")
        b.set_tooltip_text(tip)
        command = (f"{shlex.quote(sys.executable)} {shlex.quote(str(panelkit.HERE / 'hypeforge-panel'))} power"
                   if key == "shutdown" else f"{shlex.quote(str(LAUNCHER))} power {key}")
        b.connect("clicked", lambda _b, cmd=command: (panel.close(), panelkit.run_command(cmd)))
        foot.pack_end(b, False, False, 0)
    root.pack_start(foot, False, False, 0)

    first = int(os.environ.get("HYPEFORGE_START_GROUP", "0"))   # the bench opens a given group
    pick(None, first if 0 <= first < len(sets) else 0)
    edges = args.edges.split(",") if getattr(args, "edges", None) else ["bottom"]
    margins = dict(m.split("=") for m in args.margin.split(",")) if getattr(args, "margin", None) else {"bottom": 60}
    panel = panelkit.Panel("start", root, look, edges=edges, margins={k: int(v) for k, v in margins.items()})
    search.grab_focus()
    return panel
