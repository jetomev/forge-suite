"""workspaceForge's settings: what is saved, what you changed, and how to write it back.

The file is hypeForge's Workspaces applet's own (`~/.config/hypeforge/applets/workspaces.toml`);
workspaceForge reads and writes that file and never the applet's code (hypeForge D-59). Each
workspace keeps an identity (`uid`) through renames, moves and deletes, so the changes can be said
in words and the open windows can follow their workspace when it is saved.
"""

from __future__ import annotations

import copy
import os
import shutil
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "hypeforge/applets/workspaces.toml"
BACKUPS = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "workspaceforge/backups"
KEEP_BACKUPS = 20
# Win + 1 … 9 reach nine; the applet's way of naming each screen's part of a workspace
# ("<n + 10 × screen>:<name>") also stops at nine, so 0.1.0 does too (workspaceForge TODO).
MOST = 9


class Problem(ValueError):
    """An edit that can't be made, said in plain words."""


@dataclass
class Workspace:
    uid: int
    name: str
    apps: list[str] = field(default_factory=list)


@dataclass
class Settings:
    enabled: bool = True
    screens: list[str] = field(default_factory=list)
    workspaces: list[Workspace] = field(default_factory=list)
    shared: dict[str, set[int]] = field(default_factory=dict)   # screen -> uids sharing its space
    extra_share_groups: dict[str, int] = field(default_factory=dict)  # screens with groups we can't show

    # -- reading -----------------------------------------------------------------------------------
    @classmethod
    def load(cls, path: Path = CONFIG) -> "Settings":
        try:
            with open(path, "rb") as f:
                cfg = tomllib.load(f)
        except FileNotFoundError:
            cfg = {}
        s = cls(enabled=bool(cfg.get("enabled", True)), screens=[str(x) for x in cfg.get("screens", [])])
        for i, w in enumerate(cfg.get("workspace", [])):
            s.workspaces.append(Workspace(i + 1, str(w.get("name", f"Workspace {i + 1}")),
                                          [str(a) for a in w.get("apps", [])]))
        by_name = {w.name: w.uid for w in s.workspaces}
        for screen, groups in cfg.get("share", {}).items():
            groups = [[n for n in g if n in by_name] for g in groups]
            groups = [g for g in groups if len(g) > 1]
            if groups:
                s.shared[screen] = {by_name[n] for n in groups[0]}  # one group per screen (D-5)
                if len(groups) > 1:
                    s.extra_share_groups[screen] = len(groups)
        return s

    # -- looking up ----------------------------------------------------------------------------------
    def index(self, uid: int) -> int:
        """1, 2, … — the Win key that reaches it."""
        return next(i for i, w in enumerate(self.workspaces, 1) if w.uid == uid)

    def get(self, uid: int) -> Workspace:
        return next(w for w in self.workspaces if w.uid == uid)

    def has(self, uid: int) -> bool:
        return any(w.uid == uid for w in self.workspaces)

    def where(self, app_id: str) -> int | None:
        """The uid of the workspace that lists this app, or None (it opens where you are)."""
        return next((w.uid for w in self.workspaces if app_id in w.apps), None)

    def cell(self, uid: int, screen: str) -> str:
        """The name Sway knows this workspace by on that screen (the applet's naming)."""
        p = self.screens.index(screen)
        if len(self.shared.get(screen, ())) > 1 and uid in self.shared[screen]:
            return f"{100 + 10 * p + 1}:Shared"
        return f"{self.index(uid) + 10 * p}:{self.get(uid).name}"

    def is_shared(self, uid: int, screen: str) -> bool:
        return len(self.shared.get(screen, ())) > 1 and uid in self.shared[screen]

    # -- writing -------------------------------------------------------------------------------------
    def to_toml(self) -> str:
        def q(s: str) -> str:
            return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
        out = [
            "# hypeForge applet 1 · Workspaces Management (D-47) — written by workspaceForge.",
            "#",
            "# Workspaces that span all your screens: switching one switches every screen together.",
            "# Change it in workspaceForge (or by hand, then `hypeforge-workspaces reload`).",
            "",
            "# false = the applet does nothing and Sway keeps its own one-screen workspaces.",
            f"enabled = {'true' if self.enabled else 'false'}",
            "",
            "# The screens in order: the first is screen 1 (the main one), as Sway names them.",
            "screens = [" + ", ".join(q(s) for s in self.screens) + "]",
            "",
            "# One block per workspace, in order: the first is Win + 1, the second Win + 2, …",
            "# apps: the apps that open on it however they are started (their launcher names).",
            "# One app, one workspace; an app on no list opens where you are.",
        ]
        for w in self.workspaces:
            out += ["", "[[workspace]]", f"name = {q(w.name)}"]
            if w.apps:
                out.append("apps = [")
                out += [f"  {q(a)}," for a in w.apps]
                out.append("]")
            else:
                out.append("apps = []")
        out += ["", "# Sharing: a screen keeps the same apps in the workspaces listed for it.", "[share]"]
        for screen in self.screens:
            names = [w.name for w in self.workspaces if w.uid in self.shared.get(screen, set())]
            group = "[" + ", ".join(q(n) for n in names) + "]" if len(names) > 1 else ""
            out.append(f"{q(screen)} = [{group}]")
        return "\n".join(out) + "\n"


def check_name(name: str, others: list[str]) -> str:
    """A clean name, or a Problem saying why not."""
    name = " ".join(name.split())
    if not name:
        raise Problem("A workspace needs a name.")
    if len(name) > 30:
        raise Problem("Keep the name to 30 letters or fewer: it has to fit the bar.")
    if any(c in name for c in '"\\'):
        raise Problem("A name can't have quotes or backslashes in it.")
    if name.lower() in (o.lower() for o in others):
        raise Problem(f"There is already a workspace called {name}.")
    return name


class Session:
    """What is saved (`saved`) and what you have changed (`pending`), and the words for it."""

    def __init__(self, settings: Settings, path: Path = CONFIG) -> None:
        self.path = path
        self.saved = settings
        self.pending = copy.deepcopy(settings)
        self.moved_to: dict[int, int] = {}       # a deleted workspace's uid -> where its windows go
        self._next = max((w.uid for w in settings.workspaces), default=0) + 1

    @classmethod
    def load(cls, path: Path = CONFIG) -> "Session":
        return cls(Settings.load(path), path)

    # -- edits -----------------------------------------------------------------------------------------
    def add(self, name: str, after: int | None) -> int:
        p = self.pending
        if len(p.workspaces) >= MOST:
            raise Problem(f"{MOST} workspaces is the most for now: Win + 1 … {MOST} reach them.")
        name = check_name(name, [w.name for w in p.workspaces])
        uid, self._next = self._next, self._next + 1
        at = len(p.workspaces) if after is None else p.index(after)
        p.workspaces.insert(at, Workspace(uid, name))
        return uid

    def rename(self, uid: int, name: str) -> str:
        p = self.pending
        name = check_name(name, [w.name for w in p.workspaces if w.uid != uid])
        p.get(uid).name = name
        return name

    def delete(self, uid: int, move_to: int) -> None:
        p = self.pending
        if len(p.workspaces) <= 1:
            raise Problem("One workspace always stays. Rename it instead.")
        if move_to == uid or not p.has(move_to):
            raise Problem("Pick another workspace for its windows.")
        p.workspaces = [w for w in p.workspaces if w.uid != uid]
        for group in p.shared.values():
            group.discard(uid)
        for old, target in list(self.moved_to.items()):   # windows already headed here go on
            if target == uid:
                self.moved_to[old] = move_to
        if self.saved.has(uid):
            self.moved_to[uid] = move_to

    def move(self, uid: int, step: int) -> None:
        ws = self.pending.workspaces
        i = self.pending.index(uid) - 1
        j = i + step
        if 0 <= j < len(ws):
            ws[i], ws[j] = ws[j], ws[i]

    def set_enabled(self, value: bool) -> None:
        self.pending.enabled = value

    def assign(self, app_ids: list[str], uid: int) -> None:
        """Into this workspace's list; off any other (one app, one workspace)."""
        for w in self.pending.workspaces:
            w.apps = [a for a in w.apps if a not in app_ids]
        self.pending.get(uid).apps += [a for a in app_ids]

    def unassign(self, app_ids: list[str], uid: int) -> None:
        w = self.pending.get(uid)
        w.apps = [a for a in w.apps if a not in app_ids]

    def set_shared(self, screen: str, uid: int, value: bool) -> None:
        group = self.pending.shared.setdefault(screen, set())
        (group.add if value else group.discard)(uid)

    def discard(self) -> None:
        self.pending = copy.deepcopy(self.saved)
        self.moved_to = {}

    # -- the changes, in words ----------------------------------------------------------------------
    def changes(self, app_names: dict[str, str] | None = None,
                screen_names: dict[str, str] | None = None) -> list[tuple[str, str, str]]:
        """(what, before, after) — the review before saving, and the count on the bar."""
        names = app_names or {}
        screens = screen_names or {}
        s, p = self.saved, self.pending
        rows: list[tuple[str, str, str]] = []
        if s.enabled != p.enabled:
            rows.append(("Across all screens", "on" if s.enabled else "off", "on" if p.enabled else "off"))
        for w in p.workspaces:
            if not s.has(w.uid):
                rows.append(("New workspace", "—", f"{p.index(w.uid)} · {w.name}"))
            elif s.get(w.uid).name != w.name:
                rows.append((f"Workspace {p.index(w.uid)} · name", s.get(w.uid).name, w.name))
        for w in s.workspaces:
            if not p.has(w.uid):
                to = self.moved_to.get(w.uid)
                rows.append((f"Deleted · {w.name}", f"Win + {s.index(w.uid)}",
                             f"its windows to {p.get(to).name}" if to and p.has(to) else "deleted"))
        kept = [w.uid for w in s.workspaces if p.has(w.uid)]
        if [u for u in (w.uid for w in p.workspaces) if s.has(u)] != kept:
            rows.append(("Order", ", ".join(w.name for w in s.workspaces if p.has(w.uid)),
                         ", ".join(w.name for w in p.workspaces if s.has(w.uid))))
        every = sorted({a for w in s.workspaces + p.workspaces for a in w.apps}, key=lambda a: names.get(a, a).lower())
        for a in every:
            before, after = s.where(a), p.where(a)
            b = s.get(before).name if before is not None else "where you are"
            n = p.get(after).name if after is not None else "where you are"
            if before != after:                  # a renamed workspace keeps its apps: no change
                rows.append((f"App · {names.get(a, a)}", b, n))
        for screen in p.screens:
            def words(st: Settings) -> str:
                group = [w.name for w in st.workspaces if w.uid in st.shared.get(screen, set())]
                return ", ".join(group) if len(group) > 1 else "not shared"
            if words(s) != words(p):
                rows.append((f"Sharing · {screens.get(screen, screen)}", words(s), words(p)))
        return rows

    @property
    def change_count(self) -> int:
        return len(self.changes())

    # -- the open windows follow their workspace -------------------------------------------------------
    def window_moves(self) -> list[tuple[str, str]]:
        """Sway commands (and what each is for) that carry the open windows over to the new names
        and places, before the applet re-reads the file: every kept workspace's part of each screen
        is renamed through a temporary name (so two can swap), a deleted one's windows go to the
        workspace you chose. Shared spaces are left to the applet, which already hands them over."""
        s, p = self.saved, self.pending
        if not s.enabled or not p.enabled or s.screens != p.screens:
            return []
        holds: list[tuple[str, str]] = []
        moves: list[tuple[str, str]] = []
        finals: list[tuple[str, str]] = []
        for screen in s.screens:
            p_ = s.screens.index(screen)
            for w in s.workspaces:
                if s.is_shared(w.uid, screen) or (p.has(w.uid) and p.is_shared(w.uid, screen)):
                    continue                     # shared spaces: the applet hands them over itself
                old = s.cell(w.uid, screen)
                if p.has(w.uid):
                    new = p.cell(w.uid, screen)
                    if new != old:
                        tmp = f"wf-{w.uid}-{p_}"
                        holds.append((f"rename workspace {_q(old)} to {_q(tmp)}", f"{old} (hold)"))
                        finals.append((f"rename workspace {_q(tmp)} to {_q(new)}", f"→ {new}"))
                else:
                    to = self.moved_to.get(w.uid)
                    if to is None or not p.has(to):
                        continue
                    target = p.cell(to, screen)
                    if s.has(to) and not s.is_shared(to, screen) and s.cell(to, screen) != target:
                        target = f"wf-{to}-{p_}"   # held under its temporary name until the end
                    moves.append((f'[workspace="^{_re(old)}$"] move container to workspace {_q(target)}',
                                  f"{old} → {target}"))
        # every rename away first (so two can swap), then the deleted ones' windows, then the names
        steps = holds + moves + finals
        return steps

    # -- saving ----------------------------------------------------------------------------------------
    def write(self) -> Path | None:
        """Write the pending settings, a backup of the old file first (the last 20 kept). The
        written file must read back the same, or the old one is put back."""
        backup = None
        if self.path.exists():
            BACKUPS.mkdir(parents=True, exist_ok=True)
            backup = BACKUPS / f"workspaces.toml.{time.strftime('%Y%m%d-%H%M%S')}"
            n = 1
            while backup.exists():
                backup = BACKUPS / f"workspaces.toml.{time.strftime('%Y%m%d-%H%M%S')}-{n}"
                n += 1
            shutil.copy2(self.path, backup)
            for old in sorted(BACKUPS.glob("workspaces.toml.*"))[:-KEEP_BACKUPS]:
                old.unlink(missing_ok=True)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(self.pending.to_toml())
        back = Settings.load(tmp)
        same = (back.enabled == self.pending.enabled and back.screens == self.pending.screens
                and [(w.name, w.apps) for w in back.workspaces] == [(w.name, w.apps) for w in self.pending.workspaces])
        if not same:
            tmp.unlink(missing_ok=True)
            raise OSError("the new file did not read back the same; nothing was changed")
        os.replace(tmp, self.path)
        return backup

    def saved_now(self) -> None:
        """After a save: what was pending is what is saved; identities start over from the file."""
        self.saved = Settings.load(self.path)
        self.pending = copy.deepcopy(self.saved)
        self.moved_to = {}
        self._next = max((w.uid for w in self.saved.workspaces), default=0) + 1


def _q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _re(s: str) -> str:
    import re
    return re.escape(s).replace('"', '\\"')
