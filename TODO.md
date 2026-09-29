# hypeForge — the list

**Target: no date set — started 28 Sep 2026.** A Forge Suite app that installs the KognogOS Hyprland desktop onto any Arch install.
The reasons behind each item are in `docs/DECISIONS.md` and `docs/DESIGN.md`. This file only lists what gets done.

**Updated after every step.** Run `bash scripts/status.sh` for the short version.

---

## LOCKED — decided by Javier (details in docs/DECISIONS.md)
- **Name:** hypeForge, package `hypeforge` (D-1)
- **Base:** Hyprland, with settings written in Lua only (D-3, D-5)
- **Plasma is being replaced.** KognogOS moves off it little by little (D-6)
- **Windows float by default. Win + arrows tile them, like Plasma** (D-7)
- **One portable folder. System changes happen only through the app** (D-8)
- **The Hyprland family's updates are locked by us, through nog** (D-9)
- **Forge apps run in Alacritty and must be readable on a plain text screen. forgekit#1 gets fixed first** (D-10)
- **The recipe shows up to 5 researched options per job, and Javier chooses** (D-11)
- **Testing happens in VMs. The KognogOS installer image gets fully rebuilt first** (D-12)
- **Omarchy is the reference** (D-4)
- **Documentation at every step, a full GitHub, and a coming-soon note on kognogos.org** (D-13)

---

## Phase 0 · Foundations
- [x] Name chosen: hypeForge. Free on the AUR and on GitHub (D-1)
- [x] Project folder, README, decision log, design notes, research notes, roadmap, changelog, test plan
- [ ] Public GitHub repository with About, topics, labels, milestones and issues
- [ ] kognogos.org shows hypeForge as coming soon
- [ ] Recipe research: up to 5 options per job, with sources, in docs/RECIPE.md
- [ ] Research whether floating-first windows with Win + arrow snapping work in Hyprland 0.56 (Lua)
- [ ] VM 3D graphics proven on the NVIDIA desktop
- [ ] Omarchy reference VM (waiting on Javier's go-ahead)
- [ ] A real KognogOS VM, from a fully rebuilt KognogOS installer image (KognogOS work)
- [ ] A clean snapshot on every test VM

## Phase 1 · The recipe
- [ ] First choice: one all-in-one desktop program, or separate small apps
- [ ] Javier picks one option per job
- [ ] Floating-first windows with Win + arrow snapping, proven in Hyprland 0.56 (Lua)
- [ ] The full key map, starting from Plasma's shortcuts on the test desktop
- [ ] The portable folder layout decided
- [ ] The Catppuccin Mocha look for every chosen app

## Phase 2 · Build it by hand
- [ ] Build the desktop by hand on the test desktop, next to the fallback session
- [ ] Live in it. Every rough edge becomes a numbered finding
- [ ] Three monitors at 144 Hz, NVIDIA, the login screen, the password pop-up and the wallet all working
- [ ] Every setting in the portable folder, and nothing edited by hand outside it

## Phase 3 · The app
- [ ] forgekit#1 fixed first, so the app is readable on a plain text screen
- [ ] The hypeForge terminal app: install, adjust, remove
- [ ] The nog lock: a hyprland-family group and its tier
- [ ] System pieces applied only through the app, with a backup and undo
- [ ] How nog comes along on a plain Arch install

## Phase 4 · Test
- [ ] Test matrix: Omarchy comparison, KognogOS VM, plain Arch VM, then the test desktop
- [ ] A plain-text-screen run in every matrix
- [ ] Each finding (F-n) gets an issue, and they ship as one fix batch

## Phase 5 · Release
- [ ] GitHub Release with full notes, signed
- [ ] AUR package, then add the aur and aur-package topics
- [ ] kognogos.org: change "coming soon" to released

---

## Waiting on Javier's hands
- [ ] Go or no-go on the Omarchy reference VM (about a 6 GB download, and he runs its installer)
- [ ] Confirm that Plasma stays installed as the fallback session until hypeForge passes its tests (D-6, proposed)
- [ ] Keep the name even though it is one letter from "hyprforge"? (D-1, flagged)
- [ ] Recipe choices, once the options page is ready

## Open questions
- [ ] The test desktop runs nog's stock tier list, not KognogOS's. Is that on purpose? (found 2026-09-28)
