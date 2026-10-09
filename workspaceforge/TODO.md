# workspaceForge — the list

**Target: in hypeForge Settings for KognogOS v1.0 (April 2027); started 2026-10-09 (D-1).** Your workspaces in the terminal: names and order, which apps open on each (however started), and sharing. Section of the Forge Suite (D-60). Updated after every step.

## Phase 0 · Design
- [x] Born (D-1) and scoped to workspaces only (D-2), Javier, 2026-10-09
- [x] Design page drawn with Javier's real values: Workspaces, Delete, Apps, Add an app, Sharing, Save; 8 questions with recommendations — `docs/design/v0.1.0-screens.html`, published https://claude.ai/artifact/9oLhy6kVfMhJSaoiadREwx (2026-10-09)
- [x] First review (Javier, 2026-10-09, D-3): workspaces dynamic; Apps = two tables with `>>` / `<<`; second draft published
- [x] Second review (Javier, 2026-10-09, D-4): buttons on top; new and edit on the page, not pop-ups; ⚠ note after a rename; Apps "perfect"; Sharing = a switch per cell + Save; third draft published
- [x] **Approved** (Javier, 2026-10-09: "approved!!!!"; D-5) — the third draft, the 11 questions answered by the recommendations (tracking issue #56)

## Phase 1 · The engine (hypeForge F-50, #55)
- [ ] **NEXT** — The Workspaces applet reads per-workspace app lists from `workspaces.toml`, seeded once from the launcher's groups
- [ ] New windows of a listed app go to its workspace, however started; the screens follow (not in the first ~30 s after login)
- [ ] The launcher reads the same lists (one source of truth); `sections.toml`'s `[workspaces]` and group `workspace =` retired
- [ ] Tests, each seen failing first; Javier lives with it, file edited by hand

## Phase 2 · The app
- [ ] Workspaces page: buttons on top; new and edit in place (⚠ note after a rename); delete pop-up moving windows; reorder; on/off
- [ ] Apps page: the two tables, ticks, Select All / Deselect All (rows showing), `>>` / `<<`, the open-one-at-a-time workspaces
- [ ] Sharing page: the grid with an Own / Shared switch per cell, Save at the bottom
- [ ] Review and save (backup, write, `hypeforge-workspaces reload`)
- [ ] Help pages, `--hypeforge`, a "Workspaces" page in hypeForge Settings
- [ ] Tests: 1/2/3 screens, 100 columns, text console, missing or broken file

## Phase 3 · Release
- [ ] Test matrix + Javier's run → 1.0.0, GitHub Release, AUR after his local test
- [ ] **Only then, the public documentation** (Javier, 2026-10-09: "Documentation is updated only after the app is approved to publish"): the suite README's row, the kognogos.org card (drafted in homelab `fa3496b`, backed out), hypeForge's README and Help pages
