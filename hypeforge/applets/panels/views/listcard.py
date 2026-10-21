"""The list card (D-116, Javier, 2026-10-20: "popups cannot be to different between them"): every short
list a bar opens — Workspaces, Favorites, the printers, the USB drives, the notification list, the open
apps, the ⏻ list — as one card in the pop-up standard, the tray menu's look (D-105):

  - a head: the list's name in bold (and its glyph when it has one)
  - a soft line under it, fading at both ends
  - every row the same height: the app's icon (when the list has icons), the words, a ● in the accent
    colour on the one that is current; the theme's hover and highlight
  - type to narrow it (a search box appears with the first letter; long lists show it from the start);
    ↑ ↓ move, Enter or a click picks, Escape or a click elsewhere closes

It replaces fuzzel for these lists without changing their applets: `common/hfmenu.run` turns the
fuzzel command an applet gives into this card's input (a JSON object on stdin) and reads the pick back
from stdout — the row's number with `index`, else its words — exactly as fuzzel answered.
The launchers stay fuzzel: the launcher is each theme's identity (D-116).
"""

from __future__ import annotations

import json
import sys

import panelkit  # first: it picks GTK 3 before anything asks for GTK
from gi.repository import Gdk, GdkPixbuf, Gtk, Pango  # noqa: E402

sys.path.insert(0, str(panelkit.APPLETS / "common"))
from hficons import Icons  # noqa: E402

WIDTH = 300           # the standard's narrow width (menus and lists), the tray menu's
ICON = 20             # a row's icon
LONG = 18             # rows shown before it scrolls (Javier, 2026-10-20: all 18 Favorites)
SEARCH_FROM = 9       # a list this long shows its search box from the start
ROW_H = 30            # one row's height, for the scroll limit
MARK = "●"

CSS = """
.hf-card.hf-list {{ padding: 8px 6px; }}
.hf-list-head {{ padding: 2px 4px 2px 8px; }}
.hf-list-name {{ font-weight: bold; font-size: {big}pt; }}
.hf-list-glyph {{ font-family: "Symbols Nerd Font", "{font}"; color: {accent}; }}
.hf-list-line {{ min-height: 1px; margin: 5px 6px; border: none; background-color: transparent;
                 background-image: linear-gradient(to right, transparent, {line} 15%, {line} 85%, transparent); }}
.hf-list-rows, .hf-list-rows row {{ background: transparent; }}
.hf-list-rows row {{ padding: 4px 10px; border-radius: {inner}px; color: {text}; min-height: {row_h}px; }}
.hf-list-rows row:hover {{ background: {hover}; }}
.hf-list-rows row:selected, .hf-list-rows row:selected:focus {{ background: {sel}; color: {sel_text}; }}
.hf-list-rows row:selected .hf-list-mark {{ color: {sel_text}; }}
.hf-list-mark {{ color: {accent}; min-width: 14px; }}
.hf-list-empty {{ color: {dim}; padding: 8px 10px; }}
.hf-list entry {{ margin: 2px 4px 4px 4px; }}
"""


def parse(raw: str) -> dict:
    """The card's input: {"title", "glyph", "rows": [{"text", "icon", "mark"}], "selected", "index"}."""
    try:
        data = json.loads(raw or "{}")
    except ValueError:
        data = {}
    rows = [r for r in data.get("rows", []) if isinstance(r, dict) and str(r.get("text", "")).strip()]
    return {"title": str(data.get("title", "")).strip(), "glyph": str(data.get("glyph", "")),
            "rows": rows, "selected": int(data.get("selected", 0) or 0), "index": bool(data.get("index", True))}


def answer(data: dict, row_number: int) -> str:
    """What the caller reads back, as fuzzel gave it: the row's number (--index) or its words."""
    return str(row_number) if data["index"] else str(data["rows"][row_number]["text"])


def build(look: panelkit.Look, args) -> panelkit.Panel:
    c = look.colour
    inner = 0 if look.straight else max(4, look.radius // 2)
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(font=look.font, big=look.size * 1.1, accent=c["panel_tile_on"], line=c["panel_border"],
                                       inner=inner, text=c["panel_text"], hover=c["panel_hover"], sel=c["panel_selected"],
                                       sel_text=c["panel_selected_text"], dim=c["panel_text_dim"], row_h=ROW_H - 8).encode())
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)

    data = parse(sys.stdin.read() if not sys.stdin.isatty() else "")
    icons = Icons() if any(r.get("icon") for r in data["rows"]) else None
    panel_ref = {}

    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    root.set_size_request(WIDTH, -1)

    head = Gtk.Box(spacing=8)
    head.get_style_context().add_class("hf-list-head")
    if data["glyph"]:
        glyph = Gtk.Label(label=data["glyph"])
        glyph.get_style_context().add_class("hf-list-glyph")
        head.pack_start(glyph, False, False, 0)
    name = Gtk.Label(label=data["title"] or "Choose", xalign=0, ellipsize=Pango.EllipsizeMode.END, max_width_chars=30)
    name.get_style_context().add_class("hf-list-name")
    head.pack_start(name, True, True, 0)
    root.pack_start(head, False, False, 0)
    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.get_style_context().add_class("hf-list-line")
    root.pack_start(sep, False, False, 0)

    search = Gtk.SearchEntry(placeholder_text="Type to find")
    root.pack_start(search, False, False, 0)
    long_list = len(data["rows"]) >= SEARCH_FROM
    if not long_list:
        search.set_no_show_all(True)          # appears with the first letter typed

    rows = Gtk.ListBox()
    rows.get_style_context().add_class("hf-list-rows")
    rows.set_selection_mode(Gtk.SelectionMode.BROWSE)
    rows.set_activate_on_single_click(True)
    marks = any(r.get("mark") for r in data["rows"])
    for n, r in enumerate(data["rows"]):
        row = Gtk.ListBoxRow()
        row.number, row.words = n, str(r["text"]).lower()
        box = Gtk.Box(spacing=8)
        if marks:
            mark = Gtk.Label(label=MARK if r.get("mark") else "")
            mark.get_style_context().add_class("hf-list-mark")
            box.pack_start(mark, False, False, 0)
        if icons is not None:
            image = Gtk.Image()
            path = icons.find(str(r.get("icon") or ""))
            if path:
                try:
                    image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(path, ICON, ICON))
                except Exception:
                    pass
            image.set_size_request(ICON, ICON)
            box.pack_start(image, False, False, 0)
        box.pack_start(Gtk.Label(label=str(r["text"]), xalign=0, ellipsize=Pango.EllipsizeMode.END, max_width_chars=40),
                       True, True, 0)
        row.add(box)
        rows.add(row)

    scroller = Gtk.ScrolledWindow()
    scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroller.set_propagate_natural_height(True)
    scroller.set_max_content_height(LONG * ROW_H)
    scroller.set_min_content_height(min(max(len(data["rows"]), 1), LONG) * ROW_H)   # every row up to LONG, then it scrolls
    scroller.add(rows)
    root.pack_start(scroller, True, True, 0)
    empty = Gtk.Label(label="Nothing matches.", xalign=0)
    empty.get_style_context().add_class("hf-list-empty")
    empty.set_no_show_all(True)
    root.pack_start(empty, False, False, 0)

    def matches(row) -> bool:
        return all(w in row.words for w in search.get_text().strip().lower().split())

    rows.set_filter_func(matches)

    def visible():
        return [r for r in rows.get_children() if matches(r)]

    def refresh(*_):
        rows.invalidate_filter()
        shown = visible()
        empty.set_visible(not shown)
        if shown and (rows.get_selected_row() not in shown):
            rows.select_row(shown[0])

    search.connect("search-changed", refresh)

    def pick(_box, row):
        print(answer(data, row.number), flush=True)
        panel_ref["p"].close()

    rows.connect("row-activated", pick)

    def keys(_w, event):
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            row = rows.get_selected_row() or next(iter(visible()), None)
            if row is not None:
                pick(rows, row)
            return True
        if event.keyval in (Gdk.KEY_Down, Gdk.KEY_Up):
            shown = visible()
            if shown:
                here = rows.get_selected_row()
                i = shown.index(here) if here in shown else -1
                i = min(i + 1, len(shown) - 1) if event.keyval == Gdk.KEY_Down else max(i - 1, 0)
                rows.select_row(shown[i])
                shown[i].grab_focus()
            return True
        if event.string and event.string.isprintable() and not search.has_focus():
            search.show()                      # the first letter typed brings the search box
            search.grab_focus_without_selecting()
            search.set_text(search.get_text() + event.string)
            search.set_position(-1)
            return True
        return False

    edges = args.edges.split(",") if getattr(args, "edges", None) else ["top", "left"]
    panel = panelkit.Panel("list", root, look, edges=edges, margins=margins(getattr(args, "margin", None)) or {"top": 44, "left": 8})
    for child in panel.window.get_children():
        child.get_style_context().add_class("hf-list")
    panel.window.connect("key-press-event", keys)
    panel_ref["p"] = panel
    if data["rows"]:
        first = rows.get_row_at_index(min(max(data["selected"], 0), len(data["rows"]) - 1))
        rows.select_row(first)
        panel.window.connect("map", lambda *_: first.grab_focus())
    else:
        empty.set_label("Nothing here.")
        empty.set_no_show_all(False)
    return panel


def margins(text: str | None) -> dict:
    """"top=34,left=40" → {"top": 34, "left": 40}."""
    out = {}
    for part in (text or "").split(","):
        key, _, value = part.partition("=")
        if key.strip() and value.strip().lstrip("-").isdigit():
            out[key.strip()] = int(value)
    return out
