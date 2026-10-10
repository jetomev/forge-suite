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

NOTIFY = panelkit.APPLETS / "notifications/hypeforge-notifications"
SNAPSHOT = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "kognog/updates.json"
NIGHTFORGE_LIBS = [Path("/usr/lib/nightforge"), Path.home() / "Programs/forge-suite/nightforge"]
CSS = """
.hf-quick {{ min-width: 460px; }}
.hf-quick .hf-tile {{ min-height: 50px; padding: 6px; }}
.hf-quick .hf-tile-name {{ font-size: {small}pt; }}
.hf-quick .hf-tile-sub {{ font-size: {tiny}pt; color: {dim}; }}
.hf-quick button.on .hf-tile-sub {{ color: {on_text}; }}
.hf-quick scale trough {{ min-height: 4px; border-radius: 999px; background: {track}; }}
.hf-quick scale highlight {{ border-radius: 999px; background: {accent}; }}
.hf-quick scale slider {{ min-width: 16px; min-height: 16px; border-radius: 999px; background: {accent};
                          border: 3px solid {card}; box-shadow: none; }}
.hf-quick .hf-foot {{ border-top: 1px solid {line}; padding-top: 8px; }}
"""


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
        ssid = next((l.split(":", 1)[1] for l in self.run(["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"]).splitlines()
                     if l.startswith("yes:")), "")
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
    provider.load_from_data(CSS.format(small=look.size * 0.95, tiny=look.size * 0.8, dim=c["panel_text_dim"],
                                       on_text=c["panel_tile_on_text"], track=c["panel_tile"], accent=c["panel_tile_on"],
                                       card=c["panel_bg"], line=c["panel_border"]).encode())
    Gtk.StyleContext.add_provider_for_screen(panelkit.Gdk.Screen.get_default(), provider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
    be, night = Backend(), Night()
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    root.get_style_context().add_class("hf-quick")
    grid = Gtk.Grid(column_spacing=8, row_spacing=8, column_homogeneous=True)
    root.pack_start(grid, False, False, 0)

    def refresh_later():
        GLib.timeout_add(700, lambda: (fill_tiles(), False)[1])

    def toggler(fn, on):
        def clicked(_b):
            fn(on)
            refresh_later()
        return clicked

    def fill_tiles():
        for child in grid.get_children():
            grid.remove(child)
        tiles = []
        on, sub = be.wifi()
        tiles.append(("Wi-Fi", "network-wireless", on, sub, toggler(be.wifi_toggle, on)))
        on, sub = be.bluetooth()
        tiles.append(("Bluetooth", "bluetooth", on, sub, toggler(be.bluetooth_toggle, on)))
        if night.ok:
            warm, why, _k, _m = night.state()
            tiles.append(("Night light", "weather-clear-night", warm, why, toggler(night.toggle, warm)))
        on, sub = be.dnd()
        tiles.append(("Do Not Disturb", "notifications-disabled", on, sub, toggler(be.dnd_toggle, on)))
        _n, sub = be.screens()
        tiles.append(("Screens", "video-display", False, sub,
                      lambda _b: (panel.close(), panelkit.run_command("alacritty --class displayforge -e displayforge"))))
        if be.vpn_available():
            on, sub = be.vpn()
            tiles.append(("VPN", "network-vpn", on, sub, toggler(be.vpn_toggle, on)))
        for i, (name, icon, on, sub, fn) in enumerate(tiles):
            grid.attach(tile(name, icon, on, sub, fn), i % 3, i // 3, 1, 1)
        grid.show_all()

    fill_tiles()

    # the sliders
    level, muted = be.volume()
    if level is not None:
        row = Gtk.Box(spacing=10)
        mute = Gtk.Button.new_from_icon_name("audio-volume-muted" if muted else "audio-volume-high", Gtk.IconSize.BUTTON)
        mute.get_style_context().add_class("flat")
        mute.connect("clicked", lambda b: (be.mute_toggle(), b.set_image(Gtk.Image.new_from_icon_name(
            "audio-volume-muted" if be.volume()[1] else "audio-volume-high", Gtk.IconSize.BUTTON))))
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        scale.set_value(level)
        scale.set_draw_value(False)
        value = Gtk.Label(label=f"{level} %")
        scale.connect("value-changed", lambda s: (be.set_volume(s.get_value()), value.set_text(f"{int(s.get_value())} %")))
        row.pack_start(mute, False, False, 0)
        row.pack_start(scale, True, True, 0)
        row.pack_start(value, False, False, 0)
        root.pack_start(row, False, False, 0)
    if night.ok:
        _w, _why, kelvin, mode = night.state()
        row = Gtk.Box(spacing=10)
        row.pack_start(Gtk.Image.new_from_icon_name("weather-clear-night", Gtk.IconSize.BUTTON), False, False, 0)
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 3000, 5000, 500)
        scale.set_inverted(True)                  # warmer to the right
        scale.set_value(kelvin)
        scale.set_draw_value(False)
        value = Gtk.Label(label=f"{kelvin} K")
        scale.connect("value-changed", lambda s: value.set_text(f"{int(round(s.get_value() / 500) * 500)} K"))
        scale.connect("button-release-event", lambda s, *_: (night.set_warmth(round(s.get_value() / 500) * 500), refresh_later(), False)[2])
        row.pack_start(scale, True, True, 0)
        row.pack_start(value, False, False, 0)
        if mode != "auto":
            back = Gtk.Button(label="Automatic")
            back.get_style_context().add_class("flat")
            back.connect("clicked", lambda _b: (night.automatic(), refresh_later()))
            row.pack_start(back, False, False, 0)
        root.pack_start(row, False, False, 0)

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
    settings.connect("clicked", lambda _b: (panel.close(), panelkit.run_command("hypeforge-settings")))
    foot.pack_end(power, False, False, 0)
    foot.pack_end(settings, False, False, 0)
    root.pack_start(foot, False, False, 0)

    edges = args.edges.split(",") if getattr(args, "edges", None) else ["bottom", "right"]
    margins = dict(m.split("=") for m in args.margin.split(",")) if getattr(args, "margin", None) else {"bottom": 60, "right": 10}
    panel = panelkit.Panel("quick", root, look, edges=edges, margins={k: int(v) for k, v in margins.items()})
    return panel
