"""Talking to the running desktop: which windows are open where, carrying them over when the
workspaces change, and asking hypeForge's Workspaces applet to read its file again.

Only Sway's own `swaymsg` and the applet's running-copy file (its pid) are used; never the
applet's code (hypeForge D-59). Outside Sway everything here quietly does nothing.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
from pathlib import Path

PIDFILE = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "hypeforge-workspaces.pid"


class Live:
    def __init__(self, swaymsg: str = "swaymsg", pidfile: Path = PIDFILE) -> None:
        self.swaymsg, self.pidfile = swaymsg, pidfile

    @property
    def here(self) -> bool:
        return bool(os.environ.get("SWAYSOCK"))

    def _msg(self, *args: str) -> tuple[bool, object]:
        if not self.here:
            return False, None
        try:
            r = subprocess.run([self.swaymsg, *args], capture_output=True, text=True, timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            return False, None
        try:
            return r.returncode == 0, json.loads(r.stdout or "null")
        except json.JSONDecodeError:
            return r.returncode == 0, None

    def windows(self) -> dict[str, list[str]]:
        """{Sway workspace name: [window names]} for every open window."""
        ok, tree = self._msg("-t", "get_tree")
        out: dict[str, list[str]] = {}
        if not ok or not isinstance(tree, dict):
            return out

        def walk(node: dict, ws: str | None) -> None:
            if node.get("type") == "workspace":
                ws = node.get("name")
            if node.get("pid") and node.get("type") in ("con", "floating_con") and ws:
                props = node.get("window_properties") or {}
                label = node.get("app_id") or props.get("class") or node.get("name") or "a window"
                out.setdefault(ws, []).append(str(label))
            for child in node.get("nodes", []) + node.get("floating_nodes", []):
                walk(child, ws)
        walk(tree, None)
        return out

    def run(self, commands: list[str]) -> list[bool]:
        """Each Sway command on its own; whether each worked (a rename of a workspace that has no
        windows, so Sway does not keep it, fails harmlessly)."""
        results = []
        for c in commands:
            ok, reply = self._msg(c)
            results.append(bool(ok and isinstance(reply, list) and all(x.get("success") for x in reply)))
        return results

    def reload_applet(self) -> bool:
        """Ask the Workspaces applet to read its file again (what `hypeforge-workspaces reload`
        does). False when it isn't running: the new settings then apply at the next login."""
        try:
            pid = int(self.pidfile.read_text())
            os.kill(pid, signal.SIGHUP)
            return True
        except (OSError, ValueError):
            return False


class NoDesktop(Live):
    """For tests and for running outside Sway: nothing open, nothing to move, nothing to reload."""

    def __init__(self) -> None:
        super().__init__()
        self.commands: list[str] = []
        self.reloaded = 0
        self.open: dict[str, list[str]] = {}

    @property
    def here(self) -> bool:
        return False

    def windows(self) -> dict[str, list[str]]:
        return dict(self.open)

    def run(self, commands: list[str]) -> list[bool]:
        self.commands += commands
        return [True] * len(commands)

    def reload_applet(self) -> bool:
        self.reloaded += 1
        return True
