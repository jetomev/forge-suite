"""The clipboard history as a panel (Javier, 2026-10-17: "Clipboard, right now, is horrible and without
identity, needs a lot of work to make look good"). It was a plain fuzzel text list; now it is a pop-up
like the calendar and the quick settings, in the style's and theme's own look:

  - a head: the clipboard's icon, how many copies are kept, and **Clear all** (it asks, right there)
  - a search box: type to narrow the list (it has the keys from the start; ↓ goes into the list)
  - every copy a small card: a badge saying what it is (text, link, path, code, a colour — the colour
    itself), or the picture's own thumbnail; two lines of it; a dim line saying what it is; a dot on
    the ones not seen yet; ✕ forgets that one (and ✎ on a picture opens swappy to draw on it)
  - Enter or a click puts it back on the clipboard, and the panel closes

cliphist keeps the history; the applet (`applets/clipboard/hypeforge-clipboard`) still stores every copy
and draws the bar's icon, and its `list` opens this panel. Opening it marks every copy as seen.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import re
import subprocess

import panelkit  # first: it picks GTK 3 before anything asks for GTK
from gi.repository import Gdk, GdkPixbuf, Gtk, Pango  # noqa: E402

ROW = 62              # one copy's height in the list (two lines and the dim line)
SHOWN = 60            # copies listed (cliphist keeps 200); the search looks through all of them
THUMBS = 16           # pictures given a real thumbnail (the rest a badge)
TAB = "\t"

CSS = """
.hf-clip-panel {{ min-width: 440px; }}
.hf-clip-head .hf-clip-glyph {{ font-family: "Symbols Nerd Font", "{font}"; font-size: {big}pt; color: {accent}; }}
.hf-clip-count {{ color: {dim}; }}
.hf-card.hf-clip-list {{ padding: 4px; }}
.hf-clip-list list, .hf-clip-list row {{ background: transparent; }}
.hf-clip-list row {{ border-radius: {inner}px; padding: 6px 8px; margin: 1px 0; color: {text}; }}   /* the panel's text, never the GTK theme's */
.hf-clip-list row:hover {{ background: {hover}; }}
.hf-clip-list row:selected, .hf-clip-list row:selected:focus {{ background: {sel}; color: {sel_text}; }}
.hf-clip-list row:selected .hf-clip-what {{ color: {sel_text}; }}
.hf-clip-badge {{ min-width: 40px; min-height: 40px; border-radius: {inner}px; background: {tile};
                 font-family: "Symbols Nerd Font", "{font}"; font-size: {big}pt; color: {accent}; }}
.hf-clip-what {{ color: {dim}; font-size: {small}pt; }}
.hf-clip-new {{ color: {accent}; font-size: {small}pt; }}
.hf-clip-list button {{ padding: 2px 8px; min-width: 0; min-height: 0; }}
.hf-clip-empty {{ color: {dim}; padding: 18px 8px; }}
"""

# Nerd Font glyphs for each kind (ttf-nerd-fonts-symbols, already the bar's)
GLYPH = {"text": "\U000f09a8", "link": "\U000f0339", "path": "\U000f024b", "code": "\U000f0169",
         "colour": "\U000f03d8", "picture": "\U000f02e9", "clipboard": "\U000f0147"}
WORD = {"text": "Text", "link": "Link", "path": "A file or folder", "code": "Code", "colour": "A colour",
        "picture": "Picture"}
URL = re.compile(r"^(https?://|www\.)\S+$", re.I)
HEX = re.compile(r"^#?([0-9a-f]{6}|[0-9a-f]{3})$", re.I)
PATH = re.compile(r"^(~?/|\./)\S+$")
CODE = re.compile(r"[{};]\s*$|^\s*(def |class |import |from |fn |let |const |function |sudo |\$ )|=>|</?[a-z]+>|\(\)")


def applet():
    """The clipboard applet itself (its history, its 'seen' mark): one place for that logic."""
    path = panelkit.APPLETS / "clipboard/hypeforge-clipboard"
    loader = importlib.machinery.SourceFileLoader("hypeforge_clipboard", str(path))
    spec = importlib.util.spec_from_loader("hypeforge_clipboard", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def kind_of(preview: str, picture) -> str:
    if picture:
        return "picture"
    p = preview.strip()
    if URL.match(p):
        return "link"
    if HEX.match(p):
        return "colour"
    if PATH.match(p):
        return "path"
    if CODE.search(p):
        return "code"
    return "text"


def what_line(kind: str, preview: str, picture) -> str:
    """The dim line under a copy: what it is, in plain words."""
    p = preview.strip()
    if kind == "picture":
        m = re.search(r"(\d+)x(\d+)", preview)
        return f"Picture · {picture.group(1).upper()}" + (f" · {m.group(1)} × {m.group(2)}" if m else "")
    if kind == "link":
        host = re.sub(r"^(https?://)?(www\.)?", "", p).split("/")[0]
        return f"Link · {host}"
    if kind == "colour":
        return f"A colour · #{p.lstrip('#').lower()}"
    words = len(p.split())
    return f"{WORD[kind]} · {words} word{'s' if words != 1 else ''}" if kind == "text" else WORD[kind]


def build(look: panelkit.Look, args) -> panelkit.Panel:
    c = look.colour
    inner = 0 if look.straight else max(4, look.radius // 2)
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(font=look.font, big=look.size * 1.35, small=look.size * 0.88,
                                       accent=c["panel_tile_on"], dim=c["panel_text_dim"], tile=c["panel_tile"],
                                       hover=c["panel_hover"], sel=c["panel_selected"], text=c["panel_text"],
                                       sel_text=c["panel_selected_text"], inner=inner).encode())
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
    clip = applet()
    lines = clip.history()
    before = clip.seen()
    clip.mark_seen(lines)                       # opening it counts as reading: the bar's number goes away

    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    root.get_style_context().add_class("hf-clip-panel")

    # ---- the head
    head = Gtk.Box(spacing=10)
    head.get_style_context().add_class("hf-clip-head")
    glyph = Gtk.Label(label=GLYPH["clipboard"])
    glyph.get_style_context().add_class("hf-clip-glyph")
    head.pack_start(glyph, False, False, 0)
    title = Gtk.Label(label="Clipboard", xalign=0)
    title.get_style_context().add_class("hf-title")
    head.pack_start(title, False, False, 0)
    count = Gtk.Label(label=f"{len(lines)} kept" if lines else "", xalign=0)
    count.get_style_context().add_class("hf-clip-count")
    head.pack_start(count, True, True, 0)
    clear = Gtk.Button(label="Clear all")
    clear.get_style_context().add_class("flat")
    sure = Gtk.Box(spacing=6)
    sure.pack_start(Gtk.Label(label="Empty it?"), False, False, 0)
    yes, no = Gtk.Button(label="Yes"), Gtk.Button(label="No")
    yes.get_style_context().add_class("danger")
    sure.pack_start(yes, False, False, 0)
    sure.pack_start(no, False, False, 0)
    head.pack_end(sure, False, False, 0)
    head.pack_end(clear, False, False, 0)
    sure.show_all()
    sure.set_no_show_all(True)        # the panel shows everything once more when it opens: these stay as set
    clear.set_no_show_all(True)
    root.pack_start(card(head), False, False, 0)

    # ---- the search
    search = Gtk.SearchEntry(placeholder_text="Type to find a copy")
    root.pack_start(search, False, False, 0)

    # ---- the copies
    listbox = Gtk.ListBox()
    listbox.set_selection_mode(Gtk.SelectionMode.BROWSE)
    listbox.set_activate_on_single_click(True)
    scroller = Gtk.ScrolledWindow()
    scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroller.set_propagate_natural_height(True)
    scroller.set_max_content_height(520)
    scroller.add(listbox)
    holder = card(scroller, "hf-clip-list")
    root.pack_start(holder, True, True, 0)
    empty = Gtk.Label(label="Nothing copied yet. What you copy shows up here.", xalign=0.5)
    empty.get_style_context().add_class("hf-clip-empty")
    root.pack_start(empty, False, False, 0)
    empty.set_no_show_all(True)
    holder.set_no_show_all(True)
    scroller.show_all()

    panel_ref = {}
    thumbs = 0
    for line in lines[:SHOWN]:
        num, _, preview = line.partition(TAB)
        picture = clip.PICTURE.match(preview)
        kind = kind_of(preview, picture)
        row = Gtk.ListBoxRow()
        row.entry, row.kind, row.picture, row.text = line, kind, picture, preview.lower()
        box = Gtk.Box(spacing=10)
        badge = None
        if picture and thumbs < THUMBS:
            badge = thumbnail(line, picture, clip)
            thumbs += 1 if badge else 0
        if badge is None:
            badge = Gtk.Label(label=GLYPH[kind])
            badge.get_style_context().add_class("hf-clip-badge")
            if kind == "colour":     # the colour itself, as the badge
                hexv = preview.strip().lstrip("#")
                hexv = "".join(ch * 2 for ch in hexv) if len(hexv) == 3 else hexv
                badge.set_label("")
                swatch = Gtk.CssProvider()
                swatch.load_from_data(f"label {{ background: #{hexv}; }}".encode())
                badge.get_style_context().add_provider(swatch, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 2)
        box.pack_start(badge, False, False, 0)
        words = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        shown = "Picture" if picture else " ".join(preview.split())
        text = Gtk.Label(label=shown, xalign=0, max_width_chars=44, lines=2, wrap=True,
                         wrap_mode=Pango.WrapMode.WORD_CHAR, ellipsize=Pango.EllipsizeMode.END)
        words.pack_start(text, False, False, 0)
        what = Gtk.Box(spacing=6)
        if clip.number(line) > before:
            dot = Gtk.Label(label="● new")
            dot.get_style_context().add_class("hf-clip-new")
            what.pack_start(dot, False, False, 0)
        info = Gtk.Label(label=what_line(kind, preview, picture), xalign=0)
        info.get_style_context().add_class("hf-clip-what")
        what.pack_start(info, False, False, 0)
        words.pack_start(what, False, False, 0)
        box.pack_start(words, True, True, 0)
        forget = Gtk.Button(label="✕")
        forget.set_tooltip_text("Forget this one")
        forget.get_style_context().add_class("flat")
        forget.set_valign(Gtk.Align.CENTER)
        forget.connect("clicked", lambda _b, r=row: forget_row(r, listbox, count, clip))
        box.pack_end(forget, False, False, 0)
        if picture:
            draw = Gtk.Button(label="✎")
            draw.set_tooltip_text("Draw on it (swappy)")
            draw.get_style_context().add_class("flat")
            draw.set_valign(Gtk.Align.CENTER)
            draw.connect("clicked", lambda _b, l=line, p=picture: (open_in_swappy(l, p, clip), panel_ref["p"].close()))
            box.pack_end(draw, False, False, 0)
        row.add(box)
        listbox.add(row)

    listbox.show_all()                 # the rows, drawn: the list's holder skips the panel's own show_all

    def matches(row) -> bool:
        words = search.get_text().strip().lower().split()
        return all(w in row.text or w in row.kind or w in WORD[row.kind].lower() for w in words)

    listbox.set_filter_func(matches)

    def refresh(*_):
        listbox.invalidate_filter()
        visible = [r for r in listbox.get_children() if matches(r)]
        holder.set_visible(bool(visible))
        empty.set_visible(not visible)
        # the list as tall as its copies, up to seven, then it scrolls
        scroller.set_min_content_height(min(len(visible), 7) * ROW)
        if search.get_text().strip() and not visible:
            empty.set_label("No copy has that in it.")
        elif not visible:
            empty.set_label("Nothing copied yet. What you copy shows up here.")
        if visible and listbox.get_selected_row() not in visible:
            listbox.select_row(visible[0])

    search.connect("search-changed", refresh)

    def put_back(_lb, row):
        copy_back(row.entry, row.picture, clip)
        panel_ref["p"].close()

    listbox.connect("row-activated", put_back)

    def on_search_key(_w, event):
        if event.keyval in (Gdk.KEY_Down, Gdk.KEY_Tab):
            row = listbox.get_selected_row() or listbox.get_row_at_index(0)
            if row:
                listbox.select_row(row)
                row.grab_focus()
            return True
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            row = listbox.get_selected_row()
            if row and matches(row):
                put_back(listbox, row)
            return True
        return False

    search.connect("key-press-event", on_search_key)

    def on_list_key(_w, event):
        if event.keyval == Gdk.KEY_Delete:
            row = listbox.get_selected_row()
            if row:
                forget_row(row, listbox, count, clip)
            return True
        ch = event.string
        if ch and ch.isprintable() and not event.state & Gdk.ModifierType.CONTROL_MASK:
            search.grab_focus_without_selecting()      # typing anywhere goes to the search
            search.set_text(search.get_text() + ch)
            search.set_position(-1)
            return True
        return False

    listbox.connect("key-press-event", on_list_key)

    def ask(_b):
        clear.hide()
        sure.show()
        no.grab_focus()

    def cancel(_b):
        sure.hide()
        clear.show()
        search.grab_focus()

    def empty_it(_b):
        subprocess.run(["cliphist", "wipe"], capture_output=True)
        clip.mark_seen([])
        for r in listbox.get_children():
            listbox.remove(r)
        count.set_label("")
        sure.hide()
        refresh()

    clear.connect("clicked", ask)
    no.connect("clicked", cancel)
    yes.connect("clicked", empty_it)

    edges = args.edges.split(",") if getattr(args, "edges", None) else ["top", "right"]
    margins = dict(m.split("=") for m in args.margin.split(",")) if getattr(args, "margin", None) else {"top": 44, "right": 8}
    panel = panelkit.Panel("clipboard", root, look, edges=edges, margins={k: int(v) for k, v in margins.items()},
                           card=False)
    panel_ref["p"] = panel
    panel.window.show_all()
    sure.hide()
    clear.set_visible(bool(lines))
    refresh()
    first = listbox.get_row_at_index(0)
    if first:
        listbox.select_row(first)
    search.grab_focus()
    if getattr(args, "ask_clear", False) and lines:     # the bar icon's right click: "Empty it?" at once
        ask(None)
    return panel


def card(widget: Gtk.Widget, *extra: str) -> Gtk.Box:
    box = Gtk.Box()
    box.get_style_context().add_class("hf-card")
    for cls in extra:
        box.get_style_context().add_class(cls)
    widget.set_hexpand(True)
    box.add(widget)
    return box


def decoded(entry: str) -> bytes:
    return subprocess.run(["cliphist", "decode"], input=entry.encode(), capture_output=True).stdout


def picture_file(entry: str, picture, clip):
    path = clip.RUNTIME / f"hypeforge-clipboard-{entry.split(TAB)[0]}.{picture.group(1).lower()}"
    if not path.exists():
        data = decoded(entry)
        if not data:
            return None
        path.write_bytes(data)
    return path


def thumbnail(entry: str, picture, clip):
    path = picture_file(entry, picture, clip)
    if not path:
        return None
    try:
        pix = GdkPixbuf.Pixbuf.new_from_file(str(path))
    except Exception:
        return None
    side = min(pix.get_width(), pix.get_height())          # the middle square, so it lines up with the badges
    pix = pix.new_subpixbuf((pix.get_width() - side) // 2, (pix.get_height() - side) // 2, side, side)
    pix = pix.scale_simple(40, 40, GdkPixbuf.InterpType.BILINEAR)
    image = Gtk.Image.new_from_pixbuf(pix)
    image.set_size_request(40, 40)
    image.get_style_context().add_class("hf-clip-thumb")
    return image


def copy_back(entry: str, picture, clip) -> None:
    """Back on the clipboard: text as text, a picture as that picture (its own type)."""
    data = decoded(entry)
    if not data:
        return
    cmd = ["wl-copy"] + (["--type", f"image/{'jpeg' if picture.group(1).lower() in ('jpg', 'jpeg') else picture.group(1).lower()}"]
                         if picture else [])
    subprocess.run(cmd, input=data)


def open_in_swappy(entry: str, picture, clip) -> None:
    path = picture_file(entry, picture, clip)
    if path:
        subprocess.Popen(["swappy", "-f", str(path)], start_new_session=True)


def forget_row(row, listbox, count, clip) -> None:
    subprocess.run(["cliphist", "delete"], input=row.entry.encode(), capture_output=True)
    index = row.get_index()
    listbox.remove(row)
    left = len(listbox.get_children())
    count.set_label(f"{left} kept" if left else "")
    nxt = listbox.get_row_at_index(min(index, left - 1)) if left else None
    if nxt:
        listbox.select_row(nxt)
        nxt.grab_focus()
    clip.changed()
