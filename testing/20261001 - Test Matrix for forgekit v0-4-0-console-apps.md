# Test Matrix — forgekit v0.4.0 console mode, in the apps we already ship

*2026-10-01. Javier runs this himself, on the desktop's real text console (tty3), before grubForge moves onto forgekit: "Not before I test myself the console mode for the ones we already have. Remember, double check/testing is always needed."*

**Apps under test** (installed on `tphome-linux`, both on `python-forgekit 0.4.0-1` from the AUR):
- **bitlaForge 0.2.1**: Dashboard · Log · Config · Help (Shortcuts, Install & Setup, License, About) · Quit
- **alacrittyForge 0.2.0**: Dashboard · Config · Themes · Fonts · Bindings · Help (Shortcuts, License, About) · Quit

grubForge is not in this matrix: it is not on forgekit yet, so console mode does not reach it.

**How to get there:** on the desktop: `Ctrl+Alt+F3`, log in, run the app by name; back with `Ctrl+Alt+F1`. **In the KognogOS VM** (Javier's choice, 2026-10-01): Virtual Machine Manager → open `kognog-hypeforge` → menu *Send Key* → `Ctrl+Alt+F3`, log in as `javier`, run the app; *Send Key* → `Ctrl+Alt+F1` to leave.

**Do not, during the test:** start the miner (`M`), save in bitlaForge Config (`S`), apply a theme (`A`) or save (`S`) in alacrittyForge. Opening an editor and pressing `Esc` is fine; nothing is written until you save.

**What "pass" means** (the promise): every word readable; frames, menus and buttons visible; the selected item obvious; no diamonds, boxes, blank gaps or stray symbols; every key below does what it says.

## Known before the test (found by the preview sweep, Claude, 2026-10-01)
- **K-1 · bitlaForge Log and Config:** the frames around the log box and the input fields are drawn in the same grey as their background, so they cannot be seen; the fields still show as grey blocks with readable text. Cause: bitlaForge's own copy of the form colours (from before forgekit 0.3.0 took forms over). Fix belongs to bitlaForge (bitlaforge#2). **Javier: judge how bad it looks on the real console.** *Update after Claude's VM run: **not reproduced on a real console**: the real console does not show the grey (bright) field background, so the fields are black with visible thin frames. The emulation over-states it.*

## A · bitlaForge on tty3 (`bitlaforge`)

| # | Do | Expect | Result |
|---|---|---|---|
| A.1 | Start it | Blue title bar "BitlaForge" (the `⚡` shows as `!`); menu row with **Dashboard** on a **blue** block; Dashboard: "Miner state ○ stopped", section lines, **Start Miner** (cyan) and **Test Miner** (grey) buttons readable | |
| A.2 | Look at the menu row | Each option's first letter in **cyan** (the console's way of underlining), including the **D** of the active Dashboard | |
| A.3 | `2` (or `Ctrl+L`) | Log section; the log box (frame: see K-1) with readable lines | |
| A.4 | `3` (or `Ctrl+C`) | Config section: labels readable, fields as grey blocks with readable values (frames: see K-1); the Algorithm drop-down shows `▼` | |
| A.5 | In Config, `E`, then `Esc` | The Pool URL field gets the cursor. **Note:** Esc does *not* take the cursor out (bitlaForge today, in every terminal: B-1), so the next keys type into the field. Nothing is saved without `S`. Switch section with `Ctrl+L` / `Ctrl+D` (not bare digits) after editing | |
| A.6 | `F1` | Help menu opens: a box with **straight** corners, Shortcuts / Install & Setup / License / About, one highlighted in blue | |
| A.7 | `S` (in the Help menu) | Shortcuts window: keys in light blue, descriptions readable, Close button readable | |
| A.8 | `Esc`, `F1`, `I` | Install & Setup window readable, scrolls with ↑↓ if long, Close reachable | |
| A.9 | `Esc`, `F1`, `L` | License window readable | |
| A.10 | `Esc`, `F1`, `A` | About: name in pink, version, tagline in **plain grey** (not green), links in cyan | |
| A.11 | `Esc`, then `?` | The shortcuts window toggles open/closed (bitlaForge's own key) | |
| A.12 | `Ctrl+H` | Probably does nothing on the console (it arrives as Backspace: F-10). **Note what happens** | |
| A.13 | `Ctrl+Q` (or `Q`) | Quits cleanly back to the prompt, screen not garbled | |

## B · alacrittyForge on tty3 (`alacrittyforge`)

| # | Do | Expect | Result |
|---|---|---|---|
| B.1 | Start it | Blue title bar "AlacrittyForge"; Dashboard with Config file "+ Found", the path, Theme / Font / Opacity, Backups count; section lines | |
| B.2 | `2` (or `Ctrl+C`) | Config section: the settings table readable, the selected row obvious | |
| B.3 | In Config, select a row, `E`, then `Esc` | An editor opens anchored to the row; Esc closes it, nothing staged | |
| B.4 | `3` (or `Ctrl+T`) | Themes: the list readable, the selected theme obvious; `H` toggles the install guide | |
| B.5 | `4` (or `Ctrl+F`) | Fonts section readable | |
| B.6 | `5` (or `Ctrl+B`) | Bindings table readable | |
| B.7 | `F1`, `S` | Shortcuts window readable, Close readable | |
| B.8 | `Esc`, `F1`, `L` | License window | |
| B.9 | `Esc`, `F1`, `A` | About window, tagline plain grey | |
| B.10 | `Ctrl+Q` | Quits cleanly | |

## C · The same apps in a normal terminal (Alacritty, your desktop)

| # | Do | Expect | Result |
|---|---|---|---|
| C.1 | `bitlaforge` and `alacrittyforge` in Alacritty | **Exactly as before** today's release: Catppuccin colours, rounded corners, emoji in the title | |
| C.2 | `FORGE_ASCII=1 bitlaforge` in Alacritty | The console look inside Alacritty (the override works); quit with `Q` | |

## D · General impression

| # | Question | Answer |
|---|---|---|
| D.1 | Could you use these apps on a console to get something done? | |
| D.2 | Anything hard to read, confusing, or ugly enough to fix before grubForge moves over? | |
