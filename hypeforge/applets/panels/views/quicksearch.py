"""The Quick Search on Win + Space (D-123, D-124; Javier, 2026-10-27: "a Quick Search in the top/middle of the
screen, to search of anything (apps, files, history, whatnot, whatever)"; "When Win+Space is pressed what needs to
appear first is just the search, and as you start typing starts searching").

One search box, centred a fifth of the way down the screen. As you type, each kind of thing under its own
heading, the best match first (Enter opens it):

  APPS & SETTINGS   your apps, and hypeForge Settings' pages
  FILES             in your home folder, by name (fd)
  BROWSER HISTORY   Chrome's, every profile, read-only, on this computer
  CLIPBOARD         what you copied (cliphist)
  DO                search the web · `= 12*7` calculates · `> htop` runs a command in a terminal

↑ ↓ move · Enter open · Tab next kind · Ctrl + Enter show a file in its folder · Esc or Win + Space close.
Nothing leaves the computer but a web search you pick.
"""

from __future__ import annotations

import ast
import operator
import os
import re
import shlex
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
import tomllib
import urllib.parse
from pathlib import Path

import panelkit  # first: it picks GTK 3 before anything asks for GTK
from gi.repository import Gdk, GLib, Gtk, Pango  # noqa: E402

sys.path.insert(0, str(panelkit.APPLETS / "common"))
import hfapps  # noqa: E402

WIDTH = 640           # a launcher, so outside the pop-up widths (D-116: the launchers are each theme's identity)
HOME = Path.home()
CHROME = HOME / ".config/google-chrome"
SETTINGS = panelkit.APPLETS / "settings/hypeforge-settings"
SECTIONS = panelkit.APPLETS / "sections/hypeforge-sections"
MANY = {"apps": 5, "files": 5, "history": 4, "clipboard": 3}
WAIT_MS = 120         # a pause in the typing before the slower kinds (files, history) are asked

CSS = """
.hf-search {{ padding: 10px 8px 8px 8px; }}
.hf-search entry {{ font-size: {big}pt; min-height: 40px; padding: 2px 10px; border-radius: {inner}px;
                   background: {tile}; color: {text}; border: 1px solid {line}; box-shadow: none; }}
.hf-search entry image {{ color: {dim}; }}
.hf-search list, .hf-search row {{ background: transparent; }}
.hf-search row {{ padding: 4px 10px; border-radius: {inner}px; }}
.hf-search row.hf-sec {{ padding: 10px 10px 2px 10px; }}
.hf-search row.hf-sec label {{ color: {dim}; font-weight: bold; font-size: {small}pt; }}
.hf-search row:not(.hf-sec):hover {{ background: {hover}; }}
.hf-search row:selected {{ background: {sel}; }}
.hf-search row:selected label.hf-name {{ color: {sel_text}; font-weight: bold; }}
.hf-search row:selected label.hf-sub, .hf-search row:selected label.hf-hint {{ color: {sel_text}; }}
.hf-search row:selected image {{ color: {sel_text}; }}
.hf-search label.hf-name {{ color: {text}; }}
.hf-search label.hf-sub, .hf-search label.hf-hint {{ color: {dim}; font-size: {small}pt; }}
.hf-search image {{ color: {text}; }}
"""


# ---- what is searched: plain functions, each given what it needs (the tests give them stand-ins) --------------

def score(name: str, q: str) -> int:
    """How well `name` matches `q`: 3 it starts with it, 2 a word does, 1 it's inside, 0 not at all."""
    n, q = name.lower(), q.lower().strip()
    if not q or q not in n:
        return 0
    if n.startswith(q):
        return 3
    return 2 if re.search(r"(^|[\s\-_./·])" + re.escape(q), n) else 1


def search_apps(q: str, apps: dict, pages: list) -> list[dict]:
    """Apps (their name, then their one line) and Settings' pages, best first."""
    found = []
    for app_id, a in apps.items():
        s = max(score(a["name"], q) * 2, score(a.get("comment", ""), q))
        if s:
            found.append({"kind": "app", "score": s, "icon": a.get("icon") or "application-x-executable",
                          "name": a["name"], "sub": a.get("comment") or "an app", "hint": "",
                          "open": [str(SECTIONS), "launch", app_id]})
    for p in pages:
        s = max(score(p["name"], q) * 2, score(p.get("summary", ""), q))
        if s:
            found.append({"kind": "page", "score": s, "icon": "preferences-system-symbolic",
                          "name": f"hypeForge Settings · {p['name']}", "sub": p.get("summary", "a Settings page"),
                          "hint": "", "open": ["alacritty", "--class", "hypeforge-settings", "-o",
                                               "window.dimensions.columns=130", "-o", "window.dimensions.lines=40",
                                               "-e", str(SETTINGS), p["name"]]})
    found.sort(key=lambda r: (-r["score"], r["name"].lower()))
    return found[:MANY["apps"]]


def file_icon(path: Path) -> str:
    if path.is_dir():
        return "folder-symbolic"
    ext = path.suffix.lower()
    for icon, exts in (("image-x-generic-symbolic", ".png .jpg .jpeg .gif .webp .svg"),
                       ("audio-x-generic-symbolic", ".mp3 .flac .ogg .oga .wav .m4a"),
                       ("video-x-generic-symbolic", ".mp4 .mkv .webm .avi .mov"),
                       ("package-x-generic-symbolic", ".zip .tar .gz .zst .xz .7z"),
                       ("x-office-document-symbolic", ".pdf .doc .docx .odt .xlsx .ods .pptx")):
        if ext in exts.split():
            return icon
    return "text-x-generic-symbolic"


def home_words(path: Path) -> str:
    """A folder as people read it: ~/Programs/kognog."""
    try:
        return "~/" + str(path.relative_to(HOME)) if path != HOME else "~"
    except ValueError:
        return str(path)


def search_files(q: str, run=subprocess.run, home: Path = HOME) -> list[dict]:
    """Files and folders in your home folder whose NAME holds `q` (fd: hidden ones and .gitignore'd ones skipped;
    other disks mounted inside it too). Names that start with it first, then the shorter paths."""
    if len(q.strip()) < 2 or not shutil.which("fd"):
        return []
    try:
        out = run(["fd", "--fixed-strings", "--ignore-case", "--one-file-system", "--max-results", "400",
                   "--exclude", "node_modules", "--", q.strip(), str(home)],
                  capture_output=True, text=True, timeout=2).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    paths = [Path(p.rstrip("/")) for p in out.splitlines() if p.strip()]
    want = q.strip().lower()
    # the name you typed exactly first, then names that start with it, then the shortest names and paths
    paths.sort(key=lambda p: (p.name.lower() != want, -score(p.name, q), len(p.name), len(p.parts), p.name.lower()))
    return [{"kind": "file", "score": score(p.name, q), "icon": file_icon(p), "name": p.name,
             "sub": home_words(p.parent), "hint": "", "path": str(p), "open": ["xdg-open", str(p)]}
            for p in paths[:MANY["files"]]]


def chrome_when(us: int, now: float | None = None) -> str:
    """Chrome keeps a visit's time in microseconds since 1601: "today", "yesterday", "3 days ago", or the date."""
    t = us / 1_000_000 - 11_644_473_600
    days = int(((now or time.time()) - t) // 86400)
    if days <= 0:
        return "visited today"
    if days == 1:
        return "visited yesterday"
    return f"visited {days} days ago" if days < 14 else "visited " + time.strftime("%d %b %Y", time.localtime(t))


def profiles(chrome: Path = CHROME) -> list[tuple[str, str]]:
    """(folder, name) of each Chrome profile with a history, the names from Chrome's own Local State."""
    import json
    try:
        cache = json.loads((chrome / "Local State").read_text()).get("profile", {}).get("info_cache", {})
    except (OSError, ValueError):
        cache = {}
    return [(p.parent.name, cache.get(p.parent.name, {}).get("name", p.parent.name))
            for p in sorted(chrome.glob("*/History"))]


def search_history(q: str, chrome: Path = CHROME) -> list[dict]:
    """Pages you visited in Chrome whose title or address holds `q`, newest first, every profile. Read-only:
    SQLite's immutable mode reads the file Chrome keeps open without touching or locking it."""
    if len(q.strip()) < 2:
        return []
    like, seen, found = f"%{q.strip()}%", set(), []
    many = len(profiles(chrome)) > 1
    for folder, name in profiles(chrome):
        db = chrome / folder / "History"
        try:
            con = sqlite3.connect(f"file:{urllib.parse.quote(str(db))}?mode=ro&immutable=1", uri=True, timeout=0.5)
            rows = con.execute("SELECT url, title, last_visit_time FROM urls WHERE hidden = 0 AND "
                               "(title LIKE ? OR url LIKE ?) ORDER BY last_visit_time DESC LIMIT 60",
                               (like, like)).fetchall()
            con.close()
        except sqlite3.Error:
            continue
        for url, title, when in rows:
            host = urllib.parse.urlsplit(url).hostname or url
            if url in seen or (title and title.lower() in seen):
                continue
            seen.update({url, (title or "").lower()})
            # in the title or the site's name counts; only somewhere in the address comes last
            found.append({"kind": "history", "score": max(score(title or "", q) * 2, score(host, q)), "when": when,
                          "icon": "web-browser-symbolic", "name": title or url,
                          "sub": f"{host} · {chrome_when(when)}" + (f" · {name}" if many else ""), "hint": "",
                          "open": ["google-chrome", f"--profile-directory={folder}", url]})
    found.sort(key=lambda r: (-r["score"], -r["when"]))
    return found[:MANY["history"]]


def search_clipboard(q: str, run=subprocess.run) -> list[dict]:
    """Things you copied (cliphist's history), newest first; picking one copies it again."""
    if not q.strip() or not shutil.which("cliphist"):
        return []
    try:
        out = run(["cliphist", "list"], capture_output=True, text=True, timeout=2).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    found = []
    for line in out.splitlines():
        _, _, words = line.partition("\t")
        if q.lower() in words.lower() and not words.startswith("[[ binary"):
            found.append({"kind": "clipboard", "score": score(words, q), "icon": "edit-paste-symbolic",
                          "name": words.strip()[:80], "sub": "copied earlier · Enter copies it again", "hint": "",
                          "line": line})
            if len(found) == MANY["clipboard"]:
                break
    return found


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow,
        ast.USub: operator.neg, ast.UAdd: operator.pos}


def calculate(text: str):
    """`12*7`, `(3 + 4) / 2`, `2**10`, `15 % 4`: numbers and + - * / // % ** ( ) only; None for anything else."""
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            a, b = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Pow) and abs(b) > 100:
                raise ValueError("too big")
            return _OPS[type(n.op)](a, b)
        if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.operand))
        raise ValueError("not a sum")
    try:
        v = ev(ast.parse(text.strip().replace("×", "*").replace("÷", "/").replace(",", ""), mode="eval"))
    except (SyntaxError, ValueError, ZeroDivisionError, OverflowError, TypeError, RecursionError):
        return None
    if isinstance(v, float) and v.is_integer() and abs(v) < 1e15:
        v = int(v)
    return round(v, 10) if isinstance(v, float) else v


def do_rows(q: str) -> list[dict]:
    """DO: `= …` calculates (Enter copies the answer), `> …` runs a command in a terminal, anything else offers a
    web search."""
    t = q.strip()
    if t.startswith("="):
        v = calculate(t[1:])
        return [{"kind": "calc", "icon": "accessories-calculator-symbolic", "name": f"= {v}",
                 "sub": f"{t[1:].strip()} · Enter copies the answer", "hint": "", "copy": str(v)}] if v is not None else \
               [{"kind": "note", "icon": "accessories-calculator-symbolic", "name": "Type a sum: = 12 * 7",
                 "sub": "numbers and + − × ÷ ( ) %", "hint": ""}]
    if t.startswith(">"):
        cmd = t[1:].strip()
        if not cmd:
            return [{"kind": "note", "icon": "utilities-terminal-symbolic", "name": "Type a command: > htop",
                     "sub": "it runs in a terminal", "hint": ""}]
        return [{"kind": "command", "icon": "utilities-terminal-symbolic", "name": f"Run: {cmd}",
                 "sub": "in a terminal", "hint": "", "open": ["alacritty", "--hold", "-e", "sh", "-c", cmd]}]
    if not t:
        return []
    return [{"kind": "web", "icon": "system-search-symbolic", "name": f"Search the web for “{t}”",
             "sub": "in your browser", "hint": "",
             "open": ["xdg-open", "https://www.google.com/search?q=" + urllib.parse.quote_plus(t)]}]


def sections_for(q: str, apps: dict, pages: list, slow: dict | None = None, run=subprocess.run) -> list[tuple[str, list]]:
    """Every heading with its rows, the best match lifted to the top. `slow` holds the files and the history
    once they've come back (they're asked after a pause in the typing)."""
    t = q.strip()
    if not t:
        return []
    if t[0] in "=>":                                   # the calculator and the command line: just DO
        return [("DO", do_rows(t))]
    slow = slow or {}
    parts = [("APPS & SETTINGS", search_apps(t, apps, pages)), ("FILES", slow.get("files", [])),
             ("BROWSER HISTORY", slow.get("history", [])), ("CLIPBOARD", search_clipboard(t, run)),
             ("DO", do_rows(t))]
    # the best match: a strong app or page first, else a file whose name starts with it, else the newest page
    best = None
    for heading, rows in parts:
        if rows and rows[0].get("score", 0) >= (4 if heading == "APPS & SETTINGS" else 3):
            best = (heading, rows[0])
            break
    if best is None:
        for heading in ("APPS & SETTINGS", "FILES", "BROWSER HISTORY", "CLIPBOARD"):
            rows = dict(parts)[heading]
            if rows:
                best = (heading, rows[0])
                break
    out = [("BEST MATCH", [best[1]])] if best else []
    for heading, rows in parts:
        rows = [r for r in rows if not (best and r is best[1])]
        if rows:
            out.append((heading, rows))
    return out


# ---- what a pick does ---------------------------------------------------------------------------------------

def act(row: dict, folder: bool = False) -> bool:
    """Open, copy or run the row. False when it does nothing (a note)."""
    def start(cmd):
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    if folder and row.get("path"):
        start(["xdg-open", str(Path(row["path"]).parent)])
        return True
    if row.get("open"):
        start(row["open"])
        return True
    if row.get("copy") is not None:
        subprocess.run(["wl-copy", "--", row["copy"]], timeout=3)
        return True
    if row.get("line"):
        decoded = subprocess.run(["cliphist", "decode"], input=row["line"].encode(), capture_output=True, timeout=3).stdout
        subprocess.run(["wl-copy"], input=decoded, timeout=3)
        return True
    return False


# ---- the box ---------------------------------------------------------------------------------------------------

def settings_pages() -> list[dict]:
    conf = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config")) / "hypeforge/applets/settings.toml"
    src = conf if conf.exists() else panelkit.APPLETS / "settings/settings.toml"
    try:
        with open(src, "rb") as f:
            return [p for p in tomllib.load(f).get("page", []) if p.get("name")]
    except (OSError, tomllib.TOMLDecodeError):
        return []


def build(look: panelkit.Look, args) -> panelkit.Panel:
    c = look.colour
    inner = 0 if look.straight else max(4, look.radius // 2)
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.format(big=look.size * 1.3, small=look.size * 0.85, inner=inner, tile=c["panel_tile"],
                                       text=c["panel_text"], dim=c["panel_text_dim"], line=c["panel_border"],
                                       hover=c["panel_hover"], sel=c["panel_selected"],
                                       sel_text=c["panel_selected_text"]).encode())
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
    apps, pages = hfapps.apps(), settings_pages()
    state = {"q": "", "slow": {}, "asked": 0, "panel": None}

    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    root.get_style_context().add_class("hf-search")
    entry = Gtk.SearchEntry(placeholder_text="Search apps, files, settings, history…   = sums   > commands")
    root.pack_start(entry, False, False, 0)
    results = Gtk.ListBox()
    results.set_selection_mode(Gtk.SelectionMode.SINGLE)
    results.set_activate_on_single_click(True)
    results.set_no_show_all(True)
    root.pack_start(results, False, False, 0)

    def row_for(r: dict) -> Gtk.ListBoxRow:
        row = Gtk.ListBoxRow()
        row.data = r
        line = Gtk.Box(spacing=10)
        line.pack_start(Gtk.Image.new_from_icon_name(r["icon"], Gtk.IconSize.LARGE_TOOLBAR), False, False, 0)
        words = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        words.set_valign(Gtk.Align.CENTER)
        for text, cls, ell in ((r["name"], "hf-name", Pango.EllipsizeMode.END), (r["sub"], "hf-sub", Pango.EllipsizeMode.MIDDLE)):
            lab = Gtk.Label(label=text, xalign=0, ellipsize=ell, max_width_chars=60)
            lab.get_style_context().add_class(cls)
            words.pack_start(lab, False, False, 0)
        line.pack_start(words, True, True, 0)
        row.add(line)
        return row

    def heading(text: str) -> Gtk.ListBoxRow:
        row = Gtk.ListBoxRow(selectable=False, activatable=False)
        row.get_style_context().add_class("hf-sec")
        row.data = None
        row.add(Gtk.Label(label=text, xalign=0))
        return row

    def show():
        for child in results.get_children():
            results.remove(child)
        found = sections_for(state["q"], apps, pages, state["slow"])
        first = None
        for text, rows in found:
            h = heading(text)
            results.add(h)
            h.show_all()
            for r in rows:
                row = row_for(r)
                results.add(row)
                row.show_all()              # each by itself: the list keeps no_show_all, so its show_all() skips them
                first = first or row
        results.set_visible(bool(found))
        if first:
            results.select_row(first)
        if state["panel"]:
            state["panel"].window.resize(1, 1)

    def ask_slow(q: str, asked: int):
        files, history = search_files(q), search_history(q)

        def done():
            if asked == state["asked"]:                  # still what is typed
                state["slow"] = {"files": files, "history": history}
                show()
            return False
        GLib.idle_add(done)

    def changed(_e):
        state["q"] = entry.get_text()
        state["slow"] = {}
        state["asked"] += 1
        asked = state["asked"]
        show()
        q = state["q"].strip()
        if len(q) >= 2 and q[0] not in "=>":
            GLib.timeout_add(WAIT_MS, lambda: (asked == state["asked"] and threading.Thread(
                target=ask_slow, args=(q, asked), daemon=True).start(), False)[1])

    def pick(row, folder=False):
        if row is not None and row.data and act(row.data, folder):
            state["panel"].close()

    def selectable(step: int):
        rows = [r for r in results.get_children() if r.data]
        if not rows:
            return
        now = results.get_selected_row()
        i = rows.index(now) if now in rows else -1
        results.select_row(rows[max(0, min(len(rows) - 1, i + step))])

    def next_kind():
        rows = results.get_children()
        now = results.get_selected_row()
        i = rows.index(now) if now in rows else -1
        later = [k for k, r in enumerate(rows) if k > i and r.data is None]
        start = later[0] if later else 0
        for r in rows[start:] + rows[:start]:
            if r.data:
                results.select_row(r)
                return

    def key(_w, ev):
        name = Gdk.keyval_name(ev.keyval)
        if name in ("Down", "Up"):
            selectable(1 if name == "Down" else -1)
            return True
        if name in ("Tab", "ISO_Left_Tab"):
            next_kind()
            return True
        if name in ("Return", "KP_Enter"):
            pick(results.get_selected_row(), folder=bool(ev.state & Gdk.ModifierType.CONTROL_MASK))
            return True
        return False

    entry.connect("search-changed", changed)
    entry.connect("key-press-event", key)
    results.connect("row-activated", lambda _l, row: pick(row))

    screen = panelkit.screen_in_use()
    top = int(screen.get_geometry().height / 5) if screen is not None else 260
    panel = panelkit.Panel("search", root, look, width=WIDTH, edges=["top"], margins={"top": top})
    state["panel"] = panel
    GLib.idle_add(lambda: (entry.grab_focus(), False)[1])
    if os.environ.get("HYPEFORGE_SEARCH_TYPE"):          # the bench: something typed
        GLib.timeout_add(400, lambda: (entry.set_text(os.environ["HYPEFORGE_SEARCH_TYPE"]), False)[1])
    return panel
