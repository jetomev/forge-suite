# Test Matrix — workspaceForge v1.0.0 on one and two screens, and a text console

*2026-10-24 · KognogOS road, stage 03 "The desktop, finished": "workspaceForge: tested with one or two screens, and on a text console". The installed 1.0.0 (nothing changed in the app since). The test VM is a bare Sway without hypeForge's Workspaces applet, so one and two screens are tried **on the desktop, by switching screens off with displayForge** — the same thing as unplugging a monitor. Results go in a Test Results file next to this one.*

**Never press Save (F10) in displayForge during this run**: the screens are switched off with Try + Keep only, so the next login brings all three back whatever happens. In workspaceForge, Save is part of the test (one rename, undone at the end).

## Claude's part, done first

| # | What | How | Who | Result |
|---|---|---|---|---|
| C1 | The save on one, two and three hidden screens | `scripts/bench-save.py --screens 1`, `2`, `3`: a rename, a swap and a delete; every window follows its workspace; the applet keeps running; the screens stay steady | Claude | ✅ all three |
| C2 | Screens switched off and on under the applet | `hypeforge/scripts/screens-off-bench.py`: three screens → two → one → two → three; the applet alive, the screens steady, no window lost, after every step (and it reports FAIL when the applet is killed midway) | Claude | ✅ — seen: with one screen left it shows screen 3's copy of Daily, not its own |
| C3 | The app with one and two screens | drawn in memory: both open on the Workspaces page | Claude | ✅ — seen: with one screen, Daily still says "switches all your screens" |
| C4 | No Sway at all | the start-up check: "a Sway desktop, but no way to reach it"; Continue Anyway edits the file for the next login | Claude | ✅ |

## A · Two screens

| # | What | How | Who | Result |
|---|---|---|---|---|
| A1 | One screen off | `displayforge` → 2 (Settings) → pick your rightmost screen → On: off → F9 → Enter (Keep It). **Not F10.** | Javier | |
| A2 | Its windows moved over | the windows that were on it are now on the other two; the bar is fine on both | Javier | |
| A3 | The workspace keys | Win + 1 … Win + 4: both screens switch together; each shows that workspace | Javier | |
| A4 | workspaceForge sees it | `workspaceforge` → the list, the Sharing line and "Open now" read right for two screens | Javier | |
| A5 | A rename lands on both | rename Gaming → "Play" → F10 (Save) → the bar shows "Play" on both screens | Javier | |

## B · One screen

| # | What | How | Who | Result |
|---|---|---|---|---|
| B1 | A second screen off | displayForge → the middle screen → On: off → F9 → Enter. Not F10 | Javier | |
| B2 | Everything on one | every window is on your one screen; the bar is fine | Javier | |
| B3 | The workspace keys | Win + 1 … Win + 4 switch; note which "Daily" it shows (Claude's bench: another screen's copy) | Javier | |
| B4 | The words for one screen | workspaceForge → Daily's line says "switches all your screens": fine, or should it say something else with one? | Javier | |

## C · All three back

| # | What | How | Who | Result |
|---|---|---|---|---|
| C5 | Screens back on | displayForge → each screen → On → F9 → Enter (or simply log out and in again) | Javier | |
| C6 | Workspaces back where they live | each screen shows its own workspaces again; Win + 1 … 4 switch all three | Javier | |
| C7 | The rename undone | workspaceForge → "Play" back to Gaming → F10 | Javier | |

## D · A plain text console

| # | What | How | Who | Result |
|---|---|---|---|---|
| D1 | No Sway here: it says so | Ctrl + Alt + F3 → log in → `workspaceforge` → the start-up check → Close (c) | Javier | |
| D2 | Continue Anyway is readable | same → Continue Anyway (a) → the Workspaces page in the console's colours; change nothing → Q | Javier | |
| D3 | Back to the desktop | `exit`, then Ctrl + Alt + F1 (or F2) | Javier | |
