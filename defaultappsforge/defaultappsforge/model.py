"""What is saved, what you changed, the words for the review, and what a save writes.

The truth for "which app opens what" is the standard file (system.MimeApps) and, for the terminal,
xdg-terminal-exec's list. Which file types belong to which default app (File Types, D-2) is
defaultappsForge's own small file. A save writes only what changed.
"""

from __future__ import annotations

import copy
import os
import tomllib
from pathlib import Path

from . import system as S
from .roles import BY_KEY, FILE_TYPES, ROLES, default_pools

POOLS = S.CONFIG_HOME / "defaultappsforge/settings.toml"
NONE = None


class Session:
    def __init__(self, apps: dict[str, S.App] | None = None, mimeapps: S.MimeApps | None = None,
                 pools_path: Path = POOLS, terminals: Path = S.TERMINALS, ask_system=S.system_default) -> None:
        self.apps = apps if apps is not None else S.installed()
        self.mime = mimeapps or S.MimeApps()
        self.pools_path, self.terminals, self.ask_system = pools_path, terminals, ask_system
        self.saved_apps = {r.key: self._current(r.key) for r in ROLES}
        self.saved_pools = self._load_pools()
        self.apps_now = dict(self.saved_apps)
        self.pools = copy.deepcopy(self.saved_pools)

    # -- reading ------------------------------------------------------------------------------------
    def _load_pools(self) -> dict[str, list[str]]:
        try:
            with open(self.pools_path, "rb") as f:
                data = tomllib.load(f).get("pools", {})
        except (OSError, tomllib.TOMLDecodeError):
            return default_pools()
        pools = {r.key: [e for e in data.get(r.key, []) if e in FILE_TYPES] for r in ROLES}
        seen: set[str] = set()
        for k in pools:                                   # one file type, one default app
            pools[k] = [e for e in pools[k] if not (e in seen or seen.add(e))]
        return pools

    def _current(self, key: str) -> str | None:
        role = BY_KEY[key]
        if key == "terminal":
            return S.terminal_now(self.terminals, self.apps)
        chosen = self.mime.get(S.DEFAULTS)
        for t in role.main:
            for d in chosen.get(t, []):
                if d in self.apps:
                    return d
        for t in role.main[:1]:
            d = self.ask_system(t)
            if d in self.apps:
                return d
        return None

    def candidates(self, key: str) -> list[S.App]:
        """Only the apps that can do this job (their desktop entry says so)."""
        role = BY_KEY[key]
        out = [a for a in self.apps.values()
               if (role.category and role.category in a.categories) or (a.types & set(role.main))]
        for d in (self.saved_apps.get(key), self.apps_now.get(key)):
            if d and d in self.apps and self.apps[d] not in out:
                out.append(self.apps[d])          # what opens it now is always offered (Pinta declares no PNG)
        return sorted(out, key=lambda a: a.name.lower())

    def label(self, app: S.App, among: list[S.App]) -> str:
        """The app's name; with its launcher id when two share a name (two Google Chrome entries)."""
        if sum(1 for a in among if a.name == app.name) > 1:
            return f"{app.name} · {app.id.removesuffix('.desktop')}"
        return app.name

    def name(self, desktop_id: str | None) -> str:
        if not desktop_id:
            return "none"
        a = self.apps.get(desktop_id)
        return a.name if a else desktop_id.removesuffix(".desktop")

    def unassigned(self) -> list[str]:
        """The common file types on no default app (File Types' left table)."""
        taken = {e for p in self.pools.values() for e in p}
        return sorted(e for e in FILE_TYPES if e not in taken)

    # -- edits ----------------------------------------------------------------------------------------
    def choose(self, key: str, desktop_id: str | None) -> None:
        self.apps_now[key] = desktop_id

    def assign(self, exts: list[str], key: str) -> None:
        for k in self.pools:
            self.pools[k] = [e for e in self.pools[k] if e not in exts]
        self.pools[key] += [e for e in exts if e in FILE_TYPES]

    def clear(self, exts: list[str], key: str) -> None:
        self.pools[key] = [e for e in self.pools[key] if e not in exts]

    def discard(self) -> None:
        self.apps_now = dict(self.saved_apps)
        self.pools = copy.deepcopy(self.saved_pools)

    # -- the changes, in words ----------------------------------------------------------------------------
    def changes(self) -> list[tuple[str, str, str]]:
        rows = []
        for r in ROLES:
            if self.apps_now[r.key] != self.saved_apps[r.key]:
                rows.append((r.title, self.name(self.saved_apps[r.key]), self.name(self.apps_now[r.key])))
        before = {e: k for k, p in self.saved_pools.items() for e in p}
        after = {e: k for k, p in self.pools.items() for e in p}
        for e in sorted(set(before) | set(after)):
            if before.get(e) != after.get(e):
                b = BY_KEY[before[e]].title if e in before else "no default app"
                a = BY_KEY[after[e]].title if e in after else "no default app"
                rows.append((f"File type {e}", b, a))
        if rows:
            gone = sorted({d for _s, _k, d in self.mime.gone(self.apps)})
            if gone:
                rows.append(("Old choices tidied", ", ".join(d.removesuffix(".desktop") for d in gone),
                             "removed (apps gone)"))
        return rows

    @property
    def change_count(self) -> int:
        return len([r for r in self.changes() if r[0] != "Old choices tidied"])

    @property
    def terminal_changed(self) -> bool:
        return self.apps_now["terminal"] != self.saved_apps["terminal"]

    # -- saving --------------------------------------------------------------------------------------
    def plan(self) -> dict[str, list[str] | None]:
        """{MIME type: [desktop id] to set, or None to remove} — only what changed."""
        out: dict[str, list[str] | None] = {}
        for r in ROLES:
            if r.key == "terminal":
                continue
            app = self.apps_now[r.key]
            role_changed = app != self.saved_apps[r.key]
            exts = self.pools[r.key]
            new_exts = [e for e in exts if e not in self.saved_pools[r.key]]
            if app and role_changed:
                for t in r.main:
                    out[t] = [app]
                for e in exts:
                    out[FILE_TYPES[e][1]] = [app]
            elif app:
                for e in new_exts:
                    out[FILE_TYPES[e][1]] = [app]
        keep = {t for r in ROLES for t in r.main} | {FILE_TYPES[e][1] for p in self.pools.values() for e in p}
        for k, p in self.saved_pools.items():
            for e in p:
                mime = FILE_TYPES[e][1]
                if not any(e in q for q in self.pools.values()) and mime not in keep and mime not in out:
                    out[mime] = None                          # << : back to the system's guess
        return out

    def save(self, backups: Path = S.BACKUPS) -> dict:
        """Write what changed (backups first); then what is saved is what you see."""
        result = {"backup": None, "tidied": [], "terminal": None}
        plan = self.plan()
        result["tidied"] = self.mime.tidy(self.apps)
        for mime, apps in plan.items():
            self.mime.set(S.DEFAULTS, mime, apps)
        if plan or result["tidied"]:
            result["backup"] = self.mime.write(backups)
        if self.terminal_changed and self.apps_now["terminal"]:
            result["terminal"] = S.write_terminal(self.apps_now["terminal"], self.terminals, backups)
        self._write_pools()
        self.saved_apps = dict(self.apps_now)
        self.saved_pools = copy.deepcopy(self.pools)
        return result

    def _write_pools(self) -> None:
        lines = ["# defaultappsForge — which file types belong to which default app (File Types).",
                 "# Which app each default app is lives in ~/.config/mimeapps.list, the standard file.", "", "[pools]"]
        for r in ROLES:
            lines.append(f'{r.key} = [{", ".join(repr(e).replace(chr(39), chr(34)) for e in self.pools[r.key])}]')
        self.pools_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.pools_path.with_name(self.pools_path.name + ".tmp")
        tmp.write_text("\n".join(lines) + "\n")
        os.replace(tmp, self.pools_path)
