"""Alt + Tab (Javier, 2026-10-11, on the Rice: "I don't have a way to bring back a floating window when
it goes 'minimized' … and we don't have the Alt+Tab function yet"). Every open window as a card, the
ones tucked away (D-82) too, marked; the one used last comes first.

Held (Alt + Tab, `--hold`): it starts on the window used before this one; each Tab moves on (Sway
runs the key again, and the running switcher is told `next`), Shift goes back, and letting go of Alt
picks. A quick Alt + Tab flips between the last two windows. The arrows, Enter and a click work too;
Escape or a click outside closes it.
From the bar (`--tucked`): only the windows tucked away; a click brings one back.

Picking a tucked window brings it back on the workspace in use, on top (as Win + − does); any other
is focused where it is. Sway can't draw live pictures of windows, so the cards show the app, its
title and where it is (the previews come later).
"""

from __future__ import annotations

import json
import signal
import sys

import panelkit  # first: it picks GTK 3 before anything asks for GTK

from gi.repository import Gdk, GdkPixbuf, GLib, Gtk, Pango  # noqa: E402

sys.path.insert(0, str(panelkit.APPLETS / "common"))
from hfapps import Matcher, apps  # noqa: E402
from hficons import Icons  # noqa: E402

RECENT = panelkit.RUNTIME / "hypeforge-focus.json"   # the Tuck applet's record: window ids, last used first
SCRATCH = "__i3_scratch"
TITLE_CHARS = 30
CSS = """
.hf-sw {{ min-width: 168px; min-height: 104px; padding: 10px 12px; border: 2px solid transparent; }}
.hf-sw.on {{ border: 2px solid {accent}; background: {tile}; color: {text}; }}
.hf-sw .hf-sw-app {{ font-weight: bold; }}
.hf-sw .hf-sw-where {{ color: {dim}; font-size: {small}pt; }}
.hf-sw.tucked .hf-sw-where {{ font-style: italic; }}
.hf-sw-empty {{ padding: 10px 18px; color: {dim}; }}
"""


def windows(tree: dict) -> list[dict]:
    """Every window: {id, app, title, workspace, tucked, focused, raw}, in the tree's order."""
    out = []

    def walk(node, ws=None):
        if node.get("type") == "workspace":
            ws = node.get("name")
        if node.get("pid") and node.get("type") in ("con", "floating_con"):
            out.append({"id": node["id"], "title": node.get("name") or "", "workspace": ws,
                        "tucked": ws == SCRATCH, "focused": bool(node.get("focused")), "raw": node})
        for child in node.get("nodes", []) + node.get("floating_nodes", []):
            walk(child, ws)
    walk(tree)
    return out


def recent() -> list[int]:
    try:
        return [int(i) for i in json.loads(RECENT.read_text())]
    except (OSError, ValueError, TypeError):
        return []


def ordered(wins: list[dict], last_used: list[int]) -> list[dict]:
    """The window in use first, then by when each was last used; never-used ones keep the tree's order."""
    rank = {wid: n for n, wid in enumerate(last_used)}
    keyed = sorted(enumerate(wins), key=lambda p: (not p[1]["focused"], rank.get(p[1]["id"], len(rank) + p[0])))
    return [w for _, w in keyed]


def start_at(wins: list[dict], back: bool, tucked_only: bool) -> int:
    if not wins or tucked_only:
        return 0
    if back:
        return len(wins) - 1
    return 1 if len(wins) > 1 and wins[0]["focused"] else 0


def pick_command(w: dict) -> str:
    return f"[con_id={w['id']}] scratchpad show" if w["tucked"] else f"[con_id={w['id']}] focus"


def where(w: dict) -> str:
    if w["tucked"]:
        return "tucked away"
    name = (w["workspace"] or "").split(":", 1)
    return f"on {name[1]}" if len(name) == 2 and name[1] else f"workspace {name[0]}"


def build(look: panelkit.Look, args) -> panelkit.Panel:
    c = look.colour
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(accent=c["panel_tile_on"], tile=c["panel_tile"], text=c["panel_text"],
                                       dim=c["panel_text_dim"], small=look.size * 0.85).encode())
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
    tucked_only = bool(getattr(args, "tucked", False))
    wins = ordered(windows(panelkit.sway_ask(4)), recent())                    # GET_TREE
    if tucked_only:
        wins = [w for w in wins if w["tucked"]]
    entries, icons = apps(), Icons()
    matcher = Matcher(entries)
    state = {"at": start_at(wins, bool(getattr(args, "back", False)), tucked_only), "done": False}
    cards: list[Gtk.Button] = []

    grid = Gtk.FlowBox()
    grid.set_selection_mode(Gtk.SelectionMode.NONE)
    grid.set_max_children_per_line(6)
    grid.set_min_children_per_line(min(max(len(wins), 1), 6))
    grid.set_column_spacing(10)
    grid.set_row_spacing(10)
    grid.set_homogeneous(True)

    def show(i: int):
        if not cards:
            return
        state["at"] = i % len(cards)
        for n, b in enumerate(cards):
            (b.get_style_context().add_class if n == state["at"] else b.get_style_context().remove_class)("on")

    def pick(i: int | None = None):
        if state["done"]:
            return
        state["done"] = True
        chosen = wins[state["at"] if i is None else i] if wins else None
        panel.close()
        if chosen is not None:
            panelkit.sway_ask(0, pick_command(chosen))                        # RUN_COMMAND

    for n, w in enumerate(wins):
        app = matcher.of_window(w["raw"])
        name = entries[app]["name"] if app in entries else (w["raw"].get("app_id") or "Window")
        b = Gtk.Button()
        b.get_style_context().add_class("hf-sw")
        if w["tucked"]:
            b.get_style_context().add_class("tucked")
        col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        image = Gtk.Image()
        path = icons.find(entries[app]["icon"]) if app in entries else None
        try:
            image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(path, 40, 40))
        except Exception:
            image.set_from_icon_name("application-x-executable", Gtk.IconSize.DND)
        col.pack_start(image, False, False, 0)
        label = Gtk.Label(label=name)
        label.get_style_context().add_class("hf-sw-app")
        col.pack_start(label, False, False, 0)
        title = Gtk.Label(label=w["title"] if w["title"] != name else "")
        title.set_ellipsize(Pango.EllipsizeMode.END)
        title.set_max_width_chars(TITLE_CHARS)
        col.pack_start(title, False, False, 0)
        place = Gtk.Label(label=where(w))
        place.get_style_context().add_class("hf-sw-where")
        col.pack_start(place, False, False, 0)
        b.add(col)
        b.connect("clicked", lambda _b, i=n: (show(i), pick(i)))
        cards.append(b)
        grid.add(b)
    if not wins:
        empty = Gtk.Label(label="Nothing tucked away" if tucked_only else "No windows open")
        empty.get_style_context().add_class("hf-sw-empty")
        grid.add(empty)
    show(state["at"])

    # the one title row (D-116; Javier, 2026-10-24: "give all popups their title")
    panel = panelkit.Panel("switcher", panelkit.titled(grid, "Tucked away" if tucked_only else "Open windows"),
                           look, edges=[])

    def key(_w, event):
        k = event.keyval
        if k in (Gdk.KEY_Tab, Gdk.KEY_Right, Gdk.KEY_Down):
            show(state["at"] + 1)
        elif k in (Gdk.KEY_ISO_Left_Tab, Gdk.KEY_Left, Gdk.KEY_Up):
            show(state["at"] - 1)
        elif k in (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_space):
            pick()
        else:
            return False
        return True

    def released(_w, event):
        if getattr(args, "hold", False) and event.keyval in (Gdk.KEY_Alt_L, Gdk.KEY_Alt_R, Gdk.KEY_Meta_L):
            pick()
        return False

    panel.window.connect("key-press-event", key)
    panel.window.connect("key-release-event", released)

    # Alt + Tab again while it's open: Sway runs the key, hypeforge-panel tells this one to move on
    early = getattr(args, "pending", [])
    if early:
        show(state["at"] + sum(early))                  # the Tabs that came while it started
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR1, lambda *_: (show(state["at"] + 1), True)[1])
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR2, lambda *_: (show(state["at"] - 1), True)[1])

    if getattr(args, "hold", False):
        # letting go of Alt picks. Once the switcher has the keyboard, Sway tells it which keys are
        # held; Alt already up then (a quick tap) picks at once — the last two windows flip.
        keymap = Gdk.Keymap.get_for_display(Gdk.Display.get_default())
        watching = {"on": False}

        def poll():
            if state["done"]:
                return False
            if not keymap.get_modifier_state() & Gdk.ModifierType.MOD1_MASK:
                pick()
                return False
            return True

        def focused(*_):
            if not watching["on"]:
                watching["on"] = True
                GLib.timeout_add(40, poll)
            return False
        panel.window.connect("focus-in-event", focused)
    return panel
