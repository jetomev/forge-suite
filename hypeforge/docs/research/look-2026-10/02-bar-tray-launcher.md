# 02 · The bar, the tray, the launcher and a dock — six styles on Sway

*Research helper 2 of 5 for the look program (D-67, `docs/look-program.md`). Written 2026-10-10.
Research and notes only: nothing was installed, no file outside this folder was changed, Waybar
and Sway were not restarted.*

**Our machine, as checked today:** Sway 1.12, Waybar 0.15.0, fuzzel 1.15.0, mako 1.11.0, GTK3
3.24.52, gtk-layer-shell 0.10.1; three 2560×1440 screens (DP-2 left, DP-3 middle, DP-1 right),
scale 1.0. Repos enabled: core, extra, multilib **and chaotic-aur** (a third-party repo that ships
ready-built copies of AUR packages — it counts as "AUR" under our rules, not as official).

**How to read the marks:** ✅ *checked* = I read it in the installed manual page, in the program's
own source code at the exact version we run, or on the machine. 📄 = from the project's own
documentation or the vendor's support page (linked). ⚠️ *unverified* = my best understanding, not
proven; needs a test on the hidden bench before anyone relies on it.

---

## The short version (plain words)

1. **Waybar can wear all six styles.** It already does the hard parts: a bar at the top or bottom,
   several bars at once, a bar that floats in the middle at its own width, rounded "pill" shapes,
   shadows, see-through colours, a hidden drawer that slides open, and real drop-down menus.
   We do not need to replace it.
2. **The launcher, the tray drawer and the dock cost nothing or almost nothing.** A dock can be a
   second Waybar (0 packages) or **nwg-dock** (official repo, 5 MB, no new libraries).
3. **What no bar on Sway gives us for free:** Windows 11's pop-up panels (Quick Settings, the
   calendar flyout), the dock's magnifying wave from macOS, and an app's own File/Edit menus in
   the top bar (Mac OS 9, macOS). The first one we can build ourselves; the last two are not
   possible on Sway in a faithful way.
4. **A KDE-style launcher is reachable two ways:** nwg-menu (official repo, no new libraries,
   closest look today) or our own small launcher window built on what is already installed
   (Python + GTK3 + the layer-shell library are all present). Our fuzzel launcher keeps working
   either way.
5. **One "bar kit" can morph between the styles:** one Waybar, the same applets, and per style
   only a layout file (what goes where) plus a shape file (corners, sizes, shadows); the colours
   come from the theme file. A style switch rewrites two files and asks Waybar to reload.

---

## 1. What we have today (read from the files)

| Piece | Where | What it does |
|---|---|---|
| The bar | `~/.config/sway/waybar/config.jsonc`, `style.css`; started by `sway/config` line 312 (`exec waybar -c … -s …`) | One Waybar at the **top** of every screen, 32 px, straight edges, Catppuccin Mocha shades |
| Left | `custom/launcher` (the KognogOS emblem drawn as a CSS background), `group/workspaces` (applet 1 writes it into `workspaces.waybar.json`), `group/favourites` (applet 4 writes `favourites.waybar.json` + `favourites.css`) | Launcher button, the "1. Daily" workspace buttons + the number square, the Favorites ▾ drop-down |
| Centre | `wlr/taskbar` (all screens, icons only, candy-icons) | One icon per open window; click = go to it, middle click = close |
| Right | `group/indicators`: `tray`, `custom/clipboard` (applet 9), `custom/drives` (11), `custom/printers` (12), `bluetooth`, `network`, `wireplumber`, `clock`, `custom/notifications` (7), `custom/power` | Background apps, our applets, the date and time between two thin lines, the bell, the power menu |
| Launcher | `applets/sections/hypeforge-sections` + `sections.toml` | fuzzel in its menu mode: first screen = Favourites, the standard groups (D-64), All apps, Help & Keys; opens under the emblem (`--anchor top-left`) |
| fuzzel look | `~/.config/sway/fuzzel/fuzzel.ini` | Noto Sans 11, candy-icons, 40 wide × 12 lines, `radius=0` today |
| Pop-up tools | network = `networkmanager_dmenu` (fuzzel), Bluetooth = `bluetui`, mixer = `wiremix`, nmtui — each in a floating Alacritty | Our "flyouts" today are terminal apps in small floating windows (D-57 rule 1) |

**Everything our applets do stays.** Every style below only changes *where* a module sits and *how
it is drawn*. The scripts behind `custom/*` (clipboard, drives, printers, notifications, power,
workspaces, favourites) do not change; at most they gain a second output format (icon-only vs
text) chosen by a setting.

One known local trap, already written in our config: **Waybar 0.15's `image` module stops the bar
from appearing** on this machine, so pictures are drawn as CSS backgrounds. Every recipe below keeps
that workaround.

---

## 2. What the tools can really do

### 2.1 Waybar 0.15 — checked against the installed manual and the 0.15.0 source

| Ability | Answer | Proof |
|---|---|---|
| Top or bottom (or left/right) | Yes, `"position"` | ✅ `man 5 waybar` |
| Several bars at once, from one Waybar | Yes: the config file can be a **list** of bars; each can have its own `output`, `position`, modules and `name` (the name becomes a CSS class, so each bar can be styled apart) | ✅ `man 5 waybar` · *MULTI OUTPUT CONFIGURATION*, `name` |
| A bar on some screens only | Yes, `"output": "DP-3"` or a list; `!DP-1` excludes one | ✅ `man 5 waybar` · `output` |
| **A bar that floats in the middle at its own width** | Yes. Setting `"width"` to any number above 1 on a top/bottom bar **un-anchors it from the left and right edges**, and Waybar centres it itself. If the modules need more room than the number, the bar grows to fit them (GTK will not shrink a window below what its content needs), so `"width": 2` means "exactly as wide as the contents" | ✅ source `src/bar.cpp` lines 414–425 (anchors) and 630–690 (centring) at tag 0.15.0 |
| …and does it shrink again when windows close? | ⚠️ unverified — the source shows growing; shrinking back depends on GTK resizing the layer window. **Bench it** before building a dock on it | — |
| Gaps around the bar (the "floating island" look) | Yes, `"margin"` or `margin-top/left/right/bottom` | ✅ `man 5 waybar` |
| Windows drawn under the bar, or the bar on top of windows | `"exclusive": false`, `"layer": "top"/"bottom"`, `"mode": "overlay"` | ✅ `man 5 waybar` |
| Hide / show the bar | `"mode": "hide"` with `"ipc": true` (the Sway "show while the Win key is held" behaviour); `SIGUSR1` toggles; `start_hidden` | ✅ `man 5 waybar` · `mode`, `ipc`, SIGNALS |
| Hide when the mouse leaves, show at the screen edge | **No.** Waybar has no mouse-edge auto-hide | ✅ (not in `man 5 waybar`) |
| **A hidden drawer** (a group that shows only its first module and slides the rest open) | Yes: `group/…` with `"drawer": {…}`; opens on **hover**, or on **click** with `"click-to-reveal": true`; slide direction and speed settable; hidden children get a CSS class | ✅ `man 5 waybar` · *Group Drawers*; source `src/group.cpp` line 65 |
| **A real drop-down menu** from a module | Yes: `"menu": "on-click"`, `"menu-file"` (a GTK menu description in XML, submenus allowed), `"menu-actions"` (id → command). Works on every text-type module (`custom`, `clock`…) | ✅ `man 5 waybar-menu`; source `src/ALabel.cpp` lines 69–110 |
| …is that menu live (recent apps, open windows)? | **No.** The menu file is read **once, when the module is created**. New contents need a Waybar reload | ✅ source `src/ALabel.cpp` (read in the constructor) |
| Taskbar of open windows | `wlr/taskbar`: icons and/or title (`format`), per-screen or all screens, `sort-by-app-id`, `active-first`, `ignore-list`, click actions `activate`, `minimize`, `maximize`, `fullscreen`, `close` | ✅ `man 5 waybar-wlr-taskbar` |
| **Pinned apps in the taskbar** | **No.** `wlr/taskbar` only shows open windows. Pinned icons must be separate `custom/` modules (applet 4 already writes Favorites this way) | ✅ (no option in `man 5 waybar-wlr-taskbar`) |
| Focused app's name (Mac top bar) | `sway/window`: title or `{app_id}`, optional app icon (`"icon": true`), `rewrite` rules to turn ids into nice names, CSS classes for empty/solo/tabbed/floating | ✅ `man 5 waybar-sway-window` |
| Calendar | `clock` with `{calendar}` in its tooltip (month/year views, scroll to change month) — a **tooltip**, not a clickable panel | ✅ `man 5 waybar-clock` |
| Tray | `tray`: icon size, spacing, `show-passive-items`, `reverse-direction`, per-app icon override. **No option to hide chosen icons**; the man page still calls the tray "beta" | ✅ `man 5 waybar-tray` |
| Tray inside a drawer (Windows' hidden icons) | Should work: a group may hold any module. ⚠️ unverified on our bar — bench it | — |
| Live style edits | `"reload_style_on_change": true` reloads the CSS when the file (or an imported file) changes; `SIGUSR2` reloads everything | ✅ `man 5 waybar` |

### 2.2 What Waybar's CSS can draw (GTK3 rules)

Waybar and nwg-dock are GTK3 programs, so they follow GTK3's CSS, which is a *subset* of web CSS.
📄 [GTK3 CSS properties](https://docs.gtk.org/gtk3/css-properties.html):

- **Can:** rounded corners (`border-radius`), shadows (`box-shadow`, also inset), see-through colours
  (`rgba(…)`, `alpha(@colour, 0.8)`), `opacity`, straight gradients (`linear-gradient` — the Mac OS 9
  "platinum" sheen), `text-shadow`, animations between states (`transition`), margins and padding,
  minimum sizes, fonts, `:hover`.
- **Icons only:** `-gtk-icon-transform: scale(1.3)` can enlarge an *icon* (not a whole widget) and
  `-gtk-icon-shadow` can shadow it. This is the only "grow on hover" tool GTK3 offers.
- **Cannot:** the web's `transform` (no moving or scaling whole widgets), `backdrop-filter`/blur,
  radial gradients, percentages in sizes.
- **Blur behind a see-through bar is not Waybar's job — it is the compositor's.** Plain Sway does not
  blur. **SwayFX** does, for bars too: `layer_effects "waybar" blur enable; shadows enable;
  corner_radius 6` (📄 [SwayFX README](https://github.com/WillPower3309/swayfx)). SwayFX 0.6 is in
  **chaotic-aur only**, and its package **conflicts with `sway`** (✅ `pacman -Si swayfx`): it replaces
  Sway rather than sitting beside it. That question belongs to helper 01.

### 2.3 Hard limits of Sway itself (no bar can fix these)

- **No "minimize".** Sway has no minimized state; the stand-in is the **scratchpad** (Win + −).
  The taskbar's `minimize` action does nothing useful on Sway. ⚠️ from experience, not re-tested today.
- **No global app menu.** Mac OS 9 and macOS put the front app's own *File · Edit · View* menus in the
  top bar. On Wayland that needs the app and the compositor to share a menu protocol that only KDE
  uses; GTK4 apps and Chrome do not export their menus to Sway. ⚠️ unverified in detail, but no Sway
  bar offers it. We can show the **app's name** and **our own window menu** (float, full screen, tab,
  move to a workspace, close), not the app's own menus.
- **No overview of all windows** (COSMIC's "Workspaces" button, macOS' Mission Control). Sway has no
  such view; our workspace drop-down is the stand-in.

### 2.4 The candidates, and what each would cost us

*Checked 2026-10-10 with `pacman -Si`, `pacman -Q`, `nog search` (read-only) and the AUR's public
lookup. "New libraries" = dependencies not already installed on this desktop.*

| Tool | What it is | Where | Size | New libraries | Fits our rules? |
|---|---|---|---|---|---|
| **Waybar** (have) | The bar | extra | installed | — | ✅ |
| **fuzzel** (have) | Search box / menus | extra | installed | — | ✅ |
| **nwg-dock** | A dock for **Sway only**: pinned + running apps, workspace switcher, launcher button, auto-hide at the screen edge (`-d`), position bottom/top/left, alignment, margins, icon size, its own CSS | extra 0.4.3 | 5.4 MB | **none** (gtk3, gtk-layer-shell) | ✅ GTK3 only, no KDE/GNOME. No magnification. 📄 [README](https://github.com/nwg-piotr/nwg-dock) |
| **nwg-menu** | A classic start menu: categories that open sub-menus, search box, pinned apps on top, lock/log out/restart/shut down buttons, placement and margins on the command line, its own CSS | extra 0.1.9 | 5.1 MB | **none** | ✅ Uses its own 8 simplified categories, not our `sections.toml` groups. 📄 [README](https://github.com/nwg-piotr/nwg-menu) |
| **nwg-drawer** | A full-screen grid of apps (GNOME/COSMIC "App Library" look), category filter, search (also files), pinned row, power row | extra 0.7.5 | 41 MB | **none** (xdg-utils already here) | ✅ but big. 📄 [README](https://github.com/nwg-piotr/nwg-drawer) |
| nwg-panel | A whole panel with a Quick-Settings-like "Controls" pop-up (volume, brightness, custom items), clock with calendar pop-up, taskbar with a right-click window menu, tray, start menu | extra 0.12.1 | 4 MB | python-i3ipc, python-netifaces, brightnessctl | ⚠️ A second bar program next to Waybar; README warns that KDE's `kded6` can steal its tray. 📄 [README](https://github.com/nwg-piotr/nwg-panel) |
| ironbar | GTK4 bar with **real pop-ups** (clock calendar, grouped windows), a **launcher module that merges pinned and running apps** (the Windows 11 taskbar), a category **menu** module, tray | extra 0.19.1 | 26 MB | gtk4-layer-shell, lua51-lgi | ⚠️ Would replace Waybar and every module config. Docs read on the `master` branch; some options may be newer than 0.19.1. 📄 [docs](https://github.com/JakeStanger/ironbar/tree/master/docs) |
| rofi 2.0 | Launcher/menus, now with **official Wayland support** (the old rofi-wayland fork was merged) | extra 2.0.0 | 1.1 MB | xcb-imdkit | ⚠️ Click-outside-to-close does not work on Wayland. Does nothing fuzzel cannot for us. 📄 [rofi 2.0.0 notes](https://github.com/davatorium/rofi/releases/tag/2.0.0) |
| wofi | GTK3 launcher | extra 1.5.3 | 0.1 MB | none | Adds nothing over fuzzel |
| swaync | Notification centre with a side panel of widgets (Do Not Disturb, button grid, volume and brightness sliders, calendar, media) — the closest thing to Windows 11's Quick Settings + notification panel | extra 0.12.6 | 0.7 MB | gtk4-layer-shell, libgee, **granite7** | ❌ Pulls **libadwaita** (GNOME's library) and **granite7** (elementary OS) and replaces mako + our bell applet. Fails D-56/D-57. 📄 [README](https://github.com/ErikReider/SwayNotificationCenter) |
| eww | Widget kit: you draw any panel or pop-up yourself | **chaotic-aur / AUR** only | — | — | ⚠️ AUR, and everything is hand-built in its own language |
| AGS (aylurs-gtk-shell) | Widget kit in TypeScript | chaotic-aur only | — | — | ❌ AUR, JavaScript runtime |
| walker | GTK4 launcher; needs the **elephant** helper service running | AUR only (2.17.2) | — | — | ❌ AUR + a background service. 📄 [README](https://github.com/abenz1267/walker) |
| anyrun | Rust launcher | chaotic-aur / AUR | — | — | ❌ AUR |
| tofi, sfwbar, yambar, ashell, hyprpanel | Launcher / bars | AUR only | — | — | ❌ AUR (ashell and hyprpanel also target Hyprland/Niri) |
| crystal-dock, Latte | Docks | AUR / KDE | — | — | ❌ Qt/KDE pieces |

**A finding that opens a door:** Python, GTK3 and the layer-shell library's Python bindings are
**all already installed** (`python-gobject` 3.56.3, `/usr/lib/girepository-1.0/GtkLayerShell-0.1.typelib`,
✅ checked). That means hypeForge can build its **own** small graphical pop-ups — a Kickoff-style
launcher, a Quick Settings panel, a calendar flyout, a Mac OS 9 Apple menu — with **zero new
packages**, reading our existing settings files. It is a choice for Javier: these are graphical
windows, not terminal apps (D-57 rule 1), in the same family as Waybar and fuzzel.

---

## 3. The six styles, one recipe each

*Every recipe assumes: one Waybar process, our applets unchanged, the theme's colours from the
theme file (helper 03), and the bar on all three screens unless said otherwise.*

### Style 1 · Windows 11

**What it is** (📄 [Microsoft: customise the taskbar](https://support.microsoft.com/en-us/windows/customize-the-taskbar-in-windows-0657a50f-0cc7-dbfd-ae6b-05020b195b07)):
a bottom taskbar, **centred by default** (left alignment optional); Start, pinned and running apps
in the middle; on the right the tray with a **hidden-icons menu** (the "overflow area", the up-arrow),
the **Quick Settings** button (network · volume · battery as one button that opens a panel), then the
time and date, which opens the notification centre and calendar. Pop-ups have rounded corners.
Javier wants a KDE-style launcher instead of Windows' Start menu.

```
┌──────────────────────────────────────────────────────────────────────── screen ─┐
│                                                                                 │
│                         [◆][📁][🌐][💬]·[▣][▣][▣]            [^] [🔊📶] 12:15 PM │
│                         start pinned     running              tray quick  10/10 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Recipe**

- **Bar:** Waybar, `"position": "bottom"`, height 48, full width (Windows 11's bar spans the screen).
- **Centre** (`modules-center`, Waybar keeps it truly centred): `custom/launcher`, the Favorites as
  **icon buttons** (applet 4 in icon mode), then `wlr/taskbar` (icons only, `all-outputs: false` so
  each screen shows its own windows, active one with a short underline pill —
  `#taskbar button.active { border-bottom: 3px solid @accent; border-radius: 4px; }`).
- **Left:** nothing, or the workspace buttons (Windows 11 keeps Task View in the centre; for us the
  workspace drop-down can sit just left of Start).
- **Right:** `group/tray-drawer` = a **chevron button** (`custom/chevron`, text `󰅃`) as the leader + `tray`
  as the hidden child, with `"drawer": {"click-to-reveal": true, "transition-left-to-right": false}`;
  then `group/quick` = `network` + `wireplumber` + `bluetooth` drawn as **one rounded pill** (CSS on
  `#quick`), then `clock` on two lines (`"format": "{:%I:%M %p\n%m/%d/%Y}"`, `{calendar}` in the
  tooltip), then the bell (applet 7). Our clipboard, drives and printers go **into the drawer** with the
  tray, the way Windows hides less-used icons.
- **Shape (CSS):** bar background a solid or 85 % colour; `#taskbar button`, `#custom-launcher`,
  favourites: `border-radius: 6px; padding: 4px 8px;`, hover = a soft lighter tile; tooltips
  `tooltip { border-radius: 8px; }`.
- **Launcher:** see §4.2 (KDE-style). Opens **above** the Start button, centred: fuzzel with
  `--anchor bottom` today.

**What our applets keep doing:** all of them; only the positions move.

**What is missing and would need building**

1. **Pinned and running as one icon** (Windows shows a pinned app once, with a line under it while it
   runs). Waybar shows Favorites and the taskbar separately, so an open favourite would appear twice.
   *Build:* applet 4 writes one `custom/pin#<app>` per favourite with a `running`/`active` class (it can
   ask Sway, through `common/hfsway.py`), and adds those app ids to the taskbar's `ignore-list`. Medium.
2. **The pop-up panels** (Quick Settings with toggles and sliders, the calendar flyout, the
   notification panel). Waybar cannot draw a panel. Today each button opens a terminal tool in a
   floating window. *Build options:* §4.3.
3. **Choosing which tray icons hide.** Waybar's tray has no per-icon hide; the drawer hides the whole
   tray at once. Not buildable inside Waybar's tray.
4. **Rounded right-click menus of tray apps.** `#tray menu { border-radius: … }` can be set, but GTK3
   pop-up menus on Wayland may keep square corners behind the rounding. ⚠️ unverified — bench.

**Feasibility:** **close** for the bar (positions, centring, chevron drawer, pills, two-line clock are
all built-in); **approximate** for the flyouts until §4.3 is built.
**Cost:** 0 packages.

### Style 2 · Mac OS 9.x (classic) — Javier's favourite bar

**What it is:** a thin **top** menu bar in the grey "platinum" look. At the far left the **Apple
menu** — in classic Mac OS it held a shortcut to the **Control Panels**, an **Apple Menu Items**
folder of favourite apps and documents, and (from System 7.5) **Recent Applications / Documents /
Servers** submenus (📄 [Wikipedia: Apple menu](https://en.wikipedia.org/wiki/Apple_menu)). Then the
front app's own menus. At the **far right, the Application menu**, shown as the **icon of the active
application**; it lists the open programs and switches between them, and from Mac OS 8.5 it can be
**torn off** into a floating window, the *Application Switcher* (📄 Wikipedia as above; 📄 [Mac OS 9 Help:
switching between open programs](https://www.chem.uwec.edu/Chem101/System%209Folder/Help/Mac%20Help/fp/pgs/fpSwtprg.htm)).
The clock sits just left of it. Its top items were *Hide <app> · Hide Others · Show All* ⚠️ (from
memory, not found in the sources read today). Classic Mac OS had **no tray**; small controls lived in
the **Control Strip**, a collapsible strip at the bottom-left of the screen ⚠️ (from memory).

```
┌────────────────────────────────────────────────────────────────────── screen ─┐
│ ◆  Alacritty  Window  Workspaces ▾  Favorites ▾          12:15 PM   🖥 Alacritty│  ← 22 px platinum
│                                                                                │
│▐[◀ 🔊 📶 📋 🖨 ]   ← the "Control Strip": a drawer at the bottom-left           │
└────────────────────────────────────────────────────────────────────────────────┘
```

**Recipe**

- **Bar:** Waybar top, height 22–24, full width, `"exclusive": true`.
- **Platinum CSS:** `window#waybar { background: linear-gradient(to bottom, #EEEEEE, #CCCCCC);
  border-bottom: 1px solid #000; color: #000; }`; menu titles get a **solid inverted highlight** on
  hover and when open (`#custom-x:hover { background: #3333AA; color: #fff; }` — the classic blue
  highlight is themable), square corners everywhere, no shadows. Font: a Chicago-/Charcoal-style
  bitmap face if one with a shipping licence exists ⚠️ (Apple's own fonts cannot be shipped; helper 03
  or 05 should check a free look-alike).
- **Left:** `custom/apple` = our KognogOS emblem button. Two ways to make it a *real* menu:
  - **(a) Waybar's own drop-down** (`"menu": "on-click"`, a GTK menu file with submenus):
    *About This Computer* (fastfetch in a terminal) · *hypeForge Settings* (= Control Panels) ·
    a submenu per launcher group from `sections.toml` · *Recent Applications* · *Lock · Log Out ·
    Restart · Shut Down*. Faithful look (a true cascading menu under the emblem). Limit: the menu is
    read once, so applet 4 must rewrite the file and reload Waybar when apps are installed — and the
    recent list goes stale. ✅ mechanism checked in source.
  - **(b) Our fuzzel launcher** as today (always current, searchable, not a cascading menu).
  - Recommend **(a) for the static parts + one "Applications…" item that opens (b)**.
- Then `sway/window` with `"format": "{app_id}"`, a `rewrite` table for nice names
  (`"google-chrome": "Chrome"`), **bold** — the front app's name, as Mac OS 9 showed it.
- Then our **own** menus in menu-bar style: `Window` (Float · Full Screen · Tab · Move to workspace ·
  Close — Sway commands, a Waybar `menu` file, ✅ mechanism checked), `Workspaces ▾` (applet 1, today's
  drop-down), `Favorites ▾` (applet 4, today's drop-down). These are *ours*, not the app's (§2.3).
- **Right:** `clock` (`"{:%I:%M %p}"`), then **`custom/appmenu`** = the Application menu: shows the
  focused app's **icon** (or icon + name); click = a fuzzel list of open windows, grouped by app, with
  *Hide <app>* (send to scratchpad) · *Hide Others* · *Show All* (bring the scratchpad back) at the top.
- **The Control Strip** (optional, delightful): a **second, tiny Waybar** at the bottom-left
  (`"position": "bottom"`, `"width": 2`, `margin-left: 0`, `"exclusive": false`, `"layer": "top"`)
  holding `group/strip` with a drawer: the leader is a tab handle; the children are tray, volume,
  network, Bluetooth, clipboard, drives, printers. Click the handle and it slides open, as the strip
  did. ⚠️ A non-exclusive bar sits over windows — the collapsed handle must stay small.
- **Screens:** Mac OS 9 drew the menu bar on the main screen only. Javier picks: menu bar on DP-3
  only (`"output": "DP-3"`) or on all three.

**What our applets keep doing:** all; the workspaces and favourites drop-downs already *are* Mac-style
menu titles.

**Missing / to build:** the Apple-menu file generator (from `sections.toml` + Settings entries);
`custom/appmenu` (new small applet: focused-app icon + the switcher list + Hide/Show via scratchpad);
the `Window` menu file; the Control Strip bar. The app's own File/Edit menus: **not possible** (§2.3).
A tear-off Application Switcher palette: possible only as our own GTK window (§4.3), not in Waybar.

**Feasibility:** **close** — the bar's look, the Apple menu, the app name, the Application menu and the
Control Strip are all reachable; only the app's own menus are missing.
**Cost:** 0 packages.

### Style 3 · Modern macOS

**What it is:** a top menu bar (Apple menu, front app name **bold**, its menus; on the right status
icons, Control Centre, date and time) and a **Dock** at the bottom. Dock settings (📄 [Apple: Desktop &
Dock settings](https://support.apple.com/guide/mac-help/change-desktop-dock-settings-mchlp1119/mac)):
size, **magnification**, position (left/bottom/right), auto-hide and show, a **small dot under open
apps**, and an optional area of suggested and recent apps at one end.

**Recipe**

- **Top bar:** Waybar top, 28–30 px, **see-through** (`background: alpha(@bar, 0.75)`); left: emblem
  (Apple-menu role, as style 2) · `sway/window` bold · `Window` menu · Workspaces ▾; right: tray, our
  indicators (icon-only), `custom/control` (Control-Centre role, §4.3), `clock`
  `"{:%a %b %d  %I:%M %p}"`. With SwayFX the bar can be blurred.
- **The Dock — two ways:**
  - **(A) A second Waybar** (0 packages): `"position": "bottom"`, `"width": 2` (hugs its icons, centred),
    `"margin-bottom": 8`, `"name": "dock"`; modules: pinned icons (the §Style-1 build #1) + `wlr/taskbar`
    for the rest + a separator + `custom/trash`/Files. CSS: `window#waybar.dock { background:
    alpha(@surface, 0.6); border-radius: 18px; box-shadow: 0 6px 24px rgba(0,0,0,.35); }`, the running dot
    as `#taskbar button.active { border-bottom: 2px solid … }` or a background dot. Auto-hide only on the
    Win key (`"mode": "hide"`), not on the mouse edge.
  - **(B) nwg-dock** (extra, 5 MB, no new libraries): `nwg-dock -d -i 48 -mb 8 -s hypeforge.css` — pinned
    + running, mouse-edge **auto-hide**, its own CSS, a launcher button. ⚠️ It reads app icons only by
    the window's app id, and its README says to stop it with `pkill -f nwg-dock` — **never do that here**
    (our rule: never kill by command-line search); stop it by exact name or saved PID.
- **Magnification:** **not available** on Sway in a faithful way (no dock offers the wave). The closest
  is enlarging only the icon under the mouse with `-gtk-icon-transform: scale(1.35)` on `:hover` plus
  a `transition` ⚠️ unverified — the icon may be clipped by its button; bench it.

**What our applets keep doing:** all, in the top bar.
**Missing / to build:** the pinned+running merge (shared with style 1); Control Centre panel (§4.3);
magnification (not buildable faithfully).
**Feasibility:** **close** (bar faithful, dock close, no magnification).
**Cost:** 0 packages (Dock A) or nwg-dock 5 MB (Dock B).

### Style 4 · A modern Linux "rice" (r/unixporn style)

**What it is:** a top bar that **floats** with a gap from the screen edges, often split into separate
rounded "islands" (left · centre · right), **pill-shaped workspace buttons** (the active one longer),
see-through backgrounds, often blur and soft shadows. This is Waybar's home ground — most of those
setups *are* Waybar.

**Recipe**

- **Bar:** Waybar top, `"margin": "8 12 0 12"`, height 34, `"exclusive": true` (windows keep a gap below).
- **Islands:** `window#waybar { background: transparent; }`, then each block gets its own pill:
  `.modules-left, .modules-center, .modules-right { background: alpha(@surface, 0.80); border-radius:
  14px; padding: 0 10px; box-shadow: 0 2px 10px rgba(0,0,0,.30); }`. For a centre island that is only as
  wide as the clock, the default layout already works (`fixed-center: true`).
- **Pill workspaces:** our `custom/ws` buttons — `border-radius: 10px; min-width: 18px; transition:
  min-width 200ms;` and `#custom-ws.active { min-width: 36px; background: @accent; }` (the "longer
  active pill"). Applet 1 may need a compact mode that shows only the number or a dot.
- **Sway side** (helper 01): `gaps outer` above 0 so windows line up with the floating bar; with SwayFX,
  `layer_effects "waybar" blur enable; shadows enable` for frosted islands.
- **Launcher:** fuzzel centred (`--anchor center`), rounded (`[border] radius=12` in fuzzel.ini) — the
  rice-standard look, nothing new to install.

**Missing:** nothing essential. Blur needs SwayFX; without it the islands are see-through but sharp.
**Feasibility:** **faithful** (without blur on plain Sway: close).
**Cost:** 0 packages (SwayFX if blur is wanted — a separate decision).

### Style 5 · KDE Plasma

**What it is:** a full-width **bottom panel**; at the left the **Kickoff** launcher, then the task
manager, then on the right the system tray (with an arrow for hidden icons) and the digital clock with
the date beneath. Kickoff since Plasma 5.21 is a **two-pane** pop-up: a **grid of favourites**, an
alphabetical **All Applications** view, and the power actions (Sleep · Restart · Shut Down) **at the
bottom** (📄 [KDE Plasma 5.21 announcement](https://kde.org/announcements/plasma/5/5.21.0/)); search at the
top, categories, and *Applications / Places* tabs (📄 [KDE UserBase: Kickoff](https://userbase.kde.org/Plasma/Kickoff),
older page). The left-hand category list with the user picture on top is ⚠️ from memory of Plasma
5.21+/6, not confirmed in a Plasma 6 document today.

```
┌──────────────────────────────────────────────────────────────────── screen ─┐
│ [◆] [🌐 Chrome — GitHub] [▣ Alacritty] [▣ btop]        [^] 🔊 📶 🔔  12:15 PM │
│                                                                   10/10/2026 │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Recipe**

- **Bar:** Waybar bottom, full width, height 44, square or lightly rounded, a top border line.
- **Left:** `custom/launcher` (emblem), Workspaces ▾, then `wlr/taskbar` with **icon + title**
  (`"format": "{icon} {title}"`, a max length via `rewrite`, each button a rounded tile, the active one
  filled) — KDE's task manager. Pinned apps as in style 1 build #1 (KDE's icons-only task manager
  merges pinned and running too).
- **Right:** the same chevron drawer + tray as style 1 (KDE's tray also hides icons behind an arrow),
  our indicators, the bell, `clock` two lines (`"{:%I:%M %p}\n{:%m/%d/%Y}"` — ⚠️ check the two-format
  syntax on 0.15; the single-format `"{:%I:%M %p\n%m/%d/%Y}"` is safe).
- **Launcher:** §4.2. This is the style where the launcher matters most.

**What our applets keep doing:** all.
**Missing:** Kickoff (§4.2); KDE's clickable calendar pop-up (tooltip calendar only, or §4.3).
**Feasibility:** panel **faithful**; launcher **close** (nwg-menu or our own) to **approximate** (fuzzel).
**Cost:** 0 packages (own/fuzzel) or nwg-menu 5 MB.

### Style 6 · COSMIC (System76)

**What it is** (📄 [System76: Pop!_OS basics](https://system76.com/support/pop-basics)): a **top panel**
with the **clock in the middle** (calendar pop-up) and applets for volume, Bluetooth, Wi-Fi, power, and
log out/restart/shut down; a **"Workspaces"** label at the top-left. A **dock** at the bottom with pinned
apps, running apps and minimised windows; its **Launcher** (search, also a calculator and file search),
**Workspaces** (an overview) and **Applications** (the *App Library*: installed apps in alphabetical
order, with search and folders) are separate dock applets. Dock options: auto-hide, **extend to the
edges or stay in the middle**, size, background opacity. Rounded, soft shapes. (Exact left/right
placement of panel applets is not stated on that page.)

**Recipe**

- **Top panel:** Waybar top, height 32, full width or floating (`margin 6 8 0 8`, `border-radius: 12px`).
  Left: `Workspaces ▾` (applet 1) and an `Applications` text button (applet 4's group view);
  centre: `clock` (`"{:%b %d %I:%M %p}"`, `{calendar}` tooltip); right: tray drawer, our indicators,
  the bell, power.
- **Dock:** as style 3 (second Waybar or nwg-dock), centred, rounded 16 px, 70–80 % opacity; first three
  buttons = **Launcher** (fuzzel centred, COSMIC's launcher is a centred search box — a very good match),
  **Workspaces** (applet 1's menu — Sway has no overview, §2.3), **Applications** (App Library: fuzzel's
  "All apps", or **nwg-drawer**, the real full-screen grid, 41 MB).
- **Shape:** generous rounding (12–16 px), soft shadows, light borders — the COSMIC signature.

**Missing:** COSMIC's applet pop-ups (§4.3); a workspace overview (not possible on Sway).
**Feasibility:** **close**.
**Cost:** 0 packages; nwg-dock 5 MB and/or nwg-drawer 41 MB if wanted.

### Scorecard

| Style | Bar | Tray | Launcher | Dock | Overall | Packages to add |
|---|---|---|---|---|---|---|
| 1 Windows 11 | close | close (drawer, all-or-nothing) | KDE-style, §4.2 | — | **close** (flyouts approximate) | 0 |
| 2 Mac OS 9 | close | Control Strip drawer | Apple menu (Waybar menu) + fuzzel | — | **close** (no app menus) | 0 |
| 3 macOS | faithful | close | fuzzel / own | close, no magnification | **close** | 0 or nwg-dock |
| 4 Linux rice | faithful | faithful | faithful (fuzzel) | — | **faithful** (blur = SwayFX) | 0 |
| 5 KDE | faithful | close | close → approximate | — | **close** | 0 or nwg-menu |
| 6 COSMIC | close | close | close (fuzzel centred) | close | **close** | 0 or nwg-dock / nwg-drawer |

---

## 4. The shared "bar kit"

### 4.1 One Waybar that morphs: the shape of it

**Recommendation: keep Waybar as the only bar.** It covers every style; switching bars (ironbar,
nwg-panel) would mean rewriting every module config for a gain only in pop-ups, and we can get
pop-ups our own way (§4.3).

How the files would be laid out (a proposal for the theme app — Phase 2 decides the format):

```
~/.config/sway/waybar/
  config.jsonc        ← written by the theme step: a LIST of bars, built from the style's layout
  style.css           ← written by the theme step: three @import lines, nothing else
~/.config/hypeforge/look/
  theme.css           ← colours only (@define-color tokens), from the theme (one of 23)
  styles/<style>/layout.jsonc   ← which bars, where, which modules in which order, formats
  styles/<style>/shape.css      ← corners, sizes, gaps, shadows, see-through amounts
```

- **Modules are defined once** (one shared `modules.jsonc` with every `custom/*`, tray, clock… and their
  click actions) and pulled in with Waybar's `include`; a style's `layout.jsonc` only lists names in
  `modules-left/center/right`, plus position, height, margins, width, and extra bars (dock, Control
  Strip). Waybar's rule that the *first* definition wins (`man 5 waybar` · `include`) means a style can
  override a module's `format` (icon-only vs text) by defining it before the shared include. In a
  list of bars, **each bar object needs its own `include`** — an include only affects the bar it sits
  in (✅ same man page).
- **CSS order:** `@import` lines must come first (our `style.css` already does this): theme colours →
  shape → the applets' own generated CSS (favourites icons).
- **Bar names as CSS classes** (`"name": "dock"`, `"name": "strip"`) let one `shape.css` style the main
  bar, the dock and the Control Strip separately (✅ `man 5 waybar` · `name`).
- **The switch:** `hypeforge-theme apply <style> <colour>` writes the two files, then reloads Waybar with
  `SIGUSR2`, sent **by exact process name** (`pkill -USR2 -x waybar`), never by command-line search.
  A colour-only change can use `"reload_style_on_change": true` and needs no reload at all.
- **Applets learn one switch each:** a `display = "icons" | "text"` setting (Favorites as icons in
  Windows/KDE/dock styles, as the "Favorites ▾" menu title in Mac styles), read from their own settings
  file, so the theme step never touches applet code (D-59: apps read each other's settings files).
- **Bench first:** the hidden bench (`scripts/headless-check.py`) already runs a screen-less Sway with
  three fake screens; a style switch should be proven there (bars appear on all three, no error in
  Waybar's log) before it reaches the desktop.

### 4.2 The launcher — Javier wants KDE's, not Windows'

| Option | Looks like Kickoff? | Uses our groups (`sections.toml`)? | Cost | Note |
|---|---|---|---|---|
| **A. Our fuzzel launcher, restyled** (have) | Approximate: a rounded list, two steps (group → apps), search | ✅ yes | 0 | Works today; the step to rounding is `radius=` in fuzzel.ini. No side-by-side panes, no grid |
| **B. nwg-menu** | Close: categories with sub-menus, search, pinned on top, power buttons, icons, its own CSS | ❌ its own 8 categories | 5 MB, 0 new libraries | Opens bottom-left or top-left with margins, so it fits every bar position |
| **C. Our own launcher window** (Python + GTK3 + layer-shell, all installed) | **Faithful**: search on top, groups in a left column, favourites grid on the right, power row at the bottom, rounded, themed from the same tokens | ✅ yes, and our workspace routing (F-50) | 0 packages; real build work (a new applet) | A graphical window, not a terminal app — Javier's call under D-57 |
| D. ironbar's menu module | Close (categories → sub-menus) | partly (its own category lists) | 26 MB + replacing Waybar | Not worth the swap |
| E. nwg-drawer | No (a full-screen grid — the COSMIC/GNOME App Library) | ❌ | 41 MB | Good only as COSMIC's "Applications" |

**Recommendation:** keep **A** working everywhere (it is the keyboard path and always current). For the
KDE and Windows styles, propose **C** as the KognogOS launcher, and use **B** as a quick, zero-build
preview in the mock-up review so Javier can feel a Kickoff-like menu on his own desktop before we build
**C**. ⚠️ B's look on our desktop is not tested.

### 4.3 Pop-up panels (flyouts) — the one real gap

Windows 11's Quick Settings and calendar, macOS' Control Centre, COSMIC's applet pop-ups, KDE's
calendar. Waybar draws **no** panels (only tooltips and menus). Options, best first:

1. **Our own GTK3 layer-shell pop-ups** (same building block as launcher C): one small applet,
   `hypeforge-flyout quick|calendar|…`, opened from the bar button, anchored to the bar edge, rounded,
   themed, closing on Esc or on losing focus. Quick Settings tiles: Wi-Fi, Bluetooth, Do Not Disturb (our
   bell applet's setting), night light (nightForge), volume slider (wpctl). 0 packages; build work.
2. **Forge app TUIs in a borderless floating Alacritty** placed under the button with a Sway rule —
   today's way, on-brand with D-57, looks like a terminal.
3. eww (AUR) or swaync (GNOME/elementary libraries) — fail our rules (§2.4).

### 4.4 Things to build, smallest first

| # | Build | For styles | Size |
|---|---|---|---|
| B-1 | Tray drawer: chevron leader + `tray` (+ our less-used icons) in a click-to-reveal group | 1, 3, 5, 6 | config only — bench "tray inside a drawer" |
| B-2 | Favourites as icon buttons, `display` setting in applet 4 | 1, 3, 5, 6 | small |
| B-3 | Pinned + running merged (classes from Sway, taskbar `ignore-list`) | 1, 3, 5, 6 | medium |
| B-4 | `custom/appmenu` (focused app icon + switcher list + Hide/Show via scratchpad) | 2, 3 | small–medium |
| B-5 | Waybar menu files: Apple menu (generated from `sections.toml`), Window menu | 2, 3 | small |
| B-6 | Second bar (dock / Control Strip) in the layout file + `"width": 2` shrink test | 2, 3, 6 | config + bench |
| B-7 | The theme step: layout/shape/theme files → `config.jsonc` + `style.css`, reload by exact name | all | medium |
| B-8 | Flyouts (§4.3 option 1) | 1, 3, 5, 6 | large |
| B-9 | Kickoff-style launcher (§4.2 option C) | 1, 5 (any) | large |

---

## 5. Questions for Javier (to answer during the proposals, not now)

1. Mac OS 9 style: the menu bar on the **middle screen only** (as the real Mac did) or on all three?
2. The Control Strip at the bottom-left: charming or clutter?
3. Graphical pop-ups and launcher of our own (§4.2 C, §4.3 option 1) — yes, or stay with terminal tools
   in floating windows?
4. Dock: a second Waybar (nothing to install, auto-hide only on the Win key) or nwg-dock (5 MB,
   auto-hide at the screen edge)?

---

## 6. What was not proven (bench before relying on it)

- A `"width": 2` bar **shrinking back** when its contents get smaller (needed for a hugging dock).
- `tray` **inside a group drawer** behaving well (icons, menus) on our Waybar 0.15.
- Rounded corners on **GTK3 pop-up menus** (tray right-click, Waybar `menu`) on Wayland.
- `-gtk-icon-transform: scale()` on hover in `#taskbar button` without clipping (the "magnify" stand-in).
- The taskbar's `minimize` doing nothing on Sway (from experience).
- No Sway bar can show an app's own File/Edit menus (no source found that says otherwise; none that
  proves it either).
- Mac OS 9 details from memory: *Hide / Hide Others / Show All* in the Application menu; the Control Strip.
- Plasma 6 Kickoff's exact left-column categories and header (Plasma 5.21 description verified).
- nwg-menu and nwg-dock's real look and multi-screen behaviour on our three screens.
- ironbar options were read on its `master` docs; Arch ships 0.19.1.

---

## 7. Commands run (all read-only)

```
waybar --version; sway --version; fuzzel --version; pacman -Q waybar sway fuzzel mako gtk3 gtk-layer-shell
pacman -Si <nwg-panel nwg-dock nwg-drawer nwg-menu wofi rofi ironbar eww swaync swayfx …>
nog search nwg-dock   ·   nog search eww          (nog 1.8.0, search only)
curl https://aur.archlinux.org/rpc/v5/info?arg[]=walker&…   (AUR lookup)
man 5 waybar | waybar-menu | waybar-tray | waybar-wlr-taskbar | waybar-sway-window | waybar-clock | waybar-custom | waybar-styles
curl raw.githubusercontent.com/Alexays/Waybar/0.15.0/src/{bar.cpp,ALabel.cpp,AModule.cpp,group.cpp}
swaymsg -t get_outputs;  grep waybar|fuzzel ~/.config/sway/config;  cat ~/.config/sway/fuzzel/fuzzel.ini
ls /usr/lib/girepository-1.0/   (GtkLayerShell-0.1.typelib present)
```

## 8. Sources

- Waybar 0.15.0 manual pages, installed: `waybar(5)`, `waybar-menu(5)`, `waybar-tray(5)`,
  `waybar-wlr-taskbar(5)`, `waybar-sway-window(5)`, `waybar-clock(5)`, `waybar-custom(5)`, `waybar-styles(5)`
- Waybar source at tag 0.15.0: [bar.cpp](https://github.com/Alexays/Waybar/blob/0.15.0/src/bar.cpp),
  [ALabel.cpp](https://github.com/Alexays/Waybar/blob/0.15.0/src/ALabel.cpp),
  [group.cpp](https://github.com/Alexays/Waybar/blob/0.15.0/src/group.cpp)
- [GTK3 CSS properties](https://docs.gtk.org/gtk3/css-properties.html)
- [SwayFX README](https://github.com/WillPower3309/swayfx)
- [nwg-dock](https://github.com/nwg-piotr/nwg-dock) · [nwg-menu](https://github.com/nwg-piotr/nwg-menu) ·
  [nwg-drawer](https://github.com/nwg-piotr/nwg-drawer) · [nwg-panel](https://github.com/nwg-piotr/nwg-panel)
- [ironbar docs](https://github.com/JakeStanger/ironbar/tree/master/docs) (launcher, menu, tray modules)
- [SwayNotificationCenter README](https://github.com/ErikReider/SwayNotificationCenter)
- [rofi 2.0.0 release notes](https://github.com/davatorium/rofi/releases/tag/2.0.0)
- [walker README](https://github.com/abenz1267/walker)
- [Microsoft: Customize the taskbar in Windows](https://support.microsoft.com/en-us/windows/customize-the-taskbar-in-windows-0657a50f-0cc7-dbfd-ae6b-05020b195b07)
- [Wikipedia: Apple menu](https://en.wikipedia.org/wiki/Apple_menu) ·
  [Mac OS 9 Help: switching between open programs](https://www.chem.uwec.edu/Chem101/System%209Folder/Help/Mac%20Help/fp/pgs/fpSwtprg.htm) ·
  [O'Reilly, Mac OS 9: Using the Application Switcher](https://oreilly.com/library/view/mac-os-9/0201700042/0201700042_ch05lev1sec4.html)
- [Apple: Desktop & Dock settings](https://support.apple.com/guide/mac-help/change-desktop-dock-settings-mchlp1119/mac)
- [KDE Plasma 5.21 announcement](https://kde.org/announcements/plasma/5/5.21.0/) ·
  [KDE UserBase: Kickoff](https://userbase.kde.org/Plasma/Kickoff)
- [System76: Pop!_OS / COSMIC basics](https://system76.com/support/pop-basics)
- Arch package data: `pacman -Si` (core/extra/chaotic-aur), AUR RPC v5 — 2026-10-10
