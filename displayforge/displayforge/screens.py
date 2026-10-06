"""displayForge · the screens Sway knows, and the commands that change them.

Plain Python, no Textual: the screens are read from `swaymsg -t get_outputs` (or a saved copy
of it, for tests), and every change becomes exact `swaymsg output …` commands. Nothing here
applies anything — trial.py does, with the countdown.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field, replace

# Sizes the Settings form offers (D-2: 80 and 90 % added; fractional sizes blur X11 apps)
SCALES = (0.8, 0.9, 1.0, 1.25, 1.5, 2.0)
ROTATIONS = ("normal", "90", "180", "270")


@dataclass(frozen=True)
class Mode:
    width: int
    height: int
    refresh: int  # mHz, as Sway reports it (144000 = 144 Hz)

    @property
    def hz(self) -> int:
        return round(self.refresh / 1000)

    @property
    def size(self) -> str:
        return f"{self.width} × {self.height}"

    def command(self) -> str:
        # Sway takes the rate in Hz with up to three decimals
        return f"{self.width}x{self.height}@{self.refresh / 1000:.3f}Hz"


@dataclass(frozen=True)
class Screen:
    name: str                 # the connector, e.g. "DP-3" — Sway's own name for it
    make: str
    model: str
    serial: str
    on: bool
    mode: Mode | None         # None when the screen is switched off
    x: int
    y: int
    scale: float
    rotation: str             # "normal", "90", "180", "270" (Sway may add "flipped-…")
    adaptive_sync: bool
    can_adaptive_sync: bool
    hdr: bool
    can_hdr: bool
    modes: tuple[Mode, ...] = field(default_factory=tuple)

    # -- what the form offers: only what the screen really reports (D-2) --
    def sizes(self) -> list[tuple[int, int]]:
        seen = []
        for m in sorted(self.modes, key=lambda m: (m.width * m.height, m.width), reverse=True):
            if (m.width, m.height) not in seen:
                seen.append((m.width, m.height))
        return seen

    def rates(self, width: int, height: int) -> list[Mode]:
        """The refresh rates the screen offers at one size, highest first, one per whole Hz."""
        best: dict[int, Mode] = {}
        for m in self.modes:
            if (m.width, m.height) == (width, height):
                if m.hz not in best or m.refresh > best[m.hz].refresh:
                    best[m.hz] = m
        return [best[h] for h in sorted(best, reverse=True)]

    @property
    def extent(self) -> tuple[int, int]:
        """How much room the screen takes in the layout (Sway's logical size)."""
        if not self.mode:
            return (0, 0)
        w, h = self.mode.width, self.mode.height
        if self.rotation in ("90", "270") or self.rotation.endswith(("90", "270")):
            w, h = h, w
        return (round(w / self.scale), round(h / self.scale))


def _mode(d: dict | None) -> Mode | None:
    if not d or not d.get("width"):
        return None
    return Mode(int(d["width"]), int(d["height"]), int(d.get("refresh", 0)))


def parse(outputs: list[dict]) -> list[Screen]:
    """Sway's get_outputs → Screens, in Sway's order. Non-desktop outputs (VR headsets) skipped."""
    screens = []
    for o in outputs:
        if o.get("non_desktop"):
            continue
        features = o.get("features") or {}
        rect = o.get("rect") or {}
        screens.append(Screen(
            name=o["name"], make=o.get("make", ""), model=o.get("model", ""), serial=o.get("serial", ""),
            on=bool(o.get("active")), mode=_mode(o.get("current_mode")) if o.get("active") else None,
            x=int(rect.get("x", 0)), y=int(rect.get("y", 0)),
            scale=float(o.get("scale") or 1.0), rotation=str(o.get("transform") or "normal"),
            adaptive_sync=o.get("adaptive_sync_status") == "enabled",
            can_adaptive_sync=bool(features.get("adaptive_sync")),
            hdr=bool(o.get("hdr")), can_hdr=bool(features.get("hdr")),
            modes=tuple(m for m in (_mode(x) for x in o.get("modes") or []) if m),
        ))
    return screens


def read() -> list[Screen]:
    out = subprocess.run(["swaymsg", "-r", "-t", "get_outputs"], capture_output=True, text=True, check=True)
    return parse(json.loads(out.stdout))


# -- changes -------------------------------------------------------------------------------------

def commands(before: Screen, after: Screen) -> list[str]:
    """The `output …` commands that turn `before` into `after` (only what changed)."""
    n = after.name
    if not after.on:
        return [] if not before.on else [f"output {n} disable"]
    cmds = []
    if not before.on:
        cmds.append(f"output {n} enable")
    if after.mode and after.mode != before.mode:
        cmds.append(f"output {n} mode {after.mode.command()}")
    if after.scale != before.scale:
        cmds.append(f"output {n} scale {after.scale:g}")
    if after.rotation != before.rotation:
        cmds.append(f"output {n} transform {after.rotation}")
    if (after.x, after.y) != (before.x, before.y):
        cmds.append(f"output {n} position {after.x} {after.y}")
    if after.adaptive_sync != before.adaptive_sync and after.can_adaptive_sync:
        cmds.append(f"output {n} adaptive_sync {'on' if after.adaptive_sync else 'off'}")
    if after.hdr != before.hdr and after.can_hdr:
        cmds.append(f"output {n} hdr {'on' if after.hdr else 'off'}")
    return cmds


def all_commands(before: list[Screen], after: list[Screen]) -> list[str]:
    old = {s.name: s for s in before}
    out = []
    for s in after:
        out += commands(old.get(s.name, s), s)
    return out


def config_lines(screens: list[Screen]) -> list[str]:
    """What the outputs file holds: one full description per screen, so a login rebuilds it all."""
    lines = []
    for s in screens:
        if not s.on:
            lines.append(f"output {s.name} disable")
            continue
        parts = [f"output {s.name}"]
        if s.mode:
            parts.append(f"mode {s.mode.command()}")
        parts += [f"position {s.x} {s.y}", f"scale {s.scale:g}", f"transform {s.rotation}"]
        if s.can_adaptive_sync:
            parts.append(f"adaptive_sync {'on' if s.adaptive_sync else 'off'}")
        if s.can_hdr:
            parts.append(f"hdr {'on' if s.hdr else 'off'}")
        lines.append(" ".join(parts))
    return lines


# -- the layout ----------------------------------------------------------------------------------

def overlaps(screens: list[Screen]) -> list[tuple[str, str]]:
    """Pairs of switched-on screens that cover the same space."""
    on = [s for s in screens if s.on]
    bad = []
    for i, a in enumerate(on):
        aw, ah = a.extent
        for b in on[i + 1:]:
            bw, bh = b.extent
            if a.x < b.x + bw and b.x < a.x + aw and a.y < b.y + bh and b.y < a.y + ah:
                bad.append((a.name, b.name))
    return bad


def place(screens: list[Screen], name: str, where: str, of: str, align: str = "start") -> list[Screen]:
    """Put screen `name` left of / right of / above / below screen `of`, edges touching (snapped).
    `align`: "start" (tops / left edges), "centre", "end"."""
    by = {s.name: s for s in screens}
    me, ref = by[name], by[of]
    mw, mh = me.extent
    rw, rh = ref.extent
    if where in ("left", "right"):
        x = ref.x - mw if where == "left" else ref.x + rw
        y = ref.y + {"start": 0, "centre": (rh - mh) // 2, "end": rh - mh}[align]
    else:
        y = ref.y - mh if where == "above" else ref.y + rh
        x = ref.x + {"start": 0, "centre": (rw - mw) // 2, "end": rw - mw}[align]
    moved = [replace(s, x=x, y=y) if s.name == name else s for s in screens]
    return normalise(make_room(moved, name, where))


def make_room(screens: list[Screen], moved: str, where: str) -> list[Screen]:
    """The others make room (the design): a screen the moved one now covers slides on in the same
    direction until it touches the far edge — and so on down the line, so nothing overlaps."""
    order = {"right": (1, 0), "left": (-1, 0), "below": (0, 1), "above": (0, -1)}
    dx, dy = order[where]
    by = {s.name: s for s in screens}
    pushers = [moved]
    for _ in range(len(screens) * len(screens)):  # bounded: each pass settles at least one screen
        if not pushers:
            break
        p = by[pushers.pop(0)]
        pw, ph = p.extent
        for other in list(by.values()):
            if other.name == p.name or not other.on:
                continue
            ow, oh = other.extent
            if p.x < other.x + ow and other.x < p.x + pw and p.y < other.y + oh and other.y < p.y + ph:
                if dx:
                    nx = p.x + pw if dx > 0 else p.x - ow
                    by[other.name] = replace(other, x=nx)
                else:
                    ny = p.y + ph if dy > 0 else p.y - oh
                    by[other.name] = replace(other, y=ny)
                pushers.append(other.name)
    return [by[s.name] for s in screens]


def normalise(screens: list[Screen]) -> list[Screen]:
    """Shift everything so the layout starts at 0, 0 (Sway is happiest that way)."""
    on = [s for s in screens if s.on]
    if not on:
        return screens
    dx, dy = min(s.x for s in on), min(s.y for s in on)
    return [replace(s, x=s.x - dx, y=s.y - dy) if s.on else s for s in screens]
