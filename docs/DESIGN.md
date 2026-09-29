# hypeForge — design notes

*How hypeForge is meant to work. Anything marked **to decide** is still open, and is settled in the phase named next to it. Decisions are recorded in [DECISIONS.md](DECISIONS.md).*

---

## The key map

*Approved by Javier on 2026-09-29 ([D-29](DECISIONS.md#d-29--the-key-map-plasmas-keys-keep-their-jobs)).*

*Read from Plasma's shortcuts on the test desktop on 2026-09-29 (`~/.config/kglobalshortcutsrc`, plus Spectacle's defaults in its app file). **Win** is the key Plasma calls "Meta". The rule: **a key you use in Plasma today does the same thing in hypeForge.** Plasma keys with nothing behind them in hypeForge are listed at the end. Found on the way: this desktop has **one keyboard layout and one virtual desktop** across all three screens, so the layout and desktop-switching keys are little used.*

**Status** says how much work each key is: **ready** (Hyprland or the chosen app does it directly), **build** (hypeForge has to make it, see #5), or **test** (should work, not yet tried with Lua or uwsm).

### Windows
| Keys | What happens | Plasma today | How | Status |
|---|---|---|---|---|
| Win + ← / → | Snap to the left or right half | same | Lua snapping (#5) | build |
| Win + ↑ / ↓ | Snap to the top or bottom half | same | Lua snapping (#5) | build |
| Win + PgUp | Maximise | same | Hyprland's fullscreen-keep-bar mode | ready |
| Win + Backspace | Restore the window's previous size and place | same | remembered by the snapping code (#5) | build |
| Alt + F4 | Close the window | same | Hyprland | ready |
| Win + Ctrl + Esc | Force-quit a stuck window | same | `hyprctl kill` (click the window) | ready |
| Alt + Tab / Alt + Shift + Tab | Switch windows, forwards and back | same (also Win + Tab) | a switcher: Walker's window list or a small tool (#5) | build |
| Win + Alt + arrows | Move focus to the window in that direction | same | Hyprland | ready |
| Win + Shift + ← / → | Move the window to the previous / next screen | same | Hyprland | ready |
| Win + T | Switch this window between floating and tiled | *Tiles editor* | Hyprland | ready |

### Apps and menus
| Keys | What happens | Plasma today | How | Status |
|---|---|---|---|---|
| Win (tap alone) | App launcher | same | Walker, bound to the key's release | test |
| Win + Return | Terminal | same | Alacritty | ready |
| Win + V | Clipboard history | same | Walker's clipboard | ready |
| Win + K | File manager window | *Krusader to front* | Krusader | ready |
| Win + E | Terminal file manager | *(new)* | superfile in Alacritty | ready |
| Win + L | Lock the screen | same | hyprlock | ready |
| Ctrl + Alt + Del | Power menu | *Logout screen* | the Walker power list (D-26) | ready |
| Ctrl + Esc | System monitor | *(Plasma's default)* | btop in Alacritty | ready |
| Win + Shift + C | Colour picker | *(new)* | hyprpicker | ready |

### Screenshots and recording (Spectacle's keys, kept)
| Keys | What happens | How | Status |
|---|---|---|---|
| Print / Win + Shift + S | Drag a box, then draw on it | grim + slurp + Satty | ready |
| Shift + Print | Whole desktop, all three screens | grim | ready |
| Win + Print | The active window | grim + Hyprland's window position | ready |
| Win + Shift + Print | Drag a box, saved straight away | grim + slurp | ready |
| Win + Shift + R | Start/stop recording a dragged area | gpu-screen-recorder | test |
| Win + Alt + R | Start/stop recording a screen | gpu-screen-recorder | test |
| Win + Ctrl + R | Start/stop recording a window | gpu-screen-recorder | test |

### Sound, media, brightness, zoom
| Keys | What happens | How | Status |
|---|---|---|---|
| Volume keys (Shift for 1 % steps) | Volume up, down, mute | SwayOSD + `wpctl` | ready |
| Mic mute key / Win + Mute | Mute the microphone | SwayOSD + `wpctl` | ready |
| Media keys | Play, pause, next, previous | mpv-mpris + `playerctl` (to add) | test |
| Brightness keys | All three monitors brighter or dimmer | `ddcutil` on I2C buses 3, 4 and 5 (D-20) | test |
| Win + = / Win + - / Win + 0 | Zoom in, out, back to normal | Hyprland's cursor zoom | ready |

### Plasma keys with nothing behind them in hypeForge
- **Overview, grid and "present windows"** (Win + W, Win + G, Ctrl + F7/F9/F10): Hyprland has no overview of its own. An official plugin (hyprexpo) exists; a later choice.
- **Peek at desktop / show desktop** (Win + D, Ctrl + F12): not planned.
- **Minimise** (Win + PgDn): **no minimise in hypeForge** (D-34).
- **Desktop switching** (Win + F1–F4, Win + Ctrl + arrows and their Shift versions): there is one desktop today. Each monitor gets its own fixed workspace instead.
- **Win + 1…9** (open taskbar entry 1–9): there is no taskbar (D-34).
- **Activities** (Win + Q, Win + A), **power profile** (Win + B), **keyboard layout** (Win + Alt + K / L), **screen reader** (Win + Alt + S), **window menu** (Alt + F3), **panel focus** (Win + Alt + P), **clipboard actions** (Win + Ctrl + X): Plasma-only features, or not used here.

## One portable folder

**The rule ([D-8](DECISIONS.md#d-8--one-portable-folder-system-changes-only-through-the-app)):** every setting lives in one folder. Copying the folder backs everything up. Dropping it onto a new computer and running hypeForge rebuilds the same desktop. Nothing outside the home folder is edited by hand.

**The layout (approved by Javier 2026-09-29, [D-28](DECISIONS.md#d-28--the-portable-folder-holds-a-full-copy)):**

```
~/.config/hypeforge/                 ← the one folder you back up
├── hypeforge.toml                    your picks (the recipe) and a few switches
├── hypr/                             hyprland.lua and its parts, plus hyprlock, hypridle,
│                                     hyprpaper, hyprsunset settings
├── apps/<app>/                       each chosen app's settings (waybar/, walker/, mako/ …)
├── uwsm/                             env and env-hyprland: theme, cursor, NVIDIA variables (D-25)
├── services/                         the systemd user services uwsm starts (D-25)
├── autostart/                        "Hidden" copies that switch off unwanted autostart
│                                     entries, e.g. nm-applet and print-applet (D-25)
├── theme/                            one Catppuccin Mocha palette every app reads
├── machines/<hostname>/              what belongs to ONE computer: monitor names, positions
│                                     and 144 Hz, ddcutil buses (D-20, D-24)
└── system/                           the few files that go outside your home folder,
                                      applied only by hypeForge (login screen, nog pins)
```

**How it works:**
1. **Apps find their settings through links.** A link is a signpost that says "the real file is over there". `~/.config/waybar` points into `apps/waybar/`, `~/.config/uwsm` into `uwsm/`, and so on. hypeForge makes the links and checks them; the folder stays the only real copy.
2. **One computer's details live apart.** Everything in `machines/<hostname>/` describes one computer. On a new computer hypeForge starts a fresh `machines/` entry for it, so three monitors here never confuse a laptop there. This is the lesson from the KognogOS settings export: *ship the look, never the machine-specific bits.*
3. **Backups and undo live outside the folder**, in `~/.local/state/hypeforge/`. They belong to one computer and would only clutter a copy.
4. **System files** sit in `system/` under their real path (for example `system/etc/greetd/config.toml`), and are applied as described under *System pieces* below.

**Full copy, or defaults plus your changes? Decided: A, full copy (D-28).**
- **A · Full copy. ✅ Chosen.** The folder holds every setting in full. Copying it alone rebuilds the desktop, even with a different hypeForge version. When a new hypeForge version improves a default, the app **shows the change and asks** before touching your folder.
- **B · Defaults plus your changes.** hypeForge installs read-only defaults as a system package, and your folder holds only what you changed. Updates flow in by themselves, but the folder alone is not the whole desktop.

## Floating-first windows

**The rule ([D-7](DECISIONS.md#d-7--floating-windows-by-default-win--arrow-keys-tile-like-plasma)):** every window opens floating, and Win + arrow keys snap it into place, the same way Plasma does.

**Plasma's shortcuts on the test desktop today** (read from `~/.config/kglobalshortcutsrc`, 2026-09-28):

| Plasma action | Keys |
|---|---|
| Quick Tile Left / Right | Meta + Left / Meta + Right |
| Quick Tile Top / Bottom | Meta + Up / Meta + Down |
| Maximize / Minimize | Meta + PgUp / Meta + PgDown |
| Walk Through Windows | Alt + Tab, Meta + Tab |
| Window to Next Screen | Meta + Shift + Right |
| Close | Alt + F4 |
| Overview | Meta + W |
| Switch to Desktop 1–4 | Ctrl + F1…F4, Meta + F1…F4 |

*Meta is the Windows key. The quarter-screen tiles (top-left and so on) have no shortcut assigned on this desktop.*

**Why it needs proving first:** Hyprland is built to tile. Out of the box, a new window takes a slot in a grid. Floating everything by default and snapping on demand means working against that default. It is the first thing proven in Phase 1, before anything else is built on top of it.

**Feasibility (research, 2026-09-28): doable with work** ([full report](research/2026-09-28-floating-first-and-omarchy-vm.md), [#5](https://github.com/jetomev/hypeforge/issues/5)):
- **Float everything:** one documented rule, using the same "match every window" pattern as Hyprland's own example settings.
- **Win + arrow snapping:** about 150–250 lines of Lua, built from pieces documented for 0.56: key bindings that call our own functions, the active window's size and position, each monitor's size, and the space the bar reserves.
- **Plasma's rules, read from KDE's source:**
  - Win + Left/Right snaps to a half, and Win + Up/Down to the top or bottom half.
  - A second arrow turns a half into a quarter.
  - Pressing toward the side a window is already on moves it to the next monitor.
  - Win + PgUp maximises and restores.
- **Drag a window to a screen edge:** only as "drop it and it jumps into place". A Plasma-style outline *while* dragging would need a compiled plugin that breaks on every Hyprland update, so **it is left out** (proposed; Javier's call).
- **Not in Hyprland at all:** an Alt + Tab switcher with previews; it has to be built or chosen. (Minimising is also missing, and hypeForge leaves it out, D-34.)
- **Traps the source reading found:**
  - "set floating" silently *toggles* unless given `"on"`.
  - Move and resize take whole-screen coordinates, and resizing grows from the centre, so resize first, then move.
  - Monitor sizes are raw pixels while positions are scaled.
  - A settings reload wipes Lua's memory, so the "restore" sizes need a file.
  - Hyprland 0.56.2 has an unreleased-fix bug where a quickly resized window can draw into only part of its frame.
- **Nothing here has been run yet.** It gets proven on the Omarchy VM and the test desktop.

## Updates locked by us

**The rule ([D-9](DECISIONS.md#d-9--updates-are-locked-by-us-through-nog)):** Hyprland's family of packages updates together, through nog, when we decide.

**What the package database says (2026-09-28):** `hyprland 0.56.2` depends on exact versions of six helper libraries: `libaquamarine.so=14`, `libhyprcursor.so=0`, `libhyprgraphics.so=4`, `libhyprlang.so=2`, `libhyprutils.so=13`, `libhyprwire.so=3`. If one of them moves to a new version before Hyprland does, the desktop will not start.

**What nog does today:** all seven are Tier 3 (7-day wait), and nog does not know they belong together. nog already has what we need:
- **groups** in `/etc/nog/tier-pins.toml` (*"packages that must move together — members inherit the highest tier among any other group member"*)
- **pins** (`nog pin <package> <tier>`), plus an expert mode where a tier waits for a manual go-ahead

**The plan (Phase 3):** hypeForge writes a `hyprland-family` group plus a tier pin, from a file in its `system/` folder. It never edits the file by hand.
- **Found along the way:** the test desktop is not using KognogOS's own tier list. nog there reads the stock list it was installed with, and KognogOS's longer list has never been applied. hypeForge's lock has to work on either list.

## System pieces, and how they are applied

Some things cannot live in the home folder: the login screen's settings, nog's tier pins, perhaps a device rule. They are handled like this:

1. The file lives in `system/` in your folder.
2. hypeForge shows you exactly what will change.
3. It keeps a backup of whatever it replaces.
4. It applies the change with a single password prompt. It uses the same privilege pattern as grubForge (polkit, a fixed-purpose helper), never a password typed into the app.
5. **Undo** puts the backup back.

## What Plasma did quietly, and now needs an owner

Plasma handled all of these without anyone noticing. Without Plasma, each needs a chosen tool, and each one has a row in the [recipe](RECIPE.md):

- **the "enter your admin password" pop-up** (a *polkit agent*). grubForge depends on one being present.
- **the password wallet**, where browsers and apps keep saved passwords
- **automatic mounting of USB drives**
- **file-open dialogs and screen sharing**, provided by background services called *portals*
- **notifications, the lock screen, and screen-off/sleep timing**
- **printer management**

## Running in Alacritty, readable on a plain text screen

hypeForge is a [forgekit](https://github.com/jetomev/forgekit) app, like every Forge app, and runs in Alacritty ([D-10](DECISIONS.md#d-10--forge-apps-run-in-alacritty-and-must-be-readable-on-a-plain-text-screen)). It must also be readable on a plain text screen, which is where a fresh Arch install begins. That depends on [forgekit#1](https://github.com/jetomev/forgekit/issues/1) being fixed first.

## The test desktop's hardware

- **Graphics card:** NVIDIA GeForce RTX 3060, driver 615, with NVIDIA's open-source kernel modules. This is one of the two setups the [Hyprland wiki](https://wiki.hypr.land/Nvidia/) recommends. The `nvidia_drm` settings `modeset` and `fbdev` are both on.
- **Screens:** three 2560×1440 monitors at 144 Hz, side by side (DP-2, DP-3, DP-1 from left to right).
- **Login screen:** SDDM with the KognogOS theme. Today it offers only one session, Plasma.
