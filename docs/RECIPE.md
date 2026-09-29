# The recipe — one app per job

*For every job a bare Hyprland desktop needs, this page lists **up to five of the most reviewed and recommended options**, each with links showing how it works. **Javier chooses** ([D-11](DECISIONS.md#d-11--the-recipe-up-to-five-researched-options-per-job-and-javier-chooses)). A line marked "Claude's lean" is a suggestion, not a decision.*

> **Status: researched on 2026-09-28 (job 31 on 2026-09-29), waiting for Javier's choices.** Job 31 was tracked in [#11](https://github.com/jetomev/hypeforge/issues/11). Two research helpers working for Claude compiled it read-only: nothing was installed, and no system setting was changed. Claude read both halves in full before publishing, and removed personal details about the test desktop's home network and accounts. Each half ends with what it **could not verify**; those lists are kept below.

---

## Your choices at a glance

| # | Job | Claude's lean (a suggestion) | Javier's choice |
|---|---|---|---|
| 0 | **One all-in-one program, or separate small apps?** | Separate small apps. Noctalia 5 is the all-in-one to try later | ✅ **Separate small apps** (D-14, 2026-09-28) |
| 1 | Top bar | Waybar, once a release fixes clicking workspaces with the Lua config (or `waybar-git` until then). ironbar is already fixed | ✅ **Waybar**, `waybar-git` until a release after 0.15.0 (D-17, 2026-09-29) |
| 2 | App launcher | fuzzel | ✅ **Walker** + elephant, AUR only (D-18, 2026-09-29) |
| 3 | Notifications | mako | ✅ **mako** (D-19, 2026-09-29) |
| 4 | Volume and brightness pop-ups | SwayOSD for volume; monitor brightness through ddcutil |  ✅ **SwayOSD**; monitor brightness via ddcutil (D-20) |
| 5 | Lock screen | hyprlock |  ✅ **hyprlock** (D-20) |
| 6 | Screen-off and sleep timer | hypridle |  ✅ **hypridle** (D-20) |
| 7 | Wallpaper | hyprpaper |  ✅ **hyprpaper** (D-20) |
| 8 | Admin-password pop-up | hyprpolkitagent |  ✅ **hyprpolkitagent** (D-20) |
| 9 | Login screen | **The two research halves disagreed.** One suggested greetd + tuigreet (a terminal look, light). The other suggested keeping SDDM (already installed, with the KognogOS theme) | ✅ **greetd + tuigreet** (D-15, 2026-09-28) |
| 10 | Clipboard history | cliphist, with fuzzel as the picker |  ✅ **Walker's own clipboard** (D-21) |
| 11 | Screenshots | grim + slurp + Satty |  ✅ **grim + slurp + Satty** (D-21) |
| 12 | Screen recording | gpu-screen-recorder (the only fit for this NVIDIA card) |  ✅ **gpu-screen-recorder + OBS Studio** (D-21) |
| 13 | Look of other apps and the cursor | adw-gtk3 + a Catppuccin colour file; Qt follows GTK; the Catppuccin cursors already installed |  ✅ **Catppuccin everywhere:** adw-gtk-theme + Catppuccin colours, Qt follows GTK, Catppuccin cursor (D-21) |
| 14 | File manager | Yazi (terminal) + Thunar (add `gvfs`) | |
| 15 | Wi-Fi | nmtui (already installed); networkmanager-dmenu optional | |
| 16 | Bluetooth | bluetui | |
| 17 | Sound mixer | wiremix | |
| 18 | System monitor | btop + nvtop | |
| 19 | Three monitors | hypeForge writes `2560x1440@144` itself; nwg-displays as the visual fallback | |
| 20 | Night light | hyprsunset (optional; it was off on Plasma) | |
| 21 | Colour picker | hyprpicker + wl-clipboard | |
| 22 | Text editor | Fresh (already the KognogOS default) | |
| 23 | Image viewer | imv | |
| 24 | PDF viewer | Zathura (fill in forms in the browser) | |
| 25 | Video and music | mpv + mpv-mpris | |
| 26 | How Hyprland starts | start-hyprland (the plain "Hyprland" login entry), not uwsm | |
| 27 | USB drives | udiskie with a rule to ignore internal disks, + gvfs; keep `udisks2` on purpose | |
| 28 | Password wallet | KWallet on its own (keep `kwallet-pam`); pin the browsers to it | |
| 29 | Power menu | A small rofi list that calls hyprshutdown | |
| 30 | Printers | system-config-printer (already installed) | |
| 31 | File-open dialogs and screen sharing ("portals") | xdg-desktop-portal-hyprland for screen sharing + xdg-desktop-portal-gtk for the file window. A terminal (Yazi) file window can come later | ✅ **Hyprland's portal + GTK file window** (D-16, 2026-09-29) |

---

## What Plasma was quietly doing, and what that means

**Checked on this desktop (read-only): what Plasma was quietly doing**

- **Login:** SDDM 0.21 is the login screen, with the `kognogos` theme and a typed password (no auto-login). Its PAM file unlocks KWallet at login. (PAM is the login system's list of plug-ins.) The plug-in that does the unlocking, `kwallet-pam`, belongs to the `plasma` package group.
- **Wallet:** a KWallet wallet exists (`~/.local/share/kwalletd/kdewallet.kwl`). Google Chrome 154 and Brave are installed with no password-store setting, so each one picks its password store automatically. See job 28.
- **USB drives:** `udisks2` is the background service that actually mounts drives. It is installed only because KDE's `solid` library needs it. Plasma's own automounter settings are all **off** by default ([KDE source](https://github.com/KDE/plasma-desktop/blob/master/solid-device-automounter/lib/AutomounterSettingsBase.kcfg)), and this machine has no override. So Plasma listed drives and mounted them when clicked; it did not mount them on its own.
- **Wi-Fi:** NetworkManager stores the home Wi-Fi password for all users (`psk-flags` = 0). No applet is needed for it to keep auto-connecting.
- **Printer:** the HP printer queue uses driverless network printing (IPP), and it is the default. The print window inside apps comes from GTK or Qt talking to CUPS directly (`gtk3`, `gtk4` and `qt6-base` all depend on `libcups`), not from Plasma.
- **Night light:** KWin's Night Light is off by default ([KDE source](https://github.com/KDE/kwin/blob/master/src/plugins/nightlight/nightlightsettings.kcfg)), and `~/.config/kwinrc` has no Night Light section. It was off.
- **Disks:** the system disk is **not encrypted**. An internal Windows drive has an NTFS partition that udisks can see.
- **Already installed and useful:** thunar, dolphin, btop, htop, nano, vim, fresh-editor-bin 0.5.1, vlc, okular, keepassxc, network-manager-applet, nm-connection-editor, system-config-printer, cups-pk-helper, and rofi 2.0 (which runs natively on Wayland).
- **Also in the `plasma` group but outside these 17 jobs:** `polkit-kde-agent` (the pop-up that asks for your password), `powerdevil` (sleep and idle), `kscreenlocker` (lock screen), `xdg-desktop-portal-kde` (file-open dialogs) and `plasma-login-manager`.

**What follows from it:**
- **Keep on purpose:** `kwallet-pam` (it unlocks the wallet at login) and `udisks2` (it mounts drives). Both would leave with Plasma today.
- **Replace:** `polkit-kde-agent` (job 8), `powerdevil` (job 6), `kscreenlocker` (job 5) and `xdg-desktop-portal-kde`. That last one is the file-open dialogs (job 31).
- **Pin the browsers' password store** whichever wallet is chosen (job 28). Otherwise saved passwords can seem to vanish.

---

## How to read the tables

**How to read the tables**
- **Weight.** *Light* means a small program that brings no big drawing toolkit of its own. *Medium* means it brings a GUI toolkit (GTK or Qt, the building blocks programs use to draw windows) or is several MB. *Heavy* means a large app, or a full shell that brings Qt plus many services. Sizes are the package's own installed size from `pacman -Si`.
- **Kind.** *Terminal* means it runs as a command or as a text-mode app. *Graphical* means it draws its own windows or pop-ups. *Background* means an invisible helper that is set up with a config file.
- **In Arch.** This is what `nog search` printed on 2026-09-28 (repo and version). "chaotic-aur" is the extra ready-built repo KognogOS already uses. "AUR only" means it is in neither of those; that was checked with the AUR's web lookup.
- **Activity.** ★ means GitHub stars (Codeberg where noted), followed by the latest release and the latest commit. These come from `gh api` or the project page.
- **Source shorthand.** **HW** is the Hyprland wiki. **AW** is the Arch Wiki. **awesome-hyprland** is the community list the HW links to. **O3 / O4** are Omarchy 3.8.4 and Omarchy 4.0.4.

**Two facts that shape every choice**
1. **Since Hyprland 0.55, commands use the new Lua wording.** This covers the commands other programs send to Hyprland (`hyprctl dispatch …`). Tools that still send the old wording fail silently. That is exactly what broke clicking a workspace number in Waybar, ironbar, ashell and Noctalia in May 2026 (details in jobs 0 and 1).
2. **The Hyprland team's side tools did not move to Lua.** hyprlock, hypridle, hyprpaper and hyprlauncher still read their own `~/.config/hypr/*.conf` files in the older "hyprlang" format.
   - The Lua announcement says: "Other hypr* tools will for now continue using hyprlang as their config language provider" ([hypr.land/news/26_lua](https://hypr.land/news/26_lua/)).
   - The current HW pages for [hyprlock](https://wiki.hypr.land/Hypr-Ecosystem/hyprlock/), [hypridle](https://wiki.hypr.land/Hypr-Ecosystem/hypridle/) and [hyprpaper](https://wiki.hypr.land/Hypr-Ecosystem/hyprpaper/) still document `.conf` files, and their Arch packages still depend on the `hyprlang` library.
   - **One catch:** any `hyprctl dispatch` line *inside* those files must use the Lua wording. hypridle 0.1.8 changed its examples for exactly this reason ("config: update dpms commands to lua syntax", [release notes](https://github.com/hyprwm/hypridle/releases/tag/v0.1.8)).

---

# Part 1 · The things you see

## 0. One all-in-one shell, or separate small apps?
*What this job is:* Decide whether one program draws the bar, pop-ups, lock screen and menus, or whether each job gets its own small program.
*Omarchy reference:* Omarchy 3 used separate apps: Waybar, Walker, Mako, SwayOSD, hyprlock, hypridle, swaybg and polkit-gnome. Omarchy 4 replaced all of them with one Quickshell program it wrote itself: "the bar, launcher, menus, notifications, on-screen displays, control panels, lock screen, and polkit agent now all live inside a single long-running shell process" ([v4.0.0 notes](https://github.com/basecamp/omarchy/releases/tag/v4.0.0)). That shell lives inside Omarchy's own repo and is not published as a separate package.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | Separate small apps ("classic stack") | One small program per job (a bar, a launcher, a notification daemon and so on), each with its own text config file. | Light to Medium, depending on the picks (measured below) | Mixed; several jobs have terminal-style picks | Nearly every piece is in `extra` (see jobs 1–13) | per piece | This is the model both wikis teach: [HW Useful Utilities](https://wiki.hypr.land/Useful-Utilities/Must-have/) and [AW Hyprland](https://wiki.archlinux.org/title/Hyprland) walk through one tool per job. Used by O3, [HyDE](https://github.com/HyDE-Project/HyDE/blob/master/Scripts/pkg_core.lst), [ML4W](https://github.com/mylinuxforwork/dotfiles/blob/main/setup/dependencies/packages) and [JaKooLit](https://github.com/JaKooLit/Arch-Hyprland/blob/main/install-scripts/01-hypr-pkgs.sh). |
| 2 | [DankMaterialShell (DMS)](https://danklinux.com/) | A complete Material-Design shell built on Quickshell (a Qt toolkit for making shells) plus a Go helper program. Comes with a graphical settings app. | Heavy (Qt6/QML + Go; package 71.8 MiB; 32 extra packages, about 310 MiB, mostly Qt6) | Graphical | `extra/dms-shell-hyprland 1.6.2-1` (+ `dms-shell`) | ★8.2k · v1.6.2 2026-09 · commits 2026-09 | Listed twice on the HW: under ["Desktop shells"](https://wiki.hypr.land/Useful-Utilities/Status-Bars/) and as "Dank Linux" in [Preconfigured setups](https://wiki.hypr.land/Getting-Started/Preconfigured-setups/). Its [README](https://github.com/AvengeMedia/DankMaterialShell) says it "replaces waybar, swaylock, swayidle, mako, fuzzel, polkit". It has lock, idle, on-screen pop-ups, clipboard history with pictures, screenshots and a password pop-up. It also has a matching login screen ([dank-greeter](https://github.com/AvengeMedia/dank-greeter)). |
| 3 | [Noctalia](https://noctalia.dev/) (version 5) | A desktop shell rewritten for version 5 as one native C++ program "with no Qt or GTK dependency". Uses TOML config files plus a graphical settings window. | Medium (C++, no toolkit; package 33.2 MiB; 29 extra packages, about 190 MiB, of which about 100 MiB is git + perl that it requires) | Graphical | `extra/noctalia 5.2.0-1` | ★10.9k · v5.2.0 2026-09-27 (version 5 has only been stable since 2026-09-03) | Listed under HW "Desktop shells". The HW still says "Built on Quickshell", which is out of date since version 5. Its [README](https://github.com/noctalia-dev/noctalia) covers: bars, launcher, notifications, lock screen, idle, on-screen pop-ups, clipboard, wallpaper, screenshots with annotation, and a password pop-up you can switch on. It has a built-in Catppuccin palette and a separate [login screen](https://github.com/noctalia-dev/noctalia-greeter). It stays out of Hyprland's config: "Core Noctalia is non-invasive: it does not manage your compositor settings". |
| 4 | [end-4 "illogical-impulse"](https://github.com/end-4/dots-hyprland) | A full personal set of config files (dotfiles) whose graphical shell runs on Quickshell. Installed by a setup script. | Heavy (Quickshell/Qt6 plus many extras, including AI features) | Graphical | not packaged (installed with a download-and-run script, or `./setup install`) | ★16.2k · release 2026.05.11 · commits 2026-09 | HW Preconfigured setups ("end_4"). The most-starred option here. Its README warns that if your distro has not shipped Hyprland 0.55 you should use the "Pre-Hyprland Luaification release". |
| 5 | [Caelestia](https://github.com/caelestia-dots/shell) | A "fluid, morphing" Quickshell shell aimed at Hyprland. Config lives in `~/.config/caelestia/shell.json`. | Heavy (needs a Quickshell **git** build plus a long dependency list: cava, aubio, lm_sensors, fish, Material fonts and more) | Graphical | AUR only (`caelestia-shell 2.5.0-1`) | ★12.6k · v2.5.0 2026-09 · commits 2026-09 | Very high stars, and DMS credits it as inspiration. It is not on the HW. Its README requires `quickshell-git`, which "has to be the git version, not the latest tagged version". |

*Left out on purpose:*
- **HyprPanel** (built on AGS). Its GitHub repo is archived (last change 2026-04-23). The README says: "no longer maintained. Active development has moved to Wayle". Wayle is Rust/GTK4, ★943, v0.7.0, AUR only.
- **Writing our own shell on Quickshell, AGS or eww** (what Omarchy 4 did). The HW lists these as "widget systems" where "you basically need to write code". It also says Quickshell "is still in alpha and minor breaking changes are to be expected".

**The trade-off in plain words**
- **One basket or many baskets.** An all-in-one shell gives one look, one settings file and fewer programs to start. But if it crashes, or breaks after a Hyprland update, the bar, notifications, lock screen, idle timer and password pop-up all go down together. Separate apps fail one at a time, and a broken piece can be swapped without touching the rest.
- **Weight depends mostly on the drawing toolkit, not on the approach.** These are disk numbers: how many extra packages a bare `base + hyprland` Arch system would still need (measured with `pactree`).
  - Separate apps with no toolkit (fuzzel, mako, hyprlock, hypridle, hyprpaper, wob, cliphist): 14 packages, about 21 MiB.
  - The same set plus Waybar and polkit-gnome (both GTK3): 116 packages, about 380 MiB.
  - A mixed set with GTK3, GTK4 and Qt6 pieces (Waybar, SwayOSD, hyprpolkitagent and others): 150 packages, about 704 MiB.
  - Noctalia: 29 packages, about 190 MiB. DMS: 32 packages, about 310 MiB.
  - On *this* desktop, GTK3, GTK4 and Qt6 are already installed for Chrome, Brave, Discord, GIMP, Thunderbird and others, so the real extra here is much smaller.
  - Memory (RAM) use was **not measured**.
- **Fit with "light + terminal-first".** Separate apps let hypeForge pick terminal-style tools where they exist: a text-mode login screen, a text-mode clipboard, a command-line screen recorder. The all-in-one shells are graphical by design and come with graphical settings windows.
- **One portable settings folder.**
  - *Separate apps:* every one accepts a "use this config file" option (checked in the source code or docs: Waybar, mako, hyprlock, hypridle and hyprpaper all have `-c`). hypeForge can point them all at one folder.
  - *Noctalia:* reads every `*.toml` file in `~/.config/noctalia/` and saves changes made in its settings window to `~/.local/state/noctalia/settings.toml`. Both locations can be moved with `NOCTALIA_CONFIG_HOME` / `NOCTALIA_STATE_HOME` ([docs](https://docs.noctalia.dev/noctalia/configuration/)).
  - *DMS:* its settings window writes `~/.config/DankMaterialShell/settings.json`. Its `dms setup` step also writes its own Lua pieces into `~/.config/hypr/dms/` and moves old Hyprland configs into a backup folder ([docs](https://danklinux.com/docs/dankmaterialshell/compositors)). That overlaps with hypeForge owning `hyprland.lua`, and one bug in that move deleted a user's config ([#3359](https://github.com/AvengeMedia/DankMaterialShell/issues/3359), fixed in 1.6.1).
- **Surviving Hyprland updates.** The May 2026 switch to Lua was a live test. Hyprland 0.55.0 shipped on 2026-05-09.
  - Quickshell added Lua support in 0.3.0, five days earlier ([changelog](https://github.com/quickshell-mirror/quickshell/blob/master/changelog/v0.3.0.md)).
  - Noctalia fixed its breakage by 2026-05-14 ([#2603](https://github.com/noctalia-dev/noctalia/issues/2603)).
  - DMS finished its move to Lua in its development version by mid-May ([#2547](https://github.com/AvengeMedia/DankMaterialShell/issues/2547)).
  - ashell shipped its fix in 0.9.0 (June). ironbar shipped its fix only in 0.19.1 (2026-09-20).
  - Waybar fixed it in its code on 2026-05-04 but has **not released anything since 0.15.0 (Feb 2026)**. The Waybar in `extra` still cannot switch workspaces by click ([#5294](https://github.com/Alexays/Waybar/issues/5294), September 2026).
  - The Hyprland team's own tools (hyprlock, hypridle, hyprpaper) kept working because they kept their own `.conf` format.

**How it works — read more:** DMS: [docs](https://danklinux.com/docs/) · [compositor setup](https://danklinux.com/docs/dankmaterialshell/compositors). Noctalia: [docs](https://docs.noctalia.dev/noctalia/) · [how config files layer](https://docs.noctalia.dev/noctalia/configuration/). end-4: [setup wiki](https://ii.clsty.link/en/ii-qs/01setup/). Caelestia: [README](https://github.com/caelestia-dots/shell). Separate apps: [HW Useful Utilities](https://wiki.hypr.land/Useful-Utilities/Must-have/) · [AW Hyprland](https://wiki.archlinux.org/title/Hyprland).
**Claude's lean:** Separate small apps. This fits "small + terminal-first" best, nearly every piece is in `extra`, the lock, idle and wallpaper pieces come from the Hyprland team, and a broken piece can be replaced on its own. If an all-in-one is wanted later, Noctalia 5 is the best fit (no Qt/GTK, TOML config, movable config folder, leaves Hyprland's config alone), but it has only been stable since 2026-09-03. (A suggestion; Javier chooses.)

---

## 1. Top bar
*What this job is:* The strip along the top of the screen that shows workspaces, the clock, volume, network and small app icons.
*Omarchy reference:* Omarchy 3 used Waybar. Omarchy 4 draws the bar inside its own Quickshell shell, with plugin widgets and a bar you can drag to any screen edge.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [Waybar](https://github.com/Alexays/Waybar) | The classic bar for Wayland desktops, with built-in Hyprland modules. Config is JSON plus a CSS style file. | Medium (C++/GTK3; 2.2 MiB) | Graphical | `extra/waybar 0.15.0-3` (the fixed development build is `chaotic-aur/waybar-git 0.15.0.r1026`) | ★12.0k · release 0.15.0 2026-02 · commits 2026-09 | First on the [HW status bars page](https://wiki.hypr.land/Useful-Utilities/Status-Bars/). It is AW Hyprland's example and has its [own AW page](https://wiki.archlinux.org/title/Waybar). Used by O3, HyDE, ML4W and JaKooLit, and listed on awesome-hyprland. **Warning:** the `extra` 0.15.0 cannot switch workspaces by click with Hyprland's Lua config ([#5294](https://github.com/Alexays/Waybar/issues/5294)). The fix ([#5013](https://github.com/Alexays/Waybar/pull/5013)) was merged 2026-05-04 but is unreleased; there are 1,026 commits since 0.15.0. |
| 2 | [ashell](https://malpenzibo.github.io/ashell/) | A "ready to go" bar for Hyprland in Rust. It has fewer options on purpose. | Light–Medium (Rust + iced toolkit, no GTK/Qt; size not measured) | Graphical | AUR only (`ashell 0.10.0-1`) | ★1.1k · v0.10.0 2026-09 · commits 2026-09 | On the [HW status bars page](https://wiki.hypr.land/Useful-Utilities/Status-Bars/): "ready to use out of the box… pretty limited configuration options". Listed on awesome-hyprland. Its Lua fix ([PR #757](https://github.com/MalpenZibo/ashell/pull/757)) has been in releases since 0.9.0. |
| 3 | [ironbar](https://github.com/JakeStanger/ironbar) | A Rust + GTK4 bar with many ready-made modules. | Medium (Rust/GTK4; 26.1 MiB) | Graphical | `extra/ironbar 0.19.1-1` | ★1.5k · v0.19.1 2026-09-20 | Listed on awesome-hyprland and in `extra`. Its Lua workspace-click fix ([#1548](https://github.com/JakeStanger/ironbar/issues/1548)) shipped in 0.19.1. It is not on the HW. |
| 4 | [eww](https://github.com/elkowar/eww) | A widget kit that can be built into a bar. Uses its own Lisp-like config language. | Medium (Rust/GTK3) | Graphical | `chaotic-aur/eww 0.6.0-1.3` | ★12.7k · v0.6.0 2024-04 · commits 2026-07 | One of the HW "widget systems", next to AGS and Quickshell. The HW warns of "heavy reliance on external scripts" and GTK3 "which does not support GPU acceleration". You write the bar yourself. |
| 5 | Bar built into an all-in-one shell | The bar that comes with Noctalia or DMS. | See job 0 | Graphical | `extra` (noctalia / dms-shell-hyprland) | See job 0 | This is the Omarchy 4 route. It only applies if job 0 picks a shell. |

**How it works — read more:** Waybar: [wiki](https://github.com/Alexays/Waybar/wiki/Module:-Hyprland) · [AW](https://wiki.archlinux.org/title/Waybar). ashell: [docs](https://malpenzibo.github.io/ashell/). ironbar: [README](https://github.com/JakeStanger/ironbar). eww: [docs](https://elkowar.github.io/eww/). Catppuccin port for Waybar: [catppuccin/waybar](https://github.com/catppuccin/waybar).
**Claude's lean:** Waybar. It is the best-documented bar and has a Catppuccin port. But only take it once a release after 0.15.0 exists, or use `waybar-git` from chaotic-aur (installable through nog) until then. If that is unwanted, ironbar is already fixed in `extra`. (A suggestion; Javier chooses.)

---

## 2. App launcher / menu
*What this job is:* The pop-up where you type part of an app's name and press Enter. It doubles as a "pick one from a list" menu for other things, such as clipboard history.
*Omarchy reference:* Omarchy 3 used Walker (with its helper service "elephant"). Omarchy 4 has its own launcher merged into the Omarchy menu on Super+Space, which searches apps and commands.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [Rofi](https://github.com/davatorium/rofi) | The classic launcher, window switcher and list-picker. Works natively on Wayland since version 2.0 (2025). | Light (C, no GTK/Qt; 1.1 MiB) | Graphical (keyboard-driven) | `extra/rofi 2.0.0-1` (already installed here) | ★16.4k · 2.0.0 2025-09 · commits 2026-09 | On the [HW launchers page](https://wiki.hypr.land/Useful-Utilities/App-Launchers/) and has its [own AW page](https://wiki.archlinux.org/title/Rofi). Used by HyDE, ML4W and JaKooLit; listed on awesome-hyprland. Catppuccin port: [catppuccin/rofi](https://github.com/catppuccin/rofi). |
| 2 | [Walker](https://github.com/abenz1267/walker) | A Rust + GTK4 launcher with many modules: apps, calculator, files, clipboard, symbols and more. A separate service called "elephant" feeds it. | Medium (Rust/GTK4 + a Go service) | Graphical | AUR only (`walker 2.17.1`, `elephant 2.22.1`) | ★3.1k · v2.17.1 2026-09 · commits 2026-09 | Omarchy 3's launcher ([O3 package list](https://github.com/basecamp/omarchy/blob/v3.8.4/install/omarchy-base.packages)). On the HW launchers page and awesome-hyprland. |
| 3 | [fuzzel](https://codeberg.org/dnkl/fuzzel) | A tiny launcher in the style of rofi, which also works as a list-picker. | Light (C; 328 KiB; no GTK/Qt) | Graphical (keyboard-driven) | `extra/fuzzel 1.15.0-1` | ★920 (Codeberg) · 1.15.0 2026-09 | On the HW launchers page, and used in the HW clipboard examples. Listed on awesome-hyprland. DMS's README names it among the tools DMS replaces. Catppuccin port: [catppuccin/fuzzel](https://github.com/catppuccin/fuzzel). |
| 4 | [Vicinae](https://github.com/vicinaehq/vicinae) | A launcher in the style of Raycast (a popular Mac launcher). It keeps running in the background and supports extensions. | Heavy (C++/Qt; always-running service) | Graphical | `chaotic-aur/vicinae 0.29.0-1` | ★10.1k · v0.29.0 2026-09 | On the HW launchers page ("runs as a server in the background") and awesome-hyprland. Very high stars. |
| 5 | [hyprlauncher](https://wiki.hypr.land/Hypr-Ecosystem/hyprlauncher/) | The Hyprland team's own launcher and list-picker. | Light (C++ with hyprtoolkit; 392 KiB) | Graphical | `extra/hyprlauncher 0.1.6-9` | ★358 · v0.1.6 2026-04 | Listed **first** on the HW launchers page. Config is `~/.config/hypr/hyprlauncher.conf` in the hyprlang format, not Lua. Still young (0.1.x). |

**How it works — read more:** Rofi: [AW](https://wiki.archlinux.org/title/Rofi). Walker: [docs](https://benz.gitbook.io/walker/). fuzzel: [project page](https://codeberg.org/dnkl/fuzzel). Vicinae: [README](https://github.com/vicinaehq/vicinae). hyprlauncher: [HW](https://wiki.hypr.land/Hypr-Ecosystem/hyprlauncher/). Also seen: wofi (AW Hyprland's example; `extra/wofi 1.5.3-1`, GTK3); tofi (last release 2023, AUR flagged out-of-date); sway-launcher-desktop (fzf run inside a floating terminal, `chaotic-aur` 1.7.0; the most "terminal" option but last released 2023-09).
**Claude's lean:** fuzzel. It is the smallest mainstream launcher in `extra`, works entirely from the keyboard, doubles as the picker for clipboard history and hypeForge's own menus, and has a Catppuccin port. (A suggestion; Javier chooses.)

---

## 3. Notifications
*What this job is:* The small message boxes that pop up ("Download finished"), plus a way to see ones you missed.
*Omarchy reference:* Omarchy 3 used Mako. Omarchy 4 has its own notification service inside the shell, with do-not-disturb and a history that replays the last ten notifications.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [mako](https://github.com/emersion/mako) | A minimal notification service with a plain-text config. `makoctl` gives you history and restore, and "modes" (such as do-not-disturb). | Light (C; 141 KiB; no GTK/Qt) | Graphical | `extra/mako 1.11.0-1` | ★3.3k · v1.11.0 2026-03 · commits 2026-06 | Used by O3. Named as an example on the [HW must-have page](https://wiki.hypr.land/Useful-Utilities/Must-have/) and used for the pop-up examples on [AW Hyprland](https://wiki.archlinux.org/title/Hyprland). Listed on awesome-hyprland; Catppuccin port: [catppuccin/mako](https://github.com/catppuccin/mako). |
| 2 | [dunst](https://dunst-project.org/) | A very configurable notification service with history (keeps 20 by default) and progress bars. | Light (C; 291 KiB) | Graphical | `extra/dunst 1.13.2-2` | ★5.6k · v1.13.2 2026-03 · commits 2026-09 | Named on the HW must-have page and has its [own AW page](https://wiki.archlinux.org/title/Dunst). Used by HyDE; listed on awesome-hyprland; Catppuccin port: [catppuccin/dunst](https://github.com/catppuccin/dunst). |
| 3 | [SwayNotificationCenter (swaync)](https://github.com/ErikReider/SwayNotificationCenter) | A notification service plus a slide-out "control center" panel with do-not-disturb and widgets. | Medium (Vala/GTK4; 745 KiB) | Graphical | `extra/swaync 0.12.6-1` | ★2.6k · v0.12.6 2026-03 · commits 2026-06 | Named on the HW must-have page. Used by ML4W and JaKooLit; listed on awesome-hyprland; Catppuccin port: [catppuccin/swaync](https://github.com/catppuccin/swaync). |
| 4 | [fnott](https://codeberg.org/dnkl/fnott) | A "keyboard driven and lightweight" notification service. | Light (C; 218 KiB) | Graphical | `extra/fnott 1.8.0-1` | ★181 (Codeberg) · 1.8.0 2025-07 · commits 2026-09 | Named on the HW must-have page and listed on awesome-hyprland. |
| 5 | Built into an all-in-one shell | The notification service that comes with Noctalia or DMS. | See job 0 | Graphical | `extra` | See job 0 | The Omarchy 4 route. Only applies if job 0 picks a shell. |

**How it works — read more:** mako: [mako(5) manual](https://github.com/emersion/mako/blob/master/doc/mako.5.scd) · [AW Desktop notifications](https://wiki.archlinux.org/title/Desktop_notifications). dunst: [docs](https://dunst-project.org/) · [AW](https://wiki.archlinux.org/title/Dunst). swaync: [README](https://github.com/ErikReider/SwayNotificationCenter). fnott: [project page](https://codeberg.org/dnkl/fnott).
**Claude's lean:** mako. It is the smallest mainstream option, Omarchy 3's choice and AW Hyprland's example, with one plain-text config file and a Catppuccin port. (A suggestion; Javier chooses.)

---

## 4. Volume / brightness pop-ups (OSD)
*What this job is:* The small bar that flashes on screen when you press the volume or brightness keys. OSD means "on-screen display".
*Omarchy reference:* Omarchy 3 used SwayOSD. Omarchy 4 draws its own volume, brightness and media pop-ups in the shell, and added external-monitor brightness through DDC/CI (the standard way a PC talks to a monitor's own settings).

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [SwayOSD](https://github.com/ErikReider/SwayOSD) | Pop-ups for volume, brightness and Caps Lock. A background part (`swayosd-server`) runs, and your key bindings call `swayosd-client`. | Medium (Rust/GTK4; 8.5 MiB) | Graphical | `extra/swayosd 0.3.2-1` | ★1.3k · v0.3.2 2026-06 | Used by O3; listed on awesome-hyprland (OSD). Its brightness control works only on "BrightnessCtl devices" (built-in backlights). The optional Caps Lock watcher is a system service turned on with sudo. |
| 2 | Notification trick (mako / dunst) | Show volume as a notification with a progress bar, so there is nothing extra to run. | Light (reuses the notification service) | Graphical | `extra` (mako / dunst) | n/a | [AW Hyprland](https://wiki.archlinux.org/title/Hyprland) ("On-screen notifications") builds volume and brightness pop-ups this way with mako. mako draws a progress indicator from a "value" hint ([mako(5)](https://github.com/emersion/mako/blob/master/doc/mako.5.scd)); dunst has `progress_bar`. Needs a small script per key. |
| 3 | [wob](https://github.com/francma/wob) | A "dead simple" bar overlay: a script sends it a number from 0–100 and it shows a bar. | Light (C; 50 KiB) | Graphical | `extra/wob 0.16-2` | ★1.2k · 0.16 2025-05 · commits 2026-09 | Listed on awesome-hyprland (OSD). Needs a small script. |
| 4 | [avizo](https://github.com/heyjuvi/avizo) | macOS-style pop-ups, with helper scripts included. | Medium (Vala/GTK3) | Graphical | AUR only (`avizo 1.3-1`) | ★622 · 1.3 2024-01 · commits 2025-10 | Listed on awesome-hyprland (OSD). Less active than the others. |
| 5 | Built into an all-in-one shell | Noctalia (`[osd]` section; monitor brightness through ddcutil, opt-in), DMS (OSD module; checks for DDC/CI monitors by default), Omarchy 4. | See job 0 | Graphical | `extra` | See job 0 | The Omarchy 4 route. Only applies if job 0 picks a shell. |

**How it works — read more:** SwayOSD: [README](https://github.com/ErikReider/SwayOSD). Notification trick: [AW Hyprland](https://wiki.archlinux.org/title/Hyprland). wob: [README](https://github.com/francma/wob). avizo: [README](https://github.com/heyjuvi/avizo). *Hardware note:* Javier's three monitors are external, so there is no built-in backlight. Brightness keys only do something through DDC/CI. `extra/ddcutil` is already installed here (3.0.1).
**Claude's lean:** SwayOSD for volume. It is Omarchy 3's proven choice, in `extra`, and needs no helper scripts. Monitor brightness would be a separate ddcutil binding, because SwayOSD only drives built-in backlights. (A suggestion; Javier chooses.)

---

## 5. Lock screen
*What this job is:* The screen that covers everything and asks for your password before you can get back in.
*Omarchy reference:* Omarchy 3 used hyprlock. Omarchy 4 replaced it with a lock screen drawn by its shell, using the system's normal password check (PAM) plus fingerprint support.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [hyprlock](https://wiki.hypr.land/Hypr-Ecosystem/hyprlock/) | The Hyprland team's lock screen, drawn with the graphics card (GPU-accelerated). | Light (C++; 844 KiB) | Graphical | `extra/hyprlock 0.9.6-3` | ★1.7k · v0.9.6 2026-07 · commits 2026-08 | Part of the HW Hypr ecosystem. AW says "the most common setup is hypridle and hyprlock" ([AW Hyprland](https://wiki.archlinux.org/title/Hyprland)) and it has its [own AW page](https://wiki.archlinux.org/title/Hyprlock). Used by O3, HyDE, ML4W and JaKooLit; Catppuccin port: [catppuccin/hyprlock](https://github.com/catppuccin/hyprlock). Config is still `~/.config/hypr/hyprlock.conf` (hyprlang). **The HW warns:** with no config file "hyprlock exits with an error and your session will not be locked." v0.9.3 added an NVIDIA workaround. |
| 2 | [swaylock](https://github.com/swaywm/swaylock) | Sway's minimal lock screen: a coloured screen with a ring. | Light (C; 87 KiB) | Graphical | `extra/swaylock 1.8.6-1` | ★1.2k · v1.8.6 2026-07 | On the [AW Session lock](https://wiki.archlinux.org/title/Session_lock) list. awesome-hyprland calls it "very configurable, and popular". DMS's README names it among the tools DMS replaces. |
| 3 | [gtklock](https://github.com/jovanlanik/gtklock) | A GTK lock screen with add-on modules. | Light (C/GTK3; 55 KiB) | Graphical | `extra/gtklock 4.0.0-1` | ★499 · v4.0.0 2024-10 · commits 2026-02 | On the AW Session lock list. |
| 4 | [swaylock-effects](https://github.com/jirutka/swaylock-effects) | A copy of swaylock with blur and a clock added. | Light (C) | Graphical | `chaotic-aur/swaylock-effects 1.7.0.0-4.4` | ★229 · no releases · last commit 2024-03 (**stale**) | On the AW Session lock list and awesome-hyprland. |
| 5 | Built into an all-in-one shell | The lock screen of Noctalia, DMS, Caelestia or Omarchy 4. | See job 0 | Graphical | `extra` (Noctalia, DMS) | See job 0 | The Omarchy 4 route. Only applies if job 0 picks a shell. |

**How it works — read more:** hyprlock: [HW](https://wiki.hypr.land/Hypr-Ecosystem/hyprlock/) · [AW](https://wiki.archlinux.org/title/Hyprlock). swaylock: [README](https://github.com/swaywm/swaylock) · [AW Session lock](https://wiki.archlinux.org/title/Session_lock). gtklock: [README](https://github.com/jovanlanik/gtklock).
**Claude's lean:** hyprlock. It comes from the Hyprland team and moves in step with Hyprland, it is GPU-drawn for three 1440p screens, and it has a Catppuccin port. hypeForge must always ship its config file, because without one it refuses to lock. (A suggestion; Javier chooses.)

---

## 6. Idle / screen-off / sleep timer
*What this job is:* A quiet background helper. After some minutes of no keyboard or mouse it locks the screen, then turns the monitors off, then puts the PC to sleep. It holds off while a video is playing.
*Omarchy reference:* Omarchy 3 used hypridle. In Omarchy 4 the shell itself handles idle, with timings in `~/.config/omarchy/shell.json` ([O4 manual](https://github.com/basecamp/omarchy/blob/v4.0.4/manual/13-toggles-idle-screensaver.md)).

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [hypridle](https://wiki.hypr.land/Hypr-Ecosystem/hypridle/) | The Hyprland team's idle helper. You list "after N seconds do X" steps. By default it respects "don't sleep" requests from apps such as video players. | Light (C++; 279 KiB) | Background | `extra/hypridle 0.1.8-2` | ★699 · v0.1.8 2026-07 | On the HW, and on AW Hyprland ("most common setup") and [AW Session lock](https://wiki.archlinux.org/title/Session_lock). Used by O3, HyDE, ML4W and JaKooLit. Config is still `~/.config/hypr/hypridle.conf` (hyprlang), and "a config file is required". Any `hyprctl dispatch` lines in it must use Lua wording, e.g. `hyprctl dispatch 'hl.dsp.dpms({ action = "disable" })'` from the HW. AW Hyprland's example still shows the old `dpms off` wording. |
| 2 | [swayidle](https://github.com/swaywm/swayidle) | Sway's idle helper, configured with command-line options. | Light (C; 36 KiB) | Background | `extra/swayidle 1.9.0-1` | ★765 · v1.9.0 2025-11 · commits 2026-08 | On AW Session lock ("Wayland triggers") and awesome-hyprland. DMS's README names it among the tools DMS replaces. |
| 3 | Built into an all-in-one shell | Omarchy 4 (shell.json), Noctalia (`[idle.behavior.*]` blocks in TOML), DMS (idle detection, auto-lock/suspend with separate plugged-in/battery settings). | See job 0 | Background | `extra` | See job 0 | The Omarchy 4 route. Only applies if job 0 picks a shell. |

**How it works — read more:** hypridle: [HW](https://wiki.hypr.land/Hypr-Ecosystem/hypridle/) · [AW Hyprland, Idle](https://wiki.archlinux.org/title/Hyprland). swayidle: [README](https://github.com/swaywm/swayidle). Noctalia idle: [docs](https://docs.noctalia.dev/noctalia/).
**Claude's lean:** hypridle. It pairs with hyprlock and comes from the same team; hypeForge writes its `.conf` using the new Lua command wording. (A suggestion; Javier chooses.)

---

## 7. Wallpaper
*What this job is:* Draws the background picture on each of the three monitors.
*Omarchy reference:* Omarchy 3 used swaybg. Omarchy 4 draws the background inside its shell and adds a visual background picker (Super+Ctrl+Space).

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [hyprpaper](https://wiki.hypr.land/Hypr-Ecosystem/hyprpaper/) | The Hyprland team's wallpaper tool. It supports a different picture per monitor, a folder slideshow, and changing the picture while running (`hyprctl hyprpaper wallpaper …`). | Light (C++; 479 KiB) | Background | `extra/hyprpaper 0.8.4-9` | ★1.4k · v0.8.4 2026-04 · commits 2026-08 | First on the [HW wallpapers page](https://wiki.hypr.land/Useful-Utilities/Wallpapers/) and AW Hyprland's example. Used by ML4W; listed in awesome-hyprland's official tools. Config is `~/.config/hypr/hyprpaper.conf` (hyprlang; optional). |
| 2 | [swaybg](https://github.com/swaywm/swaybg) | The tiniest option: one still picture, set per monitor with options like `-o <monitor> -i <file>`. | Light (C; 34 KiB) | Background | `extra/swaybg 1.2.2-1` | ★817 · v1.2.2 2026-02 · commits 2026-09 | Used by O3. The HW calls it "great utility if all you want is one simple static wallpaper". Listed on awesome-hyprland. |
| 3 | [awww](https://codeberg.org/LGFae/awww) (formerly swww) | A wallpaper helper with animated transitions and GIF support, changeable while running. | Medium (Rust; 10.6 MiB) | Background | `extra/awww 0.12.1-1` | ★452 on Codeberg (plus ★3.6k on the archived GitHub "swww") · v0.12.1 2026-04 | On the HW wallpapers page. Used by HyDE and ML4W (as awww) and JaKooLit (as swww). Renamed and moved to Codeberg in 2025-10. |
| 4 | [wpaperd](https://github.com/danyspin97/wpaperd) | A wallpaper helper that rotates pictures automatically, configured with TOML. | Medium (Rust; 8.5 MiB) | Background | `extra/wpaperd 1.3.0-2` | ★614 · 1.3.0 2026-05 | On the HW wallpapers page and awesome-hyprland. |
| 5 | Built into an all-in-one shell | Omarchy 4 background plugin, Noctalia `[wallpaper]`, DMS, Caelestia. | See job 0 | Background | `extra` | See job 0 | The Omarchy 4 route. Only applies if job 0 picks a shell. |

**How it works — read more:** hyprpaper: [HW](https://wiki.hypr.land/Hypr-Ecosystem/hyprpaper/) · [AW Hyprland, Desktop wallpaper](https://wiki.archlinux.org/title/Hyprland). swaybg: [swaybg(1) manual](https://github.com/swaywm/swaybg/blob/master/swaybg.1.scd). awww: [project page](https://codeberg.org/LGFae/awww). Pickers that sit on top: waypaper (graphical window, AUR only) and WallRizz (a text-mode picker, fits terminal-first, on the HW, but not packaged anywhere).
**Claude's lean:** hyprpaper. It comes from the Hyprland team, handles a separate picture for each of the three monitors, and can be told to change picture while running, which hypeForge could later use for a wallpaper picker. swaybg is the choice if the aim is the absolute smallest. (A suggestion; Javier chooses.)

---

## 8. Admin password pop-up (polkit agent)
*What this job is:* The window that asks for your password when a graphical app needs admin rights, for example a disk tool. polkit is the system service that decides when an app may do admin things. Without this helper, those apps simply fail or hang.
*Omarchy reference:* Omarchy 3 used polkit-gnome. Omarchy 4 draws the password prompt inside its shell (themed, and it shows exactly what is being authorised) and moved its own admin actions to pkexec/polkit.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [hyprpolkitagent](https://wiki.hypr.land/Hypr-Ecosystem/hyprpolkitagent/) | The Hyprland team's password pop-up. In v0.2.0 its window moved to hyprtoolkit. | Medium (C++; 300 KiB, but still depends on Qt6 libraries: qt6-base, qt6-declarative, polkit-qt6) | Graphical | `extra/hyprpolkitagent 0.2.0-1` | ★226 · v0.2.0 2026-09 | The [HW must-have page](https://wiki.hypr.land/Useful-Utilities/Must-have/) points to it. AW Hyprland says "Hyprland recommends using hyprpolkitagent", and it is on the [AW Polkit agents list](https://wiki.archlinux.org/title/Polkit#Authentication_agents). Used by HyDE and JaKooLit. |
| 2 | [polkit-gnome](https://gitlab.gnome.org/Archive/policykit-gnome) | GNOME's old password pop-up. | Light (C/GTK3; 333 KiB) | Graphical | `extra/polkit-gnome 0.105-12` | Upstream **archived**: last release 0.105 in 2011-10, now in GNOME's "Archive" group | Used by O3 and ML4W; on the AW Polkit agents list. It still works, but nobody maintains it upstream. |
| 3 | [polkit-kde-agent](https://github.com/KDE/polkit-kde-agent-1) | KDE's password pop-up. | Medium (Qt6 + KDE Frameworks) | Graphical | `extra/polkit-kde-agent 6.7.5-1` (installed now, as part of Plasma) | ★34 (GitHub mirror) · commits 2026-09 · ships with Plasma | The alternative the HW names ("KDE's one"), and on the AW list. Keeping it after Plasma is removed keeps KDE library packages installed. |
| 4 | Built into an all-in-one shell | Omarchy 4; DMS (built-in agent); Noctalia (switch on with `polkit_agent = true`). Quickshell 0.3.0 added support for this. | See job 0 | Graphical | `extra` | See job 0 | The Omarchy 4 route. Only applies if job 0 picks a shell. |

**How it works — read more:** hyprpolkitagent: [HW](https://wiki.hypr.land/Hypr-Ecosystem/hyprpolkitagent/) · [v0.2.0 notes](https://github.com/hyprwm/hyprpolkitagent/releases/tag/v0.2.0). All agents: [AW Polkit](https://wiki.archlinux.org/title/Polkit#Authentication_agents). Terminal note: polkit itself ships `pkttyagent` (present here at `/usr/bin/pkttyagent`), a text agent that asks for the password inside a terminal. Graphical apps still need one of the graphical agents above. Other agents on the AW list (lxqt-policykit, mate-polkit, soteria) have little Hyprland-specific evidence.
**Claude's lean:** hyprpolkitagent. Both wikis recommend it; polkit-gnome has been abandoned upstream since 2011. (A suggestion; Javier chooses.)

---

## 9. Login screen (display manager)
*What this job is:* The screen after boot where you type your password; it then starts Hyprland.
*Omarchy reference:* Omarchy 3 used SDDM with its own QML theme and automatic login; the disk-encryption password is the real gate ([O3 sddm.sh](https://github.com/basecamp/omarchy/blob/v3.8.4/install/login/sddm.sh)). Omarchy 4 still uses SDDM, but runs SDDM's own login screen on Hyprland (`DisplayServer=wayland`, `CompositorCommand=start-hyprland … hyprland.lua`, [O4 config](https://github.com/basecamp/omarchy/blob/v4.0.4/etc/sddm.conf.d/10-wayland.conf)).

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [SDDM](https://github.com/sddm/sddm) | A Qt login screen. It is what KognogOS ships now, with the custom `kognogos` theme (checked: `Current=kognogos`, and `sddm.service` is active). | Medium–Heavy (C++/Qt6; 5.3 MiB; the Arch package depends on `xorg-server`; on this desktop its login screen runs on X11, the package default) | Graphical | `extra/sddm 0.21.0-7` (installed) | ★2.4k · v0.21.0 2024-02 · commits 2026-08 | The HW [compatibility list](https://wiki.hypr.land/Getting-Started/Master-Tutorial/) says "SDDM: Works flawlessly" (version 0.20.0 or newer). Used by O3, O4 and HyDE; has its [own AW page](https://wiki.archlinux.org/title/SDDM). Catppuccin port: [catppuccin/sddm](https://github.com/catppuccin/sddm) (★529). |
| 2 | [ly](https://codeberg.org/fairyglade/ly) | A text-mode login screen that draws on the plain console. | Light (Zig; 1.9 MiB; 1 extra package) | Terminal | `extra/ly 1.4.1-1` | ★7.6k (GitHub mirror) + ★692 on Codeberg · v1.5.0-rc1 2026-08 | HW: "ly: Works flawlessly". Has its [own AW page](https://wiki.archlinux.org/title/Ly) and is on awesome-hyprland. Config is `/etc/ly/config.ini` (or `config.lua`). |
| 3 | [greetd](https://git.sr.ht/~kennylevinsen/greetd) + [tuigreet](https://github.com/tuigreet/tuigreet) | greetd is a tiny login service; tuigreet is a text-mode login screen for it. Session and username can be remembered. | Light (Rust; greetd 650 KiB + tuigreet 3.4 MiB) | Terminal | `extra/greetd 0.10.3-2` + `extra/greetd-tuigreet 0.11.1-2` | tuigreet ★1.8k · 0.11.1 2026-08; greetd ★260 (GitHub mirror) | HW: "greetd: Works flawlessly". Has its [own AW page](https://wiki.archlinux.org/title/Greetd); both are on awesome-hyprland. One config file, `/etc/greetd/config.toml`. A graphical greeter can be swapped in later without changing the service (ReGreet, noctalia-greeter, dank-greeter). |
| 4 | greetd + [ReGreet](https://github.com/rharish101/ReGreet) | A graphical GTK4 login screen for greetd. It runs inside a small helper compositor (Cage, Sway or Hyprland). | Medium (Rust/GTK4; 8.6 MiB) | Graphical | `extra/greetd-regreet 0.5.0-1` | ★825 · 0.5.0 2026-07 | HW: "greetd: Works flawlessly, especially with ReGreet". |
| 5 | No login manager: log in on the text console | Log in on the plain console; fish then runs `start-hyprland`. Automatic login is possible through the console's login program (getty). | Light (nothing extra) | Terminal | built in | n/a | The [HW tutorial](https://wiki.hypr.land/Getting-Started/Master-Tutorial/): "Hyprland can be executed by typing `start-hyprland` in your TTY". AW Hyprland ("Terminal") notes this wrapper "provides crash recovery and safe mode". |

**How it works — read more:** SDDM: [AW](https://wiki.archlinux.org/title/SDDM). ly: [AW](https://wiki.archlinux.org/title/Ly) · [project page](https://codeberg.org/fairyglade/ly). greetd + tuigreet: [AW Greetd](https://wiki.archlinux.org/title/Greetd) · [tuigreet README](https://github.com/tuigreet/tuigreet) · screenshots: [plain](https://github.com/tuigreet/tuigreet/blob/master/contrib/assets/screenshot.png), [themed](https://github.com/tuigreet/tuigreet/blob/master/contrib/assets/screenshot-themed.png). Also on the HW list: plasma-login-manager ("works flawlessly, but depends on systemd"; installed here now, but it belongs to Plasma) and GDM ("crashing Hyprland on the first launch"). Login screens matched to the shells: noctalia-greeter (AUR 1.6.0, ★410) and dank-greeter (AUR `greetd-dms-greeter-git`, ★37).
**Claude's lean:** greetd + tuigreet. It gives a terminal look, it is light, its config is one file hypeForge can write, and a graphical greeter can be swapped in later. SDDM stays the safe fallback because the KognogOS theme already exists, but it keeps Qt6 and the X11 server on the system. (A suggestion; Javier chooses.)

---

## 10. Clipboard history
*What this job is:* Remembers the last things you copied (text and pictures) so you can paste an older one.
*Omarchy reference:* Omarchy 3 used Walker's clipboard mode on Super+Ctrl+V ([O3 bindings](https://github.com/basecamp/omarchy/blob/v3.8.4/default/hypr/bindings/clipboard.conf)). Omarchy 4 has a clipboard manager inside the shell with picture previews, and it skips sensitive items such as one-time codes.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [cliphist](https://github.com/sentriz/cliphist) | Saves everything you copy (text, pictures, other data) using `wl-clipboard`. You pick from the history with any list-picker: fuzzel, rofi, or fzf in a terminal. | Light (Go; 2.4 MiB) | Terminal (command; the picker is separate) | `extra/cliphist 1:0.7.0-2` | ★1.6k · v0.7.0 2025-10 · commits 2026-09 | First on the [HW clipboard page](https://wiki.hypr.land/Useful-Utilities/Clipboard-Managers/) and AW Hyprland's example. Used by HyDE, ML4W and JaKooLit; listed on awesome-hyprland. |
| 2 | [CopyQ](https://github.com/hluk/CopyQ) | A full clipboard manager window with search, editing, tabs and scripting. | Heavy-ish (C++/Qt6 plus some KDE library packages; 8.7 MiB) | Graphical | `extra/copyq 16.0.0-1` (installed here) | ★12.3k · v16.0.0 2026-05 · commits 2026-09 | On the HW clipboard page, with very high stars. |
| 3 | [clipse](https://github.com/savedra1/clipse) | Clipboard history as a text-mode app you open in a floating terminal window. | Light (Go) | Terminal | `chaotic-aur/clipse 1.2.1-1` | ★1.0k · v1.2.1 2026-01 · commits 2026-06 | On the HW clipboard page, with a Lua key binding for a floating window. **Catch:** picture previews need a terminal that can show images (kitty or Sixel graphics). Alacritty has no built-in image support: the Sixel request [#910](https://github.com/alacritty/alacritty/issues/910) has been open since 2017, and the maintainer confirmed "there is no upstream support" in [#8891](https://github.com/alacritty/alacritty/issues/8891). So in Alacritty, only clipse's "basic" preview mode is available. |
| 4 | [clipvault](https://github.com/Rolv-Apneseth/clipvault) | An alternative to cliphist with limits: maximum age, maximum number of entries, minimum length. | Light (Rust) | Terminal | AUR only (`clipvault 1.3.0-1`) | ★118 · v1.3.0 2026-07 | On the HW clipboard page and awesome-hyprland. |
| 5 | Built into an all-in-one shell | Omarchy 4; Noctalia (`clipboard_enabled`, keeps copied items alive after the app closes); DMS (history with picture previews). | See job 0 | Graphical | `extra` | See job 0 | The Omarchy 4 route. Only applies if job 0 picks a shell. |

**How it works — read more:** cliphist: [HW](https://wiki.hypr.land/Useful-Utilities/Clipboard-Managers/) · [AW Hyprland, Clipboard](https://wiki.archlinux.org/title/Hyprland). clipse: [README](https://github.com/savedra1/clipse). CopyQ: [docs](https://hluk.github.io/CopyQ/). Helper: `extra/wl-clip-persist 0.5.0-2` keeps copied text pasteable after the app you copied from closes (HW; used by HyDE).
**Claude's lean:** cliphist, with fuzzel as the picker. It is the best-documented option, tiny, in `extra`, and works with any picker. (A suggestion; Javier chooses.)

---

## 11. Screenshots (and annotation)
*What this job is:* Captures the whole screen, one window or a dragged area, and optionally lets you draw arrows or boxes on it before saving or pasting.
*Omarchy reference:* Omarchy 3 used grim + slurp + Satty, freezing the screen with hyprpicker while you aim ([O3 script](https://github.com/basecamp/omarchy/blob/v3.8.4/bin/omarchy-capture-screenshot)). Omarchy 4 still uses grim + slurp but switched the drawing editor from Satty to Tensaku (Rust, AUR only, ★94) ([O4 manual](https://github.com/basecamp/omarchy/blob/v4.0.4/manual/12-screenshots-recording.md)).

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [grim](https://gitlab.freedesktop.org/emersion/grim) + [slurp](https://github.com/emersion/slurp) | grim takes the picture; slurp lets you drag a box. Almost every setup builds on these two. | Light (C; 46 KiB + 39 KiB) | Terminal (commands bound to keys) | `extra/grim 1.5.0-2` + `extra/slurp 1.5.0-2` | slurp ★1.3k · v1.5.0 2023-12 · commits 2026-05; grim v1.5.0 2025-07 (freedesktop GitLab, no comparable star count) | On the [HW screenshots page](https://wiki.hypr.land/Useful-Utilities/Screenshots-and-Recording/) and [AW Screen capture (Wayland)](https://wiki.archlinux.org/title/Screen_capture#Wayland). Used by O3, O4, HyDE, ML4W and JaKooLit. |
| 2 | [Satty](https://github.com/Satty-org/Satty) | A modern editor for drawing on a screenshot: arrows, boxes, text, blur. | Medium (Rust/GTK4; 5.6 MiB) | Graphical | `extra/satty 0.22.0-1` | ★2.4k · v0.22.0 2026-08 · commits 2026-09 | On the HW screenshots page ("almost drop-in replacement for swappy"). O3's editor; used by HyDE; listed on awesome-hyprland. |
| 3 | [swappy](https://github.com/jtheoof/swappy) | An older, smaller drawing editor. | Light (C/GTK3; 124 KiB) | Graphical | `extra/swappy 1.8.0-1` | ★1.5k · v1.8.0 2025-08 · commits 2025-12 | On the HW screenshots page and AW Screen capture. Used by JaKooLit, and Caelestia depends on it. Listed on awesome-hyprland. |
| 4 | [grimblast](https://github.com/hyprwm/contrib/tree/main/grimblast) / [Hyprshot](https://github.com/Gustash/Hyprshot) | Ready-made scripts around grim + slurp with "area / window / monitor" modes for Hyprland. | Light (shell scripts) | Terminal | Hyprshot `extra/hyprshot 1.3.0-4`; grimblast `chaotic-aur/grimblast-git` | Hyprshot ★887 · 1.3.0 2024-06; hyprwm/contrib ★402 · commits 2026-08 | Both are on awesome-hyprland; ML4W installs grimblast. grimblast has already been updated for Lua (it uses `hyprctl eval`). Hyprshot only reads Hyprland's status (`hyprctl -j …`). |
| 5 | [Flameshot](https://flameshot.org/) | An all-in-one screenshot app with drawing built in. | Medium (C++/Qt6; 3.3 MiB) | Graphical | `extra/flameshot 14.0.0-1` | ★31.0k · v14.0.0 2026-06 | On the HW screenshots page, with a warning: "relies on portal support… if it cannot capture the screen… use grim with swappy instead". Has its [own AW page](https://wiki.archlinux.org/title/Flameshot). |

**How it works — read more:** grim + slurp: [AW Screen capture](https://wiki.archlinux.org/title/Screen_capture#Wayland) · [HW examples](https://wiki.hypr.land/Useful-Utilities/Screenshots-and-Recording/). Satty: [README](https://github.com/Satty-org/Satty). grimblast: [script](https://github.com/hyprwm/contrib/tree/main/grimblast). The all-in-one shells have their own screenshot tools too: Noctalia has a region overlay with an editor, and DMS has `dms screenshot`.
**Claude's lean:** grim + slurp + Satty. This is Omarchy 3's proven trio and all three are in `extra`; a small hypeForge script (or grimblast) chooses area, window or monitor. (A suggestion; Javier chooses.)

---

## 12. Screen recording
*What this job is:* Records the screen, or part of it, to a video file.
*Omarchy reference:* Omarchy 3 and Omarchy 4 both use gpu-screen-recorder. Omarchy 4 adds a recording indicator in the bar, a webcam overlay, and a clean-up step when you stop. Both also install OBS Studio.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [gpu-screen-recorder](https://git.dec05eba.com/gpu-screen-recorder/about/) | Records using only the graphics card, "a shadowplay-like screen recorder". A command, with an optional window app. | Light (C/C++; 505 KiB, uses ffmpeg libraries) | Terminal (optional graphical `gpu-screen-recorder-ui`) | `extra/gpu-screen-recorder 6.1.3-1` (+ `extra/gpu-screen-recorder-ui 1.13.10-1`) | Self-hosted, so no GitHub stars · v6.1.3 (Arch build 2026-09) | Used by O3 and O4 (O4 manual: "encodes on the GPU at 60fps and falls back to the CPU"). On the HW recording list and [AW Screen capture](https://wiki.archlinux.org/title/Screen_capture). Supports NVIDIA on Wayland. The project FAQ says capturing through the desktop "portal" (the desktop's screen-sharing permission layer) on Hyprland gives low frame rates, so record the monitor directly; Omarchy also turns portal mode off by default. |
| 2 | [OBS Studio](https://obsproject.com/) | A full recording and streaming studio. | Heavy (C/Qt6; 24.7 MiB + ffmpeg) | Graphical | `extra/obs-studio 32.2.2-1` | ★76.7k · 32.2.2 2026-08 | On the HW recording list, AW Screen capture and its [own AW page](https://wiki.archlinux.org/title/Open_Broadcaster_Software). Installed by O3 and O4. |
| 3 | [wf-recorder](https://github.com/ammen99/wf-recorder) | A tiny command-line recorder, "like grim but records video". | Light (C++; 122 KiB + ffmpeg) | Terminal | `extra/wf-recorder 0.6.0-2` | ★1.3k · v0.6.0 2025-10 · commits 2026-04 | On the HW, AW Screen capture and awesome-hyprland. **NVIDIA catch:** its documented GPU path is VA-API (a standard way for apps to use the graphics card for video), and NVIDIA's VA-API driver says "hardware decoding only, encoding is not supported" ([nvidia-vaapi-driver](https://github.com/elFarto/nvidia-vaapi-driver)). On the RTX 3060 it would encode on the CPU; its default is libx264. |
| 4 | [Kooha](https://github.com/SeaDve/Kooha) | A simple recorder window with a start/stop button. | Medium (Rust/GTK4; 2.5 MiB + GStreamer) | Graphical | `extra/kooha 2.3.2-3` | ★3.5k · v2.3.2 2026-06 · commits 2026-09 | On AW Screen capture ("Simple screen recorder with a minimal GTK interface"). |
| 5 | [wl-screenrec](https://github.com/rosalyntg/wl-screenrec) | An efficient recorder that encodes on the graphics card through VA-API. | Light (Rust) | Terminal | `chaotic-aur/wl-screenrec 0.3.2-2` | ★630 · v0.3.1 2026-08 · commits 2026-09 | On the HW recording list and awesome-hyprland ("for AMD and Intel GPUs"). AW: use it "if your GPU supports vaapi encoding". **Not for this NVIDIA card**, for the same VA-API reason as wf-recorder. |

**How it works — read more:** gpu-screen-recorder: [project page and FAQ](https://git.dec05eba.com/gpu-screen-recorder/about/). OBS: [AW](https://wiki.archlinux.org/title/Open_Broadcaster_Software). wf-recorder: [README](https://github.com/ammen99/wf-recorder). All options: [AW Screen capture](https://wiki.archlinux.org/title/Screen_capture).
**Claude's lean:** gpu-screen-recorder. It encodes on the RTX 3060 itself, Omarchy 3 and 4 both use it, and it runs from a key binding without opening a window. (A suggestion; Javier chooses.)

---

## 13. Look of GTK and Qt apps + mouse cursor
*What this job is:* Makes GTK apps (most Linux apps), Qt apps (KDE-style apps) and the mouse pointer all use Catppuccin Mocha instead of clashing styles.
*Omarchy reference:* Omarchy 3 set GTK to Adwaita-dark with Yaru icons using `gsettings`, and styled Qt apps with Kvantum (`QT_STYLE_OVERRIDE=kvantum`, [O3 envs](https://github.com/basecamp/omarchy/blob/v3.8.4/default/hypr/envs.conf)). Omarchy 4 keeps the gsettings part, drops Kvantum, and tells Qt apps to follow the GTK theme (`QT_QPA_PLATFORMTHEME=gtk3`, [O4 envs.lua](https://github.com/basecamp/omarchy/blob/v4.0.4/default/hypr/envs.lua)). Both set only the cursor size (24).

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [nwg-look](https://github.com/nwg-piotr/nwg-look) | A small settings window for GTK theme, icons, cursor and fonts on Hyprland-type desktops. | Medium (Go/GTK3; 4.9 MiB) | Graphical | `extra/nwg-look 1.1.1-3` | ★1.0k · v1.1.1 2026-05 · commits 2026-07 | Used by ML4W, HyDE and JaKooLit; Noctalia's docs recommend it. hypeForge could skip the window and run the same `gsettings` commands directly, which is what Omarchy does. **Today on this desktop:** GTK uses Plasma's `Breeze` theme, `candy-icons` and `breeze_cursors` (checked with `gsettings`). These go away with Plasma. |
| 2 | [qt6ct](https://www.opencode.net/trialuser/qt6ct) + qt5ct | Settings windows for Qt 6 / Qt 5 apps: style, colours, fonts, icons. | Light (C++/Qt; 690 KiB) | Graphical | `extra/qt6ct 0.11-8`, `extra/qt5ct 1.9-2` (also `chaotic-aur/qt6ct-kde` for KDE apps) | The GitHub repo was archived in 2024 and development moved to opencode.net (Arch 0.11 built 2026-08) | Used by HyDE, ML4W and JaKooLit; covered by [AW Uniform look](https://wiki.archlinux.org/title/Uniform_look_for_Qt_and_GTK_applications). AW Hyprland suggests `qt6ct-kde` for KDE apps. The Hyprland team's replacement, [hyprqt6engine](https://wiki.hypr.land/Hypr-Ecosystem/hyprqt6engine/), is configured by a file and reads KDE colour schemes (AUR only, ★100). |
| 3 | [Kvantum](https://github.com/tsujan/Kvantum) | A theme engine for Qt apps; a Catppuccin Kvantum theme exists. | Medium (C++/Qt6; 8.6 MiB) | Graphical (kvantummanager) or config file | `extra/kvantum 1.1.8-1` (installed); Catppuccin theme is AUR `kvantum-theme-catppuccin-git` (last updated 2024-06) | ★2.0k · V1.1.8 2026-05 | Used by O3, HyDE and JaKooLit; covered by AW Uniform look. |
| 4 | "Qt follows GTK" (QGtk3Style) | One setting, `QT_QPA_PLATFORMTHEME=gtk3`, makes Qt apps borrow the GTK theme. It is built into `qt6-base`. | Light (nothing to install) | config only | part of `qt6-base` | n/a | Omarchy 4's method; AW Uniform look ("QGtk3Style"). |
| 5 | [hyprcursor](https://wiki.hypr.land/Hypr-Ecosystem/hyprcursor/) + [Catppuccin Mocha cursors](https://github.com/catppuccin/cursors) (cursor) | Hyprland's own cursor format. The Catppuccin cursors ship both hyprcursor and classic XCursor versions. | Light | config only | `extra/hyprcursor 0.1.13-7`; `chaotic-aur/catppuccin-cursors-mocha 2.0.0-1` (already installed; checked that it contains `hyprcursors/` files) | cursors ★755 · v2.0.0 2024-12 ("implement nominal_size metadata for hyprcursor"); hyprcursor ★576 | On the HW hyprcursor page and AW Hyprland ("Hyprcursor"). The HW notes GTK apps still need `XCURSOR_THEME` + `gsettings … cursor-theme`. |

**How it works — read more:** GTK + Qt: [AW Uniform look](https://wiki.archlinux.org/title/Uniform_look_for_Qt_and_GTK_applications) · [AW GTK](https://wiki.archlinux.org/title/GTK). Kvantum: [README](https://github.com/tsujan/Kvantum). Cursor: [HW hyprcursor](https://wiki.hypr.land/Hypr-Ecosystem/hyprcursor/) · [AW Cursor themes](https://wiki.archlinux.org/title/Cursor_themes).
- **Catppuccin for GTK:** the official [catppuccin/gtk](https://github.com/catppuccin/gtk) theme is **archived** (June 2024: "a nightmare to consistently theme and maintain").
- **What still works:** [adw-gtk3](https://github.com/lassekongo83/adw-gtk3) (`extra/adw-gtk-theme 6.5-1`, ★2.1k), which "can be customized with GTK named colors". Its companion colour collection has no Catppuccin file (checked), so hypeForge would ship its own small colour file.

**Claude's lean:**
- *GTK:* adw-gtk3 plus a Catppuccin Mocha colour file.
- *Qt:* follow GTK (the Omarchy 4 route), or hyprqt6engine if Qt apps need their own colours.
- *Cursor:* the Catppuccin Mocha cursors that are already installed.

Everything is set by files and commands hypeForge writes, with no settings windows needed. (A suggestion; Javier chooses.)

---

---

# Part 2 · The tools you use

## 14. File manager (terminal first, plus one graphical fallback)
*What this job is:* Browsing, copying, moving and opening your files and folders.
*Omarchy reference:* Omarchy 3 used Nautilus, GNOME's point-and-click file manager (`SUPER+SHIFT+F`), with no terminal file manager installed; Omarchy 4 still uses Nautilus.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [Yazi](https://yazi-rs.github.io/) | A fast file manager that runs inside the terminal, with file previews | Light (Rust) | Terminal | extra/yazi 26.9.1-2 | ★42.5k · release 2026-09 | Listed on the [Hyprland wiki](https://wiki.hypr.land/Useful-Utilities/File-Managers/) and the [Arch list](https://wiki.archlinux.org/title/List_of_applications/Utilities#File_managers). The most-starred option here. Official Catppuccin Mocha theme ([yazi-rs/flavors](https://github.com/yazi-rs/flavors)) and an official [USB mount plugin](https://github.com/yazi-rs/plugins/tree/main/mount.yazi). Alacritty cannot draw pictures itself, so picture previews need Überzug++ (`extra/ueberzugpp` 2.9.10) ([Yazi docs](https://yazi-rs.github.io/docs/image-preview)). |
| 2 | [superfile](https://superfile.dev/) | A colourful terminal file manager with side-by-side panels | Light (Go) | Terminal | extra/superfile 1.6.0-1 | ★23.4k · release 2026-06 | [Hyprland wiki](https://wiki.hypr.land/Useful-Utilities/File-Managers/) and the Arch list; official [Catppuccin theme](https://github.com/catppuccin/superfile). |
| 3 | [nnn](https://github.com/jarun/nnn) | A tiny, very fast terminal file manager | Light (C, 0.4 MB) | Terminal | extra/nnn 5.3-1 | ★22.0k · release 2026-08 | [Hyprland wiki](https://wiki.hypr.land/Useful-Utilities/File-Managers/); has its own [Arch Wiki page](https://wiki.archlinux.org/title/Nnn). Minimal by design, so it needs more setup to feel friendly. |
| 4 | [ranger](https://ranger.github.io/) | A long-established terminal file manager with three columns and previews | Light (Python) | Terminal | extra/ranger 1.9.4-5 | ★17.4k · release 2024-11 (commits 2026-09) | [Hyprland wiki](https://wiki.hypr.land/Useful-Utilities/File-Managers/); [Arch Wiki page](https://wiki.archlinux.org/title/Ranger). Releases have slowed down. |
| 5 | [Thunar](https://docs.xfce.org/xfce/thunar/start) (graphical fallback) | Xfce's point-and-click file manager | Light (C, GTK3) | Graphical | extra/thunar 4.20.10-1 (**installed**) | Xfce GitLab (copy ★278) · Arch pkg 2026-09 | Hyprland wiki graphical list. The [Arch Hyprland page](https://wiki.archlinux.org/title/Hyprland#File_manager) uses it as its example, and JaKooLit ships it. The Arch list praises its "excellent start-up and directory load times". It needs `gvfs` (not installed) to show drives and use the Trash ([Arch](https://wiki.archlinux.org/title/File_manager_functionality#Mounting)). The other graphical choices are Dolphin (installed; used by HyDE and end-4; keeps KDE libraries around) and Nautilus (Omarchy, ML4W; Arch calls it "heavyweight"). |

**How it works — read more:** Yazi: [site](https://yazi-rs.github.io/) · [image previews](https://yazi-rs.github.io/docs/image-preview) · superfile: [site](https://superfile.dev/) · nnn: [Arch Wiki](https://wiki.archlinux.org/title/Nnn) · ranger: [Arch Wiki](https://wiki.archlinux.org/title/Ranger) · Thunar: [Arch Wiki](https://wiki.archlinux.org/title/Thunar) · [Xfce docs](https://docs.xfce.org/xfce/thunar/start)
**Claude's lean:** Yazi + Thunar. Yazi is the most-used terminal option and comes with a Catppuccin Mocha theme and a USB plugin. Thunar is already installed and light; it only needs `gvfs` added. (A suggestion; Javier chooses.)

## 15. Wi-Fi and network settings
*What this job is:* Choosing a Wi-Fi network, typing its password, and checking the wired connection.
*Omarchy reference:* Omarchy 3 used impala, a terminal Wi-Fi app that only works with iwd, a different Wi-Fi service ([impala asks you to disable NetworkManager](https://github.com/pythops/impala)); Omarchy 4 does it with NetworkManager and its own Network panel in its Quickshell bar (`SUPER+CTRL+W`).

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [nmtui](https://wiki.archlinux.org/title/NetworkManager#nmtui) | NetworkManager's own menu screen inside the terminal | Light (C) | Terminal | part of extra/networkmanager 1.58.1-1 (**installed**) | NetworkManager copy ★508 · commit 2026-09 | It ships with NetworkManager ([Arch](https://wiki.archlinux.org/title/NetworkManager#nmtui): it manages "connections, the system hostname and radio switches"). Nothing new to install. Its weak spot is that it cannot start a fresh Wi-Fi scan ([wifitui README](https://github.com/shazow/wifitui)). |
| 2 | [nm-applet + nm-connection-editor](https://gitlab.gnome.org/GNOME/network-manager-applet) | GNOME's tray icon for NetworkManager, plus a settings window | Light (C, GTK3) | Graphical (tray icon) | extra/network-manager-applet 1.36.0-2, extra/nm-connection-editor 1.36.0-2 (**both installed**) | GNOME GitLab (copy ★17) · Arch pkg 2026-04 | On the [Hyprland wiki "Other" page](https://wiki.hypr.land/Useful-Utilities/Other/); shipped by HyDE, JaKooLit and ML4W. [Arch](https://wiki.archlinux.org/title/NetworkManager#nm-applet) notes that an applet also "provides the agent necessary for securely storing secrets". It needs a bar with a tray area to show its icon. |
| 3 | [networkmanager-dmenu](https://github.com/firecat53/networkmanager-dmenu) | A pop-up list of networks shown through rofi, which is already installed | Light (Python, 60 KB) | Graphical (pop-up menu) | extra/networkmanager-dmenu 2.6.3-1 | ★998 · release 2026-09 (v2.7.2; Arch still has 2.6.3) | [Arch Wiki](https://wiki.archlinux.org/title/NetworkManager#networkmanager-dmenu): connects to Wi-Fi, wired and VPN networks, asks for passwords, and opens nm-connection-editor. Works with rofi, fuzzel, wofi and walker ([README](https://github.com/firecat53/networkmanager-dmenu)). |
| 4 | [wifitui](https://github.com/shazow/wifitui) | A friendly terminal Wi-Fi app | Light (Go) | Terminal | AUR only (`wifitui` / `wifitui-bin` 0.13.0) | ★341 · release 2026-04 | [Arch Wiki](https://wiki.archlinux.org/title/NetworkManager#wifitui): "inspired by impala and is similar to nmtui, but can scan wifi-networks directly". Its [README](https://github.com/shazow/wifitui) says it "works with NetworkManager over dbus". A small project, and AUR only. |

**How it works — read more:** nmtui: [Arch Wiki](https://wiki.archlinux.org/title/NetworkManager#nmtui) · nm-applet: [Arch Wiki](https://wiki.archlinux.org/title/NetworkManager#nm-applet) · networkmanager-dmenu: [README](https://github.com/firecat53/networkmanager-dmenu) · wifitui: [README](https://github.com/shazow/wifitui)
**Claude's lean:** nmtui. It is already installed, and the home Wi-Fi keeps working without Plasma because its password is stored system-wide. Add networkmanager-dmenu if a one-key rofi Wi-Fi picker is wanted. (A suggestion; Javier chooses.)

## 16. Bluetooth
*What this job is:* Pairing and connecting headphones, keyboards, game controllers and phones. (The adapter `hci0` is present and `bluetooth.service` is enabled here.)
*Omarchy reference:* Omarchy 3 used bluetui, a terminal app (`SUPER+CTRL+B`); Omarchy 4 does it with its own Bluetooth panel in the Quickshell bar (same key). Plasma used Bluedevil, which is part of the `plasma` group.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [bluetui](https://github.com/pythops/bluetui) | A terminal app to scan, pair and connect Bluetooth devices | Light (Rust) | Terminal | extra/bluetui 0.8.1-2 | ★3.0k · release 2026-01 | Omarchy 3's choice (its `omarchy-launch-bluetooth` script ran it); in the [Arch Wiki console list](https://wiki.archlinux.org/title/Bluetooth#Console). |
| 2 | [Blueman](https://github.com/blueman-project/blueman) | A full Bluetooth manager window with a tray icon | Medium (Python, GTK3, 7 MB) | Graphical | extra/blueman 2.4.6-2 | ★1.6k · release 2025-07 | Shipped by HyDE, JaKooLit and ML4W. Has its own [Arch Wiki page](https://wiki.archlinux.org/title/Blueman), which calls it "a full featured Bluetooth manager". |
| 3 | [bluetuith](https://github.com/bluetuith-org/bluetuith) | A terminal Bluetooth manager that can also send and receive files | Light (Go) | Terminal | AUR only (`bluetuith` 0.2.7) | ★1.4k · release 2026-07 | In the [Arch Wiki console list](https://wiki.archlinux.org/title/Bluetooth#Console); its README lists file transfer and pairing prompts. |
| 4 | [Overskride](https://github.com/kaii-lb/overskride) | A modern, simple Bluetooth window | Medium (Rust, GTK4) | Graphical | AUR only (`overskride` 0.6.6) | ★913 · release 2026-01 | Listed on the [Hyprland wiki "Other" page](https://wiki.hypr.land/Useful-Utilities/Other/) and in Arch's graphical list. |
| 5 | [bluetoothctl](https://wiki.archlinux.org/title/Bluetooth#Pairing) | The basic Bluetooth command you type in a terminal | Light (C) | Terminal (commands) | part of extra/bluez-utils 5.87-2 (**installed**) | BlueZ project · Arch 5.87 | [Arch Wiki](https://wiki.archlinux.org/title/Bluetooth#Console): "one of the simplest and most reliable options". Useful as a backup even if another tool is picked. |

**How it works — read more:** bluetui: [README](https://github.com/pythops/bluetui) · Blueman: [Arch Wiki](https://wiki.archlinux.org/title/Blueman) · bluetuith: [README](https://github.com/bluetuith-org/bluetuith) · Overskride: [README](https://github.com/kaii-lb/overskride) · bluetoothctl: [Arch Wiki](https://wiki.archlinux.org/title/Bluetooth#Pairing)
**Claude's lean:** bluetui. It is a terminal app, it is in the official repos, and Omarchy 3 used it. bluetoothctl is already here as a fallback. (A suggestion; Javier chooses.)

## 17. Sound mixer and output switching
*What this job is:* Changing the volume of each app, and choosing speakers, headphones or HDMI.
*Omarchy reference:* Omarchy 3 used wiremix, a terminal mixer (`SUPER+CTRL+A`); Omarchy 4 does it with its own Audio panel (volume slider, output picker, per-app mixer). Plasma used plasma-pa, which is in the `plasma` group.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [wiremix](https://github.com/tsowell/wiremix) | A terminal mixer: volume per app, send sound to another device, pick the default output | Light (Rust) | Terminal | extra/wiremix 0.11.0-1 | ★1.1k · release 2026-06 | Omarchy 3's choice; listed as a [PipeWire TUI in the Arch Wiki](https://wiki.archlinux.org/title/PipeWire#TUI). Works with the mouse too ([README](https://github.com/tsowell/wiremix)). |
| 2 | [pavucontrol](https://freedesktop.org/software/pulseaudio/pavucontrol/) | The classic volume-control window | Light (C, GTK4, 1 MB) | Graphical | extra/pavucontrol 1:6.2-1 | copy ★144 · Arch pkg 2025-09 | Shipped by HyDE, JaKooLit and ML4W; end-4 uses its Qt twin. In the [Arch front-end list](https://wiki.archlinux.org/title/PulseAudio#Front-ends). |
| 3 | [pwvucontrol](https://github.com/saivert/pwvucontrol) | A newer volume window that talks to PipeWire (the sound system) directly | Medium (Rust, GTK4 + libadwaita) | Graphical | chaotic-aur/pwvucontrol 0.5.3-2 (AUR) | ★701 · release 2026-07 | In the [Arch Wiki PipeWire GUI list](https://wiki.archlinux.org/title/PipeWire#GUI), described as an "alternative to pavucontrol". |
| 4 | [hyprpwcenter](https://github.com/hyprwm/hyprpwcenter) | Hyprland's own sound control centre | Light (C++, Hyprland's toolkit) | Graphical | extra/hyprpwcenter 0.1.2-9 | ★150 · release 2026-02 | An official Hyprland app ([wiki page](https://wiki.hypr.land/Hypr-Ecosystem/hyprpwcenter/)). Young (version 0.1). |

**How it works — read more:** wiremix: [README](https://github.com/tsowell/wiremix) · pavucontrol: [Arch Wiki](https://wiki.archlinux.org/title/PulseAudio#Front-ends) · pwvucontrol: [README](https://github.com/saivert/pwvucontrol) · hyprpwcenter: [Hyprland wiki](https://wiki.hypr.land/Hypr-Ecosystem/hyprpwcenter/) · all: [Arch PipeWire](https://wiki.archlinux.org/title/PipeWire)
**Claude's lean:** wiremix. It is a terminal app in the official repos and was Omarchy 3's choice. The volume keys can use `wpctl`, which comes with WirePlumber and is already installed. (A suggestion; Javier chooses.)

## 18. System monitor (with an NVIDIA graphics-card view)
*What this job is:* Seeing what is using the processor, memory, disk, network and graphics card, and stopping a stuck program.
*Omarchy reference:* Omarchy 3 used btop (`SUPER+CTRL+T`); Omarchy 4 still ships btop on the same key, plus a Power panel with "system stats".

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [btop](https://github.com/aristocratos/btop) | A colourful all-in-one monitor that can also show the graphics card | Light (C++) | Terminal | extra/btop 1.4.7-1 (**installed**) | ★34.8k · release 2026-05 | Used by Omarchy 3 & 4, JaKooLit and ML4W; in the [Arch list](https://wiki.archlinux.org/title/List_of_applications/Utilities#System_monitors); official [Catppuccin theme](https://github.com/catppuccin/btop). **GPU:** the installed btop is built to use NVIDIA's monitoring library (`libnvidia-ml`), which is present here with driver 615.71.09. Press `5` to show the GPU box ([README](https://github.com/aristocratos/btop)). |
| 2 | [htop](https://htop.dev/) | The long-standing simple process list | Light (C, 0.4 MB) | Terminal | extra/htop 3.5.3-1 (**installed**) | ★8.4k · release 2026-08 | Shipped by ML4W; in the [Arch list](https://wiki.archlinux.org/title/List_of_applications/Utilities#System_monitors). |
| 3 | [nvtop](https://github.com/Syllo/nvtop) | A monitor just for the graphics card, showing which programs use it | Light (C, 0.2 MB) | Terminal | extra/nvtop 3.3.2-1 | ★11.0k · release 2026-02 | Shipped by JaKooLit. Its README lists NVIDIA support through NVIDIA's monitoring library. The best per-program GPU view. |
| 4 | [Glances](https://nicolargo.github.io/glances/) | An everything-at-a-glance monitor | Medium (Python) | Terminal | extra/glances 4.5.7-1 | ★33.7k · release 2026-09 | In the [Arch list](https://wiki.archlinux.org/title/List_of_applications/Utilities#System_monitors); many stars. Heavier because it is written in Python. |
| 5 | [bottom](https://github.com/ClementTsang/bottom) | A graph-style monitor | Light (Rust) | Terminal | extra/bottom 0.14.9-1 | ★14.1k · release 2026-08 | In the [Arch list](https://wiki.archlinux.org/title/List_of_applications/Utilities#System_monitors); official [Catppuccin theme](https://github.com/catppuccin/bottom). |

**How it works — read more:** btop: [README (GPU section)](https://github.com/aristocratos/btop) · htop: [site](https://htop.dev/) · nvtop: [README](https://github.com/Syllo/nvtop) · Glances: [site](https://nicolargo.github.io/glances/) · bottom: [README](https://github.com/ClementTsang/bottom) · NVIDIA's own `nvidia-smi` command (installed): [Arch Wiki](https://wiki.archlinux.org/title/NVIDIA/Tips_and_tricks#nvidia-smi)
**Claude's lean:** btop, with nvtop added. btop is already installed and built to show the RTX 3060; nvtop adds a per-program graphics view. (A suggestion; Javier chooses.)

## 19. Arranging three monitors
*What this job is:* Telling Hyprland where each screen sits and its resolution, refresh rate (144 Hz) and scale.
*Omarchy reference:* Omarchy 3 had you edit `~/.config/hypr/monitors.conf` by hand; Omarchy 4 has you edit `monitors.lua` by hand, and its Display panel only covers brightness and laptop-screen controls. On Plasma this was KScreen, which is in the `plasma` group.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [Hyprland's own monitor rules](https://wiki.hypr.land/Configuring/Basics/Monitors/) | One `hl.monitor({...})` line per screen in the Lua config: name, mode, position, scale | Light (built in) | Config file (hypeForge could write it) | part of extra/hyprland 0.56.2-3 | Hyprland ★38.7k · release 2026-08 | The official method (see the [Hyprland wiki](https://wiki.hypr.land/Configuring/Basics/Monitors/) and [Arch](https://wiki.archlinux.org/title/Hyprland#Setting_screen_resolution)), and what Omarchy 3 & 4 use. Every tool below writes these same rules. `hyprctl monitors all` lists the available modes. |
| 2 | [nwg-displays](https://github.com/nwg-piotr/nwg-displays) | Drag your screens into place in a window, then save | Light (Python, GTK3, 0.5 MB) | Graphical | extra/nwg-displays 0.4.4-1 | ★1.1k · release 2026-08 | The [Arch Hyprland page's "Settings GUI"](https://wiki.archlinux.org/title/Hyprland#Settings_GUI). Shipped by HyDE, JaKooLit and ML4W. **Lua-ready:** since v0.4.3 it writes `~/.config/hypr/monitors.lua` for Hyprland 0.55+ ([releases](https://github.com/nwg-piotr/nwg-displays/releases)). |
| 3 | [hyprmon](https://github.com/erans/hyprmon) | A terminal "desk map" where you arrange screens with the keyboard or mouse | Light (Go) | Terminal | AUR only (`hyprmon-bin` 0.0.17; the AUR package named `hyprmon` is a different project) | ★517 · release 2026-05 | Made for Hyprland. Since v0.0.16 it writes `~/.config/hypr/hyprmon.lua` and adds a line to `hyprland.lua` that loads it ([README](https://github.com/erans/hyprmon)). Young (version 0.0.x). |
| 4 | [Monique](https://github.com/ToRvaLDz/monique) | A drag-and-drop monitor window with saved profiles | Medium (Python, GTK4 + libadwaita) | Graphical | AUR only (`monique` 0.8.2) | ★195 · release 2026-09 | Listed on [awesome-hyprland](https://github.com/hyprland-community/awesome-hyprland) (Display). Lua output was added in May 2026 ([issue #33](https://github.com/ToRvaLDz/monique/issues/33)). |

**How it works — read more:** rules: [Hyprland wiki: monitors](https://wiki.hypr.land/Configuring/Basics/Monitors/) · [modes](https://wiki.hypr.land/configuring/core/monitors/modes/) · nwg-displays: [README](https://github.com/nwg-piotr/nwg-displays) · hyprmon: [README](https://github.com/erans/hyprmon) · Monique: [README](https://github.com/ToRvaLDz/monique)
**Claude's lean:** hypeForge writes the three rules itself, with the exact mode `2560x1440@144` and fixed positions, rather than the wiki's `preferred` mode ("the display's preferred size and refresh rate", which may not be 144 Hz). Ship nwg-displays as the visual fallback: it is in the official repos and understands the Lua config. (A suggestion; Javier chooses.)

## 20. Night light (blue-light filter)
*What this job is:* Warming the screen colours in the evening. (Plasma's Night Light was off on this machine, so this is a new feature, not a replacement.)
*Omarchy reference:* Omarchy 3 used hyprsunset with a toggle key (`SUPER+CTRL+N`); Omarchy 4 still uses hyprsunset, shows its state on the bar, and re-sends the setting at start-up until it takes effect.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [hyprsunset](https://github.com/hyprwm/hyprsunset) | Hyprland's own blue-light filter, with times set in a small file | Light (C++, 0.26 MB) | Background (no window; `hyprctl hyprsunset …` commands) | extra/hyprsunset 0.4.0-3 | ★483 · release 2026-07 | The official app. The [Hyprland wiki](https://wiki.hypr.land/Hypr-Ecosystem/hyprsunset/) prefers it over screen shaders because it "will not be captured via recording/screenshots". Used by Omarchy 3 & 4, HyDE, ML4W and end-4. On NVIDIA, Hyprland automatically skips only the fade animation ([config options: `ctm_animation`](https://github.com/hyprwm/hyprland-wiki/blob/main/content/configuring/core/config-options.md)). |
| 2 | [gammastep](https://gitlab.com/chinstrap/gammastep) | Shifts colour temperature by the time of day and your location | Light (C) | Background | extra/gammastep 2.0.11-2 | GitLab (no GitHub stars) · Arch pkg 2026-01 | Listed on the [Hyprland wiki "Other" page](https://wiki.hypr.land/Useful-Utilities/Other/); has an [Arch Wiki page](https://wiki.archlinux.org/title/Gammastep). |
| 3 | [wlsunset](https://sr.ht/~kennylevinsen/wlsunset/) | A tiny day/night colour changer for Wayland | Light (C, 32 KB) | Background | extra/wlsunset 0.4.0-1 | sourcehut (no stars) · Arch pkg 2024-04 | In [awesome-hyprland](https://github.com/hyprland-community/awesome-hyprland) (Display). Little recent activity. |
| 4 | [hyprshade](https://github.com/loqusion/hyprshade) | Applies screen "shaders" (colour filters), on a schedule if wanted | Light (Python) | Background / terminal | chaotic-aur/hyprshade 5.0.0-1 (AUR) | ★569 · release 2026-06 | On the [Hyprland wiki "Other" page](https://wiki.hypr.land/Useful-Utilities/Other/). Because it uses shaders, the filter shows up in screenshots, which is why the wiki prefers hyprsunset. |

**How it works — read more:** hyprsunset: [Hyprland wiki](https://wiki.hypr.land/Hypr-Ecosystem/hyprsunset/) · gammastep: [Arch Wiki](https://wiki.archlinux.org/title/Gammastep) · wlsunset: [project](https://sr.ht/~kennylevinsen/wlsunset/) · hyprshade: [README](https://github.com/loqusion/hyprshade)
**Claude's lean:** hyprsunset. It is the official app, tiny, keeps its schedule inside `~/.config/hypr`, and stays out of screenshots. It is optional, since Night Light was off on Plasma. (A suggestion; Javier chooses.)

## 21. Colour picker
*What this job is:* Clicking any dot on the screen to copy its colour code (such as `#1e1e2e`).
*Omarchy reference:* Omarchy 3 used hyprpicker (`SUPER+PRINT`); Omarchy 4 does the same.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [hyprpicker](https://github.com/hyprwm/hyprpicker) | Click a dot on screen and it copies the colour code | Light (C++, 0.23 MB) | Runs on demand (on-screen magnifier) | extra/hyprpicker 0.4.7-4 | ★1.1k · release 2026-05 | The [Hyprland wiki](https://wiki.hypr.land/Useful-Utilities/Color-Pickers/) says it "seems to be the only one that doesn't suck". Used by Omarchy 3 & 4, HyDE, ML4W and end-4. Hyprland's portal (the go-between that answers apps' "pick a colour" buttons) runs hyprpicker for them ([portal source](https://github.com/hyprwm/xdg-desktop-portal-hyprland/blob/master/src/portals/Screenshot.cpp)). Copying needs `wl-clipboard`, which is not installed ([wiki](https://wiki.hypr.land/Hypr-Ecosystem/hyprpicker/)). |
| 2 | [Eyedropper](https://apps.gnome.org/Eyedropper/) | A small window that picks colours, keeps a history and shows every colour format | Medium (Rust, GTK4 + libadwaita) | Graphical | extra/eyedropper 2.2.1-1 | ★332 · release 2026-03 | In the [Arch colour-picker list](https://wiki.archlinux.org/title/List_of_applications/Multimedia#Color_pickers_and_palettes). It picks through the desktop portal (checked in its source), so on Hyprland it uses hyprpicker underneath. |
| 3 | [wl-color-picker](https://github.com/jgmdev/wl-color-picker) | A script that shows a colour dialog after you click | Light (shell script) | Graphical dialog | AUR only (`wl-color-picker` 1.4) | ★170 · release 2025-02 | A Wayland picker on the AUR (24 votes). Not updated since February 2025. |

**How it works — read more:** hyprpicker: [Hyprland wiki](https://wiki.hypr.land/Hypr-Ecosystem/hyprpicker/) · Eyedropper: [app page](https://apps.gnome.org/Eyedropper/) · wl-color-picker: [README](https://github.com/jgmdev/wl-color-picker)
**Claude's lean:** hyprpicker. It is official and tiny, and it also serves the "pick colour" buttons inside other apps. Install it together with `wl-clipboard`. (A suggestion; Javier chooses.)

## 22. Text editor (in the terminal)
*What this job is:* Editing text and settings files inside the terminal.
*Omarchy reference:* Omarchy 3 used Neovim (its own ready-made setup), and its editor launcher also accepts nvim, vim, nano, micro, helix and **fresh**; Omarchy 4 does the same, with the default chosen through its `omarchy-default-editor` setting.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [Neovim](https://neovim.io/) | A powerful "modal" editor: keys switch between typing mode and command mode | Medium (C/Lua, 30 MB) | Terminal | extra/neovim 0.12.5-1 | ★102.7k · release 2026-08 | The default in Omarchy 3 & 4; shipped by ML4W; [Arch Wiki page](https://wiki.archlinux.org/title/Neovim); official [Catppuccin theme](https://github.com/catppuccin/nvim). Steep learning curve. |
| 2 | [Helix](https://helix-editor.com/) | A modern modal editor that works well with no setup | Medium (Rust, 207 MB with language files) | Terminal | extra/helix 25.07.1-2 | ★46.4k · release 2025-07 (commits 2026-09) | Omarchy 4 has a Helix installer (`omarchy-install-editor-helix`); [Arch Wiki page](https://wiki.archlinux.org/title/Helix); official [Catppuccin theme](https://github.com/catppuccin/helix). Also modal. |
| 3 | [micro](https://micro-editor.github.io/) | An easy editor with normal keys (Ctrl-S saves, Ctrl-C copies) and mouse support | Light (Go) | Terminal | extra/micro 2.0.15-3 | ★29.6k · release 2025-12 (commits 2026-09) | Its [README](https://github.com/micro-editor/micro) calls it a "successor to the nano editor". [Arch Wiki page](https://wiki.archlinux.org/title/Micro); accepted by Omarchy's editor launcher; official [Catppuccin theme](https://github.com/catppuccin/micro). |
| 4 | [nano](https://wiki.archlinux.org/title/Nano) | The simple classic, with key hints at the bottom of the screen | Light (C) | Terminal | core/nano 9.2-1 (**installed**) | GNU project (no GitHub) · Arch pkg 2026-08 | Shipped by JaKooLit; accepted by Omarchy's launcher; [Arch Wiki page](https://wiki.archlinux.org/title/Nano). |
| 5 | [Fresh](https://sinelaw.github.io/fresh/) | A VS Code-style terminal editor: familiar keys, mouse, menus, no setup | Light (Rust) | Terminal | chaotic-aur/fresh-editor 0.5.2-1 (AUR; `fresh-editor-bin` 0.5.1 **installed**) | ★9.1k · release 2026-09-28 | Javier's chosen editor and the KognogOS default (from our own notes). Omarchy 3 & 4's editor launcher accepts `fresh`. Its README says it needs "zero configuration" and has "no modes". |

**How it works — read more:** Neovim: [Arch Wiki](https://wiki.archlinux.org/title/Neovim) · Helix: [Arch Wiki](https://wiki.archlinux.org/title/Helix) · micro: [site](https://micro-editor.github.io/) · nano: [Arch Wiki](https://wiki.archlinux.org/title/Nano) · Fresh: [site](https://sinelaw.github.io/fresh/) · [README](https://github.com/sinelaw/fresh)
**Claude's lean:** Fresh. It is already installed and is already the KognogOS default, so hypeForge stays consistent with the rest of KognogOS. Note it is not in the official repos (chaotic-aur/AUR). (A suggestion; Javier chooses.)

## 23. Image viewer (light)
*What this job is:* Opening photos and screenshots quickly.
*Omarchy reference:* Omarchy 3 used imv; Omarchy 4 still uses imv, now moving deleted images to the Trash and adding a key to annotate them.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [imv](https://sr.ht/~exec64/imv/) | A tiny keyboard-driven picture viewer | Light (C, 0.24 MB) | Graphical | extra/imv 5.0.1-2 | sourcehut (GitHub copy archived) · Arch pkg 2026-07 | Omarchy 3 & 4 default. The [Arch list](https://wiki.archlinux.org/title/List_of_applications/Multimedia#Image_viewers) calls it a "lightweight image viewer with support for Wayland and animated GIFs". Official [Catppuccin theme](https://github.com/catppuccin/imv). |
| 2 | [Loupe](https://apps.gnome.org/Loupe/) | GNOME's modern picture viewer | Medium (Rust, GTK4 + libadwaita, 7 MB) | Graphical | extra/loupe 50.0-1 | GNOME GitLab (copy ★19) · Arch pkg 2026-04 | Shipped by JaKooLit and ML4W; in the [Arch list](https://wiki.archlinux.org/title/List_of_applications/Multimedia#Image_viewers). |
| 3 | [swayimg](https://github.com/artemsen/swayimg) | A light picture viewer made for Wayland | Light (C++, 1.3 MB) | Graphical | extra/swayimg 5.6-2 | ★722 · release 2026-09 | Active and in the official repos. No major setup was found using it. |
| 4 | [qimgv](https://github.com/easymodo/qimgv) | A fast point-and-click picture viewer (can play short videos) | Medium (C++, Qt) | Graphical | chaotic-aur/qimgv-git (AUR `qimgv`) | ★3.1k · release 2021-09 (AUR updated 2026-07) | In the [Arch list](https://wiki.archlinux.org/title/List_of_applications/Multimedia#Image_viewers). Formal releases are old. |

**How it works — read more:** imv: [project](https://sr.ht/~exec64/imv/) · Loupe: [app page](https://apps.gnome.org/Loupe/) · swayimg: [README](https://github.com/artemsen/swayimg) · qimgv: [README](https://github.com/easymodo/qimgv)
**Claude's lean:** imv. It is tiny, native to Wayland, used by Omarchy, and has an official Catppuccin theme. (A suggestion; Javier chooses.)

## 24. PDF and document viewer (light)
*What this job is:* Reading PDFs, and sometimes filling in PDF forms.
*Omarchy reference:* Omarchy 3 used Evince (GNOME's "Document Viewer"); Omarchy 4 still uses Evince.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [Zathura](https://pwmt.org/projects/zathura/) | A minimal, keyboard-driven document viewer | Light (C, GTK4, 1.8 MB) | Graphical | extra/zathura 2026.07.18-1 (+ extra/zathura-pdf-mupdf for PDFs) | ★3.3k · release 2026-07 | Has an [Arch Wiki page](https://wiki.archlinux.org/title/Zathura); official [Catppuccin theme](https://github.com/catppuccin/zathura). The Arch comparison marks it Wayland-native, but **cannot fill PDF forms or annotate** ([table](https://wiki.archlinux.org/title/PDF,_PS_and_DjVu#Comparison)). |
| 2 | [Evince](https://wiki.gnome.org/Apps/Evince) | GNOME's classic document viewer | Medium (C, GTK3, 12.5 MB; Arch notes it pulls in `gnome-desktop`) | Graphical | extra/evince 1:48.4-1 | GNOME GitLab (copy ★378) · Arch pkg 2026-05 | Omarchy 3 & 4 default; [Arch Wiki page](https://wiki.archlinux.org/title/GNOME/Document_viewer). The Arch comparison marks forms, annotations and Wayland as "yes". |
| 3 | [Okular](https://apps.kde.org/okular/) | KDE's all-format document viewer | Heavy (Qt + KDE libraries, 19.5 MB) | Graphical | extra/okular 26.08.1-1 (**installed**) | KDE (copy ★1.5k) · commit 2026-09 | Already here. Arch comparison: forms, annotations and Wayland are all "yes". It keeps KDE libraries around. |
| 4 | [Papers](https://apps.gnome.org/Papers/) | GNOME's newer document viewer, a modern fork of Evince | Medium (GTK4 + libadwaita, partly Rust, 18.5 MB) | Graphical | extra/papers 50.3-1 | GNOME GitLab (copy ★6) · Arch pkg 2026-09 | The [Arch document list](https://wiki.archlinux.org/title/PDF,_PS_and_DjVu#Graphical) describes it as a "modern fork of evince, partly written in Rust". |
| 5 | [MuPDF](https://mupdf.com/) | A very small, very fast PDF viewer | Light (C, 0.16 MB) | Graphical | extra/mupdf 1.28.5-1 | copy ★3.0k · commit 2026-09 | Has an [Arch Wiki page](https://wiki.archlinux.org/title/MuPDF). The Arch comparison marks it **not** Wayland-native (it runs through the X11 compatibility layer). |

**How it works — read more:** Zathura: [Arch Wiki](https://wiki.archlinux.org/title/Zathura) · Evince: [Arch Wiki](https://wiki.archlinux.org/title/GNOME/Document_viewer) · Okular: [app page](https://apps.kde.org/okular/) · Papers: [app page](https://apps.gnome.org/Papers/) · MuPDF: [Arch Wiki](https://wiki.archlinux.org/title/MuPDF) · all: [Arch comparison table](https://wiki.archlinux.org/title/PDF,_PS_and_DjVu#Comparison)
**Claude's lean:** Zathura. It is the lightest, keyboard-driven, and has an official Catppuccin theme. It cannot fill forms, so use the browser for those: Arch notes that Chromium's built-in PDF viewer fills forms. (A suggestion; Javier chooses.)

## 25. Video and music player (light)
*What this job is:* Playing video files and music.
*Omarchy reference:* Omarchy 3 used mpv for video, and Spotify plus cliamp (a terminal music player) for music; Omarchy 4 keeps mpv and cliamp, adds `mpv-mpris` so the media keys control mpv, and makes Spotify an optional install.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [mpv](https://mpv.io/) | A minimal player for video and music, with on-screen controls | Light (C, 6.5 MB) | Graphical (can be run from the terminal) | extra/mpv 1:0.41.0-6 | ★37.2k · release 2025-12 (commits 2026-09) | Omarchy 3 & 4 and JaKooLit; [Arch Wiki page](https://wiki.archlinux.org/title/Mpv); official [Catppuccin theme](https://github.com/catppuccin/mpv). |
| 2 | [VLC](https://www.videolan.org/vlc/) | The well-known "plays everything" player | Heavy (C, Qt, 42 MB) | Graphical | extra/vlc 3.0.23_2-16 (**installed**) | copy ★19.8k · commit 2026-09 | Shipped by ML4W; the [Arch list](https://wiki.archlinux.org/title/List_of_applications/Multimedia#Video_players) calls it a "middleweight video player"; [Arch Wiki page](https://wiki.archlinux.org/title/VLC_media_player). |
| 3 | [cmus](https://cmus.github.io/) | A classic terminal music library player | Light (C, 0.85 MB) | Terminal | extra/cmus 2.12.0-7 | ★6.3k · release 2024-10 (commits 2026-08) | [Arch Wiki page](https://wiki.archlinux.org/title/Cmus); the Arch list calls it a "very feature-rich ncurses-based music player". |
| 4 | [cliamp](https://github.com/bjarneo/cliamp) | A terminal music player "inspired by Winamp" | Light (Go) | Terminal | AUR only (`cliamp` / `cliamp-bin` 2.3.0) | ★4.4k · release 2026-09-28 | Omarchy 3 & 4 ship it as their "Music TUI" (`SUPER+SHIFT+ALT+M`). |
| 5 | [kew](https://github.com/ravachol/kew) | A terminal music player with themes | Light (C, 1.4 MB) | Terminal | extra/kew 4.3.8-1 | ★3.1k · release 2026-09 | In the [Arch audio-player list](https://wiki.archlinux.org/title/List_of_applications/Multimedia#Audio_players). |

**How it works — read more:** mpv: [site](https://mpv.io/) · [Arch Wiki](https://wiki.archlinux.org/title/Mpv) · VLC: [Arch Wiki](https://wiki.archlinux.org/title/VLC_media_player) · cmus: [Arch Wiki](https://wiki.archlinux.org/title/Cmus) · cliamp: [README](https://github.com/bjarneo/cliamp) · kew: [README](https://github.com/ravachol/kew)
**Claude's lean:** mpv (with `mpv-mpris` so the media keys work). It is light, plays both video and music, and has a Catppuccin theme. Add cliamp or cmus only if a music-library player is wanted. (A suggestion; Javier chooses.)

## 26. How Hyprland is started (session start)
*What this job is:* What happens between typing your password at the login screen and seeing the desktop. Rows 1–2 are the two ways to *start Hyprland*; rows 3–5 are *login screens*, and each of them can start either one.
*Omarchy reference:* Omarchy 3 used SDDM with auto-login into a uwsm-managed session ("Omarchy (Hyprland uwsm)"), and its SDDM screen itself ran on Hyprland through `start-hyprland`; Omarchy 4 keeps that same uwsm session, with auto-login now set by its installer.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [start-hyprland](https://wiki.hypr.land/Getting-Started/Master-Tutorial/) (the plain **"Hyprland"** entry at login) | Hyprland's own starter. It launches Hyprland and watches it. If Hyprland crashes, it restarts it in a "safe mode", and back behind the lock screen if the screen was locked ([source](https://github.com/hyprwm/Hyprland/tree/main/start)). | Light (C++, part of Hyprland) | Launcher | part of extra/hyprland 0.56.2-3 (ships `/usr/bin/start-hyprland` and `hyprland.desktop`) | Hyprland ★38.7k · release 2026-08 | **This is what the Hyprland wiki recommends today.** Its [Master tutorial](https://wiki.hypr.land/Getting-Started/Master-Tutorial/) says to type `start-hyprland`. The [0.53 news](https://hypr.land/news/update53/) (2025-12-29) says Hyprland "should no longer be launched via `Hyprland`, but rather `start-hyprland`… crash recovery and safe mode". [Arch](https://wiki.archlinux.org/title/Hyprland#Terminal) agrees. |
| 2 | [uwsm](https://github.com/Vladimir-csp/uwsm) (the **"Hyprland (uwsm-managed)"** entry) | A "session manager" that runs Hyprland and your background helpers as systemd services. (systemd is Linux's service manager.) Services then start in order and shut down cleanly, and autostart entries are handled for you. | Light (Python, 0.3 MB) | Launcher | extra/uwsm 0.27.0-1 | ★1.2k · release 2026-09 | Used by Omarchy 3 & 4, HyDE and ML4W. However, the wiki [stopped recommending it on 2025-07-30](https://github.com/hyprwm/hyprland-wiki/commit/7611480bc4c6a5cae1734cd7d6ea480b55e4c368) and [now says](https://wiki.hypr.land/Useful-Utilities/Systemd-start/) it "is for advanced users and has its issues and additional quirks". If used, you must log out with `uwsm stop` (not Hyprland's exit), and settings such as environment variables move to `~/.config/uwsm/` ([Arch](https://wiki.archlinux.org/title/Hyprland#Universal_Wayland_Session_Manager)). |
| 3 | [SDDM](https://github.com/sddm/sddm) | A graphical login screen | Medium (C++, Qt, 5.3 MB) | Login screen (graphical) | extra/sddm 0.21.0-7 (**installed, active**, KognogOS theme) | ★2.4k · release 2024-02 (commits 2026-08) | The Hyprland wiki: "SDDM: Works flawlessly" (version 0.20 or newer; 0.21 is here). Used by Omarchy, HyDE and JaKooLit. Its PAM file here already has the lines that unlock a KWallet or GNOME keyring. **NVIDIA note:** logging out can leave a black screen on NVIDIA with SDDM; the wiki's fix is `hyprshutdown --vt 2` ([wiki](https://wiki.hypr.land/Hypr-Ecosystem/hyprshutdown/)). SDDM was installed on purpose, so removing Plasma keeps it; `plasma-login-manager`, installed but unused, goes with Plasma. |
| 4 | [greetd + tuigreet](https://wiki.archlinux.org/title/Greetd) | A minimal login service with a text-style login screen | Light (Rust) | Login screen (text) | extra/greetd 0.10.3-2 + extra/greetd-tuigreet 0.11.1-2 | tuigreet ★1.8k · release 2026-08; greetd Arch pkg 2026-03 | The Hyprland wiki: "greetd: Works flawlessly". Has an Arch Wiki page. Unlocking a wallet needs its own PAM lines ([Arch](https://wiki.archlinux.org/title/KDE_Wallet#Configure_PAM_on_Plasma_6_%28KF6%29)). |
| 5 | [ly](https://wiki.archlinux.org/title/Ly) | A lightweight text-style login screen | Light (Zig, 1.9 MB) | Login screen (text) | extra/ly 1.4.1-1 | copy ★7.6k · Arch pkg 2026-05 | The Hyprland wiki: "ly: Works flawlessly". Has an Arch Wiki page. |

**How it works — read more:** start-hyprland: [Hyprland wiki](https://wiki.hypr.land/Getting-Started/Master-Tutorial/) · [0.53 news](https://hypr.land/news/update53/) · uwsm: [Hyprland wiki](https://wiki.hypr.land/Useful-Utilities/Systemd-start/) · [Arch Wiki](https://wiki.archlinux.org/title/Universal_Wayland_Session_Manager) · SDDM: [Arch Wiki](https://wiki.archlinux.org/title/SDDM) · greetd: [Arch Wiki](https://wiki.archlinux.org/title/Greetd) · ly: [Arch Wiki](https://wiki.archlinux.org/title/Ly)
**Claude's lean:** keep SDDM (installed and themed) and use the plain "Hyprland" entry (start-hyprland). It is the wiki's current recommendation, gives crash recovery, and keeps every setting inside `~/.config/hypr`, which fits the one-folder rule. uwsm is Omarchy's path; revisit it only if we want systemd-managed autostart. (A suggestion; Javier chooses.)

## 27. Auto-mounting USB drives and disks
*What this job is:* Making a plugged-in USB stick or disk appear and open without typing a password. (On this machine Plasma did **not** mount drives by itself: it listed them and mounted one when clicked. See the checks at the top.)
*Omarchy reference:* Omarchy 3 had no background auto-mounter (Nautilus plus `gvfs` mounted a drive when you clicked it); Omarchy 4 added udiskie, started at login with `--automount --no-notify --no-tray`.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [udiskie](https://github.com/coldfix/udiskie) | A small background helper that mounts removable drives as they are plugged in (tray icon and pop-ups optional) | Light (Python; GTK3 only for the tray) | Background | extra/udiskie 2.7.0-2 | ★1.1k · release 2026-07 | The [Hyprland wiki "Other" page](https://wiki.hypr.land/Useful-Utilities/Other/) recommends it by name. Listed under [Arch mount helpers](https://wiki.archlinux.org/title/Udisks#Mount_helpers). Used by Omarchy 4, HyDE and ML4W. **Caution:** its built-in rules do not skip the internal Windows NTFS partition. Give it a rule to ignore internal disks, since our homelab rule is that NTFS is mounted read-only only. |
| 2 | [gvfs](https://gitlab.gnome.org/GNOME/gvfs) | GNOME's helper that lets graphical file managers show drives, mount them on click, and use the Trash | Light (C, 5.4 MB) | Background (used by Thunar or Nautilus) | extra/gvfs 1.60.3-3 | GNOME GitLab (copy ★92) · Arch pkg 2026-09 | [Arch](https://wiki.archlinux.org/title/File_manager_functionality#Mounting) calls it "the recommended solution for most file managers". Used by Omarchy 3 & 4 (with Nautilus), JaKooLit and ML4W. Needed by Thunar (job 14). |
| 3 | [thunar-volman](https://wiki.archlinux.org/title/Thunar#Thunar_Volume_Manager) | Thunar's add-on that acts when media is plugged in | Light (C) | Background (Thunar must run in "daemon mode") | extra/thunar-volman 4.20.0-2 | Xfce (copy ★6) · Arch 4.20.0 | [Arch Thunar page](https://wiki.archlinux.org/title/Thunar#Thunar_Volume_Manager). Needs both `gvfs` and Thunar kept running in the background. |
| 4 | [Yazi mount plugin](https://github.com/yazi-rs/plugins/tree/main/mount.yazi) | A mount, unmount and eject screen inside Yazi | Light (Lua plugin) | Terminal (you mount it yourself) | Yazi plugin (installed with `ya pkg add yazi-rs/plugins:mount`); uses `udisksctl` | plugins repo ★611 · commit 2026-09 | An official Yazi plugin ([README](https://github.com/yazi-rs/plugins/tree/main/mount.yazi)). Only useful if Yazi is chosen in job 14. |
| 5 | [bashmount](https://github.com/jamielinux/bashmount) | A terminal menu to mount and unmount drives | Light (Bash) | Terminal (you mount it yourself) | AUR only (`bashmount` 4.3.2) | ★291 · last commit 2022-06 | Listed under [Arch mount helpers](https://wiki.archlinux.org/title/Udisks#Mount_helpers). Not updated since 2022. |

**How it works — read more:** udiskie: [Hyprland wiki](https://wiki.hypr.land/Useful-Utilities/Other/) · [usage](https://github.com/coldfix/udiskie/wiki/Usage) · gvfs: [Arch Wiki](https://wiki.archlinux.org/title/File_manager_functionality#Mounting) · thunar-volman: [Arch Wiki](https://wiki.archlinux.org/title/Thunar#Thunar_Volume_Manager) · all of them sit on udisks2: [Arch Wiki](https://wiki.archlinux.org/title/Udisks)
**Claude's lean:** udiskie + gvfs. Give udiskie a rule to ignore internal disks, and have hypeForge mark `udisks2` as explicitly installed, because today it is kept only by KDE's `solid` library and would leave with Plasma. (A suggestion; Javier chooses.)

## 28. Password wallet / keyring
*What this job is:* The locked safe where browsers and apps keep saved passwords and keys, unlocked automatically when you log in.
*Omarchy reference:* Omarchy 3 used GNOME Keyring with a password-less "Default keyring" so it opens without asking; Omarchy 4 keeps that and pins Chrome-family browsers to it "so backend autodetection can't silently log you out of everything".
**Important for this machine:** Chrome 154 and Brave have no password-store setting. On Plasma, Chromium's code picks KWallet; on an unrecognised desktop such as Hyprland it switches to the standard "Secret Service" (checked in [Chromium's source](https://github.com/chromium/chromium/blob/main/components/os_crypt/async/browser/freedesktop_secret_key_provider.cc)). [Arch warns](https://wiki.archlinux.org/title/Chromium#Force_a_password_store) this "can lead to you apparently losing your passwords and cookies". So pin the flag whichever option is chosen. The disk here is **not** encrypted, so Omarchy's password-less keyring would leave the secrets unprotected on disk ([Arch](https://wiki.archlinux.org/title/GNOME/Keyring#PAM_step): "stored unencrypted").

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [GNOME Keyring](https://wiki.gnome.org/Projects/GnomeKeyring) | GNOME's password safe, which almost every app can use; optional viewer window: Seahorse | Light (C, 3.3 MB) | Background | extra/gnome-keyring 1:50.0-1 (+ extra/seahorse 1:47.0.1-6 to browse it) | GNOME GitLab (copy ★39) · Arch pkg 2026-04 | Used by Omarchy 3 & 4 and end-4. The Hyprland wiki shows how to unlock it at login ([uwsm page](https://wiki.hypr.land/Useful-Utilities/Systemd-start/)). SDDM's PAM file here already has its lines. Browsers need `--password-store=gnome-libsecret`. Switching means moving the browser passwords over (export, then import). |
| 2 | [KWallet on its own](https://wiki.archlinux.org/title/KDE_Wallet) | KDE's password safe, kept without the rest of Plasma | Medium (Qt6 + KDE libraries) | Background | extra/kwallet 6.30.0-1 + extra/kwallet-pam 6.7.5-1 (**both installed; holds this machine's wallet**) | KDE (copy ★44) · Arch pkg 2026-09 | Nothing to migrate. Since KDE Frameworks 5.97 it speaks the standard Secret Service ([Arch](https://wiki.archlinux.org/title/KDE_Wallet)). To unlock at login outside Plasma, keep PAM and start `/usr/lib/pam_kwallet_init` from Hyprland's autostart ([Arch](https://wiki.archlinux.org/title/KDE_Wallet#Unlocking_KWallet_automatically_in_a_window_manager)). Browsers need `--password-store=kwallet6` ([Arch](https://wiki.archlinux.org/title/KDE_Wallet#KDE_Wallet_for_Chromium_and_VSCode)). **`kwallet-pam` is in the `plasma` group, so hypeForge must keep it on purpose.** |
| 3 | [KeePassXC](https://keepassxc.org/) (Secret Service mode) | A password-manager app that can also act as the system's password safe | Medium (C++, Qt5, 31 MB) | Graphical | extra/keepassxc 2.7.12-5 (**installed**) | ★29.0k · release 2026-03 | [Arch Wiki](https://wiki.archlinux.org/title/KeePass#Secret_Service). It refuses to switch this on while another safe (such as GNOME Keyring) is running, and apps can fail if the database is not open yet. The [Arch NetworkManager page](https://wiki.archlinux.org/title/NetworkManager#nm-applet) lists it as a valid safe. |
| 4 | [oo7](https://github.com/linux-credentials/oo7) | A newer, small password safe written in Rust, with its own login-unlock module | Light (Rust) | Background | extra/oo7 0.6.0-3 (ships `oo7-daemon`, `pam_oo7.so`) | ★385 · release 2026-02 | In the official repos. Its README mentions a KWallet-file reader "used for automatic migration". Newer and less proven; no major setup was found using it. |

**How it works — read more:** GNOME Keyring: [Arch Wiki](https://wiki.archlinux.org/title/GNOME/Keyring) · KWallet: [Arch Wiki](https://wiki.archlinux.org/title/KDE_Wallet) · KeePassXC: [Arch Wiki](https://wiki.archlinux.org/title/KeePass#Secret_Service) · oo7: [docs](https://linux-credentials.github.io/oo7/oo7/) · browsers: [Arch: force a password store](https://wiki.archlinux.org/title/Chromium#Force_a_password_store)
**Claude's lean:** KWallet on its own for the switch-over. It already holds this machine's secrets and SDDM already unlocks it. Pin Chrome and Brave to `--password-store=kwallet6` and keep `kwallet-pam`. Consider moving to GNOME Keyring later, once browser passwords have been exported. Run only one password safe at a time. (A suggestion; Javier chooses.)

## 29. Power menu (log out / restart / shut down)
*What this job is:* A menu to log out, restart or shut down safely.
*Omarchy reference:* Omarchy 3 used a "System" menu inside its Walker launcher (`SUPER+ESC`, and the power button); Omarchy 4 has the same menu rebuilt inside its Quickshell shell.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [wlogout](https://github.com/ArtsyMacaw/wlogout) | A full-screen set of big buttons: lock, log out, restart, shut down | Light (C, GTK3) | Graphical | chaotic-aur/wlogout 1.2.2-0.3 (AUR) | ★1.1k · release 2024-04 (last commit 2024-07) | Shipped by HyDE, JaKooLit and end-4; listed on [awesome-hyprland](https://github.com/hyprland-community/awesome-hyprland); official [Catppuccin theme](https://github.com/catppuccin/wlogout). No updates since 2024. |
| 2 | [hyprshutdown](https://github.com/hyprwm/hyprshutdown) | Hyprland's own "close everything politely, then leave" tool, with a progress window. It is not a menu by itself: `--post-cmd 'reboot'` makes it restart afterwards. | Light (C++, 0.36 MB) | Graphical (progress window) | extra/hyprshutdown 0.1.1-8 (Arch lists it as an optional part of `hyprland`) | ★141 · release 2026-05 | The [Hyprland wiki](https://wiki.hypr.land/Hypr-Ecosystem/hyprshutdown/) calls it "the recommended way to exit Hyprland", because apps otherwise "die instead of exiting". Shipped by ML4W. Its `--vt 2` option fixes the NVIDIA + SDDM black screen, but needs a sudo rule for `chvt`. |
| 3 | [rofi power list](https://github.com/jluttine/rofi-power-menu) | A pop-up list in rofi (already installed) with Lock / Log out / Restart / Shut down | Light (script) | Graphical (keyboard pop-up) | rofi: extra/rofi 2.0.0-1 (**installed**); ready-made script: AUR only (`rofi-power-menu` 3.1.0) | script ★516 · last commit 2025-03 | The same idea as Omarchy's System menu, which is a list inside its launcher. Needs no new menu app; hypeForge could ship its own small script instead of the AUR one. |
| 4 | [nwg-bar](https://github.com/nwg-piotr/nwg-bar) | A small bar of power buttons | Light (Go, GTK3) | Graphical | extra/nwg-bar 0.1.6-4 | ★179 · release 2024-01 | The example on the [Arch Hyprland page's "Power control"](https://wiki.archlinux.org/title/Hyprland#Power_control). Little activity since 2024. |
| 5 | [wleave](https://github.com/AMNatty/wleave) | A modern, maintained take on wlogout | Light (Rust, GTK4) | Graphical | AUR only (`wleave` 0.7.1) | ★346 · release 2026-02 | Listed on [awesome-hyprland](https://github.com/hyprland-community/awesome-hyprland) ("Wayland-native logout script written in Gtk3" there; its GitHub now says GTK4). |

**How it works — read more:** wlogout: [README](https://github.com/ArtsyMacaw/wlogout) · hyprshutdown: [Hyprland wiki](https://wiki.hypr.land/Hypr-Ecosystem/hyprshutdown/) · rofi-power-menu: [README](https://github.com/jluttine/rofi-power-menu) · nwg-bar: [Arch Wiki example](https://wiki.archlinux.org/title/Hyprland#Power_control) · wleave: [README](https://github.com/AMNatty/wleave)
**Claude's lean:** a small rofi power list whose Log out, Restart and Shut down entries call hyprshutdown. It adds no new menu app, is keyboard-first, and uses the wiki's recommended safe exit. Add `--vt 2` only if the NVIDIA black screen appears. (A suggestion; Javier chooses.)

## 30. Printing
*What this job is:* Adding and managing printers and print jobs. The HP LaserJet already prints; the print window inside apps comes from GTK and Qt, not from Plasma.
*Omarchy reference:* Omarchy 3 used CUPS with system-config-printer (plus cups-browsed and a "print to PDF" printer); Omarchy 4 keeps CUPS and system-config-printer, adds cups-pk-helper, ships locked-down cups-browsed settings that only auto-add modern "driverless" printers, and hides the print-status tray icon.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [system-config-printer](https://github.com/OpenPrinting/system-config-printer) | A simple printer settings window (add printers, see queues) | Medium (Python, GTK3, 8.4 MB) | Graphical | extra/system-config-printer 1.5.18-7 (**installed**) | ★204 · release 2022-08 (commits 2026-09) | Used by Omarchy 3 & 4. The [Arch CUPS page](https://wiki.archlinux.org/title/CUPS#GUI_applications) calls it a "GTK printer configuration tool and status applet". With `cups-pk-helper` (installed) it asks for permission through polkit (the system's permission pop-up) instead of needing the root password ([Arch](https://wiki.archlinux.org/title/CUPS#Allowing_admin_authentication_through_PolicyKit)). |
| 2 | [CUPS web page](https://wiki.archlinux.org/title/CUPS#Web_interface) | The printer system's own admin page, opened in a browser at `http://localhost:631` | Light (nothing to add) | Browser page | part of extra/cups 2:2.4.19-1 (**installed**) | CUPS ★1.8k · release 2026-04 | [Arch](https://wiki.archlinux.org/title/CUPS#Web_interface): CUPS "can be fully administered through the web interface". Caution from our 2026-09-14 printer notes: its "Print Test Page" button is broken on this box, so test with a real document. |
| 3 | [CUPS commands](https://wiki.archlinux.org/title/CUPS#CLI_tools) (`lpstat`, `lpadmin`, `lp`, `cancel`) | Typed commands to check, add or fix printers and jobs | Light | Terminal (commands) | part of extra/cups (**installed**) | as above | [Arch CUPS CLI tools](https://wiki.archlinux.org/title/CUPS#CLI_tools). Our notes say to run `lpstat -v` after every change. Checked today: the HP queue is present and is the default. |
| 4 | [print-manager](https://github.com/KDE/print-manager) | KDE's printer settings page and job pop-up | Heavy (Qt + KDE libraries) | Graphical | extra/print-manager 1:6.7.5-1 (**installed**, but in the `plasma` group) | KDE (copy ★28) · commit 2026-09 | Listed on the [Arch CUPS page](https://wiki.archlinux.org/title/CUPS#GUI_applications). It is what Plasma used, and it leaves with Plasma unless kept on purpose. |

**How it works — read more:** system-config-printer: [Arch Wiki](https://wiki.archlinux.org/title/CUPS#GUI_applications) · CUPS web page: [Arch Wiki](https://wiki.archlinux.org/title/CUPS#Web_interface) · CUPS commands: [Arch Wiki](https://wiki.archlinux.org/title/CUPS#CLI_tools) · CUPS itself: [OpenPrinting](https://openprinting.github.io/cups/)
**Claude's lean:** system-config-printer. It is already installed, Omarchy uses it, and with `cups-pk-helper` it asks through a normal password pop-up. Use `lpstat -v` for quick checks. Nothing in CUPS depends on Plasma. (A suggestion; Javier chooses.)

## 31. File-open dialogs and screen sharing ("portals")
*What this job is:* A *portal* is a hidden helper that apps call when they need something from the desktop: the "open file" and "save as" windows, sharing your screen in a video call, taking a screenshot, or asking whether you prefer dark mode. You never start it yourself; it wakes up when an app asks. On Plasma, `xdg-desktop-portal-kde` does all of this. Under Hyprland the job is split in two: **one helper for screen sharing, and one for the file window**, because Hyprland's own helper has no file window.
*Omarchy reference:* Omarchy 4.0.4 installs `xdg-desktop-portal-hyprland` and `xdg-desktop-portal-gtk` together ([omarchy-base.packages](https://github.com/basecamp/omarchy/blob/quattro/install/omarchy-base.packages)), with Nautilus as its file manager. It ships no portal settings file of its own, so it relies on the defaults.

**Part A: screen sharing, screenshots, global shortcuts.** There is really one answer here.

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [xdg-desktop-portal-hyprland](https://github.com/hyprwm/xdg-desktop-portal-hyprland) (XDPH) | Hyprland's own portal: screen sharing (including single windows), screenshots, global shortcuts | Light (817 KiB; brings Qt 6 for its small "what to share" window) | Background | extra/xdg-desktop-portal-hyprland 1.4.1-2 | ★482 · release 2026-07 · commit 2026-09 | The [HW page](https://wiki.hypr.land/Hypr-Ecosystem/xdg-desktop-portal-hyprland/) calls it "Hyprland's xdg-desktop-portal implementation. It allows for screen sharing, global shortcuts, etc." Used by Omarchy 4. Starts by itself when Hyprland starts. The screenshot part needs `grim`, which job 11 installs anyway. |
| 2 | [xdg-desktop-portal-wlr](https://github.com/emersion/xdg-desktop-portal-wlr) | The same kind of helper, for Sway and similar desktops | Light | Background | extra/xdg-desktop-portal-wlr 0.8.4-1 | — | Listed only so it is **not** installed by mistake. The HW notes XDPH already covers these desktops, and window sharing is a Hyprland-only feature. Two screen-sharing helpers side by side can conflict. |

**Part B: the "open file" / "save as" window.**

| # | Option | What it is | Weight | Kind | In Arch | Activity | Why it's on the list |
|---|---|---|---|---|---|---|---|
| 1 | [xdg-desktop-portal-gtk](https://github.com/flatpak/xdg-desktop-portal-gtk) | The GNOME-style (GTK) file window, plus the dark-mode setting, print dialog and "open with" chooser | Light (428 KiB; GTK 3, already on the system) | Graphical | extra/xdg-desktop-portal-gtk 1.15.3-1 (**installed**) | ★172 · release 2025-03 · commit 2026-09 | The HW says: "XDPH doesn't implement a file picker. For that, it is recommended to install `xdg-desktop-portal-gtk` alongside XDPH." It is also the default: `hyprland-portals.conf` falls back to GTK. Used by Omarchy 4. It follows the Catppuccin GTK look chosen in job 13. |
| 2 | [xdg-desktop-portal-kde](https://github.com/KDE/xdg-desktop-portal-kde) | The KDE file window we use today | Heavy (2.8 MB **and it depends on `plasma-workspace`**, Plasma's core) | Graphical | extra/xdg-desktop-portal-kde 6.7.5-1 (**installed**, `plasma` group) | ★83 (mirror) · commit 2026-09 | The HW gives a recipe to keep the KDE window under Hyprland (`FileChooser = kde` in `~/.config/xdg-desktop-portal/hyprland-portals.conf`). But checked today with `pacman -Si`: it needs `plasma-workspace`, so **keeping it keeps half of Plasma installed**. That works against D-6 once Plasma leaves. |
| 3 | [xdg-desktop-portal-termfilechooser](https://github.com/hunkyburrito/xdg-desktop-portal-termfilechooser) | Opens your **terminal file manager** as the file window. It ships a ready-made Yazi wrapper (job 14) | Light | Terminal | **AUR only**: `xdg-desktop-portal-termfilechooser` 1.4.3-1 (2 votes) or the `-hunkyburrito-git` build (21 votes) | ★328 · release 2026-06 · commit 2026-09 | The most terminal-first choice, and it matches Yazi from job 14. It comes with wrappers for yazi, lf, nnn, ranger, vifm and superfile. The catch: it is AUR only (nog's AUR path is not tested, see "Could not verify"), and a terminal file window is a new habit for anyone used to Plasma's. |
| 4 | [xdg-desktop-portal-gnome](https://gitlab.gnome.org/GNOME/xdg-desktop-portal-gnome) | GNOME's newer (GTK 4) file window | Heavy (brings `nautilus`, `libadwaita`, `gnome-desktop-4`) | Graphical | extra/xdg-desktop-portal-gnome 50.0-1 (`gnome` group) | GNOME GitLab | Listed because it is common, but it pulls in GNOME's file manager and is built for GNOME. Omarchy does not use it. |

**Two things that ride along with this job**
- **The dark-mode setting.** Apps such as browsers ask the portal "is dark mode on?". Today Plasma answers (`Settings=kde;gtk` in `kde-portals.conf`). Under Hyprland the GTK portal answers from the GTK settings of job 13, so that job must set dark mode, or apps may come up light.
- **The password wallet.** This desktop also has a KWallet portal (`kwallet.portal`, used for `Secret`). Whether it stays depends on job 28.

**How it works — read more:** XDPH and the KDE-picker recipe: [HW](https://wiki.hypr.land/Hypr-Ecosystem/xdg-desktop-portal-hyprland/) · Portals in general: [Arch Wiki](https://wiki.archlinux.org/title/XDG_Desktop_Portal) · Terminal file window: [README](https://github.com/hunkyburrito/xdg-desktop-portal-termfilechooser)
**Claude's lean:** XDPH for screen sharing, plus xdg-desktop-portal-gtk for the file window. They are small, the Hyprland wiki recommends the pair, Omarchy uses the same pair, and the GTK one is already installed. `xdg-desktop-portal-kde` leaves with Plasma. The terminal (Yazi) file window is worth trying in Phase 2 as an extra, once nog's AUR path is tested. (A suggestion; Javier chooses.)

---

---

## Could not verify

**Part 1 (the things you see):**

- **Memory (RAM) and processor use** of any option. Nothing was installed. Disk numbers come from `pactree` / `pacman -Si` only.
- **Whether DMS's settings folder can be moved** to a custom path. Only its default `~/.config/DankMaterialShell/` location was documented in what was read.
- **Whether nog can install AUR-only picks:** Walker/elephant, ashell, clipvault, avizo, Tensaku, hyprqt6engine, Caelestia, noctalia-greeter. `nog search` does not cover the AUR, and nog's AUR path was not tested.
- **Whether the stale options work on Hyprland 0.56:** swaylock-effects (last commit 2024-03) and gtklock (last release 2024-10). Not tested.
- **Whether wf-recorder can use NVIDIA's own encoder (NVENC)** through ffmpeg's `h264_nvenc`. Its README documents only VA-API.
- **Smooth recording at 144 Hz across three 1440p screens** with this NVIDIA driver, for any recorder. Not tested.
- **Whether Alacritty supports the kitty image protocol.** Only the "no Sixel" status was confirmed.
- **The exact colour options for a Catppuccin tuigreet or ly screen.** Their docs say "themeable"; the specific flags were not checked.
- **Whether GTK4/libadwaita apps pick up a Catppuccin colour file** alongside adw-gtk3. Noctalia's docs say its template writes GTK4 colours; not tested.
- **Whether Omarchy 4's shell can run outside Omarchy.** Not tested; it appears to be wired to Omarchy's own commands.
- **The HW's "works flawlessly" login-manager claims** are the wiki's word and were not tested on this NVIDIA machine.
- **Whether SDDM's login screen here could move from X11 to Wayland** without other changes. Omarchy does it; not tried here.
- **A search-result claim that Noctalia uses about 30–40 MiB of RAM** came from a snippet, not an official source, so it was not used.
- **How long "for now" lasts** for hyprlock, hypridle and hyprpaper keeping the hyprlang `.conf` format. The Lua announcement gives no date.
- **Comparable popularity numbers** for self-hosted projects (gpu-screen-recorder, grim, wofi, greetd's main home). No star counts exist for them.

**Part 2 (the tools you use):**

- **Real memory and processor use** of any tool. "Weight" is judged from the toolkit and the package size, not measured.
- **hyprsunset on this RTX 3060:** not run. Hyprland's settings docs imply it works on NVIDIA (only the fade is disabled). One open report ([#80](https://github.com/hyprwm/hyprsunset/issues/80)) describes no effect on a hybrid AMD + NVIDIA laptop.
- **btop's GPU box:** that btop links NVIDIA's library was checked; the GPU box itself was not opened on screen.
- **KWallet unlock at login:** it only works if the wallet password equals the login password (Arch). Not checked.
- **What Chrome and Brave would do on first start under Hyprland:** predicted from Chromium's source, the Arch warning and Omarchy's release note, not tested. Brave is assumed to behave like Chromium. What Chrome stores in KWallet was not read.
- **Job 31, portals:** nothing was installed or run. Not tested: screen sharing through XDPH with this NVIDIA driver across three monitors, whether Chrome and Brave use the GTK file window under Hyprland without extra settings (the HW warns Firefox may need extra settings for the KDE one), and how smooth the Yazi file window is in daily use. The Arch Wiki portal page refused automated reading today, so the portal facts come from the HW, `pacman -Si` and the files in `/usr/share/xdg-desktop-portal/`.
- **udiskie and the internal Windows NTFS partition:** udisks marks it "system" and not ignored, and udiskie's built-in rules would not skip it. Whether udiskie would ask for a password or mount it read-write was not tested.
- **Plasma's automount defaults** were read from KDE's current source code (plasma-desktop master), not from the installed 6.7.5 package, and no USB stick was plugged in to confirm.
- **hyprshutdown combined with uwsm** (which one should end the session): no source found.
- **Lua output of nwg-displays, hyprmon and Monique on Hyprland 0.56.2:** their release notes say Lua is supported; none was run. **HyprDynamicMonitors** (a terminal monitor tool) was left out because its Lua request ([#151](https://github.com/fiffeek/hyprdynamicmonitors/issues/151)) is still open.
- **Whether mode `preferred` gives 144 Hz** on these three monitors: not checked. The lean writes `@144` explicitly for that reason.
- **Yazi picture previews in Alacritty through Überzug++** on Hyprland + NVIDIA: the docs say this is supported; not tested.
- **oo7's automatic KWallet migration:** its README mentions it; its behaviour was not tested.
- **Release dates for projects not on GitHub** (imv, wlsunset, greetd, gammastep, nano, pavucontrol, Evince, Papers, Loupe, gvfs, gnome-keyring, kwallet): sourcehut blocked the requests, so Arch package dates are given instead. Stars on their GitHub copies undercount.
- **AUR-only tools** (wifitui, bluetuith, Overskride, hyprmon-bin, Monique, cliamp, wleave, bashmount, wl-color-picker, rofi-power-menu): not built or installed.
- **bluetui with devices that ask for a PIN:** its README shows pairing; PIN prompts were not checked.
- **swayimg:** no major setup using it was found. Its evidence is GitHub activity and Arch packaging only.
- **Other setups' choices not traced:** ML4W's password safe (only `libsecret` is in its list) and whether HyDE's login entry uses uwsm by default (uwsm is in its core list).
- **Omarchy 4 and cups-browsed:** Omarchy 4 ships settings for cups-browsed, but the package is not in its base list, so whether it installs it is unverified.
- **Hyprland wiki:** the site was rewritten on 2026-09-18. Quotes come from its source repo at commit d5498a9 (2026-09-27); the live pages were spot-checked, not all re-read.
