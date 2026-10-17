# hypeForge's own Sway build

*D-111 (Javier, 2026-10-17): "can the title bar have the right side icons for minimize, maximize/resize,
close?" — plain Sway can't (a left click on a title bar is Sway's own: it starts a drag), so hypeForge
patches Sway to draw them and act on their clicks, dragging untouched.*

## What is here

| File | What it does |
|---|---|
| `0001-titlebar-buttons.patch` | the change to Sway: two config lines (`titlebar_buttons none\|floating\|all`, `titlebar_button minimize\|maximize\|close <glyph> <command>`), the three symbols drawn at the title bar's right in its own colours, a left press on one runs its command (anything else on the bar still drags). 9 files, ~300 lines; off unless the config asks |
| `build.py` | the system's Sway version: download (github.com/swaywm/sway) → signature checked against Sway's release key → patches applied (stops if one no longer fits) → built → installed to `~/.local/opt/sway-hypeforge/<version>`, `current` pointing at it. Logs to `logs/sway-build-*.log` |
| `hypeforge-session` | the "Sway (hypeForge buttons)" login: our build only when it is the system's Sway version and starts; otherwise the system's Sway, the buttons off, and one notification saying so |
| `hypeforge-buttons.desktop` | that login's entry, for `/usr/share/wayland-sessions/` |
| `../sway/config-buttons` | what only our build reads: `include ~/.config/sway/config`, then the button lines |

## Why a Sway update can't break the desktop

- The system's Sway is never replaced or touched; ours lives in `~/.local/opt/sway-hypeforge/`.
- Stock Sway never reads the button lines (they'd be an error to it): they live in `config-buttons`.
- The login checks versions every time and falls back by itself (`tests/test_sway_session.py`).
- After an Arch update of Sway: run `build.py` again. If the patch no longer fits, it says so and the
  fallback keeps the desktop whole until the patch is brought up to date.

## Testing

`scripts/titlebar-bench.py --ours` — our build on a hidden screen with the real button lines: drawn,
close · minimise · maximise and back, a drag beside them still moves the window.
