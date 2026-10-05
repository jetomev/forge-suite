# Research: a good-looking screen settings app (F-5)

*2026-09-30 · for hypeForge · Hyprland 0.56.2, Lua settings, started by uwsm · target: three identical 2560x1440 144 Hz screens on NVIDIA*

**Why this exists.** Javier tried nwg-displays and called it "a horrible piece of software". The earlier research ([2026-09-30-hyprland-own-apps.md](2026-09-30-hyprland-own-apps.md), section 6) found that wdisplays changes screens live but does not save anything. This page looks for something that looks good **and** saves the result so it survives a restart.

Nothing was installed and nothing was changed on this computer. Every fact below was read from package lists, GitHub, the Hyprland wiki or the apps' own source code on 2026-09-30.

## The short answer

**Monique** is the one to try. It is a proper window app (not a terminal app), it uses the same modern GNOME look (GTK4 + libadwaita, the kit most new Linux apps use), you drag the screens around on a canvas, and — the important part — it **saves into Hyprland's new Lua format** (`hl.monitor({ ... })` lines), the same format hypeForge uses. It can also be pointed at a folder of our choosing, so it can save straight into `machines/<hostname>/`. Everything it needs is already installed on this desktop; only Monique itself would come from the AUR.

There is **no official Hyprland screen settings app**, and the Hyprland wiki lists none.

## Summary table

| # | Option | Looks | Drag to arrange | Saves? | Writes Lua (`hl.monitor`)? | Package | Version · last activity | Stars | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Monique** | Clean dark GNOME-style window, side panel of settings | Yes | **Yes**, to a file Hyprland reads, plus named profiles | **Yes** (also old format, or both) | AUR `monique` (4 votes) | 0.8.3 · 2026-09-30 | 196 | **Try first** |
| 2 | **hyprmoncfg** | Tidy, handsome *terminal* app (text boxes, mouse works) | Yes (mouse in the terminal) | **Yes**, plus profiles and a switching helper | **Yes**, automatically | AUR `hyprmoncfg`, `-bin`, `-git` | 1.22.0 · 2026-09-30 | 444 | Best engineered, but it is a terminal app |
| 3 | **DankMaterialShell "Displays" page** | Polished Material-style settings page | Yes | **Yes**, into `~/.config/hypr/dms/outputs.lua` | **Yes** | `extra/dms-shell` | 1.6.2 · 2026-09-30 | 8,279 | Only comes with the whole DMS desktop shell; too big to borrow |
| 4 | **HyprMon** | Terminal app, simpler look | Yes | Yes, plus profiles | Yes, but **open bug #92: it replaces your whole `hyprland.lua`** | AUR `hyprmon-bin` | 0.0.17 · 2026-05-18 (code 2026-09-14) | 517 | Avoid for now |
| 5 | **Build our own** | Whatever we design | We build it | We decide: `machines/<hostname>/` | Yes | — | — | — | Only if Monique fails the test |
| — | nwg-displays | Plain older GTK3 window | Yes | Yes (Lua since 0.4.3) | Yes | `extra/nwg-displays` | 0.4.4 · 2026-09-30 | 1,111 | Already rejected by Javier |
| — | wdisplays | Plain GTK3 window | Yes | **No** | — | `extra/wdisplays` | 1.1.3 | 286 | Preview only |
| — | kanshi / shikane / way-displays | No window at all (text files) | No | Yes, their own files | No, they bypass Hyprland's settings | extra / extra / AUR | 1.9.0 / 1.1.1 / 2.0.0 | — | Not what we want |
| — | Noctalia, Caelestia | Full desktop shells | — | — | — | — | — | — | **No screen settings page** in either |

## Details

### 1. Monique — the recommendation

- **What it is:** "MONitor Integrated QUick Editor". A window app written in Python with GTK4 and libadwaita. Works on Hyprland, Sway and Niri.
- **Looks:** I viewed the author's screenshot. A dark window: the left two-thirds is a grid canvas with each screen drawn as a labelled rectangle (the selected one in blue); the right side is a neat settings column with sections "Monitor", "Resolution", "Position", "Scale & Transform", with drop-downs, +/- buttons and on/off switches. A profile picker and an **Apply** button sit at the top. It looks like a modern GNOME Settings page, not like nwg-displays. Screenshots:
  [layout editor](https://raw.githubusercontent.com/ToRvaLDz/monique/main/data/screenshots/1.png) · [workspace rules](https://raw.githubusercontent.com/ToRvaLDz/monique/main/data/screenshots/2.png) · [quick setup](https://raw.githubusercontent.com/ToRvaLDz/monique/main/data/screenshots/3.png) · [login-screen option](https://raw.githubusercontent.com/ToRvaLDz/monique/main/data/screenshots/4.png)
- **Features:** drag-and-drop canvas; resolution and refresh rate; scale; rotation ("transform"); turn a screen on/off; mirroring; VRR (variable refresh rate, the anti-tearing feature for games); 10-bit colour and HDR settings; which workspaces go on which screen; named profiles; a double-click shows a big label on each real screen so you know which is which; **a 10-second "keep these settings?" countdown that undoes the change if the screen goes black**; an optional background helper (`moniqued`) that switches profiles when screens are plugged in or out; a command-line mode (`monique --switch-profile Desk`) for key bindings.
- **"Primary" screen:** Hyprland itself has no "primary screen" setting, so no tool offers a true one. Monique uses "primary" only to decide where workspaces go when a screen disappears.
- **How it saves:** profiles in `~/.config/monique/profiles/*.json`, and the real settings file at `~/.config/hypr/monitors.lua` (Lua) and/or `monitors.conf` (old format) — you choose "legacy", "lua" or "both" in Preferences. I checked the source code (`models.py`, `to_hyprland_lua_block`): it writes genuine `hl.monitor({ output = ..., mode = ..., position = ..., scale = ... })` blocks. **It does not add the line that loads the file for you**; the README says to add `require("monitors")` yourself.
- **Fit with hypeForge:** Preferences → Config Output lets us pick another folder (`--config-dir`) and file name. Pointing it at `~/.config/hypeforge/machines/<hostname>/` with the name `monitors` gives `machines/<hostname>/monitors.lua`; our `machine.lua` would then load it with one `dofile(...)` line. That keeps screen details in the per-computer folder (D-28) and never touches our shipped `hyprland.lua`.
- **Package:** AUR `monique` 0.8.3-1, updated 2026-09-30, 4 votes, maintained by the author. Needs `python`, `python-gobject`, `python-cairo`, `gtk4`, `libadwaita` — **all already installed here** (checked with `pacman -Q`). Not in the official repos or chaotic-aur. Also on PyPI.
- **Health:** started 2026-02-19, very active (commits today), GPL-3.0, 109 automated tests in the code. Two open issues: #48 laptop lid mode not working (irrelevant for a desktop), #42 an internal tidy-up.
- **Known problems / unproven:**
  - Young project (7 months), one main author, few AUR votes.
  - hyprmoncfg's comparison table says Monique has no Lua support; **that table is out of date** — Monique's README and code both show Lua.
  - The look follows the GNOME/libadwaita theme, **not** `hyprtoolkit.conf`. It will match our GTK theme, not the Hyprland-made apps, unless we theme libadwaita too.
  - **Three identical screens:** if we tell it to name screens by description (make + model + serial) and the three screens report the same serial, the names would clash. Naming by port (`DP-1`, `DP-2`, `DP-3`) avoids that, but ports can swap after a driver change. Needs checking on the real machine (`hyprctl monitors -j`, look at the `serial` field).
  - Nothing is known about NVIDIA specifically; untested.

### 2. hyprmoncfg — the best-built, but in a terminal

- **What it is:** a Go program with a terminal interface (a "TUI": an app drawn with text inside a terminal window) plus a background helper `hyprmoncfgd`.
- **Looks:** I viewed the screenshot. Genuinely handsome for a terminal app: three tabs (Layout, Workspaces, Profiles), screens as boxed rectangles on a dotted grid with their workspace numbers, a settings column with clickable choices (scale 1x / 1.25x / 1.5x…), and a hint bar at the bottom. It takes the terminal's colours, so it would wear our theme. But it is still text in a terminal, not a window app. [Screenshot](https://raw.githubusercontent.com/crmne/hyprmoncfg/HEAD/docs/assets/images/screenshots/layout-dark.png) · [gallery](https://hyprmoncfg.dev/what-is-hyprmoncfg/#screenshots)
- **Features:** drag with the mouse; mode, scale, VRR, mirror, rotation, exact position; profiles that recognise screens by make/model/serial (with an extra check for identical screens); automatic switching on plug/unplug; workspace planner; **apply → check it worked → keep or undo**; a `hyprmoncfg doctor` command that checks Hyprland actually loads the file it writes.
- **How it saves:** writes `~/.config/hypr/hyprmoncfg-monitors.lua` automatically when `hyprland.lua` is in use, and **appends one line to the end of your main Hyprland file** to load it. For hypeForge that means it edits our shipped `hyprland.lua` — a friction point, since that file lives in the portable folder.
- **Package:** AUR `hyprmoncfg` 1.22.0 (maintained by the author), plus `hyprmoncfg-bin` and `-git`. Needs `hyprland` and `xdg-terminal-exec`. MIT licence.
- **Health:** 444 stars, very active (release 2026-09-29), 3 open issues, all about laptop lids and wake-up recovery.
- **Why not first:** Javier asked for something that *looks much better* than nwg-displays. A terminal app is a different kind of thing; worth showing him as the second option.

### 3. DankMaterialShell's Displays page

- **What it is:** DMS is a complete desktop shell (bar, notifications, launcher, settings) built on Quickshell. Its Settings has a **Display Config** tab with a drag canvas, per-screen cards, an "identify" overlay, profiles and HDR options (source: `Modules/Settings/DisplayConfig/`).
- **Saves:** `~/.config/hypr/dms/outputs.lua`, loaded with `require("dms.outputs")`, which DMS adds to `hyprland.lua` itself. Its test files show real `hl.monitor({...})` lines, including a 2560x1440@144 example. Lua support shipped in 1.6.0 (2026-09-03). If a machine still uses `hyprland.conf`, the page goes read-only and asks you to run `dms setup`.
- **Package:** official `extra/dms-shell` and `extra/dms-shell-hyprland` 1.6.2 (installable with nog).
- **Why not:** the Displays page cannot be run on its own; you get the whole DMS shell, which would replace hypeForge's bar and helpers. Good as **a design reference** for our own app if we ever build one.

### 4. HyprMon

- Terminal app in Go, 517 stars, AUR `hyprmon-bin` 0.0.17 (last release 2026-05-18). Drag, scale, rotation, mirroring, HDR, profiles, backups.
- **Open bug #92 (2026-09-11): "Lua config writer replaces entire hyprland.lua instead of only adding the managed include."** For a Lua-only setup like ours that is a data-loss risk. Avoid until fixed.
- Note: a different AUR package called `hyprmon` (1.1.1, 3 stars, Rust) is an unrelated project with the same name.

### Shells without screen settings

- **Noctalia** (now `noctalia-dev/noctalia`, rewritten in C++, ~11k stars): only per-screen *bar* options; no screen layout page. Not in the AUR under `noctalia-shell` any more.
- **Caelestia** (`caelestia-dots/shell`, ~12.6k stars; AUR `caelestia-shell` 2.5.0): its settings app has pages for apps, audio, Bluetooth, network, panels and wallpaper — **no displays page**.

### Official Hyprland (hyprwm)

I listed all 40 hyprwm repositories: there is no screen settings app, nor any sign of one. `hyprland-guiutils` holds small helper windows only. The wiki's "Useful utilities" pages mention no screen tool at all. The wiki's monitor page documents only hand-written `hl.monitor()` lines.

### Profile daemons (kanshi, shikane, way-displays)

All three keep screen layouts in their own text files and apply them at runtime through a Wayland standard for screen control. None has a window, none writes Hyprland's settings, and a Hyprland settings reload can fight with them. Not useful for F-5.

## 5. Option: build our own

**The smallest good design** (one window, one job):

1. Read the screens: `hyprctl monitors all -j` (name, description, serial, available modes, current position, scale, rotation).
2. Draw them on a canvas as rectangles; drag to move, snap edges together, show the numbers.
3. A side panel per screen: resolution + refresh (from the list Hyprland reports), scale, rotation, on/off, mirror of.
4. **Try it:** apply live through `hyprctl` (the exact live-apply command in Lua mode is **not yet checked**; Noctalia's source shows Lua-mode Hyprland taking `hl.dsp...` calls over `hyprctl dispatch`, so a similar route likely exists), then a 10-second "Keep these settings?" countdown that reverts if not confirmed.
5. **Save:** write `machines/<hostname>/monitors.lua` with plain `hl.monitor({...})` lines (a file we own, loaded by `machine.lua`); never edit `hyprland.lua`.

**Toolkit choices:**

| Toolkit | Looks match | Drag canvas | Effort | Notes |
|---|---|---|---|---|
| **hyprtoolkit** (C++) | Best: themed by `~/.config/hypr/hyprtoolkit.conf` like hyprlauncher, hyprpwcenter | Must be hand-built: it has rectangles, absolute positioning and mouse-enter/leave hooks, but no ready canvas or drag helper | **3–5 weeks** | Young (0.6.0), open crash-at-logout bug; C++ build and packaging |
| **GTK4 + libadwaita via Python** | Matches Monique/GNOME apps and our GTK theme | Easy (`Gtk.DrawingArea` + drag gesture) | **1–2 weeks** | Same stack as Monique, so at that point we are rebuilding Monique |
| Qt/QML (Quickshell-style) | Matches DMS-style shells | Easy in QML | 2–3 weeks | We run no Qt shell, so it adds a stack |

**Honest view:** building our own only pays off if we want the screens app to match the Hyprland-made apps exactly (hyprtoolkit). Otherwise Monique already does what a GTK version of ours would do.

## Suggested next step

1. Install Monique from the AUR (via nog/paru — raw AUR because it is not in the official repos; this is a finding for the "nog first" rule).
2. In Preferences set format **lua**, config folder `~/.config/hypeforge/machines/<hostname>/`, file name `monitors`.
3. Add one line to `machine.lua` that loads `monitors.lua`.
4. Test on the real three-screen NVIDIA desk: drag, change refresh to 144, save, **log out and back in**, check the layout stayed. Also check whether the three screens report different serials.
5. If Javier still dislikes the look, show hyprmoncfg next; if both fail, open the "build our own" question.

## Commands run (all read-only)

- `pacman -Si` for nwg-displays, wdisplays, kanshi, shikane, hyprland, hyprtoolkit, hyprland-guiutils, hyprsysteminfo, quickshell, noctalia-shell, dms-shell, way-displays, monique, hyprmoncfg, hyprmoncfg-bin, hyprmon-bin; `pacman -Ss dms-shell`; `pacman -Q python-gobject gtk4 libadwaita python-cairo`.
- AUR lookups with `curl -s 'https://aur.archlinux.org/rpc/v5/info?arg[]=<name>'` for: nwg-displays-git, hyprmon, hyprmon-bin, monique, hyprdisplays, hyprdisplay, hypr-displays, noctalia-shell(-git), dms-shell-git, caelestia-shell(-git), way-displays, wlr-randr, kanshi-gui, hyprmonitors, hyprland-monitor-settings, hyprmoncfg(-bin,-git), hyprdynamicmonitors(-bin), nwg-look.
- GitHub API (`api.github.com/repos/...`) for stars, last push, open issues and releases of monique, hyprmoncfg, both hyprmon projects, nwg-displays, wdisplays, noctalia, DankMaterialShell, caelestia shell, hyprland-guiutils; the list of all hyprwm repos.
- `git clone --depth 1` into a scratch folder (not the project) of hyprland-wiki, DankMaterialShell, noctalia, caelestia shell and monique, then `grep` for monitor-settings code and `hl.monitor` writers.
- Downloaded and viewed the Monique and hyprmoncfg screenshots.
- Read hypeForge's own `desktop/hypr/hyprland.lua` and `docs/DECISIONS.md` (D-28) to see how `machines/<hostname>/machine.lua` is loaded.

## Sources

- Monique: <https://github.com/ToRvaLDz/monique> · AUR <https://aur.archlinux.org/packages/monique> · <https://www.linuxlinks.com/monique-monitor-integrated-quick-editor/>
- hyprmoncfg: <https://github.com/crmne/hyprmoncfg> · <https://hyprmoncfg.dev> · AUR <https://aur.archlinux.org/packages/hyprmoncfg> · <https://www.linuxlinks.com/hyprmoncfg-monitor-configurator-and-background-daemon-hyprland/>
- HyprMon: <https://github.com/erans/hyprmon> · bug <https://github.com/erans/hyprmon/issues/92>
- DankMaterialShell: <https://github.com/AvengeMedia/DankMaterialShell> (releases 1.6.0–1.6.2)
- Noctalia: <https://github.com/noctalia-dev/noctalia> · Caelestia: <https://github.com/caelestia-dots/shell>
- nwg-displays: <https://github.com/nwg-piotr/nwg-displays> (releases 0.4.3, 0.4.4) · wdisplays: <https://github.com/artizirk/wdisplays>
- hyprtoolkit: <https://github.com/hyprwm/hyprtoolkit> · Hyprland wiki source: <https://github.com/hyprwm/hyprland-wiki> (useful-utilities, configuring/core/monitors)
- Search overview: <https://linux-meta.duckdns.org/en/p/monique>, <https://linux-meta.duckdns.org/en/p/hyprmon>
