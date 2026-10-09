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


# ---- 1 · Workspaces -----------------------------------------------------------------------------

def s_workspaces():
    L = header("Workspaces")
    L += [blank]
    left = ["{m: Win   Workspace     on now }"] + ws_list("Gaming") + ["", "", "{d: up to 9  (Win + 1 … 9)}"]
    right = [
        "{v b:4 · Gaming}   {m:Win + 4 switches all three screens here}",
        "",
        "{b:Name}            {foc: Gaming                    }",
        "",
        "{b:Apps that open}  {b:7} {m:Steam, Sim Companies, SuperTux 2, Lutris, …}",
        "                {d:change them on the Apps page (Ctrl + A)}",
        "",
        "{b:Sharing}         {m:none: every screen has its own space here}",
        "                {d:the Sharing page (Ctrl + S)}",
        "",
        "{b:Open now}        {m:nothing}",
        "",
        "{btn: Rename (r) }  {btn: New Workspace (n) }  {btn: Delete (d) }",
        "{btn: Move Up (+) }  {btn: Move Down (-) }",
    ]
    for i in range(max(len(left), len(right))):
        a = left[i] if i < len(left) else ""
        b = right[i] if i < len(right) else ""
        L.append(col(a, b))
    L += [blank]
    L += [line("  " + r) for r in box("Workspaces across all screens", [
        "{ok b:● On}   {m:switching a workspace switches every screen together (3 screens: Main, Left, Right)}",
        "{d:Off = Sway's own: each screen switches by itself.}            {btn: Turn Off (o) }"], 96)]
    L += [blank, hint("{a:↑ ↓} {d:pick}  ·  {a:Tab} {d:into the form}  ·  {a:F10} {d:save}  ·  {a:1-4} {d:menu}  ·  {a:F1} {d:help}")]
    return pad(L)


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


# ---- 2 · Apps -----------------------------------------------------------------------------------

def s_apps():
    L = header("Apps")
    L += [blank]
    left = ["{m: Win   Workspace      apps }"] + ws_list("Gaming", counts=True) + [
        "", " –  Where you are     26 ", "", "{d: each app opens on ONE}", "{d: workspace, or where}", "{d: you are}"]
    right = ["{v b:Apps that open on Gaming}   {m:however you start them}", ""]
    for i, a in enumerate(APPS["Gaming"]):
        txt = f"  {a}"
        g = "{d:" + GROUP[a] + "}"
        row = txt + " " * (36 - len(txt)) + g
        right.append("{sel:" + txt + " " * (36 - len(txt)) + "}" + g if i == 1 else row)
    right += ["",
              "{btn: Add an App (a) }  {btn: Move To… (m) }  {btn: Remove (d) }",
              "",
              "{b:When one opens}  {ok:● the screens go with it}",
              "                {d:not in the first 30 s after login, so apps}",
              "                {d:that start by themselves don't move you}"]
    for i in range(max(len(left), len(right))):
        a = left[i] if i < len(left) else ""
        b = right[i] if i < len(right) else ""
        L.append(col(a, b))
    L += [blank, hint("{a:↑ ↓} {d:pick}  ·  {a:Tab} {d:the apps}  ·  {a:a} {d:add}  ·  {a:m} {d:move}  ·  {a:d} {d:remove}  ·  {a:F10} {d:save}  ·  {a:F1} {d:help}")]
    return pad(L)


# ---- 2b · Add an app ----------------------------------------------------------------------------

def s_add():
    L = header("Apps")
    L += [blank] * 2
    rows = ["{b:Search}  {foc: disc▏                                      }",
            "",
            "{m:App                         now opens on}",
            "{sel: Discord                     Daily: moves to Gaming     }",
            " Discover                    {d:where you are}",
            "",
            "{d:Every installed app, as the launcher lists them (95). One already}",
            "{d:on another workspace moves here: an app opens on ONE workspace.}",
            "",
            "        {pri: Add to Gaming (Enter) }   {btn: Back (Esc) }"]
    L += [line(" " * 14 + r) for r in box("Add an app to Gaming", rows, 72)]
    L += [blank] * 6
    L += [hint("{d:type to search}  ·  {a:↑ ↓} {d:pick}  ·  {a:Enter} {d:add}  ·  {a:Esc} {d:back}")]
    return pad(L)


# ---- 3 · Sharing --------------------------------------------------------------------------------

def s_sharing():
    L = header("Sharing")
    L += [blank,
          line("  {v b:Which screens keep the same apps across workspaces}"),
          line("  {m:A shared screen shows the same windows in every workspace of its group; the others change.}"),
          blank,
          line("                       {b:Main · DP-3}           {b:Left · DP-2}           {b:Right · DP-1}"),
          line("  {d:─────────────────────────────────────────────────────────────────────────────────}")]
    grid = [("1  Daily", "own", "{ok:┐ shared  A}", "own"),
            ("2  Work", "own", "{ok:┤ shared  A}", "own"),
            ("3  Entertainment", "own", "{ok:┘ shared  A}", "{sel:own}"),
            ("4  Gaming", "own", "own", "own"),
            ("5  Monitoring", "own", "own", "own"),
            ("6  Settings", "own", "own", "own")]
    for n, a, b, c in grid:
        def cell(x):
            return x + " " * (22 - len(vis(x)))
        L.append(line("  " + n.ljust(21) + cell(a) + cell(b) + c))
    L += [blank,
          line("  {d:The drawing shows an EXAMPLE: Left shared by Daily, Work and Entertainment (group A).}"),
          line("  {d:Today nothing is shared: every cell is “own”.}"),
          blank,
          line("  {btn: Share With the One Above (space) }  {btn: Stop Sharing (d) }"),
          blank,
          line("  {m:A new window can still land on a shared screen (the fill order decides);}"),
          line("  {m:it then shows in every workspace of that group, as sharing means.}"),
          blank,
          hint("{a:← → ↑ ↓} {d:pick a cell}  ·  {a:space} {d:share with the one above}  ·  {a:d} {d:stop}  ·  {a:F10} {d:save}  ·  {a:F1} {d:help}")]
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


SCREENS = {"workspaces": s_workspaces(), "delete": s_delete(), "apps": s_apps(), "add": s_add(),
           "sharing": s_sharing(), "save": s_save()}

if __name__ == "__main__":
    for k, v in SCREENS.items():
        print(k, len(v), "lines")
