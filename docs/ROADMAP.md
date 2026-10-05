# hypeForge — roadmap

*Upcoming work first, then history, newest first. The README carries a summary; this page has the detail. Every phase ends with the usual release discipline: a `Phase N:` commit, a docs commit with the version bump, and an annotated tag.*

---

## Upcoming — the Sway path (from 4 October 2026, D-44 / D-45)

The live, step-by-step list is [TODO.md](../TODO.md) (Phases 10–14). In short:

- [x] **Choose the base:** Sway 1.12 (D-45); three screens at 144 Hz on the NVIDIA test desktop
- [ ] **The jobs, one by one, terminal first (D-57):** workspaces ✅, window placement ✅, launcher with sections and favourites ✅, window rules ✅, Help & Keys ✅, lock screen + idle ✅, KDE apps replaced (numbat, cliamp) ✅ · next: notifications, screenshots, sound / network / Bluetooth, the password pop-up (our own app, D-56)
- [ ] **Our own look:** folder-style tabs, our own top bar, a palette from the KognogOS brand
- [ ] **The Forge Suite apps (D-59):** one Forge app per setting, held by **hypeForge Settings**, the control centre
- [ ] **The first KognogOS release** with hypeForge as its only desktop

---

## The first attempt (28 Sep – 3 Oct 2026) — history

*A floating Hyprland desktop with Noctalia. Kept as it was when the restart was decided (D-44).*

### Phase 0 · Foundations — 🔄 in progress
- [x] Name chosen: **hypeForge** ([D-1](DECISIONS.md#d-1--the-name-is-hypeforge))
- [x] Decisions of the first night logged ([DECISIONS.md](DECISIONS.md))
- [x] Public repository: README, About, topics, labels, milestones, [issues](https://github.com/jetomev/hypeforge/issues)
- [x] Research notes of the first night ([research/2026-09-28-kickoff.md](research/2026-09-28-kickoff.md))
- [x] [kognogos.org](https://kognogos.org/#hypeforge) announces hypeForge as coming soon
- [x] Recipe research: up to five options per job, with sources ([RECIPE.md](RECIPE.md)) · #1, #11
- [x] Virtual machines that can run Hyprland: 3D graphics switched on and proven on the NVIDIA desktop · #2
- [x] Omarchy machine, a known-good Hyprland setup: installed and snapshotted 2026-09-28 · #3
- [ ] A real KognogOS machine, from a fully rebuilt KognogOS installer image *(KognogOS work)* · #4
- [ ] A saved clean state (snapshot) on every test machine

### Phase 1 · The recipe
- [x] First choice: separate small apps ([D-14](DECISIONS.md)) · #6
- [x] One app chosen per job: all 32, on 2026-09-29, each a first try ([D-14 to D-26](DECISIONS.md))
- [x] Floating-first windows with Win + arrow snapping, proven in Hyprland 0.56 (Lua) · #5
- [x] The full key map: Plasma's keys keep their jobs (D-29)
- [x] The portable folder layout: a full copy (D-28) · #7
- [ ] The Catppuccin Mocha look for every chosen app

### Phase 2 · Build it by hand
- [ ] Build the desktop by hand on the test desktop, next to the existing one
- [ ] Live in it; every rough edge becomes a numbered finding
- [ ] Three monitors at 144 Hz, NVIDIA, the login screen, the password pop-up and the wallet all working
- [ ] Every setting kept in the portable folder, and nothing edited by hand outside it

### Phase 3 · The app
- [ ] [forgekit#1](https://github.com/jetomev/forgekit/issues/1) fixed first: readable on a plain text screen · #8
- [ ] The hypeForge terminal app (install · adjust · remove), on forgekit
- [ ] The nog lock: a `hyprland-family` group and its tier · #9
- [ ] System pieces applied only through the app, with a backup and undo
- [ ] How nog comes along on a plain Arch install

### Phase 4 · Test
- [ ] Test matrix: the KognogOS machine, the plain Arch machine, then the test desktop
- [ ] A run on a plain text screen in every matrix
- [ ] Numbered findings (F-1, F-2…), each with its own issue, shipped as one fix batch

### Phase 5 · Release
- [ ] GitHub Release with full notes, signed
- [ ] AUR package (`hypeforge`), then the `aur` and `aur-package` topics
- [ ] kognogos.org updated from "coming soon" to released

---

## History

*No releases yet. The project started on 2026-09-28.*
