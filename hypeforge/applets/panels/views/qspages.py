"""Quick Settings' pages (D-117, Javier 2026-10-25): a click on a big tile turns the Quick Settings card
into that part's page — "‹" (or Esc) goes back; nothing is stacked over it. No arrows (Javier, after the
first build: "no arrow to open the popup. If I click in the quick settings big button, the popup opens…").
The same page opens alone from a bar icon (`--only`), without the "‹".

Every page: the one title row (a "‹" when it came from Quick Settings, the part's on/off switch on the
right where it has one), its rows in the tray menu's look, and an icon button at the bottom right that
opens its full app (Javier: "a button/icon bottom right side of the popup").
  Night light   on/off, the schedule in words, the warmth, Warm now / Automatic (nightForge)
  Sound         the volume, your outputs and your microphones; a click makes one the one in use (WirePlumber)
  Wi-Fi         on/off; the cable; the networks nearby, strongest first: a click connects (a password box
                opens under a new secured one), the connected one has Disconnect (NetworkManager, nmcli)
  Bluetooth     on/off; your devices, the connected ones first, Connect / Disconnect, the battery when the
                device tells it; "Pair a new device…" opens the full app (BlueZ, bluetoothctl)
  Printer       your printers and what they're doing, the jobs waiting with Cancel; Print Settings at the foot
                (CUPS, through the printer applet: Javier, 2026-10-25, "move the Printer" into Quick Settings)
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
import threading
from pathlib import Path

from gi.repository import GLib, Gtk, Pango

import panelkit

CSS = """
.hf-quick .hf-back {{ padding: 0 8px 0 2px; min-width: 0; }}
.hf-quick .hf-back label {{ font-size: {big}pt; }}
.hf-quick .hf-section {{ color: {dim}; font-weight: bold; font-size: {small}pt; padding: 2px 10px 0 10px; }}
.hf-page-rows, .hf-page-rows row {{ background: transparent; }}
.hf-page-rows row {{ padding: 4px 10px; border-radius: {inner}px; min-height: 30px; }}
.hf-page-rows row:hover {{ background: {hover}; }}
.hf-page-rows label, .hf-page-rows image {{ color: {text}; }}
.hf-quick image {{ color: {text}; }}
.hf-quick button.on image {{ color: {on_text}; }}
.hf-page-rows label.hf-row-sub {{ color: {dim}; font-size: {small}pt; }}
.hf-page-rows label.hf-row-on {{ color: {accent}; }}
.hf-quick .hf-status {{ color: {dim}; font-size: {small}pt; padding: 0 10px; }}
"""

# which page each bar icon's pop-up opens (`--only`)
ONLY_PAGE = {"night": "night", "sound": "sound", "network": "wifi", "bluetooth": "bluetooth"}


def css(look: panelkit.Look) -> bytes:
    c = look.colour
    return CSS.format(big=look.size * 1.3, accent=c["panel_tile_on"], on_text=c["panel_tile_on_text"],
                      dim=c["panel_text_dim"], small=look.size * 0.9, inner=0 if look.straight else look.radius // 2,
                      hover=c["panel_hover"], text=c["panel_text"]).encode()


# ---- the pieces every page is made of -----------------------------------------------------------

def mono(name: str, *instead: str) -> str:
    """The one-colour (symbolic) version of an icon, drawn in the card's text colour (Javier, 2026-10-27, the
    Rice review: "fix 1" — Quick Settings mixed one-colour symbols with full-colour pictures, and the
    headphones came out dark blue on the dark card). `instead`: names to try when the icon set has no
    one-colour version of the first."""
    theme = Gtk.IconTheme.get_default()
    for n in (name, *instead):
        if not n:
            continue
        sym = n if n.endswith("-symbolic") else n + "-symbolic"
        if theme is None or theme.has_icon(sym):
            return sym
    return name


def friendly(name: str, source: bool) -> str:
    """A sound device's name as people say it (Javier, 2026-10-27: "fix 2" — "GA106 High Definition Audio
    Controller Digital Stereo (…" was cut off). PipeWire's description, shortened: the monitor's name and its
    port, the computer's own jack, the "Analog Stereo" endings dropped. The full name stays on hover."""
    m = re.match(r"^(.*?)\s*\[(.+)\]$", name)
    if m:                                             # a screen's speakers: "… Digital Stereo (HDMI) [Sceptre Y27]"
        port = re.search(r"\(([^()]+)\)\s*$", m.group(1))
        return f"{m.group(2)} · {port.group(1)}" if port else m.group(2)
    if "audio controller" in name.lower():            # the computer's own chip, no screen named
        if "digital" in name.lower() or "hdmi" in name.lower():
            return "HDMI audio"
        return "Microphone jack" if source else "Speakers jack"
    m = re.match(r"^(.*?)\s+(?:Analog |Digital )?(?:Stereo|Mono|Surround [0-9.]+)\s*(?:\(([^()]+)\))?$", name)
    if m:                                             # "… Analog Stereo", "… Digital Stereo (HDMI 2)"
        return f"{m.group(1)} · {m.group(2)}" if m.group(2) else m.group(1)
    return name


def head(title: str, back=None, switch: bool | None = None, switched=None, extra=()) -> Gtk.Box:
    """The one title row: "‹" when `back` is given (it is called on a click), the name, an on/off switch,
    and `extra` buttons left of the switch (Wi-Fi's refresh)."""
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
    for w in extra:
        row.pack_end(w, False, False, 0)
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
        if it.get("tip"):
            r.set_tooltip_text(it["tip"])
        line = Gtk.Box(spacing=10)
        line.pack_start(Gtk.Image.new_from_icon_name(mono(it.get("icon") or ""), Gtk.IconSize.LARGE_TOOLBAR), False, False, 0)
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


def foot(app: str, clicked, icon: str = "preferences-system") -> Gtk.Box:
    """The page's last row: its full app as an icon button at the bottom right (its name on hover)."""
    row = Gtk.Box(spacing=8)
    b = Gtk.Button.new_from_icon_name(mono(icon), Gtk.IconSize.BUTTON)
    b.get_style_context().add_class("flat")
    b.set_tooltip_text(f"Open {app}")
    b.connect("clicked", lambda _b: clicked())
    row.pack_end(b, False, False, 0)
    return row


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
        mute = Gtk.Button.new_from_icon_name(mono("audio-volume-muted" if muted else "audio-volume-high"), Gtk.IconSize.BUTTON)
        mute.get_style_context().add_class("flat")
        mute.set_tooltip_text("Mute")
        mute.connect("clicked", lambda b: (be.mute_toggle(), b.set_image(Gtk.Image.new_from_icon_name(
            mono("audio-volume-muted" if be.volume()[1] else "audio-volume-high"), Gtk.IconSize.BUTTON))))
        row.pack_start(mute, False, False, 0)
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
            lists.pack_start(rows([{"icon": sound_icon(d["name"], source), "name": friendly(d["name"], source),
                                    "tip": d["name"],
                                    "sub": "In use" if d["now"] else "", "on": d["now"],
                                    "picked": (lambda i=d["id"]: (be.run(["wpctl", "set-default", i]), fill()))}
                                   for d in now[part]]), False, False, 0)
        lists.show_all()
    if devices["Sinks"] or devices["Sources"]:
        fill()
    else:
        lists.pack_start(status("No sound device found."), False, False, 0)
    page.pack_start(lists, False, False, 0)
    page.pack_start(foot("the mixer (wiremix)", lambda: (close(), panelkit.run_command(
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
    row.pack_start(Gtk.Image.new_from_icon_name(mono("weather-clear-night"), Gtk.IconSize.BUTTON), False, False, 0)
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
    page.pack_start(foot("nightForge", lambda: (close(), panelkit.run_command(
        "alacritty --class nightforge -e nightforge"))), False, False, 0)
    return page


# ---- Wi-Fi (NetworkManager) --------------------------------------------------------------------

FIELDS = re.compile(r"(?<!\\):")


def nm_fields(line: str) -> list[str]:
    """One `nmcli -t` line: fields split on ":" — a ":" inside a value comes escaped as "\\:"."""
    return [f.replace("\\:", ":").replace("\\\\", "\\") for f in FIELDS.split(line)]


def parse_networks(text: str) -> list[dict]:
    """`nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY dev wifi list` → one row per name (its strongest), the
    connected one first, then strongest first; hidden networks (no name) left out."""
    best: dict[str, dict] = {}
    for line in text.splitlines():
        f = nm_fields(line)
        if len(f) < 4 or not f[1]:
            continue
        n = {"ssid": f[1], "signal": int(f[2]) if f[2].isdigit() else 0, "security": f[3].strip(),
             "now": f[0].strip() == "*"}
        old = best.get(n["ssid"])
        if old is None or n["now"] or (not old["now"] and n["signal"] > old["signal"]):
            best[n["ssid"]] = n
    return sorted(best.values(), key=lambda n: (not n["now"], -n["signal"]))


def parse_cables(text: str) -> list[dict]:
    """`nmcli -t -f DEVICE,TYPE,STATE,CONNECTION dev` → the cable ports, with what they say."""
    out = []
    for line in text.splitlines():
        f = nm_fields(line)
        if len(f) >= 4 and f[1] == "ethernet":
            on = f[2] == "connected"
            out.append({"device": f[0], "name": f[3] or "Cable", "now": on,
                        "sub": "Connected" if on else "Cable unplugged" if f[2] == "unavailable" else f[2].capitalize()})
    return out


def signal_icon(signal: int) -> str:
    """The bars, as a symbolic icon: drawn in the card's text colour (a full-colour one came out black on the
    dark card)."""
    return "network-wireless-signal-" + ("excellent" if signal >= 75 else "good" if signal >= 50
                                         else "ok" if signal >= 25 else "weak") + "-symbolic"


class Wifi:
    """What the page asks NetworkManager, through `nmcli` (the same as the tile). `run` is swapped in tests."""

    def __init__(self, run):
        self.run = run

    def on(self) -> bool | None:
        r = self.run(["nmcli", "-t", "-f", "WIFI", "radio"]).strip()
        return None if not r else r == "enabled"

    def switch(self, on: bool):
        self.run(["nmcli", "radio", "wifi", "on" if on else "off"])

    def cables(self) -> list[dict]:
        return parse_cables(self.run(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "dev"]))

    def networks(self) -> list[dict]:
        # --rescan no: what NetworkManager already saw (a scan takes seconds; rescan() asks for a new one)
        return parse_networks(self.run(["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "dev", "wifi", "list",
                                        "--rescan", "no"]))

    def rescan(self):
        self.run(["nmcli", "dev", "wifi", "rescan"], timeout=10)

    def saved(self) -> set[str]:
        return {nm_fields(l)[0] for l in self.run(["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"]).splitlines()
                if nm_fields(l)[-1] == "802-11-wireless"}

    def connect(self, ssid: str, security: str, password: str | None = None, hidden: bool = False) -> bool:
        """A saved network, or an open one: straight up. A new secured one: a profile, then up with the
        password in a private file (never on a command line, where any program could read it); a wrong
        password takes the new profile away again, so the next try asks again."""
        if ssid in self.saved():
            return self._ok(self.run(["nmcli", "connection", "up", "id", ssid], timeout=45))
        if not security and not hidden:
            return self._ok(self.run(["nmcli", "dev", "wifi", "connect", ssid], timeout=45))
        key = "sae" if "WPA3" in security and "WPA2" not in security else "wpa-psk"
        add = ["nmcli", "connection", "add", "type", "wifi", "con-name", ssid, "ssid", ssid]
        if hidden:                                  # a network that doesn't say its name: asked for by name
            add += ["802-11-wireless.hidden", "yes"]
        if password or not hidden:
            add += ["wifi-sec.key-mgmt", key]
        if not self._ok(self.run(add)):
            return False
        if hidden and not password:                 # an open hidden network: no password to hand over
            ok = self._ok(self.run(["nmcli", "connection", "up", "id", ssid], timeout=45))
            if not ok:
                self.run(["nmcli", "connection", "delete", "id", ssid])
            return ok
        fd, path = tempfile.mkstemp(prefix="hf-wifi-", dir=os.environ.get("XDG_RUNTIME_DIR") or None)
        try:
            with os.fdopen(fd, "w") as f:                     # mkstemp: only this person can read it
                f.write(f"802-11-wireless-security.psk:{password or ''}\n")
            ok = self._ok(self.run(["nmcli", "connection", "up", "id", ssid, "passwd-file", path], timeout=45))
        finally:
            Path(path).unlink(missing_ok=True)
        if not ok:
            self.run(["nmcli", "connection", "delete", "id", ssid])
        return ok

    def disconnect(self, ssid: str):
        self.run(["nmcli", "connection", "down", "id", ssid], timeout=20)

    @staticmethod
    def _ok(out: str) -> bool:
        return "success" in out.lower() or "activated" in out.lower()


SHOWN = 8            # named networks listed, strongest first (a coffee shop shouldn't be a mile long)
LOOK_EVERY_MS = 2000  # re-read what NetworkManager knows (cheap: no scan)
SCAN_EVERY_S = 15     # ask for a fresh scan (Javier, 2026-10-25: switched on, it "said no connections", and
                      # only showed it connected after closing and opening it again — it looked once, too early)


def picture(state: dict) -> tuple:
    """What the page shows, in a form that compares: rebuilt only when it changes (no flicker every 2 s)."""
    return (state["on"], tuple((c["name"], c["sub"]) for c in state["cables"]),
            tuple((n["ssid"], n["now"], bool(n["security"]), n["signal"] // 25) for n in state["nets"]), state["note"])


def wifi_page(run, back, close, refresh) -> Gtk.Box:
    wifi = Wifi(run)
    page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    state = {"on": wifi.on(), "cables": [], "nets": [], "note": "", "shown": None, "busy": False, "starting": False}

    def later(fn, then):
        """fn in the background (connecting takes seconds), then `then(result)` back in the pop-up."""
        threading.Thread(target=lambda: GLib.idle_add(lambda r=fn(): (then(r), False)[1]), daemon=True).start()

    def switched(want):
        state["starting"] = bool(want)
        state["note"] = "Starting Wi-Fi…" if want else ""
        later(lambda: wifi.switch(want), lambda _r: (refresh(), look(), later(wifi.rescan, lambda _r: look()) if want else None))

    again = Gtk.Button.new_from_icon_name(mono("view-refresh-symbolic"), Gtk.IconSize.BUTTON)
    again.get_style_context().add_class("flat")
    again.set_tooltip_text("Look for networks again")
    again.connect("clicked", lambda _b: (state.update(note="Looking for networks…"), draw(force=True),
                                         later(wifi.rescan, lambda _r: (state.update(note=""), look()))))
    page.pack_start(head("Wi-Fi", back, state["on"] if state["on"] is not None else None, switched,
                         extra=[again] if state["on"] is not None else []), False, False, 0)
    page.pack_start(body, False, False, 0)

    def look():
        """Read NetworkManager again; redraw only what changed, never while a password box is open."""
        state["on"], state["cables"] = wifi.on(), wifi.cables()
        state["nets"] = wifi.networks() if state["on"] else []
        if state["starting"] and (state["nets"] or not state["on"]):
            state["starting"] = False
            if state["note"] == "Starting Wi-Fi…":
                state["note"] = ""
        if not state["busy"]:
            draw()
        return True                                  # the timer keeps going

    def draw(force=False):
        pic = picture(state)
        if pic == state["shown"] and not force:
            return
        state["shown"] = pic
        for child in body.get_children():
            body.remove(child)
        if state["cables"]:
            body.pack_start(section("Cable"), False, False, 0)
            body.pack_start(rows([{"icon": "network-wired-symbolic", "name": c["name"], "sub": c["sub"], "on": c["now"]}
                                  for c in state["cables"]]), False, False, 0)
        body.pack_start(section("Wi-Fi networks"), False, False, 0)
        if state["on"] is False:
            body.pack_start(status("Wi-Fi is off."), False, False, 0)
        else:
            if state["nets"]:
                body.pack_start(network_rows(state["nets"][:SHOWN]), False, False, 0)
            elif not state["note"]:
                body.pack_start(status("No networks found."), False, False, 0)
        if state["note"]:
            body.pack_start(status(state["note"]), False, False, 0)
        body.show_all()

    def network_rows(nets) -> Gtk.ListBox:
        lb = Gtk.ListBox()
        lb.get_style_context().add_class("hf-page-rows")
        lb.set_selection_mode(Gtk.SelectionMode.NONE)
        lb.set_activate_on_single_click(True)
        for n in nets + [{"ssid": "", "hidden": True}]:
            r = Gtk.ListBoxRow()
            r.net = n
            v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            line = Gtk.Box(spacing=10)
            words = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            words.set_valign(Gtk.Align.CENTER)
            if n.get("hidden"):
                line.pack_start(Gtk.Image.new_from_icon_name(mono("network-wireless-symbolic"), Gtk.IconSize.LARGE_TOOLBAR), False, False, 0)
                words.pack_start(Gtk.Label(label="Hidden network…", xalign=0), False, False, 0)
                sub = Gtk.Label(label="one that doesn't show its name", xalign=0)
                sub.get_style_context().add_class("hf-row-sub")
            else:
                line.pack_start(Gtk.Image.new_from_icon_name(mono(signal_icon(n["signal"])), Gtk.IconSize.LARGE_TOOLBAR), False, False, 0)
                words.pack_start(Gtk.Label(label=n["ssid"], xalign=0, ellipsize=Pango.EllipsizeMode.END, max_width_chars=30), False, False, 0)
                secured = "secured" if n["security"] else "open · not secured"
                sub = Gtk.Label(label=f"Connected · {secured}" if n["now"] else secured.capitalize(), xalign=0)
                sub.get_style_context().add_class("hf-row-on" if n["now"] else "hf-row-sub")
            words.pack_start(sub, False, False, 0)
            line.pack_start(words, True, True, 0)
            if n.get("now"):
                b = Gtk.Button(label="Disconnect")
                b.set_valign(Gtk.Align.CENTER)
                b.connect("clicked", lambda _b, s=n["ssid"]: (state.update(note=""), later(lambda: wifi.disconnect(s),
                                                                                              lambda _r: (look(), refresh()))))
                line.pack_end(b, False, False, 0)
            v.pack_start(line, False, False, 0)
            r.add(v)
            r.box, r.sub = v, sub
            lb.add(r)
        lb.connect("row-activated", lambda _lb, r: picked(r))
        return lb

    def picked(r):
        n = r.net
        if n.get("now") or getattr(r, "asking", False):
            return
        if n.get("hidden"):
            ask(r, name=True)
        elif n["security"] and n["ssid"] not in wifi.saved():
            ask(r)
        else:
            go(r, n["ssid"], n["security"], None)

    def ask(r, name=False):
        """A password box (and a name box for a hidden network) under the row clicked, Connect and Cancel."""
        r.asking = state["busy"] = True
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        named = Gtk.Entry()
        named.set_placeholder_text("Network name")
        if name:
            box.pack_start(named, False, False, 0)
        line = Gtk.Box(spacing=8)
        entry = Gtk.Entry()
        entry.set_visibility(False)
        entry.set_placeholder_text("Password" + (" (none for an open one)" if name else ""))
        connect = Gtk.Button(label="Connect")
        connect.get_style_context().add_class("on")
        cancel = Gtk.Button(label="Cancel")
        cancel.get_style_context().add_class("flat")
        line.pack_start(entry, True, True, 0)
        line.pack_start(connect, False, False, 0)
        line.pack_start(cancel, False, False, 0)
        box.pack_start(line, False, False, 0)
        r.box.pack_start(box, False, False, 0)
        r.box.show_all()
        (named if name else entry).grab_focus()

        def send(*_):
            ssid = named.get_text().strip() if name else r.net["ssid"]
            if ssid:
                go(r, ssid, r.net.get("security", ""), entry.get_text() or None, hidden=name)
        for w in (entry, named):
            w.connect("activate", send)
        connect.connect("clicked", send)
        cancel.connect("clicked", lambda _b: (state.update(busy=False), draw(force=True)))

    def go(r, ssid, security, password, hidden=False):
        r.sub.set_text("Connecting…")
        state["busy"], state["note"] = True, ""

        def done(ok):
            state["busy"] = False
            if not ok:
                state["note"] = f"Couldn't connect to {ssid}" + (": check the password." if password else ".")
            look()
            draw(force=True)
            refresh()
        later(lambda: wifi.connect(ssid, security, password, hidden=hidden), done)

    look()
    if state["on"]:                             # a fresh look straight away, then every SCAN_EVERY_S
        later(wifi.rescan, lambda _r: look())
    timers = [GLib.timeout_add(LOOK_EVERY_MS, look),
              GLib.timeout_add_seconds(SCAN_EVERY_S, lambda: (later(wifi.rescan, lambda _r: look()) if state["on"] else None, True)[1])]
    page.connect("destroy", lambda *_: [GLib.source_remove(t) for t in timers])
    page.pack_start(foot("networkForge (nmtui until it exists)", lambda: (close(), panelkit.run_command("hypeforge-nmtui"))),
                    False, False, 0)
    return page


# ---- Bluetooth (BlueZ) --------------------------------------------------------------------------

BT_ICONS = {"audio-headset": "audio-headphones-symbolic", "audio-headphones": "audio-headphones-symbolic",
            "audio-card": "audio-speakers-symbolic", "input-gaming": "input-gaming-symbolic",
            "input-keyboard": "input-keyboard-symbolic", "input-mouse": "input-mouse-symbolic",
            "input-tablet": "input-tablet-symbolic", "phone": "phone-symbolic", "computer": "computer-symbolic"}
BLUETUI = "alacritty --class hf-bluetooth -o window.dimensions.columns=110 -o window.dimensions.lines=30 -e bluetui"


def parse_bt_info(text: str) -> dict:
    """`bluetoothctl info <address>` → connected, icon, battery (None when the device doesn't tell)."""
    info = {"connected": False, "icon": "", "battery": None}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Connected:"):
            info["connected"] = line.split(":", 1)[1].strip() == "yes"
        elif line.startswith("Icon:"):
            info["icon"] = line.split(":", 1)[1].strip()
        elif line.startswith("Battery Percentage:"):
            m = re.search(r"\((\d+)\)", line)
            info["battery"] = int(m.group(1)) if m else None
    return info


class Bluetooth:
    """What the page asks BlueZ, through `bluetoothctl` (the same as the tile). `run` is swapped in tests."""

    def __init__(self, run):
        self.run = run

    def on(self) -> bool | None:
        show = self.run(["bluetoothctl", "show"])
        return None if "Powered:" not in show else "Powered: yes" in show

    def switch(self, on: bool):
        self.run(["bluetoothctl", "power", "on" if on else "off"])

    def devices(self) -> list[dict]:
        """Your paired devices, the connected ones first, then by name."""
        out = []
        for line in self.run(["bluetoothctl", "devices", "Paired"]).splitlines():
            parts = line.split(" ", 2)
            if len(parts) == 3 and parts[0] == "Device":
                d = {"address": parts[1], "name": parts[2], **parse_bt_info(self.run(["bluetoothctl", "info", parts[1]]))}
                out.append(d)
        return sorted(out, key=lambda d: (not d["connected"], d["name"].lower()))

    def connect(self, address: str) -> bool:
        return "successful" in self.run(["bluetoothctl", "connect", address], timeout=20).lower()

    def disconnect(self, address: str) -> bool:
        return "successful" in self.run(["bluetoothctl", "disconnect", address], timeout=10).lower()


def bt_picture(state: dict) -> tuple:
    return (state["on"], tuple((d["address"], d["name"], d["connected"], d["battery"]) for d in state["devices"]),
            state["note"], tuple(sorted(state["working"])))


def bluetooth_page(run, back, close, refresh) -> Gtk.Box:
    bt = Bluetooth(run)
    page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    state = {"on": bt.on(), "devices": [], "note": "", "shown": None, "working": set()}

    def later(fn, then):
        threading.Thread(target=lambda: GLib.idle_add(lambda r=fn(): (then(r), False)[1]), daemon=True).start()

    def switched(want):
        later(lambda: bt.switch(want), lambda _r: (refresh(), look()))

    page.pack_start(head("Bluetooth", back, state["on"] if state["on"] is not None else None, switched), False, False, 0)
    page.pack_start(body, False, False, 0)

    def look():
        state["on"] = bt.on()
        state["devices"] = bt.devices() if state["on"] else []
        draw()
        return True

    def act(d, connect):
        state["working"].add(d["address"])
        state["note"] = ""
        draw()

        def done(ok):
            state["working"].discard(d["address"])
            if not ok:
                state["note"] = f"Couldn't {'connect' if connect else 'disconnect'} {d['name']}" + \
                                (": is it on, and close by?" if connect else ".")
            look()
            refresh()
        later(lambda: bt.connect(d["address"]) if connect else bt.disconnect(d["address"]), done)

    def draw(force=False):
        pic = bt_picture(state)
        if pic == state["shown"] and not force:
            return
        state["shown"] = pic
        for child in body.get_children():
            body.remove(child)
        if state["on"] is None:
            body.pack_start(status("No Bluetooth on this computer."), False, False, 0)
        elif state["on"] is False:
            body.pack_start(status("Bluetooth is off."), False, False, 0)
        else:
            body.pack_start(section("Your devices"), False, False, 0)
            items = []
            for d in state["devices"]:
                busy = d["address"] in state["working"]
                sub = ("Connecting…" if not d["connected"] else "Disconnecting…") if busy else \
                      (f"Connected · battery {d['battery']} %" if d["battery"] is not None else "Connected") if d["connected"] \
                      else "Not connected"
                items.append({"icon": BT_ICONS.get(d["icon"], "bluetooth-symbolic"), "name": d["name"], "sub": sub,
                              "on": d["connected"] and not busy,
                              "button": None if busy else ("Disconnect" if d["connected"] else "Connect",
                                                           lambda d=d: act(d, not d["connected"]))})
            items.append({"icon": "list-add-symbolic", "name": "Pair a new device…",
                          "sub": "in the Bluetooth app", "picked": lambda: (close(), panelkit.run_command(BLUETUI))})
            if not state["devices"]:
                body.pack_start(status("No devices yet: pair one first."), False, False, 0)
            body.pack_start(rows(items), False, False, 0)
        if state["note"]:
            body.pack_start(status(state["note"]), False, False, 0)
        body.show_all()

    look()
    timer = GLib.timeout_add(3000, look)          # a device connecting by itself shows up without reopening
    page.connect("destroy", lambda *_: GLib.source_remove(timer))
    page.pack_start(foot("bluetoothForge (bluetui until it exists)", lambda: (close(), panelkit.run_command(BLUETUI))),
                    False, False, 0)
    return page


# ---- Printer (CUPS, through the printer applet) -------------------------------------------------

PRINT_SETTINGS = "system-config-printer"


def printer_applet():
    """The printer applet (applets/printers/): its CUPS readings — one place for how printers are asked about."""
    import importlib.machinery
    import importlib.util
    path = panelkit.APPLETS / "printers/hypeforge-printers"
    try:
        loader = importlib.machinery.SourceFileLoader("hypeforge_printers", str(path))
        spec = importlib.util.spec_from_loader("hypeforge_printers", loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        return mod
    except Exception:
        return None


def printer_words(printers: list, jobs: list) -> tuple[bool, str]:
    """The tile: lit while something prints or waits; what it says."""
    if not printers:
        return False, "none set up"
    if jobs:
        return True, f"{len(jobs)} job{'s' if len(jobs) != 1 else ''} waiting"
    stopped = [n for n, st in printers if st == "stopped"]
    if stopped:
        return False, f"{stopped[0]} · stopped"
    name, state = printers[0]
    return any(st == "printing" for _, st in printers), f"{name} · {state}" if len(printers) == 1 else f"{len(printers)} printers"


def printer_page(back, close, applet=None) -> Gtk.Box:
    app = applet or printer_applet()
    page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    page.pack_start(head("Printer", back), False, False, 0)
    page.pack_start(body, False, False, 0)
    state = {"shown": None, "note": ""}

    def cancel(jid):
        r = subprocess.run(["cancel", jid], capture_output=True, text=True) if app else None
        state["note"] = "" if r is None or r.returncode == 0 else f"Couldn't cancel {jid}."
        look()

    def look():
        ps, js = (app.printers(), app.jobs()) if app else ([], [])
        pic = (tuple(ps), tuple(js), state["note"])
        if pic == state["shown"]:
            return True
        state["shown"] = pic
        for child in body.get_children():
            body.remove(child)
        if not ps:
            body.pack_start(status("No printer set up yet: Print Settings adds one."), False, False, 0)
        else:
            body.pack_start(section("Printers"), False, False, 0)
            body.pack_start(rows([{"icon": "printer-symbolic", "name": n, "sub": st.capitalize(),
                                   "on": st == "printing"} for n, st in ps]), False, False, 0)
            body.pack_start(section("Waiting to print"), False, False, 0)
            if js:
                body.pack_start(rows([{"icon": "document-print-symbolic", "name": jid,
                                       "sub": f"{user} · {size} bytes" if size else user,
                                       "button": ("Cancel", lambda jid=jid: cancel(jid))} for jid, _p, user, size in js]),
                                False, False, 0)
            else:
                body.pack_start(status("Nothing waiting to print."), False, False, 0)
        if state["note"]:
            body.pack_start(status(state["note"]), False, False, 0)
        body.show_all()
        return True

    look()
    timer = GLib.timeout_add(3000, look)          # a job finishing disappears by itself
    page.connect("destroy", lambda *_: GLib.source_remove(timer))
    page.pack_start(foot("Print Settings (printerForge one day)", lambda: (close(), panelkit.run_command(PRINT_SETTINGS))),
                    False, False, 0)
    return page
