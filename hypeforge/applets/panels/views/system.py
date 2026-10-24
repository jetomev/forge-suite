"""The system pop-ups (Javier, 2026-10-17: "icons and popups for CPU, GPU, Temperature, Memory, Disks
Space. Let's make them pretty too!!!"). One pop-up per bar piece (`--part`), each one window with soft
lines between its parts (the same day, for the tray's menu: "one window, and using pretty separator
lines"), in the style's and theme's own look:

  - cpu      the processor: how busy, its last three minutes as a graph, every thread as a small bar,
             its speed, temperature, load and time since start, the busiest apps
  - gpu      the graphics card: how busy and its graph, its own memory, temperature, power, fan, speed,
             the apps holding its memory
  - temp     every sensor in groups (processor, graphics, drives, memory sticks, the board), each with a
             bar up to its own "hot" mark, the processor's and card's graph, and every fan
  - memory   in use / cache / free as one bar, the graph, the swap, the apps holding the most
  - disk     every disk in plain words (System, Boot, a USB drive by its name), how full, how much is
             free; a click opens it in the file manager; Eject on a USB drive, Mount on one plugged in
             but not mounted (it took the USB icon's job, 2026-10-17); the internal drives not opened

The numbers move while it is open (every two seconds). The sampler (`applets/system/hypeforge-system
run`) keeps the last three minutes, so the graphs are drawn from the first moment.
"""

from __future__ import annotations

import math
import shlex
import cairo
import sys
import time

import panelkit  # first: it picks GTK 3 before anything asks for GTK
from gi.repository import Gdk, GLib, Gtk, Pango  # noqa: E402

sys.path.insert(0, str(panelkit.APPLETS / "system"))
import hfsys  # noqa: E402

GLYPH = {"cpu": "\U000f035b", "gpu": "\U000f08ae", "temp": "\U000f050f", "memory": "\U000f061a", "disk": "\U0000f0a0",
         "ssd": "\U0000f0a0", "nvme": "\U0000f0a0", "hdd": "\U000f02ca", "usb": "\U000f0553", "fan": "\U000f0210"}
TITLE = {"cpu": "Processor", "gpu": "Graphics card", "temp": "Temperature", "memory": "Memory", "disk": "Disks"}
WIDTH = 380
TICK = 2000           # ms between updates while open

CSS = """
.hf-sys {{ min-width: {width}px; }}
.hf-sys-glyph {{ font-family: "Symbols Nerd Font", "{font}"; font-size: {glyph}pt; color: {accent}; }}   /* the drive rows' */
.hf-sys-sub {{ color: {dim}; font-size: {small}pt; }}
.hf-sys-big {{ font-size: {big}pt; font-weight: bold; color: {text}; }}
.hf-sys-big.warning {{ color: {warm}; }}
.hf-sys-big.critical {{ color: {danger}; }}
.hf-sys-section {{ color: {dim}; font-size: {small}pt; font-weight: bold; }}
.hf-sys-name {{ color: {text}; }}
.hf-sys-value {{ color: {text}; font-feature-settings: "tnum"; }}
.hf-sys-value.warning {{ color: {warm}; }}
.hf-sys-value.critical {{ color: {danger}; }}
.hf-sys-tile {{ background: {tile}; border-radius: {inner}px; padding: 6px 10px; }}
.hf-sys-tile-word {{ color: {dim}; font-size: {small}pt; }}
.hf-sys-tile-value {{ color: {text}; font-weight: bold; }}
.hf-sys-key {{ font-size: {small}pt; color: {dim}; }}
.hf-sys-dot {{ font-size: {small}pt; }}
.hf-line {{ min-height: 1px; margin: 9px 0; border: none;
           background-image: linear-gradient(to right, transparent, {line} 12%, {line} 88%, transparent); background-color: transparent; }}
button.hf-sys-row {{ background: transparent; border-color: transparent; padding: 5px 6px; border-radius: {inner}px; }}
button.hf-sys-row:hover, button.hf-sys-row:focus {{ background: {hover}; }}
"""


# ---- colours ------------------------------------------------------------------------------------

def rgb(hexv: str) -> tuple[float, float, float]:
    h = hexv.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix(a: str, b: str, t: float) -> str:
    ra, rb = rgb(a), rgb(b)
    return "#" + "".join(f"{round((x + (y - x) * t) * 255):02x}" for x, y in zip(ra, rb))


class Paint:
    """The colours the drawings use, from the look: the accent for calm, a warm mix, the danger red."""

    def __init__(self, look: panelkit.Look):
        c = look.colour
        self.accent, self.danger, self.track = c["panel_tile_on"], c["panel_danger"], c["panel_tile"]
        self.warm = mix(c["panel_tile_on"], c["panel_danger"], 0.55)
        self.text, self.dim, self.line = c["panel_text"], c["panel_text_dim"], c["panel_border"]
        self.second = mix(c["panel_text_dim"], c["panel_tile_on"], 0.25)
        self.round = not look.straight

    def of(self, state: str) -> str:
        return {"warning": self.warm, "critical": self.danger}.get(state, self.accent)


def rounded(cr, x, y, w, h, r):
    r = max(0.0, min(r, w / 2, h / 2))
    if r <= 0:
        cr.rectangle(x, y, w, h)
        return
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


# ---- the drawings ---------------------------------------------------------------------------------

class Meter(Gtk.DrawingArea):
    """A bar: one or more coloured parts on a track (memory: in use, then cache)."""

    def __init__(self, paint: Paint, height: int = 8):
        super().__init__()
        self.paint, self.parts = paint, []
        self.set_size_request(-1, height)
        self.connect("draw", self._draw)

    def set(self, parts: list[tuple[float, str]]):
        """parts: (fraction 0-1, colour), left to right."""
        self.parts = parts
        self.queue_draw()

    def _draw(self, _w, cr):
        w, h = self.get_allocated_width(), self.get_allocated_height()
        r = h / 2 if self.paint.round else 0
        rounded(cr, 0, 0, w, h, r)
        cr.set_source_rgb(*rgb(self.paint.track))
        cr.fill_preserve()
        cr.clip()
        x = 0.0
        for frac, colour in self.parts:
            pw = max(0.0, min(frac, 1.0)) * w
            if pw <= 0:
                continue
            rounded(cr, x, 0, pw + (r if x + pw < w - 1 else 0), h, r)
            cr.set_source_rgb(*rgb(colour))
            cr.fill()
            x += pw
        return False


class Graph(Gtk.DrawingArea):
    """The last three minutes: a line with a soft fill under it, faint lines at a quarter, half, three
    quarters; a second line (dashed) when given."""

    def __init__(self, paint: Paint, height: int = 74, top: float = 100.0, low: float = 0.0):
        super().__init__()
        self.paint, self.top, self.low = paint, top, low
        self.series: list[tuple[list, str, bool]] = []
        self.set_size_request(-1, height)
        self.connect("draw", self._draw)

    def set(self, series: list[tuple[list, str, bool]], top: float | None = None):
        self.series = series
        if top:
            self.top = top
        self.queue_draw()

    def _draw(self, _w, cr):
        w, h = self.get_allocated_width(), self.get_allocated_height()
        p = self.paint
        rounded(cr, 0, 0, w, h, 8 if p.round else 0)
        cr.set_source_rgba(*rgb(p.track), 0.55)
        cr.fill_preserve()
        cr.clip()
        cr.set_line_width(1)
        cr.set_source_rgba(*rgb(p.line), 0.45)
        for q in (0.25, 0.5, 0.75):
            y = round(h * q) + 0.5
            cr.set_dash([2, 4])
            cr.move_to(0, y)
            cr.line_to(w, y)
            cr.stroke()
        cr.set_dash([])
        for values, colour, dashed in self.series:
            pts = [v for v in values[-hfsys.KEEP:]]
            if len(pts) < 2:
                continue
            step = w / (hfsys.KEEP - 1)
            x0 = w - step * (len(pts) - 1)
            coords = [(x0 + i * step, h - 3 - (h - 6) * max(0.0, min(((v or self.low) - self.low) / (self.top - self.low), 1.0))) for i, v in enumerate(pts)]
            cr.move_to(*coords[0])
            for x, y in coords[1:]:
                cr.line_to(x, y)
            if not dashed:
                cr.line_to(coords[-1][0], h)
                cr.line_to(coords[0][0], h)
                cr.close_path()
                grad = cairo.LinearGradient(0, 0, 0, h)
                grad.add_color_stop_rgba(0, *rgb(colour), 0.42)
                grad.add_color_stop_rgba(1, *rgb(colour), 0.03)
                cr.set_source(grad)
                cr.fill()
                cr.move_to(*coords[0])
                for x, y in coords[1:]:
                    cr.line_to(x, y)
            cr.set_source_rgb(*rgb(colour))
            cr.set_line_width(2 if not dashed else 1.5)
            cr.set_dash([4, 3] if dashed else [])
            cr.stroke()
            cr.set_dash([])
            x, y = coords[-1]                              # the latest reading, a dot
            cr.arc(x - 2, y, 3, 0, 2 * math.pi)
            cr.fill()
        return False


class Threads(Gtk.DrawingArea):
    """Every thread of the processor as a small upright bar."""

    def __init__(self, paint: Paint, height: int = 44):
        super().__init__()
        self.paint, self.values = paint, []
        self.set_size_request(-1, height)
        self.connect("draw", self._draw)

    def set(self, values: list[float]):
        self.values = values
        self.queue_draw()

    def _draw(self, _w, cr):
        n = len(self.values)
        if not n:
            return False
        w, h = self.get_allocated_width(), self.get_allocated_height()
        gap = 3 if n <= 32 else 1
        bw = (w - gap * (n - 1)) / n
        r = min(bw / 2, 3) if self.paint.round else 0
        for i, v in enumerate(self.values):
            x = i * (bw + gap)
            rounded(cr, x, 0, bw, h, r)
            cr.set_source_rgb(*rgb(self.paint.track))
            cr.fill()
            vh = max(2.0, h * min(v, 100) / 100)
            rounded(cr, x, h - vh, bw, vh, r)
            cr.set_source_rgb(*rgb(self.paint.of(hfsys.level(v, *hfsys.BUSY))))
            cr.fill()
        return False


# ---- small pieces ----------------------------------------------------------------------------------

def label(words: str = "", *classes: str, xalign: float = 0, ellipsize: bool = True) -> Gtk.Label:
    lab = Gtk.Label(label=words, xalign=xalign)
    if ellipsize:
        lab.set_ellipsize(Pango.EllipsizeMode.END)
    for c in classes:
        lab.get_style_context().add_class(c)
    return lab


def line() -> Gtk.Widget:
    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.get_style_context().add_class("hf-line")
    return sep


def section(words: str) -> Gtk.Label:
    lab = label(words.upper(), "hf-sys-section")
    lab.set_margin_bottom(4)
    return lab


def state_class(widget: Gtk.Widget, state: str):
    ctx = widget.get_style_context()
    for s in ("warning", "critical"):
        (ctx.add_class if s == state else ctx.remove_class)(s)


class Tiles(Gtk.Grid):
    """Small facts two by two: a dim word over a bold value."""

    def __init__(self, words: list[str]):
        super().__init__(column_spacing=6, row_spacing=6, column_homogeneous=True)
        self.values = {}
        for i, w in enumerate(words):
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
            box.get_style_context().add_class("hf-sys-tile")
            box.pack_start(label(w, "hf-sys-tile-word"), False, False, 0)
            v = label("–", "hf-sys-tile-value")
            box.pack_start(v, False, False, 0)
            self.values[w] = v
            self.attach(box, i % 2, i // 2, 1, 1)

    def set(self, word: str, value: str, state: str = "ok"):
        self.values[word].set_label(value)
        state_class(self.values[word], state)


class Rows(Gtk.Box):
    """A short list: a name, its number, a thin bar under it (the busiest apps, the sensors)."""

    def __init__(self, paint: Paint, n: int, bars: bool = True):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.paint, self.rows = paint, []
        for _ in range(n):
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            top = Gtk.Box(spacing=8)
            name, value = label("", "hf-sys-name"), label("", "hf-sys-value", xalign=1, ellipsize=False)
            top.pack_start(name, True, True, 0)
            top.pack_end(value, False, False, 0)
            box.pack_start(top, False, False, 0)
            meter = Meter(paint, 4) if bars else None
            if meter:
                box.pack_start(meter, False, False, 0)
            self.pack_start(box, False, False, 0)
            self.rows.append((box, name, value, meter))
        self.empty = label("", "hf-sys-sub")
        self.pack_start(self.empty, False, False, 0)

    def set(self, items: list[tuple[str, str, float, str]], empty: str = ""):
        """items: (name, value words, fraction 0-1, state)."""
        for i, (box, name, value, meter) in enumerate(self.rows):
            if i < len(items):
                n, v, frac, state = items[i]
                name.set_label(n)
                value.set_label(v)
                state_class(value, state)
                if meter:
                    meter.set([(frac, self.paint.of(state))])
                box.show_all()
            else:
                box.hide()
        self.empty.set_label(empty if not items else "")
        self.empty.set_visible(bool(empty and not items))


def legend(paint: Paint, keys: list[tuple[str, str]]) -> Gtk.Box:
    box = Gtk.Box(spacing=12)
    for words, colour in keys:
        dot = Gtk.Label(label="●")
        dot.get_style_context().add_class("hf-sys-dot")
        prov = Gtk.CssProvider()
        prov.load_from_data(f"label {{ color: {colour}; }}".encode())
        dot.get_style_context().add_provider(prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 2)
        pair = Gtk.Box(spacing=4)
        pair.pack_start(dot, False, False, 0)
        pair.pack_start(label(words, "hf-sys-key", ellipsize=False), False, False, 0)
        box.pack_start(pair, False, False, 0)
    return box


# ---- the pop-up ------------------------------------------------------------------------------------

class View:
    """The open pop-up: its head, its parts, and one update() every two seconds."""

    def __init__(self, look: panelkit.Look, part: str, panel_close):
        self.part, self.paint, self.close = part, Paint(look), panel_close
        state = hfsys.read_state()
        self.sampler = hfsys.Sampler(state.get("history"))
        if hfsys.fresh(state):
            self.sampler.now = state
        else:                                          # no sampler running: read now (the processor needs two looks)
            time.sleep(0.4)
            self.sampler.sample(with_gpu=part in ("gpu", "temp"))
        self.scan, self.scan_at = (hfsys.proc_scan(), time.time()) if part in ("cpu", "memory") else ({}, 0)
        self.top_cpu: list = []
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.root.get_style_context().add_class("hf-sys")
        self.updates = []
        self._head()
        getattr(self, f"_{part}")()
        self.update()

    # the head: the glyph, the title and a dim line (the one title row, D-116), the big number
    def _head(self):
        head = Gtk.Box(spacing=12)
        glyph = label(GLYPH[self.part], "hf-head-glyph", ellipsize=False)
        head.pack_start(glyph, False, False, 0)
        words = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        words.set_valign(Gtk.Align.CENTER)
        words.pack_start(label(TITLE[self.part], "hf-head-name"), False, False, 0)
        self.sub = label("", "hf-head-sub")
        words.pack_start(self.sub, False, False, 0)
        head.pack_start(words, True, True, 0)
        self.big = label("", "hf-sys-big", xalign=1, ellipsize=False)
        head.pack_end(self.big, False, False, 0)
        self.root.pack_start(head, False, False, 0)

    def add(self, *widgets: Gtk.Widget, gap: int = 6, into: Gtk.Box | None = None):
        for w in widgets:
            w.set_margin_top(gap if w is not widgets[0] else 0)
            (into or self.root).pack_start(w, False, False, 0)

    def button(self, words: str, command: str) -> Gtk.Button:
        b = Gtk.Button(label=words)
        b.connect("clicked", lambda _b: (self.close(), panelkit.run_command(command)))
        return b

    def footer(self, *buttons: Gtk.Button):
        box = Gtk.Box(spacing=6, homogeneous=True)
        for b in buttons:
            box.pack_start(b, True, True, 0)
        self.add(line(), box, gap=0)

    # ---- the processor
    def _cpu(self):
        self.graph = Graph(self.paint)
        self.threads = Threads(self.paint)
        self.threads_word = section("")
        self.tiles = Tiles(["Speed", "Temperature", "Load (1 minute)", "Running for"])
        self.apps = Rows(self.paint, 5)
        self.add(panelkit.head_line(), section("The last 3 minutes"), self.graph, gap=0)
        self.add(line(), self.threads_word, self.threads, gap=0)
        self.add(line(), self.tiles, gap=0)
        self.add(line(), section("Busiest apps"), self.apps, gap=0)
        self.footer(self.button("Every program (btop)", "alacritty --class hf-btop -e btop"))
        self.updates.append(self._cpu_update)

    def _cpu_update(self, n: dict):
        busy = n.get("cpu", 0.0)
        self.sub.set_label(f"{hfsys.cpu_model()}")
        self.big.set_label(f"{busy:.0f} %")
        state_class(self.big, hfsys.level(busy, *hfsys.BUSY))
        self.graph.set([(n["history"]["cpu"], self.paint.of(hfsys.level(busy, *hfsys.BUSY)), False)])
        cores = n.get("cores") or []
        self.threads.set(cores)
        self.threads_word.set_label(f"{len(cores)} THREADS · EACH ONE'S SHARE OF THE WORK")
        self.tiles.set("Speed", f"{n['speed']:.2f} GHz" if n.get("speed") else "–")
        t = hfsys.cpu_temp(n.get("temps") or [])
        tr = next((r for r in n.get("temps") or [] if r["group"] == "Processor"), None)
        self.tiles.set("Temperature", f"{t:.0f} °C" if t is not None else "–", tr["state"] if tr else "ok")
        cores_n = max(len(cores), 1)
        load = n.get("load", 0.0)
        self.tiles.set("Load (1 minute)", f"{load:.2f}", hfsys.level(100 * load / cores_n, *hfsys.BUSY))
        self.tiles.set("Running for", hfsys.duration(n.get("uptime", 0)))
        self.apps.set([(name, f"{pct:.1f} %", pct / 100, hfsys.level(pct, *hfsys.BUSY)) for name, pct in self.top_cpu],
                      "Counting… (a moment)" if not self.top_cpu else "")

    # ---- the graphics card
    def _gpu(self):
        self.graph = Graph(self.paint)
        self.vram = Meter(self.paint, 8)
        self.vram_word = label("", "hf-sys-sub")
        self.tiles = Tiles(["Temperature", "Power", "Fan", "Speed"])
        self.apps = Rows(self.paint, 5)
        self.add(panelkit.head_line(), section("The last 3 minutes"), self.graph, gap=0)
        vrow = Gtk.Box(spacing=8)
        vrow.pack_start(section("Its own memory"), True, True, 0)
        vrow.pack_end(self.vram_word, False, False, 0)
        self.add(line(), vrow, self.vram, gap=0)
        self.add(line(), self.tiles, gap=0)
        self.add(line(), section("Apps using it"), self.apps, gap=0)
        self.updates.append(self._gpu_update)
        self.gpu_apps_at = 0.0

    def _gpu_update(self, n: dict):
        g = n.get("gpu")
        if not g:
            self.sub.set_label("No graphics card readings on this computer")
            self.big.set_label("–")
            return
        busy = g.get("busy") or 0.0
        self.sub.set_label(f"{g['maker']} {g['name']}" if g["maker"] not in g["name"] else g["name"])
        self.big.set_label(f"{busy:.0f} %")
        state_class(self.big, hfsys.level(busy, *hfsys.BUSY))
        self.graph.set([(n["history"]["gpu"], self.paint.of(hfsys.level(busy, *hfsys.BUSY)), False)])
        if g.get("mem_total"):
            frac = g["mem_used"] / g["mem_total"]
            self.vram.set([(frac, self.paint.of(hfsys.level(100 * frac, *hfsys.FULL)))])
            self.vram_word.set_label(f"{hfsys.gib(g['mem_used'])} of {hfsys.gib(g['mem_total'])}")
        t = g.get("temp")
        self.tiles.set("Temperature", f"{t:.0f} °C" if t is not None else "–", hfsys.level(t, 75, 87))
        self.tiles.set("Power", f"{g['power']:.0f} of {g['power_limit']:.0f} W" if g.get("power") is not None
                       and g.get("power_limit") else f"{g['power']:.0f} W" if g.get("power") is not None else "–")
        self.tiles.set("Fan", f"{g['fan']:.0f} %" if g.get("fan") is not None else "–")
        self.tiles.set("Speed", f"{g['clock']:.0f} MHz" if g.get("clock") is not None else "–")
        if time.time() - self.gpu_apps_at > 5:            # the list changes slowly: every few seconds
            self.gpu_apps_at = time.time()
            apps = hfsys.gpu_apps()
            most = max((mb for _n, mb in apps), default=1) or 1
            self.apps.set([(name, f"{mb:.0f} MB", mb / most, "ok") for name, mb in apps[:5]],
                          "No app list for this card" if g["maker"] != "NVIDIA" else "Nothing using it")

    # ---- temperatures
    def _temp(self):
        # many sensors: two columns side by side (one column ran past a 1080-line screen)
        cols = Gtk.Box(spacing=22, homogeneous=True)
        left, right = (Gtk.Box(orientation=Gtk.Orientation.VERTICAL) for _ in range(2))
        cols.pack_start(left, True, True, 0)
        cols.pack_start(right, True, True, 0)
        self.add(panelkit.head_line(), cols, gap=0)
        self.graph = Graph(self.paint, top=100, low=20)
        self.add(section("The last 3 minutes · 20 to 100 °C"), self.graph, gap=0, into=left)
        self.add(legend(self.paint, [("Processor", self.paint.accent), ("Graphics card", self.paint.second)]), gap=6, into=left)
        self.groups: dict[str, Rows] = {}
        self.tiled: dict[str, Tiles] = {}
        temps = self.sampler.now.get("temps") or []
        for g in hfsys.GROUP_ORDER:
            rows = [r for r in temps if r["group"] == g]
            if not rows:
                continue
            words = {"Drives": "Drives", "Memory": "Memory sticks", "Board": "The board and the case"}.get(g, g)
            if g == "Memory":                       # the sticks read alike: small tiles, two across
                box = Tiles([r["name"].replace("Memory stick", "Stick") for r in rows])
                self.tiled[g] = box
            else:
                box = Rows(self.paint, len(rows))
                self.groups[g] = box
            col = left if g in ("Processor", "Graphics", "Drives") else right
            first = not col.get_children()
            self.add(*([] if first else [line()]), section(words), box, gap=0, into=col)
        fans = self.sampler.now.get("fans") or []
        self.fans = Tiles([f["name"] for f in fans]) if fans else None
        if self.fans:
            self.add(*([line()] if right.get_children() else []), section("Fans"), self.fans, gap=0, into=right)
        self.updates.append(self._temp_update)

    def _temp_update(self, n: dict):
        temps = n.get("temps") or []
        hot = hfsys.hottest(temps)
        state = hot["state"] if hot else "ok"
        self.sub.set_label({"ok": "Everything's cool", "warning": f"{hot['name']} is running warm" if hot else "",
                            "critical": f"{hot['name']} is hot!" if hot else ""}[state])
        cpu = hfsys.cpu_temp(temps)
        shown = cpu if cpu is not None else hot["temp"] if hot else None
        self.big.set_label(f"{shown:.0f}°" if shown is not None else "–")
        state_class(self.big, next((r["state"] for r in temps if r["group"] == "Processor"), state))
        self.graph.set([(n["history"]["cpu_temp"], self.paint.accent, False),
                        (n["history"]["gpu_temp"], self.paint.second, True)])
        for g, box in self.groups.items():
            box.set([(r["name"], f"{r['temp']:.0f} °C", r["temp"] / r["hot"], r["state"]) for r in temps if r["group"] == g])
        for g, box in self.tiled.items():
            for r in temps:
                if r["group"] == g:
                    box.set(r["name"].replace("Memory stick", "Stick"), f"{r['temp']:.0f} °C", r["state"])
        if self.fans:
            for f in n.get("fans") or []:
                if f["name"] in self.fans.values:
                    self.fans.set(f["name"], (f"{f['rpm']:,} rpm" if f["rpm"] else "stopped") if "rpm" in f
                                  else f"{f['percent']:.0f} %")

    # ---- memory
    def _memory(self):
        self.meter = Meter(self.paint, 12)
        self.graph = Graph(self.paint)
        self.swap = Meter(self.paint, 6)
        self.swap_word = label("", "hf-sys-sub", ellipsize=False)
        self.apps = Rows(self.paint, 5)
        self.add(panelkit.head_line(), self.meter, gap=0)
        self.keys = legend(self.paint, [("In use", self.paint.accent), ("Cache (given back when needed)", self.paint.second),
                                        ("Free", self.paint.dim)])
        self.add(self.keys, gap=6)
        self.add(line(), section("The last 3 minutes"), self.graph, gap=0)
        srow = Gtk.Box(spacing=8)
        srow.pack_start(section("Swap (memory kept on the disk)"), True, True, 0)
        srow.pack_end(self.swap_word, False, False, 0)
        self.add(line(), srow, self.swap, gap=0)
        self.add(line(), section("Apps holding the most"), self.apps, gap=0)
        self.footer(self.button("Every program (btop)", "alacritty --class hf-btop -e btop"))
        self.updates.append(self._memory_update)

    def _memory_update(self, n: dict):
        m = n["memory"]
        state = hfsys.level(m["percent"], *hfsys.BUSY)
        self.sub.set_label(f"{hfsys.gib(m['used'])} of {hfsys.gib(m['total'])} in use")
        self.big.set_label(f"{m['percent']:.0f} %")
        state_class(self.big, state)
        t = m["total"] or 1
        self.meter.set([(m["used"] / t, self.paint.of(state)), (m["cache"] / t, self.paint.second)])
        self.graph.set([(n["history"]["memory"], self.paint.of(state), False)])
        if m["swap_total"]:
            self.swap.set([(m["swap_used"] / m["swap_total"], self.paint.second)])
            self.swap_word.set_label(f"{hfsys.gib(m['swap_used'])} of {hfsys.gib(m['swap_total'])}")
        else:
            self.swap_word.set_label("none set up")
        apps = hfsys.top_memory(self.scan)
        self.apps.set([(name, hfsys.gib(b), b / t, "ok") for name, b in apps])

    # ---- disks
    def _disk(self):
        self.drives_tool = drives_applet()
        self.disk_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.disk_box, gap=0)
        self.footer(self.button("Free up space (nogForge)", "alacritty --class nogforge -e nogforge"))
        self.updates.append(self._disk_update)
        self._disk_fill()

    def _disk_fill(self):
        """Every disk with its space, and the USB drives' actions (2026-10-17, Javier: the disk work "shouldn't
        replace the mount/umount icon?"): Eject on a USB drive mounted for the desktop, Mount on one plugged
        in but not mounted. A row's click opens it. Drawn again after every action."""
        for child in self.disk_box.get_children():
            self.disk_box.remove(child)
        self.disk_rows: dict[str, tuple] = {}
        self.disk_at = 0.0
        info = hfsys.block_info()
        self.disks = hfsys.disks(info=info)
        usb = {d[0]: d for d in self.drives_tool.drives()} if self.drives_tool else {}
        rows = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.add(panelkit.head_line(), rows, gap=0, into=self.disk_box)
        for d in self.disks:
            b = Gtk.Button()
            b.get_style_context().add_class("hf-sys-row")
            b.set_tooltip_text(f"Open {d['where']} in the file manager")
            b.connect("clicked", lambda _b, where=d["where"]: (self.close(), panelkit.run_command(f"xdg-open {shlex.quote(where)}")))
            box = Gtk.Box(spacing=10)
            glyph = label(GLYPH[d["kind"]], "hf-sys-glyph", ellipsize=False)
            glyph.set_valign(Gtk.Align.CENTER)
            box.pack_start(glyph, False, False, 0)
            col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            top = Gtk.Box(spacing=8)
            top.pack_start(label(d["name"], "hf-sys-name"), True, True, 0)
            free = label("", "hf-sys-value", xalign=1, ellipsize=False)
            top.pack_end(free, False, False, 0)
            col.pack_start(top, False, False, 0)
            meter = Meter(self.paint, 7)
            col.pack_start(meter, False, False, 0)
            where = {"usb": "USB drive", "hdd": "hard drive", "nvme": "NVMe drive", "ssd": "solid-state drive"}[d["kind"]]
            drive = usb.get(d["device"])
            if drive and not self.drives_tool.ejectable(drive):
                where += " · mounted by the system"          # e.g. /mnt/exodos: shown, never offered for Eject
            col.pack_start(label(f"{d['where']} · {where}", "hf-sys-sub"), False, False, 0)   # the model: in the tip
            if d["model"]:
                b.set_tooltip_text(f"{d['model']}\nOpen {d['where']} in the file manager")
            box.pack_start(col, True, True, 0)
            b.add(box)
            row = Gtk.Box(spacing=4)
            row.pack_start(b, True, True, 0)
            if drive and self.drives_tool.ejectable(drive):
                row.pack_end(self.drive_button("Eject", drive, self.drives_tool.eject), False, False, 0)
            rows.pack_start(row, False, False, 0)
            self.disk_rows[d["device"]] = (free, meter)
        waiting = [d for d in usb.values() if not d[3]]      # plugged in, not mounted
        if waiting:
            plugged = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            for drive in waiting:
                row = Gtk.Box(spacing=10)
                glyph = label(GLYPH["usb"], "hf-sys-glyph", ellipsize=False)
                row.pack_start(glyph, False, False, 0)
                words = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
                words.set_valign(Gtk.Align.CENTER)
                words.pack_start(label(drive[1], "hf-sys-name"), False, False, 0)
                words.pack_start(label(f"{drive[2]} · not mounted", "hf-sys-sub"), False, False, 0)
                row.pack_start(words, True, True, 0)
                row.pack_end(self.drive_button("Mount", drive, self.drives_tool.mount), False, False, 0)
                plugged.pack_start(row, False, False, 0)
            self.add(line(), section("USB drives"), plugged, gap=0, into=self.disk_box)
        if info["idle"]:
            inside = [i for i in info["idle"] if i["tran"] != "usb"]
            if inside:
                names = ", ".join(f"{i['model'] or 'a drive'} ({hfsys.size(i['size'])})" for i in inside)
                idle = Gtk.Label(label=f"Not opened (inside the computer, never mounted from here): {names}",
                                 xalign=0, wrap=True, max_width_chars=48)
                idle.get_style_context().add_class("hf-sys-sub")
                self.add(line(), idle, gap=0, into=self.disk_box)
        self.disk_box.show_all()
        self._disk_update({})

    def drive_button(self, words: str, drive, action) -> Gtk.Button:
        b = Gtk.Button(label=words)
        b.set_valign(Gtk.Align.CENTER)
        b.set_tooltip_text(f"{words} {drive[1]}")

        def clicked(_b):
            b.set_sensitive(False)
            b.set_label("…")
            GLib.idle_add(lambda: (action(drive), self._disk_fill(), False)[2])
        b.connect("clicked", clicked)
        return b

    def _disk_update(self, _n: dict):
        if time.time() - self.disk_at < 10 and self.disk_at:
            return
        self.disk_at = time.time()
        disks = hfsys.disks(info={"parts": {}, "idle": []})
        main = next((d for d in self.disks if d["where"] == "/"), self.disks[0] if self.disks else None)
        for d in disks:
            row = self.disk_rows.get(d["device"])
            if not row:
                continue
            free, meter = row
            state = hfsys.level(d["percent"], *hfsys.FULL)
            free.set_label(f"{hfsys.size(d['free'])} free of {hfsys.size(d['total'])}")
            state_class(free, state)
            meter.set([(d["percent"] / 100, self.paint.of(state))])
            if main and d["device"] == main["device"]:
                self.sub.set_label(f"The system disk: {hfsys.size(d['used'])} used")
                self.big.set_label(f"{d['percent']:.0f} %")
                state_class(self.big, state)
        if not disks:
            self.sub.set_label("No disks to read")

    # ---- every two seconds
    def update(self) -> bool:
        n = self.sampler.now
        if self.part in ("cpu", "memory") and self.scan_at:
            now_scan, now_at = hfsys.proc_scan(), time.time()
            if now_at - self.scan_at > 0.3:
                self.top_cpu = hfsys.top_cpu(self.scan, now_scan, now_at - self.scan_at, max(len(n.get("cores") or []), 1))
            self.scan, self.scan_at = now_scan, now_at
        for u in self.updates:
            u(n)
        return True

    def tick(self) -> bool:
        state = hfsys.read_state()
        if hfsys.fresh(state, within=hfsys.EVERY * 1.5):
            self.sampler.now = state
        else:
            self.sampler.sample(with_gpu=self.part in ("gpu", "temp"))
        return self.update()


def drives_applet():
    """The USB drives applet (applets/drives/): its list, and its Eject and Mount — one place for those rules
    (only what was mounted for the desktop is ever ejected; internal drives are never mounted)."""
    import importlib.machinery
    import importlib.util
    path = panelkit.APPLETS / "drives/hypeforge-drives"
    try:
        loader = importlib.machinery.SourceFileLoader("hypeforge_drives", str(path))
        spec = importlib.util.spec_from_loader("hypeforge_drives", loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        return mod
    except Exception:
        return None


def build(look: panelkit.Look, args) -> panelkit.Panel:
    c = look.colour
    inner = 0 if look.straight else max(4, look.radius // 2)
    paint = Paint(look)
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(width=WIDTH, font=look.font, glyph=look.size * 1.9, big=look.size * 1.9,
                                       small=look.size * 0.86, accent=c["panel_tile_on"], dim=c["panel_text_dim"],
                                       text=c["panel_text"], warm=paint.warm, danger=c["panel_danger"],
                                       tile=c["panel_tile"], inner=inner, line=c["panel_border"],
                                       hover=c["panel_hover"]).encode())
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
    part = args.part or "cpu"
    ref = {}
    view = View(look, part, lambda: ref["p"].close())
    edges = args.edges.split(",") if getattr(args, "edges", None) else ["top", "right"]
    margins = dict(m.split("=") for m in args.margin.split(",")) if getattr(args, "margin", None) else {"top": 56, "right": 10}
    if part == "temp":
        view.root.set_size_request(WIDTH * 2, -1)
    panel = panelkit.Panel(f"system-{part}", view.root, look, edges=edges, margins={k: int(v) for k, v in margins.items()})
    ref["p"] = panel
    def first():                       # the processor's busiest apps need a second look soon
        view.tick()
        GLib.timeout_add(TICK, view.tick)
        return False

    GLib.timeout_add(700 if part == "cpu" else TICK, first)
    return panel
