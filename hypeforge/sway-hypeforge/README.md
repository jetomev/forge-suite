# hypeForge's own Sway build

*D-111 (Javier, 2026-10-17): "can the title bar have the right side icons for minimize, maximize/resize,
close?" — plain Sway can't (a left click on a title bar is Sway's own: it starts a drag), so hypeForge
patches Sway to draw them and act on their clicks, dragging untouched.*

## What is here

| File | What it does |
|---|---|
| `0001-titlebar-buttons.patch` | the change to Sway: two config lines (`titlebar_buttons none\|floating\|all`, `titlebar_button minimize\|maximize\|close <glyph> <command>`), the three symbols drawn at the title bar's right in its own colours, a left press on one runs its command (anything else on the bar still drags). 9 files, ~300 lines; off unless the config asks |
| `0002-titlebar-button-hover.patch` | the button under the pointer lights up: `titlebar_button_hover <bg> <text> <close bg> <close text>` — a square in the theme's hover colour, close in its red |
| `0003-seat-cursor-position.patch` | Sway's `get_seats` answer also says **where the pointer is** — `"cursor": {"x", "y"}` in layout pixels (D-116, 2026-10-20): a pop-up opens right under what was clicked. A new surface is told the pointer's place only once it moves, and plain Sway reports it nowhere (both measured); 12 lines in `ipc-json.c`. Stock Sway answers without it, and the pop-ups keep their old places |
| `0004-titlebar-background-pieces.patch` | the title bar's background is drawn in as many pieces as its texts cut it into (2026-10-27, F-87): Sway makes five, the title and the three buttons need seven, and the last two were never drawn — a see-through strip under the title bar and right of the close button. Bench: `scripts/titlebar-paint-bench.py` (magenta behind a floating window; any magenta inside its title bar fails) |
| `0005-mouse-cancels-held-release-binding.patch` | Win alone opens the launcher (D-123, 2026-10-27): Sway cancels a `bindsym --release` shortcut when another key joins in, but not when the mouse does — Win + a click or Win + drag (moving a window) opened the launcher on letting go of Win. A mouse button or a scroll now cancels it. Bench: `scripts/winkey-bench.py` (8 cases: Win alone, held, + Enter, + 1, + Shift + Q, + Space, + a click, + a drag) |
| `build.py` | the system's Sway version: download (github.com/swaywm/sway) → signature checked against Sway's release key → patches applied (stops if one no longer fits) → built → installed to `~/.local/opt/sway-hypeforge/<version>`, `current` pointing at it. Logs to `logs/sway-build-*.log` |
| `hypeforge-session` | the "Sway (hypeForge)" login (D-114; was the test entry "Sway (hypeForge buttons)"): our build only when it is the system's Sway version and starts; otherwise the system's Sway, the buttons off, and one notification saying so |
| `hypeforge.desktop` | that login's entry (`/usr/share/wayland-sessions/sway-hypeforge.desktop`) |
| `hypeforge-safe.desktop` | "Sway (hypeForge safe mode)": the stock Sway, the full setup, no buttons — the way in if our build misbehaves |
| `../sway/config-buttons` | what only our build reads: `include ~/.config/sway/config`, then the button lines and Win alone (it needs patch 5) |

## Why a Sway update can't break the desktop

- The system's Sway is never replaced or touched; ours lives in `~/.local/opt/sway-hypeforge/`.
- Stock Sway never reads the button lines (they'd be an error to it): they live in `config-buttons`.
- The login checks versions every time and falls back by itself (`tests/test_sway_session.py`).
- After an Arch update of Sway: run `build.py` again. If the patch no longer fits, it says so and the
  fallback keeps the desktop whole until the patch is brought up to date.

## Testing

`login-test.sh` (in a test VM, as its user — it refuses on a real desktop): the login starter three ways — versions match · a Sway update · our build broken. Proven on a clean KognogOS VM 2026-10-17 (`testing/`).


`scripts/titlebar-bench.py --ours` — our build on a hidden screen with the real button lines: drawn,
close · minimise · maximise and back, a drag beside them still moves the window.
