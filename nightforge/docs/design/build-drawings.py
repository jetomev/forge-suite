#!/usr/bin/env python3
"""Builds nightForge's design drawings: every terminal drawing exactly 100 columns, checked.

Same builder as displayForge's and workspaceForge's: {style:text} marks a coloured run. The values
are Javier's real ones on 2026-10-09: wlsunset 0.4.0 running with Miami's place, 4000 K at night,
6500 K by day; today's sun in Miami, 07:15 up and 19:00 down (worked out by nightforge/sun.py).
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
    left = " {v b:nightForge 0.1.0}{m: · warmer screens in the evening}"
    gap = W - len(vis(left)) - len(right) - 1
    top = line(left + " " * gap + "{m:" + right + "} ", "hdr")
    items = [("Night Light", "N"), ("Schedule", "S"), ("Help ▾", "H"), ("Quit", "Q")]
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



def toggle(on):
    return "{ok b:● On}" if on else "{m:○ Off}"


def temps(pick, values=(3000, 3500, 4000, 4500, 5000)):
    out = []
    for v in values:
        out.append("{act: " + str(v) + " }" if v == pick else " " + str(v) + " ")
    return " ".join(out) + " {m:K}"


# ---- 1 · Night Light --------------------------------------------------------------------------------

def s_night():
    L = header("Night Light")
    L += [blank]
    L += [line("  " + r) for r in box("Right now", [
        "{ok b:● Warm}  {b:4000 K}  {m:since sunset at 19:00 · back to daylight at sunrise, 07:15}",
        "{d:On all three screens. Screenshots and what you share are not affected.}"], 96, "ok")]
    L += [blank,
          line("  {b:Night light}       " + toggle(True) + "   {d:Off: no warm colours, now and at every login}       {btn: Turn Off (o) }"),
          blank,
          line("  {b:Right now}         {act: (•) Automatic }  ( ) Warm Now   ( ) Daylight Now"),
          line("                    {d:Warm Now / Daylight Now hold until you pick Automatic again, or log out}"),
          blank,
          line("  {b:Evening warmth}    " + temps(4000)),
          line("                    {d:3000 very warm · 3500 warm · 4000 gentle (today) · 4500 · 5000 just a touch}"),
          line("                    {btn: Preview (p) }  {d:shows it on your screens for 10 seconds, then goes back}"),
          blank,
          line("  {b:Daytime}           {m:6500 K · the screens' own white (no change)}"),
          blank,
          ]
    L += [blank, hint("{a:o} {d:on/off}  ·  {a:← →} {d:choose}  ·  {a:p} {d:preview}  ·  {a:F10} {d:save}  ·  {a:1-3} {d:menu}  ·  {a:F1} {d:help}")]
    return pad(L)


# ---- 2 · Schedule -----------------------------------------------------------------------------------

def s_schedule():
    L = header("Schedule")
    L += [blank,
          line("  {b:When}              {act: (•) By the Sun at Your Place }   ( ) Fixed Times"),
          blank,
          line("  {b:Your place}        {d:Latitude}  {foc: 25.77 }  {d:Longitude}  {foc: -80.19 }   {m:25.8° N, 80.2° W}"),
          line("                    {d:one decimal is plenty (about 10 km); nothing is looked up online}"),
          blank]
    L += [line("  " + r) for r in box("Your sun, worked out on this computer", [
        "{b:Today}      sunset {v b:19:00}   ·   sunrise tomorrow {v b:07:15}",
        "{b:In June}    sunset {m:20:14}   ·   sunrise {m:06:29}",
        "{d:The change is gradual around sunset and sunrise: you never see it jump.}"], 96)]
    L += [blank,
          line("  {d:── or, with Fixed Times ─────────────────────────────────────────────────────────────────────}"),
          line("  {m:Warm from}         {fld: 21:00 }   {m:Daylight from}  {fld: 07:00 }   {m:Fade}  {fld: 30 }{m: minutes}"),
          line("                    {d:the same every day, whatever the season}")]
    L += [blank, hint("{a:← →} {d:choose}  ·  {a:Tab} {d:next field}  ·  {a:F10} {d:save}  ·  {a:1-3} {d:menu}  ·  {a:F1} {d:help}")]
    return pad(L)


# ---- Preview -----------------------------------------------------------------------------------------

def s_preview():
    L = header("Night Light")
    L += [blank] * 7
    L += [line(" " * 22 + r) for r in box("Preview", [
        "",
        "Your screens are showing {b:3000 K} now — very warm.",
        "",
        "{w b:Back to how it was in 8 seconds.}",
        "",
        "         {pri: Keep 3000 (Enter) }    {btn: Back Now (Esc) }",
        ""], 56, "w")]
    L += [blank] * 8
    L += [hint("{a:Enter} {d:keep it (then F10 saves it)}  ·  {a:Esc} {d:back now}")]
    return pad(L)


# ---- Save -------------------------------------------------------------------------------------------

def s_save():
    L = header("Night Light", right="KognogOS · javier · 2 changes waiting")
    L += [blank,
          line("  {v b:Save the night light settings?}"),
          blank,
          line("  {m:Change                     Before                    After}"),
          line("  {d:──────────────────────────────────────────────────────────────────────}"),
          line("  Evening warmth             4000 K                    {ok:3500 K}"),
          line("  When                       by the sun, Miami         {ok:fixed: 21:00 → 07:00}"),
          blank,
          line("  {m:Written to}   ~/.config/nightforge/settings.toml"),
          line("  {m:Backup first} ~/.config/nightforge/backups/          {d:the last 20 are kept}"),
          line("  {m:Then}         the night light restarts with them: {b:at once}, and at every login"),
          blank,
          line("                                {pri: Save (Enter) }    {btn: Back (Esc) }"),
          blank,
          hint("{a:Enter} {d:save}  ·  {a:Esc} {d:back}")]
    return pad(L)


# ---- The bar ----------------------------------------------------------------------------------------

def s_bar():
    """The top bar's right side, with the moon while the screens are warm."""
    L = [line(" {v b:◆} {m:1}  Workspaces  Favorites            " + " " * 18 +
              "{w:☾}  {m:🔊 40%}  {m:⇅ wired}  {m:ᛒ}  {m:⏏}  {m:Fri 19:42}  {m:⏻}", "hdr")]
    return L


SCREENS = {"night": s_night(), "schedule": s_schedule(), "preview": s_preview(), "save": s_save()}

if __name__ == "__main__":
    for k, v in SCREENS.items():
        print(k, len(v), "lines")
