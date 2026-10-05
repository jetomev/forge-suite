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

## 2 · Claude + Javier, from inside Sway
| ID | Do | Expect | Result |
|---|---|---|---|
| 2.1 | Chrome (opened by Claude with `swaymsg exec`), a YouTube video, Win + F in and out | smooth, no tearing or flicker | ✅ PASS (Javier): "perfect!" (Learn Linux TV). Claude: Chrome runs natively on Wayland (`xdg_shell`). **F-41:** video decoder at 0 % — Chrome decodes on the processor, not the graphics card (no `nvidia-vaapi-driver`); smooth anyway, machine-wide, not Sway's doing |
| 2.2 | Discord screen share | the other side sees the screen | ✅ PASS (Javier): "everything worked perfectly well". Before it, Claude installed `xdg-desktop-portal-wlr` 0.8.4 (Sway's screen-sharing helper; nog, `extra`) and restarted the portal; Sway's `sway-portals.conf` routes ScreenCast to it; Discord 1:1.0.159 runs natively on Wayland. **F-42:** the Sway session sets no `SUDO_ASKPASS`, so nothing gets the password window by itself; Claude passed `SUDO_ASKPASS=/usr/bin/ksshaskpass NOG_ASKPASS=1` by hand |
| 2.3 | WoW full screen (launcher as is → XWayland on Sway) | plays; clicks land where aimed | ❌ FAIL (Javier): opened well, full screen 2560x1440 on DP-3 by itself; but turning the camera the pointer leaves the screen and the game loses focus; windowed mode snapped to half the screen (tiled) and the menu stopped taking clicks; closed with Alt + F4. **F-43:** same as Hyprland via XWayland (F-40) — the game's pointer lock is not honoured; the launcher only picks Wine's Wayland driver on Hyprland |
| 2.3b | WoW with Wine's Wayland driver (`env -u DISPLAY` play-wotlk.sh, launcher unchanged) | camera turns only with the mouse; clicks land | ✅ PASS (Javier): "everything worked well… runs and looks amazing!" Native Wayland window (`xdg_shell`), full screen 2560x1440 on DP-3 with no rule needed. In full screen the pointer stays inside the game (fine for him). First try covered Claude's terminal → Claude moved it to workspace 3 (DP-1) and opened the game on workspace 1. F-43's fix = the launcher should pick the Wayland driver on Sway too |
| 2.4 | Brightness with ddcutil (Claude: each bus to 10 for 5 s, back to 75, in order 3 → 4 → 5) | each screen changes on its own | ✅ PASS (Javier): one screen at a time, order "3, 1, 2" in his numbering (2 left, 1 middle, 3 right) → **bus 3 = right (DP-1), bus 4 = middle (DP-3), bus 5 = left (DP-2)**. First try (30 %) was too subtle to see; 10 % was clear. All three verified back at 75 |

## Outcome
**Sections 1 and 2 pass (10-04).** Sway on this computer: three screens at 144 Hz in order, keys, tiling, Chrome video, Discord screen share, WoW (with Wine's Wayland driver), per-screen brightness. Findings: F-41 #23 (video decoded on the processor), F-42 #24 (no password window set for the session), F-43 #25 (WoW via XWayland; the launcher must pick Wayland on Sway too). Tiling order is a later job.
