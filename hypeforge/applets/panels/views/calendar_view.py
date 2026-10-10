"""The calendar with your notifications (Windows 11's clock pop-up, D-71; macOS's Notification
Center, D-74): the recent notifications as cards, then the month.

The notifications are the bell's own list (on screen now + mako's history, newest first), and
opening this panel counts as reading them, so the bell's "new" number clears, as its own list does.
"Clear all" hides the ones shown here and dismisses any still on screen (mako keeps no way to
empty its history, so the panel remembers what was cleared). Escape or a click outside closes.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import subprocess
from datetime import date
from pathlib import Path

import sys

from gi.repository import GdkPixbuf, Gtk, Pango

import panelkit

sys.path.insert(0, str(panelkit.APPLETS / "common"))
from hfapps import apps  # noqa: E402
from hficons import Icons  # noqa: E402

NOTIFY = panelkit.APPLETS / "notifications/hypeforge-notifications"
CLEARED = panelkit.RUNTIME / "hypeforge-panel-cleared"     # notifications up to this id are cleared
SHOWN = 6
CSS = """
.hf-calendar {{ min-width: 380px; }}
.hf-note-app {{ font-weight: bold; }}
.hf-note-body {{ color: {dim}; font-size: {small}pt; }}
.hf-calendar calendar {{ background: transparent; color: {text}; border: none; padding: 4px; }}
.hf-calendar calendar:selected {{ background: {accent}; color: {on_accent}; border-radius: 999px; }}
.hf-calendar calendar.header {{ border: none; }}
.hf-calendar calendar.button {{ color: {dim}; }}
.hf-calendar calendar:indeterminate {{ color: {muted}; }}
"""


def bell():
    loader = importlib.machinery.SourceFileLoader("hfbell", str(NOTIFY))
    spec = importlib.util.spec_from_loader("hfbell", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def note_id(n) -> int:
    try:
        return int(n.get("id", 0))
    except (TypeError, ValueError):
        return 0


def cleared() -> int:
    try:
        return int(CLEARED.read_text())
    except (OSError, ValueError):
        return 0


def visible(notes: list[dict]) -> list[dict]:
    """The notes newer than the last "Clear all", newest first."""
    floor = cleared()
    return [n for n in sorted(notes, key=note_id, reverse=True) if note_id(n) > floor]


def icon_for(n: dict, entries: dict) -> str:
    """The notification's own icon name, else the icon of the installed app it names (Steam →
    Steam's), else a generic one."""
    own = plain(n.get("app_icon")) or plain(n.get("desktop_entry"))
    if own:
        return own
    name = plain(n.get("app_name")).lower()
    for app_id, app in entries.items():
        if name and (app["name"].lower() == name or app_id.lower() == name):
            return app["icon"]
    return "dialog-information"


def plain(v) -> str:
    """mako writes missing fields as the word None."""
    return "" if v in (None, "None") else str(v)


def build(look: panelkit.Look, args) -> panelkit.Panel:
    c = look.colour
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(dim=c["panel_text_dim"], small=look.size * 0.9, text=c["panel_text"],
                                       accent=c["panel_tile_on"], on_accent=c["panel_tile_on_text"],
                                       muted=c["panel_border"]).encode())
    Gtk.StyleContext.add_provider_for_screen(panelkit.Gdk.Screen.get_default(), provider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
    b = bell()
    notes = b.everything()
    if notes:  # opening this counts as reading them: the bell's "new" number clears
        b.SEEN.write_text(str(max(note_id(n) for n in notes)))
        b.changed()
    shown = visible(notes)

    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    root.get_style_context().add_class("hf-calendar")

    head = Gtk.Box()
    head.pack_start(Gtk.Label(label="Notifications", xalign=0), True, True, 0)
    if shown:
        clear = Gtk.Button(label="Clear all")
        clear.get_style_context().add_class("flat")
        head.pack_end(clear, False, False, 0)
    root.pack_start(card(head), False, False, 0)

    cards = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    if not shown:
        cards.pack_start(card(Gtk.Label(label="No new notifications", xalign=0)), False, False, 0)
    entries, icons = apps(), Icons()
    for n in shown[:SHOWN]:
        box = Gtk.Box(spacing=12)
        icon = icon_for(n, entries)
        path = icons.find(icon)
        image = Gtk.Image()
        try:
            image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(path, 28, 28))
        except Exception:  # no file, or one GTK can't read: the theme's icon by name
            image.set_from_icon_name(icon, Gtk.IconSize.LARGE_TOOLBAR)
        box.pack_start(image, False, False, 0)
        words = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        app = Gtk.Label(label=plain(n.get("app_name")) or "Notification", xalign=0)
        app.get_style_context().add_class("hf-note-app")
        words.pack_start(app, False, False, 0)
        summary = Gtk.Label(label=plain(n.get("summary")), xalign=0, max_width_chars=40, ellipsize=Pango.EllipsizeMode.END)
        words.pack_start(summary, False, False, 0)
        if plain(n.get("body")):
            body = Gtk.Label(label=plain(n["body"]).replace("\n", " "), xalign=0, max_width_chars=44,
                             ellipsize=Pango.EllipsizeMode.END)
            body.get_style_context().add_class("hf-note-body")
            words.pack_start(body, False, False, 0)
        box.pack_start(words, True, True, 0)
        cards.pack_start(card(box), False, False, 0)
    if len(shown) > SHOWN:
        more = Gtk.Label(label=f"and {len(shown) - SHOWN} more — the bell lists them all", xalign=0)
        more.get_style_context().add_class("hf-note-body")
        cards.pack_start(more, False, False, 0)
    root.pack_start(cards, False, False, 0)

    if shown:
        def clear_all(_b):
            CLEARED.write_text(str(max(note_id(n) for n in notes)))
            subprocess.run(["makoctl", "dismiss", "--all"], capture_output=True)
            for child in cards.get_children():
                cards.remove(child)
            cards.pack_start(card(Gtk.Label(label="No new notifications", xalign=0)), False, False, 0)
            cards.show_all()
            clear.hide()
        clear.connect("clicked", clear_all)

    today = date.today()
    month = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    title = Gtk.Label(label=f"{today:%A, %B} {today.day}", xalign=0)
    title.get_style_context().add_class("hf-title")
    month.pack_start(title, False, False, 0)
    cal = Gtk.Calendar()
    cal.set_display_options(Gtk.CalendarDisplayOptions.SHOW_HEADING | Gtk.CalendarDisplayOptions.SHOW_DAY_NAMES)
    month.pack_start(cal, False, False, 0)
    root.pack_start(card(month), False, False, 0)

    edges = args.edges.split(",") if getattr(args, "edges", None) else ["bottom", "right"]
    margins = dict(m.split("=") for m in args.margin.split(",")) if getattr(args, "margin", None) else {"bottom": 60, "right": 10}
    return panelkit.Panel("calendar", root, look, edges=edges, margins={k: int(v) for k, v in margins.items()},
                          card=False)


def card(widget: Gtk.Widget) -> Gtk.Box:
    box = Gtk.Box()
    box.get_style_context().add_class("hf-card")
    widget.set_hexpand(True)      # the header's "Clear all" sits at the card's right edge
    box.add(widget)
    return box
