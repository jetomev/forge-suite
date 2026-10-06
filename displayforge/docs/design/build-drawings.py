#!/usr/bin/env python3
"""Builds displayForge's design page: every terminal drawing exactly 100 columns, checked."""
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


def header(active, right="KognogOS · javier · changes apply live"):
    left = " {v b:displayForge 0.1.0}{m: · screen settings}"
    gap = W - len(vis(left)) - len(right) - 1
    top = line(left + " " * gap + "{m:" + right + "} ", "hdr")
    items = [("Screens", "S", 0), ("Settings", "e", 1), ("Arrange", "A", 0), ("Brightness", "B", 0),
             ("Identify", "I", 0), ("Help ▾", "H", 0), ("Quit", "Q", 0)]
    parts = []
    for name, letter, idx in items:
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
    for l in lines:
        pass
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

B = ""  # blank
blank = line("")

# ---- the three screens, drawn small ------------------------------------------------------------

def screens_drawing(sel=None, moved=False, rot=None):
    """Three 2560×1440 screens side by side: left DP-2 (2), middle DP-3 (1, main), right DP-1 (3)."""
    order = [("2", "DP-2", "left"), ("1", "DP-3", "main"), ("3", "DP-1", "right")]
    if moved:
        order = [("1", "DP-3", "main"), ("2", "DP-2", "left"), ("3", "DP-1", "right")]
    w = 22
    rows = []
    def box(num, name, part):
        hl = "a" if sel == name else "m"
        if part == "top":
            return "{" + hl + ":╭" + "─" * (w - 2) + "╮}"
        if part == "bot":
            return "{" + hl + ":╰" + "─" * (w - 2) + "╯}"
        inner = {"n": (f"★ {num}" if num == "1" else num), "c": name, "r": "2560 × 1440", "h": "144 Hz", "e": ""}[part]
        txt = inner.center(w - 2)
        style = "v b" if part == "n" else ("b" if part == "c" else "m")
        return "{" + hl + ":│}{" + style + ":" + txt + "}{" + hl + ":│}"
    for part in ("top", "e", "n", "c", "r", "h", "bot"):
        rows.append("        " + " ".join(box(n, nm, part) for n, nm, _ in order))
    places = ["left", "middle", "right"]
    labels = "        " + " ".join("{d:" + (places[i] + (" · main" if o[0] == "1" else "")).center(w) + "}"
                                    for i, o in enumerate(order))
    rows.append(labels)
    return rows


# ---- screens ------------------------------------------------------------------------------------

def s_screens():
    L = header("Screens")
    L += [blank]
    L += [line("  " + r) for r in box("Your screens", [r[6:] for r in screens_drawing(sel="DP-3")], 96)]
    L += [blank]
    L += side(box("Screen 1 · DP-3 · the main one", [
                "{m:Shows     } 2560 × 1440 at 144 Hz",
                "{m:Size      } 100 % · normal rotation",
                "{m:Brightness} 75 %",
                "{m:Workspaces} screen 1 of 3"], 47),
              box("All good", [
                "{ok b:✓} {b:3 screens, all on, nothing overlaps.}",
                "  {d:Saved settings match what you see.}",
                "",
                "  {btn: Identify screens }  {btn: Brightness }"], 47, "ok"))
    L += [blank, blank,
          hint("{a:← →} {d:pick a screen}  ·  {a:Enter} {d:its settings}  ·  {a:1-5} {d:screens}  ·  {a:F1} {d:help}  ·  {a:?} {d:all keys}")]
    return L


def s_settings():
    L = header("Settings")
    L += [blank,
          line("  {sel:  Screen 1 · DP-3     }{d:│} {v b:Screen 1}  {m:DP-3 · Sceptre Y27 · middle · the main one}"),
          line("    Screen 2 · DP-2     {d:│}"),
          line("    Screen 3 · DP-1     {d:│} {b:On}              {fld: ● On }  {d:switch this screen off (others stay on)}"),
          line("                        {d:│}"),
          line("                        {d:│} {b:Resolution}      {foc: 2560 × 1440  ▾ }  {d:what the screen offers: 7 sizes}"),
          line("                        {d:│}"),
          line("                        {d:│} {b:Refresh rate}    {btn: 144 }  {act: 120 Hz }  {btn: 100 }  {btn: 60 }  {d:Hz at 2560 × 1440}"),
          line("                        {d:│}"),
          line("                        {d:│} {b:Size of things}  {act: 100 % }  {btn: 125 % }  {btn: 150 % }  {btn: 200 % }"),
          line("                        {d:│}"),
          line("                        {d:│} {b:Rotation}        {fld: (•) Normal   ( ) 90°   ( ) 180°   ( ) 270° }"),
          line("                        {d:│}"),
          line("                        {d:│} {b:Main screen}     {fld: ● This is the main one }  {d:workspaces start here}"),
          line("                        {d:│}"),
          line("                        {d:│} {b:Brightness}      {fld:  75 }  {d:%}  {btn: 25 }{btn: 50 }{act: 75 }{btn: 100 }  {d:changes at once}"),
          line("                        {d:│}"),
          line("                        {d:│} {b:Smooth motion}   {fld: ○ Off }  {d:adaptive sync (FreeSync); some screens flicker}"),
          line("                        {d:│}"),
          line("                        {d:│} {pc:● changed} {d:· was 144 Hz — you will be asked to keep it}"),
          blank,
          line(" {pc:● 1 change not saved yet}                                            {pri: Try it…  F9 }  {btn: Save…  F10 }"),
          hint("{a:↑↓} {d:pick a screen}  ·  {a:Tab} {d:its settings}  ·  {a:F9} {d:try live}  ·  {a:F10} {d:save}  ·  {a:?} {d:all keys}")]
    return L


def s_arrange():
    L = header("Arrange")
    L += [blank, line("  {m:Move the picked screen with the arrows; the others make room. Edges snap together.}"), blank]
    for r in screens_drawing(sel="DP-2", moved=True):
        L.append(line(r))
    L += [blank,
          line("  {v b:Screen 2 · DP-2}  {d:now:} {b:right of screen 1}       {d:position} 2560, 0   {d:(was 0, 0)}"),
          blank,
          line("  {b:Put it}   {fld: ( ) left of 1   (•) right of 1   ( ) above 1   ( ) below 1 }"),
          line("  {b:Line up}  {fld: (•) tops   ( ) centres   ( ) bottoms }"),
          blank,
          line("  {d:Moving a screen does not change its number: workspaces still start on the main one (★).}"),
          blank, blank,
          line(" {pc:● screen 2 moved}                                                    {pri: Try it…  F9 }  {btn: Save…  F10 }"),
          hint("{a:← → ↑ ↓} {d:move it}  ·  {a:Tab} {d:next screen}  ·  {a:F9} {d:try live}  ·  {a:Esc} {d:put it back}  ·  {a:?} {d:all keys}")]
    return L


def s_brightness():
    L = header("Brightness")
    L += [blank, line("  {m:Brightness changes at once and is kept by the screen itself — nothing to save.}"), blank,
          line("  {b:Screen 2} {d:· left  }   {fld:▕█████████████████████████████▏          }  {b: 75 %}  {btn: − }{btn: + }"),
          blank,
          line("  {b:Screen 1} {d:· middle}   {foc:▕█████████████████████████████▏          }  {b: 75 %}  {btn: − }{btn: + }"),
          blank,
          line("  {b:Screen 3} {d:· right }   {fld:▕█████████████████████████████▏          }  {b: 75 %}  {btn: − }{btn: + }"),
          blank,
          line("  {b:All screens}         {btn: 25 % }  {btn: 50 % }  {act: 75 % }  {btn: 100 % }   {d:the same on every screen}"),
          blank,
          line("  {b:Night light}         {fld: ○ Off }  {d:warmer colours in the evening — a later version}"),
          blank, blank,
          line("  {d:Which screen is which was set in Identify (5 Oct). Wrong? Run Identify again.}"),
          blank, blank, blank, blank,
          hint("{a:↑↓} {d:pick a screen}  ·  {a:← →} {d:darker / brighter}  ·  {a:0-9} {d:set in tens}  ·  {a:?} {d:all keys}")]
    return L


def s_identify():
    L = header("Identify")
    L += [blank,
          line("  {m:Your three screens are the same model with the same serial number, so the computer cannot}"),
          line("  {m:tell them apart for brightness. This takes a few seconds and is remembered.}"),
          blank,
          line("  {b:Step 1}  A big number is now on every screen, as Sway sees them:"),
          blank,
          line("            {d:┌─────────┐}         {d:┌─────────┐}         {d:┌─────────┐}"),
          line("            {d:│}  {v b:  2  }  {d:│}         {d:│}  {v b:  1  }  {d:│}         {d:│}  {v b:  3  }  {d:│}"),
          line("            {d:└─────────┘}         {d:└─────────┘}         {d:└─────────┘}"),
          line("               {d:left}              {d:middle}              {d:right}"),
          blank,
          line("  {b:Step 2}  One screen goes {b:dark for 3 seconds}. Which one?"),
          blank,
          line("          {btn: The left one (2) }   {foc: The middle one (1) }   {btn: The right one (3) }   {btn: None }"),
          blank,
          line("  {d:Done 1 of 3 · then the next screen dims.}"),
          blank, blank,
          hint("{a:← →} {d:pick}  ·  {a:Enter} {d:that one}  ·  {a:R} {d:dim it again}  ·  {a:Esc} {d:stop (nothing changes)}")]
    return L


def s_keep():
    L = header("Settings")
    L += [blank, blank, blank]
    L += [line(" " * 20 + r) for r in box("Keep these settings?", [
        "",
        "Screen 1 now shows {b:2560 × 1440 at 120 Hz}.",
        "",
        "{w b:Going back in 12 seconds}, unless you keep it.",
        "{d:So a screen that went black fixes itself.}",
        "",
        "          {pri: Keep it }      {btn: Go back now }",
        ""], 58, "w")]
    L += [blank] * 7
    L += [hint("{a:Enter} {d:keep it}  ·  {a:Esc} {d:go back now}  ·  {d:no key for 12 seconds: it goes back by itself}")]
    return L


def s_save():
    L = header("Settings")
    L += [blank,
          line("  {v b:Save these screen settings?}"),
          blank,
          line("  {m:Setting                 Before                  After}"),
          line("  {d:────────────────────────────────────────────────────────────────────}"),
          line("  Screen 1 · refresh      144 Hz                  {ok:120 Hz}"),
          line("  Screen 2 · position     left of 1               {ok:right of 1}"),
          blank,
          line("  {m:Written to}   ~/.config/sway/outputs                {d:Sway reads it at every login}"),
          line("  {m:Backup first} ~/.config/displayforge/backups/      {d:the last 20 are kept}"),
          blank,
          line("  {d:Brightness is not part of this: the screens keep it themselves.}"),
          blank,
          line("                                    {pri: Save }    {btn: Back }"),
          blank, blank, blank, blank, blank,
          blank,
          hint("{a:Enter} {d:save}  ·  {a:Esc} {d:back to the settings}  ·  {d:after saving: a note with what was written}")]
    return L


SCREENS = {"screens": s_screens(), "settings": s_settings(), "arrange": s_arrange(),
           "brightness": s_brightness(), "identify": s_identify(), "keep": s_keep(), "save": s_save()}

if __name__ == "__main__":
    for k, v in SCREENS.items():
        print(k, len(v), "lines")
