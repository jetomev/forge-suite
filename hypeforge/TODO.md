# hypeForge — the list

**Target: no date set — started 28 Sep 2026; started again 4 Oct 2026 (D-44).** A Forge Suite app that installs the KognogOS tiling desktop onto any Arch install.
The reasons behind each item are in `docs/DECISIONS.md` and `docs/DESIGN.md`. This file only lists what gets done.

**The order from here (Javier, 2026-10-05):** finish the Sway setup → then every pending Forge Suite app → the first KognogOS release. Every pick follows D-57: terminal first (1), Sway-compatible (2), smallest install (3).

**Updated after every step.** Run `bash scripts/status.sh` for the short version.

---

## Phase 10 · The restart: choose the base — **in progress**
*D-44 (Javier, 4 Oct 2026): "I want to start again" — barebones tiling, terminal apps first, our own look, one step at a time. The first attempt was removed on 2026-10-05 (it lives in git history before `864885d`).*
- [x] D-44 recorded (the restart)
- [x] **The Hyprland days cleared off this computer** (Javier, 10-05): 24 packages removed with nog (hyprland + family, noctalia, uwsm, the Hyprland portal — 117 MB; Lutris's portal need is met by the wlr/gtk/kde portals), 4 old background services switched off, the old settings folders, links and launcher entries deleted. Backup first: `logs/20261005-hyprland-days-backup.tar.gz` (1,874 files, on this computer only). The login screen offers Plasma, Sway, Sway (hypeForge)
- [x] Research done (4 Oct): top pick **Sway** 1.12, runner-up **niri** 26.04; i3 the X11 safety net; Hyprland, dwm, river, MangoWC, Qtile not now. Hyprland, Sway, i3, dwm, river, niri… on NVIDIA (RTX 3060, 3 × 144 Hz), maturity, ease, tiling, terminal ecosystem, theming, community (`docs/research/2026-10-04-tiling-base-choice.md`)
- [x] Javier chose **Sway** (D-45): a new login session; the current one stays the main desktop meanwhile
- [x] Barebones session next to Plasma on this computer: tiling, a terminal, three monitors at 144 Hz, NVIDIA right, nothing else — **10-04: Javier logged in to "Sway (hypeForge)"; Claude confirmed all three screens at 144 Hz in the right order (matrix 1.4 ✅). Javier: 1.1–1.3 + 1.5 ✅ (section 1 complete). §2: 2.1 Chrome video ✅ (F-41 found); 2.2 Discord share ✅ (installed xdg-desktop-portal-wlr; F-42 found); 2.3 WoW via XWayland ❌ (F-43, pointer escapes); 2.3b WoW with Wine's Wayland driver ✅ ("runs and looks amazing"); 2.4 brightness ✅ (bus 3 = right, 4 = middle, 5 = left). **Matrix sections 1–2 complete**

## Phase 11 · The jobs, one by one, terminal first
- [ ] F-41 (#23) — deferred, stays open (Javier 10-04: works; not needed for the window setup): hardware video decoding — Chrome decodes video on the processor (no `nvidia-vaapi-driver`); smooth, low priority, machine-wide
- [ ] F-42 (#24) — waits for our own password helper (D-56): the Sway session sets no `SUDO_ASKPASS` — the password window only works when it is passed by hand; set it for the session (with the password/polkit job)
- [ ] F-43 (#25) — deferred, stays open (launcher fix not now): WoW through XWayland on Sway — pointer escapes while turning the camera, focus lost; windowed mode tiles to half the screen. Wine's Wayland driver works (2.3b ✅); the launcher (pi-kognog-azerothcore) only picks it on Hyprland
- [x] Windows look (D-46): border only (2 px, palette white active / dark grey inactive), tabs when windows share a space, 10 px gaps — Javier: "Border only + tabs works wonders"
- [x] **Applet 1 · Workspaces Management** (D-47): `applets/workspaces/` — settings file `~/.config/hypeforge/applets/workspaces.toml` (enabled, screens, names) + routine `hypeforge-workspaces`; 6 workspaces across all 3 screens (1 Daily · 2 Work · 3 Entertainment · 4 Gaming · 5 Monitoring · 6 Settings), Win + 1…6 / Win + Shift + 1…6. **10-04: built and tested — Javier: "the mouse stays put now, everything works" (D-48).** Later: add/edit/delete workspaces from hypeForge Settings
- [x] **Top bar = Waybar** 0.15.0 (nog, `extra`): all workspaces always shown as "1. Daily"…, clickable, active one coloured; the applet writes its workspace list (`workspaces.waybar.json`). Waybar started by `exec` (Sway's `swaybar_command` did not start it on reload); `mouse_warping none` so a bar click leaves the pointer where it is
- [x] `CLAUDE.md`, the README (text + badges), GitHub description + topics brought to the Sway path (10-05, D-59); the banner + images: step 2 of the public update
- [x] **Launcher = fuzzel** (D-51) on Win + Space, apps only, terminal apps in Alacritty; sway-launcher-desktop tried and removed — Javier: "Works very well"
- [x] **Applet 4 · App Sections** (D-52): `applets/sections/` on Win + Space — first screen = the workspaces + All apps + Lock Screen · Log Out · Reboot · Shutdown (asks first); a section pick opens the app in that workspace — Javier: "Looking great so far!"
- [x] Favourites (Javier, 10-05): 18 apps in his order in `~/.config/hypeforge/applets/sections.toml`, all 18 found by the launcher; new entries `applications/mc.desktop` (Midnight Commander) + `claude-terminal.desktop` (Claude Code in Alacritty); "hypeForge Settings" added when hypeForge Settings exists. Javier: "Yes, perfect!"
- [x] Lock screen (D-57): **gtklock + swayidle**: swaylock tried first (its ring was not wanted), then gtklock (password box with dots, big clock; 100 KiB, GTK3 already here), background = the wallpaper blurred once (`assets/lock/`); Win + Escape and Lock Screen in Win + Space lock; locks after 30 min, screens off after 60, no sleep (Javier); KognogOS wallpaper; Javier wanted a password box, not the ring → **gtklock** (100 KiB, GTK3 already here) (`sway/swaylock/config`). Javier: "it is perfect my friend". Then remove hyprlock + swaylock (nog)
- [x] Replace the KDE apps (D-57): calculator: numbat tried (Javier: "numbat is weird" — he wants one that looks like a calculator; no terminal keypad calculator is in the repos) → **galculator** for now (GTK3, 1.3 MB, floats), numbat removed; our own Forge calculator on the roadmap; **cliamp** (Winamp-style) in Elisa's, with the playlist "Music (tphome00)" → `/mnt/tphome00/media2/music` (1,209 songs, read-only) — Javier: "It works well". Own entries `applications/cliamp.desktop`
- [ ] **Public update (D-59, order agreed):** (1) GitHub description + topics + README text and badges for the Sway path → shown to Javier; (2) new banner + images, designed and approved first; (3) kognogos.org hypeForge section + "In the pipeline" with the upcoming Forge apps, shown before it goes live
- [x] **Applet 1, matrix** (D-49): a screen can share one space between workspaces (`[share]` in `workspaces.toml`; all own for now); bar buttons drawn by the applet; windows follow when the grid changes — Javier: "everything works, the highlight follows on all three"
- [x] **Applet 2 · Window Placement** (D-50): `applets/placement/` — fill order 1 middle → 2 beside → 3 left → 4 beside → 5 right → 6 beside → 7 under 4 → 8 under 6, in every workspace, counting a shared screen too; 9+ go round again as tabs — Javier: "all works perfect!"
- [x] **Notifications** (Javier 10-05): **mako** (0.14 MB, nog) — top right under the bar, screen in use, 5 s, urgent ones stay; Mocha; click closes, right click closes all; Win + N closes all, Win + Shift + N brings back the last (`sway/mako/config`) — Javier: "that worked"
- [x] **Applet 7 · the bell** (`applets/notifications/`): a bell next to the clock — grey, or yellow and ringing with the count of unseen; left click lists recent notifications (fuzzel) and marks them seen; right click = Do Not Disturb (red, pop-ups hidden, still kept); redrawn by mako's on-notify through the F-45-safe signal (now shared: `applets/common/hfbar.py`) — Javier: "it showed the 3 notifications… now there is one"
- [ ] **F-46 (#28) the launcher closed by itself**: Sway's focus-follows-mouse + fuzzel closing on focus loss → `exit-on-keyboard-focus-loss=no` (every pop-up list); tested both ways. Javier: "the launcher stays open now" — close #28 with the next commit
- [ ] **Fonts on the KognogOS disc** (Javier, 10-05, "very important"): `docs/FONTS.md` lists every font hypeForge needs. **Missing on the disc: `ttf-nerd-fonts-symbols`** (the bar's icons) → add to KognogOS `iso/packages.x86_64` (KognogOS has no TODO.md yet — gap)
- [x] **Screenshots** (Javier 10-05): grim + slurp + **applet 8** (`applets/screenshot/`): Print = drag a box, Shift = this screen, Ctrl = all screens, Alt = this window; saved to ~/Pictures/Screenshots, copied, a notification — click it → **swappy** (0.12 MB; satty removed: GTK4 + GNOME's libadwaita). Javier: "Works great"
- [ ] **The bar, redesigned (Javier, 10-05)** — design first, approved, then built one piece at a time:
  - [x] **1 · Launcher button** (10-05): the KognogOS emblem at the left (`custom/launcher`, the picture drawn by style.css from `~/.config/hypeforge/bar/launcher.png` — swap the file to change it). **Waybar 0.15's image module stops the bar from appearing** on this setup (tested with the real bar stopped: 0 of 3 bars, any picture), so the emblem is a CSS background. A second press (button or Win + Space) closes the open launcher. Workspace buttons are now `group/workspaces`, placed by the bar's own settings. Javier: "Button looks amazing… worked as expected"
  - [x] **2 · Workspace dropdown** (10-05): one button "1. Daily ▾" (`custom/ws`, applet 1 writes it); click or **Win + Tab** → the list under the button (fuzzel, current one selected), pick one = every screen switches. **Shared pop-up helper** `applets/common/hfmenu.py`: one list at a time, a second press closes it (launcher, dropdown, bell, clipboard). Help updated: new **Tools** tab, Start / Workspaces / Apps pages. Javier: "works wonders!!!! it is perfect!"
  - [ ] **3 · Favorites ▾** (10-05): first built as a row of 18 icons (Javier: "look good"), then folded into one **dropdown button** at his request — the list shows each app with its icon, under the button; a second click closes it. `hypeforge-sections bar` writes it (runs at login), `hypeforge-sections favorites` opens the list. US spelling "Favorites" on screen (Javier). **Waiting: Javier's test**
  - [ ] **The left side a shade lighter** with a rounded end (Javier: "a visual distinction" between left and right). **Waiting: Javier's look**
  - [ ] **The tray** (Javier, 10-05) left of the clipboard: Steam, Insync, Dropbox showed at once; Discord needs one restart (it started before the tray existed). Clipboard and bell icons at 17 px to match the tray's 16 px icons (Javier: "they don't look aligned"). **Waiting: Javier's test**
  - [ ] **Applet 10 · Start-at-login apps** (`applets/autostart/`): Sway does not read `~/.config/autostart/`, so Dropbox and Insync never started — the applet starts that folder's apps at login (only the user's folder, not the system one full of KDE items; skips hidden / other-desktop / running). Help page on the Tools tab. **Waiting: Javier's next login**
  - **Direction (Javier, 10-05):** the bar becomes a menu bar, almost like Apple's — dropdowns (workspaces, Favorites…), later a new launcher idea and **hypeForge Settings** as a menu
  - **Open apps as icons** (Waybar's taskbar: click to focus, middle click to close) — test 10-05: the taskbar found the open windows (log), not yet seen on screen
  - [x] **Built first (Javier's order): the clipboard** — **applet 9** (`applets/clipboard/`) + cliphist (2.3 MB, nog, last 200 copies): an icon left of the bell, blue with the count of new copies (seen mark in ~/.local/state, survives restarts), redrawn at every copy (Sway's watchers run `hypeforge-clipboard store`); left click / **Win + C** = the history (text copied again, a picture opens in swappy), right click = empty it (asks). Secret copies (CLIPBOARD_STATE=sensitive) tested twice: not kept. Icons 5 px apart. Javier: "tested! works well"
  - [ ] The clipboard and notification lists (fuzzel pop-ups) need their own look later (Javier) → Theme manager / the Forge apps
  - [ ] **Where the pop-up lists open** (Javier, 10-05): the launcher, the clipboard list and the notification list each need a **position option** (centre, under their bar button, a corner…) → a setting in the Launcher, clipboard and Notifications Forge apps (fuzzel can be anchored and offset per list)
- [ ] Later (Javier, 10-04, "for when we get there"): **Alt + Tab** across the apps of the workspace on all 3 screens, with window pictures (applet candidate)
- [ ] Later (Javier, 10-04): **drag and drop** of windows — explore: swapping apps, dropping one onto another to tab/stack
- [x] **Applet 5 · Window Rules** (D-53): small tools float (`applets/rules/`); Alt + F4 closes; the launcher's first screen searches every app — Javier: "everything is working. Excellent!"
- [x] **F-45 (#27): no top bar after login** (found 10-05) — the Workspaces applet's first "redraw" signal reached Waybar before it was listening, which ends the program. Fixed: signal only once the bar listens (`SigCgt`), wait up to 5 s; tested 0/5 → 5/5; Javier logged out and in: the bar appeared ✅
- [ ] F-44 (#26) — waits for our own password helper (D-56; no KDE, nothing installed meanwhile): no admin-password helper (polkit agent) runs in the Sway session — apps that ask for admin rights through a pop-up cannot 
- [x] **Applet 6 · Help** (D-54): Win + F1 + Help & Keys in the launcher → key chart + guide pages in one floating viewer (border, "q to close" line); one source (`applets/help/`) for Win + F1 and hypeForge Settings; the chart checked against Sway's keys before every commit
- [x] **Help & Keys as a forgekit app** (D-55): tabs Keys · Start · Workspaces · Windows · Apps · About · Quit, the same look on every page, wrapping tables with alternating rows — Javier: "Everything works! Great job."
- [ ] forgekit (its own repo): the menu bar does not wrap and is cut off on a narrow window — affects every Forge app (found 10-05)
- [x] Wallpaper : the KognogOS Semi Mocha wallpaper on all three screens, via swaybg (D-54)
- [x] **KognogOS Mocha skin for Midnight Commander** (Javier, 10-05): `themes/mc/kognogos-mocha.ini` — full colour (Catppuccin Mocha + the emblem's blue/peach, mauve accents, rounded corners), tested in a hidden terminal and a real Alacritty window (`themes/mc/preview.png`). **The default now** (`skin=kognogos-mocha` in `~/.config/mc/ini`); Help: a Midnight Commander page on the Tools tab. Later: the Theme manager switches it
- [ ] Apps that draw their own minimise/maximise/close bar (Chrome…): switch it off where the app allows
- [ ] Try SwayFX for rounded corners (`chaotic-aur/swayfx` 0.6, same config) — later, separate trial
- [ ] The remaining jobs, one at a time with Javier (sound, network, Bluetooth, files, monitors, USB, printing…): a terminal (CLI/TUI) app first wherever one exists
- [ ] **Forge Suite roadmap (D-59)** — every configurable thing becomes its own Forge app, held by hypeForge Settings (names: Javier's call):
  - Our applets as apps: Workspaces · Monitors · Window placement / snap · Launcher (App Sections) · Window Rules · Help & Keys · Idle · Lock screen
  - Outside programs set up only by a config file: cliamp (music folders, providers… **needs a long conversation first**; found 10-05: started bare it opens on its radio list and no key reaches the local playlists until a track has played — the launcher now starts it with `--playlist "Music (tphome00)"`; a setting for the start playlist; the radio as an option, not the default); Javier's way in: **Tab → Source → Local** shows the tracks. **Open questions (Javier, 10-05):** create playlists, collections, lists per artist and per disc — cliamp has playlists (a), folder sources (live), sort by artist / album / artist+album, filter (/), favourites (n); automatic per-artist / per-album lists from the server's "Artist - Album" folders would be the Forge app's job · Waybar · fuzzel · gtklock · Alacritty (= alacrittyForge ✅) · GRUB (= grubForge ✅)
  - **Notifications** (Javier, 10-05, "another project"): mako's whole settings file in a Forge app — colours, font, size, corners, borders, icons, corner and screen, timing, mouse buttons, Do Not Disturb, history, rules per app or urgency (`~/.config/mako/config`)
  - **Default apps** (Javier, 10-05): which app opens what — browser, files, text, pictures, music, video…
  - **Startup apps** (Javier, 10-05): the start-at-login list — takes over applet 10
  - **Theme manager** (Javier, 10-05): the look of everything in one Forge app — GTK windows (swappy, galculator, gtklock: today they get KDE's Breeze theme from `~/.config/gtk-3.0/settings.ini` → adw-gtk3-dark + our colours), icons, mouse pointer, fonts, the KognogOS palette
  - **Calculator** (Javier, 10-05): a keypad in our look, mouse + keyboard, a strong engine underneath (numbat / qalc); replaces the stopgap galculator. A good early candidate for the app-inside-hypeForge-Settings spike
  - **Password helper** (D-56): the admin pop-up (polkit) + the `sudo`/`nog` password window; closes F-44 (#26) + F-42 (#24)
  - First: a spike — a full Forge app inside forgekit's terminal pane (colours, mouse, keys)
  - **Any number of screens** (Javier, 10-05): "not everyone has 3 screens… 1, and others 6" — a flexible matrix of monitors × workspaces × window placement, designed when the Monitors / Workspaces / Placement apps are built (today's settings assume this desktop's three)
- [ ] **hypeForge Settings = the control centre** (D-59): list on the left, the chosen Forge app running in a terminal pane on the right

## Phase 12 · Our own look
- [ ] **Applet 3 · Folder tabs** (D-47): small left-aligned tabs like folders in a holder, rounded tops, our colours; replaces Sway's even tab row
- [ ] **Our own bar** (Javier, 10-04): Waybar for now; once the setup is done, our own bar as a hypeForge applet — a Waybar fork or a small one of our own, decided then
- [ ] **hypeForge Settings** (D-47): every applet switched on/off, its behaviour and look changed in one place
  - Launcher / App Sections in hypeForge Settings (Javier, 10-04): modify its look · tie its colours to the active theme · add, edit, remove sections · add apps to sections · pin favourites · switch its other options on and off
  - Workspaces in hypeForge Settings: add, edit, delete workspaces; the sharing grid as switches
  - Help in hypeForge Settings: the same key chart and guide pages as Win + F1 (`applets/help/`)
  - Lock screen in hypeForge Settings (Javier, 10-05): gtklock's look — background (and its blur strength / darkness), clock and date format, password box, colours (`sway/gtklock/`)
  - Idle and lock in hypeForge Settings (Javier, 10-05): minutes until the screen locks (30 now), minutes until the screens turn off (60 now), the lock key (Win + Escape)
- [ ] From the KognogOS brand (logo, colours): a palette with contrast between elements on purpose — connected, not fused, not monotone
- [ ] Each visual step designed and approved before it is built (bar, borders, launcher, notifications, lock screen, terminal, wallpaper…)

## Phase 13 · Forge apps for the gaps
- [ ] New Forge Suite apps for the jobs with no terminal app (one at a time, each its own project)

## Phase 14 · Our own terminal apps for the rest
- [ ] Once everything is set up: our own TUI versions of the apps we use that are not Forge Suite (fork the one we use, or write one from zero)

---

## Open questions
- [ ] The test desktop runs nog's stock tier list, not KognogOS's. Is that on purpose? (found 2026-09-28)
