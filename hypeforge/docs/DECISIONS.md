# hypeForge — decision log

*Every decision that shapes hypeForge, dated, with who made it and why. Newest first.*
*A decision here is only reopened by Javier. **Proposed** entries are suggestions still waiting for his answer.*

---

## 2026-10-10

### D-85 · No Control Strip — one place for each thing (Javier, 2026-10-10)
Once the status icons were back on Mac OS 9's menu bar, the Control Strip (bottom-left, D-72 / M-3) only repeated them — and it surprised Javier on his desktop ("a bar on the bottom of the screen with tons of icons!!!!"). His call: *"no need to have same buttons in several places. let's keep the tray as is, forget about the strip. Let's simplify here."* The strip is removed with everything only it used (its applet, its panel view, the panel's stay-open and `--keep` modes, the restart-on-apply list). The tray and status icons stay on the menu bar. The switch bench now proves the style helpers come and go with Windows 11's Taskbar applet.

### D-84 · Win + Space opens the style's own launcher; the menus have keys (Javier, 2026-10-10)
His first look at Mac OS 9: Win + Space opened the Rice's list, and Window · Special · Help had no underlined letter and key (Workspaces and Favorites did). Now Win + Space runs `hypeforge-sections key`, which reads the style's `[layout] launcher`: **"start-panel"** opens Windows 11's Start, **"emblem-menu"** Mac OS 9's emblem menu as a list (`hypeforge-menubar open emblem`); any other — the Rice's, or KDE's and COSMIC's not built yet — is the usual list. The menu bar's menus open as lists by his letter rule: **Win + O** Window, **Win + I** Special, **Win + P** Help, on every style (first shipped as I · P · H: Win + H was already `$mod+$left` and Sway raised its error bar — `scripts/check-keys.py` now resolves `set $x` names and refuses one key bound twice). Tests prove each style's launcher, and that hypeForge Settings opens through its launcher entry.

### D-83 · A style takes its helpers with it when you switch away (2026-10-10)
Mac OS 9 starts two helpers (the Menu bar applet and the Control Strip); Windows 11 starts the Taskbar applet. Sway's `exec_always` starts them, but nothing stopped them on a switch — the Control Strip would have stayed on the Rice. Now `hypeforge-theme apply` (and `undo`) stops the applets other styles name and the new one doesn't, **by their saved process number only, and only when that process is still the applet** (a number can be reused; never by searching command lines). Tested both ways (a reused number is left alone); `scripts/switch-bench.py` now checks the strip appears on Mac OS 9 and is gone on every other style — 16/16, and 11/16 with the stop switched off. Same evening: applets that read the colours once (the strip) are restarted on every apply (`RESTYLE`), after the strip kept Light Gray's white on Mocha.

### D-82 · Floating windows are tucked away when you click what they cover (Javier, 2026-10-10)
A floating terminal over a tiled, full-screen Chrome; clicking Chrome left the terminal on top — Sway always draws floating windows above tiled ones. Javier: *"It is not about Chrome … I am using this like a user. What I am doing, someone will do it. We cannot ask someone to don't do something just because."* Option 1, like minimised: the **Tuck applet** (`applets/tuck/`) watches focus; when a tiled window is focused, the floating windows on its workspace that **cover it** go to Sway's scratchpad — not one beside it, not one of the same app (a dialog), not a sticky one. The taskbar shows a tucked app dimmed and a click brings it back on top; **Win + −** too; Alt + Tab later. Benched: `scripts/tuck-bench.py` 7/7. **Same day: focus on a click only** — Sway's focus-follows-mouse made just moving the pointer off a floating window tuck it away (Javier: *"lose focus is only when I click (and in the future using ALT+Tab) on another app. Not when the mouse is not over it"*); `focus_follows_mouse no` in sway/config.

### D-81 · Corners are the person's choice, for every style and theme (Javier, 2026-10-10)
On the Rice, live: *"for all themes, we need an option to switch between rounded and straight corners for sure. I am liking the straight corners a lot."* A setting saved with the look, `hypeforge-theme corners straight|rounded|style`: **straight** makes every corner square — the bar's areas and pills, pop-up panels (their round buttons and sliders too), the launcher's lists, notifications, the FX login's windows; **rounded** rounds what a style left square (windows 12, pop-ups 10); **style** (the default) keeps each style's own. It stays through later style or theme changes; COSMIC's roundness choice gives way to it. Not yet covered: the lock screen's own stylesheet (a fixed file, `sway/gtklock/style.css`).

### D-80 · hypeForge FX: a quiet frame and room at the screen edges (Javier, 2026-10-10, replaces D-79's "no frame")
With no frame line (D-79) the tiled windows looked flat: Mocha's windows and the dark wallpaper are almost the same colour, a dark shadow on a dark background doesn't show, and windows ran to the screen edges. Four looks were rendered on the hidden SwayFX; Javier picked **C**: a **quiet 2 px frame** (the window in use `border.subtle*2+border.strong` = Mocha `#585b70`, the others `surface.overlay` = `#313244`), **10 px at the screen edges** (first 20 — 10 inner + 10 outer — then, Javier 17:55: "too much": `gap_outer = 0`, the edges equal the space between windows), the others still dimmed 0.12. Quiet colours also hide most of F-56's corner notch (it shows with a bright frame). Plain Sway unchanged. New in the theme step: a colour may blend roles (`role*2+role`).

### D-79 · hypeForge FX: rounded windows without a frame line, the others dimmed (Javier, 2026-10-10)
F-56: SwayFX 0.6 draws a notch where a big window's rounded corner meets its frame line, and the curve is stepped; not a setting, not the shadows (tested with every shadow off), and a one-pixel patch fixed only half. Javier picked **1 + 3**: in the FX login, windows keep their 12 px rounded corners and shadow but **no frame line** (`[fx] frame = false`), and the focus shows by **dimming the other windows a little** (`dim_inactive = 0.12`); the float key keeps "no frame" in FX (`bindsym --no-warn`, or SwayFX shows its config-errors bar). Plain Sway keeps its 2 px frame. And the notch is **reported to SwayFX** with our reproduction (Javier's OK).

### D-78 · The build plan approved: Rice first; today's look stays as Classic; themeForge; the Rice ships as the default (Javier)
The phase-4 plan (shared pieces first, a test of Javier's after every step) with his answers: B-1 the styles in this order — **Linux Rice, Windows 11, Mac OS 9, KDE, COSMIC, macOS**; B-2 today's look stays as a seventh style, **hypeForge Classic**; B-3 the switcher is **themeForge**, a Forge app with **a full page in hypeForge Settings** and **a tray icon for a quick switch** (its icon in KognogOS colours, like nightForge's); B-4 **the Linux Rice is KognogOS's default style** (*"Linux Rice, of course :D"*).

### D-77 · Style 6 approved: COSMIC, tiled — all six styles approved (Javier)
Review 7, all five as proposed: C-1 **the top panel and the dock**, C-2 **slightly round** by default (Round and Square stay choices in hypeForge Settings), C-3 **the active hint** (a 3 px frame in the theme's bright colour), C-4 **the launcher and the App Library** with group folders, C-5 **each applet its own pop-up**. No COSMIC software (D-56). Spec: `docs/design/look/styles/cosmic/style.toml`. With it all six styles of the look program are approved (D-71, D-72, D-74, D-75, D-76, D-77) on the approved 25 themes (D-73); next is the build plan (look program phase 4).

### D-76 · Style 5 approved: KDE Plasma, tiled (Javier)
Review 6, all five as proposed: K-1 the **floating panel**, K-2 **the pager** (six little screens), K-3 **Kickoff as KDE's list** with descriptions, K-4 **Breeze-style title bars on**, K-5 **one tray pop-up** with a page per setting. Plasma's look from hypeForge's own pieces, no KDE software (D-56). Spec: `docs/design/look/styles/kde/style.toml`.

### D-75 · Style 4 approved: the Linux rice, tiled; every theme brings its wallpaper (Javier)
Review 5: R-1 **one floating island with three areas** (not three separate islands): the emblem and workspace pills, the clock and what's playing, the system modules, tray and power; R-2 **numbered pills, the active one named**; R-3 **the wallpaper follows the theme, for every theme**: each of the 25 brings its own generated picture (`docs/design/look/review-5-rice/make-wallpapers.py`) and switching the theme switches the wallpaper, in every style, unless the person picked one of their own; R-4 a bright frame on the window in use (see-through, frosted terminals on SwayFX); R-5 the **big-button power menu**. Spec: `docs/design/look/styles/rice/style.toml`.

### D-74 · Style 3 approved: modern macOS, tiled (Javier)
Review 4, all five as proposed: MA-1 the Dock **always there** (a second Waybar; windows tile above it), MA-2 **Spotlight and Launchpad**, MA-3 Control Center's blocks (Wi-Fi/Bluetooth/VPN, Do Not Disturb, Night light, Screens, sound, what's playing), MA-4 **Mac OS 9's menus kept** (Special moves into the emblem menu), MA-5 **frosted** bar, Dock and panels on SwayFX. Spec: `docs/design/look/styles/macos/style.toml`.

### D-73 · The foundation approved: palettes v2, 25 themes (Javier)
Review 1, round 2: F-1 the black/white/gray/orange theme is called **Ember**; F-2 its pop stays **cream**; F-3 the light themes' pops are lively enough; F-4 **KognogOS Mocha** keeps its five tiny brightness changes from Catppuccin so it passes our readability checks. The 25 themes (`docs/research/look-2026-10/palette/palettes.toml`, schema 2) are the colours every style is drawn in; KognogOS Mocha is the default.

### D-72 · Style 2 approved: Mac OS 9, tiled (Javier)
Review 3, all five as proposed: M-1 the menu bar as drawn (emblem menu with group submenus · bold app name · Workspaces · Favorites · Window · Special · Help … clock · Application menu), M-2 **real title bars on** (centred), M-3 **the Control Strip** holds the tray and status icons, M-4 **Noto Sans bold**, M-5 **the crisp shadow with SwayFX**. Spec: `docs/design/look/styles/mac-os-9/style.toml`. Its colours follow D-70 and the in-window contrast note of D-71.

### D-71 · Style 1 approved: Windows 11, tiled (Javier)
Review 2: *"A killer proposal. Sold!"* — and Javier's answers: W-1 taskbar icons **on the left** (centered stays an option), W-2 yes, the **KDE-style Start** as drawn (no recent files), W-3 the six Quick Settings tiles (Wi-Fi, Bluetooth, Night light, Do Not Disturb, Screens, VPN), W-4 **soft windows with SwayFX** (square on plain Sway), W-5 **a taskbar on every screen** (tray and Quick Settings on the main one). The style file `docs/design/look/styles/windows-11/style.toml` is the approved spec; it is built after the six reviews (look program phase 4). Javier, same day: *"consider my comments for windows 11 proposal for better themed color and contrast combinations. But we are very close"* — the layout and shapes stand; its colours are redone with the 60-30-10 palettes (D-70): neutral glass for the taskbar, the theme's colour on Start's sidebar, selected rows and the focused border, the pop colour on toggles and badges. And: *"Inside the window's colors are too much of the same. That is where more contrast is needed"* — inside a window, its parts (tab strip, toolbar, side panel, content, cards) step through clearly different neutral levels, with the theme's colour on the part that leads.

### D-70 · Colour themes are 60-30-10, not one colour everywhere (Javier)
Javier on review 1: the samples were "too one sided of the color… extremely monotone". Every colour theme now mixes **white, black and grays** with its colour: about 60 % neutral foundation (windows, panels), 30 % the theme's colour in big secondary places (the bar, panel headers, selected rows, the focused border), 10 % a contrasting "pop" colour for small important things, plus more contrast between layers. Middle themes sit **"middle to darker"**. A new **black · white · dark gray · orange** theme (the emblem's orange). "The Kognog colours" are **KognogOS Mocha**, today's Catppuccin Mocha combination, its own theme, not "purple". Q-5 picks: neutral themes use the emblem blue; the focused border wears the theme's colour; urgent moves away from red in red/pink themes; the emblem orange is the orange theme's colour, otherwise the logo's.

### D-69 · Wallpapers: our generator, plus hand-picked free-licence art (Javier)
Q-3 B: the generator makes every theme's five; real illustrations and photos may be added one file at a time from sources whose licence allows shipping (Wikimedia Commons CC0 / CC BY / CC BY-SA), with a credits file. Unsplash, Pexels and Wallhaven are out (their terms forbid it).

### D-68 · SwayFX as a second login; graphical panels from the bar (Javier, amends D-56 and D-57)
Q-1 A: **SwayFX counts as Sway** — Sway 1.12 with rounded corners, shadows and blur. It comes as a second login ("hypeForge FX"); plain Sway stays the default and the safe one, and every style is drawn for plain Sway first, the effects in one optional file. Animations stay off (SwayFX #565/#569). Q-2 A: **small graphical panels may open from the bar** (Start, Quick Settings, calendar, workspaces), Python + GTK with no new packages. The Forge apps stay terminal apps, as they are.

### D-67 · The look program: six styles × 23 colour themes, still tiling (Javier)
*"Where a beautifully stylised Windows 11 desktop exists, what classic Mac OS 9 functionality offered, and KognogOS identity meets."* Six styles proposed and reviewed one by one (Windows 11, Mac OS 9.x, modern macOS, a Linux rice, KDE, COSMIC), each with 23 colour themes and five wallpapers per colour; rounding, shades, shadows, borders; contrast that makes things pop; all inside Sway's (and SwayFX's) capabilities, still tiling with our workspaces and placement. Forge Suite terminal apps keep their look for now. Everything documented for a later theme app. Claude runs it with up to five research helpers; a GitHub Project holds the plan and timeline. The plan: `docs/look-program.md`.

---

## 2026-10-09

### D-66 · "Workspaces & Windows" is two Forge apps: workspaceForge now, windows later
**Decided by Javier:** *"Why don't we work on workspaceForge already. It is HOT topic xD"* and *"Notice I said only workspaces, windows is another Forge app. I like atomized solutions."*
- **workspaceForge** (Forge Suite section `workspaceforge/`, born 2026-10-09): workspace names and order, the apps that open on each one (F-50, #55), sharing. It edits the Workspaces applet's settings; the applet keeps doing the work.
- **Windows** (where a window sits on a screen, which ones float: today's Window Placement and Window Rules applets) becomes its own Forge app later.
- The Settings catalogue's "Workspaces & Windows" line is split accordingly. Also decided the same morning, for F-50: the screens follow an app to its workspace (not in the first ~30 s after login), and shared screens get no special rule.

---

## 2026-10-08 (late)

### D-65 · hypeForge Settings opens on a Home page of cards, each with an icon and three lines
**Decided by Javier** (#46): from two layouts (rows like a table, or cards), **cards in two columns**; then *"can we add some icons to the left menu options representative of what they are, and in the Home page titles? … Per box, 3 rows of relevant content."* Verdict on 0.5.0: *"beautiful. Great for a first version!"*
- Ten cards: Screens, Workspaces, Network, Sound, Printer, Night light, Passwords, Packages, Boot Menu, Terminal — real values, asked in the background, never able to freeze or crash the window. A card opens its page where Settings has one.
- Icons from the Nerd Font every KognogOS terminal uses (not emoji); none on a plain text console.

### D-64 · The launcher's groups are the standard kinds of app; where an app opens is a separate choice
**Decided by Javier:** *"I know we named them like the Workspaces, but in reality what should apply is the standard names all OS uses to classify the applications… so when people install something, or want to use something, they know where they are or should be."* On where they open: *"I will leave that to you."*
- **Groups:** Development, Education, Games, Graphics, Internet, Multimedia, Office, Science, Settings, System, Utilities, Other — the freedesktop.org main categories, under the names GNOME, KDE and XFCE show. An app goes where its own desktop entry's Categories put it; when it names several, `claim_order` decides (Settings > Games > Multimedia > Graphics > Office > Development > Education > Science > Internet > System > Utilities). Apps that declare nothing (WoW, Chrome web apps, Rofi) are placed by hand. Empty groups are hidden; nothing is left only in "All apps" (95 of 95 placed).
- **Where they open (Claude's choice, keeping the old places):** picked from its group, an app opens on the group's workspace — Internet 1, Office and Development 2, Multimedia 3, Games 4, Settings 6 — or on its own line in `[workspaces]` (the monitors on 5, Alacritty on 2); Graphics, System and Utilities open where you are. Search and Favorites still open where you are.
- Replaces D-52's "the first screen is the workspaces". Under the standard, **bitlaForge and Help & Keys move from Settings (D-63) to Utilities** (what their own entries say); hypeForge Settings stays first in Settings.

### D-63 · The launcher's Forge Suite group is gone: its apps live in Settings, with hypeForge Settings first
**Decided by Javier:** *"Everything inside the Forge Suite app launcher group, move it to Settings, and delete the Forge Suite group/folder. Then add the hypeForge Settings app to Settings too."*
- The **Settings** section lists hypeForge Settings, then displayForge, nogForge, grubForge, alacrittyForge, bitlaForge and Help & Keys, then the printer settings and the other settings programs.
- **What changes:** picked from the launcher, these apps now open on the **Settings workspace (6)**, like the rest of that section. The Forge Suite group opened them on the screen you were on (Javier, 2026-10-06); that rule went with the group. Javier can ask for it back for Settings.
- Same day, same spirit: Thunar replaces mc in Favorites until fileForge exists.

---

## 2026-10-08

### D-62 · Inside hypeForge Settings an app has no Quit; Settings closes it, and each app asks its own question
**Decided by Javier**, after running every app inside Settings: *"q still quit apps. We need to create a command for all apps. When they are open with the command `[app]Forge --hypeForge` … it will not show the Quit option, and disable the quit shortcuts."* Then, from the options, **"ask each app, its own way"**.
- Every Forge app accepts `--hypeforge` (any capitals). Settings starts the Forge pages with it (`forge = true` in `settings.toml`). Started that way the app has no Quit in its menu bar, and Q, Esc (Help & Keys) and Ctrl+Q do nothing.
- Settings' Quit asks every app to close (forgekit's `host_quit`, through SIGUSR1). An app with nothing unsaved closes at once; one with unsaved work is shown, and asks its usual "Save first / Quit without saving" (displayForge: "Apply your changes?"). Settings closes after the last one has closed.
- The option is for Settings only, so it's left out of `--help` and the man pages, but it's written down in every app's README, manual, CLAUDE.md and changelog.
- **Javier's run 2 (evening):** *"Shortcuts always should use the first letter, unless already being used, then we pick in sequence the next."* forgekit picks every underlined letter this way (Help H and Quit Q always; an app's own Ctrl keys count as taken). A menu's number pressed again closes it, the open menu's title is lit, and **About and License open in the content area, not in a window**.
- **Also from the same run:** every underlined letter in a menu bar is a Ctrl shortcut, every entry has a number (Help included), and the bottom bar says "1-N menu" (forgekit 0.10.0). Button labels read "Words (key)", e.g. "Save Changes (s)" (Javier, 2026-10-03). **Proposed (Claude, to confirm with Javier):** standard title case, so small words such as *the*, *of* and *and* stay lowercase, as in nogForge's already approved "Update the Ticked Ones (u)".

---

## 2026-10-06

### D-61 · The password helper is called sudoForge; the keyring comes later, as its own step
**Decided by Javier**, from the options: the name **sudoForge**, and the keyring (where apps keep saved logins) **"later, separate step"**.

**What it means:**
- sudoForge is the D-56 app: one helper for the whole Sway session that answers polkit's admin pop-up (F-44, #26) and `sudo -A` / `nog` (F-42, #24) with forgekit's password box in a small floating window. It is born as its own section of the Forge Suite (D-60), with its own version, tags and AUR package.
- **The keyring is not in version 1.** Found today: Claude Desktop on Sway has no keyring (`safeStorage … basic_text`), so its login is kept as plain text and lost on restart. That gets its own research after sudoForge works. KWallet is a KDE piece, so it is not the answer (D-56).
- Facts measured on this computer before the design: no polkit agent runs for the Sway session, `SUDO_ASKPASS` is unset, and a new Alacritty window with forgekit loaded is on screen in about 0.35 s, so the box can be opened only when needed.

## 2026-10-05

### D-60 · One Forge Suite repository; hypeForge is its first section
**Decided by Javier:** *"So we do not have 100,000 repositories of Forge Suite apps, let's add them all inside the Forge Suite repository, each with its own section… Then hypeForge is part of the Forge Suite, and now KognogOS is about nog and the Forge Suite of apps… which sounds very strong!"* Then, from the options: **phased**, and **A — rename this repository**.

**What it means:**
- `jetomev/hypeforge` is renamed **`jetomev/forge-suite`** (GitHub redirects every old link; the issues and history stay). hypeForge moves into its own section, `hypeforge/`; every new Forge app is born in a section next to it — no new repositories.
- **Phased:** forgekit and the shipped apps (alacrittyForge, bitlaForge, nogForge, grubForge last — it has the most users and outside contributors) move in later, one at a time, each tested; their old repositories are archived with a pointer. **nog stays its own repository**: KognogOS = **nog + the Forge Suite**. **mindForge stays outside too, for now** (Javier, 2026-10-05: *"mindForge, the only one thing we keep out of the Forge Suite for now"*).
- Each app keeps **its own version, tags (`<app>-vX.Y.Z`) and AUR package**; the release rules are adapted when the first shipped app moves in.
- On the test desktop the folder is `~/Programs/forge-suite/`, with `~/Programs/hypeforge` left as a shortcut so the running desktop keeps working.

### D-59 · Every setting is a Forge app; hypeForge Settings is the control centre that holds them
**Decided by Javier:** *"All apps that we use that can only be configured by touching a config file should be part of the Forge Suite… the workspace manager = Forge app, monitor(s) manager = Forge app, window snap manager = Forge app, launcher = Forge app… same for all rules, help, idle, lock… cliamp settings, Waybar settings, fuzzel settings, Alacritty, etc. Then hypeForge Settings is a Control Center from where we can open the apps, like the KDE Settings window. A list of configurable functionalities and apps on a menu to the left, and then in the display area to the right, the apps open (an inside terminal, where we will run the apps)… If we modify the Forge app, it is transparent for the rest, especially for the holder… unless they connect."*

**What it means:**
- **Each configurable thing is its own Forge Suite app** — our applets (workspaces, monitors, window placement/snap, launcher, rules, help, idle, lock) and every outside program set up only by a config file (cliamp, Waybar, fuzzel, gtklock, Alacritty → alacrittyForge, GRUB → grubForge…). Each is a full application: own repo, package, version; runs on its own too.
- **hypeForge Settings** is the control centre: a list on the left, and on the right a terminal pane where the chosen Forge app runs, with its own forgekit menu bar. It holds the apps; it does not copy them.
- **forgekit is the visual standard** every app follows (same look, widgets, settings handling), so swapping one app is invisible to the rest.
- **Proposed by Claude, to settle as we build:** (1) the settings file is the contract between apps that connect (they read each other's files, never each other's code); (2) a running helper (e.g. the workspaces helper) stays separate from the Forge app that sets it up; (3) the release cost of many small apps — decide later whether the smallest share one repository; (4) a spike first: a full Forge app inside forgekit's terminal pane (colours, mouse, keys).
- The Forge Suite candidate list becomes the **roadmap**, published on kognogos.org with the upcoming apps. hypeForge's description, README, banner and images, on GitHub and on kognogos.org, are rewritten for the Sway path (order: text first, then the banner, each shown to Javier before it goes public).

### D-58 · "hypeForge Settings" is the name; the lock screen and idle timers are set there
**Decided by Javier:** *"Add this one to be set up using hypeForge Board — let's call it better 'hypeForge Settings', another to the bag, same for the screen idle and lock, to be configured using hypeForge Settings."*

**What it means:**
- The place where every applet is switched on/off and set up (D-47's "Settings Board") is called **hypeForge Settings**. Renamed in every current file; older entries in this log keep their wording.
- Two more pages for it: **Lock screen** (gtklock's background, blur strength and darkness, clock and date, password box, colours) and **Idle and lock** (minutes to lock, minutes to screens off, the lock key).
- The lock screen as Javier approved it (2026-10-05, *"it is perfect my friend"*): **gtklock** — a rounded password box with a dot per key, a big 12-hour clock and the date, Catppuccin Mocha, over the KognogOS wallpaper blurred once (GaussianBlur 18, 20 % darker; GTK3 cannot blur live). swaylock was tried first; its ring was not wanted. Locks on Win + Escape, Lock Screen in Win + Space, and after 30 minutes; screens off after 60; no sleep.

### D-57 · The three-part rule: terminal first, Sway-compatible, smallest footprint
**Decided by Javier:** *"Rule: Everything we do has to be CLI/TUI (1), SWAY compatible (2), or minimum installation and dependencies as possible (3). I want a slim, quick, low memory, fast window tiling/manager system."*

**What it means:**
- Every pick is measured in this order: **(1)** a terminal app (CLI or TUI) wherever one exists; **(2)** it works under Sway (Sway's own family first: swaylock, swayidle, swaybg…); **(3)** the fewest packages and the smallest install. A choice that brings back KDE, GNOME or Hyprland pieces fails (2) and (3) — see D-56.
- Applied first on 2026-10-05: the lock screen moves from Hyprland's hyprlock to **swaylock + swayidle** (87 KiB + 36 KiB, Arch `extra`); KCalc and Elisa (KDE apps) get terminal replacements; options are compared with their size and dependencies written out.

### D-56 · KognogOS ships with Sway only; the password helper is our own Forge app
**Decided by Javier:** *"Remember right now we have KDE installed, but the idea is not to have it in KognogOS. KognogOS will ship only with Sway. The password handler needs to be either something Sway can handle, or something developed by us (which we will have to place in our list of self-developed apps)."* Then, from the options: **our own, nothing meanwhile**.

**What it means:**
- **KDE is not part of KognogOS.** Plasma stays on this computer only as the fallback login while hypeForge is built (D-6). No hypeForge pick may lean on a KDE piece: KDE's password pop-up (polkit-kde-agent) and password window (ksshaskpass) are out, and so is anything that pulls KDE, GNOME or Hyprland libraries back in.
- **Options looked at (2026-10-05):** polkit-gnome (GTK3, legacy), mate-polkit (GTK3), lxqt-policykit (Qt + KDE's kwindowsystem), hyprpolkitagent (four Hyprland libraries), soteria (not found by `nog search`). Sway itself has no password helper.
- **Our own:** a new Forge Suite app (name: Javier's call) that runs for the whole Sway session. When an app asks the system for admin rights (polkit) — and when `sudo` or `nog` needs the password (askpass) — it opens a small floating terminal window with forgekit's password box. Built from what forgekit 0.6.0 already has (its polkit agent and password box), so one tool answers both F-44 (#26) and F-42 (#24).
- **Nothing installed meanwhile.** Forge apps already ask for the password inside the app; terminals ask in the terminal. F-44 and F-42 stay open, pointing at the new app.

## 2026-10-04

### D-55 · Help & Keys is a small Forge app: tabs, one look, text that wraps
**Decided by Javier:** *"They need a holder with tabs, which is going to become a theme in our setup… And let's just access it using the Help & Keys app, instead of a whole section for it"*; *"Let's use forgeKit to create this app, please, so we keep consistency with our other apps"*; no Help menu inside it; the key chart as tables *"with the same look of the other apps… rows with two alternate colors"*; the same design on every page; text that wraps on a small screen (*"the horizontal scrolls do not make lot of sense"*); and the tab names *Keys · Start · Workspaces · Windows · Apps · About · Quit*. Then: *"Everything works! Great job."*

**What it means:**
- `applets/help/hypeforge-help` is a **forgekit app** (title bar, menu-bar sections as tabs, hint bar, Quit), version 0.1.0. Win + F1 and the launcher's Help & Keys open it **directly** in its own floating window (no fuzzel menu any more); `hypeforge-help <page>` opens it on one page.
- **The tabs** come from `applets/help/guide/pages.toml` (tab name → guide files, in order); Keys is always first. Windows = Window Placement + Window Rules.
- **One look on every page:** the guide's Markdown is turned into the same widgets as the key chart — accent title and headings, text, list items, and **our own wrapping tables** (rows of cells: first column fixed, at most 40 % of the window; the last wraps; forgekit's header colours, two alternating row colours). No sideways scrolling anywhere.
- **Keys:** ← → or 1–6 change page, ↑ ↓ / Page Up / Page Down scroll, Q or Esc close. forgekit's own Help (F1 / Ctrl+H) is switched off in this window.
- The old page viewer (glow + less, `show-page`) is gone. Found for forgekit: its menu bar does not wrap and is cut off on a narrow window (every Forge app) — short tab names solve it here.

### D-54 · Help (applet 6): one source, shown on Win + F1 and on the Board; the KognogOS wallpaper
**Decided by Javier:** *"We need to have a good help for all the functionalities, applets, and also the key combos chart"*; *"the help has to be both accessible with Win+F1 and part of the hypeForge Board app."* On the first look: the help pages *"need a border and an instruction telling people how to exit the screen (q)"*, and *"I would prefer the Key combos screen is the same as the rest of the help, it looks different and disruptive."* Also: *"can you add our KognogOS background."*

**What it means:**
- **One source, two readers:** `applets/help/keys.toml` (the key chart: groups of keys + plain words + the exact Sway key names covered) and `applets/help/guide/*.md` (one page per applet). Win + F1 shows them now; the hypeForge Settings Board will read the same files.
- **Win + F1** (and **Help & Keys** in the launcher) opens a small menu: Key chart, then Guide · one page per applet. Every page — the key chart too, written from `keys.toml` each time — opens in the same floating window (white 3 px border, focused) with a bottom line: *↑ ↓ Page Up / Down to read — / to search — q to close*.
- **The chart cannot go stale:** `scripts/check-keys.py` compares it with every key in `sway/config` (minus the number keys applet 1 switches off) and runs as the git pre-commit hook (`git config core.hooksPath scripts/hooks`). Tested in the failing direction: a fake extra key stopped it and was named.
- **Found while collecting the keys:** Sway's own Win + 7…0 still opened stray one-screen workspaces; applet 1 now switches off the number keys beyond its workspaces.
- **Window Rules** gained `border` and `focus` options (the help window uses both).
- **Wallpaper:** "Kognog OS Semi – Logo Catpuccin Mocha" on all three screens, through **swaybg** (installed with nog; Sway's own wallpaper helper).

### D-53 · Window Rules (applet 5): small tools float; Alt + F4 closes
**Decided by Javier:** floating for *"dialogs, small tools, and we will see"*; *"ALT+F4 should close the apps, very standard key combination"*; and in the launcher, *"Can be fixed so the search always look for all apps?"* Then: *"everything is working. Excellent!"*

**What it means:**
- `applets/rules/` — settings `~/.config/hypeforge/applets/rules.toml` (`enabled`, one `[[float]]` block per rule: match on app_id / class / title / window_role / window_type, options `sticky`, `size`) + `hypeforge-rules`, started by Sway. Applied to new windows, to open ones, and again after every Sway reload.
- **Floating now:** older apps' pop-ups, dialogs, utility and splash windows; KCalc (16 × 40 % of the screen: KDE apps remember their last size); Network Connections; Print Settings; About windows; password windows; picture-in-picture video (also sticky); Steam's side windows. Sway's own dialog floating stays; **Win + Shift + Space** floats or un-floats any window.
- **Two lessons about Sway's socket:** a `for_window` swallows the rest of its message (so one rule per message), and its actions must be quoted (a comma ends the rule and the rest hits the focused window — which floated this terminal once; fixed).
- **Alt + F4 closes the window** (with Win + Shift + Q).
- **The launcher's first screen searches every app:** the apps sit below the menus, out of sight until you type.
- Found on the way: **no admin-password helper (polkit agent) runs in the Sway session** (F-44, RECIPE job 8).

### D-52 · App Sections (applet 4): the launcher's first screen is the workspaces
**Decided by Javier:** the sketch — Favourites, one section per workspace, All apps — *"Your proposal is perfect. We can start with that one."* Then: every line aligned to the left; *"Under All Apps, still show a list of all apps available, it shouldn't"*; and at the bottom, *"In this order top-down: Lock Screen, Log Out, Reboot, Shutdown."* Favourites get pinned later; apps get added to sections from the applet (the Board).

**What it means:**
- `applets/sections/` — settings `~/.config/hypeforge/applets/sections.toml` (`enabled`, `favourites`, one `[[section]]` per workspace with `icon`, `workspace`, `apps`, `categories`; `[power]` commands) + `hypeforge-sections`, on **Win + Space** (Win + D stays the plain fuzzel search). Read every time it opens; switched off, Win + Space is the plain search.
- **fuzzel draws the menus** (its list mode, with icons); the routine only decides what is in them. Every line carries an icon from the icon theme, so all line up.
- **A section pick opens the app in that section's workspace** (through applet 1), where applet 2 places it. Apps named in a section come first; every other app falls into a section by its own kind (its desktop entry's categories), so the menu works before anything is sorted.
- **Power:** Lock Screen (hyprlock for now; the Sway lock screen is a later job), Log Out, Reboot, Shutdown — the last three ask first with "No" selected.
- **For the Board:** the launcher's look, its colours tied to the active theme, adding/editing/removing sections, adding apps to sections, pinning favourites, every option on/off.
- Javier: *"all aligned now, lock screen works. Looking great so far!"*

### D-51 · The launcher is fuzzel, on Win + Space
**Decided by Javier:** option A first (*"A, Win only if possible, if not Win+Space"*); the Win key alone *"started opening terminals"*, so Win + Space; the terminal launcher showed every program (*"just show applications, not everything?"*), looked like a terminal and could not open btop, so fuzzel: *"Works very well."* And: *"remove the one we aren't using, let's not keep things installed we do not need."*

**What it means:**
- **fuzzel** (`extra`, nog): a small graphical search box of applications with icons, settings in `sway/fuzzel/fuzzel.ini` (Mocha colours, candy-icons, a 10 px corner radius as a first try of softer shapes). Win + Space (and Win + D); Sway's floating/tiled focus switch moved to Win + Shift + Tab.
- **Terminal apps open in Alacritty** (`terminal=alacritty -e`): the Sway session sets no `$TERMINAL`, which is why btop did not open from the first launcher.
- **sway-launcher-desktop was removed** (nog), with its settings and history files. Rule from Javier: nothing stays installed that we do not use.
- Sections, favourites and our look for the launcher: applet 4 (App Sections), next.

### D-50 · Window Placement (applet 2): a fixed fill order, then tabs
**Decided by Javier:** the order — *"Window 1: Screen 1 full screen · Window 2: Screen 1 right to w1 · Window 3: Screen 2 full screen · Window 4: Screen 2 right to w3 · Window 5: Screen 3 full screen · Window 6: Screen 3 right to w5 · Window 7: Screen 2 under w4 · Window 8: Screen 3 under w6"*; beyond that, *"9 and beyond follow the same pattern but stacking with existing windows"*; and with a shared screen, *"they should open following the flow, based on the open windows, shared screen included."*

**What it means:**
- **Its own applet**, separate from Workspaces Management: `applets/placement/` — settings `~/.config/hypeforge/applets/placement.toml` (`enabled`, `screens`, `order` as screen + spot: `fill`, `right`, `under-right`) + routine `hypeforge-placement`, started by Sway.
- **Counts everything visible** on every screen in the workspace on screen (a shared screen included) and puts the new window in the first free spot of the order. Once all 8 are taken, the next go round the order again **as tabs** (9 on window 1's spot, 10 on window 2's…).
- **Left alone:** floating windows and dialogs, and windows that open on a workspace not on screen.
- **Shared code:** both applets talk to Sway through `applets/common/hfsway.py` (Python standard library only).
- Tested by Claude with ten terminals (exact pattern, 10 px gaps, tabs on spots 1 and 2), then by Javier: *"all works perfect!"*

### D-49 · The workspace matrix: a screen can share one space between workspaces
**Decided by Javier:** *"I want to have the possibility to tell the screens exactly which workspace they will share… Screen 1… part of all workspaces with the apps I have open… while the other 2 screen will hold different apps on each workspace… It is kind of a matricial relationship, to activate and deactivate at will by the user using our hypeForge Board."* Then: *"matrix first, all screens own for now."*

**What it means:**
- **A grid:** workspaces down, screens across; each cell is either the workspace's own space on that screen, or a space **shared** with other workspaces on the same screen. Switching between workspaces that share a screen leaves that screen as it is.
- **Settings:** a `[share]` section in `workspaces.toml`, one line per screen, each `[ … ]` a group (`"DP-3" = [["Daily", "Work", "Entertainment"]]`). All empty for now ("all own"). The Board will show it as a grid of switches.
- **Sharing works down a screen, never across screens:** a window can only be in one place.
- **Nothing gets stranded:** when the grid changes, windows in a space no longer used move to the cell that replaced it (tested on and off).
- **The bar's buttons are drawn by the applet** (one Waybar module per workspace), so every screen always shows all of them whatever the grid says; the routine keeps the workspace on screen in `$XDG_RUNTIME_DIR/hypeforge-workspaces.current` and signals Waybar to redraw.
- **Window placement (applet 2) must respect shared cells**, so it comes after this.
- Javier's test: *"everything works, the highlight follows on all three. Both clicking and Win+numbers."*

### D-48 · Workspaces Management (applet 1) and Waybar as the bar for now
**Decided by Javier:** six names, *"Daily, Work, Entertainment, Gaming, Monitoring, Settings (for now — but later we should be able to add, edit, delete workspaces)"*, with *"a flag to switch it on and off"*, shaped as *"a config file with variables, and a routine that reads them and delivers to sway"*, so the Board later becomes *"the visual handler of the config file."* The bar: *"can the workspaces name appear in the top bar, one next to the other, for me to click on them… we can color the active workspace"*, numbered *"1. Daily, 2. Work"*. Our own bar later: *"we can start using one that exist, and then when the setup is done, include it as one of our hypeForge development."*

**What it means:**
- **Settings file** `~/.config/hypeforge/applets/workspaces.toml` (`enabled`, `screens` in order, one `[[workspace]]` block per name, up to 9); **routine** `applets/workspaces/hypeforge-workspaces`, started by Sway, Python standard library only (talks to Sway over its socket). Switched off, it does nothing.
- Each workspace is one Sway workspace per screen (`1:Daily` middle, `11:Daily` left, `21:Daily` right), kept in step: **Win + 1…6** switches all three, **Win + Shift + 1…6** sends a window on its own screen, and a switch from anywhere (a bar click) pulls the other screens along. It re-applies itself after a Sway reload.
- **The bar is Waybar** (`extra`, nog) until our own: all workspaces always shown, "1. Daily"…, active one in the palette's white; the routine writes Waybar's workspace list from the same settings file, so a rename shows on the bar.
- **The mouse stays where it is** when the focus changes screen (`mouse_warping none`): a bar click had dragged it to the middle of screen 1.
- Javier's test: *"the mouse stays put now, everything works."*

### D-47 · Every hypeForge feature is its own applet, switched on and off from one Settings Board
**Decided by Javier:** *"Each functionality we say we are going to develop, let's make it separate so later we can tie them all to a Settings board, to activate, deactivate, and manipulate how it behaves or looks. Like little applets or widgets we can offer using our main hypeForge Settings Board."*

**What it means:**
- **One feature, one applet.** Each piece hypeForge adds on top of Sway is built separately, with its own settings, and can be switched off without breaking the others.
- **The hypeForge Settings Board** is where they all come together: turn each applet on or off, change how it behaves, change how it looks.
- **The first applets** (all from this session):
  1. **Linked workspaces** — four workspaces that span all three screens: Win + 1…4 (or a click on the bar) switches all three together. Sway gives each screen its own workspaces, so each of ours is three Sway workspaces kept in step.
  2. **Window placement** — the same fill order in every workspace (screen 1 = middle, 2 = left, 3 = right): 1 fills screen 1, 2 beside it, 3 fills screen 2, 4 beside it, 5 fills screen 3, 6 beside it, 7 under 4, 8 under 6.
  3. **Folder tabs** — small tabs lined up on the left like folders in a document holder, rounded tops, KognogOS colours, replacing Sway's even tab row (Sway has no setting for that; patching Sway was rejected as a fork to maintain forever). Built in the look phase.
  - Candidate: **apps open in their own workspace** (btop → Settings/Monitoring…), decided with the launcher.
- **The four workspaces:** 1 Day-to-Day (email, browsers, light things) · 2 Work (terminal, AI desktop apps, Fresh, OnlyOffice) · 3 Gaming · 4 Settings/Monitoring (btop, settings apps).

### D-46 · Windows: border only, tabs when they share a space, 10 px gaps, colours from the palette
**Decided by Javier**, after seeing the looks one by one on the real desktop: title bars *"kind of noise"*; border only *"I like it better"*; a stack *"would have been better… like tabs"*; tabs → **"Border only + tabs works wonders."**

**What it means:**
- **No title bars; a 2-pixel border.** Active window: the palette's white; the others: the palette's dark grey. The colours are named once at the top of `sway/config` (`$hf_active`, `$hf_inactive`…) so the KognogOS brand palette (Phase 12) replaces them in one place; for now Catppuccin Mocha (#cdd6f4 / #45475a).
- **10 px gaps** between windows and at every screen edge (measured: 10 at the edges, under the bar, at the bottom and between windows).
- **Windows that share a space are tabbed** (Win + W), not stacked; Sway's tab row is the stand-in for the folder-tabs applet (D-47).
- **Still open, from Javier's notes:** rounded corners to soften the straight lines (SwayFX, `chaotic-aur/swayfx` 0.6, reads the same config — a later, separate trial); apps that draw their own minimise / maximise / close bar (Chrome…) get tidied one by one; dialogs and small tools float (to build).

### D-45 · Sway is the new base, tried as an extra login session
**Decided by Javier:** *"A, let's go with Sway"* (from the research, `docs/research/2026-10-04-tiling-base-choice.md`), and *"new session then.... excellent to keep using this one as main."*

**What it means:**
- **Sway** (from Arch `extra`, installed with nog): mature, plain-text settings, explicit sync for NVIDIA since 1.11, the widest set of terminal companion tools. Started with `--unsupported-gpu` (the developers' label for closed drivers, not a missing feature).
- **A new login choice next to the others.** The current session stays Javier's main desktop meanwhile; Plasma stays the fallback (D-6). Sway replaces them only when it is ready.
- **Barebones first:** tiling, a terminal, the three screens at 144 Hz (by connector: DP-2 left, DP-3 middle, DP-1 right — the three share one name and serial), nothing else. Then the first test: Chrome with a video, a Discord screen share, WoW full screen, brightness.
- **Plain looks are accepted for now:** no blur, rounded corners or animations; our identity comes from colour, contrast, fonts, the bar and the terminal (Phase 12). SwayFX (same settings, adds effects) stays a later option.
- **If Sway fails the test on this card:** niri next, then i3 (the research's fallbacks).

### D-44 · Start again: barebones tiling, terminal apps first, our own look
**Decided by Javier:** *"I know we invested time on setting up the setup we have right now, but, honest. I do not like it. I want to start again"* … *"I want something that it's us, as everything we are building. We have come too far to use standard stuff that doesn't differentiate you but just makes you look like everyone else."* … *"let's take it one step at a time, let's build it slowly, take our time to select, customize, and make things work."*

**What it means:**
- **The base is chosen again, from research.** Barebones Hyprland, or something more mature and proven, kinder to NVIDIA, easy to set up, rich in terminal (TUI) options and liked by the community: Sway, i3, dwm and others are compared (`docs/research/2026-10-04-tiling-base-choice.md`); Claude recommends, Javier chooses. **Tiling first**, as first intended.
- **Then the ~31 jobs of `docs/RECIPE.md`, one by one, again**, each chosen with Javier, **command-line and terminal apps first**. This replaces D-39 ("settings get graphical apps, not terminal ones; Forge apps later") and the shell choice of D-40 (Noctalia).
- **A job with no good terminal app becomes a new Forge Suite app** (forgekit, Python/Textual). The gaps are listed as they are found.
- **Our own look, built little by little** from the KognogOS brand: its logo and its colours. Elements connected but not fused: contrast between them on purpose, so the desktop is neither a monotone mash nor stock Catppuccin. Each visual step is designed and approved before it is built (the grubForge 2.0 method).
- **Later, once everything is set up:** terminal apps of our own for what we use that is not Forge Suite, by forking the one we use, or writing one from zero.
- **Kept meanwhile:** Plasma stays the fallback login (D-6); the current hypeForge session stays usable on this computer until the new one replaces it; everything built so far (decisions, research, scripts, findings) stays as history and as material.

## Before 2026-10-04

The first attempt — a floating Hyprland desktop, D-1 to D-43 (28 Sep – 3 Oct 2026) — was removed from this log on 2026-10-05 at Javier's request: *"Anything talking about the Hyprland days needs to be removed."* It lives in git history: commit `864885d` is the last that holds it.
