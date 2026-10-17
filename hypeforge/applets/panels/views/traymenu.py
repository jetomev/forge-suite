"""A tray app's menu as a hypeForge pop-up (Javier, 2026-10-17: Dropbox's menu "is horrible, and opens on
top of the bar/icon area"). The app hands over its menu (com.canonical.dbusmenu); this draws it like the
other panels, under the bar, in the style's and theme's own look:

  - a head: the app's icon and name, and **Open <app>** when the app has a window to open
  - the entries in cards, a card between the app's own separators
  - a greyed entry is information, so it reads as a quiet line (Dropbox's account, "Up to date"); the
    spaces an app puts in front of a line to indent it become a real indent
  - a check or a choice the app marks shows as ✓ / ●
  - a submenu opens in place (▸ → ▾), and scrolls when it is long
  - a click sends the app its own "clicked", and the pop-up closes

hypeforge-tray (applets/tray/) keeps the icons on the bar; this only draws the one menu.
"""

from __future__ import annotations

import sys

import panelkit  # first: it picks GTK 3 before anything asks for GTK
from gi.repository import Gdk, GdkPixbuf, Gtk, Pango  # noqa: E402

sys.path.insert(0, str(panelkit.APPLETS / "tray"))
import hfsni  # noqa: E402

LONG = 12             # a submenu longer than this scrolls
CSS = """
.hf-tm {{ min-width: 300px; }}
.hf-card.hf-head {{ padding: 6px 8px 6px 12px; }}
.hf-tm-name {{ font-weight: bold; font-size: {big}pt; }}
.hf-card.hf-tm-group {{ padding: 4px; }}
.hf-tm-group button {{ background: transparent; border-color: transparent; padding: 4px 10px; border-radius: {inner}px;
                      color: {text}; }}
.hf-tm-group button:hover, .hf-tm-group button:focus {{ background: {hover}; }}
.hf-tm-group button label {{ color: {text}; }}
.hf-tm-group button.hf-tm-quit:hover, .hf-tm-group button.hf-tm-quit:focus {{ background: {danger}; }}
.hf-tm-group button.hf-tm-quit:hover label, .hf-tm-group button.hf-tm-quit:focus label {{ color: {bg}; }}
.hf-tm-info {{ color: {dim}; font-size: {small}pt; padding: 3px 10px; }}
.hf-tm-mark {{ color: {accent}; min-width: 14px; }}
.hf-tm-arrow {{ color: {dim}; }}
.hf-tm-sub {{ margin-left: 14px; }}
.hf-tm-sub button {{ padding: 4px 10px; }}
"""


def clean(label: str) -> tuple[str, int]:
    """(words, indent): the app's leading spaces as an indent, its mnemonic underscores removed."""
    stripped = label.lstrip(" ")
    indent = (len(label) - len(stripped)) // 3
    words = stripped.replace("__", "\x00").replace("_", "").replace("\x00", "_")
    return words, indent


def groups(entries: list) -> list[list]:
    """The entries cut into groups at the app's separators (empty groups dropped)."""
    out, cur = [], []
    for e in entries:
        _id, p, _kids = e
        if not p.get("visible", True):
            continue
        if p.get("type") == "separator":
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(e)
    if cur:
        out.append(cur)
    return out


def build(look: panelkit.Look, args) -> panelkit.Panel:
    c = look.colour
    inner = 0 if look.straight else max(4, look.radius // 2)
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(big=look.size * 1.1, small=look.size * 0.9, inner=inner, text=c["panel_text"],
                                       hover=c["panel_hover"], dim=c["panel_text_dim"], accent=c["panel_tile_on"],
                                       danger=c["panel_danger"], bg=c["panel_bg"]).encode())
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)

    slots = hfsni.read_slots()
    try:
        item = slots[int(args.slot) - 1]
    except (TypeError, ValueError, IndexError):
        item = None
    conn = hfsni.bus()
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    root.get_style_context().add_class("hf-tm")
    panel_ref = {}

    def close():
        panel_ref["p"].close()

    # ---- the head
    head = Gtk.Box(spacing=10)
    name = (item or {}).get("title") or (item or {}).get("id") or "Tray app"
    if item and item.get("picture"):
        try:
            head.pack_start(Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(item["picture"], 24, 24)),
                            False, False, 0)
        except Exception:
            pass
    label = Gtk.Label(label=name, xalign=0, ellipsize=Pango.EllipsizeMode.END, max_width_chars=28)
    label.get_style_context().add_class("hf-tm-name")
    head.pack_start(label, True, True, 0)
    # an app that only offers a menu has no window to open: ItemIsMenu, or an Ayatana item (Dropbox), which
    # never answers Activate
    if item and not item.get("is_menu") and not str(item.get("path", "")).startswith("/org/ayatana/"):
        opener = Gtk.Button(label="Open")
        opener.set_tooltip_text(f"Open {name}'s own window")
        opener.connect("clicked", lambda _b: (hfsni.activate(conn, item["name"], item["path"]), close()))
        head.pack_end(opener, False, False, 0)
    root.pack_start(card(head, "hf-head"), False, False, 0)

    # ---- the menu
    entries = []
    if item and item.get("menu"):
        try:
            entries = hfsni.menu_layout(conn, item["name"], item["menu"])
        except Exception as e:  # an app that doesn't answer: say so, never crash
            root.pack_start(card(info_line(f"{name} didn't answer for its menu ({e.__class__.__name__}).")), False, False, 0)
    elif item is None:
        root.pack_start(card(info_line("That tray app has gone.")), False, False, 0)

    def clicked(entry_id: int):
        try:
            hfsni.menu_click(conn, item["name"], item["menu"], entry_id)
        except Exception:
            pass
        close()

    for group in groups(entries):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        for e in group:
            box.pack_start(entry_widget(e, clicked, depth=0), False, False, 0)
        root.pack_start(card(box, "hf-tm-group"), False, False, 0)
    if item and item.get("menu") and not entries:
        root.pack_start(card(info_line(f"{name} has no menu to show.")), False, False, 0)

    edges = args.edges.split(",") if getattr(args, "edges", None) else ["top", "right"]
    margins = dict(m.split("=") for m in args.margin.split(",")) if getattr(args, "margin", None) else {"top": 44, "right": 8}
    panel = panelkit.Panel("traymenu", root, look, edges=edges, margins={k: int(v) for k, v in margins.items()}, card=False)
    panel_ref["p"] = panel
    return panel


def info_line(words: str, indent: int = 0) -> Gtk.Label:
    lab = Gtk.Label(label=words, xalign=0, ellipsize=Pango.EllipsizeMode.END, max_width_chars=40)
    lab.get_style_context().add_class("hf-tm-info")
    lab.set_margin_start(indent * 14)
    return lab


def entry_widget(e, clicked, depth: int) -> Gtk.Widget:
    eid, p, kids = e
    words, indent = clean(str(p.get("label", "")))
    enabled = p.get("enabled", True)
    if not enabled:
        return info_line(words, indent)
    row = Gtk.Box(spacing=8)
    mark = Gtk.Label(label="")
    mark.get_style_context().add_class("hf-tm-mark")
    if p.get("toggle-type") == "checkmark":
        mark.set_label("✓" if p.get("toggle-state") == 1 else "")
    elif p.get("toggle-type") == "radio":
        mark.set_label("●" if p.get("toggle-state") == 1 else "○")
    if mark.get_label() or p.get("toggle-type"):
        row.pack_start(mark, False, False, 0)
    text = Gtk.Label(label=words, xalign=0, ellipsize=Pango.EllipsizeMode.END, max_width_chars=40)
    row.pack_start(text, True, True, 0)
    button = Gtk.Button()
    button.add(row)
    button.set_margin_start(indent * 14)
    if p.get("children-display") == "submenu" or kids:
        arrow = Gtk.Label(label="▸")
        arrow.get_style_context().add_class("hf-tm-arrow")
        row.pack_end(arrow, False, False, 0)
        holder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sub = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        sub.get_style_context().add_class("hf-tm-sub")
        shown = [k for k in kids if k[1].get("visible", True)]
        for k in shown:
            if k[1].get("type") == "separator":
                continue
            sub.pack_start(entry_widget(k, clicked, depth + 1), False, False, 0)
        if len(shown) > LONG:
            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            scroll.set_min_content_height(LONG * 26)
            scroll.add(sub)
            inner = scroll
        else:
            inner = sub
        inner.set_no_show_all(True)
        holder.pack_start(button, False, False, 0)
        holder.pack_start(inner, False, False, 0)

        def toggle(_b):
            opening = not inner.get_visible()
            inner.set_visible(opening)
            if opening:
                inner.show_all()
            arrow.set_label("▾" if opening else "▸")

        button.connect("clicked", toggle)
        return holder
    if words.lower().startswith(("quit", "exit")):
        button.get_style_context().add_class("hf-tm-quit")
    button.connect("clicked", lambda _b: clicked(eid))
    return button


def card(widget: Gtk.Widget, *extra: str) -> Gtk.Box:
    box = Gtk.Box()
    box.get_style_context().add_class("hf-card")
    for cls in extra:
        box.get_style_context().add_class(cls)
    widget.set_hexpand(True)
    box.add(widget)
    return box
