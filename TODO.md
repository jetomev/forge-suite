# Forge Suite — the list

**Target: the first KognogOS release (v1.0, April 2027).** Each section keeps its own detailed list; this one tracks the suite. Updated after every step.

## 2026-10-20 — hypeForge: Phase 11 closed, one pop-up standard (D-116), Sway tells where the pointer is
- [x] **hypeForge** (details in [hypeforge/TODO.md](hypeforge/TODO.md)): Phase 11 closed (the apps' own title bars → Phase 12, removing KDE → Phase 15); **D-115** Waybar stays, our own bar scratched, a bar guard instead; **D-116** one pop-up standard for v1.0 — the panel kit on every style, the **list card** (on; Javier's live test 3/3); the previews fixed (F-79, F-80, F-81)
- [x] **Our Sway, patch 3** (`hypeforge/sway-hypeforge/0003-…`): `get_seats` says where the pointer is; VM from nothing 7/7 (`hypeforge/testing/20261020 …`)
- [ ] **The full theme review** (Javier: Mac OS 9 · macOS · COSMIC *"0/100"*): every style, pop-up, launcher and colour theme, one by one — a long road
- [x] Pushed 2026-10-22 (Javier: "push, update, document, publish"): the 10 commits, issues #108–#110 (F-79…F-81) opened and closed; hypeForge README roadmap current; Vault entry

## 2026-10-17 — hypeForge: the system on the bar, our own tray polished, title bars, our own Sway build
- [x] **hypeForge** (details in [hypeforge/TODO.md](hypeforge/TODO.md)): our own tray (D-103) and its menu as one window (D-105); CPU · GPU · temperature · memory · disk on the bar with their pop-ups (D-104, "Beautiful!"); F-75 #104 (the night light pop-up waited on a Wi-Fi scan); tray icons in each style's colour and a tray restart with no gap (D-106); even 10 px spacing (D-107); numbers that never move the bar (D-108); the disk piece took the USB icon's job (D-109, his USB test passed) — all approved
- [x] **Title bars on floating windows + the window menu** (D-110): left drag moves, middle click tucks away, right click = float / back into the grid, full screen, workspaces, close; `scripts/titlebar-bench.py` 16/16 — live, his test next
- [ ] **Our own Sway build** (D-111): minimise / maximise / close buttons on the title bar (`hypeforge/sway-hypeforge/`: patch, `build.py`, update-safe login with fallback — his rule: a Sway update must never break the desktop); bench 22/22 — **next:** the test login entry (one sudo), his test, then the main login + a safe-mode entry

## 2026-10-13 — themeForge's Wallpaper page three runs deep, the bars share their pop-ups, Settings talks to its panes
- [x] **themeForge** (details in [themeforge/TODO.md](themeforge/TODO.md)): the Wallpaper page redesigned as Javier drew it (D-8, D-9), then from his runs: Browse as a small file manager (D-10), the first picture by itself and the sharp preview inside Settings (D-11); F-73 and F-74 fixed; #96 and #90 closed on his "perfect!!!"; tests 48, overlay bench 15/15
- [x] **hypeForge** (details in [hypeforge/TODO.md](hypeforge/TODO.md)): the Rice's gaps 14 → 10 (D-95); **three pop-ups, one version each, on every style** (D-96: the date-time-bell piece, the Quick Settings pill, the night-light moon, defined once; `hypeforge-bar` places pop-ups itself); Settings hands its terminal's cells to the apps in its panes (D-97); a sent window lands by the fill order (D-98, "tested, works!"); the brightness keys on a desktop too (D-99, #94); #95 was a false finding — the audit looked up a /usr/lib program on PATH
- [x] **Issue sweep** across all 17 repos (Javier: "close whatever has been already finished"): #84 themeForge born, #56 workspaceForge, #44 nightForge, #19 default apps, #61 F-54 closed here; nogforge #1 too. Issues #96 #98–#103 opened and closed with the day
- [ ] **nightForge 1.1** (#82) with themeForge's next batch · **mindForge 0.1.9** carries the brief fix (#46) and #64

## 2026-10-12 · CLAUDE.md keeps only this project's own rules
- [x] **One rule, one level** (Javier, 2026-10-12): the suite file and nine section files keep only their own rules (decisions file, versioning, signing); plain words, nog first, TODO after every step and the co-author trailer come from the global agreement and the release rules. Commit pushed the same night.

## 2026-10-11 — what every app needs, measured (#91)
- [x] **The dependency audit** (Javier: "check all Forge Suite apps for all dependencies needed to build and run them. Very important to have done now"): `scripts/needs-audit.py` (imports, programs, linked libraries → Arch packages, beside each AUR recipe); `docs/PACKAGING.md` + `tests/test_needs.py` in every section and every outside app (nog and mindForge: the list); **every AUR recipe built in a clean Arch system** (devtools, the kognog-hypeforge VM, snapshot `before-needs-audit`)
- [x] Found: **three published packages don't build on a clean system** — displayForge 1.1.0 (F-7 #92, a test assumed ddcutil), nightForge 1.0.0 (F-1 #93, a test assumed Miami time), grubForge 2.2.0 (grubforge#41, F-8: reload() read the system's GRUB file); **recipes missing needs** — nog sudo + zstd (nog#50), python-rich (displayForge, workspaceForge, nightForge), glib2 (nightForge), grub (grubForge), optional flatpak/snapd (nog, nogForge); hypeForge F-71 #94 (brightnessctl), F-72 #95 (pam_kwallet_init); the wallpaper generator lives in docs/; KognogOS's profiles list none of hypeForge's 34 needs (KognogOS TODO)
- [x] Fixed and proven in the clean system: nog 1.8.0-2, workspaceForge 1.0.0-2, displayForge 1.1.1 · nightForge 1.1.0's own new tray test read hypeForge's files (fixed with fixtures, `06ab889`)
- [x] **GitHub Releases** (signed tags + assets, checksums checked against the downloads): displayForge 1.1.1, nightForge 1.1.0 (Latest), grubForge v2.2.1; issues #58 #92 #93 #82 grubforge#41 closed
- [x] **Javier's local test passed** (`scripts/install-aur-batch.sh`), **all six on the AUR** (nog 1.8.0-2, workspaceForge 1.0.0-2, nogForge 1.4.0-2, displayForge 1.1.1, nightForge 1.1.0, grubForge 2.2.1; RPC checked); #91 and nog#50 closed

## 2026-10-10 / 11 — hypeForge's look program: all six styles built
- [x] **hypeForge** (details in [hypeforge/TODO.md](hypeforge/TODO.md)): Mac OS 9, KDE, COSMIC and macOS built and live-tested (the Rice and Windows 11 the day before) — six styles × 25 colour themes; one bar program with a bar per screen, pop-ups on the clicked screen (D-86); the dock on the main screen (D-87); macOS (D-88); the Rice in Javier's order (D-89); issues #67–#83; Vault (68)–(70); kognogos.org card and hypeForge's README current
- [x] **themeForge 0.1.0** (new section, #84, 2026-10-11): the Theme Picker — theme and colours, two drop-downs, Apply / Undo through hypeForge; the Look page + Home card in Settings, launcher entry, float rule; 14 tests — **waits for Javier's run**; more pages later (pop-ups, icons, fonts…), then the tray icon
- [ ] **nightForge 1.1** (#82): hide its tray icon where a hypeForge bar shows the night-light moon — released with the themeForge batch, AUR after Javier's local test
- [ ] **The frost** (#83): see-through, blurred bars on the SwayFX login, every style

## 2026-10-09 — three new apps in a day, and every app says where it runs
- [x] **workspaceForge 1.0.0** (new section): designed, approved, built, released — GitHub Latest, AUR after Javier's local test, kognogos.org card; the F-50 engine in hypeForge's Workspaces applet (F-51 loop found and fixed on the new hidden bench)
- [x] **Where it runs, everywhere** (Javier's rule): a line on every README + GitHub About + kognogos.org card; AUR descriptions at each app's next release
- [x] **displayForge 1.1.0 + mindForge 0.1.7 on the AUR** (signed files added to their releases; Javier's local tests) — 10 on the AUR
- [x] **nightForge** (new section, #44): the night light's app + its own tray icon, live at login; **1.0.0 prepared, the tag waits for Javier's sunset check**
- [x] **defaultappsForge** (new section, #19): designed ("WOW APP!!!!"), 0.1.0 built and in hypeForge Settings — **waits for Javier's run**
- [x] **displayForge 1.1.1** (#58 F-6 + #92 F-7) — released 2026-10-11, GitHub + AUR
- [ ] Section rows in the suite README for nightForge and defaultappsForge — at their releases

## 2026-10-08 — six releases from Javier's runs inside hypeForge Settings
- [x] **forgekit 0.10.0** (AUR first) + **displayForge 1.1.0**, and outside the suite **alacrittyForge 1.1.0 · nogForge 1.4.0 · grubForge 2.2.0 · bitlaForge 1.1.0** — GitHub → Javier's run on the installed packages ("all perfect!") → AUR. Every app: Ctrl + the underlined letter by Javier's rule, numbers with Help, "1-N menu", About/License/Keys/Manual as pages, `--hypeforge`, labels "Words (key)" (hypeForge D-62); 17 issues closed
- [x] hypeForge: launcher Forge Suite group → Settings (D-63), then standard groups (D-64); **Settings 0.5.0 Home page** (#46, D-65); kognogos.org updated twice
- [ ] Desktop entries in each AUR package (Ideas below) — still open; the four 10-08 releases did not add them

## The move-in (D-60, phased)
- [x] `jetomev/hypeforge` renamed `jetomev/forge-suite` (old links redirect); hypeForge moved into `hypeforge/` (2026-10-05)
- [x] GitHub About + topics for the suite (2026-10-06)
- [x] kognogos.org: "KognogOS = nog + the Forge Suite", hypeForge on Sway with the new banner, displayForge 1.0, forgekit's new home, 6 on the AUR — live 2026-10-06 (homelab `a9fdc2e`)
- [x] **forgekit moved in** (2026-10-06): full history, tags `forgekit-v0.1.0…v0.6.0`, old repo archived with a pointer, `~/Programs/forgekit` → shortcut. At its next release the AUR recipe points here
- [ ] alacrittyForge · bitlaForge · nogForge move in, one at a time, each tested; AUR recipes repointed
- [ ] grubForge moves in last (most users, outside contributors)
- [ ] Release rules (`~/.claude/rules/release.md`) adapted for per-app tags in one repository

## Ideas
- [ ] **Desktop entries in every Forge app's package** (2026-10-06): none of the four AUR apps ships one — grubforge#37, alacrittyforge#18, bitlaforge#12, nogforge#16; hypeForge carries its own until then
- [ ] **fileForge** (Javier, 2026-10-06) — our own file manager, **later**: forgekit look, **full mouse support** (what superfile lacks for him), keyboard too. Replaces the mcForge question below.
- [ ] **mcForge?** (Javier, 2026-10-06) — Midnight Commander is free software (GPLv3, written in C, github.com/MidnightCommander/mc), so a fork is allowed, and GPLv3 matches ours. Honest size: ~300,000 lines of C, 30 years old — a fork means maintaining all of it. Lighter path that fits D-59: an **mcForge settings app** (look, editor, panels, keys) over the stock mc. Decide later.

## Sections
- **walletForge** — **born 2026-10-07** (D-1, D-2): our own secret store, replacing KDE's before KDE leaves; copies its entries; SSH keys + GPG in scope; not urgent — the login password already opens KDE's store through hypeForge's PAM handshake (#41) → [walletforge/TODO.md](walletforge/TODO.md)
- **sudoForge** — **1.0.1 released and installed 2026-10-07** (F-2 #37 closed: the first backup of `/etc/sudo.conf` is kept, this desktop's backup repaired; 38 tests), after 1.0.0 on 2026-10-06 (AUR `sudoforge`; closes hypeForge F-42/F-44); next: a sudoForge pinentry and the keyring → [sudoforge/TODO.md](sudoforge/TODO.md)
- **displayForge** — **1.0.1 released 2026-10-06** (Sway only, checked at launch); next: the 1.0.x tests, the KDE-login check → [displayforge/TODO.md](displayforge/TODO.md)
- **forgekit** — **0.9.0 released 2026-10-07** (the menu bar wraps on a narrow window, #40, Javier: URGENT; 110 tests), after 0.8.0 on 10-06 (the password's dots centred, #34); next: button labels "Words (k)", fold sudoForge's session agent back in → [forgekit/TODO.md](forgekit/TODO.md)
- **hypeForge** — the bar, launcher, sound / network / Bluetooth / USB done; the password pop-up done (sudoForge); next: printing, night light → [hypeforge/TODO.md](hypeforge/TODO.md)
- [x] **Every surface shows live versions** (Javier, 2026-10-06): kognogos.org (rebuilt in the homelab repo — it had been server-only and was wiped by a deploy), and live badges in the KognogOS, suite and hypeForge READMEs; kognogos.org "Honest progress" brought current

## 2026-10-07 — the issue sweep
- [x] **17 open issues → 5** (Javier: "close them all tonight"). Closed with a full explanation each: #33 and #32 had shipped (forgekit 0.7.0, displayForge 1.0.1) and were left open by oversight; #17 #16 #15 #9 #13 #5 #7 #4 described the Hyprland days, cleared off this computer on 10-05; #8 holds by construction (every app is on forgekit ≥ 0.4); #22 (D-44) is carried out, Phase 10 complete. Left open: #37 (sudoForge 1.0.1, tonight), #25 (F-43, fix prepared, Javier's test), #19 (default apps, a pick for Javier), #23 (F-41, Javier deferred it 10-04), #10 (the Plasma marker, by rule)
- [x] Later the same night: F-43 (#25) and F-41 (#23) proven and closed; **Claude Desktop's login on Sway (#39)**: flags file + `exec ksecretd` at login — after the reboot the store runs from login and the wallet unlocks through KDE's password window once per login (the Forge wallet, D-61, replaces that window); nine-spot window order (#38), forgekit menu bar (#40) filed; Javier's Settings catalogue + the agreed v1.0 cut ranked in hypeForge's TODO
- [x] Found on the way: `monique` 0.8.3 (the Hyprland screens app) was still installed and unused — removed by Javier 10-07 (nog from Claude's shell could not: no terminal to answer pacman's question → folded into jetomev/nog#32)

## 2026-10-06 evening — the first releases from the suite
- [x] **forgekit 0.7.0** (`forgekit-v0.7.0`, GitHub Release with signed assets, AUR `python-forgekit` fetching from this repository) and **displayForge 1.0.1** (`displayforge-v1.0.1`, Latest): the per-app tag release works end to end. Details in each section's TODO
- [ ] Write the per-app release recipe (archive a section at its tag, sign, Release, AUR) into `forgekit/CLAUDE.md` and this file, now that it is proven
