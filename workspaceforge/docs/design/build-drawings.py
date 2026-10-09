#!/usr/bin/env python3
"""Builds workspaceForge's design drawings: every terminal drawing exactly 100 columns, checked.

Same builder as displayForge's (docs/design there): {style:text} marks a coloured run.
The values are Javier's real ones on 2026-10-09: six workspaces, three screens, the apps the
launcher's groups would put on each workspace today.
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
    left = " {v b:workspaceForge 0.1.0}{m: · workspaces across your screens}"
    gap = W - len(vis(left)) - len(right) - 1
    top = line(left + " " * gap + "{m:" + right + "} ", "hdr")
    items = [("Workspaces", "W"), ("Apps", "A"), ("Sharing", "S"), ("Help ▾", "H"), ("Quit", "Q")]
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

WS = ["Daily", "Work", "Entertainment", "Gaming", "Monitoring", "Settings"]
APPS = {  # what the launcher's groups put on each workspace today (2026-10-09), counted on the desktop
    "Daily": ["Google Chrome", "Discord", "Thunderbird", "WhatsApp Web", "Microsoft Teams", "Dropbox",
              "Insync", "Private Internet Access", "Sparrow", "Avahi SSH Browser", "Avahi VNC Browser"],
    "Work": ["Alacritty", "Claude", "Claude Terminal", "Obsidian", "ONLYOFFICE", "Fresh", "Kate", "GitHub",
             "Master PDF Editor", "Zathura", "CMake", "Qt Assistant", "Qt D-Bus Viewer", "Qt Linguist",
             "Qt Widgets Designer"],
    "Entertainment": ["Spotify", "cliamp", "VLC media player", "mpv Media Player", "Qt V4L2 test Utility",
                      "Qt V4L2 video capture"],
    "Gaming": ["Steam", "Sim Companies", "SuperTux 2", "World of Warcraft Pi5", "Battle.net", "Lutris",
               "ProtonUp-Qt"],
    "Monitoring": ["btop++", "Htop", "nvtop", "System Monitor", "Hardware Locality lstopo"],
    "Settings": ["hypeForge Settings", "displayForge", "nogForge", "grubForge", "alacrittyForge",
                 "Input Remapper", "Manage Printing", "Print Settings", "Wiremix", "NetworkManager Dmenu",
                 "Advanced Network Config", "Removable Drives", "Thunar Preferences", "KDE System Settings"],
}
WHERE_YOU_ARE = 26
GROUP = {"Steam": "Games", "Sim Companies": "Games", "SuperTux 2": "Games", "World of Warcraft Pi5": "Games",
         "Battle.net": "Games", "Lutris": "Games", "ProtonUp-Qt": "Games"}


def ws_list(sel, counts=False, width=26):
    """The workspaces down the left: Win + N, the name, ● for the one on screen now."""
    rows = []
    for i, n in enumerate(WS, 1):
        mark = "●" if n == "Daily" else " "
        right = f"{len(APPS[n]):>3}" if counts else f" {mark} "
        txt = f" {i}  {n}"
        txt = txt + " " * (width - len(txt) - len(right) - 1) + right + " "
        rows.append("{sel:" + txt + "}" if n == sel else txt)
    return rows


# ---- 1 · Workspaces: buttons on top, new and edit on the same page (Javier, D-4) -------------------

LC = 31   # the list column on the Workspaces page


def ws_rows(names, sel, new_row=False):
    rows = []
    for i, n in enumerate(names, 1):
        mark = "●" if n == "Daily" else " "
        txt = f" {i}  {n}"
        txt = txt + " " * (27 - len(txt) - 2) + mark + "  "
        rows.append("{sel:" + txt + "}" if n == sel else txt)
    if new_row:
        txt = f" {len(names) + 1}  (new)"
        rows.append("{sel:" + txt + " " * (27 - len(txt)) + "}")
    return rows


def ws_page(names, sel, right, new_row=False, status="KognogOS · javier · nothing changed yet",
            hint_text=None):
    L = header("Workspaces", right=status)
    L += [blank]
    left = ["{btn: Move Up (+) } {btn: Move Down (-) }", "",
            "{m: Win  Workspace       on now}"] + ws_rows(names, sel, new_row)
    for i in range(max(len(left), len(right))):
        L.append(col(left[i] if i < len(left) else "", right[i] if i < len(right) else "", LC))
    L += [blank]
    L += [line("  " + r) for r in box("Workspaces across all screens", [
        "{ok b:● On}   {m:switching a workspace switches every screen together (3 screens: Main, Left, Right)}",
        "{d:Off = Sway's own: each screen switches by itself.}            {btn: Turn Off (o) }"], 96)]
    L += [blank, hint(hint_text or "{a:↑ ↓} {d:pick}  ·  {a:n} {d:new}  ·  {a:e} {d:edit}  ·  {a:d} {d:delete}  ·  {a:+ -} {d:move}  ·  {a:F10} {d:save}  ·  {a:F1} {d:help}")]
    return pad(L)


TOP_BUTTONS = "{btn: New (n) }  {btn: Edit (e) }  {btn: Delete (d) }"


def s_workspaces():
    right = [TOP_BUTTONS, "",
             "{v b:4 · Gaming}   {m:Win + 4 switches all three screens here}",
             "",
             "{b:Name}            Gaming",
             "",
             "{b:Apps that open}  {b:7} {m:Steam, Sim Companies, SuperTux 2, …}",
             "                {d:change them on the Apps page (Ctrl + A)}",
             "",
             "{b:Sharing}         {m:none: every screen has its own space}",
             "",
             "{b:Open now}        {m:nothing}"]
    return ws_page(WS, "Gaming", right)


def s_new():
    right = ["{d: New (n) }  {d: Edit (e) }  {d: Delete (d) }", "",
             "{v b:New workspace}   {m:fill it in right here}",
             "",
             "{b:Name}            {foc: ▏                         }",
             "",
             "{b:Goes after}      {fld: 6 · Settings          ▾ }",
             "",
             "{d:It becomes 7: Win + 7 takes every screen there.}",
             "{d:It starts with no apps; give it some on the Apps page.}",
             "",
             "{pri: Create (Enter) }  {btn: Cancel (Esc) }"]
    return ws_page(WS, None, right, new_row=True,
                   hint_text="{d:type a name}  ·  {a:Tab} {d:where it goes}  ·  {a:Enter} {d:create}  ·  {a:Esc} {d:cancel}")


def s_edit():
    names = ["Daily", "Work", "Media", "Gaming", "Monitoring", "Settings"]
    right = [TOP_BUTTONS, "",
             "{v b:3 · Media}   {m:Win + 3 switches all three screens here}",
             "",
             "{b:Name}            Media  {ok:✓ renamed from Entertainment}",
             "",
             "{b:Apps that open}  {b:6} {m:Spotify, cliamp, VLC media player, …}",
             "                {w:⚠ renamed: check these apps still belong}",
             "                {w:  here, on the Apps page (Ctrl + A)}",
             "",
             "{b:Sharing}         {m:none: every screen has its own space}",
             "",
             "{b:Open now}        {m:nothing}"]
    return ws_page(names, "Media", right, status="KognogOS · javier · 1 change waiting")


# ---- 1b · Delete a workspace that has windows ---------------------------------------------------

def s_delete():
    L = header("Workspaces")
    L += [blank] * 5
    L += [line(" " * 17 + r) for r in box("Delete “Work”?", [
        "",
        "{b:3 windows are open on Work:}",
        "  {m:Alacritty · Obsidian · ONLYOFFICE}",
        "",
        "They move to   {foc: 1 · Daily        ▾ }",
        "",
        "{d:Win + 3 … 6 become Win + 2 … 5 (the ones after it move up).}",
        "{d:Its 15 apps go to “opens where you are” until you place them.}",
        "",
        "        {pri: Delete and Move Them (d) }   {btn: Stay (Esc) }",
        ""], 66, "w")]
    L += [blank] * 6
    L += [hint("{a:d} {d:delete}  ·  {a:Esc} {d:stay}  ·  {d:nothing is closed: windows only move}")]
    return pad(L)


# ---- 2 · Apps: two tables and the arrows between them (Javier's layout, 2026-10-09) ---------

UTILITIES = ["Ark", "bitlaForge", "Bulk Rename", "Flatseal", "Galculator", "hypeForge Help & Keys",
             "KeePassXC", "KWrite", "Midnight Commander", "Raspberry Pi Imager", "Spectacle", "Termius",
             "Vim", "Winetricks", "xgps", "xgpsspeed"]
LW, MW, RW = 45, 8, 45   # left table, the arrows, right table: 45 + 8 + 45 + 2 margins = 100


def trow(ticked, name, cat, width, shade, cur=False):
    """One table row: [x] the app, its category; every other row shaded (our table formatting)."""
    box_ = "[x]" if ticked else "[ ]"
    txt = f" {box_} {name}"
    txt = txt + " " * (width - len(txt) - len(cat) - 1) + cat + " "
    if cur:
        return "{sel:" + txt + "}"
    return "{fld:" + txt + "}" if shade else txt


def theading(width):
    h = "     App ▲"
    return "{b:" + h + " " * (width - len(h) - len("Category ") ) + "Category }"


def fit(s, width):
    n = len(vis(s))
    if n > width:
        sys.exit(f"CELL TOO WIDE ({n} > {width}): {vis(s)!r}")
    return s + " " * (width - n)


def s_apps():
    L = header("Apps")
    L += [blank]
    left = ["{v b:Apps on no workspace}" + " " * 13 + "{m:16 of 26}",
            fit(" " * 9 + "{d:Find} {fld:          }  {foc: Utilities ▾ }", LW),
            "{btn: Select All (a) }  {btn: Deselect All (u) }",
            theading(LW)]
    for i, n in enumerate(UTILITIES):
        left.append(trow(n == "Winetricks", n, "Utilities", LW, i % 2 == 1, cur=n == "Winetricks"))
    right = ["{v b:Workspaces}" + " " * 29 + "{m:6}"]
    for i, n in enumerate(WS, 1):
        k = f"{len(APPS[n])} apps"
        if n == "Gaming":
            head = f" ▾ {i}  {n}"
            right.append("{act:" + head + " " * (RW - len(head) - len(k) - 1) + k + " }")
            right.append("{btn: Select All (a) }  {btn: Deselect All (u) }")
            right.append(theading(RW))
            for j, a in enumerate(APPS["Gaming"]):
                right.append(trow(False, a, "Games", RW, j % 2 == 1))
        else:
            head = f" ▸ {i}  {n}"
            right.append(head + " " * (RW - len(head) - len(k) - 1) + "{m:" + k + "} ")
    mid = [""] * 9 + ["{pri:  >>  }", "{d: send}", "", "", "{btn:  <<  }", "{d: back}"]
    h = max(len(left), len(right))
    for i in range(h):
        a = fit(left[i] if i < len(left) else "", LW)
        m = fit(" " + (mid[i] if i < len(mid) else ""), MW)
        b = right[i] if i < len(right) else ""
        L.append(line(" " + a + m + b))
    L += [blank, hint("{a:Space} {d:tick}  ·  {a:>} {d:send to the open workspace}  ·  {a:<} {d:send back}  ·  {a:Tab} {d:other side}  ·  {a:F10} {d:save}")]
    return pad(L)


# ---- 3 · Sharing: a switch in every cell, Save at the bottom (Javier, D-4) ------------------------

def s_sharing():
    L = header("Sharing", right="KognogOS · javier · 3 changes waiting")
    L += [blank,
          line("  {v b:Which screens keep the same apps across workspaces}"),
          line("  {m:Switch a cell to Shared: that screen keeps the same apps in every workspace switched to}"),
          line("  {m:Shared in its column. The other screens change as usual.}"),
          blank,
          line("                       {b:Main · DP-3}           {b:Left · DP-2}           {b:Right · DP-1}"),
          line("  {d:─────────────────────────────────────────────────────────────────────────────────}")]
    own, shared = "{fld: ○ Own      }", "{ok b: ● Shared   }"
    grid = [("1  Daily", own, shared, own), ("2  Work", own, shared, own),
            ("3  Entertainment", own, "{foc: ● Shared   }", own), ("4  Gaming", own, own, own),
            ("5  Monitoring", own, own, own), ("6  Settings", own, own, own)]
    for n, a_, b_, c_ in grid:
        def cell(x):
            return x + " " * (22 - len(vis(x)))
        L.append(line("  " + n.ljust(21) + cell(a_) + cell(b_) + c_))
    L += [blank,
          line("  {d:EXAMPLE: the left screen shared by Daily, Work and Entertainment: your chat there stays put}"),
          line("  {d:while the main and right screens change. Today nothing is shared.}"),
          blank,
          line("  {m:One cell alone shares nothing: it takes two or more in a column.}"),
          blank,
          line("                                {pri: Save (F10) }    {btn: Undo Changes (Esc) }"),
          blank,
          hint("{a:← → ↑ ↓} {d:pick a cell}  ·  {a:Space} {d:Own / Shared}  ·  {a:F10} {d:save}  ·  {a:Esc} {d:undo}  ·  {a:F1} {d:help}")]
    return pad(L)


# ---- Save ---------------------------------------------------------------------------------------

def s_save():
    L = header("Apps", right="KognogOS · javier · 2 changes waiting")
    L += [blank,
          line("  {v b:Save these workspace settings?}"),
          blank,
          line("  {m:Change                          Before                    After}"),
          line("  {d:──────────────────────────────────────────────────────────────────────────}"),
          line("  Workspace 3 · name              Entertainment             {ok:Media}"),
          line("  Apps · Discord                  Daily                     {ok:Entertainment}"),
          blank,
          line("  {m:Written to}   ~/.config/hypeforge/applets/workspaces.toml"),
          line("  {m:Backup first} ~/.config/workspaceforge/backups/         {d:the last 20 are kept}"),
          line("  {m:Then}         the Workspaces applet re-reads it: {b:at once}, no logout"),
          blank,
          line("  {d:Open windows stay where they are; the renamed workspace keeps its windows.}"),
          blank,
          line("                                {pri: Save (Enter) }    {btn: Back (Esc) }"),
          blank,
          hint("{a:Enter} {d:save}  ·  {a:Esc} {d:back}  ·  {d:after saving: a note with what was written}")]
    return pad(L)


SCREENS = {"workspaces": s_workspaces(), "new": s_new(), "edit": s_edit(), "delete": s_delete(), "apps": s_apps(),
           "sharing": s_sharing(), "save": s_save()}

if __name__ == "__main__":
    for k, v in SCREENS.items():
        print(k, len(v), "lines")
