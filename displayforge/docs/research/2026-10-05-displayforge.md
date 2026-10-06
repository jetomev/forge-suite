# displayForge — research (2026-10-05)

*Javier: "Monitor Settings please" → "Build the Monitors Forge app" → name **displayForge**. Commands run on the KognogOS test desktop (Sway 1.12, NVIDIA RTX 3060, three Sceptre Y27).*

## Why a Forge app
No terminal (TUI) app arranges screens on Sway. There are command-line tools (`swaymsg output`, `wlr-randr` 28 KB) and graphical ones (nwg-displays 542 KB GTK, wdisplays 108 KB GTK). By the D-57 rule (terminal first) this is a gap → a Forge app (D-59: "monitor(s) manager = Forge app").

## What Sway can set per screen (`man sway-output`)
`mode` (width × height @ rate, `--custom`), `position` X Y, `scale` (+ `scale_filter`), `transform` (rotation 90 / 180 / 270, flipped), `enable` / `disable` / `toggle`, `power` on / off, `adaptive_sync`, `render_bit_depth` 6 / 8 / 10, `max_render_time`, `subpixel`, `color_profile`, `allow_tearing`, `hdr`, `background`. All apply live with `swaymsg output <name> …`; `swaymsg -t get_outputs` reports each screen's make, model, serial, current mode, the modes it offers (32 each here), position, scale, transform, focus.

Today the layout is written by hand in `sway/config`: DP-2 left (0,0), DP-3 middle (2560,0), DP-1 right (5120,0), each 2560×1440 @ 144 Hz, scale 1.

## Brightness (DDC/CI)
`ddcutil` 3.0.2 is installed. `ddcutil --bus N getvcp 10` works **without a password** (the i2c devices carry an access-control entry for the logged-in user). Each read takes ~250 ms. All three report 75 of 100.

**Which screen is which cannot be read:** `ddcutil detect` → "Displays with I2C bus numbers 3, 4, 5 have identical EDIDs. DRM connector names may not be accurate." All three report model *Sceptre Y27*, serial *MXY275BIG0001*; NVIDIA exposes no connector link. The HomeLab notes' mapping (bus 3 = right, 4 = middle, 5 = left) was found by eye. → displayForge needs an **Identify** step (show a big number on each screen; dim one bus at a time and ask which went dark) and remembers the answer.

## How others do it (with thanks, no comparison)
- GNOME / KDE / Windows: a drawing of the screens to drag; on a resolution change, **"Keep these settings?" with a countdown that reverts by itself** — a must: a wrong mode can leave a screen black.
- kanshi: named profiles that switch when screens are plugged in or out (laptops, docks) — a later phase.

## Fits with hypeForge
- Workspaces (applet 1) lists screens by connector name in `workspaces.toml`; the bar and placement read it. displayForge writes the screens; when the order changes it must offer to update the workspaces' screen order (the settings file is the contract, D-59).
- "Any number of screens" (Javier): displayForge is where 1 … 6+ screens get arranged; it must work with one screen.
- Saving: a file Sway includes (`~/.config/sway/outputs`), written by displayForge, a backup before every save — the Forge apps' pattern.
