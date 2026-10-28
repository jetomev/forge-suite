"""The pop-up panels' core (look program step 4), without opening any window: the look of every
style × theme, one panel per view (a second press closes it), the power panel's asking rule."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/panels"))
sys.path.insert(0, str(HERE / "applets/panels/views"))
import panelkit  # noqa: E402
import power  # noqa: E402
import start  # noqa: E402
import quick  # noqa: E402
import qspages  # noqa: E402
import calendar_view as hfcalendar  # noqa: E402
import workspaces as wsview  # noqa: E402


class Look(unittest.TestCase):
    def test_every_style_with_every_theme_gives_a_whole_look(self):
        ht = panelkit.theme_tool()
        for style in ht.styles():
            for theme in ht.themes():
                look = panelkit.Look(style, theme)
                self.assertEqual(set(look.colour), set(panelkit.Look.ROLES))
                for role, value in look.colour.items():
                    self.assertRegex(value, r"^#[0-9a-f]{6}$", f"{style}/{theme}: {role}")
                self.assertIsInstance(look.radius, int)
                css = look.css()
                self.assertIn(look.colour["panel_bg"], css)

    def looks(self, corners):
        """Every style's Look with the corners switch on `corners` (not the person's own state)."""
        from unittest import mock
        ht = panelkit.theme_tool()                   # Look loads a fresh copy each time: hand it this one
        asked = []
        with mock.patch.object(ht.Place, "read_state", lambda self: asked.append(1) or {"corners": corners}), \
             mock.patch.object(panelkit, "theme_tool", lambda: ht):
            looks = {slug: panelkit.Look(slug, "kognogos-mocha") for slug in ht.styles()}
        self.assertEqual(len(asked), len(looks))     # the setup took effect: never the person's own switch
        return looks

    def test_one_pop_up_standard_on_every_style(self):
        # D-116 (Javier, 2026-10-20): the Rice was 14 px JetBrains Mono, Mac OS 9 square — now one standard
        for corners in ("style", "rounded"):
            looks = self.looks(corners)
            self.assertGreater(len(looks), 5)
            shapes = {(lk.font, lk.size, lk.border, lk.radius) for lk in looks.values()}
            self.assertEqual(shapes, {("Noto Sans", 10.5, 1, 10)}, corners)

    def test_pop_ups_follow_the_corners_switch(self):
        self.assertEqual({lk.radius for lk in self.looks("straight").values()}, {0})


class TitleRow(unittest.TestCase):
    """D-116 (Javier, 2026-10-20): "the same bold title row" on every pop-up, the tray menu's. Seven views
    drew their titles four ways (1.1x, 1.25x, 1.35x, none: Quick Settings); now one set of panel-kit
    classes and one soft line. The launchers (start, kickoff, library) are each style's own, outside it."""

    VIEWS = HERE / "applets/panels/views"
    TITLED = ["quick", "clipboard", "calendar_view", "system", "windowmenu", "traymenu", "listcard",
              "power", "workspaces", "switcher"]          # Javier, 2026-10-24: "give all popups their title"
    # their head is a card of its own above the others: the card's edge does the line's job (whether they
    # become one card, as D-116 says, is for Javier's pop-up review)
    OWN_CARD = {"clipboard", "calendar_view"}
    OLD = ["hf-one-title", "hf-wm-title", "hf-tm-name", "hf-list-name", "hf-clip-glyph",
           '"hf-title"']

    def test_the_kit_draws_the_one_title_row(self):
        css = panelkit.Look("rice", "kognogos-mocha").css()
        for cls in (".hf-head ", ".hf-head-name", ".hf-head-glyph", ".hf-head-sub", ".hf-head-line"):
            self.assertIn(cls, css)
        self.assertIn(f"font-size: {panelkit.Look.SIZE * 1.1}pt", css.split(".hf-head-name")[1].split("}")[0])
        self.assertTrue(callable(getattr(panelkit, "head_line", None)), "one shared soft line under the head")
        self.assertTrue(callable(getattr(panelkit, "titled", None)), "one shared way to put the title row on top")

    def test_every_titled_pop_up_wears_it(self):
        for view in self.TITLED:
            src = (self.VIEWS / f"{view}.py").read_text()
            shared = "panelkit.titled(" in src                   # the kit's title row and line, whole
            self.assertTrue(shared or "hf-head-name" in src, f"{view} has no title row")
            if view not in self.OWN_CARD:
                self.assertTrue(shared or "panelkit.head_line(" in src, f"{view} has no soft line under its head")
            for old in self.OLD:
                self.assertFalse(old in src, f"{view} still draws its own title ({old})")


class Widths(unittest.TestCase):
    """D-116: three widths only (Javier, 2026-10-24: "300 · 380 · 460"). Workspaces and the window switcher
    grow with their tiles and Power has no card (his call the same day); the launchers are each style's own."""

    VIEWS = HERE / "applets/panels/views"
    SIZED = ["quick", "clipboard", "calendar_view", "system", "windowmenu", "traymenu", "listcard"]

    def test_the_kit_has_the_three(self):
        self.assertEqual((panelkit.NARROW, panelkit.MEDIUM, panelkit.WIDE), (300, 380, 460))

    def test_no_pop_up_picks_its_own_width(self):
        # the width is the card's VISIBLE width, applied by the Panel to its outermost piece: set inside a
        # card's padding (most views) or on a stack of cards (Calendar, Clipboard) the same number showed
        # 30 px apart (measured on the photos, 2026-10-24)
        import re
        for view in self.SIZED:
            src = (self.VIEWS / f"{view}.py").read_text()
            self.assertTrue(re.search(r"width=(panelkit\.)?(NARROW|MEDIUM|WIDE|WIDTH)\b", src), f"{view} hands the Panel no width")
            own = re.findall(r"min-width: (?:\d{3}|\{\w+\})px|set_size_request\((?:\d{3}|WIDTH|panelkit\.\w+)", src)
            self.assertEqual(own, [], f"{view} still sets its own width: {own}")

    def test_the_content_fills_the_width(self):
        # 2026-10-24, Javier: "the content has been shrunk, and looks pushed to the left". The card had the
        # width; what was inside kept its own smaller size. Measured here off screen, nothing shown.
        from gi.repository import Gtk
        for card in (True, False):
            label = Gtk.Label(label="Night light")
            outer = panelkit.wrap(label, card=card, width=panelkit.NARROW)
            win = Gtk.OffscreenWindow()
            win.add(outer)
            win.show_all()
            while Gtk.events_pending():
                Gtk.main_iteration()
            self.assertGreaterEqual(label.get_allocated_width(), panelkit.NARROW - 40,
                                    f"card={card}: the content is {label.get_allocated_width()} px in a {panelkit.NARROW} px pop-up")
            win.destroy()

    def test_the_notifications_share_the_standard(self):
        # the theme tool writes mako's settings from its POPUP; the panel kit draws the pop-ups: one standard
        ht = panelkit.theme_tool()
        L = panelkit.Look
        self.assertEqual((ht.POPUP["font"], ht.POPUP["size"], ht.POPUP["border"], ht.POPUP["radius"]),
                         (L.FONT, L.SIZE, L.BORDER, L.RADIUS))
        self.assertEqual((ht.POPUP["narrow"], ht.POPUP["medium"], ht.POPUP["wide"]),
                         (panelkit.NARROW, panelkit.MEDIUM, panelkit.WIDE))

    def test_the_panel_puts_it_on_the_outermost_piece(self):
        import inspect
        self.assertIn("width", inspect.signature(panelkit.Panel.__init__).parameters)


class HoverTip(unittest.TestCase):
    """2026-10-24: the bar's hover tip stayed up over an open pop-up. Sway looks at what is under the mouse only
    when it moves; the pop-up's backdrop lands over the bar under a still mouse, so the bar never heard it leave."""

    def setUp(self):
        sys.path.insert(0, str(HERE / "applets/common"))
        import hfbackdrop
        self.hb = hfbackdrop

    def test_the_nudge_is_a_move_of_zero(self):
        from unittest import mock
        with mock.patch.dict(os.environ, {"SWAYSOCK": "/nowhere"}), mock.patch.object(self.hb.subprocess, "Popen") as run:
            self.assertFalse(self.hb._nudge(), "once, not again and again")
        cmd = run.call_args[0][0]
        self.assertEqual(cmd[0], "swaymsg")
        self.assertEqual(cmd[-5:], ["seat", "-", "cursor", "move", "0", "0"][-5:])
        self.assertIn("-", cmd)

    def test_no_sway_no_nudge(self):
        from unittest import mock
        env = {k: v for k, v in os.environ.items() if k != "SWAYSOCK"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(self.hb.subprocess, "Popen") as run:
            self.hb._nudge()
        run.assert_not_called()

    def test_a_backdrop_showing_nudges(self):
        from unittest import mock
        if not os.environ.get("WAYLAND_DISPLAY"):
            self.skipTest("the backdrops are layer surfaces: they need a Wayland screen")
        from gi.repository import Gdk
        with mock.patch.object(self.hb, "_nudge") as nudge, \
                mock.patch.object(self.hb.GLib, "timeout_add", side_effect=lambda _ms, f: f()):
            wins = self.hb.backdrops(lambda: None)
            wins[0].emit("map-event", Gdk.Event.new(Gdk.EventType.MAP))
            for w in wins:
                w.destroy()
        nudge.assert_called_once()


class TemperatureList(unittest.TestCase):
    def test_every_sensor_shows_without_scrolling(self):
        # 2026-10-24: one column at WIDE, the sensors in a scrolling list (D-116). The pop-up took the list's
        # smallest height, one row: Processor only, the drives, the board and the fans hidden below it.
        from unittest import mock
        from gi.repository import Gtk
        import system as sysview
        temps = [{"group": g, "name": f"{g} {i}", "temp": 40.0, "hot": 90.0, "state": "ok"}
                 for g in ("Processor", "Graphics", "Drives", "Board") for i in range(3)]
        state = {"temps": temps, "fans": [{"name": "Case fan 1", "rpm": 1100}],
                 "history": {"cpu_temp": [40.0], "gpu_temp": [40.0]}}
        with mock.patch.object(sysview.hfsys, "read_state", return_value=state), \
                mock.patch.object(sysview.hfsys, "fresh", return_value=True):
            view = sysview.View(panelkit.Look("kde", "dark-blue"), "temp", lambda: None)
            win = Gtk.OffscreenWindow()
            win.add(panelkit.wrap(view.root, width=panelkit.WIDE))
            win.show_all()
            for _ in range(20):                      # a window takes a new size on its next drawing tick
                while Gtk.events_pending():
                    Gtk.main_iteration()
                time.sleep(0.02)
        scroller = next(w for w in walk(view.root) if isinstance(w, Gtk.ScrolledWindow))
        whole = scroller.get_child().get_preferred_height()[1]
        self.assertGreater(whole, 200, "the setup: twelve sensors and a fan")
        self.assertGreaterEqual(scroller.get_allocated_height(), min(whole, sysview.sensor_room()) - 2,
                                f"the list shows {scroller.get_allocated_height()} of its {whole} px")
        win.destroy()


def walk(widget):
    yield widget
    if hasattr(widget, "get_children"):
        for c in widget.get_children():
            yield from walk(c)


WPCTL = """PipeWire 'pipewire-0' [1.4.9, jetomev@tphome-linux, cookie:1]
 └─ Clients:
        33. pipewire                            [1.4.9, jetomev@tphome-linux, pid:1]

Audio
 ├─ Devices:
 │      44. Ryzen HD Audio Controller           [alsa]
 │      46. SteelSeries Arctis 5                [alsa]
 │  
 ├─ Sinks:
 │      55. SteelSeries Arctis 5 Game           [vol: 0.36]
 │      65. SteelSeries Arctis 5 Chat           [vol: 0.50]
 │      67. GA106 High Definition Audio Controller Digital Stereo (HDMI) [Sceptre Y27] [vol: 0.55]
 │  *   82. Ryzen HD Audio Controller Analog Stereo [vol: 0.40]
 │  
 ├─ Sources:
 │  *   56. SteelSeries Arctis 5 Chat           [vol: 0.94]
 │      63. C920 PRO HD Webcam Analog Stereo    [vol: 0.47]
 │  
 ├─ Filters:
 │  
 └─ Streams:

Video
 ├─ Devices:
 │      77. C920 PRO HD Webcam                  [v4l2]
 ├─ Sources:
 │  *   90. C920 PRO HD Webcam (V4L2)
"""


class QuickSettingsPages(unittest.TestCase):
    """D-117 (Javier, 2026-10-25): a tile's › opens its page inside Quick Settings; ‹ or Esc goes back."""

    def test_sound_reads_this_computers_outputs_and_inputs(self):
        d = qspages.parse_wpctl(WPCTL)
        self.assertEqual([x["name"] for x in d["Sinks"]], ["SteelSeries Arctis 5 Game", "SteelSeries Arctis 5 Chat",
                         "GA106 High Definition Audio Controller Digital Stereo (HDMI) [Sceptre Y27]",
                         "Ryzen HD Audio Controller Analog Stereo"])
        self.assertEqual([x["id"] for x in d["Sinks"] if x["now"]], ["82"], "the one in use")
        self.assertEqual([x["name"] for x in d["Sources"]], ["SteelSeries Arctis 5 Chat", "C920 PRO HD Webcam Analog Stereo"],
                         "audio only: the webcam's video source is not a microphone")
        self.assertEqual([x["id"] for x in d["Sources"] if x["now"]], ["56"])

    def test_nothing_to_read_is_empty_not_a_crash(self):
        self.assertEqual(qspages.parse_wpctl(""), {"Sinks": [], "Sources": []})

    def test_each_device_gets_an_icon_that_says_what_it_is(self):
        self.assertEqual(qspages.sound_icon("SteelSeries Arctis 5 Game", False), "audio-headphones")
        self.assertEqual(qspages.sound_icon("GA106 … Digital Stereo (HDMI) [Sceptre Y27]", False), "video-display")
        self.assertEqual(qspages.sound_icon("Ryzen HD Audio Controller Analog Stereo", False), "audio-speakers")
        self.assertEqual(qspages.sound_icon("C920 PRO HD Webcam Analog Stereo", True), "camera-web")
        self.assertEqual(qspages.sound_icon("SteelSeries Arctis 5 Chat", True), "audio-input-microphone")

    def test_esc_on_a_page_goes_back_before_it_closes(self):
        from gi.repository import Gdk
        closed = []

        class Fake:
            escape = None
            def close(self):
                closed.append(True)
        key = Gdk.Event.new(Gdk.EventType.KEY_PRESS)
        key.keyval = Gdk.KEY_Escape
        p = Fake()
        p.escape = lambda: True                         # a page was open: it went back
        self.assertTrue(panelkit.Panel._key(p, None, key))
        self.assertEqual(closed, [], "Esc on a page goes back to Quick Settings, it doesn't close")
        p.escape = lambda: False                        # already on Quick Settings
        panelkit.Panel._key(p, None, key)
        self.assertEqual(closed, [True])
        p.escape = None                                 # every other pop-up
        panelkit.Panel._key(p, None, key)
        self.assertEqual(closed, [True, True])

    def test_the_speaker_mutes_and_the_icon_opens_sound(self):
        # Javier, 2026-10-25: "clicking in the speaker should indeed mute the volume… add an icon next to the
        # volume % to the right to open the popup"
        ran, opened = [], []
        be = quick.Backend(lambda cmd, timeout=3.0: (ran.append(" ".join(cmd)), "Volume: 0.40")[1])
        row = quick.volume_row(be, 40, False, lambda: opened.append("sound"))
        row.mute.clicked()
        self.assertIn("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle", ran)
        self.assertEqual(opened, [], "the speaker mutes; it doesn't open the page")
        row.more.clicked()
        self.assertEqual(opened, ["sound"])
        kids = row.get_children()
        self.assertIs(kids[-1], row.more, "the icon sits right of the number")
        self.assertIsNone(quick.volume_row(be, 40, False).more, "the speaker's own pop-up has no icon to itself")

    def test_the_night_light_page_says_it_whole(self):
        night = quick.Night.__new__(quick.Night)
        night.ok = True

        class Settings:
            @staticmethod
            def load():
                return object()
        night.settings = type("S", (), {"Settings": Settings})
        for st, words in (({"state": "day", "why": "warm again from 18:45"}, "Daylight now · warm again from 18:45"),
                          ({"state": "warm", "why": "4000 K since 18:46 · daylight at 07:02"}, "4000 K since 18:46 · daylight at 07:02"),
                          ({"state": "day", "why": "Daylight Now, until you pick Automatic"}, "Daylight Now, until you pick Automatic")):
            night.control = type("C", (), {"status": staticmethod(lambda _s, st=st: st)})
            self.assertEqual(night.sentence(), words)


class WifiPage(unittest.TestCase):
    """D-117 (Javier, 2026-10-25): "how do you pick the wifi, connect or disconnect either wifi or cable"."""

    LIST = "*:Home-5G:88:WPA2\n :Cafe\\:Bar:61:WPA1 WPA2\n ::70:WPA2\n :Guest:40:\n :Home-5G:52:WPA2\n :Office:55:WPA3\n"

    def runner(self, answers, seen):
        def run(cmd, timeout=3.0):
            seen.append(list(cmd))
            if "passwd-file" in cmd:
                f = Path(cmd[cmd.index("passwd-file") + 1])
                seen.append(["FILE", f.read_text(), oct(f.stat().st_mode & 0o777), str(f)])
            for key, out in answers.items():
                if key in " ".join(cmd):
                    return out
            return ""
        return run

    def test_the_list_reads_like_a_person_wants_it(self):
        nets = qspages.parse_networks(self.LIST)
        self.assertEqual([n["ssid"] for n in nets], ["Home-5G", "Cafe:Bar", "Office", "Guest"],
                         "the connected one first, then strongest; one row per name; a ':' in a name kept; hidden left out")
        self.assertEqual(nets[0]["signal"], 88, "the connected one's own signal, not its weaker twin")
        self.assertTrue(nets[0]["now"])
        self.assertEqual(nets[-1]["security"], "", "an open network")

    def test_the_cable(self):
        c = qspages.parse_cables("enp5s0:ethernet:connected:Wired connection 1\neth1:ethernet:unavailable:\nwlan0:wifi:unavailable:\n")
        self.assertEqual([(x["name"], x["sub"], x["now"]) for x in c],
                         [("Wired connection 1", "Connected", True), ("Cable", "Cable unplugged", False)])

    def test_a_new_secured_network_never_puts_the_password_on_a_command_line(self):
        seen = []
        w = qspages.Wifi(self.runner({"connection show": "", "connection add": "successfully added",
                                      "connection up": "Connection successfully activated"}, seen))
        self.assertTrue(w.connect("Cafe:Bar", "WPA1 WPA2", "s3cret pass"))
        self.assertFalse(any("s3cret pass" in " ".join(c) for c in seen if c[0] != "FILE"), "the password on a command line")
        add = next(c for c in seen if c[:3] == ["nmcli", "connection", "add"])
        self.assertIn("wpa-psk", add)
        f = next(c for c in seen if c[0] == "FILE")
        self.assertEqual(f[1], "802-11-wireless-security.psk:s3cret pass\n")
        self.assertEqual(f[2], "0o600", "only this person can read it")
        self.assertFalse(Path(f[3]).exists(), "the file is gone afterwards")

    def test_a_wrong_password_takes_the_new_profile_away(self):
        seen = []
        w = qspages.Wifi(self.runner({"connection show": "", "connection add": "successfully added",
                                      "connection up": "Error: Connection activation failed: Secrets were required"}, seen))
        self.assertFalse(w.connect("Office", "WPA3", "wrong"))
        self.assertIn(["nmcli", "connection", "delete", "id", "Office"], seen, "so the next try asks again")
        self.assertIn("sae", next(c for c in seen if c[:3] == ["nmcli", "connection", "add"]), "WPA3 alone: SAE")
        self.assertFalse(Path(next(c for c in seen if c[0] == "FILE")[3]).exists())

    def test_saved_and_open_networks_connect_without_asking(self):
        seen = []
        w = qspages.Wifi(self.runner({"NAME,TYPE connection show": "Home-5G:802-11-wireless\n",
                                      "up id Home-5G": "Connection successfully activated",
                                      "wifi connect Guest": "Device 'wlan0' successfully activated"}, seen))
        self.assertTrue(w.connect("Home-5G", "WPA2"))
        self.assertIn(["nmcli", "connection", "up", "id", "Home-5G"], seen)
        self.assertTrue(w.connect("Guest", ""))
        self.assertIn(["nmcli", "dev", "wifi", "connect", "Guest"], seen)
        self.assertFalse(any(c[:3] == ["nmcli", "connection", "add"] for c in seen), "no new profile for those")

    def test_a_hidden_network_is_asked_for_by_name(self):
        seen = []
        w = qspages.Wifi(self.runner({"connection show": "", "connection add": "successfully added",
                                      "connection up": "Connection successfully activated"}, seen))
        self.assertTrue(w.connect("Backroom", "", "pw 1", hidden=True))
        add = next(c for c in seen if c[:3] == ["nmcli", "connection", "add"])
        self.assertEqual(add[add.index("802-11-wireless.hidden") + 1], "yes")
        self.assertIn("wpa-psk", add)
        self.assertFalse(any("pw 1" in " ".join(c) for c in seen if c[0] != "FILE"), "the password on a command line")
        seen.clear()
        self.assertTrue(w.connect("OpenBack", "", None, hidden=True))
        add = next(c for c in seen if c[:3] == ["nmcli", "connection", "add"])
        self.assertNotIn("wifi-sec.key-mgmt", add, "an open hidden network: no security")
        self.assertIn(["nmcli", "connection", "up", "id", "OpenBack"], seen)

    def test_it_redraws_only_when_something_changed(self):
        # Javier, 2026-10-25: switched on, it "said no connections" until closed and opened — now it looks every
        # 2 s, and redraws only when what it shows changed (no flicker)
        net = lambda signal, now=False: {"ssid": "TPHOME", "signal": signal, "security": "WPA2", "now": now}
        a = {"on": True, "cables": [], "nets": [net(55)], "note": ""}
        self.assertEqual(qspages.picture(a), qspages.picture(dict(a, nets=[net(60)])), "a small signal wobble: no redraw")
        self.assertNotEqual(qspages.picture(a), qspages.picture(dict(a, nets=[net(55, True)])), "connected: redraw")
        self.assertNotEqual(qspages.picture(a), qspages.picture(dict(a, nets=[])), "gone: redraw")
        self.assertEqual(qspages.LOOK_EVERY_MS, 2000)
        self.assertLessEqual(qspages.SCAN_EVERY_S, 20)
        self.assertGreaterEqual(qspages.SHOWN, 5, "Javier: 'at least the top five'")

    def test_the_tile_opens_the_page(self):
        self.assertEqual(quick.PAGES["Wi-Fi"], "wifi")
        self.assertEqual(qspages.ONLY_PAGE["network"], "wifi", "the bar's network pop-up is the page too")


class BluetoothPage(unittest.TestCase):
    """D-117 (Javier, 2026-10-25): "Same for bluetooth." Your devices, Connect / Disconnect, pair a new one."""

    def runner(self, answers, seen):
        def run(cmd, timeout=3.0):
            seen.append(list(cmd))
            return answers.get(" ".join(cmd[1:]), "")
        return run

    ANSWERS = {"show": "\tPowered: yes\n",
               "devices Paired": "Device AA:01 WH-1000XM4\nDevice AA:02 Xbox Wireless Controller\nDevice AA:03 a keyboard\n",
               "info AA:01": "\tIcon: audio-headset\n\tConnected: yes\n\tBattery Percentage: 0x50 (80)\n",
               "info AA:02": "\tIcon: input-gaming\n\tConnected: no\n",
               "info AA:03": "\tConnected: no\n",
               "connect AA:02": "Attempting to connect to AA:02\nConnection successful\n",
               "connect AA:03": "Failed to connect: org.bluez.Error.Failed\n",
               "disconnect AA:01": "Successful disconnected\n"}

    def test_your_devices_the_connected_first(self):
        bt = qspages.Bluetooth(self.runner(self.ANSWERS, []))
        d = bt.devices()
        self.assertEqual([x["name"] for x in d], ["WH-1000XM4", "a keyboard", "Xbox Wireless Controller"])
        self.assertEqual((d[0]["connected"], d[0]["battery"], d[0]["icon"]), (True, 80, "audio-headset"))
        self.assertIsNone(d[1]["battery"], "no battery said: none shown")

    def test_connect_and_disconnect_say_whether_they_worked(self):
        seen = []
        bt = qspages.Bluetooth(self.runner(self.ANSWERS, seen))
        self.assertTrue(bt.connect("AA:02"))
        self.assertFalse(bt.connect("AA:03"), "a failure is a failure, not a success")
        self.assertTrue(bt.disconnect("AA:01"))
        self.assertIn(["bluetoothctl", "connect", "AA:02"], seen)

    def test_off_and_missing(self):
        self.assertFalse(qspages.Bluetooth(self.runner({"show": "\tPowered: no\n"}, [])).on())
        self.assertIsNone(qspages.Bluetooth(self.runner({}, [])).on(), "no Bluetooth at all")

    def test_each_device_gets_its_icon(self):
        self.assertEqual(qspages.BT_ICONS["audio-headset"], "audio-headphones-symbolic")
        self.assertEqual(qspages.BT_ICONS["input-gaming"], "input-gaming-symbolic")

    def test_the_tile_opens_the_page(self):
        self.assertEqual(quick.PAGES["Bluetooth"], "bluetooth")
        self.assertEqual(qspages.ONLY_PAGE["bluetooth"], "bluetooth")


class PrinterInQuickSettings(unittest.TestCase):
    """Javier, 2026-10-25: "The 'Do not Disturb' option in the Quick Settings, we should move it to the
    Time/Date/Alerts combo… In the open space, let's move the Printer, so we can take out the solo printer icon"."""

    def test_the_tile_says_what_the_printer_is_doing(self):
        self.assertEqual(qspages.printer_words([], []), (False, "none set up"))
        self.assertEqual(qspages.printer_words([("HP_M15w", "idle")], []), (False, "HP_M15w · idle"))
        self.assertEqual(qspages.printer_words([("HP_M15w", "printing")], [("HP-7", "HP", "j", "100")]),
                         (True, "1 job waiting"))
        self.assertEqual(qspages.printer_words([("A", "idle"), ("B", "stopped")], []), (False, "B · stopped"))

    def test_printer_took_do_not_disturbs_place(self):
        import inspect
        src = inspect.getsource(quick.build)
        self.assertIn('("Printer"', src)
        self.assertNotIn('("Do Not Disturb"', src, "Do Not Disturb lives on the calendar's header now")
        self.assertEqual(quick.PAGES["Printer"], "printer")

    def test_do_not_disturb_is_on_the_calendar(self):
        import inspect
        self.assertIn("dnd_switch()", inspect.getsource(hfcalendar.build))
        self.assertIn('"dnd"', inspect.getsource(hfcalendar.dnd_switch), "through the bell, so the bell redraws")

    def test_no_bar_places_the_printer(self):
        import json, re
        for cfg in sorted((HERE / "styles").glob("*/bar/config.jsonc")) + [HERE / "sway/waybar/config.jsonc"]:
            text = "\n".join(l.split("//", 1)[0] for l in cfg.read_text().splitlines())
            placed = [m for m in re.findall(r'"custom/printers"\s*([,\]\n])', text)]
            self.assertEqual(placed, [], f"{cfg.parent.parent.name}: the printer is still on the bar")


class ViewNames(unittest.TestCase):
    def test_no_view_module_shadows_the_standard_library(self):
        # views/ goes first on the import path: a view called calendar.py would replace Python's own
        import sys as _sys
        names = {p.stem for p in (HERE / "applets/panels/views").glob("*.py")}
        self.assertFalse(names & set(_sys.stdlib_module_names), names & set(_sys.stdlib_module_names))


class OnePanelPerView(unittest.TestCase):
    def test_the_same_button_again_closes_the_open_panel(self):
        with tempfile.TemporaryDirectory() as d:
            old = panelkit.RUNTIME
            panelkit.RUNTIME = Path(d)
            try:
                self.assertFalse(panelkit.close_open("power"), "nothing open: open it")
                sleeper = subprocess.Popen(["sleep", "30"])
                panelkit.pidfile("power").write_text(str(sleeper.pid))
                self.assertTrue(panelkit.close_open("power"))
                self.assertEqual(sleeper.wait(5), -15, "the open one got the close request")
                panelkit.pidfile("power").write_text("999999")
                self.assertFalse(panelkit.close_open("power"), "a stale file means nothing is open")
            finally:
                panelkit.RUNTIME = old


class PowerAsks(unittest.TestCase):
    def setUp(self):
        self.a = power.Asking({key: confirm for key, _l, _i, confirm in power.ACTIONS})

    def test_lock_goes_at_once(self):
        self.assertEqual(self.a.press("lock"), "run")

    def test_restart_asks_then_runs(self):
        self.assertEqual(self.a.press("reboot"), "ask")
        self.assertEqual(self.a.press("reboot"), "run")

    def test_pressing_another_moves_the_question(self):
        self.assertEqual(self.a.press("reboot"), "ask")
        self.assertEqual(self.a.press("shutdown"), "ask", "Shut Down asks too; it doesn't inherit Restart's yes")
        self.assertEqual(self.a.press("shutdown"), "run")

    def test_the_commands_come_from_the_launchers_power_settings(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "sections.toml"
            f.write_text('[power]\nreboot = "systemctl reboot"\n')
            old = power.SECTIONS
            power.SECTIONS = f
            try:
                self.assertEqual(power.commands(), {"reboot": "systemctl reboot"})
            finally:
                power.SECTIONS = old


def entry(name, cats=()):
    return {"name": name, "icon": name.lower(), "exec": name.lower(), "terminal": False, "categories": set(cats), "wmclass": ""}


START_ENTRIES = {"google-chrome": entry("Google Chrome", ["Network"]), "steam": entry("Steam", ["Game"]),
                 "chromium": entry("Chromium", ["Network"]), "gimp": entry("GIMP", ["Graphics"])}


class StartPanel(unittest.TestCase):
    def test_search_finds_every_word_and_names_starting_with_it_first(self):
        self.assertEqual(start.matches(START_ENTRIES, "chrom"), ["chromium", "google-chrome"])
        self.assertEqual(start.matches(START_ENTRIES, "google chr"), ["google-chrome"])
        self.assertEqual(start.matches(START_ENTRIES, "steam"), ["steam"])
        more = dict(START_ENTRIES, helper=entry("A Steam Helper"))
        self.assertEqual(start.matches(more, "steam"), ["steam", "helper"],
                         "Steam (starts with it) before A Steam Helper, though A sorts first")
        self.assertEqual(start.matches(START_ENTRIES, "nothing-like-it"), [])

    def test_the_groups_are_the_launchers_own_with_favorites_first_and_all_apps_last(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "sections.toml"
            cfg.write_text('favourites = ["steam", "gone"]\nclaim_order = ["Games", "Internet"]\n'
                           '[[section]]\nname = "Games"\ncategories = ["Game"]\n'
                           '[[section]]\nname = "Internet"\ncategories = ["Network"]\n')
            real = start.panelkit_launcher
            def launcher():
                mod = real()
                mod.CONFIG = cfg
                return mod
            start.panelkit_launcher = launcher
            try:
                sets = start.groups(START_ENTRIES)
            finally:
                start.panelkit_launcher = real
        names = [n for n, _ in sets]
        self.assertEqual(names, ["Favorites", "Games", "Internet", "All apps"])
        self.assertEqual(dict(sets)["Favorites"], ["steam"], "a favourite that isn't installed is left out")
        self.assertEqual(len(dict(sets)["All apps"]), 4)


class FakeRun:
    """Answers commands from a table; records what was run."""
    def __init__(self, answers):
        self.answers, self.ran = answers, []

    def __call__(self, cmd, timeout=3.0):
        self.ran.append(cmd)
        return self.answers.get(" ".join(cmd), "")


class QuickSettings(unittest.TestCase):
    def test_each_slider_writes_its_own_number(self):
        # Javier, 2026-10-24: "If I move the volume, it is the night light indicator that moves" — both rows
        # named their label `value`, and the volume's handler found the night light's at run time
        moved = []
        volume, vol_label = quick.slider(0, 100, 1, 40, lambda v: f"{int(v)} %", moved.append)
        warmth, warm_label = quick.slider(3000, 5000, 500, 4000, lambda v: f"{int(v)} K", moved.append)
        volume.set_value(70)
        self.assertEqual(vol_label.get_text(), "70 %")
        self.assertEqual(warm_label.get_text(), "4000 K", "the volume wrote into the night light's number")
        self.assertEqual(moved, [70])

    def test_the_full_pop_up_has_no_warmth_slider(self):
        # Javier, 2026-10-24: "since we have a night light popup, we don't need the night light bar in the
        # quick settings popup"; the Night light tile stays, the slider lives on its page (D-117, 2026-10-25)
        self.assertEqual(quick.SLIDERS[None], ("volume",))
        self.assertNotIn("night", quick.SLIDERS)
        self.assertEqual(qspages.ONLY_PAGE, {"night": "night", "sound": "sound", "network": "wifi", "bluetooth": "bluetooth"}, "the bar's pop-ups open their pages")

    def test_wifi_off_on_a_cable_says_so(self):
        be = quick.Backend(FakeRun({"nmcli -t -f WIFI radio": "disabled\n",
                                    "nmcli -t -f DEVICE,TYPE,STATE dev": "enp5s0:ethernet:connected\nwlan0:wifi:unavailable\n"}))
        self.assertEqual(be.wifi(), (False, "off · wired"))

    def test_wifi_on_shows_the_network(self):
        be = quick.Backend(FakeRun({"nmcli -t -f WIFI radio": "enabled\n", "nmcli -t -f TYPE,NAME connection show --active": "802-3-ethernet:Wired 1\n802-11-wireless:tphome\n"}))
        self.assertEqual(be.wifi(), (True, "tphome"))
        self.assertFalse(any("wifi" in c and "dev" in c for c in map(" ".join, getattr(be.run, "ran", []))),
                         "never the Wi-Fi list: it scans first, seconds long (2026-10-17)")

    def test_a_missing_program_is_a_dash_not_a_crash(self):
        be = quick.Backend(FakeRun({}))
        self.assertEqual(be.wifi(), (None, "—"))
        self.assertEqual(be.bluetooth(), (None, "—"))
        self.assertEqual(be.volume(), (None, False))

    def test_bluetooth_names_the_connected_device(self):
        be = quick.Backend(FakeRun({"bluetoothctl show": "\tName: x\n\tPowered: yes\n",
                                    "bluetoothctl devices Connected": "Device AA:BB Logitech G13\n"}))
        self.assertEqual(be.bluetooth(), (True, "Logitech G13"))

    def test_the_switches_run_the_owning_programs(self):
        run = FakeRun({})
        be = quick.Backend(run)
        be.wifi_toggle(False)
        be.bluetooth_toggle(True)
        be.dnd_toggle(False)
        be.set_volume(37.6)
        self.assertIn(["nmcli", "radio", "wifi", "on"], run.ran)
        self.assertIn(["bluetoothctl", "power", "off"], run.ran)
        self.assertTrue(run.ran[2][0].endswith("hypeforge-notifications") and run.ran[2][1] == "dnd",
                        "Do Not Disturb through the bell, so the bell redraws")
        self.assertEqual(run.ran[3][-1], "37%")

    def test_the_night_lights_sentence_is_cut_to_fit_a_tile(self):
        self.assertEqual(quick.short("warm again from 18:59"), "from 18:59")
        self.assertEqual(quick.short("4500 K since 18:46 · daylight at 07:02"), "until 07:02")
        self.assertEqual(quick.short("Warm Now, 4500 K, until you pick Automatic"), "warm now")
        self.assertEqual(quick.short("switched off"), "off")

    def test_volume_and_mute(self):
        be = quick.Backend(FakeRun({"wpctl get-volume @DEFAULT_AUDIO_SINK@": "Volume: 0.52 [MUTED]\n"}))
        self.assertEqual(be.volume(), (52, True))

    def test_updates_from_the_snapshot_never_the_network(self):
        with tempfile.TemporaryDirectory() as d:
            old = quick.SNAPSHOT
            quick.SNAPSHOT = Path(d) / "updates.json"
            try:
                self.assertEqual(quick.Backend(FakeRun({})).updates(), "Updates: not checked yet")
                quick.SNAPSHOT.write_text('{"count": 212, "ready": []}')
                self.assertEqual(quick.Backend(FakeRun({})).updates(), "212 waiting their turn · nog")
                quick.SNAPSHOT.write_text('{"count": 212, "ready": [{"pkg": "a"}, {"pkg": "b"}]}')
                self.assertEqual(quick.Backend(FakeRun({})).updates(), "2 updates ready · nog")
            finally:
                quick.SNAPSHOT = old


class CalendarPanel(unittest.TestCase):
    def test_clear_all_hides_what_was_shown_but_not_what_comes_after(self):
        notes = [{"id": "3"}, {"id": "7"}, {"id": "5"}]
        with tempfile.TemporaryDirectory() as d:
            old = hfcalendar.CLEARED
            hfcalendar.CLEARED = Path(d) / "cleared"
            try:
                self.assertEqual([n["id"] for n in hfcalendar.visible(notes)], ["7", "5", "3"], "newest first")
                hfcalendar.CLEARED.write_text("5")
                self.assertEqual([n["id"] for n in hfcalendar.visible(notes)], ["7"])
            finally:
                hfcalendar.CLEARED = old

    def test_a_notification_borrows_its_apps_icon(self):
        entries = {"steam": {"name": "Steam", "icon": "steam"}}
        self.assertEqual(hfcalendar.icon_for({"app_name": "Steam", "app_icon": "None"}, entries), "steam")
        # nog has no app entry of its own: its Forge app's icon since 2026-10-27 (the Rice review, fix 3)
        self.assertEqual(hfcalendar.icon_for({"app_name": "nog", "app_icon": "None"}, entries), "system-software-install")
        self.assertEqual(hfcalendar.icon_for({"app_name": "x", "app_icon": "mail-unread"}, entries), "mail-unread")

    def test_makos_none_is_nothing(self):
        self.assertEqual(hfcalendar.plain("None"), "")
        self.assertEqual(hfcalendar.plain(None), "")
        self.assertEqual(hfcalendar.plain("Hi"), "Hi")


class WorkspacesStrip(unittest.TestCase):
    def test_sway_names_map_to_our_workspaces_on_every_screen(self):
        self.assertEqual(wsview.index_of("4:Gaming", 6), 4)
        self.assertEqual(wsview.index_of("14:Gaming", 6), 4, "the second screen adds 10")
        self.assertEqual(wsview.index_of("24:Gaming", 6), 4)
        self.assertIsNone(wsview.index_of("101:Shared", 6), "a shared space is no single workspace")
        self.assertIsNone(wsview.index_of("9:Extra", 6))
        self.assertIsNone(wsview.index_of("scratch", 6))

    def test_apps_are_counted_once_per_workspace_across_screens(self):
        from hfapps import Matcher
        entries = {"steam": {"name": "Steam", "icon": "steam", "exec": "steam %U", "terminal": False,
                             "categories": set(), "wmclass": ""}}
        win = lambda i, a: {"id": i, "pid": i, "type": "con", "app_id": a, "nodes": [], "floating_nodes": []}
        tree = {"nodes": [{"nodes": [{"name": "4:Gaming", "nodes": [win(1, "steam")], "floating_nodes": []}]},
                          {"nodes": [{"name": "14:Gaming", "nodes": [win(2, "steam"), win(3, "mystery")], "floating_nodes": []}]}]}
        per = wsview.apps_per_workspace(tree, entries, Matcher(entries), 6)
        self.assertEqual(per[4], ["steam", "mystery"], "two Steam windows on two screens: one app")
        self.assertEqual(per[1], [])


class CosmicPopups(unittest.TestCase):
    """The small pop-ups (COSMIC's C-5, D-77) and, since D-96 (Javier, 2026-10-13), the three pieces every
    style shares the same way: the status pill → Quick Settings, the date-time-bell piece → the calendar
    with the alerts, the moon → the night light's part. Defined once, in modules.jsonc."""

    def shared(self):
        import json
        loader = __import__("importlib.machinery").machinery.SourceFileLoader("hfbar_c", str(HERE / "applets/bar/hypeforge-bar"))
        bar = __import__("importlib.util").util.module_from_spec(__import__("importlib.util").util.spec_from_loader("hfbar_c", loader))
        loader.exec_module(bar)
        return json.loads(bar.strip_comments((HERE / "sway/waybar/modules.jsonc").read_text()))

    def test_the_status_pill_opens_quick_settings_from_any_of_its_icons(self):
        """Javier, 2026-10-13: Windows 11's bundle "for all themes": audio, network and Bluetooth in one
        control, with the big buttons into the Forge apps and hypeForge Settings."""
        shared = self.shared()
        self.assertEqual(shared["group/quick"]["modules"], ["bluetooth", "network", "wireplumber"])
        for module in ("bluetooth", "network", "wireplumber"):
            self.assertIn("hypeforge-panel quick {popup}", shared[module]["on-click"], module)
            self.assertIn("on-click-right", shared[module], f"{module}: right click keeps the full app")

    def test_the_rice_right_side_is_in_javiers_order(self):
        """Javier, 2026-10-11, right to left: power, the status pill (volume · network · Bluetooth), disks/USB,
        printers, clipboard, CPU, memory, night light, the programs' icons. 2026-10-17: after the processor,
        in his order, the graphics card, temperature, memory and disk; the disk piece took the USB icon's
        place ("the system disk work… shouldn't replace the mount/umount icon?")."""
        rice = self.rice()
        right_to_left = ["custom/power-panel", "group/quick", "custom/clipboard",   # the printer: Quick Settings (10-25)
                         "custom/cpu", "custom/gpu", "custom/temperature", "custom/memory", "custom/disk", "tray"]   # the moon left (D-117)
        self.assertEqual(rice["modules-right"], right_to_left[::-1])

    def test_the_bell_sits_with_the_time_and_opens_the_same_pop_up(self):
        """Javier, 2026-10-11: 'Icon alert should go here, and the alert icon should not open the alert
        popup. Clicking on the Date/Time/Alert will open … all three.' 2026-10-13: on every style."""
        rice, shared = self.rice(), self.shared()
        self.assertEqual(rice["modules-center"], ["group/datetime"])
        self.assertEqual(shared["group/datetime"]["modules"], ["clock", "custom/notifications"])
        for module in ("clock", "custom/notifications"):
            self.assertIn("hypeforge-panel calendar {popup-calendar}", shared[module]["on-click"], module)
        self.assertIn("dnd", shared["custom/notifications"]["on-click-right"])
        self.assertNotIn("custom/notifications", rice["modules-right"])

    def test_the_moon_opens_the_night_light_part(self):
        self.assertIn("hypeforge-panel quick --only night {popup}", self.shared()["custom/nightlight"]["on-click"])
        self.assertIn("night", quick.ONLY)

    def rice(self):
        import json
        loader = __import__("importlib.machinery").machinery.SourceFileLoader("hfbar_r2", str(HERE / "applets/bar/hypeforge-bar"))
        bar = __import__("importlib.util").util.module_from_spec(__import__("importlib.util").util.spec_from_loader("hfbar_r2", loader))
        loader.exec_module(bar)
        return json.loads(bar.strip_comments((HERE / "styles/rice/bar/config.jsonc").read_text()))

    def test_the_parts_name_real_tiles_and_a_settings_app(self):
        src = (HERE / "applets/panels/views/quick.py").read_text()
        for part, (title, tiles, more) in quick.ONLY.items():
            for name in tiles:
                self.assertIn(f'("{name}", lambda', src, f"{part}: {name}")
            self.assertTrue(more.split()[0] in ("alacritty", "hypeforge-nmtui"), part)

    def test_the_panel_offers_only_those_parts(self):
        out = subprocess.run([sys.executable, str(HERE / "applets/panels/hypeforge-panel"), "--help"],
                             capture_output=True, text=True).stdout
        self.assertIn("{network,sound,bluetooth,night}", out)
        self.assertIn("library", out)

    def test_the_app_library_opens_on_every_app_then_the_groups(self):
        self.assertTrue((HERE / "applets/panels/views/library.py").is_file())
        self.assertIn("sets = sets[-1:] + sets[:-1]", (HERE / "applets/panels/views/start.py").read_text())



class QuickSettingsOneColourAndShortNames(unittest.TestCase):
    """The Rice review, 2026-10-27 (Javier: "fix 1 and 2"): Quick Settings mixed one-colour symbols with
    full-colour pictures (the headphones dark blue on the dark card), and long sound names were cut off."""

    def test_every_icon_goes_through_the_one_colour_helper(self):
        import re
        for f, helper in (("views/quick.py", "qspages.mono("), ("views/qspages.py", "mono(")):
            src = (HERE / "applets/panels" / f).read_text()
            calls = re.findall(r"new_from_icon_name\(\s*(\S+?\()?", src)
            self.assertTrue(calls, f)
            for found in re.finditer(r"new_from_icon_name\(\s*", src):
                self.assertTrue(src[found.end():].startswith(helper), f"{f}: {src[found.end():found.end() + 60]!r}")

    def test_the_helper_gives_one_colour_names(self):
        self.assertTrue(qspages.mono("printer").endswith("-symbolic"))
        self.assertEqual(qspages.mono("view-refresh-symbolic"), "view-refresh-symbolic")

    def test_icons_wear_the_cards_text_colour_and_the_on_tiles_own(self):
        css = qspages.css(panelkit.Look("rice", "kognogos-mocha")).decode()
        self.assertIn(".hf-quick image", css)
        self.assertIn(".hf-quick button.on image", css)

    def test_short_sound_names(self):
        f = qspages.friendly
        self.assertEqual(f("GA106 High Definition Audio Controller Digital Stereo (HDMI) [Sceptre Y27]", False),
                         "Sceptre Y27 · HDMI")
        self.assertEqual(f("Ryzen HD Audio Controller Analog Stereo", False), "Speakers jack")
        self.assertEqual(f("Ryzen HD Audio Controller Analog Stereo", True), "Microphone jack")
        self.assertEqual(f("C920 PRO HD Webcam Analog Stereo", True), "C920 PRO HD Webcam")
        self.assertEqual(f("SteelSeries Arctis 5 Chat", False), "SteelSeries Arctis 5 Chat")
        self.assertEqual(f("Navi 21 HDMI/DP Audio Digital Stereo (HDMI 2)", False), "Navi 21 HDMI/DP Audio · HDMI 2")


class TheVolumeChime(unittest.TestCase):
    """Javier, 2026-10-27: "When you are sliding the volume, when you release the button … sound a chime so people
    can hear the chime at the set volume"."""

    def setUp(self):
        self.popen, self.old = [], quick.subprocess.Popen
        quick.subprocess.Popen = lambda cmd, **kw: self.popen.append(cmd)

    def tearDown(self):
        quick.subprocess.Popen = self.old

    def test_letting_go_of_the_slider_chimes(self):
        be = quick.Backend(lambda cmd, timeout=3.0: "Volume: 0.40")
        row = quick.volume_row(be, 40, False)
        event = panelkit.Gdk.Event.new(panelkit.Gdk.EventType.BUTTON_RELEASE)
        event.button.button = 1
        handled = row.scale.emit("button-release-event", event)
        self.assertFalse(handled, "the slider still gets its release (it lets go of the knob)")
        self.assertEqual(len(self.popen), 1)
        self.assertEqual(self.popen[0][0], "pw-play")
        self.assertTrue(self.popen[0][1].endswith("audio-volume-change.oga"))

    def test_no_chime_when_muted(self):
        be = quick.Backend(lambda cmd, timeout=3.0: "Volume: 0.40 [MUTED]")
        be.chime()
        self.assertEqual(self.popen, [])

    def test_the_sound_page_chimes_too(self):
        src = (HERE / "applets/panels/views/qspages.py").read_text()
        self.assertIn("released=be.chime", src)


class TheCalendarReview(unittest.TestCase):
    """The Rice review, piece 5 (Javier, 2026-10-27: "fix all three … If I click on a date, I would like for the
    default calendar to open")."""

    def setUp(self):
        import calendar_view
        self.c = calendar_view

    def test_only_the_weeks_the_month_has(self):
        from datetime import date
        self.assertEqual(len(self.c.weeks(2026, 10)), 5)
        self.assertEqual(len(self.c.weeks(2026, 2)), 4, "February 2026 starts on a Sunday: four rows, no fifth")
        self.assertEqual(len(self.c.weeks(2027, 5)), 6)
        for y in (2025, 2026, 2027):
            for m in range(1, 13):
                w = self.c.weeks(y, m)
                self.assertEqual(w[0][0].weekday(), 6, "Sunday first")
                self.assertTrue(any(d.month == m for d in w[-1]), f"{y}-{m}: a week of only next month")
                self.assertTrue(any(d == date(y, m, 1) for d in w[0]))

    def test_the_notifications_heading_is_a_title(self):
        src = (HERE / "applets/panels/views/calendar_view.py").read_text()
        self.assertRegex(src, r'heading = Gtk.Label\(label="Notifications".*\n.*add_class\("hf-head-name"\)')

    def test_our_own_senders_get_their_icon(self):
        entries = {"nogforge": {"name": "nogForge", "icon": "system-software-install"}}
        self.assertEqual(self.c.icon_for({"app_name": "nog"}, entries), "system-software-install")
        self.assertEqual(self.c.icon_for({"app_name": "nightForge"}, {}), "weather-clear-night")
        self.assertEqual(self.c.icon_for({"app_name": "someone"}, {}), "dialog-information")

    def test_a_day_opens_your_calendar(self):
        from datetime import date
        day = date(2026, 10, 30)
        tb = {"org.mozilla.Thunderbird": {"exec": "thunderbird %u"}}
        self.assertEqual(self.c.open_day(day, run=lambda *a, **k: None, query="org.mozilla.Thunderbird.desktop",
                                         entries=tb), ["thunderbird", "-calendar"])
        web = {"gcal": {"exec": "google-chrome --app=https://calendar.google.com/calendar/r %U"}}
        self.assertEqual(self.c.open_day(day, run=lambda *a, **k: None, query="gcal.desktop", entries=web),
                         ["google-chrome", "--app=https://calendar.google.com/calendar/r/day/2026/10/30"])
        ours = {"kognogos-web-google-calendar": {"exec": "/usr/bin/python3 /x/webapp-open google-calendar %u"}}
        self.assertEqual(self.c.open_day(day, run=lambda *a, **k: None, query="kognogos-web-google-calendar.desktop",
                                         entries=ours), ["/usr/bin/python3", "/x/webapp-open", "google-calendar",
                                                         "--day=2026-10-30"])
        self.assertEqual(self.c.open_day(day, run=lambda *a, **k: None, query="", entries={}),
                         ["xdg-open", "https://calendar.google.com/calendar/r/day/2026/10/30"])

if __name__ == "__main__":
    unittest.main()


class ClipboardPanel(unittest.TestCase):
    """Javier, 2026-10-17: the clipboard list "is horrible and without identity" → a panel like the others."""

    @classmethod
    def setUpClass(cls):
        import clipboard as clipview
        cls.v = clipview
        loader = __import__("importlib.machinery").machinery.SourceFileLoader(
            "hf_clipboard_test", str(HERE / "applets/clipboard/hypeforge-clipboard"))
        spec = __import__("importlib.util").util.spec_from_loader("hf_clipboard_test", loader)
        cls.app = __import__("importlib.util").util.module_from_spec(spec)
        loader.exec_module(cls.app)

    def test_each_copy_says_what_it_is(self):
        k = self.v.kind_of
        pic = self.app.PICTURE.match("[[ binary data 12 KiB png 640x360 ]]")
        self.assertEqual(k("https://github.com/jetomev/forge-suite/issues/54", None), "link")
        self.assertEqual(k("#cba6f7", None), "colour")
        self.assertEqual(k("~/Programs/forge-suite/hypeforge", None), "path")
        self.assertEqual(k("def copy_back(entry) -> None:", None), "code")
        self.assertEqual(k("Meeting moved to Thursday at 3 pm", None), "text")
        self.assertEqual(k("[[ binary data 12 KiB png 640x360 ]]", pic), "picture")
        self.assertEqual(self.v.what_line("picture", "[[ binary data 12 KiB png 640x360 ]]", pic), "Picture · PNG · 640 × 360")
        self.assertEqual(self.v.what_line("link", "https://www.example.com/a/b", None), "Link · example.com")
        self.assertEqual(self.v.what_line("text", "two words", None), "Text · 2 words")

    def test_it_opens_where_the_bars_pop_ups_do(self):
        with tempfile.TemporaryDirectory() as d:
            places = Path(d) / "places.json"
            places.write_text('{"{popup}": "--edges bottom,right --margin bottom=56,right=8"}')
            argv = self.app.panel_argv([], (), places)
            self.assertEqual(argv[1:], ["clipboard", "--edges", "bottom,right", "--margin", "bottom=56,right=8"],
                             "Win + C: the bar's note (Windows 11's bar is at the bottom)")
            argv = self.app.panel_argv(["--edges", "top,right", "--margin", "top=44,right=8"], ("--ask-clear",), places)
            self.assertEqual(argv[1:], ["clipboard", "--edges", "top,right", "--margin", "top=44,right=8", "--ask-clear"],
                             "a click: the bar's own words win; the right click asks to empty it")
            self.assertEqual(self.app.panel_argv([], (), Path(d) / "none.json")[1:], ["clipboard"], "no note: its own corner")

    def test_the_bar_passes_its_place_on_both_clicks(self):
        for f in ("sway/waybar/modules.jsonc", "sway/waybar/config.jsonc"):
            text = (HERE / f).read_text()
            self.assertIn("hypeforge-clipboard list {popup}", text, f)
            self.assertIn("hypeforge-clipboard clear {popup}", text, f)

    def test_the_panel_knows_the_view(self):
        self.assertIn('"clipboard": "clipboard"', (HERE / "applets/panels/hypeforge-panel").read_text())


class NotificationCards(unittest.TestCase):
    def test_closer_and_smaller(self):
        """Javier, 2026-10-17: "a little big and space between them is too much"."""
        src = (HERE / "applets/panels/views/calendar_view.py").read_text()
        self.assertIn(".hf-card.hf-note {{ padding: 6px 12px; }}", src)
        self.assertIn("root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)", src, "the blocks 4 px apart (was 10)")
        self.assertIn(".hf-card.hf-head {{ padding: 4px 6px 4px 12px; }}", src, "a slim head")
        self.assertIn("cards = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)", src)
        self.assertIn("new_from_file_at_size(path, 24, 24)", src)


class TrayMenu(unittest.TestCase):
    """2026-10-17: a tray app's menu as a hypeForge pop-up (Waybar's opened at the pointer, over the bar)."""

    @classmethod
    def setUpClass(cls):
        import traymenu
        sys.path.insert(0, str(HERE / "applets/tray"))
        import hfsni
        import json as _json
        cls.v, cls.sni = traymenu, hfsni
        cls.layout = _json.loads((HERE / "tests/fixtures/tray-menu-dropbox.json").read_text())

    def test_the_apps_spaces_become_an_indent_and_underscores_go(self):
        self.assertEqual(self.v.clean("   you@example.com"), ("you@example.com", 1))
        self.assertEqual(self.v.clean("_Preferences"), ("Preferences", 0))
        self.assertEqual(self.v.clean("Save__As"), ("Save_As", 0))

    def test_the_separators_cut_the_menu_into_cards(self):
        g = self.v.groups(self.layout)
        self.assertEqual([len(x) for x in g], [2, 4, 3, 4, 1], "Dropbox's menu: five cards, the double separator once")
        self.assertEqual(g[-1][0][1]["label"], "Quit Dropbox")

    def test_an_item_is_found_by_its_name_or_its_path(self):
        self.assertEqual(self.sni.split(":1.48/org/ayatana/NotificationItem/dropbox"),
                         (":1.48", "/org/ayatana/NotificationItem/dropbox"))
        self.assertEqual(self.sni.split("org.kde.StatusNotifierItem-5001-1"),
                         ("org.kde.StatusNotifierItem-5001-1", "/StatusNotifierItem"))
        self.assertEqual(self.sni.split("/StatusNotifierItem", ":1.9"), (":1.9", "/StatusNotifierItem"))


class OwnTray(unittest.TestCase):
    def test_every_styles_tray_becomes_ours_nested_ones_too(self):
        import importlib.machinery, importlib.util
        ld = importlib.machinery.SourceFileLoader("hb_tray_test", str(HERE / "applets/bar/hypeforge-bar"))
        sp = importlib.util.spec_from_loader("hb_tray_test", ld)
        hb = importlib.util.module_from_spec(sp)
        ld.exec_module(hb)
        self.assertEqual(hb.own_tray({"modules-right": ["tray", "clock"], "group/hidden": {"modules": ["x", "tray"]}}),
                         {"modules-right": ["group/tray", "clock"], "group/hidden": {"modules": ["x", "group/tray"]}})
        mods = (HERE / "sway/waybar/modules.jsonc").read_text()
        for n in range(1, 11):
            self.assertIn(f'"image#tray-{n}"', mods)
        self.assertIn("menu 1 {popup}", mods, "a click carries the bar's pop-up place")
        self.assertEqual(mods.count('"interval": 3600, "signal": 15'), 10,
                         "every piece has an interval: an exec without one hangs Waybar 0.15 before it draws")

    def test_the_tray_starts_at_login_under_the_watcher(self):
        self.assertIn("hypeforge-watch tray ~/Programs/forge-suite/hypeforge/applets/tray/hypeforge-tray run",
                      (HERE / "sway/config").read_text())
