#!/usr/bin/env python3
"""Builds defaultappsForge's design drawings: every terminal drawing exactly 100 columns, checked.

Same builder as the other Forge apps: {style:text} marks a coloured run. The values are Javier's
real ones on 2026-10-09: ~/.config/mimeapps.list and what xdg-mime answers for each kind of file.
"""
import html, re, sys

W = 100
TOK = re.compile(r"\{([a-z0-9 ]+):((?:[^{}]|\{\})*?)\}")


def vis(s):
    return TOK.sub(lambda m: m.group(2), s)


def render(s):
    out, pos = [], 0
    for m in TOK.finditer(s):
        out.append(html.escape(s[pos:m.start()]))
        out.append(f'<span class="{m.group(1)}">{html.escape(m.group(2))}</span>')
        pos = m.end()
    out.append(html.escape(s[pos:]))
    return "".join(out)


def line(s, cls=None):
    n = len(vis(s))
    if n > W:
        sys.exit(f"TOO WIDE ({n}): {vis(s)!r}")
    body = render(s) + " " * (W - n)
    return f'<span class="{cls}">{body}</span>' if cls else body


def header(active, right="KognogOS · javier · nothing changed yet"):
    left = " {v b:defaultappsForge 0.1.0}{m: · which app opens what}"
    gap = W - len(vis(left)) - len(right) - 1
    top = line(left + " " * gap + "{m:" + right + "} ", "hdr")
    items = [("Default Apps", "D"), ("File Types", "F"), ("Help ▾", "H"), ("Quit", "Q")]
    parts = []
    for name, letter in items:
        if name.startswith(active):
            parts.append("{act: " + name + " }")
        else:
            i = name.index(letter)
            parts.append(name[:i] + "{u:" + letter + "}" + name[i + 1:])
    menu = line(" " + "   ".join(parts), "bar")
    return [top, menu]


def hint(s):
    return line(" " + s, "hdr")


def term(lines, cls="term"):
    return f'<div class="{cls}"><pre>' + "\n".join(lines) + "</pre></div>"


def box(title, rows, width, cls="a"):
    """A rounded box exactly `width` columns wide; rows are markup strings padded inside."""
    t = f"╭─ {title} "
    out = ["{" + cls + ":" + t + "─" * (width - len(t) - 1) + "╮}"]
    for r in rows:
        pad = width - 4 - len(vis(r))
        if pad < 0:
            sys.exit(f"BOX ROW TOO WIDE: {vis(r)!r}")
        out.append("{" + cls + ":│} " + r + " " * pad + " {" + cls + ":│}")
    out.append("{" + cls + ":╰" + "─" * (width - 2) + "╯}")
    return out


def side(a, b, gap=2, indent=2):
    h = max(len(a), len(b))
    wa = len(vis(a[0]))
    a = a + [" " * wa] * (h - len(a)); b = b + [""] * (h - len(b))
    return [line(" " * indent + x + " " * gap + y) for x, y in zip(a, b)]


def col(a, b, w=28):
    """The list on the left (exactly w columns, checked), a bar, the page on the right."""
    if len(vis(a)) > w:
        sys.exit(f"LEFT COLUMN TOO WIDE: {vis(a)!r}")
    return line(" " + a + " " * (w - len(vis(a))) + "{d:│} " + b)


def pad(lines, total=30):
    """Every drawing is the same height, like a real terminal of 100 × 30."""
    if len(lines) > total:
        sys.exit(f"TOO TALL ({len(lines)} lines)")
    return lines[:-1] + [blank] * (total - len(lines)) + lines[-1:]


blank = line("")





# ---- 1 · Default Apps (Javier's list and layout, first review 2026-10-09) ---------------------------
# today on Javier's desktop (xdg-mime + ~/.config/mimeapps.list, 2026-10-09)
DEFAULTS = [
    ("Web Browser", "Google Chrome"), ("Email Client", "Thunderbird"), ("Calendar", "Thunderbird"),
    ("Phone Numbers", "— none installed —"), ("Image Viewer", "Pinta"), ("Music Player", "mpv"),
    ("Video Player", "mpv"), ("Text Editor", "Fresh"), ("PDF Viewer", "Google Chrome"),
    ("File Manager", "Thunar"), ("Terminal Emulator", "Alacritty"), ("Archive Manager", "Ark"),
    ("Map", "Google Maps"),
]


def dropdown(app, focus=False):
    inner = f" {app:<24}▾ "
    return ("{foc:" if focus else "{fld:") + inner + "}"


def item(name, app, focus=False):
    """• Name, the drop-down close by (Javier, second review: bullets, closer, a gap between rows)."""
    return f"   • {name:<20}" + dropdown(app, focus)


def s_defaults():
    L = header("Default Apps")
    L += [blank, line("     {u b:Defaults}" + " " * 12 + "{u b:Selection}"), blank]   # a little space under the titles
    for i, (name, app) in enumerate(DEFAULTS):
        if i:
            L.append(blank)                       # a small gap between rows
        L.append(line(item(name, app, focus=(name == "PDF Viewer"))))
    L += [hint("{a:↑ ↓} {d:next}  ·  {a:Enter} {d:open the list}  ·  {a:F10} {d:save}  ·  {a:1-3} {d:menu}  ·  {a:F1} {d:help}")]
    return pad(L, total=31)   # one line more than the window: the list scrolls by a line at 100 × 30


def s_dropdown():
    """The PDF Viewer's list, open."""
    L = header("Default Apps")
    L += [blank, line("     {u b:Defaults}" + " " * 12 + "{u b:Selection}"), blank]
    rows = DEFAULTS[:8]
    for i, (name, app) in enumerate(rows):
        if i:
            L.append(blank)
        L.append(line(item(name, app, focus=(name == "PDF Viewer"))))
    opts = [("Google Chrome", True), ("Master PDF Editor", False), ("Zathura", False), ("Okular", False),
            ("ONLYOFFICE", False), ("GIMP", False)]
    for o, cur in opts:
        mark = "●" if cur else " "
        txt = f" {mark} {o:<24}"
        L.append(line(" " * 25 + ("{sel:" + txt + "}" if o == "Master PDF Editor" else "{fld:" + txt + "}")))
    L += [hint("{a:↑ ↓} {d:pick}  ·  {a:Enter} {d:use it}  ·  {a:Esc} {d:close the list}")]
    return pad(L)


# ---- 2 · File Types: two tables with >> / << (like workspaceForge's Apps page) ---------------------

LW, MW, RW = 40, 10, 48


def trow(ticked, ext, what, width, shade, cur=False):
    txt = f" {'[x]' if ticked else '[ ]'} {ext:<12}{what}"
    txt = txt + " " * (width - len(txt))
    return "{sel:" + txt + "}" if cur else ("{fld:" + txt + "}" if shade else txt)


def s_types():
    L = header("File Types")
    L += [blank]
    # the header band: the same height on both sides (Javier: "both tables aligned from the top")
    lhead = ["{v b:File types on no default app}", fit(" " * 10 + "{d:Find} {fld:          }", LW),
             "{btn: Select All (a) } {btn: Deselect All (u) }"]
    rhead = ["{v b:Default apps}  {m:open one to see its file types}", "", ""]
    for a_, b_ in zip(lhead, rhead):
        L.append(line(" " + fit(a_, LW) + " " * MW + b_))
    left = ["{b:     Type ▲      What}"]
    pool = [(".csv", "spreadsheet text"), (".docx", "Word document"), (".epub", "e-book"), (".ics", "calendar event"),
            (".iso", "disc image"), (".odt", "document"), (".rtf", "rich text"), (".srt", "subtitles"),
            (".torrent", "torrent"), (".ttf", "font"), (".xlsx", "Excel sheet")]
    for i, (e, w) in enumerate(pool):
        left.append(trow(e == ".ics", e, w, LW, i % 2 == 1, cur=e == ".ics"))
    right = []
    counts = {"Web Browser": 3, "Email Client": 1, "Calendar": 0, "Image Viewer": 7, "Music Player": 6,
              "Video Player": 6, "Text Editor": 12, "PDF Viewer": 1, "Archive Manager": 6}
    for name, n in counts.items():
        words = f"{n} type{'s' if n != 1 else ''}".rjust(RW - 33)
        if name == "Calendar":
            right.append("{act: ▾ " + f"{name:<28}" + words + " }")
            right.append("{btn: Select All (a) } {btn: Deselect All (u) }")
            right.append("{d:   nothing yet: send .ics here with >>}")
        else:
            right.append(f" ▸ {name:<28}" + "{m:" + words + "}")
    mid = [""] * 4 + ["{pri:   >>   }", "{d:  assign}", "", "{btn:   <<   }", "{d:  clear}"]
    for i in range(max(len(left), len(right))):
        a_ = fit(left[i] if i < len(left) else "", LW)
        m = fit(" " + (mid[i] if i < len(mid) else ""), MW)
        b_ = right[i] if i < len(right) else ""
        L.append(line(" " + a_ + m + b_))
    L += [blank, hint("{a:Space} {d:tick}  ·  {a:>} {d:assign to the open one}  ·  {a:<} {d:clear}  ·  {a:Tab} {d:other side}  ·  {a:F10} {d:save}")]
    return pad(L)


def fit(s, width):
    n = len(vis(s))
    if n > width:
        sys.exit(f"CELL TOO WIDE ({n} > {width}): {vis(s)!r}")
    return s + " " * (width - n)


# ---- Save: a pop-up ----------------------------------------------------------------------------------

def s_save():
    L = header("Default Apps", right="KognogOS · javier · 3 changes waiting")
    L += [blank] * 3
    L += [line("      " + r) for r in box("Save your default apps?", [
        "",
        "{m:Change                    Before                 Now}",
        "{d:────────────────────────────────────────────────────────────────────────}",
        "PDF Viewer                Google Chrome          {ok:Master PDF Editor}",
        "File type .ics            —                      {ok:Calendar (Thunderbird)}",
        "Old choices tidied        Typora, Nemo, Brave    {ok:removed (apps gone)}",
        "",
        "{m:Written to}    ~/.config/mimeapps.list   {d:every desktop and app reads it}",
        "{m:Backup first}  ~/.config/defaultappsforge/backups/   {d:the last 20 kept}",
        "{m:Then}          at once: the next file you open uses it",
        "",
        "                  {pri: Save (Enter) }    {btn: Cancel (Esc) }",
        ""], 86, "a")]
    L += [blank] * 4
    L += [hint("{a:Enter} {d:save}  ·  {a:Esc} {d:cancel: nothing is written}")]
    return pad(L)


SCREENS = {"defaults": s_defaults(), "dropdown": s_dropdown(), "types": s_types(), "save": s_save()}

if __name__ == "__main__":
    for k, v in SCREENS.items():
        print(k, len(v), "lines")
