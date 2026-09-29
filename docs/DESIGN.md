# hypeForge — design notes

*How hypeForge is meant to work. Anything marked **to decide** is still open, and is settled in the phase named next to it. Decisions are recorded in [DECISIONS.md](DECISIONS.md).*

---

## One portable folder

**The rule ([D-8](DECISIONS.md#d-8--one-portable-folder-system-changes-only-through-the-app)):** every setting lives in one folder. Copying the folder backs everything up. Dropping it onto a new computer and running hypeForge rebuilds the same desktop. Nothing outside the home folder is edited by hand.

**A first sketch (to decide in Phase 1):**

```
~/.config/hypeforge/            ← the one folder you back up
├── hypeforge.toml               which app does which job, your choices
├── hypr/                        Hyprland's own settings (hyprland.lua + parts)
├── apps/<app>/                  each chosen app's settings
├── theme/                       one Catppuccin Mocha palette that every app reads
└── system/                      the few files that must go outside your home folder,
                                 applied only by hypeForge (login screen, update locks)
```

- Apps expect their settings in their own places (for example `~/.config/waybar/`). hypeForge points those places **at the folder** (a *link*: a signpost that says "the real file is over there"), so the folder stays the only real copy.
- **To decide:** whether hypeForge also ships read-only *defaults* that your folder overrides. Omarchy 4 moved its internals into system packages "for safely separating user modifications". This keeps updates from overwriting your changes, but it means the portable folder holds only what you changed.

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

**Why it needs proving first:** Hyprland is built to tile. Out of the box, a new window takes a slot in a grid. Floating everything by default and snapping on demand means working against that default. It is the first thing proven in Phase 1, before anything else is built on top of it. The feasibility research is tracked in the issues.

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
