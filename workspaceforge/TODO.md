# workspaceForge — the list

**Target: in hypeForge Settings for KognogOS v1.0 (April 2027); started 2026-10-09 (D-1).** Your workspaces in the terminal: names and order, which apps open on each (however started), and sharing. Section of the Forge Suite (D-60). Updated after every step.

## Phase 0 · Design
- [x] Born (D-1) and scoped to workspaces only (D-2), Javier, 2026-10-09
- [x] Design page drawn with Javier's real values: Workspaces, Delete, Apps, Add an app, Sharing, Save; 8 questions with recommendations — `docs/design/v0.1.0-screens.html`, published https://claude.ai/artifact/9oLhy6kVfMhJSaoiadREwx (2026-10-09)
- [ ] **Javier's approval** of the design and answers to the 8 questions

## Phase 1 · The engine (hypeForge F-50, #55)
- [ ] The Workspaces applet reads per-workspace app lists from `workspaces.toml`, seeded once from the launcher's groups
- [ ] New windows of a listed app go to its workspace, however started; the screens follow (not in the first ~30 s after login)
- [ ] The launcher reads the same lists (one source of truth); `sections.toml`'s `[workspaces]` and group `workspace =` retired
- [ ] Tests, each seen failing first; Javier lives with it, file edited by hand

## Phase 2 · The app
- [ ] Workspaces page (rename, new, delete with windows moved, reorder, on/off)
- [ ] Apps page + Add an app
- [ ] Sharing page (the grid)
- [ ] Review and save (backup, write, `hypeforge-workspaces reload`)
- [ ] Help pages, `--hypeforge`, a "Workspaces" page in hypeForge Settings
- [ ] Tests: 1/2/3 screens, 100 columns, text console, missing or broken file

## Phase 3 · Release
- [ ] Test matrix + Javier's run → 1.0.0, GitHub Release, AUR after his local test
