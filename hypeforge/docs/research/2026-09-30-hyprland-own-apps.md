# Research notes — 2026-09-30, Hyprland's own apps for each desktop job

*The question from Javier: "let's use as many of available apps first from hyprland this time." So for every desktop job, this note asks: does the Hyprland team (the `hyprwm` group on GitHub, also called the "hypr ecosystem") make an app for it? If not, what do most Hyprland users pick instead? Terminal apps are ruled out for settings. Graphical apps are wanted, ideally panels that drop down under the top bar.*

*Nothing was installed. Every package fact comes from `pacman -Si` (reading only) or the AUR's lookup service. Every feature claim comes from the app's own source code or the Hyprland wiki. Where something could not be checked without installing, it says* **unproven**.

---

## The short answer

The Hyprland team makes graphical apps for **four** of the nine jobs: the app launcher, sound, system info and logging out. It makes **no** top bar, **no** notification service, **no** network app, **no** Bluetooth app and **no** screen-settings app. Hyprland's own starter settings file points at community apps for those: Waybar for the bar and `nm-applet` for the network.

The best news: **every Hyprland-made app takes its colours and fonts from one small settings file**, `~/.config/hypr/hyprtoolkit.conf`. hypeForge can write that one file and the launcher, the sound app, the system-info app, the logout screen and the password pop-up all match at once.

The honest catch: these apps are young (versions 0.1 to 0.2). Two of them miss something Javier asked for. **hyprlauncher has no categories.** **hyprpwcenter has no clear "use this speaker" switch** in its code.

## Summary table

| Job | Hyprland's own app | Runner-up community app | Package (repo) | Ready for our ISO? |
|---|---|---|---|---|
| 1. Top bar | **none** | **Waybar** (also: nwg-panel, ashell) | `waybar` 0.15.0 (extra); `waybar-git` (chaotic-aur) | **Yes, with `waybar-git`.** The released 0.15.0 cannot switch workspaces by click under the Lua settings (already known, D-17). Taskbar and tray: yes. Real drop-down panels: no, it opens apps instead. |
| 2. App launcher | **hyprlauncher** | nwg-drawer (has categories) | `hyprlauncher` 0.1.6 (extra); `nwg-drawer` 0.7.5 (extra) | **hyprlauncher: yes, but no categories.** If categories are a must, nwg-drawer is the only official-repo launcher that has them. |
| 3. Sound | **hyprpwcenter** | pavucontrol | `hyprpwcenter` 0.1.2 (extra); `pavucontrol` 6.2 (extra) | **Yes for volumes.** Choosing the default speaker or microphone is **not found** in its code (unproven, needs a test). pavucontrol does it for sure. |
| 4. Network | **none** | nm-applet + nm-connection-editor | `network-manager-applet` 1.36.0 (extra) | **Yes.** Its tray icon gives a real drop-down list of Wi-Fi networks right under the bar. |
| 5. Bluetooth | **none** | Blueman | `blueman` 2.4.6 (extra) | **Yes.** Tray icon plus a manager window. Overskride looks more modern but is AUR-only. |
| 6. Screens | **none** | wdisplays | `wdisplays` 1.1.3 (extra) | **Only as a preview tool.** It changes screens live but does not save them. hypeForge already writes the monitor rules itself (job 19). |
| 7. System info and utilities | **hyprsysteminfo**, **hyprshutdown**, **hyprland-guiutils** | — | `hyprsysteminfo` 0.2.0 (**AUR only**); `hyprshutdown` 0.1.1 (extra); `hyprland-guiutils` 0.2.2 (extra, pulled in by Hyprland itself) | **hyprshutdown and guiutils: yes. hyprsysteminfo: no** — AUR only, so it breaks "official repos first". |
| 8. Notifications | **none** (Hyprland's built-in pop-ups are "not meant to handle your system notifications") | mako (our pick) | `mako` 1.11.0 (extra) | **Yes, keep mako** (D-19). |
| 9. Other | hyprpolkitagent, hyprlock, hypridle, hyprpaper, hyprsunset, hyprpicker (already used); hyprqt6engine, hyprland-qt-support | — | hyprqt6engine is **AUR only** | Already covered. The one extra worth a look is **hyprqt6engine**, a colour theme for Qt apps; AUR only. |

"Ready for our ISO" means: in an official Arch repository (or chaotic-aur, which KognogOS already uses), works with Hyprland 0.56's Lua settings, and can be themed from a file hypeForge writes.

---

## What the Hyprland team makes (the full list)

The `hyprwm` group on GitHub has 44 projects. Most are building blocks for programmers. The ones a person actually sees on screen are:

| App | What it is | Arch package | Last change on GitHub |
|---|---|---|---|
| hyprlauncher | app launcher and picker | extra 0.1.6 | 2026-09-09 |
| hyprpwcenter | sound control centre | extra 0.1.2 | 2026-09-30 |
| hyprsysteminfo | system information window | AUR 0.2.0 | 2026-08-11 |
| hyprshutdown | graceful logout screen | extra 0.1.1 | 2026-08-11 |
| hyprland-guiutils | five small helper windows (below) | extra 0.2.2 | 2026-08-11 |
| hyprpolkitagent | the admin-password pop-up | extra 0.2.0 | 2026-09-09 |
| hyprlock, hypridle, hyprpaper, hyprsunset, hyprpicker | lock screen, idle timer, wallpaper, night light, colour picker | extra | Aug–Sep 2026 |
| hyprqt6engine | colour theme for Qt apps | AUR 0.1.0 | 2026-08-11 |
| hyprland-qt-support | style for older Hyprland Qt apps | extra 0.1.0 | 2026-06-28 |

Two older apps are **retired** ("archived" on GitHub, meaning frozen and read-only): `hyprland-qtutils` and the stand-alone `hyprland-welcome`. Both were folded into `hyprland-guiutils`.

**There is no Hyprland-made bar, notification service, network app, Bluetooth app, screen-settings app or settings centre.** This was checked against the whole list, not guessed.

### One file themes all of them

Most new Hyprland apps are built on **hyprtoolkit**, the team's own toolkit for drawing windows (a "toolkit" is the kit of buttons, sliders and text boxes an app is made from). hyprtoolkit reads one file: `~/.config/hypr/hyprtoolkit.conf`.

It holds: `background`, `base`, `alternate_base`, `text`, `bright_text`, `link_text`, `accent`, `accent_secondary`, font sizes (`h1_size`, `h2_size`, `h3_size`, `font_size`, `small_font_size`), `font_family`, `font_family_monospace`, `icon_theme`, `rounding_large` and `rounding_small`. The list was read from the toolkit's source code and matches the wiki.

This file uses the old, simple `name = value` style, not Lua. The move to Lua only affects Hyprland's own settings file, so this is fine.

**What it means for us:** hypeForge writes one small file with the Catppuccin colours, and hyprlauncher, hyprpwcenter, hyprsysteminfo, hyprshutdown, the guiutils windows and hyprpolkitagent all match. That is less work than theming any community app.

---

## 1. Top bar

**Hyprland's own app: none.** The Hyprland team has never made a bar. Its own welcome app says: *"For new users we recommend waybar, for advanced users quickshell."* Its starter settings file also mentions `waybar`.

### Waybar (the most used)
- **What it does:** the strip across the top with workspaces, clock, tray and status icons.
- **Official Hyprland?** No. Community, 12,000 GitHub stars, last change 2026-09-24.
- **Package:** `extra/waybar 0.15.0-3`. Also `chaotic-aur/waybar-git 0.15.0.r822`.
- **Lua settings (0.56):** Waybar talks to Hyprland through its message line (IPC, a local channel apps use to ask Hyprland things), not through the settings file. So Lua does not matter for most of it. **One known problem:** in 0.15.0, clicking a workspace number does nothing on Hyprland 0.55 and newer ([#5029](https://github.com/Alexays/Waybar/issues/5029), [#5294](https://github.com/Alexays/Waybar/issues/5294)). It is fixed in the development version only. Arch's `waybar 0.15.0-3` carries **no patch** for it (checked: the Arch package file downloads the plain 0.15.0 source). D-17 already handles this with `waybar-git`.
- **Open-app icons (taskbar):** yes, the `wlr/taskbar` section. Click an icon to bring that window forward.
- **System tray:** yes (`tray` section).
- **Drop-downs for sound, network, Bluetooth:** **not real panels.** Waybar shows status icons. A click can run a command (for example, open hyprpwcenter), or show a simple text menu. It cannot draw a slider panel of its own. The drop-down feel has to come from the app it opens, placed under the bar with a Hyprland window rule. **Unproven** until tried.
- **Theming:** a CSS file (the same style language web pages use) — colours, fonts, spacing. Easy to generate. A Catppuccin port exists.

### nwg-panel (runner-up with real drop-downs)
- **What it does:** a full panel with a taskbar, a tray, and a **"Controls" drop-down** with a volume slider (and per-app sliders), brightness, battery and a power menu.
- **Package:** `extra/nwg-panel 0.12.0-1`, released 2026-09-29.
- **Lua settings:** broke once in Hyprland 0.55 ("running commands through compositor"), fixed ([#426](https://github.com/nwg-piotr/nwg-panel/issues/426)). One open bug: its Hyprland watcher can die if Hyprland is not ready at start ([#436](https://github.com/nwg-piotr/nwg-panel/issues/436)).
- **Theming:** CSS file. Settings are made in its own graphical settings window or a JSON file.
- **Catch:** same maker as nwg-displays, which Javier rejected. It is closer to "a panel under the bar" than Waybar, though.

### Others worth knowing
- **ashell** (AUR, 0.10.0, active): a ready-made bar with a real settings drop-down (sound in and out, Wi-Fi with password entry, Bluetooth, VPN, power menu) and its own notifications. **No taskbar** of open apps. AUR only.
- **HyprPanel:** **retired.** Its GitHub project was frozen in April 2026. Its maker moved to a new bar called **Wayle** (AUR, 0.7.0, young). Do not use HyprPanel.
- **Full "desktop shells"**: DankMaterialShell (`extra/dms-shell-hyprland 1.6.2`) and Noctalia (AUR `noctalia-git`). They replace the bar, launcher, notifications and settings panels with one program. They do everything Javier asked for, but they replace most of the Hyprland apps in this note, which goes against "Hyprland's own apps first".

**Recommendation:** keep Waybar (via `waybar-git` until a release after 0.15.0 reaches `extra`). Make its sound, network and Bluetooth icons open the apps below as floating windows placed under the bar. If that does not feel like a drop-down, nwg-panel is the fallback with real ones.

---

## 2. App launcher / app menu

**Hyprland's own app: hyprlauncher.** Hyprland's starter settings file uses it: `local menu = "hyprlauncher"`. If it is missing, Hyprland falls back to `hyprland-run` (a tiny "type a command" box from guiutils).

- **What it does:** a search box. Type a few letters, pick an app. It can also do sums (`=`), emoji and symbols (`.`), and fonts (`'`).
- **Official:** yes. 358 stars, last change 2026-09-09.
- **Package:** `extra/hyprlauncher 0.1.6-9`.
- **Categories: no.** The app-finding code reads each app's name, command and icon. It never reads the `Categories=` line that app files carry. There is no category view. The list is a flat, searchable list that puts often-used apps first. (Checked in the source code: no mention of categories anywhere.)
- **Lua settings:** its own settings file is separate (`~/.config/hypr/hyprlauncher.conf`), so Lua does not affect it. Hyprland's own 0.56 starter file uses it, so it is the tested path.
- **How it opens:** it stays running in the background ("daemon") so it opens instantly. Start it once with `hyprlauncher -d`, then bind a key to `hyprlauncher` (or `hyprlauncher -t` to open and close with the same key). It appears as a box in the middle of the screen, 400 × 260 by default (`ui:window_size`).
- **Useful settings:** `finders:desktop_launch_prefix = uwsm app --` so apps start the uwsm way (uwsm is the session starter we use); `finders:desktop_terminal` for terminal apps; `general:show_apps_on_open` to show the list before typing.
- **Theming:** from `hyprtoolkit.conf` (see above).
- **Known problems (open on GitHub):** it can launch the chosen app again and again after closing (reported 2026-09-25); apps that need a terminal do not start (2026-06-18); a crash on VMware graphics (2026-05-19, matters only for VMware test machines).

### Runner-up with categories: nwg-drawer
- **What it does:** a full-screen grid of app icons, **with a row of category buttons** (Office, Internet, Games…) to filter.
- **Package:** `extra/nwg-drawer 0.7.5-1`, last release 2026-03-24.
- **How it opens:** `nwg-drawer`, or run it once in the background and open it with `nwg-drawer -open`.
- **Theming:** CSS file `~/.config/nwg-drawer/drawer.css`.
- Same maker as nwg-panel and nwg-displays.

Other common launchers (rofi, fuzzel, wofi, walker) are search boxes without category views.

**Recommendation:** hyprlauncher for the everyday "type and go" launcher, because it is Hyprland's own and themes for free. **If a menu with categories is a must, Javier has to choose:** add nwg-drawer next to it (for example, on the bar's app-menu button), or accept no categories.

---

## 3. Sound

**Hyprland's own app: hyprpwcenter.** (PipeWire is the sound system on modern Linux; "pw" in the name stands for it.)

- **What it does:** a window with five tabs: **Apps** (volume per app), **Nodes** (volume per speaker and output), **Inputs** (volume per microphone), **Configuration** (switch a sound card's mode, called a "profile", for example HDMI versus headphones) and **Graph** (a wiring diagram of what plays where).
- **Official:** yes. 150 stars, last change today (2026-09-30).
- **Package:** `extra/hyprpwcenter 0.1.2-9`.
- **Pick the default output or input:** **not found.** The code sets volume, mute and card profiles. It never sets PipeWire's "default device" setting. You may be able to move one app's sound by rewiring it in the Graph tab, but "make these headphones the default" does not appear to exist. **Unproven — needs a test on the real machine.**
- **Lua settings:** not affected; it talks to PipeWire, not to Hyprland.
- **How it opens:** `hyprpwcenter`. It is a normal window, so it would need a Hyprland rule to float it under the bar.
- **Theming:** from `hyprtoolkit.conf`.
- **Known problems:** a crash when closing ([open](https://github.com/hyprwm/hyprpwcenter/issues)); "app does not boot" (open, 2026-04); volume curve handling (open). No setting to pick which tab it opens on.

### Runner-up: pavucontrol
- `extra/pavucontrol 6.2`. The long-standing sound mixer. Sets the default speaker and microphone for sure, and moves single apps between devices. GTK 4, so it follows the GTK theme rather than our file.

**Recommendation:** hyprpwcenter first. Test on the real desktop whether it can switch the default speaker. If it cannot, keep pavucontrol installed for that one job.

---

## 4. Network (Wi-Fi and cable)

**Hyprland's own app: none.** Hyprland's starter file lists `nm-applet` in its example start-up lines.

### nm-applet (from network-manager-applet)
- **What it does:** a network icon in the bar's tray. **Clicking it opens a real drop-down list of Wi-Fi networks right under the bar**, plus on/off switches and VPN. "Edit Connections" opens `nm-connection-editor` for the detailed settings.
- **Package:** `extra/network-manager-applet 1.36.0-2` (brings `nm-connection-editor`).
- **Fits this machine:** NetworkManager (the service that manages connections) is running on the desktop (`systemctl is-active NetworkManager` → active; `iwd` is inactive).
- **How it opens:** start `nm-applet --indicator` at login; it lives in the tray.
- **Lua settings:** not affected.
- **Theming:** follows the GTK 3 theme, not a file of ours alone. It can be made to match with a Catppuccin GTK theme.

Other options named by the Hyprland wiki: **iwgtk** (AUR, for `iwd` only, not used here, last change 2025-07).

**Recommendation:** nm-applet. It is the closest match to "a drop-down under the bar" of anything in this note, and it is in the official repos.

---

## 5. Bluetooth

**Hyprland's own app: none.**

### Blueman
- **What it does:** a tray icon (`blueman-applet`) with a quick menu of devices, plus a manager window (`blueman-manager`) to pair and connect.
- **Package:** `extra/blueman 2.4.6-2`, last change on GitHub 2026-08-03.
- **Lua settings:** not affected.
- **Theming:** follows the GTK 3 theme.

### Overskride (modern-looking runner-up)
- GTK 4 app, clean look. **AUR only** (`overskride` / `overskride-bin` 0.6.6). Last change 2026-09-01.

Blueberry (Linux Mint's app) is AUR only and quiet since 2024-04.

**Recommendation:** Blueman. It is in the official repos and its tray icon gives a quick drop-down.

---

## 6. Screens (monitor settings)

**Hyprland's own app: none.** (nwg-displays was already rejected.)

### wdisplays
- **What it does:** a window with the screens drawn as boxes. Drag them, change resolution and refresh rate, and it applies live.
- **Package:** `extra/wdisplays 1.1.3-2`. Last change 2026-09-28.
- **Big limit:** it **does not save** anything. Changes vanish at the next login. Hyprland supports the standard it uses (wlr-output-management), but Hyprland's own settings file still wins at restart. **Unproven on 0.56.**
- **Theming:** GTK 3 theme.

Also known: `hyprmon` (AUR) is a terminal app, so it is ruled out. The full desktop shells (DankMaterialShell) have a screen page that writes Lua; not worth taking a whole shell for this.

**Recommendation:** there is no good graphical tool. hypeForge's plan to write the three monitor rules itself (job 19) is still the right one. wdisplays could be offered as "try a layout live", with hypeForge then saving the result. That saving step would be ours to build.

---

## 7. System info and other Hyprland utilities

### hyprsysteminfo
- **What it does:** a small window showing the system (CPU, graphics card, memory, Hyprland version) with buttons to copy it. The Arch logo shows if `/etc/os-release` has a `LOGO=` line; a KognogOS logo would need that line.
- **Official:** yes. Now built on hyprtoolkit, so themed by our file. (The AUR description still says "qt6/qml", which is out of date.)
- **Package:** **AUR only** (`hyprsysteminfo 0.2.0`, 8 votes). Not in `extra` or chaotic-aur.
- **How it opens:** `hyprsysteminfo`.

### hyprshutdown
- **What it does:** a logout screen that politely asks every app to close first, so nothing loses work, then leaves Hyprland. It does **not** power the computer off on its own. For that: `hyprshutdown -t 'Shutting down...' --post-cmd 'shutdown -P 0'` or `--post-cmd 'reboot'`.
- **Official:** yes. Hyprland's 0.56 starter file binds it to SUPER + M, and the `hyprland` package lists it as optional.
- **Package:** `extra/hyprshutdown 0.1.1-8`.
- **Theming:** hyprtoolkit file.
- **Known problems, important for this desktop:** on **NVIDIA + SDDM** (our test desktop), logging out can hang on a black screen. The wiki fix is `hyprshutdown --vt 2`, which needs a sudo rule for `chvt` (a tool that switches screens). Also open: very large button text (2026-09-27), and Firefox not restoring all windows.

### hyprland-guiutils (five helper windows)
Already installed with Hyprland (the `hyprland` package depends on it). It contains:

| Program | What it is | Who starts it |
|---|---|---|
| `hyprland-dialog` | general pop-up boxes, including "this app is not responding" | Hyprland itself |
| `hyprland-welcome` | first-start tour | Hyprland, **only** when it made the settings file itself (`autogenerated`) |
| `hyprland-update-screen` | "Hyprland was updated" news | Hyprland, after an update |
| `hyprland-donate-screen` | donation request, about twice a year | Hyprland |
| `hyprland-run` | tiny "run a command" box | fallback launcher |

- **Theming:** hyprtoolkit file.
- **For our ISO:** the welcome tour talks about kitty, dolphin and editing `hyprland.lua` by hand, which does not fit KognogOS. It will not appear, because hypeForge writes the settings file (so it is not "autogenerated"). The update and donation pop-ups can be turned off with `ecosystem:no_update_news` and `ecosystem:no_donation_nag`. **That is Javier's call.** Turning off the donation request is a question of courtesy to the Hyprland team, not only a technical one.

### hyprtoolkit
The toolkit under all of these (`extra/hyprtoolkit 0.6.0`). Not an app. Worth knowing its open bugs: apps built on it can crash at logout when Hyprland goes away (hyprpaper, hyprpolkitagent; 2026-09-16), and icons from some theme folders are missed (Chromium web-app icons invisible; 2026-08-18).

---

## 8. Notifications

**Hyprland's own app: none.** Hyprland has built-in pop-ups (`hyprctl notify`), but its own wiki says: *"They are not meant to handle your system notifications."* The Hyprland welcome app lists **dunst** and **mako** as the choices.

**Recommendation:** keep **mako** (D-19; `extra/mako 1.11.0`). Nothing from Hyprland replaces it. (`hyprnotify` in the AUR is a third-party bridge, unmaintained since 2024-09.)

---

## 9. Anything else Hyprland makes

Already in use: hyprpolkitagent, hyprlock, hypridle, hyprpaper, hyprsunset, hyprpicker. Beyond those:

- **hyprqt6engine** — colours and fonts for Qt apps (KDE-style apps), a replacement for `qt6ct`. Set `QT_QPA_PLATFORMTHEME=hyprqt6engine`; settings in `~/.config/hypr/hyprqt6engine.conf`. **AUR only** (`hyprqt6engine 0.1.0`, 14 votes). Worth it only if Qt apps look out of place.
- **hyprland-qt-support** — a style for older Hyprland Qt apps; `extra`. Nothing we use needs it now that hyprpolkitagent moved to hyprtoolkit (the `pacman -Si` description still says "QT/QML", but GitHub says hyprtoolkit).
- **xdg-desktop-portal-hyprland** — screen sharing and file pickers; needed, `extra`.
- **hyprshot** is in `extra` but is **not** from the Hyprland team (a community screenshot script with a similar name).
- **No settings centre and no welcome app for end users** exist from Hyprland. A "settings" hub for KognogOS would be ours to build, most likely as launcher entries that open the apps above.

---

## A side note found while reading

`docs/DECISIONS.md` seems to say two different things about a taskbar: one entry says *"No list of open apps in the top bar"* (line 59), another says *"Open apps show in a taskbar inside the top bar"* (line 78). One is probably the newer decision. Flagged for Javier, not changed.

---

## Commands run (all read-only)

- `pacman -Sl extra | grep -i hypr` and `pacman -Ss hypr` — what Hyprland packages exist.
- `pacman -Si` for hyprlauncher, hyprpwcenter, hyprland-guiutils, hyprshutdown, hyprtoolkit, hyprpolkitagent, hyprland-qt-support, hyprland, waybar, nwg-panel, nwg-drawer, nwg-displays, mako, swaync, dunst, blueman, network-manager-applet, nm-connection-editor, pavucontrol, wiremix, rofi, fuzzel, wofi, wdisplays, kanshi, nwg-look, swayosd, quickshell, dms-shell, dms-shell-hyprland, bluetui, impala, iwd, networkmanager.
- AUR lookups (`curl 'https://aur.archlinux.org/rpc/v5/info?...'`) for hyprsysteminfo, hyprland-qtutils, hyprpanel, ags-hyprpanel-git, hyprmon, walker, overskride, blueberry, iwgtk, hyprnotify, ashell, wayle, noctalia, hyprqt6engine, quickshell-git, caelestia-shell. Plus the AUR build file for hyprsysteminfo.
- `gh api orgs/hyprwm/repos` — the whole list of Hyprland projects, with last-change dates and retired status.
- `gh api repos/<owner>/<repo>` for star counts and last-change dates; `gh issue list` and `gh search issues` for known problems; `gh release list` for release dates.
- `git clone --depth 1` of hyprlauncher, hyprpwcenter, hyprtoolkit, hyprsysteminfo and Hyprland into a scratch folder, then `grep` for categories, default-device code, settings names, and what starts the guiutils windows.
- `curl` of Arch's Waybar package file and history (gitlab.archlinux.org) — confirms no workspace-click patch.
- `systemctl is-active NetworkManager iwd bluetooth` → active, inactive, active.

## Sources read

- Hyprland wiki pages (read from the wiki's GitHub source, `hyprwm/hyprland-wiki`): hyprlauncher, hyprtoolkit, hyprpwcenter, hyprsysteminfo, hyprshutdown, hyprland-guiutils, hyprqt6engine, hyprland-qt-support, hyprpolkitagent, Status bars, App launchers, Other (wireless settings), Must-have, Notifications. Published at <https://wiki.hypr.land/>.
- Hyprland starter settings file: <https://github.com/hyprwm/Hyprland/blob/main/example/hyprland.lua>
- Hyprland source: `src/managers/WelcomeManager.cpp`, `DonationNagManager.cpp`, `VersionKeeperManager.cpp`, `src/config/values/ConfigValues.cpp`.
- READMEs: hyprlauncher, hyprpwcenter, hyprland-guiutils, hyprshutdown, hyprsysteminfo, hyprtoolkit, hyprqt6engine, hyprland-qt-support, HyprPanel, ashell, nwg-panel, nwg-drawer.
- Welcome app source (`hyprland-guiutils/utils/welcome/src/main.cpp`) for Hyprland's own recommended apps.
- Issues: Waybar #5029, #5294, #5301; nwg-panel #426, #436; nwg-displays #131, #134; open issue lists for hyprlauncher, hyprpwcenter, hyprshutdown, hyprsysteminfo, hyprland-guiutils, hyprtoolkit.
- HyprPanel retirement notice: <https://github.com/Jas-SinghFSU/HyprPanel/issues/1193>
