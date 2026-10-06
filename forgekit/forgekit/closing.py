"""The start and end of a run, printed in the terminal (v0.5.0).

Javier's rule (2026-10-02, from nog): every run starts with the app's version
and the run requested, and ends with what happened, where it was logged, and a
thank-you. A full-screen app's window disappears when it closes, so a Forge app
prints that record to the terminal after ``app.run()`` returns:

    print(session_banner("grubForge", "2.0.0", "grubforge", started, ended, user))
    print(closing_notice("Closed · saved, not rebuilt", [...], level="warn",
                         logs=[path], thanks="Thank you for using grubForge!"))

``runs_log_row`` appends one CSV line per run to a daily file, the same shape
nog uses (``YYYYMMDD <app>-runs.csv``), so the closing can always name a log.

Colours: 24-bit Catppuccin in a terminal window, the basic 8 on a text console,
none when ``NO_COLOR`` is set or the output is not a terminal.
"""

from __future__ import annotations

import csv
import datetime as _dt
import io
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from .console import console_mode
from .theme import COLORS

_ROLE_RGB = {"ok": COLORS["green"], "warn": COLORS["yellow"], "error": COLORS["red"],
             "info": COLORS["blue"], "title": COLORS["mauve"], "muted": COLORS["subtext"]}
_ROLE_BASIC = {"ok": "32", "warn": "33", "error": "31", "info": "36", "title": "35", "muted": "37"}


def _paint(text: str, role: str, bold: bool = False, *, enabled: bool | None = None) -> str:
    if enabled is None:
        enabled = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
    if not enabled:
        return text
    if console_mode():
        code = _ROLE_BASIC[role]
    else:
        h = _ROLE_RGB[role].lstrip("#")
        code = "38;2;{};{};{}".format(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    return f"\x1b[{'1;' if bold else ''}{code}m{text}\x1b[0m"


def session_banner(app: str, version: str, run: str, started: _dt.datetime,
                   ended: _dt.datetime | None = None, user: str | None = None,
                   *, color: bool | None = None) -> str:
    """The framed start of the record. Leading blank line included; no trailing one."""
    user = user or os.environ.get("USER") or os.environ.get("LOGNAME") or "unknown"
    heading = f"{app} v{version}  ·  Session"
    when = f"{started:%m/%d/%Y}   {started:%I:%M %p}"
    if ended:
        when += f"   →   {ended:%I:%M %p}"
    width = max(41, len(heading) + 4, len(run) + 11)
    rule = _paint("=" * width, "title", True, enabled=color)
    return "\n".join(["", rule, _paint(f"  {heading}", "title", True, enabled=color), rule,
                      f"  Run:   {run}", f"  Date:  {when}", f"  User:  {user}"])


def closing_notice(heading: str, lines: Sequence[str] = (), *, level: str = "ok",
                   logs: Sequence[str | Path] = (), thanks: str = "",
                   color: bool | None = None) -> str:
    """The designed end: one blank line before (included), the ``==>`` heading,
    indented lines, the logs, the thank-you. The caller's print adds the
    blank line after."""
    home = os.path.expanduser("~")
    out = ["", _paint(f"==> {heading}", level, True, enabled=color)]
    out += [f"    {l}" for l in lines]
    if logs:
        out.append("    Logged in:")
        for p in logs:
            s = str(p)
            out.append(f"      {'~' + s[len(home):] if home and s.startswith(home) else s}")
    if thanks:
        out.append(f"    {thanks}")
    return "\n".join(out) + "\n"


def runs_log_row(folder: str | Path, app: str, row: Sequence[str],
                 header: Sequence[str] = ("date", "time", "user", "run", "outcome", "detail"),
                 when: _dt.datetime | None = None) -> Path:
    """Append one line to ``<folder>/YYYYMMDD <app>-runs.csv`` (header on a new file)."""
    when = when or _dt.datetime.now()
    folder = Path(os.path.expanduser(str(folder)))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{when:%Y%m%d} {app}-runs.csv"
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    if not path.exists() or path.stat().st_size == 0:
        w.writerow(header)
    w.writerow(row)
    with path.open("a", encoding="utf-8") as f:
        f.write(buf.getvalue())
    return path
