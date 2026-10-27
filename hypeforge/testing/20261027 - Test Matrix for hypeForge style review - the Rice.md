# Test matrix: hypeForge style review, the Rice (KognogOS's default look)

KognogOS stage 04, "The four styles and their colours" (board card look-071: *"Full review of each style that ships: bar, launcher, tray, every pop-up. Step by step, your look on each piece."*). Started 2026-10-27; Javier chose the Rice first.

**How each piece is checked.** It is shot on the hidden screen (`scripts/style-preview.py --style rice --theme kognogos-mocha --scale 1 --click X,Y`) and put on a sheet in `logs/rice-review-20261027/`. Then Javier gives his call, and any fix goes through the benches. Last comes his look on the real desktop. The hidden screen has no wallpaper, no tray apps and no sound service, so those pieces are judged on the desktop.

| # | Piece | Sheet | Javier's call | Findings | Fixed |
|---|---|---|---|---|---|
| 1 | The bar: three areas (emblem + pills · date, time, bell · the system, clipboard, Quick Settings, power) | `sheet-1-bar.png` | **Approved** (2026-10-27): *"bar looks good to me"* | R-1: the middle area and the tray area still change width when the notification count or the clipboard count appears. *"It doesn't bother me that much… not as visible as the others were before."* Logged, not fixed. | — |
| 2 | The launcher (Win + Space, or a click on the emblem) | `sheet-2-launcher.png`; the seven launchers `launcher-sheet-A…G.png` | **Decided (D-118):** *"I would like to use G for rice too. Let's save A, as an option when we start adding theme edits"*: COSMIC's App Library | The list's four (4 px under the bar, square picked row, two gears, a grey star) go with the list into the theme options | `c322098`: Win + Space and the emblem open it (hidden screen, live code) |
| 1b | The bar's icon colour | `sheet-3-icon-colour.png` | **Asked (D-119):** *"Let's make the tray icons same colors as the elements of the other 2 islands… for all Rice themes, all the same"* | R-2: the right area's icons, the bell and the tray's one-colour icons wore the accent | the text colour in all 25 themes (test seen failing on the old colour) |
| 3 | The tray (programs' icons, their menus) | real desktop, at the end beside 13 | | | |
| 4 | Quick Settings + its pages (Wi-Fi, Bluetooth, Sound, Night light, Printer) | `sheet-4-quick-settings.png`, after: `sheet-4b-quick-settings-fixed.png` | **Fix 1 and 2 (D-120):** *"fix 1 and 2, go ahead. switches are the theme color, so good"* | R-3 icons mixed (one-colour beside full-colour; headphones dark on dark) · R-4 long sound names cut off · (the bench: stock icons on the hidden screen, fixed `e03cbe6`) | one-colour icons in the text colour, short names; 4 tests seen failing on the old code |
| 5 | The date, time and bell → alerts + calendar | | | | |
| 6 | The system pop-ups (disk, memory, temperature, graphics card, processor) | | | | |
| 7 | The clipboard | | | | |
| 8 | Power | | | | |
| 9 | The list cards (Workspaces, Favorites, USB drives, open apps) | | | | |
| 10 | Alt + Tab | | | | |
| 11 | Notifications | | | | |
| 12 | Windows: the frame, gaps, title bars on floating windows | | | | |
| 13 | The whole look on the real desktop | | | | |
