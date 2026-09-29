# hypeForge — decision log

*Every decision that shapes hypeForge, dated, with who made it and why. Newest first.*
*A decision here is only reopened by Javier. **Proposed** entries are suggestions still waiting for his answer.*

---

## 2026-09-29

### D-22 · The tools: Midnight Commander + superfile + Krusader, nmtui, bluetui, wiremix, btop + nvtop
**Decided by Javier** ([RECIPE.md, jobs 14–18](RECIPE.md#14-file-manager-terminal-first-plus-one-graphical-fallback)).
- **Job 14, file manager: Midnight Commander + superfile + Krusader.** This differs from the lean (Yazi + Thunar). Midnight Commander and Krusader were not among the researched options; they were checked the same day:
  - **Midnight Commander** (`extra/mc` 4.8.33, **already installed**): the classic two-panel terminal file manager, ★997, commits 2026-09. A Catppuccin theme exists ([catppuccin/mc](https://github.com/catppuccin/mc)) but was last updated 2022.
  - **superfile** (`extra/superfile` 1.6.0): a terminal file manager with side-by-side panels and an official Catppuccin theme, ★23.5k, release 2026-06.
  - **Krusader** (`extra/krusader` 2.9.0, 14.7 MiB): a graphical two-panel file manager from KDE. It does **not** need `plasma-workspace`, but it depends on about 30 KDE Frameworks libraries (KIO, KWallet, Solid and others), **so those stay installed after Plasma leaves** (D-6). Today they are all already present, so installing it adds only Krusader itself. Whether it looks right when Qt follows GTK (D-21) is untested.
  - **Thunar is not part of the recipe.** It stays installed for now and can be removed later.
  - The terminal file-window idea from job 31 (D-16) would now pair with **superfile**: termfilechooser ships a superfile wrapper, and none for Midnight Commander.
- **Job 15, Wi-Fi: nmtui**, already installed.
- **Job 16, Bluetooth: bluetui**, Omarchy 3's choice. `bluetoothctl` stays as the fallback.
- **Job 17, sound mixer: wiremix**, Omarchy 3's choice. The volume keys use `wpctl`.
- **Job 18, system monitor: btop + nvtop.** btop is already installed; nvtop adds the per-program graphics-card view.

### D-21 · Clipboard, screenshots, recording and the look of other apps
**Decided by Javier** ([RECIPE.md, jobs 10–13](RECIPE.md#10-clipboard-history)).
- **Job 10, clipboard history: Walker's own.** Walker's service, elephant, has a clipboard provider for text and pictures. This is Omarchy 3's setup (Super+Ctrl+V), and nothing extra is installed. It replaces the lean (cliphist + fuzzel), which assumed fuzzel as the launcher (D-18).
- **Job 11, screenshots: grim + slurp + Satty**, Omarchy 3's trio. A small hypeForge script picks area, window or monitor.
- **Job 12, screen recording: both gpu-screen-recorder and OBS Studio.** gpu-screen-recorder handles quick recordings from a key, using the RTX 3060's own encoder. OBS handles bigger jobs. Omarchy 3 and 4 install the same pair.
- **Job 13, the look of other apps: Catppuccin Mocha everywhere.** GTK uses `adw-gtk-theme` (the Arch name for adw-gtk3) plus a Catppuccin Mocha colour file, with dark mode on. Qt apps follow GTK (`QT_QPA_PLATFORMTHEME=gtk3`, Omarchy 4's method). The cursor is the Catppuccin Mocha set that is already installed. The dark-mode setting is also what apps read through the GTK portal (D-16).

All of it is in `extra` (checked with `nog search` 2026-09-29). None of it is installed on the test desktop yet.

### D-20 · The background helpers: SwayOSD, hyprlock + hypridle, hyprpaper, hyprpolkitagent
**Decided by Javier**, agreeing with every lean in [RECIPE.md, jobs 4–8](RECIPE.md#4-volume--brightness-pop-ups-osd).
- **Job 4, volume pop-up: SwayOSD**, Omarchy 3's choice. SwayOSD only drives built-in screen backlights, so **monitor brightness is a separate key binding through `ddcutil`**.
- **Jobs 5 + 6, lock screen and screen-off timer: hyprlock + hypridle**, the Hyprland team's pair. hypeForge must always ship hyprlock's settings file, because without one it refuses to lock. Commands inside hypridle's file use the new Lua wording.
- **Job 7, wallpaper: hyprpaper.** A separate picture per monitor, changeable while running.
- **Job 8, admin-password pop-up: hyprpolkitagent.** `polkit-kde-agent` leaves with Plasma.

Four of the five come from the Hyprland team, so they update with Hyprland inside the nog lock (D-9).

**Checked on the test desktop the same day (read-only):** `ddcutil` 3.0.2 is installed, and all three Sceptre Y27 monitors answer DDC/CI on I2C buses 3, 4 and 5 (brightness read as 75 of 100 on each). **Quirk:** all three report the same model, the same serial and the same connector (`card1-DP-1`), so the brightness binding must address monitors by bus number, not by name.

### D-19 · Notifications: mako
**Decided by Javier**, agreeing with the lean in [RECIPE.md, job 3](RECIPE.md#3-notifications). mako is a tiny notification service with one plain-text settings file and a Catppuccin port, and it was Omarchy 3's choice. History, restore and do-not-disturb work through `makoctl`, bound to keys.

### D-18 · App launcher: Walker
**Decided by Javier.** This differs from Claude's lean (fuzzel). Walker was Omarchy 3's launcher. It searches apps and also has modules for the calculator, files, clipboard, symbols and more. A small background service called **elephant** feeds it ([RECIPE.md, job 2](RECIPE.md#2-app-launcher--menu)).
**What it means:**
- **Walker and elephant are AUR only** (checked 2026-09-29: `walker` 2.17.1, `elephant` 2.22.1, both updated 2026-09-24; neither is in `extra` or chaotic-aur). **This makes nog's AUR path a real requirement**, not an option. It gets tested early, and every gap is a nog finding.
- Walker's own modules may cover later jobs: clipboard history (job 10, where the lean had fuzzel as the picker) and the power menu (job 29, where the lean was a rofi list). Those jobs get re-read with Walker in mind before they are decided.
- It is heavier than fuzzel (GTK 4, plus an always-running service). That is accepted.

### D-17 · Top bar: Waybar, on the development build until a release fixes it
**Decided by Javier**, agreeing with the lean in [RECIPE.md, job 1](RECIPE.md#1-top-bar). Waybar is the best-documented bar, with a Catppuccin port.
**What it means:**
- The released Waybar 0.15.0 cannot switch workspaces by click with Hyprland's Lua settings ([#5294](https://github.com/Alexays/Waybar/issues/5294)). The fix is merged but unreleased; checked again 2026-09-29, and the latest release is still 0.15.0.
- Until a release after 0.15.0 exists, hypeForge uses **`waybar-git` from chaotic-aur**, installed through nog. It moves back to the regular `waybar` as soon as that release reaches `extra`.

### D-16 · Portals: Hyprland's own for screen sharing, GTK for the file window
**Decided by Javier**, agreeing with the lean in [RECIPE.md, job 31](RECIPE.md#31-file-open-dialogs-and-screen-sharing-portals). A *portal* is the hidden helper apps call for the "open file" window, screen sharing, screenshots and the dark-mode question.
- **Screen sharing, screenshots, global shortcuts:** `xdg-desktop-portal-hyprland`.
- **The "open file" / "save as" window:** `xdg-desktop-portal-gtk`, already installed. It is the Hyprland wiki's recommendation and the same pair Omarchy 4 uses.
- **`xdg-desktop-portal-kde` leaves with Plasma.** It depends on `plasma-workspace`, so keeping it would keep Plasma's core.
- **Job 13 must set dark mode in the GTK settings**, because under Hyprland the GTK portal is what answers apps asking "is dark mode on?".
- A terminal (Yazi) file window stays an idea to try in Phase 2, once nog's AUR path is tested. It is not part of this decision.

## 2026-09-28 — the first night

### D-15 · The login screen is greetd + tuigreet
**Decided by Javier**, after seeing the project's own screenshots and sources: *"terminal look and lighter fits."* **greetd** is a tiny login service that runs whatever login screen it is given. **tuigreet** is a login screen drawn in text, with username and password, the date, and a session picker on F3 (Hyprland, or Plasma while it is still the fallback), plus power actions on F12. The research halves had disagreed, and this settles job 9 ([RECIPE.md, job 9](RECIPE.md#9-login-screen-display-manager)).

**What it means:**
- **It is proven in a VM before it replaces SDDM on the test desktop.** Arch's greetd has no test mode, so trying it means making it a real login screen.
- The KognogOS SDDM theme retires when the switch lands.
- Nothing needs a display server (X11) any more just to log in.
- tuigreet's colours come from the text screen's 16-colour palette. A Catppuccin palette there is an idea still to be tested, and it would also help the Forge apps on a text screen (forgekit#1).
- The work list: a bigger console font for the 1440p screens, and greetd's login settings must unlock the password wallet.

### D-14 · Separate small apps, not one all-in-one program
**Decided by Javier:** recipe job 0 goes to **separate small apps**: a top bar, a launcher, a notification service and so on, each its own program with its own settings file.
**Why it fits:**
- It matches "light, with light apps and terminal apps first".
- A broken piece can be swapped on its own, without taking the bar, notifications, lock screen and password pop-up down together.
- Every piece takes a "use this settings file" option, so the one portable folder (D-8) stays simple.

This is where we deliberately part from Omarchy 4, which moved to one Quickshell program in August 2026 (D-4). Details: [RECIPE.md, job 0](RECIPE.md#0-one-all-in-one-shell-or-separate-small-apps).

### D-13 · Documentation is written at every step, starting tonight
**Decided by Javier.** The project gets its full GitHub presence from the first night. That means the README, About, topics, labels, milestones and issues. Documentation is written as the work happens, not afterwards. The public project page at [kognogos.org](https://kognogos.org) announces hypeForge as coming soon.

### D-12 · How testing is done: virtual machines, then this desktop
**Decided by Javier:** testing happens in virtual machines. The existing test machine (`kognog-test`) **is not a real KognogOS install**. It was put together by hand without the KognogOS apps and settings. **The KognogOS installer image has to be fully rebuilt** so that a virtual machine can get a proper KognogOS install. That rebuild is KognogOS work, and hypeForge's KognogOS testing waits on it.
**Decided by Javier, the same night:** also build an **Omarchy virtual machine** as the hands-on reference. See D-4.

### D-11 · The recipe: up to five researched options per job, and Javier chooses
**Decided by Javier.** For every job (top bar, launcher, notifications, file manager…), the recipe shows **no more than five options**. They are the most reviewed and most recommended ones, each with links to sources that show how it works. Javier makes every choice. Claude may add a one-line suggestion, clearly marked as a suggestion. → [RECIPE.md](RECIPE.md)

### D-10 · Forge apps run in Alacritty, and must be readable on a plain text screen
**Decided by Javier.** Under hypeForge, the Forge apps (hypeForge included) run in Alacritty, exactly as they do today. He also agreed with the fix for [forgekit#1](https://github.com/jetomev/forgekit/issues/1): the Forge apps are currently hard to read on a plain text screen. hypeForge will often be started from a text screen, because a fresh Arch install has no desktop yet. So that fix has to land **before hypeForge ships**.

### D-9 · Updates are locked by us, through nog
**Decided by Javier:** *"nog treatment will be locked by us, to ensure it updates when needed."*
**Why:** Hyprland is linked to exact versions of six small helper packages (aquamarine, hyprcursor, hyprgraphics, hyprlang, hyprutils, hyprwire). All seven have to update together or the desktop breaks. Out of the box, nog treats all of them as ordinary packages (Tier 3, a 7-day wait) and has no way of knowing they belong together.
**What it means:** hypeForge owns a nog **group** for the Hyprland family, so the whole family moves together, and the family gets a tier we choose. The details are designed in Phase 3. → [DESIGN.md](DESIGN.md#updates-locked-by-us)

### D-8 · One portable folder; system changes only through the app
**Decided by Javier:** *"Everything from the beginning has to be installed through apps, libraries, and config files, properly saved in a folder for Hyprland to access, and easily portable. Whatever has to be installed in system folders has to be through an app using our config files."*
**Why:** installing, backing up and moving to a new computer all become simple. The folder is the backup.
**What it means:** nothing outside the home folder is ever edited by hand. The hypeForge app applies those pieces from files kept in the folder. → [DESIGN.md](DESIGN.md#one-portable-folder)

### D-7 · Floating windows by default; Win + arrow keys tile, like Plasma
**Decided by Javier:** *"Our window system has to be built to support floating windows by default, always, and tiling will come using Win+arrows to tile, simple, same as Plasma."*
**Note:** Hyprland is built for tiling first. Making every window float and adding Plasma-style snapping is possible, but it works against Hyprland's grain, so it gets proven early (Phase 1) before anything else is built on it. The key map copies the shortcuts Plasma uses on the test desktop today (read from its settings on 2026-09-28). → [DESIGN.md](DESIGN.md#floating-first-windows)

### D-6 · Plasma will be replaced
**Decided by Javier:** *"We will ditch Plasma and keep a lighter UI system. This will reshape some of our KognogOS decisions little by little, but it is a thing."*
**What it means:** hypeForge becomes the KognogOS desktop, and KognogOS moves off Plasma step by step. → [KOGNOGOS-IMPACT.md](KOGNOGOS-IMPACT.md)
**Decided by Javier, the same night:** *"Only when hypeForge works and I am fully daily driving it is when we will take down Plasma."* Until then, Plasma stays installed on the test desktop as a **fallback login choice**, so there is always a working desktop to log into while the new one is built. The condition is **daily driving**, which is more than passing tests.

### D-5 · Hyprland settings are written in Lua, from day one
**Decided with Javier (following Hyprland upstream).** From version 0.55, Hyprland's settings are written in **Lua**. The old format is supported for *"1 – 2 releases starting from 0.55. After that, hyprlang will be dropped"* ([Hyprland, 26 April 2026](https://hypr.land/news/26_lua/)). Version 0.56 is already current, so we write Lua only. Omarchy 4 made the same move.

### D-4 · Omarchy is the reference
**Decided by Javier:** [Omarchy](https://github.com/basecamp/omarchy) (MIT) is *"our reference, definitive."*
**Worth knowing:** Omarchy 4 "Quattro" (14 August 2026) replaced its separate small apps (Waybar, Walker, Mako, SwayOSD, hyprlock, hypridle, swaybg, polkit-gnome) with **one Quickshell-based desktop program**. So "follow Omarchy" and "light, separate apps" now point in different directions. The recipe asks that question first.
**Decided by Javier, the same night:** build an Omarchy virtual machine. Hyprland needs 3D graphics, even inside a virtual machine, and the virtual machines on this NVIDIA desktop have never had 3D switched on. Omarchy is a known-good Hyprland setup, so if the machine works, we know the test setup works before we test our own work in it.

### D-3 · The desktop is built on Hyprland
**Decided by Javier.** Hyprland 0.56.2 is in Arch's official repositories. It supports floating and tiled windows, and it is the base Omarchy uses.

### D-2 · It is a full project, run with the usual method
**Decided by Javier.** The project gets a full public GitHub presence, phased releases, a published test matrix with numbered findings, issues opened and closed with full explanations, and co-author credit on every commit.

### D-1 · The name is hypeForge
**Decided by Javier.** It follows the Forge Suite naming rule: `[name]Forge`, lowercase first letter. The repository and package name is `hypeforge`.
**Checked on 2026-09-28:** the name is free on the AUR and at `jetomev/hypeforge`. No other GitHub project called hypeforge is a Linux desktop tool.
**Flagged to Javier the same night:** `hypeforge` is one letter away from `hyprforge`, an active GitHub project that builds Hyprland desktop apps ([hyprforge-suite](https://github.com/hyprforge-suite/hyprforge)). The name `hyprForge` was avoided for that reason. Keeping the one-letter neighbour is Javier's call.
