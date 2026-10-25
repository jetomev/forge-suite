"""Quick Settings' pages (D-117, Javier 2026-10-25): a tile's › turns the Quick Settings card into that
part's page — "‹" (or Esc) goes back; nothing is stacked over it. The same page opens alone from a bar
icon (`--only`), without the "‹". Approved from the mock: logs/quick-settings-mock-20261025/.

Every page: the one title row (a "‹" when it came from Quick Settings, the part's on/off switch on the
right where it has one), its rows in the tray menu's look, and its full settings app at the foot.
  Night light   on/off, the schedule in words, the warmth, Warm now / Automatic (nightForge)
  Sound         the volume, your outputs and your microphones; a click makes one the one in use (WirePlumber)
"""

from __future__ import annotations

import re

from gi.repository import GLib, Gtk, Pango

import panelkit

CSS = """
.hf-quick .hf-back {{ padding: 0 8px 0 2px; min-width: 0; }}
.hf-quick .hf-back label {{ font-size: {big}pt; }}
.hf-quick .hf-tile.hf-split {{ border-top-right-radius: 0; border-bottom-right-radius: 0; }}
.hf-quick button.hf-arrow {{ padding: 0 6px; min-width: 0; border-left-width: 0;
                             border-top-left-radius: 0; border-bottom-left-radius: 0; }}
.hf-quick button.hf-arrow.on {{ background: {accent}; color: {on_text}; border-color: {accent}; }}
.hf-quick .hf-section {{ color: {dim}; font-weight: bold; font-size: {small}pt; padding: 2px 10px 0 10px; }}
.hf-page-rows, .hf-page-rows row {{ background: transparent; }}
.hf-page-rows row {{ padding: 4px 10px; border-radius: {inner}px; min-height: 30px; }}
.hf-page-rows row:hover {{ background: {hover}; }}
.hf-page-rows label {{ color: {text}; }}
.hf-page-rows label.hf-row-sub {{ color: {dim}; font-size: {small}pt; }}
.hf-page-rows label.hf-row-on {{ color: {accent}; }}
.hf-quick .hf-status {{ color: {dim}; font-size: {small}pt; padding: 0 10px; }}
"""

# which page each bar icon's pop-up opens (`--only`)
ONLY_PAGE = {"night": "night", "sound": "sound"}


def css(look: panelkit.Look) -> bytes:
    c = look.colour
    return CSS.format(big=look.size * 1.3, accent=c["panel_tile_on"], on_text=c["panel_tile_on_text"],
                      dim=c["panel_text_dim"], small=look.size * 0.9, inner=0 if look.straight else look.radius // 2,
                      hover=c["panel_hover"], text=c["panel_text"]).encode()


# ---- the pieces every page is made of -----------------------------------------------------------

def head(title: str, back=None, switch: bool | None = None, switched=None) -> Gtk.Box:
    """The one title row: "‹" when `back` is given (it is called on a click), the name, an on/off switch."""
    top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    row = Gtk.Box(spacing=4)
    row.get_style_context().add_class("hf-head")
    if back:
        b = Gtk.Button(label="‹")
        for cls in ("flat", "hf-back"):
            b.get_style_context().add_class(cls)
        b.set_tooltip_text("Quick Settings")
        b.connect("clicked", lambda _b: back())
        row.pack_start(b, False, False, 0)
    name = Gtk.Label(label=title, xalign=0)
    name.get_style_context().add_class("hf-head-name")
    row.pack_start(name, True, True, 0)
    if switch is not None:
        sw = Gtk.Switch()
        sw.set_active(bool(switch))
        sw.set_valign(Gtk.Align.CENTER)
        if switched:
            sw.connect("notify::active", lambda s, _p: switched(s.get_active()))
        row.pack_end(sw, False, False, 0)
    top.pack_start(row, False, False, 0)
    top.pack_start(panelkit.head_line(), False, False, 0)
    return top


def section(words: str) -> Gtk.Label:
    lab = Gtk.Label(label=words.upper(), xalign=0)
    lab.get_style_context().add_class("hf-section")
    return lab


def status(words: str) -> Gtk.Label:
    lab = Gtk.Label(label=words, xalign=0, wrap=True)
    lab.get_style_context().add_class("hf-status")
    return lab


def rows(items: list[dict]) -> Gtk.ListBox:
    """items: {icon, name, sub, on (the sub in the accent), button: (words, fn), picked: fn (a click on the row)}."""
    lb = Gtk.ListBox()
    lb.get_style_context().add_class("hf-page-rows")
    lb.set_selection_mode(Gtk.SelectionMode.NONE)
    lb.set_activate_on_single_click(True)
    for it in items:
        r = Gtk.ListBoxRow()
        r.picked = it.get("picked")
        line = Gtk.Box(spacing=10)
        line.pack_start(Gtk.Image.new_from_icon_name(it.get("icon") or "", Gtk.IconSize.LARGE_TOOLBAR), False, False, 0)
        words = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        words.set_valign(Gtk.Align.CENTER)
        words.pack_start(Gtk.Label(label=it["name"], xalign=0, ellipsize=Pango.EllipsizeMode.END, max_width_chars=34),
                         False, False, 0)
        if it.get("sub"):
            sub = Gtk.Label(label=it["sub"], xalign=0, ellipsize=Pango.EllipsizeMode.END, max_width_chars=40)
            sub.get_style_context().add_class("hf-row-on" if it.get("on") else "hf-row-sub")
            words.pack_start(sub, False, False, 0)
        line.pack_start(words, True, True, 0)
        if it.get("button"):
            text, fn = it["button"]
            b = Gtk.Button(label=text)
            b.set_valign(Gtk.Align.CENTER)
            b.connect("clicked", lambda _b, fn=fn: fn())
            line.pack_end(b, False, False, 0)
        r.add(line)
        lb.add(r)
    lb.connect("row-activated", lambda _lb, r: r.picked() if r.picked else None)
    return lb


def foot(words: str, clicked) -> Gtk.Button:
    b = Gtk.Button(label=words)
    b.get_style_context().add_class("flat")
    b.set_halign(Gtk.Align.START)
    b.connect("clicked", lambda _b: clicked())
    return b


# ---- Sound (WirePlumber) ------------------------------------------------------------------------

def parse_wpctl(text: str) -> dict[str, list[dict]]:
    """`wpctl status` → {"Sinks": [{id, name, now}], "Sources": [...]} for Audio only (Video lists cameras)."""
    out: dict[str, list[dict]] = {"Sinks": [], "Sources": []}
    audio, part = False, None
    for line in text.splitlines():
        if not line.startswith((" ", "│", "├", "└")):
            audio = line.strip() == "Audio"
            part = None
            continue
        if not audio:
            continue
        m = re.match(r"^[\s│├└─]*(\w[\w ]*):\s*$", line)
        if m:
            part = m.group(1) if m.group(1) in out else None
            continue
        m = re.match(r"^[\s│]*(\*)?\s*(\d+)\.\s+(.*?)\s*(\[vol:[^\]]*\])?\s*$", line)
        if part and m:
            out[part].append({"id": m.group(2), "name": m.group(3).strip(), "now": bool(m.group(1))})
    return out


def sound_icon(name: str, source: bool) -> str:
    n = name.lower()
    if source:
        return "camera-web" if "webcam" in n or "c920" in n else "audio-input-microphone"
    if any(w in n for w in ("headset", "headphone", "arctis", "buds", "wh-")):
        return "audio-headphones"
    if "hdmi" in n or "displayport" in n:
        return "video-display"
    return "audio-speakers"


def sound_page(be, back, close) -> Gtk.Box:
    from quick import slider               # the same slider as the main card: its number moves with it
    page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    page.pack_start(head("Sound", back), False, False, 0)
    level, muted = be.volume()
    if level is not None:
        row = Gtk.Box(spacing=10)
        row.pack_start(Gtk.Image.new_from_icon_name("audio-volume-muted" if muted else "audio-volume-high",
                                                    Gtk.IconSize.BUTTON), False, False, 0)
        scale, number = slider(0, 100, 1, level, lambda v: f"{int(v)} %", be.set_volume)
        row.pack_start(scale, True, True, 0)
        row.pack_start(number, False, False, 0)
        page.pack_start(row, False, False, 0)
    devices = parse_wpctl(be.run(["wpctl", "status"]))
    lists = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    def fill():
        for child in lists.get_children():
            lists.remove(child)
        now = parse_wpctl(be.run(["wpctl", "status"]))
        for part, words, source in (("Sinks", "Output", False), ("Sources", "Input", True)):
            if not now[part]:
                continue
            lists.pack_start(section(words), False, False, 0)
            lists.pack_start(rows([{"icon": sound_icon(d["name"], source), "name": d["name"],
                                    "sub": "In use" if d["now"] else "", "on": d["now"],
                                    "picked": (lambda i=d["id"]: (be.run(["wpctl", "set-default", i]), fill()))}
                                   for d in now[part]]), False, False, 0)
        lists.show_all()
    if devices["Sinks"] or devices["Sources"]:
        fill()
    else:
        lists.pack_start(status("No sound device found."), False, False, 0)
    page.pack_start(lists, False, False, 0)
    page.pack_start(foot("Sound settings…", lambda: (close(), panelkit.run_command(
        "alacritty --class hf-mixer -o window.dimensions.columns=110 -o window.dimensions.lines=30 -e wiremix"))), False, False, 0)
    return page


# ---- Night light (nightForge) -------------------------------------------------------------------

def night_page(night, back, close, refresh) -> Gtk.Box:
    from quick import slider
    page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    if not night.ok:
        page.pack_start(head("Night light", back), False, False, 0)
        page.pack_start(status("nightForge isn't installed."), False, False, 0)
        return page
    warm, _why, kelvin, mode = night.state()
    words = status(night.sentence())
    page.pack_start(head("Night light", back, warm, lambda on: (night.toggle(not on), refresh(),
                                                               GLib.timeout_add(600, lambda: (words.set_text(night.sentence()), False)[1]))),
                    False, False, 0)
    page.pack_start(words, False, False, 0)
    row = Gtk.Box(spacing=10)
    row.pack_start(Gtk.Image.new_from_icon_name("weather-clear-night", Gtk.IconSize.BUTTON), False, False, 0)
    scale, number = slider(3000, 5000, 500, kelvin, lambda v: f"{int(round(v / 500) * 500)} K", inverted=True)
    # set when the slider is let go (nightForge restarts its filter), not on every step
    scale.connect("button-release-event", lambda s, *_: (night.set_warmth(round(s.get_value() / 500) * 500), refresh(), False)[2])
    row.pack_start(scale, True, True, 0)
    row.pack_start(number, False, False, 0)
    page.pack_start(row, False, False, 0)
    buttons = Gtk.Box(spacing=8)
    now = Gtk.Button(label="Warm now")
    now.connect("clicked", lambda _b: (night.toggle(False), refresh()))
    auto = Gtk.Button(label="Automatic")
    auto.set_sensitive(mode != "auto")
    auto.connect("clicked", lambda _b: (night.automatic(), refresh()))
    buttons.pack_start(now, False, False, 0)
    buttons.pack_start(auto, False, False, 0)
    page.pack_start(buttons, False, False, 0)
    page.pack_start(foot("Night light settings…", lambda: (close(), panelkit.run_command(
        "alacritty --class nightforge -e nightforge"))), False, False, 0)
    return page
