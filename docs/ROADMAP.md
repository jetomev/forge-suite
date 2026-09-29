# hypeForge — roadmap

*Upcoming work first, then history, newest first. The README carries a summary; this page has the detail. Every phase ends with the usual release discipline: a `Phase N:` commit, a docs commit with the version bump, and an annotated tag.*

---

## Upcoming

### Phase 0 · Foundations — 🔄 in progress
- [x] Name chosen: **hypeForge** ([D-1](DECISIONS.md#d-1--the-name-is-hypeforge))
- [x] Decisions of the first night logged ([DECISIONS.md](DECISIONS.md))
- [x] Public repository: README, About, topics, labels, milestones, [issues](https://github.com/jetomev/hypeforge/issues)
- [x] Research notes of the first night ([research/2026-09-28-kickoff.md](research/2026-09-28-kickoff.md))
- [x] [kognogos.org](https://kognogos.org/#hypeforge) announces hypeForge as coming soon
- [ ] Recipe research: up to five options per job, with sources ([RECIPE.md](RECIPE.md)) · #1
- [ ] Virtual machines that can run Hyprland: 3D graphics switched on and proven on the NVIDIA desktop · #2
- [ ] Omarchy reference machine *(proposed, awaiting Javier)* · #3
- [ ] A real KognogOS machine, from a fully rebuilt KognogOS installer image *(KognogOS work)* · #4
- [ ] A saved clean state (snapshot) on every test machine

### Phase 1 · The recipe
- [ ] First choice: one all-in-one desktop program, or separate small apps · #6
- [ ] One app chosen per job
- [ ] Floating-first windows with Win + arrow snapping, proven in Hyprland 0.56 (Lua) · #5
- [ ] The full key map, starting from Plasma's shortcuts on the test desktop
- [ ] The portable folder layout · #7
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
- [ ] Test matrix: Omarchy-reference comparison, the KognogOS machine, the plain Arch machine, then the test desktop
- [ ] A run on a plain text screen in every matrix
- [ ] Numbered findings (F-1, F-2…), each with its own issue, shipped as one fix batch

### Phase 5 · Release
- [ ] GitHub Release with full notes, signed
- [ ] AUR package (`hypeforge`), then the `aur` and `aur-package` topics
- [ ] kognogos.org updated from "coming soon" to released

---

## History

*No releases yet. The project started on 2026-09-28.*
