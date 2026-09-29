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
- [ ] Minimise: Waybar's taskbar in the top bar, minimised windows on a hidden workspace, a small helper until Hyprland 0.57 (D-31, #5)
- [ ] Window buttons: `button-layout` set to minimise, maximise, close (proven in the VM); hyprbars for windows without their own title bar, untested with Lua (D-31)
- [x] Windows open floating at 80 % of the screen, centred; dialogs keep their size (untested); Chromium's "open maximised" undone; Alt + F4 closes (D-32)
- [x] Gaps: 8 between windows, 13 at the edges (D-33)
- [x] Alacritty with KognogOS's `decorations = "Full"` tried in the VM, 2026-09-29: opens floating at 80 %, **but draws no title bar on Hyprland** (screenshot checked). Hyprland takes over decorations and draws only a border (D-33)
- [ ] hyprbars: title bars with minimise, maximise and close for windows that draw none (Alacritty, terminals); build it with hyprpm in the VM and prove it works with Lua settings (D-31, D-33)
- [ ] An Alt + Tab switcher, which Hyprland lacks (#5)
- [ ] Five themes from the KognogOS wallpapers (Mocha, Black, Green, Gray, White): a preview page to choose the palettes (Javier, 2026-09-29)
- [x] The portable folder layout decided: a full copy, with machines/<hostname>/ apart (D-28, #7)
- [ ] The folder round trip: build, copy to a clean VM, apply, same desktop (#7)
- [ ] The Catppuccin Mocha look for every chosen app. Check Krusader when Qt follows GTK, and whether the 2022 Catppuccin theme for Midnight Commander still fits (D-22)

## Phase 2 · Build it by hand
- [ ] Build the desktop by hand on the test desktop, next to the fallback session
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
