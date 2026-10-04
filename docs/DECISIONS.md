# hypeForge — decision log

*Every decision that shapes hypeForge, dated, with who made it and why. Newest first.*
*A decision here is only reopened by Javier. **Proposed** entries are suggestions still waiting for his answer.*

---

## 2026-10-01

### D-43 · Maximise is hypeForge's own, so a maximised window comes to the front
**Decided by Javier**, from a bug he found: *"If I use alt+tab to switch from the terminal on top to chrome, or click on chrome, it doesn't bring it to the top"* … *"it happens with all maximized windows."*

**What it means:**
- **Why:** Hyprland's maximise puts the window on a layer of its own. A window opened over it is allowed to stay above it, so clicking the maximised window or Alt + Tabbing to it gave it the keyboard but left it underneath.
- **Now every maximise is ours:** the window stays an ordinary floating window, stretched over the usable screen (inside the 13 px edge gap, above the bar). Clicking it or Alt + Tab brings it to the front like any other window.
- **The app is told it is maximised**, so its button offers "restore". Hyprland takes that "restore" without any event (F-39); it only sets the window's client state back to 0. A small watcher in `snap.lua` checks the windows we maximised four times a second and restores any whose app has said so. (Not telling the app was tried first: Chrome decides by itself that it is maximised, so its restore click went nowhere.)
- It covers **Win + Page Up**, **Win + ↑ at the top** (D-30) and **an app's own maximise** (its button, or a double-click on its title bar), which `snap.lua` catches and converts. **Win + ↓** and Win + Page Up go back to the half or size the window had. Real fullscreen (F11, a video) stays Hyprland's.
- D-32 (an app's "open maximised" undone in its first moments) is unchanged.

### D-42 · No title bars from hypeForge
**Decided by Javier**, after a morning in the real session: *"the top bar on the apps. apps with no bar show it, and it is great. other apps that have a bar, may also add it on top or not. weird. Let's just remove it please."* And on snapping: *"on the top it doesn't show well, like it passes the monitor frame, and then snapping between apps it gets under the one on top.... don't like it."*

**What it means:**
- **hyprbars is no longer loaded.** Apps that draw their own title bar keep it; apps that do not (Alacritty and other terminals) have none. Close with **Alt + F4**, maximise with **Win + Page Up** or **Win + ↑ twice**, move with **Win + drag**.
- **Why snapping looked wrong:** hyprbars draws its 26 px bar *above* the window, and `snap.lua` places windows by their own edges. A window snapped to the top had its bar pushed past the screen edge, and a window snapped below slid its bar under the one above. With no bar the problem is gone, so `snap.lua` is unchanged.
- **This replaces the title-bar parts of D-31 and D-33**; those entries stay as they were written, as history. `hypr/titlebars.lua` is removed from the desktop folder (the prototype keeps its copy). The `hyprland-plugin-hyprbars` package is no longer needed; taking it off this computer and out of the KognogOS build list is a separate, later step.

### D-41 · The bar: along the bottom, full width, clock in the corner
**Decided by Javier**, shaped live on this computer in four small steps, then: *"lock the bar information for our KognogOS hypeForge build. It is perfect."*

**What it means:**
- **Noctalia's bar sits along the bottom of the screen, edge to edge, with square corners** (`position = "bottom"`, `margin_ends = 0`, `radius = 0`).
- **40 pixels tall** (Noctalia's default is 34).
- **Icons about 2 pixels bigger.** Noctalia has no icon size in pixels, only a size multiplier per widget, so every icon on the bar gets `scale = 1.17` (measured from screenshots: about 12 → 14–15 px). The clock and the "Nothing Playing" text keep their size.
- **Left:** the KognogOS emblem (launcher), then the open-app icons. **No workspace number**: Javier read it as the monitor number; workspaces still switch by keyboard.
- **Right:** media, tray, notifications, clipboard, network, Bluetooth, volume, brightness, battery, control centre, power, and **the clock last, in the corner**. The middle is empty. *(Later on 2026-10-01, Javier: the clock shows 12-hour time with AM/PM and the date, the power button moved after it to the very end, unopened pinned apps show at full strength, and app icons are tinted with the theme's text colour so they read on every theme.)* *(2026-10-04, Javier: app icons show in their own colours, no tint.)*
- It lives in `desktop/noctalia/00-hypeforge.toml`, so it is the default for every hypeForge install, and the KognogOS hypeForge edition picks it up at its next ISO build (`build-iso.sh` stages hypeForge from this folder). Anything a user changes in Noctalia's Settings window still wins.
- This replaces "top bar" wherever hypeForge's earlier decisions and research say it; those entries stay as they were written, as history.

## 2026-09-30

### D-40 · Noctalia is hypeForge's desktop shell
**Decided by Javier** after bar trial 1 in the KognogOS VM: *"WOW. We found what we are looking for. I did not know about noctalia. It is a beautifully done piece of software. Now we need to see how we make it shine for us. Lots of the things we work are going to be eliminated, but it is ok."* On themes: *"It manages themes, actually, and I like how it works. Let's create our themes using noctalia. Brings several themes, and they rock... with ours added, would be even better."* On the launcher: *"The launcher is amazing. Set!"*

**What it means:**
- **Noctalia** (`extra/noctalia`, MIT, a native Wayland shell with no Qt or GTK) becomes the layer around Hyprland: the top bar, launcher, notifications, sound / network / Bluetooth drop-downs, control centre, on-screen pop-ups, wallpaper and theme handling. It is in Arch's official repos, so nog installs and locks it like the rest of the Hyprland family (D-9).
- **The five KognogOS themes (D-36) are rebuilt as Noctalia palettes**, next to Noctalia's own. One theme choice should drive everything: the bar, apps, terminal, title bars, lock screen and the matching KognogOS wallpaper.
- **Pieces it replaces leave the recipe** once each one is proven covered: Waybar (D-17), mako (D-19), SwayOSD (D-20), hyprpaper, Walker + elephant (D-18, D-21; elephant paused development on 2026-09-29), hyprlauncher, hyprpwcenter and the tray apps for network and Bluetooth. The research and the findings about them stay in the log.
- Still open from the trial: open-app icons in the bar (*"if not, I don't care for it or minimize"*), the wallpaper picker showing no wallpapers, theme switches not changing the wallpaper, and which lock screen stays (hyprlock *"looks amazing"*, Noctalia has its own).
- **We learn from Noctalia and credit it; we never compare** (D-27).

### D-39 · Settings get graphical apps, not terminal ones; Forge apps later
**Decided by Javier** after the first hands-on test of the installed VM: *"The whole hypeForge all terminal phylosophy is going to take time, and following up with our Forge Suite KognogOS phylosophy, we will have to create our own apps until the system becomes a shell for graphic apps, and terminal based for everything else based on Forge Suite. But what we are using terminal, I don't like."*

**What it means:**
- **The terminal tools picked for settings are out:** wiremix (sound), nmtui (network), bluetui (Bluetooth) and nwg-displays (screens, *"a horrible piece of software"*). Each is replaced by a graphical app that opens from the top bar, as a panel under it where possible (*"one that opens under the bar, and then offers settings to change the audio output, source, etc."*).
- **Long term, KognogOS grows its own Forge apps** for system settings. Until then, the best graphical apps other Hyprland users rely on fill the gap, chosen the D-11 way: up to 5 researched options per job, Javier picks.
- Jobs 14–19 and the top-bar part of job 1 in RECIPE.md are reopened.

### D-38 · The login screen is KognogOS's own SDDM greeter, not tuigreet
**Decided by Javier:** *"I don't like the login screen. I know is "terminal" but does not go with the look of the OS. Let's use the one we already have with plasma."* **This replaces D-15** (greetd + tuigreet).

**What it means:** SDDM comes back as the login manager, with the KognogOS greeter theme built on 2026-08-12 (plain QtQuick only, so it runs without Plasma). It starts the hypeForge session through uwsm. Plasma itself stays out. A graphical login also covers finding F-3 (text messages between login and desktop).

### D-37 · A KognogOS edition with hypeForge only, tested in a VM before this computer
**Decided by Javier:** *"only our hypeForge or terminal. Nothing else. That is why I want us to create a new ISO with all KognogOS perks, but only with hypeForge as window manager. Then we install the iso on a VM and test it and fix it there."* And: *"I will install it here in this pc once it is tested, and working properly on our own KognogOS+hypeForge."*

**What it means:**
- **Plasma is not in this edition at all** (it moves D-6's "little by little" to one step for the ISO). The login screen offers two choices only: **hypeForge** or **Terminal**. The live disc logs straight into hypeForge.
- **Nothing is installed on the test desktop first.** Phase 2 ("build it by hand") happens in the KognogOS VM instead of next to Plasma here. The desktop comes to this computer only after it works in the VM.
- The login is greetd + tuigreet (D-15), proven in the VM as planned.
- KognogOS gets its **first installer**, a small script (`installer/tui/kognog-install.sh`, KognogOS #2): it copies the tested live system to the disk and sets up start-up, login and a user. Javier chose it over archinstall, which would install plain Arch first.
- The KognogOS work happens on the `hypeforge-edition` branch, so today's Plasma ISO still builds until the new one passes.
- **The desktop is one folder in this repo, `desktop/`**, and `scripts/desktop/install-into.sh <home>` puts it into any home folder. The ISO build, the installer and later the app all use that one script, so there is one source of truth.
- The title bars are a package (`hyprland-plugin-hyprbars` from the AUR, built into KognogOS's local repo in a clean chroot, so Hyprland is never installed on this computer to build it), loaded with `hl.plugin.load`. No hyprpm, no password at login.

---

## 2026-09-29

### D-36 · Five themes, one per KognogOS wallpaper
**Decided by Javier** on the theme preview page (`prototype/themes/preview.html`), after one round of changes: *"the gray, let's use pastel greens for a lighter theme. Make the Gray theme the white theme, and the Gray theme, let's use darker grays instead"*, then *"perfect!"*.

| Theme | Wallpaper | Kind | In short |
|---|---|---|---|
| **Catppuccin Mocha** (default) | `#1e1e2e` | dark | Catppuccin's own Mocha colours, mauve accent |
| **Black** | `#000000` | dark | pure black, quiet greys from the logo |
| **Green** | `#014b27` | light | pastel greens, dark green text |
| **Gray** | `#a6a6a6` | dark | charcoal greys, light text |
| **White** | `#ffffff` | light | light grey windows, dark text |

- Dark themes use Catppuccin Mocha's colours in the terminal, light ones Catppuccin Latte's, with Latte's yellow and blue and the maximise button's green darkened so they stay readable.
- Every graded pair (text, quiet text, title, top bar, active workspace, button icons, terminal red, yellow and blue) reaches **4.5:1 or better**.
- The exact colours are the proposals in the preview page; each theme becomes one colour file in the portable folder's `theme/` (D-28) that drives every app. A theme can still be adjusted and saved on the page later (D-23).

### D-35 · Alt + Tab stays simple: next window, no list
**Decided by Javier**, after trying the test machine's own Alt + Tab: *"Yes, keep it simple."* **Alt + Tab** jumps to the next window and brings it to the front, and **Alt + Shift + Tab** goes back. No window list or previews appear. hypeForge carries the two keys itself (`prototype/snap.lua`), the same ones Omarchy uses, with thanks. hyprshell (a switcher with a window list, 4.10.8, working with Lua settings since May 2026) was considered and not needed.

### D-34 · No taskbar, and no minimise
**Decided by Javier**, after the taskbar and minimise were built in the test machine: *"let's not do a application bar better, and let's forget about the minimizing function, please."*
- **No list of open apps in the top bar.** Waybar stays the top bar (D-17), without a taskbar section.
- **No minimise anywhere:** no minimise button on title bars, no Win + PgDn, and apps are told to show only **maximise and close** (`button-layout` = `:maximize,close`).
- **This replaces the minimise and taskbar parts of D-31**, and drops Win + PgDn (minimise) from the key map (D-29). The title bars (hyprbars) and never blocking apps' maximise requests stay.
- The taskbar prototype (Waybar's taskbar, the minimise helper and the "bring back" settings) was removed from the test machine and the repository. It is in git history (`bdb244a`) if it is ever wanted again.

### D-33 · Title bars with three buttons on every app that can have them; a little more space
**Decided by Javier:** *"our alacritty terminal when opening in KognogOS, it should have buttons to minimize, maximize, and close. Not as Omarchy. Same for all apps, if available."* And: *"Can we add a little more padding to windows, maybe like 3 more points?"*
- **Alacritty keeps KognogOS's `decorations = "Full"`**, which on Hyprland makes Alacritty draw its own title bar. The test machine's settings use `"None"` (no title bar). Every app that can draw its own title bar gets minimise, maximise and close (`button-layout`, D-31); hyprbars covers the rest.
- **Gaps grow by 3:** 8 between windows (was 5) and 13 at the screen edges (was 10). Applied in the VM 2026-09-29 and read back. *(2026-10-01, Javier: the space between snapped windows halved: `gaps_in` 4, which leaves 8 px between two windows instead of 16. The edges stay 13.)*

### D-32 · New windows open floating, at 80 % of the screen, centred
**Decided by Javier:** *"can we open windows by default floating, 80% of the screen size, centered?"* Every normal window opens floating at 80 % of its screen's width and height, centred. Dialogs ("modal" windows, like "Are you sure?") keep the size they ask for. An app that asks to be maximised in its first moments (Chromium remembers "maximised") is set back to floating at 80 %, while its maximise button keeps working afterwards. **Alt + F4** closes the active window (D-29).
Found on the way, in the test machine only: its settings force every Chromium-based browser to tile and block every app's maximise request. The test machine's settings are filtered so hypeForge's own behaviour can be tested; hypeForge adds neither rule.
Proven in the VM 2026-09-29: Chromium and a terminal both opened floating at 1024×640 on a 1280×800 screen, centred. **Not yet proven:** that a real dialog keeps its own size.

### D-31 · Window buttons, and where minimised windows go
**Decided by Javier**, after testing snapping in the test machine: *"if I minimize, where do the app goes? there is not a bar showing open apps."*
- **Every window gets minimise, maximise and close, top right.** Apps that draw their own title bar read one desktop setting, `button-layout`, which hypeForge sets to `:minimize,maximize,close` (it was `appmenu:close`, close only). Windows with no title bar of their own, like terminals, get **hyprbars**, the Hyprland team's title-bar add-on, once it is proven with Lua settings.
- **hypeForge never blocks apps' maximise requests.** The test machine's settings block them for every window (`suppress_event = "maximize"`), which would make the maximise button do nothing.
- **Open apps show in a taskbar inside the top bar** (Waybar's taskbar section). Clicking an app's icon brings it back or minimises it.
- **Minimised windows park on a hidden workspace** and come back when their icon is clicked. Hyprland 0.56 cannot react to an app's minimise request by itself; Hyprland added a `minimize` event on 2026-09-01 ([#16071](https://github.com/hyprwm/Hyprland/pull/16071)), which ships after 0.56.2. Until then a small hypeForge helper does it.

### D-30 · Win + Up twice maximises, Win + Down comes back
**Decided by Javier.** Win + Up on a window already at the top (a top half or top quarter) maximises it, and Win + Down on a maximised window returns it to its half. This goes one step past Plasma's rules. It is safe on the test desktop because its three monitors sit side by side, so Up and Down never need to jump to another screen. Win + PgUp still maximises too.

### D-29 · The key map: Plasma's keys keep their jobs
**Decided by Javier:** the key map in [DESIGN.md](DESIGN.md#the-key-map) is approved as written. Every Plasma key used on the test desktop today does the same job in hypeForge. Four keys are new: Win + E (superfile), Win + Shift + C (colour picker), Ctrl + Esc (btop) and Win + T (floating or tiled). Plasma-only extras are dropped. Minimise, restore, Alt + Tab and the snapping itself are built in Phase 2 (#5). Like every pick (D-23), any key can change later, in the folder.

### D-28 · The portable folder holds a full copy
**Decided by Javier:** option A in [DESIGN.md](DESIGN.md#one-portable-folder). `~/.config/hypeforge/` holds **every setting in full**, so copying it alone rebuilds the desktop, even with a different hypeForge version. When a new hypeForge version improves a default, the app shows the change and asks before touching the folder. The layout is approved with it: apps reach their settings through links, one computer's details live in `machines/<hostname>/`, backups and undo live outside the folder in `~/.local/state/hypeforge/`, and system files sit in `system/` under their real path. What is still open for #7 is the round-trip test: build, copy to a clean machine, apply, and get the same desktop.

### D-27 · We do not compare. We are grateful
**Decided by Javier:** *"We do not compare ourselves with Omarchy. We are just grateful to them and any other developer for their applications. We do not compare. Our picks are simply picks."*
**What it means:**
- **Omarchy is where we learn, not a yardstick.** Nothing in hypeForge is framed as "better than" or "different from" Omarchy or any other project. This refines D-4.
- **Our picks are simply picks** (D-14 to D-26). They need no justification against what someone else chose.
- **Credit stays.** Anything adapted from Omarchy (MIT) or another project keeps its notice and is credited, and the README thanks the people whose work we build on.
- **The Omarchy test machine** stays useful as a known-good Hyprland setup: it proves our test machines can run Hyprland at all. It is not a comparison run in the test matrix.
- The "comparison note" that issue #3 asked for is dropped, and #3 is closed.

### D-26 · USB drives, the password wallet, the power menu and printers
**Decided by Javier**, agreeing with the leans in [RECIPE.md, jobs 27–30](RECIPE.md#27-auto-mounting-usb-drives-and-disks), with job 29 re-read for Walker (D-18).
- **Job 27, USB drives: udiskie + gvfs.** udiskie mounts removable drives when they are plugged in, with a rule to ignore internal disks, including the Windows NTFS partition. gvfs lets the GTK file window (D-16) list drives. **hypeForge marks `udisks2` as explicitly installed**, because today only KDE's `solid` keeps it and it would leave with Plasma.
- **Job 28, password wallet: KWallet on its own.** It already holds this machine's secrets. `kwallet-pam` stays, greetd's login settings unlock it (D-15), and Chrome and Brave are pinned to `--password-store=kwallet6`. Only one password safe runs at a time.
- **Job 29, power menu: a Walker list** (Lock / Log out / Restart / Shut down), drawn the way Omarchy 3 drew its menus (`walker --dmenu`). No extra menu app. Under uwsm (D-25), **Log out calls `uwsm stop`**. How hyprshutdown's polite close fits with uwsm's shutdown is checked in Phase 2.
- **Job 30, printers: system-config-printer**, already installed and independent of Plasma.

### D-25 · Hyprland starts through uwsm
**Decided by Javier.** This differs from the lean (Hyprland's own `start-hyprland`). uwsm is Omarchy's path ([RECIPE.md, job 26](RECIPE.md#26-how-hyprland-is-started-session-start)). The login screen stays greetd + tuigreet (D-15), which starts the "Hyprland (uwsm-managed)" session.
**What it means** (from the [Hyprland wiki's uwsm page](https://github.com/hyprwm/hyprland-wiki/blob/main/content/useful-utilities/uwsm.md), read 2026-09-29, which calls uwsm "for advanced users" with "its issues and additional quirks"):
- **Background helpers run as systemd user services** (for example `systemctl --user enable hyprpaper.service`), not as start lines in Hyprland's Lua. Apps started from keys and Walker are prefixed `uwsm app --`.
- **Environment settings** (theme, cursor, NVIDIA and toolkit variables) go in `~/.config/uwsm/env`, and `HYPR*` / `AQ_*` ones in `~/.config/uwsm/env-hyprland`, not in `hyprland.lua`. Both are inside `$HOME`, so the one-folder rule (D-8) holds.
- **Never quit Hyprland directly.** Log out with `uwsm stop`, or the ordered shutdown is forced.
- **uwsm runs XDG autostart entries.** Checked on the test desktop the same day: it would also start `nm-applet` and `print-applet` (not wanted, since jobs 15 and 30 chose other tools), plus `input-remapper-autoload` (the G13), `pam_kwallet_init`, Dropbox and Insync (wanted). **hypeForge must switch off unwanted entries** with `Hidden=true` copies in `~/.config/autostart/`.
- `uwsm` 0.27.0 is in `extra` (★1.2k, commits 2026-09). Not installed yet.
- **Not verified:** whether a uwsm session keeps start-hyprland's crash recovery (restart into safe mode). It is tested in a VM.

### D-24 · Monitors, night light, colour picker, editor, viewers and media
**Decided by Javier** ([RECIPE.md, jobs 19–25](RECIPE.md#19-arranging-three-monitors)).
- **Job 19, three monitors: hypeForge writes the three monitor rules itself**, with the exact mode `2560x1440@144` and fixed positions, not Hyprland's `preferred` mode. **nwg-displays** is the drag-and-drop fallback. Checked 2026-09-29: the kernel lists `card1-DP-1`, `DP-2` and `DP-3`, each at 2560x1440 (the refresh rate is confirmed in Phase 2). ddcutil reported all three as `DP-1` (D-20), so the kernel's names are the ones hypeForge uses.
- **Job 20, night light: hyprsunset.** New, since Night Light was off on Plasma.
- **Job 21, colour picker: hyprpicker**, with `wl-clipboard`.
- **Job 22, text editor: Fresh**, the KognogOS default, already installed.
- **Job 23, image viewer: imv.**
- **Job 24, PDF viewer: Zathura** (+ `zathura-pdf-mupdf`). PDF forms are filled in the browser. Okular leaves with Plasma.
- **Job 25, video and music: mpv + mpv-mpris + cliamp.** mpv plays video and music, and `mpv-mpris` makes the media keys work. **cliamp** is Omarchy's Winamp-style terminal music player. It is **AUR only** (`cliamp` 2.3.0, updated 2026-09-28), the second AUR pick after Walker (D-18).

### D-23 · Every recipe pick is a first try
**Decided by Javier:** *"We can try them out. If they don't fit what we want to do, we can always replace them."* The recipe choices are the starting set for Phase 2, not a final list. Living in the desktop (Phase 2) is the real test. A pick that does not fit becomes a numbered finding and is swapped for another option from its job in [RECIPE.md](RECIPE.md), with a new decision entry. The portable folder (D-8) keeps a swap cheap.

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
**Decided by Javier:** [Omarchy](https://github.com/basecamp/omarchy) (MIT) is *"our reference, definitive."* **Refined by [D-27](#d-27--we-do-not-compare-we-are-grateful), 2026-09-29:** we learn from it and are grateful for it; we do not compare ourselves with it.
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
