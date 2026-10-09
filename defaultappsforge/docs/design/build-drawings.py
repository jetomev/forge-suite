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
    items = [("Kinds", "K"), ("File Types", "F"), ("Help ▾", "H"), ("Quit", "Q")]
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





# ---- 1 · Kinds ---------------------------------------------------------------------------------------
# (kind, opens with, status) — today on Javier's desktop (xdg-mime + ~/.config/mimeapps.list, 2026-10-09)
KINDS = [
    ("Web browser", "Google Chrome", "mine"),
    ("Email", "Thunderbird", "guess"),
    ("Files & folders", "Thunar", "mine"),
    ("Text & code", "Fresh", "mine"),
    ("PDF", "Google Chrome", "guess"),
    ("Pictures", "Pinta · Google Chrome", "mixed"),
    ("Music", "mpv", "guess"),
    ("Video", "mpv", "guess"),
    ("Documents & sheets", "ONLYOFFICE", "guess"),
    ("Archives", "Ark", "kde"),
]
STATUS = {"mine": "{ok:✓ your choice}", "guess": "{m:~ the system's guess}", "mixed": "{w:◐ split: 2 apps}",
          "kde": "{w:⚠ leaves with KDE}", "gone": "{er:⚠ app is gone}"}


def table_row(kind, app, status, sel=False, shade=False):
    txt = f"  {kind:<22}{app:<26}"
    st = STATUS[status]
    row = txt + st + " " * (26 - len(vis(st)))
    if sel:
        return "{sel:" + txt + "}" + st + "{sel:" + " " * (26 - len(vis(st))) + "}"
    return "{fld:" + txt + "}" + st + "{fld:" + " " * (26 - len(vis(st))) + "}" if shade else row


def s_kinds():
    L = header("Kinds")
    L += [blank]
    L += [line("  " + r) for r in box("Needs attention", [
        "{w:⚠} {b:3 old choices point to apps that are gone:} Typora, Nemo, Brave",
        "{w:⚠} {b:Ark} (archives) and {b:Konsole} (shell scripts) leave with KDE: pick others before it goes",
        "{d:Saving tidies the old choices away; nothing else changes unless you pick it.}"], 96, "w")]
    L += [blank,
          line("  {b:Kind ▲                Opens with                Status}" + " " * 22 + "{d:Show}  {fld: All ▾ }"),
          line("  {d:" + "─" * 94 + "}")]
    for i, (k, a, s) in enumerate(KINDS):
        L.append(line(table_row(k, a, s, sel=(k == "PDF"), shade=i % 2 == 1)))
    L += [blank, line("  {btn: Change… (Enter) }  {d:pick the app for the highlighted kind}")]
    L += [blank, hint("{a:↑ ↓} {d:pick}  ·  {a:Enter} {d:change}  ·  {a:F10} {d:save}  ·  {a:1-3} {d:menu}  ·  {a:F1} {d:help}")]
    return pad(L)


# ---- Change: a pop-up ------------------------------------------------------------------------------

def s_pick():
    L = header("Kinds")
    L += [blank] * 3
    rows = ["",
            "{b:These can open PDFs:}",
            "",
            "{sel:  (•) Master PDF Editor                                        }",
            "  ( ) Zathura                {d:light, keyboard-driven}",
            "  ( ) Okular                 {w:leaves with KDE}",
            "  ( ) ONLYOFFICE",
            "  ( ) Google Chrome          {d:now, the system's guess}",
            "  ( ) GIMP",
            "",
            "{d:Applies to every PDF. A kind with many file types (Pictures: PNG, JPEG,}",
            "{d:GIF, WebP, SVG…) sets each one the app can open; the others stay.}",
            "",
            "            {pri: Use Master PDF Editor (Enter) }    {btn: Cancel (Esc) }",
            ""]
    L += [line("        " + r) for r in box("PDF: open with…", rows, 82)]
    L += [blank] * 2
    L += [hint("{a:↑ ↓} {d:pick}  ·  {a:Enter} {d:use it}  ·  {a:Esc} {d:cancel}")]
    return pad(L)


# ---- 2 · File Types ---------------------------------------------------------------------------------

def s_types():
    L = header("File Types")
    L += [blank,
          line("  {d:Every file type one by one, for the ones a kind doesn't cover.}" + " " * 4 + "{d:Find} {fld: image     }  {fld: All ▾ }"),
          blank,
          line("  {b:Type ▲                     Example     Opens with           Status}"),
          line("  {d:" + "─" * 94 + "}")]
    rows = [("image/bmp", ".bmp", "Pinta", "mine"), ("image/gif", ".gif", "Google Chrome", "guess"),
            ("image/jpeg", ".jpg", "Pinta", "mine"), ("image/png", ".png", "Pinta", "mine"),
            ("image/svg+xml", ".svg", "Pinta", "guess"), ("image/webp", ".webp", "Google Chrome", "guess")]
    for i, (t_, ex, app, st) in enumerate(rows):
        txt = f"  {t_:<27}{ex:<12}{app:<21}"
        s = STATUS[st]
        L.append(line(("{sel:" + txt + "}" + s) if t_ == "image/gif" else (("{fld:" + txt + "}" + s) if i % 2 else txt + s)))
    L += [blank, line("  {m:6 of 1,129 types}   {btn: Change… (Enter) }  {btn: Back to the System's Guess (d) }")]
    L += [blank, hint("{a:↑ ↓} {d:pick}  ·  {a:Enter} {d:change}  ·  {a:d} {d:system's guess}  ·  {a:F10} {d:save}  ·  {a:F1} {d:help}")]
    return pad(L)


# ---- Save: a pop-up ----------------------------------------------------------------------------------

def s_save():
    L = header("Kinds", right="KognogOS · javier · 3 changes waiting")
    L += [blank] * 3
    L += [line("      " + r) for r in box("Save your default apps?", [
        "",
        "{m:Change                    Before                 Now}",
        "{d:────────────────────────────────────────────────────────────────────────}",
        "PDF                       Google Chrome (guess)  {ok:Master PDF Editor}",
        "Pictures (GIF, WebP)      Google Chrome (guess)  {ok:Pinta}",
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


SCREENS = {"kinds": s_kinds(), "pick": s_pick(), "types": s_types(), "save": s_save()}

if __name__ == "__main__":
    for k, v in SCREENS.items():
        print(k, len(v), "lines")
