# hypeForge — the list

**Target: no date set — started 28 Sep 2026.** A Forge Suite app that installs the KognogOS Hyprland desktop onto any Arch install.
The reasons behind each item are in `docs/DECISIONS.md` and `docs/DESIGN.md`. This file only lists what gets done.

**Updated after every step.** Run `bash scripts/status.sh` for the short version.

---

## LOCKED — decided by Javier (details in docs/DECISIONS.md)
- **Name:** hypeForge, package `hypeforge` (D-1)
- **Base:** Hyprland, with settings written in Lua only (D-3, D-5)
- **Plasma is being replaced.** KognogOS moves off it little by little. Plasma stays installed as the fallback login until hypeForge works **and Javier is fully daily driving it** (D-6, #10)
- **Windows float by default. Win + arrows tile them, like Plasma** (D-7)
- **One portable folder. System changes happen only through the app** (D-8)
- **The Hyprland family's updates are locked by us, through nog** (D-9)
- **Forge apps run in Alacritty and must be readable on a plain text screen. forgekit#1 gets fixed first** (D-10)
- **The recipe shows up to 5 researched options per job, and Javier chooses** (D-11)
- **Testing happens in VMs. The KognogOS installer image gets fully rebuilt first** (D-12)
- **We learn from Omarchy and every developer, with thanks; we do not compare** (D-4, refined by D-27)
- **The desktop is built from separate small apps, not one all-in-one program** (D-14)
- **The login screen is greetd + tuigreet, proven in a VM first** (D-15)
- **Portals: Hyprland's own for screen sharing, GTK for the file window** (D-16)
- **Top bar Waybar (dev build for now), launcher Walker, notifications mako** (D-17, D-18, D-19)
- **Background helpers: SwayOSD, hyprlock + hypridle, hyprpaper, hyprpolkitagent** (D-20)
- **Clipboard via Walker, screenshots grim + slurp + Satty, recording gpu-screen-recorder + OBS, Catppuccin everywhere** (D-21)
- **Files: Midnight Commander + superfile + Krusader; nmtui, bluetui, wiremix, btop + nvtop** (D-22)
- **Monitors written by hypeForge; hyprsunset, hyprpicker, Fresh, imv, Zathura, mpv + cliamp** (D-24)
- **Hyprland starts through uwsm** (D-25)
- **udiskie + gvfs, KWallet on its own, a Walker power list, system-config-printer** (D-26)
- **The folder is a full copy; the key map keeps Plasma's keys** (D-28, D-29)
- **No taskbar and no minimise; title bars show maximise and close** (D-34)
- **Five themes, one per KognogOS wallpaper; Mocha is the default** (D-36)
- **The bar: along the bottom, full width, 40 px, bigger icons, clock in the corner** (D-41)
- **Every recipe pick is a first try; a misfit becomes a finding and is swapped** (D-23)
- **Documentation at every step, a full GitHub, and a coming-soon note on kognogos.org** (D-13)

---

## Phase 0 · Foundations
- [x] Name chosen: hypeForge. Free on the AUR and on GitHub (D-1)
- [x] Project folder, README, decision log, design notes, research notes, roadmap, changelog, test plan
- [x] Public GitHub repository: github.com/jetomev/hypeforge, with About, 16 topics, labels, 6 phase milestones and issues #1–#9. The commit is Verified and the license is recognised
- [x] kognogos.org shows hypeForge as coming soon: a feature card, a nav link and a progress tile, deployed and checked live
- [x] Recipe research: 31 jobs, up to 5 options each, with sources and a lean, in docs/RECIPE.md; personal details removed (#1)
- [x] Research job 31: portals, meaning file-open dialogs and screen sharing (Plasma's xdg-desktop-portal-kde). Researched 2026-09-29, now in docs/RECIPE.md (#11)
- [x] Research: floating-first windows with Win + arrow snapping in Hyprland 0.56 are doable with work; report in docs/research/ (#5)
- [x] libvirt allowed to use the NVIDIA card for VM 3D: scripts/test-rig/enable-nvidia-vm-3d.sh, applied 2026-09-28 (#2)
- [x] VM display on NVIDIA: SPICE without OpenGL + egl-headless works (with OpenGL on, the window stays black) (#2)
- [x] Hyprland running with 3D inside a VM: the installed Omarchy 4.0.4 desktop runs well (Javier), and on the host `nvidia-smi` lists the VM's QEMU using 400 MiB of the RTX 3060 (#2)
- [x] Omarchy 4.0.4 ISO downloaded to ~/Downloads, SHA256 verified against the release notes (#3)
- [x] omarchy-ref VM created (8 GB, 4 threads, 64 GB disk, UEFI, 3D on) and booted into Omarchy's installer (#3)
- [x] Omarchy 4.0.4 installed in omarchy-ref by Javier. It runs from its own disk: the installer ejected the ISO, and the boot order is now disk only (#3)
- [x] Clean snapshot `clean-install` of omarchy-ref: internal, taken while shut down, and reverting it tested (#2, #3)
- [x] SSH into omarchy-ref from the desktop (2026-09-29): its own key `~/.ssh/id_ed25519_omarchy-ref`, user `jetomev`, IP 192.168.122.187, UFW `limit 22/tcp` (6 connections per 30 s, so keep attempts few). It runs Hyprland 0.56.2 with Lua settings
- [ ] A real KognogOS VM, from a fully rebuilt KognogOS installer image (KognogOS work) (#4)
- [ ] A clean snapshot on every future test VM too, starting with the KognogOS VM (#4)

## Phase 1 · The recipe
- [x] First choice: separate small apps, decided 2026-09-28 (D-14, #6)
- [x] Javier picks one option per job: all 32 decided on 2026-09-29, each a first try (D-23). Decided: job 0 (separate small apps, D-14), job 9 (greetd + tuigreet, D-15) job 1 (Waybar, D-17), job 2 (Walker, D-18), job 3 (mako, D-19), jobs 4–8 (SwayOSD, hyprlock, hypridle, hyprpaper, hyprpolkitagent, D-20), jobs 10–13 (Walker clipboard, grim + slurp + Satty, gpu-screen-recorder + OBS, Catppuccin everywhere, D-21), jobs 14–18 (mc + superfile + Krusader, nmtui, bluetui, wiremix, btop + nvtop, D-22), jobs 19–25 (monitor rules + nwg-displays, hyprsunset, hyprpicker, Fresh, imv, Zathura, mpv + cliamp, D-24), job 26 (uwsm, D-25), jobs 27–30 (udiskie + gvfs, KWallet, Walker power list, system-config-printer, D-26) and job 31 (portals: Hyprland's + GTK, D-16)
- [x] Floating-first windows with Win + arrow snapping, proven in Hyprland 0.56 (Lua): `prototype/snap.lua` in omarchy-ref, 2026-09-29. Javier: *"It works amazing!!!!! So cool!"* (#5)
- [ ] Snapping, still untested: hopping to the next monitor (the VM has one screen), snapping by dragging to an edge, and keeping the remembered size across a settings reload (#5)
- [ ] Test nog's AUR path early: Walker, elephant (D-18) and cliamp (D-24) are AUR only. Every gap is a nog finding
- [x] Re-read jobs 10 and 29 with Walker in mind: Walker's clipboard (D-21) and a Walker power list (D-26)
- [ ] Move from `waybar-git` to the regular `waybar` once a release after 0.15.0 reaches `extra` (D-17)
- [x] The full key map: Plasma's keys keep their jobs, approved 2026-09-29 (D-29)
- [x] Win + Up twice maximises, Win + Down comes back; no error notification at a screen edge (26 presses, 0 failures) (D-30, #5)
- [x] ~~Minimise and a taskbar~~: built in the VM, then dropped by Javier (D-34); removed from the VM and the repo. Was: Waybar's taskbar in the top bar, minimised windows on a hidden workspace, a small helper until Hyprland 0.57 (D-31, #5). Built in the VM 2026-09-29: `prototype/waybar/`, `prototype/minimise.lua`, `prototype/minimise-helper.py`; bringing a parked window back tested from the repl (it returns to workspace 1 and the hidden workspace closes); taskbar clicks waiting for Javier's test
- [x] Window buttons: `button-layout` = `:maximize,close` (D-34); hyprbars for windows without their own title bar, proven with Lua (D-31, D-33)
- [x] Windows open floating at 80 % of the screen, centred; dialogs keep their size (untested); Chromium's "open maximised" undone; Alt + F4 closes (D-32)
- [x] Gaps: 8 between windows, 13 at the edges (D-33)
- [x] Alacritty with KognogOS's `decorations = "Full"` tried in the VM, 2026-09-29: opens floating at 80 %, **but draws no title bar on Hyprland** (screenshot checked). Hyprland takes over decorations and draws only a border (D-33)
- [x] hyprbars built with hyprpm in the VM (needs `cmake` + `meson`; enabling needs sudo) and set up in Lua: `prototype/titlebars.lua`, Catppuccin bar with maximise and close (minimise removed, D-34), double-click maximises; screenshot checked, no config errors (D-31, D-33)
- [x] hyprbars proven by Javier 2026-09-29: every button acts on its own window, double-click maximises, Chromium keeps a single bar. *"all buttons work, Chromium has one bar. Great!"*
- [ ] hyprbars at login: load it from the config (hl.plugin.load) or hyprpm reload in autostart, since buttons are added only when the plugin is loaded; rebuild after each Hyprland update inside the nog lock (D-9)
- [x] Alt + Tab: simple, next window brought to the front, Shift goes back, no list (D-35, #5)
- [x] Five themes from the KognogOS wallpapers, decided 2026-09-29: Mocha (default), Black, Green (light, pastel greens), Gray (dark greys), White (light greys); all 4.5:1 or better (D-36)
- [x] Themes as colour files: `prototype/themes/<id>.lua` generated from the preview page; `prototype/theme.lua` paints borders, hyprbars and Alacritty; Win + Alt + T switches (D-36). Javier: borders and title bars follow; Alacritty's file follows (screenshot)
- [x] Themes reach GTK apps: generated gtk-3.0/gtk-4.0 gtk.css (adw-gtk-theme named colours) + light/dark from the theme's kind; verified in the VM (D-36)
- [x] Theme switching tested by Javier across Alacritty, title bars, borders, GTK apps and Chromium: *"it works pretty well"* (2026-09-29)
- [ ] Chromium's frame colour is a system policy file (/etc/chromium/policies/managed/): tested through the VM's own helper (password each switch); hypeForge needs its own single-purpose helper for it (D-8), and a ruling on password-or-not
- [ ] Themes still to reach: the top bar (our Waybar, Phase 2), the wallpaper (hyprpaper, Phase 2)
- [x] Win + Return opens Alacritty (D-29); the test machine's own terminal (foot) is not part of hypeForge
- [x] The portable folder layout decided: a full copy, with machines/<hostname>/ apart (D-28, #7)
- [ ] The folder round trip: build, copy to a clean VM, apply, same desktop (#7)
- [ ] The Catppuccin Mocha look for every chosen app. Check Krusader when Qt follows GTK, and whether the 2022 Catppuccin theme for Midnight Commander still fits (D-22)

## Phase 2 · Build it by hand
- [ ] Build the desktop by hand on the test desktop, next to the fallback session
- [ ] **2026-09-30 · the KognogOS hypeForge edition (D-37):** no Plasma; build the ISO, install it in a VM, test and fix there; this computer only after that. Also closes Phase 0's #4
- [x] The desktop as one folder, `desktop/` (hypr, waybar, mako, uwsm, elephant, systemd): the prototype files moved in, paths fixed, the test machine's Chromium helper removed (2026-09-30)
- [x] A standalone `desktop/hypr/hyprland.lua`: screens, look, the full D-29 key map, uwsm app launching, a per-machine file (D-28). Checked against Hyprland 0.56.2's own reference (`hl.meta.lua`) and syntax-checked; **not yet run in Hyprland**
- [x] Themes now also reach the wallpaper (hyprpaper), the top bar, notifications and the lock screen; dry-run with a stand-in for Hyprland: switching to White rewrote all eight files correctly
- [x] Waybar top bar (no taskbar, D-34), hyprlock, hypridle (lock 10 min, screens off 11, no auto-suspend), the Walker power list, uwsm env files
- [x] Nine background helpers as systemd user services (D-25): top bar, notifications, wallpaper, idle, password pop-up, SwayOSD, elephant, Walker, udiskie
- [x] `scripts/desktop/install-into.sh <home>`: puts the desktop into any home folder; tested twice on a fake home (an old `hypr` folder was set aside, not deleted)
- [x] hyprbars as a package, not hyprpm: `hyprland-plugin-hyprbars` 0.56.2 (AUR) → KognogOS local repo, built in a clean chroot
- [ ] Javier: build the ISO (KognogOS `hypeforge-edition` branch) with `scripts/build-hypeforge-edition.sh`; log in `kognog/logs/build-latest.log`
  - Run 1 (15:18): makepkg tried to install Walker's runtime parts on this computer (refused, nothing installed) → Walker/elephant now repackaged with `makepkg -d`, cliamp moved to the chroot; the fix tested here without sudo
  - Run 2 (15:23): all regular packages built; stopped at the chroot: `mkarchroot` cannot resolve a path whose parent folder is missing ("Please specify a working directory") → `mkdir -p` first
  - Run 3 (15:30): **BUILD FINISHED OK**, `kognogos-2026.09.30-x86_64.iso`, 5.4 GB, 1,210 packages, no Plasma. Checked in the work folder: KognogOS os-release, greetd, hyprbars, installer, the hypeForge folder in the live home
  - Build findings: broadcom-wl DKMS not built (no kernel headers on the disc: real Broadcom Wi-Fi would not work live); a default "which package" answer added nvidia-utils as the Vulkan driver (harmless)
- [x] New VM `kognog-hypeforge` (8 GB, 4 threads, 64 GB, UEFI, 3D on the RTX 3060), live session **boots straight into hypeForge**: Hyprland + all 9 helpers running, `hyprctl configerrors` empty, hyprbars loaded, top bar and title bars drawn (screenshot, 2026-09-30 15:49). The VM's guest agent lets Claude run checks and take screenshots inside it without a password
- [x] Test-rig trap: `virt-install --cdrom` removes the disc from the VM's saved settings after the first start, so the next power-on found no bootable device. Fixed with `virsh change-media … --insert --config` and boot order disc → disk (`virt-xml --edit --boot cdrom,hd`). Next VM: create it with `--disk device=cdrom` instead of `--cdrom`
- [x] Installer bug caught before use: the live system is at `/run/archiso/airootfs`, not `/run/archiso/sfs/airootfs`; fixed, and the installer now logs to `/tmp/kognog-install.log` (copied to the VM for this test; the next ISO build carries it)
- [x] Installed with `sudo kognog-install /dev/vda` (Javier, 16:38): **INSTALL FINISHED OK**; 9.5 GB used on btrfs @ subvolumes, GRUB "KognogOS" + splash, no failed services. Snapshot **`clean-install`** taken (shut off, disc ejected, boots from disk)
- [x] First login on the installed system: greetd + tuigreet, no auto-login; **hypeForge session up: Hyprland + all 9 helpers, no config errors, hyprbars loaded, wallpaper + top bar + local clock** (screenshot 16:56)
- [x] Fixed from the install (next ISO build): hypeForge is tuigreet's default session (`--cmd`; the first login offered Terminal); the disk confirmation accepts `vda` as well as `/dev/vda`; live-only packages are removed after KognogOS's start-up recipe is written (the disc's recipe had fired one harmless error)
- [ ] Still to fix: `consolefont: no font found` (no FONT in /etc/vconsole.conf); the live welcome says "Update status unknown" (kognog-updates.timer not on in the live session)
- [x] Javier tested the installed desktop by hand (2026-09-30, 26 notes). **Works:** Win tapped alone opens Walker, Win + arrow snapping (*"works perfect (so happy!)"*), mouse resizing, Alt + Tab, the lock screen (*"looks amazing!"*, themed), Satty (*"so cool!"*, themed), Krusader (themed), btop, reboot/shutdown screens, alacrittyForge changing Alacritty's font size
- **Findings from VM test 1** (fix = Claude can fix it directly; research = options first, Javier picks, D-11):
  - [x] **F-1** GRUB starts without the KognogOS GRUB theme (the installer never applies it) · **fixed in the repo, untested:** the theme lived only on this desktop (`/boot/grub/themes/kognogos`), never in the KognogOS repo; now in `kognog/assets/grub-theme/`, carried on the disc, installed and set by the installer, plus a KognogOS menu icon
  - [x] **F-2** The login screen (tuigreet) does not match the OS → SDDM with KognogOS's own greeter (D-38) · **fixed in the repo, untested:** greetd out, SDDM + the kognogos theme back, live auto-login into hypeForge, only the hypeForge session listed
  - [x] **F-3** No splash between login and desktop, only text messages · **fixed with F-2, untested** (SDDM is graphical; session output goes to its log, not the screen)
  - [x] Research: `docs/research/2026-09-30-hyprland-own-apps.md`. Hyprland makes graphical apps for 4 of 9 jobs (launcher, sound, system info, logout); every one of them reads one colour file, `hyprtoolkit.conf`, which the theme now writes
  - [x] On the disc for the next test (D-39, Hyprland's own first): hyprlauncher (Win tapped, bar button), hyprpwcenter, hyprshutdown (Log out); nm-applet, Blueman, pavucontrol; wiremix, bluetui and nwg-displays removed; duplicate autostarts switched off
  - [ ] Open choices for Javier: Hyprland's twice-yearly donation pop-up and after-update news pop-up, keep or switch off? hyprshutdown can hang at logout on NVIDIA + SDDM (the real desktop, not the VM)
  - [x] **F-17** The live session locked itself after 10 minutes and could not be unlocked: the live user's password is empty, and hyprlock does not send an empty password (Javier: *"Now it is stuck in the lock screen"*) · **unstuck** by setting a temporary password `live` through the VM's guest agent; **fixed for the next build:** live password `live` (airootfs shadow), no idle lock in the live session (installed systems keep it), and the terminal welcome says the password and how to install
  - [x] **F-18** Build-2 install would not start: "No bootable option or device was found". The firmware's own boot list had lost its KognogOS entry, and the installer never put GRUB in the standard fallback place (`EFI/BOOT/BOOTX64.EFI`) that every UEFI firmware checks. Real PCs lose that list too (BIOS update, CMOS reset). Javier: *"we need to fix this Grub/UEFI thing in the next ISO"* · **fixed in the installer** (second `grub-install --removable`); the VM repaired by hand through the guest agent, snapshot `clean-install-2` retaken
  - [x] **F-1 confirmed** in the VM: KognogOS GRUB theme with the emblem icon
  - [x] **F-19** GRUB 2.16 fills the menu with firmware entries ("UEFI QEMU DVD-ROM (EFI BootNext)", "EFI Internal Shell"…) · **fixed in the installer:** `GRUB_DISABLE_BOOTNEXT=true`. Note for this desktop and grubForge: the same clutter arrives with GRUB 2.16 here (2.14 installed today)
  - [x] **F-17 addition** (Javier: *"the live disk should not have lock screen usable or active"*): the live session also loses Win + L (unbound in `machines/kognog-live/machine.lua`) and "Lock" in the power list; tested on a fake live home
- **Findings from VM test 2** (build 2, installed, 2026-09-30 evening). **Works:** GRUB theme, boot transitions, the SDDM login (*"great!"*), Walker windows in our colours, themes switch the wallpaper, the KognogOS launcher icon (*"awesome"*), btop (*"still awesome!!!!"*), log out, Monique (*"looks good"*)
  - [ ] **F-19b** GRUB menu: *"minimum needed please"*. BootNext entries already off for build 3; decide on "Advanced options" and "UEFI Firmware Settings" (or hide the menu on single-system machines)
  - [ ] **F-20** Win + F1: an error, no list · **cause found:** the disc build drops the "may run as a program" mark on files it copies, so the script could not start · **fixed:** started through `bash`
  - [ ] **F-21** Switching themes fast: the wallpaper stops showing · restart-limit guess **disproved by the log** (hyprpaper stays active); each restart logs `EGL_BAD_ALLOC`. Fix: tell the running hyprpaper to swap the picture instead of restarting it · open
  - [ ] **F-22** A wallpaper picker app is needed (*"we need an app to change backgrounds manually"*) · research (Noctalia and DMS both have one)
  - [ ] **F-23** hyprlauncher rejected: *"horrible, empty unless do a search, mouse doesn't work"*. Wanted: categories and every app's icon visible without searching; search for finding fast · with the bar trials
  - [ ] **F-24** hyprpwcenter rejected: a window pretending to be a drop-down, *"looks horrible"* · with the bar trials (real drop-downs)
  - [ ] **F-25** Two network icons: nm-applet's (full colour, good menu) and Waybar's (matching, but opens a window mid-screen) · with the bar trials
  - [ ] **F-26** Screens: keep Monique for the full window, and add a top-bar icon with quick screen options · with the bar trials
  - [ ] **F-27** Idea: the login screen follows the desktop theme (SDDM theme colours written by a small system helper, D-8) · later
  - [x] **F-28** Top bar font 11 (*"can we set it for 11"*) and the terminal's default font 11 · **done in the repo.** Today it lives in `~/.config/hypeforge/waybar/style.css`; the app (or the chosen shell's settings) makes it a setting
  - [ ] **F-29** udiskie's tray icon is full colour and does not match · with the bar trials
  - [x] **F-30** Alacritty follows the theme (Javier confirmed), but transparency spoilt the light themes · **done:** solid terminal background (opacity 1.0, no blur); Green's terminal background darkened to `#e2efe6` and its grey text to `#3b6a4f` (5.3:1, was 4.5:1); applied live in the VM too
  - [ ] **nog finding (handled in Javier's nog session, not here):** in the VM `nog install noctalia` failed with database errors: nog does not refresh the package databases first. Javier installed it with pacman
  - [x] **Bar trial 1 · Noctalia 5.2.0 → chosen (D-40).** Javier: launcher *"amazing. Set!"*; sound, network, Bluetooth, notifications *"amazing"*; tray all good; *"WOW. We found what we are looking for."* Its settings window doubles as system settings for themes. Icon tinting kept on (*"looks cool"*). Lock screen: hyprlock stays. Trials 2–7 (DMS, ironbar…) not needed
  - [x] Noctalia integration built in the repo (untested in the VM): five hypeForge palettes generated from themes/*.lua + terminal.lua (`scripts/desktop/make-noctalia-palettes.lua`); `noctalia/00-hypeforge.toml` (no welcome window, no startup ping, icon tint, taskbar on, Noctalia's lock off, wallpapers from /usr/share/wallpapers/kognog, five wallpaper favourites that carry their palette); `bin/hypeforge-theme-sync` (Noctalia's colors_changed hook) and `bin/hypeforge-theme-next` (Win + Alt + T); a template so Noctalia's own palettes colour borders, title bars and the terminal too; keys through `noctalia msg`; theme.lua slimmed to borders, title bars, Alacritty, GTK, hyprtoolkit, hyprlock
  - [x] Retired from the desktop and the disc (D-40): Waybar, mako, SwayOSD, hyprpaper, Walker + elephant, hyprlauncher, hyprpwcenter, hyprshutdown, pavucontrol, nm-applet, Blueman (17 packages); helpers 12 → 4 (Noctalia, hypridle, hyprpolkitagent, udiskie). Research: `docs/research/2026-09-30-noctalia-integration.md`
  - [x] **Build 3, first try (20:14), stopped, and an incident on this desktop:** the build's clean-up `sudo rm -rf iso/work` met /sys and the firmware's efivars still attached inside work/ from an earlier build. rm was refused 144 times, but it **deleted this computer's UEFI boot entries** (Boot#### and BootOrder; Linux allows those to be deleted). Found from the log before any restart. **Repaired** (KDE password window): leftovers detached; `efibootmgr --create` → `Boot0000* KognogOS` (sda1, `\EFI\BOOT\BOOTX64.EFI`), BootOrder 0000. **Prevented:** build-iso.sh now detaches leftovers, stops if anything stays attached, and uses `rm -rf --one-file-system`. Open: Windows' own firmware entries were deleted too (GRUB's menu still reaches Windows); re-add after checking their paths
  - [x] **Build 3 (20:23): BUILD FINISHED OK, no rm errors** (the safe clean-up worked). Live session: Noctalia + hyprpolkitagent + udiskie, no config errors, no failed services, palette `custom hypeForge-Mocha` with the Mocha wallpaper (screenshot 00:37). Thunar was added after this build started (next build)
  - [ ] **F-31** The live disc started hypridle anyway: Arch's user-preset policy enables any unit it finds at first login, and the live home still had the unit file (only its start link was removed) · **fixed in build-iso.sh** (the unit file goes too); stopped in the running VM
  - [ ] **F-32** Noctalia's launcher button is a magnifying glass, not the KognogOS emblem (F-8 again, in Noctalia) · find its icon setting
  - [x] Thunar added next to Krusader (Javier: *"we are going to use thunar too … it is themable. We will keep the other one too"*): thunar, thunar-volman, thunar-archive-plugin, tumbler; Thunar opens folders by default
  - [x] Build 3 installed (20:46), clean log; **F-18 confirmed** (started on its own: GRUB installed to the firmware list and the fallback place) and **F-19 confirmed** (menu: KognogOS Linux, Advanced options, UEFI Firmware Settings). Snapshot `clean-install-3`
  - [x] **Build 3 tested on the installed VM by Javier (2026-09-30, evening): *"I tested and all is good!"*** Themes + wallpapers together, Noctalia's own palettes, the wallpaper picker, the taskbar, Win + V, Ctrl + Alt + Del, hyprlock on Win + L, Monique
  - [ ] **F-16** (found in the build-2 live session, screenshot) the sound centre's panel opened with its title bar under the top bar and its Inputs page cut off · **fixed in the repo, next build:** 940 × 580, 74 px from the top
  - [x] Build 2 (18:17): **BUILD FINISHED OK**, 5.5 GB; live session through SDDM auto-login: Hyprland + all helpers incl. hyprlauncher, nm-applet, blueman; no config errors, no failed services; emblem on the bar; hyprpwcenter themed by hyprtoolkit.conf
  - [ ] **F-4** Top bar · **plan: try in the installed VM, one by one, each installed with nog:** Noctalia, DankMaterialShell, ironbar, nwg-panel, Waybar richer (extra); ashell, Caelestia (AUR, nog AUR-path tests). HyprPanel is archived · Top bar: Javier misses Plasma's open-app icons and options; what can the bar do or add? Reopens part of D-34 · research
  - [x] **F-5** Screen settings (*"Sucks. We need something that looks better"*) · **first pick on the disc, untested: Monique** (AUR 0.8.3, GTK4 + libadwaita window app, drag-to-arrange, 10-second undo countdown, saves real `hl.monitor()` Lua). "Screens" menu entry opens it on `machines/<hostname>/`; hyprland.lua loads `monitors.lua` from there. Research: `docs/research/2026-09-30-display-settings.md` (runner-up hyprmoncfg is a terminal app; DankMaterialShell's page only comes with its whole shell). To check: Lua output chosen in its Preferences; the three identical Sceptre screens' serial numbers; NVIDIA
  - [ ] **F-6** The app menu has no categories · **decided 2026-09-30: settle after the bar trials** (Noctalia and DankMaterialShell bring menus with real categories). Research: Omarchy 4 dropped Walker; its "categories" are the Omarchy menu (Apps, Learn, Style, Setup, Install…), not app categories; a Walker recipe exists, but elephant paused development 2026-09-29 (`docs/research/2026-09-30-bars-and-walker-categories.md`) · earlier: the launcher is now Hyprland's own hyprlauncher (D-39), which has no categories either (its code never reads them); runner-up with categories: nwg-drawer. Javier evaluates
  - [x] **F-7** Font size 12 as the standard everywhere · **fixed, untested:** top bar 12pt, notifications, title bars, Walker, GTK (Qt follows GTK); the terminal was already 12
  - [x] **F-8** The top bar's app button shows the Arch logo · **fixed, untested:** Waybar `image` module with `/usr/share/pixmaps/kognogos.png`
  - [x] **F-9** A keyboard-shortcut list · **fixed, tested with stand-ins:** `bin/hypeforge-keys` reads every described key live from Hyprland into Walker; Win + F1 and a "Keyboard shortcuts" menu entry
  - [x] **F-10** Walker does not follow the theme · **fixed, output tested:** theme.lua writes a "hypeforge" Walker theme (Walker's default style + our colours + 12pt) and restarts Walker; Walker's full default settings shipped with `theme = "hypeforge"`
  - [x] **F-11** Win + Alt + T changes everything but the wallpaper. **Claude's bug:** theme.lua restarted `hyprpaper.service`, the unit is `hypeforge-hyprpaper.service` · **fixed, untested**
  - [x] **F-12** Alacritty's colours per theme look bad (*"it gets pretty ugly! lol!"*) · **fixed, output tested:** Javier: *"all the proposed terminal themes I like"* (preview https://claude.ai/artifact/PmTan1DKRuBtxAxxanVamt, v2 gave Green its own set). Palettes in `desktop/hypr/themes/terminal.lua`; the theme writes `hypeforge-current.toml` plus `hypeforge-<id>.toml` for each theme, so alacrittyForge lists them. The system switch sets the terminal; alacrittyForge overrides for the terminal only
  - [ ] alacrittyForge: show `hypeforge-current` as "Follow the desktop (hypeForge)" (small change in alacrittyForge's theme list)
  - [x] **F-13** Sound: the terminal app is rejected · **first pick on the disc, untested:** hyprpwcenter (Hyprland's own) opens as a panel top right; right-click → pavucontrol, because hyprpwcenter's code never sets the default speaker (research, unproven). Evaluate later (D-39)
  - [x] **F-14** Network · **first pick on the disc, untested:** Hyprland makes none; nm-applet in the tray (a real Wi-Fi drop-down under the bar), click → nm-connection-editor
  - [x] **F-15** The Bluetooth icon does nothing · **first pick on the disc, untested:** Hyprland makes none; Blueman in the tray, click → blueman-manager. (The VM has no Bluetooth adapter, so it cannot be fully tested there)
- [ ] Unverified guesses to check in the VM: Walker's `-m clipboard` / `-m menus:power` options, the hyprpaper 0.8 file format, `mode = "highrr"`, Win tapped alone opening Walker, zoom keys
- [ ] Possible nog/yay finding: `yay -Ssa walker` printed nothing, while the AUR website lists walker 2.17.1 (2026-09-30). Check before filing
- [ ] `install-into.sh` replaces the whole folder, so running it again on a real home resets the chosen theme. Fine for the ISO; the app must keep the user's choices
- [ ] **hypeForge on this computer (tphome-linux), started 2026-09-30 evening** (Javier: *"I want to recreate hypeForge in my machine to start using it!"*). Next to Plasma, which stays at the login screen (D-6)
  - [x] Restore points before anything: snapper #2194 for root and for home
  - [x] The helpers only start in a Hyprland session (`ConditionEnvironment=XDG_CURRENT_DESKTOP=Hyprland`), so Noctalia never starts inside Plasma
  - [x] `machines/tphome-linux/`: three screens DP-2 / DP-3 / DP-1 at 2560x1440@144; NVIDIA env (LIBVA_DRIVER_NAME, __GLX_VENDOR_LIBRARY_NAME, NVD_BACKEND) loaded by uwsm; brightness keys through ddcutil buses 3/4/5 (untested)
  - [x] Step 2 · Javier ran `scripts/desktop/this-pc-1-install-packages.sh`: **FINISHED OK, all 32 installed** through nog (hyprbars built against Hyprland 0.56.2)
  - [x] Step 3 · Plasma's GTK folders backed up to `~/.local/share/hypeforge-backups/before-hypeforge-20260930-2123/`; `install-into.sh ~` done (hypr, noctalia, uwsm linked; 4 helpers; machines/tphome-linux). Helpers stay inactive under Plasma (checked). `Hyprland --verify-config`: only the hyprbars keys, which that check cannot see without the plugin. Note: GTK apps under Plasma now also get the theme's gtk.css (backup kept)
  - [x] Step 4 · Javier logged in with "Hyprland (uwsm-managed)" (21:31). Title bars, the four helpers, no config errors: all checked from the running session
  - [x] F-33 (#16): Monique (Screens) saved DP-1 and DP-2 at the same spot (2560x0), so DP-1 mirrored DP-2. The three Sceptres share one name and serial, so Monique likely cannot tell them apart. Its files set aside as `monitors.lua.bak` / `monitors.conf.bak`; machine.lua's layout back (DP-2 0, DP-3 2560, DP-1 5120, checked). Monique is not safe on this computer until this is understood
  - [ ] F-34 (#17): the plain "Hyprland" entry at the login screen fails (SDDM: `start-hyprland` crashed after ~1 min, 21:30). Only "Hyprland (uwsm-managed)" works. Find out why, then hide the plain entry or make it work
  - [x] F-35 (#18): the bar had no Lock: Noctalia hides its own Lock whenever its lock screen is off (`session_panel.cpp`, 5.2.0), even with a `command` set. Javier chose **B, keep hyprlock**: a custom "Lock" entry runs `loginctl lock-session`, which hypridle answers with hyprlock. Applied live; **proven by Javier**: Lock from the bar and from the keyboard both lock
  - [x] Bar only on the middle screen DP-3 (Javier): `machines/tphome-linux/noctalia.toml` switches it off on DP-1 / DP-2, pulled in by an `[include]` in 00-hypeforge.toml via `HYPEFORGE_MACHINE`, set by uwsm/env at login. Checked with `hyprctl layers`. Note: Noctalia resolves relative includes from the link (`~/.config/noctalia`), not from hypeForge's folder, so the path is absolute. A computer without a machines folder gets one warning line
  - [x] Tray icons removed (Javier): nm-applet's autostart switched off (`autostart/nm-applet.desktop`, Plasma never ran it anyway: `NotShowIn=KDE`); udiskie runs `--no-tray` (still mounts drives and notifies)
  - [x] F-9 again: Win + F1 did nothing on this computer, because the shortcut list still fed Walker, which Noctalia replaced (D-40) and which is not installed here. `bin/hypeforge-keys` now uses `noctalia dmenu`; tested: the launcher opens with the list. **proven by Javier**
  - [x] F-37 (#20): Win + E did nothing (Javier): it ran `superfile`, but the package's program is `spf`. Fixed in hyprland.lua; every other shortcut's program checked present. **proven by Javier**
  - [x] Win + K opens Thunar instead of Krusader (Javier, 2026-09-30); Krusader stays installed, from the launcher
  - [x] Win + E opens Midnight Commander (`mc`) instead of superfile (Javier, 2026-09-30); superfile stays installed
  - [x] The bar moves to the bottom, edge to edge, 4 px taller, clock in the bottom-right corner (Javier, 2026-10-01, in two steps: first full width + 36 px at the top, then bottom + 38 px + clock right): `[bar.default]` position "bottom", margin_ends 0, radius 0 (square corners), thickness 38 (Noctalia's default is 34), center empty, `clock` last in `end`. Applies to every hypeForge computer, not only this one. Picked up live without a restart; checked with `noctalia config export` and screenshots (bar at the bottom, nothing left at the top). **Javier to judge by eye, and to check that the drop-downs (sound, network, calendar) open upwards cleanly**
  - [x] The workspace number ("3", the pill next to the emblem) taken off the bar (Javier, 2026-10-01: he read it as the monitor number; it is the workspace on that screen, DP-3 holds workspace 3). `workspaces` removed from `start`; workspaces still work by keyboard. Checked live with a screenshot
  - [x] Bar 40 px tall (Javier, 2026-10-01, third step) and icons about 2 px bigger: Noctalia has no icon size in pixels, only a per-widget `scale`, so every icon widget (launcher, taskbar, tray, notifications, clipboard, network, bluetooth, volume, brightness, battery, control-center, session) gets `scale = 1.17`; the clock and the media text keep their size. Measured from screenshots: clipboard ~12 → ~15 px, power ~10 → ~13 px (rough: the theme changed between the two shots, so the edge detection differs). **Javier to judge by eye**
  - [x] **Bar locked as the KognogOS hypeForge default (D-41, Javier: *"It is perfect."*)**: bottom, full width, 40 px, icons ×1.17, no workspace number, clock in the corner. README updated; the ISO build stages it from this folder, so the next build carries it (checked: `kognog/scripts/build-iso.sh` uses `~/Programs/hypeforge`)
  - [ ] Next ISO build: confirm the live session shows the bar at the bottom, as on this computer
  - [x] Keyboard on this computer: US International with dead keys (Javier, 2026-10-01, "us-latin"): `machines/tphome-linux/machine.lua` sets `kb_variant = "intl"`, matching the system setting (`localectl`: us / intl, console `us-acentos`) that Plasma followed and Hyprland did not. Applied with `hyprctl reload`; `hyprctl devices` shows "English (US, intl., with dead keys)", other input settings kept, no config errors. **Javier to try an accent (' then a → á)**
  - [x] Clock: 12-hour time with AM/PM, plus the date (Javier, 2026-10-01): `[widget.clock] format = "{:%I:%M %p  ·  %a %b %d}"` in `noctalia/00-hypeforge.toml`, every hypeForge computer. Picked up live, no errors in the log; screenshot shows "09:11 AM · Thu Oct 01". Noctalia's time codes have no way to drop the leading zero (09, 01). **Javier to judge by eye**
  - [x] Power button moved to the very end of the bar, after the clock (Javier, 2026-10-01): `session` now follows `clock` in `[bar.default] end`. Picked up live; screenshot shows "09:16 AM · Thu Oct 01" then the power icon
  - [ ] Seen in the log while checking: Noctalia warns "[brightness] failed to resolve logind session" (41 times since login at 07:53, before today's changes). Noctalia runs as a user service under uwsm, outside the login session. This computer's brightness keys use ddcutil (machine.lua), so nothing visible is broken here; check whether Noctalia's own brightness slider works
  - [x] Window borders: one light grey (#bdbdbd) for every window, active or not, in every theme (Javier, 2026-10-01: the theme colour, purple on Mocha, changing tone on the active window, was "very noisy"). `hypr/theme.lua`; the themes keep their own colours for everything else. Applied with `hyprctl reload`, no config errors, `hyprctl getoption` shows bdbdbd for both. Trade-off: the border no longer shows which window is active (title bars and focus still do). **Javier to judge by eye**
  - [x] Favourites on the taskbar, next to the launcher (Javier, 2026-10-01): he pinned 11 apps by right-clicking (Alacritty, Thunar, Chrome, WhatsApp Web, ONLYOFFICE, Obsidian, Elisa, Spotify, KCalc, KeePassXC, Termius). Noctalia keeps right-click pins in `~/.local/state/noctalia/settings.toml`, outside the hypeForge folder, and that file wins. Copied to `machines/tphome-linux/noctalia.toml` (checked identical) so they survive a reinstall. The launcher has favourites too: right-click → "Pin to Launcher"
  - [ ] Phase 3 (the app): later right-click pins do not reach the hypeForge folder by themselves; the app should copy Noctalia's pins into `machines/<hostname>/` (or offer to)
  - [x] Fresh could not be pinned (Javier, 2026-10-01): it is a terminal program (`Terminal=true`), so its window was just "Alacritty" and the taskbar filed it under the Alacritty pin. **Fixed:** hypeForge's own `applications/fresh.desktop` (replaces the system entry by name) runs `alacritty --class fresh -e fresh %F` with `StartupWMClass=fresh`; `TryExec=fresh` hides it where Fresh is missing. `install-into.sh` already links every file in `applications/`, so new installs get it; linked by hand here. Tested: opened through the entry (`gio launch`), the window's class is `fresh`, and the bar shows it as its own icon (screenshot). **Pinned by Javier** (12th favourite); machine-folder copy updated
  - [x] Pinned apps that are not open were dimmed, "barely visible" (Javier, 2026-10-01): `pinned_opacity = 1.0` in `[widget.taskbar]` of `noctalia/00-hypeforge.toml`, every hypeForge computer. Open apps keep their dot. Picked up live (`noctalia config export` shows 1.0); screenshot: all icons at full strength, Chrome with its dot. **Javier to judge by eye**
  - [x] Still too dark (Javier): the cause was the tint, not the dimming. Noctalia recolours every app icon to one theme colour (`app_icon_colorize`, Javier's earlier pick) and used a dim one. Now `app_icon_color = "on_surface"`, the theme's text colour, every hypeForge computer. Contrast against the bar, measured from the five palettes: Black 15.1, White 14.4, Mocha 11.3, Gray 11.2, Green 11.1 (4.5 is the usual "easy to read" line), so light themes get dark icons automatically. Picked up live; screenshot: icons clearly brighter on Mocha. **Javier: "yes, a lot better!"** Still to see on White or Green some time
  - [x] Pushed to GitHub (`ac41c87..4eb7d5a`, 19 commits, all signed with the co-author line); README brought current first (runs on the test desktop since 30 Sep); issues #14 (F-38, opened and closed) and #15 (F-39, open); Vault entry (5) written (2026-10-01)
  - [x] Issues for the first desktop evening's findings, which had none (F-31/F-32 were already in #13's comment): F-33 #16, F-34 #17, F-36 #19 open; F-35 #18 and F-37 #20 opened and closed with Javier's proof (2026-10-01)
  - [x] **Title bars removed (D-42, Javier, 2026-10-01):** some apps showed two bars, and snapping placed windows without room for the 26 px bar, so a top-snapped window's bar went past the screen edge and a lower window's bar slid under the one above. `hyprland.lua` no longer loads hyprbars; `hypr/titlebars.lua` removed. Applied with `hyprctl reload`, no config errors; screenshot shows the three snapped terminals with no bar and even gaps. **Javier to try snapping top/bottom again**
  - [ ] Take `hyprland-plugin-hyprbars` off this computer (nog) and out of the KognogOS hypeForge build list and `scripts/desktop/this-pc-1-install-packages.sh` (D-42)
  - [x] **F-38: a maximised window stayed under a window opened over it** (Javier, 2026-10-01, every maximised app): clicking it or Alt + Tab gave it focus but not the front. Cause: Hyprland's maximise is a layer of its own. **Fixed with our own maximise (D-43)** in `snap.lua`: floating, stretched over the usable screen, app told "maximised". Tested live with two test terminals: an app-style maximise request became ours (fs 0, client 1, full area); the maximised window came to the front over the newer one (screenshot); un-maximise returned the exact earlier size and spot; left → ↑ → ↑ maximised; Win + ↓ went back to the top-left quarter; no config errors. **Proven by Javier** (2026-10-01): maximise, open another program, switch back: works. Still unproven: an app's own "restore" button (Chrome's) after our maximise
  - [x] **F-39: Chrome's restore button did nothing after our maximise** (Javier, 2026-10-01). A logger on Hyprland's fullscreen event caught nothing from his clicks: Chrome was told "maximised" (client = 1) while Hyprland's own state was "not maximised", and Hyprland drops a restore request in that state silently. **Fixed:** the app is no longer told it is maximised, so its button keeps offering "maximise", which reaches us; pressed on a window we maximised, it restores. Tested with a test window: press 1 maximised, press 2 restored the exact spot; Win + ↑ ↑ maximised and a press then went back to the top half; no config errors. **Javier tried Chrome: nothing.** A screenshot showed Chrome's button still on "restore" while Hyprland said "not maximised": Chrome decides that by itself. **Second fix:** apps are told "maximised" again, and a watcher (four times a second) restores any window we maximised whose client state Hyprland has set back to 0, which is all Hyprland does with a "restore" click. Tested with a test window: app maximise → full area, client 1; a simulated app restore → exact earlier spot; Win + ↑ ↑ stays maximised; Win + ↓ → quarter. **Javier tried Chrome: still nothing.**
  - [ ] **F-39 root cause found, not fixed:** Hyprland 0.56.2 tells EVERY newly opened window "maximized" plus "tiled" on all four sides, though nobody maximised it (`fullscreenClient` reads 0). Proven with `testing/tools/wlstates.py`, a tiny raw Wayland client that prints each configure: `configure 2048 1152 [tiled_left, tiled_right, tiled_top, tiled_bottom, maximized, activated]`. So Chrome shows "restore" from the start; its click asks "unmaximise"; Hyprland only sends back the old size, still marked "maximized", and changes no state hypeForge can see (`client` stays 1, no event). ONLYOFFICE and a GTK test window did resize themselves, Chrome does not. Nothing in hypeForge's config asks for it. Workaround: Win + Page Up / Win + ↓ restore Chrome.
    - **Read in Hyprland 0.56.2's source (2026-10-01):** `src/protocols/XDGShell.cpp` ~529 calls `setMaximized(true)` on every Wayland window when it first maps (*"this forces apps to not draw CSD"*), and nothing ever calls `setMaximized(false)`. An app's maximise OR restore request is treated as a toggle of Hyprland's own client state (`Window.cpp` `onUpdateState`). No setting turns the label off.
    - **Proven with a separate test Chrome** (blank temporary profile, `WAYLAND_DEBUG`), maximised our way: first click on its button sent `unset_maximized` and restored (Javier saw it); a second click sent **nothing**: Chrome waits for the "maximized" label to go, and it never does. Javier's own Chrome was already in that stuck state. A 10-minute recorder on his Chrome showed no state change and no event from his click. Test client, test Chrome, recorder and logger all removed afterwards.
    - **Javier chose (2026-10-01): the keys for now, and report it upstream.** No report needed: **already fixed upstream** in hyprwm/Hyprland#16013 ("protocols/xdg-shell: don't maximize on toplevel map", merged 2026-09-01, commit `d7a4335`), which is NOT in 0.56.2 (it is 159 commits past the tag) and not yet in a release. Win + Page Up / Win + ↓ meanwhile; the watcher stays, it makes the first restore click work
  - [ ] When Hyprland's next release (after 0.56.2, with #16013) comes through nog: re-test Chrome's maximise / restore button several times in a row; then decide whether `snap.lua` still needs to tell apps "maximised" (client = 1) and the watcher (D-43, F-39)
  - [x] Space between snapped windows halved (Javier, 2026-10-01): `gaps_in` 8 → 4, so 8 px between two snapped windows instead of 16; screen edges stay 13 (D-33 note). Checked: a left-snapped test window is 1259 wide on a 2530 area (half, minus 4 gap, minus border)
  - [x] Bar back on all three screens (Javier, 2026-10-01: "now that it is at the bottom, works better to me"): the DP-1 / DP-2 `enabled = false` blocks removed from `machines/tphome-linux/noctalia.toml`. Picked up live: `hyprctl layers` lists a `noctalia-bar-default` at the bottom of each screen (y 1388, 52 high)
  - [ ] Design: hypeForge should take the keyboard layout from the system setting (`localectl`, set by the KognogOS installer) on every computer, instead of a fixed `us` in hyprland.lua. Today each machine has to repeat it by hand
  - [ ] **Next session:** go through the shortcuts with Javier: many he does not want (Win + F1 lists them all). (Win + E, Win + K, Win + F1 and Lock all proven by Javier, 2026-09-30)
  - [ ] F-36 (#19): no app to choose default apps in the hypeForge session (Javier). For now KDE's page works here (`kcmshell6 kcm_componentchooser`; Plasma and Hyprland share `~/.config/mimeapps.list`), but it leaves with Plasma. Research a hypeForge pick (nog finds no `selectdefaultapplication`)
  - [ ] `install-into.sh` must link `autostart/nm-applet.desktop` too (it links every file in autostart/, check) and the machine-name variable needs a fresh login to come from uwsm (set by hand for tonight)
  - [ ] Later, not today (Javier): this computer still carries every KDE app, so a clean install will come; and the home folder is a mess of things put there openly. Both are their own topics
- [ ] "Hyprland (uwsm-managed)" is a long, unclear name at the login screen; greetd (D-15) will replace it anyway
- [ ] greetd + tuigreet proven in a VM (console font, Catppuccin palette, wallet unlock) before it replaces SDDM here (D-15, #12)
- [ ] uwsm session in a VM first: crash recovery, `uwsm stop` with hyprshutdown, helpers as user services, and switch off unwanted autostart entries (nm-applet, print-applet) (D-25)
- [ ] Mark `udisks2` as explicitly installed before Plasma leaves (D-26)
- [ ] Live in it. Every rough edge becomes a numbered finding
- [ ] Monitor brightness keys through ddcutil, addressed by I2C bus (3, 4, 5): the three monitors share one name, serial and connector (D-20)
- [ ] Three monitors at 144 Hz, NVIDIA, the login screen, the password pop-up and the wallet all working
- [ ] Every setting in the portable folder, and nothing edited by hand outside it

## Phase 3 · The app
- [ ] forgekit#1 fixed first, so the app is readable on a plain text screen (#8)
- [ ] The hypeForge terminal app: install, adjust, remove
- [ ] The nog lock: a hyprland-family group and its tier (#9)
- [ ] System pieces applied only through the app, with a backup and undo
- [ ] How nog comes along on a plain Arch install

## Phase 4 · Test
- [ ] Test matrix: KognogOS VM, plain Arch VM, then the test desktop (the Omarchy VM only proves the test rig, D-27)
- [ ] A plain-text-screen run in every matrix
- [ ] Each finding (F-n) gets an issue, and they ship as one fix batch

## Phase 5 · Release
- [ ] GitHub Release with full notes, signed
- [ ] AUR package, then add the aur and aur-package topics
- [ ] kognogos.org: change "coming soon" to released

---

## Waiting on Javier's hands
- [ ] Keep the name even though it is one letter from "hyprforge"? (D-1, flagged)

## Open questions
- [ ] The test desktop runs nog's stock tier list, not KognogOS's. Is that on purpose? (found 2026-09-28)
