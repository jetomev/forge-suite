"""Quick Settings (Windows 11 W-3, D-71; also macOS's Control Center, D-74): six tiles, two
sliders, the update count.

Every tile switches the real thing through the program that owns it, so the bar, the apps and
this panel never disagree:
  Wi-Fi           NetworkManager (`nmcli radio wifi on|off`); the network's name, or "off"
  Bluetooth       `bluetoothctl power on|off`; the connected device's name
  Night light     nightForge (Warm Now / Daylight Now; "Automatic" puts the schedule back)
  Do Not Disturb  the bell applet (`hypeforge-notifications dnd`), so the bell redraws too
  Screens         opens displayForge
  VPN             Private Internet Access (`piactl connect|disconnect`), when it is installed
Sliders: the volume (WirePlumber, `wpctl`), the night warmth (nightForge's own settings). The
footer: updates from KognogOS's snapshot (~/.cache/kognog/updates.json; a click opens nogForge),
hypeForge Settings, the power buttons.

`--only network|sound|bluetooth|night` (COSMIC's C-5, D-77; night: the Rice's moon, 10-10): one
small pop-up per status icon — just that part, with a button to its full settings app (nmtui,
wiremix, bluetui, nightForge).

Pages (D-117, 2026-10-25, views/qspages.py): a click on a big tile that has a page (Night light, Wi-Fi), or on
the icon right of the volume's number, opens that part's page inside this same card — "‹" or Esc goes
back; its on/off switch is on the page; the speaker mutes. `--only night|sound|network` opens that page alone.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from gi.repository import GLib, Gtk

import panelkit
import qspages

NOTIFY = panelkit.APPLETS / "notifications/hypeforge-notifications"
SNAPSHOT = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "kognog/updates.json"
NIGHTFORGE_LIBS = [Path("/usr/lib/nightforge"), Path.home() / "Programs/forge-suite/nightforge"]
CSS = """
.hf-quick .hf-tile {{ min-height: 50px; padding: 6px; }}
.hf-quick .hf-tile-name {{ font-size: {small}pt; }}
.hf-quick .hf-tile-sub {{ font-size: {tiny}pt; color: {dim}; }}
.hf-quick button.on .hf-tile-sub {{ color: {on_text}; }}
.hf-quick scale trough {{ min-height: 4px; border-radius: {pill}px; background: {track}; }}
.hf-quick scale highlight {{ border-radius: {pill}px; background: {accent}; }}
.hf-quick scale slider {{ min-width: 16px; min-height: 16px; border-radius: {pill}px; background: {accent};
                          border: 3px solid {card}; box-shadow: none; }}
.hf-quick .hf-foot {{ border-top: 1px solid {line}; padding-top: 8px; }}
"""
# the one-part pop-ups (C-5): which tiles and sliders each shows, and its full settings app
ONLY = {
    "network": ("Network", ("Wi-Fi", "VPN"), "hypeforge-nmtui"),
    "sound": ("Sound", (), "alacritty --class hf-mixer -o window.dimensions.columns=110 -o window.dimensions.lines=30 -e wiremix"),
    "night": ("Night light", ("Night light",), "alacritty --class nightforge -e nightforge"),
    "bluetooth": ("Bluetooth", ("Bluetooth",),
                  "alacritty --class hf-bluetooth -o window.dimensions.columns=110 -o window.dimensions.lines=30 -e bluetui"),
}
# Settings is a terminal app: its launcher entry opens it in its window (a bare start showed nothing, 10-10)
SETTINGS = f"{panelkit.APPLETS / 'sections/hypeforge-sections'} launch hypeforge-settings"


def run(cmd: list[str], timeout: float = 3.0) -> str:
    """A command's output, or "" when it is missing, fails or hangs (a tile then shows "—")."""
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


# ---- Each tile: what it shows, what a click does -----------------------------------------------

class Backend:
    """The tiles' facts and switches. `runner` is swapped out in the tests."""

    def __init__(self, runner=run):
        self.run = runner

    # Wi-Fi
    def wifi(self):
        radio = self.run(["nmcli", "-t", "-f", "WIFI", "radio"]).strip()
        if not radio:
            return None, "—"
        on = radio == "enabled"
        # the network's name from the active connection: asking for the Wi-Fi list makes NetworkManager scan
        # first when its last scan is over ~30 s old (5 s here, 2026-10-17: the pop-ups "take time to appear")
        ssid = next((l.split(":", 1)[1] for l in self.run(["nmcli", "-t", "-f", "TYPE,NAME", "connection", "show",
                                                             "--active"]).splitlines()
                     if l.startswith("802-11-wireless:")), "")
        wired = any(":ethernet:connected" in l for l in self.run(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "dev"]).splitlines())
        return on, ssid if on and ssid else ("on" if on else "off · wired" if wired else "off")

    def wifi_toggle(self, on):
        self.run(["nmcli", "radio", "wifi", "off" if on else "on"])

    # Bluetooth
    def bluetooth(self):
        show = self.run(["bluetoothctl", "show"])
        if "Powered:" not in show:
            return None, "—"
        on = "Powered: yes" in show
        device = next((l.split(" ", 2)[2] for l in self.run(["bluetoothctl", "devices", "Connected"]).splitlines()
                       if l.startswith("Device ") and len(l.split(" ", 2)) == 3), "")
        return on, device if on and device else ("on" if on else "off")

    def bluetooth_toggle(self, on):
        self.run(["bluetoothctl", "power", "off" if on else "on"])

    # Do Not Disturb
    def dnd(self):
        modes = self.run(["makoctl", "mode"]).split()
        return ("do-not-disturb" in modes), ("on" if "do-not-disturb" in modes else "off")

    def dnd_toggle(self, _on):
        self.run([str(NOTIFY), "dnd"])

    # VPN
    def vpn_available(self):
        return bool(shutil.which("piactl"))

    def vpn(self):
        state = self.run(["piactl", "get", "connectionstate"]).strip()
        if not state:
            return None, "—"
        on = state == "Connected"
        region = self.run(["piactl", "get", "region"]).strip() if on else ""
        return on, region or state.lower()

    def vpn_toggle(self, on):
        self.run(["piactl", "disconnect" if on else "connect"], timeout=8)

    # Screens
    def screens(self):
        n = sum(1 for o in panelkit.sway_ask(3) if o.get("active"))    # GET_OUTPUTS
        return None, f"{n} screen{'s' if n != 1 else ''}" if n else "—"

    # Volume
    def volume(self):
        out = self.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
        m = re.search(r"Volume:\s*([\d.]+)", out)
        return (round(float(m.group(1)) * 100) if m else None), "[MUTED]" in out

    def set_volume(self, percent):
        self.run(["wpctl", "set-volume", "-l", "1.0", "@DEFAULT_AUDIO_SINK@", f"{int(percent)}%"])

    def mute_toggle(self):
        self.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])

    # Updates (KognogOS's snapshot, written by its update timer; never a network call here)
    def updates(self):
        try:
            snap = json.loads(SNAPSHOT.read_text())
        except (OSError, ValueError):
            return "Updates: not checked yet"
        ready, count = len(snap.get("ready") or []), int(snap.get("count") or 0)
        if ready:
            return f"{ready} update{'s' if ready != 1 else ''} ready · nog"
        return f"{count} waiting their turn · nog" if count else "Up to date · nog"


def short(why: str) -> str:
    """nightForge's sentence, cut to fit a tile: "warm again from 18:59" → "from 18:59",
    "4500 K since 18:46 · daylight at 07:02" → "until 07:02", "Warm Now, …" → "warm now"."""
    import re as _re
    m = _re.search(r"daylight at (\d\d:\d\d)", why)
    if m:
        return f"until {m.group(1)}"
    m = _re.search(r"warm again from (\d\d:\d\d)", why)
    if m:
        return f"from {m.group(1)}"
    for start, words in (("Warm Now", "warm now"), ("Daylight Now", "daylight now"), ("switched off", "off")):
        if why.startswith(start):
            return words
    return why


class Night:
    """nightForge, through its own code (the tray icon's way): Warm Now, Daylight Now, Automatic,
    and the evening warmth. None when nightForge isn't installed."""

    def __init__(self):
        for lib in NIGHTFORGE_LIBS:
            if (lib / "nightforge/control.py").exists():
                sys.path.insert(0, str(lib))
                break
        try:
            from nightforge import control, settings
        except ImportError:
            self.ok = False
            return
        self.ok, self.control, self.settings = True, control, settings

    def state(self):
        s = self.settings.Settings.load()
        st = self.control.status(s)
        return st["state"] == "warm", short(st["why"]), s.warmth, st["mode"]

    def sentence(self) -> str:
        """nightForge's own sentence, whole, for the Night light page (the tile has room for `short()` only)."""
        st = self.control.status(self.settings.Settings.load())
        why = st["why"]
        if st["state"] != "warm" and not why.startswith(("Daylight Now", "switched off")):
            why = "Daylight now · " + why
        return why[:1].upper() + why[1:]

    def toggle(self, warm_now: bool):
        self.control.start(self.settings.Settings.load(), "day" if warm_now else "warm")

    def automatic(self):
        self.control.start(self.settings.Settings.load(), "auto")

    def set_warmth(self, kelvin: int):
        s = self.settings.Settings.load()
        s.warmth = int(kelvin)
        s.save()
        self.control.start(s, self.control.mode())


# ---- The panel -----------------------------------------------------------------------------

def redraw_moon():
    """The bar's night-light moon follows a switch made here at once (SIGRTMIN+13)."""
    sys.path.insert(0, str(panelkit.APPLETS / "common"))
    try:
        import signal as _signal
        from hfbar import signal_bar
        signal_bar(_signal.SIGRTMIN + 13, wait=0.5)
    except Exception:
        pass


# Which sliders each pop-up shows (Javier, 2026-10-24: the night light has its own pop-up, so the full Quick
# Settings keeps its tile, not the warmth slider)
SLIDERS = {None: ("volume",), "network": (), "bluetooth": ()}   # night and sound: their pages (D-117)


def slider(low, high, step, now, words, changed=None, inverted=False):
    """A slider and ITS number, tied together here (2026-10-24: two rows named their number `value`, and moving
    the volume rewrote the night light's). `words(v)` is what the number says; `changed(v)` runs on a move."""
    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, low, high, step)
    scale.set_inverted(inverted)
    scale.set_value(now)
    scale.set_draw_value(False)
    number = Gtk.Label(label=words(now))

    def moved(s):
        number.set_text(words(s.get_value()))
        if changed:
            changed(s.get_value())
    scale.connect("value-changed", moved)
    return scale, number


def volume_row(be, level, muted, opened=None):
    """The volume: the speaker mutes, the slider and its number, and — in Quick Settings — an icon right of
    the number that opens the Sound page (Javier, 2026-10-25: "clicking in the speaker should indeed mute the
    volume… add an icon next to the volume % to the right to open the popup")."""
    row = Gtk.Box(spacing=10)
    mute = Gtk.Button.new_from_icon_name("audio-volume-muted" if muted else "audio-volume-high", Gtk.IconSize.BUTTON)
    mute.get_style_context().add_class("flat")
    mute.set_tooltip_text("Mute")
    mute.connect("clicked", lambda b: (be.mute_toggle(), b.set_image(Gtk.Image.new_from_icon_name(
        "audio-volume-muted" if be.volume()[1] else "audio-volume-high", Gtk.IconSize.BUTTON))))
    scale, number = slider(0, 100, 1, level, lambda v: f"{int(v)} %", be.set_volume)
    row.pack_start(mute, False, False, 0)
    row.pack_start(scale, True, True, 0)
    row.pack_start(number, False, False, 0)
    row.mute, row.scale = mute, scale
    row.more = None
    if opened:
        more = Gtk.Button.new_from_icon_name("preferences-desktop-sound", Gtk.IconSize.BUTTON)
        more.get_style_context().add_class("flat")
        more.set_tooltip_text("Sound: outputs and microphones")
        more.connect("clicked", lambda _b: opened())
        row.pack_start(more, False, False, 0)
        row.more = more
    return row


def tile(name, icon, on, sub, clicked):
    b = Gtk.Button()
    b.get_style_context().add_class("hf-tile")
    if on:
        b.get_style_context().add_class("on")
    box = Gtk.Box(spacing=8)
    box.pack_start(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.LARGE_TOOLBAR), False, False, 0)
    words = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    n = Gtk.Label(label=name, xalign=0)
    n.get_style_context().add_class("hf-tile-name")
    s = Gtk.Label(label=sub, xalign=0, max_width_chars=20, ellipsize=3)
    s.get_style_context().add_class("hf-tile-sub")
    words.pack_start(n, False, False, 0)
    words.pack_start(s, False, False, 0)
    box.pack_start(words, True, True, 0)
    b.add(box)
    b.connect("clicked", clicked)
    return b


def build(look: panelkit.Look, args) -> panelkit.Panel:
    c = look.colour
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(wide=panelkit.WIDE, narrow=panelkit.NARROW, small=look.size * 0.95, tiny=look.size * 0.8, dim=c["panel_text_dim"],
                                       on_text=c["panel_tile_on_text"], track=c["panel_tile"], accent=c["panel_tile_on"],
                                       card=c["panel_bg"], line=c["panel_border"], pill=look.pill).encode())
    Gtk.StyleContext.add_provider_for_screen(panelkit.Gdk.Screen.get_default(), provider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
    pages_css = Gtk.CssProvider()
    pages_css.load_from_data(qspages.css(look))
    Gtk.StyleContext.add_provider_for_screen(panelkit.Gdk.Screen.get_default(), pages_css,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 2)
    be, night = Backend(), Night()
    only = getattr(args, "only", None)
    # the card is a stack: the main page, and a part's page in its place when its tile is clicked (D-117)
    stack = Gtk.Stack()
    stack.set_homogeneous(False)
    stack.set_transition_type(Gtk.StackTransitionType.NONE)
    stack.get_style_context().add_class("hf-quick")

    tiles = {"fill": lambda: None}            # the tiles, once there are any (a page alone has none)

    def refresh_later():
        GLib.timeout_add(700, lambda: (tiles["fill"](), redraw_moon(), False)[2])

    def shrink():
        if panel is not None:
            panel.window.resize(1, 1)          # the card takes the page's height, smaller or bigger

    def back():
        if stack.get_visible_child_name() == "main":
            return False
        old = stack.get_visible_child()
        stack.set_visible_child_name("main")
        stack.remove(old)
        refresh_later()
        GLib.idle_add(lambda: (shrink(), False)[1])
        return True

    def page_of(name, with_back):
        go_back = back if with_back else None
        close = lambda: panel.close()
        if name == "night":
            return qspages.night_page(night, go_back, close, refresh_later)
        if name == "wifi":
            return qspages.wifi_page(be.run, go_back, close, refresh_later)
        return qspages.sound_page(be, go_back, close)

    def open_page(name):
        page = page_of(name, True)
        page.get_style_context().add_class("hf-quick")
        stack.add_named(page, name)
        page.show_all()
        stack.set_visible_child_name(name)
        GLib.idle_add(lambda: (shrink(), False)[1])

    if only in qspages.ONLY_PAGE:              # a bar icon's pop-up: the page alone, no "‹"
        page = page_of(qspages.ONLY_PAGE[only], False)
        stack.add_named(page, "main")
        return finish(stack, look, args)

    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    root.get_style_context().add_class("hf-quick")
    if only:
        root.get_style_context().add_class("hf-one")
    # the one title row (D-116): Quick Settings had none; a one-part pop-up names its part
    top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    head = Gtk.Box(spacing=8)
    head.get_style_context().add_class("hf-head")
    name = Gtk.Label(label=ONLY[only][0] if only else "Quick Settings", xalign=0)
    name.get_style_context().add_class("hf-head-name")
    head.pack_start(name, True, True, 0)
    top.pack_start(head, False, False, 0)
    top.pack_start(panelkit.head_line(), False, False, 0)
    root.pack_start(top, False, False, 0)
    grid = Gtk.Grid(column_spacing=8, row_spacing=8, column_homogeneous=True)
    root.pack_start(grid, False, False, 0)

    def toggler(fn, on):
        def clicked(_b):
            fn(on)
            refresh_later()
        return clicked

    def fill_tiles():
        for child in grid.get_children():
            grid.remove(child)
        # each tile asks its own program only when it is shown: the moon's pop-up waited three seconds on
        # Wi-Fi it never showed (2026-10-17)
        makers = [("Wi-Fi", lambda: ("network-wireless", *be.wifi(), be.wifi_toggle)),
                  ("Bluetooth", lambda: ("bluetooth", *be.bluetooth(), be.bluetooth_toggle))]
        if night.ok:
            makers.append(("Night light", lambda: ("weather-clear-night", *night.state()[:2], night.toggle)))
        makers.append(("Do Not Disturb", lambda: ("notifications-disabled", *be.dnd(), be.dnd_toggle)))
        makers.append(("Screens", lambda: ("video-display", False, be.screens()[1], None)))
        if be.vpn_available():
            makers.append(("VPN", lambda: ("network-vpn", *be.vpn(), be.vpn_toggle)))
        if only:
            makers = [m for m in makers if m[0] in ONLY[only][1]]
        for i, (name, make) in enumerate(makers):
            icon, on, sub, switch = make()
            if switch is None:                     # Screens opens displayForge
                fn = lambda _b: (panel.close(), panelkit.run_command("alacritty --class displayforge -e displayforge"))
            elif not only and name in PAGES:       # a tile with a page opens it; the switch is on the page (D-117)
                fn = lambda _b, p=PAGES[name]: open_page(p)
            else:
                fn = toggler(switch, on)
            grid.attach(tile(name, icon, on, sub, fn), i % 3, i // 3, 1, 1)
        grid.show_all()

    tiles["fill"] = fill_tiles
    fill_tiles()

    # the sliders: which ones each pop-up shows (SLIDERS), each built with its own number (slider())
    wanted = SLIDERS.get(only, ())
    level, muted = be.volume() if "volume" in wanted else (None, False)
    if level is not None:
        root.pack_start(volume_row(be, level, muted, None if only else (lambda: open_page("sound"))), False, False, 0)
    elif only == "sound":
        root.pack_start(Gtk.Label(label="No sound device found", xalign=0), False, False, 0)
    if only:                     # a one-part pop-up ends with its full settings app
        more = Gtk.Button(label=f"{ONLY[only][0]} settings…")
        more.get_style_context().add_class("flat")
        more.connect("clicked", lambda _b: (panel.close(), panelkit.run_command(ONLY[only][2])))
        root.pack_start(more, False, False, 0)
        stack.add_named(root, "main")
        return finish(stack, look, args)

    # the footer
    foot = Gtk.Box(spacing=8)
    foot.get_style_context().add_class("hf-foot")
    updates = Gtk.Button(label=be.updates())
    updates.get_style_context().add_class("flat")
    updates.connect("clicked", lambda _b: (panel.close(), panelkit.run_command("alacritty --class nogforge -e nogforge")))
    foot.pack_start(updates, False, False, 0)
    power = Gtk.Button.new_from_icon_name("system-shutdown", Gtk.IconSize.BUTTON)
    power.get_style_context().add_class("flat")
    power.set_tooltip_text("Power")
    power.connect("clicked", lambda _b: (panel.close(), panelkit.run_command(
        f"{shlex.quote(sys.executable)} {shlex.quote(str(panelkit.HERE / 'hypeforge-panel'))} power")))
    settings = Gtk.Button.new_from_icon_name("preferences-system", Gtk.IconSize.BUTTON)
    settings.get_style_context().add_class("flat")
    settings.set_tooltip_text("hypeForge Settings")
    settings.connect("clicked", lambda _b: (panel.close(), panelkit.run_command(SETTINGS)))
    foot.pack_end(power, False, False, 0)
    foot.pack_end(settings, False, False, 0)
    root.pack_start(foot, False, False, 0)
    stack.add_named(root, "main")
    return finish(stack, look, args, escape=back)


PAGES = {"Night light": "night", "Wi-Fi": "wifi"}   # tiles that open a page (D-117); Bluetooth comes next


panel = None


def finish(root, look, args, escape=None) -> panelkit.Panel:
    global panel
    edges = args.edges.split(",") if getattr(args, "edges", None) else ["bottom", "right"]
    margins = dict(m.split("=") for m in args.margin.split(",")) if getattr(args, "margin", None) else {"bottom": 60, "right": 10}
    panel = panelkit.Panel("quick", root, look, edges=edges, margins={k: int(v) for k, v in margins.items()},
                           width=panelkit.WIDE if getattr(args, "only", None) in (None, *qspages.ONLY_PAGE) else panelkit.NARROW)
    panel.escape = escape
    return panel
