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
| 1.1 | Choose "Sway (hypeForge)", log in | a plain grey desktop with a bar at the bottom of each screen (date and time on the right) | |
| 1.2 | Look at the three screens | left / middle / right in the right order; the mouse moves smoothly across all three | |
| 1.3 | Win + Enter twice | two terminals side by side, filling the screen (tiling) | |
| 1.4 | In a terminal: `claude --continue` | this conversation back; Claude checks the screens are at 144 Hz (`swaymsg -t get_outputs`) | |
| 1.5 | Type `'` then `a` | á (US-International as before) | |

## 2 · Claude + Javier, from inside Sway (next)
Chrome with a video · Discord screen share · WoW full screen · brightness (ddcutil) · anything that flickers or stutters → a finding.
