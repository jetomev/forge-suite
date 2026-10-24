# displayForge — changelog

*Newest first.*

## 1.1.2 — 2026-10-24 · tested on one and two screens; 80 / 90 % works beside other screens

Javier's run of the stage-03 tests ([the matrix](../testing/20261024%20-%20Test%20Matrix%20for%20displayForge%20v1-1-2.md), [the results](../testing/20261024%20-%20Test%20Results%20for%20displayForge%20v1-1-2.md)): one and two screens in a virtual machine, 80 / 90 % on real apps, a plain text console — every row passed, after F-10 was fixed during the run.


- **The bar tells the truth during the countdown** ([F-8 #121](https://github.com/jetomev/forge-suite/issues/121)): while "Keep these settings?" counts down, the bar under it says *Trying 1 change on your screens · keep them or go back in the window*. It used to say "not tried yet" until you answered.

- **A screen that lists no sizes no longer crashes Settings** ([F-9 #125](https://github.com/jetomev/forge-suite/issues/125)): a virtual screen (what screen-sharing tools add to Sway) reports the size it is at but no list; the Resolution drop-down came out empty and the app stopped. The form now offers the size the screen is at. Found by the new screens bench.
- **80 % and 90 % work on a screen with neighbours** ([F-10 #126](https://github.com/jetomev/forge-suite/issues/126), found in Javier's test run): a smaller size gives a screen more desktop, and it grew into the screen beside it — displayForge said *these screens overlap* and changed nothing. Now when a screen's room changes (size of things, resolution, rotation) the screens to its right and below slide by the same amount: no overlap, and no gap when it shrinks.
- **A screens bench** (`scripts/screens-bench.py`, for the people building it): a screen-less Sway with one, two and three fake screens; the real engine tries 80 % and 90 % sizes and a new arrangement through the countdown and checks Sway after each answer, and the app is photographed at 100 columns. 43 / 43 (it resizes the leftmost screen now: resizing only the rightmost had missed F-10).

Tests: 66 → **72**. Warnings: 0 → 0.

## 1.1.1 — 2026-10-11 · one-screen computers start again, and the AUR package builds on any machine

- **Computers with one screen crashed at start** ([F-6 #58](https://github.com/jetomev/forge-suite/issues/58)): Textual 8 changed what an empty choice is (`Select.BLANK` is False now), and the one-screen path used the old one. Fixed with `Select.NULL` (`9648068`).
- **The AUR package builds on any machine** ([F-7 #92](https://github.com/jetomev/forge-suite/issues/92)). Found by the Forge Suite's dependency audit ([#91](https://github.com/jetomev/forge-suite/issues/91)), which built every AUR recipe in a clean Arch system: **1.1.0 failed to build where ddcutil isn't installed**. A start-up test expected the message for one missing need; without the optional ddcutil the app correctly names two. The test now pins ddcutil (it's about Sway), and a new test covers both missing.
- The package now depends on **python-rich**, which the code imports directly (it only came through Textual).
- What the package needs, with why: [docs/PACKAGING.md](PACKAGING.md), kept honest by a test that fails on any import not listed there.
- Nothing changes in the app itself.

Tests: 63 → **66** (the both-missing start-up test, the needs list; the old start-up test fails without ddcutil). Warnings: 0 → 0.

## 1.1.0 — 2026-10-08 · keys, Try and Save where they belong, and a real question before quitting

From Javier's run of displayForge inside hypeForge Settings ([F-4 #50](https://github.com/jetomev/forge-suite/issues/50), [F-5 #51](https://github.com/jetomev/forge-suite/issues/51)).
- **Every underlined letter is a shortcut:** Ctrl+S Screens, Ctrl+E Settings, Ctrl+A Arrange, Ctrl+B Brightness, Ctrl+I Identify, Ctrl+H Help. **Help has a number (6)**, and the bottom bar says **"1-6 menu"** instead of "1-5 screens". All of it comes from forgekit 0.10.0, which makes the keys from the menu itself; displayForge's own number keys are gone.
- **From Javier's second run:** Help's number (6) pressed again closes it; the open menu's title is lit; **About, License, Keys and the manual open as pages** in the work area instead of windows (Esc goes back). The letters follow Javier's rule (the first letter of the name, else the next free one); for displayForge they stay the same.
- **Try (F9) and Save (F10) belong to Settings and Arrange**, the pages that change something. Elsewhere the keys only remind you, and so does the bar at the bottom: "2 changes not tried yet · finish them in Settings (2) or Arrange (3)".
- **A real question before quitting:** "Apply your changes before quitting?" **Yes** tries them with the countdown, then saves; **No** quits without them; **Esc** stays. It also asks about changes that were kept on screen but **not saved**, which quitting used to lose silently.
- **The Save button in the bar works.** It never had anything behind it: only F10 saved.
- **`--hypeforge`** (or `--hypeForge`): how hypeForge Settings starts displayForge. No Quit, and Q and Ctrl+Q do nothing; Settings asks the question above when it closes. Meant for Settings only; written down here, in the README and in the manual.
- **Button labels as "Words (key)":** Try It (F9), Save Changes (F10), Discard Changes, Keep It (Enter), Go Back Now (Esc), None of Them, Dim It Again.
- **Needs forgekit 0.10.0.**
- **Tests: 63 (was 54), warnings: 0 (was 0).** Four older tests now open Settings before trying a change. Each new test was checked by taking its fix out and watching it fail.

## 1.0.1 — 2026-10-06 · Sway only, said and checked ([forge-suite #32](https://github.com/jetomev/forge-suite/issues/32))

Javier, the night 1.0.0 shipped: displayForge must say clearly it works on Sway only, and check at launch — if not Sway, say why, with only a Close button. Until now it would have crashed on KDE with an error dump.
- **A start-up check**, on forgekit 0.7.0's shared one ([#33](https://github.com/jetomev/forge-suite/issues/33)): a Sway session, required; `ddcutil`, optional (Brightness and Identify need it; the screen offers Continue Anyway). On anything else — KDE, GNOME, Hyprland, a text console, a terminal over SSH — one plain screen: what it needs, what was found instead ("KDE Plasma (Wayland)"), why, what to use; **Close (c)**; the same words in the terminal afterwards. Nothing touched.
- **"Sway only" said everywhere:** README, the manual's first page, About, the launcher entry, the suite README, the KognogOS README.
- **Needs forgekit 0.7.0 or newer** (`python-forgekit` on the AUR, released the same day).
- **Tests: 54 (was 50), warnings: 0** (was 0): a fake KDE session, a Sway socket that doesn't answer, a live one, and `main()` closing without starting the app.

## 1.0.0 — 2026-10-06 · the first release

**Everything the approved design asked for** ([D-2](DECISIONS.md)), declared done by Javier ([D-4](DECISIONS.md)).
- **Screens** drawn to scale, any layout; the main screen (★); All good / needs attention.
- **Settings** per screen: on/off, resolution, refresh rate, size 80–200 %, rotation, smooth motion, HDR where supported — only real options.
- **Arrange**: the arrow keys move a screen, the others make room, edges snap, overlaps refused.
- **Brightness** in tens, per screen and for all, through ddcutil (no password).
- **Identify**: one screen dark at a time, "which one?", remembered; **names**.
- **Try (F9)** with a 12-second keep-or-go-back countdown run by an independent process; **Save (F10)** with a plain review and a backup (20 kept).
- **The manual** (M), seven pages.
- **Fixed from Javier's first run:** F-1 typing a name closed the app · F-2 screens stayed dark after Identify · F-3 no manual.
- **After a save, a warning if Sway would not read the file** (the include line missing).
- **Tests: 50, warnings: 0** (first release, so no earlier count to compare).
- **Not tested yet:** one and two screens, 80 / 90 % on real apps, text console — see the README.
