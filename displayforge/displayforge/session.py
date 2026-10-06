"""displayForge · the session: the screens as they are, your changes, and what Identify remembers.

The app's screens read and change only this. Nothing reaches Sway until a change is tried
(trial.py, with the countdown) and nothing reaches a file until it is saved (saving.py).
"""

from __future__ import annotations

from dataclasses import replace

from . import brightness as B, screens as S, saving as V

PLACES = {0: "left", 1: "middle", 2: "right"}


class Session:
    def __init__(self, live: list[S.Screen], remembered: dict | None = None, *, main: str | None = None):
        self.live = list(live)                      # what Sway shows now
        self.pending = list(live)                   # with your changes
        self.at_save = list(live)                   # as of the last save (or the start)
        self.saved_once = False
        self.remembered = remembered if remembered is not None else {"names": {}, "bus": {}}
        self.main = main or (self.live[0].name if self.live else "")

    @classmethod
    def load(cls) -> "Session":
        return cls(S.read(), B.load(), main=main_screen())

    # -- reading ---------------------------------------------------------------------------------
    def reload(self) -> None:
        """Read Sway again; changes not yet tried are kept where the screen still exists."""
        fresh = S.read()
        mine = {s.name: s for s in self.pending}
        old = {s.name: s for s in self.live}
        self.live = fresh
        self.pending = [mine[s.name] if s.name in mine and mine[s.name] != old.get(s.name) else s
                        for s in fresh]

    def screen(self, name: str, pending: bool = True) -> S.Screen:
        return next(s for s in (self.pending if pending else self.live) if s.name == name)

    def number(self, name: str) -> int:
        """Screen numbers as the workspaces count them: the main one is 1, then Sway's order."""
        names = [self.main] + [s.name for s in self.live if s.name != self.main]
        return names.index(name) + 1 if name in names else 0

    def label(self, name: str) -> str:
        n = self.remembered["names"].get(name)
        return f"Screen {self.number(name)}" + (f" · {n}" if n else f" · {name}")

    def place_words(self, name: str, pending: bool = True) -> str:
        """left / middle / right … by position, for one row of screens; otherwise "x, y".
        `pending=False`: where the screens physically are now (Identify, Brightness)."""
        on = sorted((s for s in (self.pending if pending else self.live) if s.on), key=lambda s: (s.y, s.x))
        if on and all(s.y == on[0].y for s in on) and len(on) <= 3:
            order = [s.name for s in sorted(on, key=lambda s: s.x)]
            if name in order:
                return PLACES[order.index(name)] if len(order) == 3 else (
                    ["left", "right"][order.index(name)] if len(order) == 2 else "")
        s = self.screen(name, pending)
        return f"at {s.x}, {s.y}"

    # -- changing --------------------------------------------------------------------------------
    def change(self, name: str, **fields) -> None:
        self.pending = [replace(s, **fields) if s.name == name else s for s in self.pending]

    def arrange(self, name: str, where: str, of: str, align: str = "start") -> None:
        self.pending = S.place(self.pending, name, where, of, align)

    def discard(self) -> None:
        self.pending = list(self.live)

    @property
    def untried(self) -> list[str]:
        return S.all_commands(self.live, self.pending)

    @property
    def change_count(self) -> int:
        return len(self.changes())

    def to_save(self) -> list[tuple[str, str, str]]:
        """What a save would change: on screen now, against the last save."""
        return self.changes(self.at_save, self.live)

    def saved(self) -> None:
        self.at_save = list(self.live)

    def changes(self, before: list[S.Screen] | None = None, after: list[S.Screen] | None = None
                ) -> list[tuple[str, str, str]]:
        """(what, before, after) in plain words: by default your untried changes; the save review
        passes what was last saved and what is on screen now."""
        out = []
        old = {s.name: s for s in (self.live if before is None else before)}
        for s in (self.pending if after is None else after):
            o = old.get(s.name)
            if not o:
                continue
            who = self.label(s.name)
            if o.on != s.on:
                out.append((f"{who} · on", "on" if o.on else "off", "on" if s.on else "off"))
            if s.on and o.mode and s.mode and (o.mode.width, o.mode.height) != (s.mode.width, s.mode.height):
                out.append((f"{who} · resolution", o.mode.size, s.mode.size))
            if s.on and o.mode and s.mode and o.mode.hz != s.mode.hz:
                out.append((f"{who} · refresh rate", f"{o.mode.hz} Hz", f"{s.mode.hz} Hz"))
            if o.scale != s.scale:
                out.append((f"{who} · size of things", f"{o.scale:.0%}", f"{s.scale:.0%}"))
            if o.rotation != s.rotation:
                out.append((f"{who} · rotation", rotation_words(o.rotation), rotation_words(s.rotation)))
            if (o.x, o.y) != (s.x, s.y):
                out.append((f"{who} · position", f"{o.x}, {o.y}", f"{s.x}, {s.y}"))
            if o.adaptive_sync != s.adaptive_sync:
                out.append((f"{who} · smooth motion", "on" if o.adaptive_sync else "off",
                            "on" if s.adaptive_sync else "off"))
            if o.hdr != s.hdr:
                out.append((f"{who} · HDR", "on" if o.hdr else "off", "on" if s.hdr else "off"))
        return out

    def tried(self) -> None:
        """A trial was kept: what is on screen is now the pending state."""
        self.live = list(self.pending)

    # -- saving ----------------------------------------------------------------------------------
    def saved_differs(self) -> bool:
        """Do the saved settings differ from what is on screen?"""
        if not V.OUTPUTS.exists():
            return False
        saved = [l for l in V.OUTPUTS.read_text().splitlines() if l.startswith("output ")]
        return saved != S.config_lines(self.live)

    def problems(self) -> list[str]:
        p = []
        if not any(s.on for s in self.pending):
            p.append("At least one screen has to stay on.")
        clash = S.overlaps(self.pending)
        if clash:
            p.append("These screens overlap: " + ", ".join(f"{self.label(a)} and {self.label(b)}"
                                                          for a, b in clash) + ".")
        return p


def rotation_words(r: str) -> str:
    return {"normal": "normal", "90": "90°", "180": "180°", "270": "270°"}.get(r, r)


def main_screen() -> str | None:
    """The screen the workspaces start on: the first in hypeForge's workspaces settings."""
    import tomllib
    from pathlib import Path
    import os
    p = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "hypeforge/applets/workspaces.toml"
    try:
        with open(p, "rb") as f:
            screens = tomllib.load(f).get("screens", [])
        return screens[0] if screens else None
    except (OSError, tomllib.TOMLDecodeError):
        return None
