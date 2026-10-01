# Test Matrix — forgekit v0.4.0 (console mode)

*2026-10-01. The promise under test (issue #1): every Forge app is **readable and usable on a plain text console (`TERM=linux`)**; it does not have to look the same as in a terminal window. And in a terminal window, **nothing changes**.*

| # | Area | Check | How |
|---|---|---|---|
| 1.1 | Detection | `TERM=linux` → console mode; terminal windows (`xterm-256color`, `alacritty`, `xterm-kitty`, `tmux-256color`, empty) → not | tests `Detection` |
| 1.2 | Override | `FORGE_ASCII=1` forces on, `FORGE_ASCII=0` forces off, anything else falls back to `TERM` | tests `Detection` |
| 2.1 | Characters | every fallback is drawable by the console font and no wider than the original | tests `CharacterSwaps` |
| 2.2 | Characters | swaps keep the width (columns stay aligned), including two-cell emoji | tests `CharacterSwaps` |
| 2.3 | Characters | accents the font lacks fall back to the letter (`Á` → `A`); `ñ é ü` kept | tests `CharacterSwaps` |
| 2.4 | Glyph table | `glyph()` follows the mode; every console form drawable | tests `CharacterSwaps` |
| 3.1 | Colours | same roles in both modes; window mode = Catppuccin | tests `ColourRoles` |
| 3.2 | Colours | console uses only console colours, never bright backgrounds, no bold on coloured blocks, no rounded corners | tests `ColourRoles` |
| 3.3 | Colours | the active menu item is not cyan on the console (its underlined letter is drawn cyan there) | tests `ColourRoles` |
| 4.1 | App | layout positions identical in both modes (title row 0, menu row 1, work area row 2, every menu item's x and width) | tests `AppInBothModes` |
| 4.2 | App | console app: flag, scrollbar drawer, glyph filter, console colours, ANSI colour mode all on; Textual's own `console` attribute untouched | tests `AppInBothModes` |
| 4.3 | App | window app: none of that switched on; screen background `#1e1e2e` | tests `AppInBothModes` |
| 4.4 | Keys | F1 opens Help in both modes (F-10) | tests `AppInBothModes` |
| 5.1 | Console emulation | demo main view, menu, edit window, About (via F1): only console-font characters, no letter in its own background colour | tests `ConsolePreview` (`tools/console-preview.py`) |
| 6.1 | Window look | the four README screenshots regenerate identical to v0.3.0 | `docs/screenshots/generate.py`, compared apart from Textual's random ids |
| 6.2 | Packaging | the AUR `check()` smoke (import the API, mount a minimal app) passes, in both modes | the PKGBUILD's check, run by hand |
| 7.1 | **Real console** | the demo on tty3 of the KognogOS VM: menus, edit window, F1 → Help, About; no stray characters; every letter visible | VM test (`CLAUDE.md`), `tools/vcsa-shot.py` |
| 8.1 | Failing direction | the guards fail when they should: the `console` naming bug, a disabled character swap, and the v0.3.x colours each make tests fail | code broken on purpose, then restored |
