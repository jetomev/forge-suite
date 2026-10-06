"""displayForge · the screens drawn as they sit on the desk, any layout, to scale.

Pure text: each switched-on screen becomes a box placed by its real position and size (D-2:
four in a row, three over three, one under another — whatever Sway has). A character cell is
about twice as tall as wide, so heights are halved. The picked screen is drawn in the accent.
Returns lines of Rich markup; colours are forgekit's roles.
"""

from __future__ import annotations

from rich.markup import escape

from . import screens as S


def draw(screens: list[S.Screen], labels: dict[str, list[str]], picked: str | None = None,
         width: int = 86, max_height: int = 12) -> list[str]:
    on = [s for s in screens if s.on]
    if not on:
        return ["[$forge-muted]No screen is on.[/]"]
    x0 = min(s.x for s in on)
    y0 = min(s.y for s in on)
    x1 = max(s.x + s.extent[0] for s in on)
    y1 = max(s.y + s.extent[1] for s in on)
    # one column per `k` pixels across, one row per `2k` pixels down (cells are ~2:1)
    k = max((x1 - x0) / width, (y1 - y0) / (2 * max_height), 1e-9)
    cols, rows = int(round((x1 - x0) / k)), int(round((y1 - y0) / (2 * k)))
    grid = [[" "] * (cols + 1) for _ in range(rows + 1)]
    style = [[""] * (cols + 1) for _ in range(rows + 1)]

    boxes = []
    for s in on:
        # edges from the same rounding, so neighbours always end up exactly one column apart
        cx = int(round((s.x - x0) / k))
        cy = int(round((s.y - y0) / (2 * k)))
        right = int(round((s.x + s.extent[0] - x0) / k))
        bottom = int(round((s.y + s.extent[1] - y0) / (2 * k)))
        cw = max(6, right - cx - 1)                       # the column at `right - 1` stays a gap
        ch = max(3, bottom - cy)
        boxes.append((s, cx, cy, cw, ch))

    for s, cx, cy, cw, ch in boxes:
        tone = "$forge-accent" if s.name == picked else "$forge-muted"
        for x in range(cx, min(cx + cw, cols + 1)):
            for y, c in ((cy, "─"), (min(cy + ch - 1, rows), "─")):
                grid[y][x], style[y][x] = c, tone
        for y in range(cy, min(cy + ch, rows + 1)):
            for x, c in ((cx, "│"), (min(cx + cw - 1, cols), "│")):
                grid[y][x], style[y][x] = c, tone
        last_x, last_y = min(cx + cw - 1, cols), min(cy + ch - 1, rows)
        for (x, y), c in (((cx, cy), "╭"), ((last_x, cy), "╮"), ((cx, last_y), "╰"), ((last_x, last_y), "╯")):
            grid[y][x], style[y][x] = c, tone
        inner = labels.get(s.name, [s.name])
        room = cw - 2
        top = cy + max(1, (ch - len(inner)) // 2)
        for i, text in enumerate(inner):
            y = top + i
            if y >= last_y:
                break
            text = text[:room]
            sx = cx + 1 + (room - len(text)) // 2
            for j, c in enumerate(text):
                grid[y][sx + j] = c
                style[y][sx + j] = "$forge-accent b" if (i == 0) else "$forge-text"

    out = []
    for y in range(rows + 1):
        line, cur, run = [], None, []
        for x in range(cols + 1):
            st = style[y][x]
            if st != cur and run:
                text = escape("".join(run))
                line.append(f"[{cur}]{text}[/]" if cur else text)
                run = []
            cur = st
            run.append(grid[y][x])
        if run:
            text = escape("".join(run))
            line.append(f"[{cur}]{text}[/]" if cur else text)
        out.append("".join(line).rstrip())
    while out and not out[-1].strip():
        out.pop()
    return out
