# Test Matrix — displayForge v1.1.2 (stage 03: one and two screens, 80 / 90 %, a text console)

*2026-10-24 · KognogOS road, stage 03 "The desktop, finished": the three displayForge cards not yet run — one and two screens, the 80 / 90 % sizes on real apps, a plain text console. Runs the code on `main` (F-8 #121 and F-9 #125 in it, not released yet): in the VM from its copy of the source, on the desktop with `python3 ~/Programs/forge-suite/displayforge/main.py`. Results go in a Test Results file next to this one; the release (1.1.2) comes after.*

**Never press Save (F10) during this run** on the desktop: every change here is tried and kept or undone, never saved, so the next login is as before no matter what.

## Claude's part, done first

| # | What | How | Who | Result |
|---|---|---|---|---|
| C1 | Automatic tests | `PYTHONPATH=../forgekit python -W always -m unittest discover -s tests`: 68 pass, 0 warnings | Claude | ✅ 2026-10-24 |
| C2 | One, two, three screens on the hidden bench | `scripts/screens-bench.py`: 80 % and 90 % on and back, Keep It keeps, a screen moved to the other side and back to its exact place; the app drawn at 100 columns for each | Claude | ✅ 31 / 31 — it found F-9 (a screen that lists no sizes crashed Settings), fixed |
| C3 | No Sway at all | started with no Sway reachable: the start-up check page says it needs a Sway session, Close quits | Claude | ✅ |
| C4 | The VM ready | snapshot `screens-test-before`; today's source copied in; Win + Enter opens a terminal; logs straight into Sway | Claude | ✅ |

## A · The test VM, one screen

Open it: virt-manager → `kognog-hypeforge` → Open. It is already logged in, a terminal open (Win + Enter opens another).

| # | What | How | Who | Result |
|---|---|---|---|---|
| A1 | Starts and draws one screen | in the VM's terminal: `cd ~/Programs/forge-suite/displayforge` then `python3 main.py` → one box, "Virtual-1", "All good · 1 screen on" | Javier | |
| A2 | Settings lists the sizes | press 2 → Resolution shows the VM's sizes; no crash | Javier | |
| A3 | 90 %, then Go Back | Size of things → 90 → F9: everything gets smaller; the bar under the window says "Trying 1 change on your screens…" (F-8) → Esc (Go Back Now): back to 100 % | Javier | |
| A4 | 80 %, then Keep | 80 → F9 → Enter (Keep It): stays at 80 %; then 100 → F9 → Enter: back to normal | Javier | |
| A5 | The countdown undoes it by itself | 90 → F9 → touch nothing: when the count reaches 0 it goes back on its own | Javier | |
| A6 | Quit asks | change something → Q → "Apply your changes before quitting?" → No: quits, nothing changed | Javier | |

## B · The test VM, two screens

Claude shuts the VM down, gives it a second screen and starts it again (virt-manager shows two display windows, or a menu to pick the second).

| # | What | How | Who | Result |
|---|---|---|---|---|
| B1 | Starts and draws two screens | `python3 main.py` again → two boxes side by side, "All good · 2 screens on", the main one starred | Javier | |
| B2 | Arrange: the other side, then Go Back | 3 (Arrange) → move screen 2 to the other side → F9: the two VM windows swap places → Esc: back as before | Javier | |
| B3 | One screen off, then Go Back | 2 (Settings) → pick screen 2 → On: off → F9: that window goes dark → Esc: it comes back | Javier | |
| B4 | Identify where screens can't answer | 5 (Identify): it says the screens can't be reached (VM screens have no brightness line), no crash | Javier | |

## C · Your desktop: 80 % and 90 % on real apps

Open a terminal, a Chrome window and an older app (Steam, or anything X11) on your main screen first.

| # | What | How | Who | Result |
|---|---|---|---|---|
| — | **F-10 #126, found on C5's first try** | "says these screens overlap and doesn't change to 90%": the middle screen grew into its neighbour; fixed (the neighbours slide), tests  (4) and the bench now resize the leftmost screen (43 / 43, fails on the old code with his message) | Claude | ✅ fixed, C5 again |
| C5 | 90 % on real apps | `python3 ~/Programs/forge-suite/displayforge/main.py` → 2 → your main screen → Size of things 90 → F9 → look: terminal and Chrome sharp, the older app slightly soft (what the note under the setting says) → Esc: back | Javier | |
| C6 | 80 % on real apps | same with 80 → look → Esc: back | Javier | |
| C7 | The bar and the pop-ups at 90 % | while at 90 % (F9, then Enter to keep it a moment): the bar, a pop-up from it, a notification look right → set 100 → F9 → Enter | Javier | |

## D · Your desktop: a plain text console

| # | What | How | Who | Result |
|---|---|---|---|---|
| D1 | No Sway here: it says so | Ctrl + Alt + F3 → log in → `python3 ~/Programs/forge-suite/displayforge/main.py` → the start-up check: "needs a Sway session" → Close | Javier | |
| D2 | Pointed at your running desktop: readable | same console: `env SWAYSOCK=(ls /run/user/1000/sway-ipc.*.sock) python3 ~/Programs/forge-suite/displayforge/main.py` → the three screens drawn in the console's colours; look at the boxes' right edge; **change nothing here** (you can't see the screens from a console) → Q | Javier | |
| D3 | Back to the desktop | `exit`, then Ctrl + Alt + F1 (or F2) | Javier | |
