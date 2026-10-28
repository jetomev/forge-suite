"""The calendar with your notifications (Windows 11's clock pop-up, D-71; macOS's Notification
Center, D-74): the recent notifications as cards, then the month.

The notifications are the bell's own list (on screen now + mako's history, newest first), and
opening this panel counts as reading them, so the bell's "new" number clears, as its own list does.
"Clear all" hides the ones shown here and dismisses any still on screen (mako keeps no way to
empty its history, so the panel remembers what was cleared). Escape or a click outside closes.
**Do Not Disturb** is a switch on the Notifications header (Javier, 2026-10-25: "move it to the
Time/Date/Alerts combo. Doesn't make sense to have it in the QS popup"); the bell's right click too.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import subprocess
from datetime import date, timedelta
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
# KognogOS's own senders that have no app entry of their own (Javier, 2026-10-27, the Rice review: a blue "i"
# stood in for nightForge and nog)
OWN_ICONS = {"nightforge": "weather-clear-night", "nog": "system-software-install", "hypeforge": "preferences-desktop",
             "sudoforge": "dialog-password", "themeforge": "preferences-desktop-theme"}
CSS = """
.hf-note-app {{ font-weight: bold; }}
.hf-card.hf-note {{ padding: 6px 12px; }}     /* Javier, 10-17: the notifications a little smaller, closer together */
.hf-card.hf-head {{ padding: 4px 6px 4px 12px; }}   /* 10-17, his second look: "gap spaces, still too much" */
.hf-head button {{ padding: 3px 10px; }}
.hf-card.hf-month {{ padding: 10px 12px; }}
.hf-note-body {{ color: {dim}; font-size: {small}pt; }}
.hf-month-name {{ color: {text}; }}
.hf-month-nav {{ color: {dim}; padding: 0 8px; min-height: 0; }}
.hf-day-name {{ color: {dim}; font-size: {small}pt; padding: 4px 0; }}
.hf-day {{ color: {text}; padding: 3px 0; min-height: 0; min-width: 0; border-radius: {pill}px; }}
.hf-day.hf-other {{ color: {muted}; }}
.hf-day.hf-today {{ background: {accent}; color: {on_accent}; }}
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
    for app_id, app in entries.items():          # a command-line sender, by its Forge app: nog → nogForge
        if name and app["name"].lower() == name + "forge":
            return app["icon"]
    return OWN_ICONS.get(name, "dialog-information")


def plain(v) -> str:
    """mako writes missing fields as the word None."""
    return "" if v in (None, "None") else str(v)


def dnd_on() -> bool:
    return "do-not-disturb" in subprocess.run(["makoctl", "mode"], capture_output=True, text=True).stdout.split()


def dnd_switch() -> Gtk.Box:
    """"Do Not Disturb" and its switch, through the bell applet (`hypeforge-notifications dnd`), so the bell
    redraws too. Moved here from Quick Settings (Javier, 2026-10-25)."""
    box = Gtk.Box(spacing=6)
    words = Gtk.Label(label="Do Not Disturb")
    words.get_style_context().add_class("hf-note-body")
    sw = Gtk.Switch()
    sw.set_valign(Gtk.Align.CENTER)
    sw.set_active(dnd_on())
    sw.connect("notify::active", lambda s, _p: subprocess.run([str(NOTIFY), "dnd"], capture_output=True)
               if s.get_active() != dnd_on() else None)
    box.pack_start(words, False, False, 0)
    box.pack_start(sw, False, False, 0)
    box.switch = sw
    return box


def build(look: panelkit.Look, args) -> panelkit.Panel:
    c = look.colour
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(medium=panelkit.MEDIUM, dim=c["panel_text_dim"], small=look.size * 0.9, text=c["panel_text"],
                                       accent=c["panel_tile_on"], on_accent=c["panel_tile_on_text"],
                                       muted=c["panel_border"], pill=look.pill).encode())
    Gtk.StyleContext.add_provider_for_screen(panelkit.Gdk.Screen.get_default(), provider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
    b = bell()
    notes = b.everything()
    if notes:  # opening this counts as reading them: the bell's "new" number clears
        b.SEEN.write_text(str(max(note_id(n) for n in notes)))
        b.changed()
    shown = visible(notes)

    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    root.get_style_context().add_class("hf-calendar")

    head = Gtk.Box(spacing=8)
    heading = Gtk.Label(label="Notifications", xalign=0)
    heading.get_style_context().add_class("hf-head-name")    # the one title row, as the month's (D-116)
    head.pack_start(heading, True, True, 0)
    if shown:
        clear = Gtk.Button(label="Clear all")
        clear.get_style_context().add_class("flat")
        head.pack_end(clear, False, False, 0)
    head.pack_end(dnd_switch(), False, False, 0)
    root.pack_start(card(head, "hf-head"), False, False, 0)

    cards = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
    if not shown:
        cards.pack_start(card(Gtk.Label(label="No new notifications", xalign=0)), False, False, 0)
    entries, icons = apps(), Icons()
    for n in shown[:SHOWN]:
        box = Gtk.Box(spacing=10)
        icon = icon_for(n, entries)
        path = icons.find(icon)
        image = Gtk.Image()
        try:
            image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(path, 24, 24))
        except Exception:  # no file, or one GTK can't read: the theme's icon by name
            image.set_from_icon_name(icon, Gtk.IconSize.LARGE_TOOLBAR)
        box.pack_start(image, False, False, 0)
        words = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
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
        cards.pack_start(card(box, "hf-note"), False, False, 0)
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
    panel_ref = {}
    month = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    title = Gtk.Label(label=f"{today:%A, %B} {today.day}", xalign=0)
    title.get_style_context().add_class("hf-head-name")      # the one title row (D-116)
    title.get_style_context().add_class("hf-head")
    month.pack_start(title, False, False, 0)
    month.pack_start(month_view(today, lambda day: (panel_ref["panel"].close(), open_day(day))), False, False, 0)
    root.pack_start(card(month, "hf-month"), False, False, 0)

    edges = args.edges.split(",") if getattr(args, "edges", None) else ["bottom", "right"]
    margins = dict(m.split("=") for m in args.margin.split(",")) if getattr(args, "margin", None) else {"bottom": 60, "right": 10}
    panel = panelkit.Panel("calendar", root, look, edges=edges, margins={k: int(v) for k, v in margins.items()}, width=panelkit.MEDIUM,
                          card=False)
    panel_ref["panel"] = panel
    return panel


def weeks(year: int, month: int) -> list[list[date]]:
    """The month's weeks, Sunday first, only as many as it has (4 to 6): a week of the next month is never added
    (Javier, 2026-10-27, the Rice review: GTK's calendar always drew six rows, the last one next month's)."""
    first = date(year, month, 1)
    start = first - timedelta(days=(first.weekday() + 1) % 7)
    out, day = [], start
    while day.month == month or day < first or not out:
        out.append([day + timedelta(days=i) for i in range(7)])
        day += timedelta(days=7)
        if day.month != month and day > first:
            break
    return out


def month_view(today: date, picked) -> Gtk.Box:
    """‹ October 2026 › and the days; today is the accent pill, the other months' days dim; a click on a day
    calls `picked(day)`."""
    shown = {"y": today.year, "m": today.month}
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    nav = Gtk.Box(spacing=4)
    back, ahead = Gtk.Button(label="‹"), Gtk.Button(label="›")
    for b in (back, ahead):
        b.get_style_context().add_class("flat")
        b.get_style_context().add_class("hf-month-nav")
    name = Gtk.Label()
    name.get_style_context().add_class("hf-month-name")
    nav.pack_start(back, False, False, 0)
    nav.pack_start(name, True, True, 0)
    nav.pack_start(ahead, False, False, 0)
    box.pack_start(nav, False, False, 0)
    grid = Gtk.Grid(column_homogeneous=True, row_spacing=2, column_spacing=2)
    box.pack_start(grid, False, False, 0)

    def fill():
        for child in grid.get_children():
            grid.remove(child)
        y, m = shown["y"], shown["m"]
        name.set_text(date(y, m, 1).strftime("%B %Y"))
        for i, word in enumerate(("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")):
            lab = Gtk.Label(label=word)
            lab.get_style_context().add_class("hf-day-name")
            grid.attach(lab, i, 0, 1, 1)
        for r, week in enumerate(weeks(y, m), 1):
            for i, day in enumerate(week):
                b = Gtk.Button(label=str(day.day))
                ctx = b.get_style_context()
                ctx.add_class("flat")
                ctx.add_class("hf-day")
                if day == today:
                    ctx.add_class("hf-today")
                if day.month != m:
                    ctx.add_class("hf-other")
                b.set_tooltip_text(day.strftime("%A %d %B: open your calendar on this day"))
                b.connect("clicked", lambda _b, d=day: picked(d))
                grid.attach(b, i, r, 1, 1)
        grid.show_all()

    def step(n):
        m = shown["m"] - 1 + n
        shown["y"], shown["m"] = shown["y"] + m // 12, m % 12 + 1
        fill()
    back.connect("clicked", lambda _b: step(-1))
    ahead.connect("clicked", lambda _b: step(1))
    fill()
    return box


GOOGLE_DAY = "https://calendar.google.com/calendar/r/day/{y}/{m}/{d}"


def open_day(day: date, run=subprocess.Popen, query=None, entries=None) -> list[str]:
    """Your calendar, on that day (Javier, 2026-10-27: "If I click on a date, I would like for the default calendar to
    open"): the app set for calendars (defaultappsForge's Calendar; xdg-mime's text/calendar). Thunderbird opens on
    its calendar; a web calendar on that day; no calendar set: Google Calendar's day in the browser. Returns the
    command it ran."""
    import shlex
    if query is None:
        try:
            query = subprocess.run(["xdg-mime", "query", "default", "text/calendar"], capture_output=True, text=True,
                                   timeout=3).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            query = ""
    entries = apps() if entries is None else entries
    app = entries.get(query[:-len(".desktop")] if query.endswith(".desktop") else query)
    if app:
        words = [w for w in shlex.split(app["exec"]) if not (len(w) == 2 and w.startswith("%")) and w not in ("@@u", "@@")]
        url = GOOGLE_DAY.format(y=day.year, m=day.month, d=day.day)
        if any("calendar.google.com" in w for w in words):        # a Google Calendar web app: on that day
            words = [w if "calendar.google.com" not in w else (w.split("=", 1)[0] + "=" + url if "=" in w else url)
                     for w in words]
        elif "thunderbird" in app["exec"].lower():
            words.append("-calendar")
        cmd = words
    else:
        cmd = ["xdg-open", GOOGLE_DAY.format(y=day.year, m=day.month, d=day.day)]
    run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return cmd


def card(widget: Gtk.Widget, *extra: str) -> Gtk.Box:
    box = Gtk.Box()
    box.get_style_context().add_class("hf-card")
    for cls in extra:
        box.get_style_context().add_class(cls)
    widget.set_hexpand(True)      # the header's "Clear all" sits at the card's right edge
    box.add(widget)
    return box
