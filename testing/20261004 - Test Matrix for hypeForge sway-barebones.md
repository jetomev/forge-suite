# hypeForge — the barebones Sway session (D-45) — Test Matrix

*2026-10-04. Sway 1.12 from Arch `extra` (nog); config `sway/config` (Sway's own example + 6 marked changes), copied to `~/.config/sway/config`; login choice **"Sway (hypeForge)"** (`sway --unsupported-gpu`). The current session stays the main desktop; Plasma the fallback.*

**Getting in and out:** log out → at the login screen choose the session **"Sway (hypeForge)"** (not plain "Sway": it refuses NVIDIA without the flag) → your password. To leave: **Win + Shift + E**, then click "Yes, exit sway".
**This conversation:** logging out closes it. In Sway: **Win + Enter** (a terminal), then `claude --continue`.

## Sway's own keys (Win = $mod)
| Keys | Does |
|---|---|
| Win + Enter | terminal (Alacritty) |
| Win + Shift + Q | close the window |
| Win + ← ↓ ↑ → (or H J K L) | move focus |
| Win + Shift + ← ↓ ↑ → | move the window |
| Win + 1 … 0 / Win + Shift + 1 … 0 | go to workspace / send the window there |
| Win + B / Win + V | the next window splits sideways / downwards |
| Win + S / W / E | stacked / tabbed / back to split |
| Win + F | fullscreen |
| Win + Shift + Space / Win + Space | float the window / focus floating ↔ tiled |
| Win + R | resize mode (arrows, then Enter) |
| Win + Shift + C | reload the settings |
| Win + Shift + E | exit Sway |

## 1 · Javier: the first look
| ID | Do | Expect | Result |
|---|---|---|---|
| 1.1 | Choose "Sway (hypeForge)", log in | a black desktop with a grey bar at the top (date and time on the right) — *expectation corrected 10-04: the sheet first said grey + bottom; Sway's example config has `position top` and no wallpaper = black* | ✅ PASS (Javier): black background, top grey bar with date and clock |
| 1.2 | Look at the three screens | left / middle / right in the right order; the mouse moves smoothly across all three | ✅ PASS (Javier): right order — workspace 2 left, 1 middle (main), 3 right; mouse smooth |
| 1.3 | Win + Enter twice | two terminals side by side, filling the screen (tiling) | ✅ PASS (Javier): 3 side by side (Claude's terminal + 2). Note: how new windows split → later (Phase 11/12) |
| 1.4 | In a terminal: `claude --continue` | this conversation back; Claude checks the screens are at 144 Hz (`swaymsg -t get_outputs`) | ✅ PASS (Claude, 10-04): conversation back; DP-2 left (0,0), DP-3 middle (2560,0), DP-1 right (5120,0), all 2560x1440 @ 144.000 Hz; keyboard layout reads US-International with dead keys; live config = repo `sway/config` (no difference) |
| 1.5 | Type `'` then `a` | á (US-International as before) | ✅ PASS (Javier): keys work as expected |

## 2 · Claude + Javier, from inside Sway (next)
Chrome with a video · Discord screen share · WoW full screen · brightness (ddcutil) · anything that flickers or stutters → a finding.
