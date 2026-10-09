# displayForge — the list

**1.1.0 released 2026-10-08** (his runs inside hypeForge Settings: keys, Try/Save where they belong, a real question before quitting, pages for Help); before it **1.0.1 released 2026-10-06** (Sway only, D-5), after 1.0.0 the same morning (D-4). Next: 1.1.x tests (one and two screens, 80 / 90 %, text console). A Forge Suite app (terminal, forgekit) for screen settings on Sway: arrange, resolution, refresh rate, scale, rotation, on / off, main screen, brightness. Section of the Forge Suite (D-60). Updated after every step.

## At the next release
- [ ] **The AUR description, at the next release** (Javier, 2026-10-09): the AUR `pkgdesc` (and `.SRCINFO`) gets the same "where it runs" words as the README, GitHub About and kognogos.org — distribution · desktop · plain text console. Not pushed on its own: AUR pushes stay one per proven version.

## Phase 0 · Research and design
- [x] Name: **displayForge** (Javier, 2026-10-05)
- [x] Research: `docs/research/2026-10-05-displayforge.md` — Sway's per-screen settings, brightness via ddcutil without a password, **identical screens can't be told apart by software → an Identify step**, keep-or-revert countdown
- [x] Screen designs (100-column terminal drawings, the alacrittyForge / grubForge pattern) → **approved by Javier** (D-2: "Wow!!!! I love what you have done! Let's go!" — with any arrangement, sizes 80/90 %, brightness in tens, HDR only where supported, screen names) — drawn 2026-10-05: `docs/design/v0.1.0-screens.html` (published privately: https://claude.ai/artifact/NX3YSPKvbcgL7dayRnLoHg), seven screens (Screens, Settings, Keep or go back, Arrange, Brightness, Identify, Save) + seven questions for Javier.

## Phase 1 · Build (after the design is approved)
- [x] **Engine step 1 — `displayforge/screens.py`** (2026-10-05): read screens from Sway; only real sizes / rates; exact `output …` commands for a change (HDR / adaptive sync only where supported); the saved-file lines; place left / right / above / below with edges snapped and **the others make room**; overlaps found. **20 tests** (`tests/test_screens.py`: Javier's real three Sceptres, serial blanked; 1, 4, 6 screens; a fourth under screen 1; rotated; 80 %)
- [x] **Engine step 2** (2026-10-05): `trial.py` — try a change live, undone by itself unless kept, through an **independent safety timer** (a separate process: the undo happens even if displayForge freezes or dies); `saving.py` — `~/.config/sway/outputs`, backup first (20 kept), written all-or-nothing, `included()` checks Sway reads it; `brightness.py` — ddcutil, steps of ten, Identify's names and which control is which screen. **35 tests, 0 warnings** (the safety timer tested in the failing direction, including displayForge dying mid-countdown)
- [x] **App, first part** (2026-10-06, night): `app.py` on forgekit — the frame and menu; **Screens** (the layout drawn to scale from real positions — any layout, `drawing.py`; the picked screen; All good / Needs attention); **Settings** form (On, Resolution dropdown, Refresh rate, Size 80–200 %, Rotation, Smooth motion, HDR only where supported; changed marks); **Try (F9)** with the **keep-or-go-back countdown dialog**; **Save (F10)** with a plain-words review against the last save. Checked as pictures rendered in memory with a fake Sway (nothing on Javier's screens). Bugs found and fixed: form rebuilt before the old one was gone (DuplicateIds); the review spoke Sway's language; **a default path fixed at import time sent a test save to the real ~/.config/sway/outputs** (not read by Sway; removed, paths now resolved at call time, a test guards it). 36 tests
- [x] **Arrange, Brightness, Identify** (2026-10-06, night): Arrange — arrows move the picked screen (others make room), Tab picks the next, Put it / Of / Line up; Brightness — one row per screen in tens + All screens (from a real reading), at once via ddcutil; Identify — dims one control at a time (0 → back to what it was), "which went dark?" by where the screens physically sit, remembered; names. **The design's big numbers on each screen were left out of 0.1.0** (needs a window drawn per monitor; the Screens drawing shows which is which) — Javier may push back. Fixed in the walk-through: empty Of choice, run-together words, planned instead of physical places, a made-up starting brightness
- [x] **tests/test_app.py**: the app driven in memory (fake swaymsg + ddcutil, throwaway folders; each test checks the real files are untouched) — **41 tests, 0 warnings**
- [x] `include ~/.config/sway/outputs` in hypeForge's sway/config (checked: a missing file is skipped quietly); a warning after a save if the line is missing (2 tests)
- [x] **F-1 (Javier's first real run, 2026-10-06):** everything worked until he typed a screen name — the first letter closed the app. A helper named `_name` hid Textual's own `_name` on every widget. Renamed; a typing test and a permanent name-clash check (that would have caught it) added. 43 tests
- [x] **F-2 (Javier's run):** after Identify the screens stayed dark. Cause: during each 3-second dim the previous round's answer buttons were still up, and clicking one cancelled the running step before its restore. Fix: no answer buttons while a screen is dark; each dim + restore runs in its own process (`brightness.dim`), so nothing in the app can skip the restore; the restore is read back and retried. Tests in the failing direction (step cancelled mid-dim, a screen that ignores two restores, one that never comes back). 47 tests
- [x] **F-3 (Javier's run): no manual in Help** — 7 pages (start, Screens, Settings, Arrange, Brightness, Identify, where things are kept); Help → Manual and the M key; test that it opens. 48 tests
- [x] **1.0.0 released** (2026-10-06): README with pictures (`scripts/make-screenshots.py`), CHANGELOG, ROADMAP, D-3 + D-4, testing/ matrix + results, tag `displayforge-v1.0.0`, GitHub Release, issues for F-1..F-3. **50 tests, 0 warnings**

## 1.1.0 · Javier's run inside hypeForge Settings (2026-10-08)
- [x] **F-4 (#50):** the underlined letters were not shortcuts → forgekit 0.10.0 makes Ctrl + each letter and 1-6 (Help included) from the menu; displayForge's own number keys removed; "1-6 menu" in the bar
- [x] **F-5 (#51):** Try / Save only on Settings and Arrange (per-page bottom row; elsewhere F9 / F10 and the bar only remind); **"Apply your changes before quitting?"** (Yes = try with the countdown, then save; No = quit; Esc = stay), also for kept-but-not-saved; **found on the way: the bar's Save button had no handler since 1.0.0**, fixed
- [x] `--hypeforge` (forgekit reads it), button labels as "Try It (F9)", version 1.1.0 in README / CHANGELOG / ROADMAP / manual / CLAUDE.md; `testing/20261008 - Test Matrix … v1-1-0.md`. **63 tests (was 54), 0 warnings**; each new test seen failing with its fix taken out
- [x] **Released 2026-10-08**: tag `displayforge-v1.1.0`, GitHub Release (Latest); #50 #51 closed; Javier: "all perfect!"

## 1.1.x · the tests not run yet
- [x] **Sway only, said and checked — built 2026-10-06** (Javier; https://github.com/jetomev/forge-suite/issues/32) on forgekit 0.7.0's start-up check (#33): `needs()` = a Sway session (required) + ddcutil (optional: Brightness and Identify); `main()` shows the shared screen and returns 2 when it can't start. Said everywhere: README, manual page 1, About, launcher entry, suite README, KognogOS README; kognogos.org at the release. **54 tests (was 50), 0 warnings.** Version 1.0.1 on main
- [x] **1.0.1 released 2026-10-06 evening**: Javier's run of the check screen (forgekit's example, 17:57) PASS; `python-forgekit` 0.7.0 installed from the AUR (18:37); tag `displayforge-v1.0.1`, GitHub Release, suite README, KognogOS README, kognogos.org; the launcher entry back on the installed forgekit. Still to run by Javier: the launcher from a KDE login (expect the screen) — not tonight, he did not want to close everything
- [x] **Javier, 2026-10-06 evening, on the real screens:** Arrange "worked as I expected, no issues"; Identify "worked wonders" (the F-2 re-run: the screens come back) — the last piece of his own 1.0 testing
- [ ] One and two screens (test VM)
- [ ] Sizes 80 / 90 % on real apps (X11 apps blur at non-whole sizes)
- [ ] Plain text console, 100 columns; the drawing's right edge in a real terminal
- [ ] The status bar under the keep dialog still says "not tried yet" while the countdown runs (seen in the screenshots)

## Later
- [ ] Profiles (switch layouts when screens are plugged in / out)
- [ ] A page in hypeForge Settings
- [ ] AUR package (after forgekit moves into the Forge Suite)
- [ ] Night light · big numbers during Identify (D-3)
