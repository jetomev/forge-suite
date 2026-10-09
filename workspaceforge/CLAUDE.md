# workspaceForge — section rules

*A Forge Suite app (D-60): the settings app for hypeForge's workspaces. Read the suite's `CLAUDE.md` first; this file adds what is particular here.*

- **One job: workspaces** (Javier, 2026-10-09: *"only workspaces, windows is another Forge app. I like atomized solutions"*). Names and order, the apps that open on each, sharing. Window placement and float rules are **not** here.
- **It edits, the applet works.** hypeForge's Workspaces applet (`hypeforge/applets/workspaces/`) does everything live; workspaceForge only edits `~/.config/hypeforge/applets/workspaces.toml` (a backup before every save) and tells the applet to re-read (`hypeforge-workspaces reload`). Workspaces keep working with workspaceForge closed or uninstalled.
- **A design is approved by Javier, screen by screen, before code is written** (`docs/design/`, built by `build-drawings.py` + `build-page.py`, every drawing checked at 100 columns).
- **Built on forgekit, the displayForge look:** title bar, menu bar with underlined letters, list left, page right, status and hint bars; colours only through forgekit's roles; readable on a text console and at 100 columns.
- **Keys come from the menu** (forgekit 0.10.0): Ctrl + each underlined letter and 1-N (Help included); no two entries share a letter. Buttons read "Words (key)". Quitting with unsaved changes always asks.
- **`--hypeforge`** (any case): how hypeForge Settings starts it — no Quit; documented in README, manual and CHANGELOG.
- **Any number of screens** (1 … 6+); never assume three. Nothing closes a window, ever.
- Packages through nog; decisions in `docs/DECISIONS.md` (D-n); TODO.md after every step; plain words.
- **Versioning:** own version, tags `workspaceforge-vX.Y.Z`, AUR `workspaceforge` when it ships (after Javier's local test).
- **Run and test:** `python3 main.py` (from this folder; forgekit from the system). Tests: `python3 -m unittest discover -s tests -t .` (headless, Textual's Pilot; report the count). Pictures: `python3 scripts/make-screenshots.py` (a copy of the real settings, nothing touched).
- **The hidden bench before going live** (hypeForge F-51 rule): any change to how saving moves windows (`model.window_moves`, `live.py`) passes `python3 scripts/bench-save.py` (a screen-less Sway, the real applet, a rename + swap + delete) before Javier uses it.

