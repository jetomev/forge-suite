# workspaceForge — the list

**Target: in hypeForge Settings for KognogOS v1.0 (April 2027); started 2026-10-09 (D-1).** Your workspaces in the terminal: names and order, which apps open on each (however started), and sharing. Section of the Forge Suite (D-60). Updated after every step.

## Phase 0 · Design
- [x] Born (D-1) and scoped to workspaces only (D-2), Javier, 2026-10-09
- [x] Design page drawn with Javier's real values: Workspaces, Delete, Apps, Add an app, Sharing, Save; 8 questions with recommendations — `docs/design/v0.1.0-screens.html`, published https://claude.ai/artifact/9oLhy6kVfMhJSaoiadREwx (2026-10-09)
- [x] First review (Javier, 2026-10-09, D-3): workspaces dynamic; Apps = two tables with `>>` / `<<`; second draft published
- [x] Second review (Javier, 2026-10-09, D-4): buttons on top; new and edit on the page, not pop-ups; ⚠ note after a rename; Apps "perfect"; Sharing = a switch per cell + Save; third draft published
- [x] **Approved** (Javier, 2026-10-09: "approved!!!!"; D-5) — the third draft, the 11 questions answered by the recommendations (tracking issue #56)

## Phase 1 · The engine (hypeForge F-50, #55)
- [x] The Workspaces applet reads per-workspace app lists from `workspaces.toml`; the repo's default seeded once from the launcher's groups (`scripts/seed-workspace-apps.py`), 2026-10-09
- [x] New windows of a listed app go to its workspace, however started; the screens follow (not in the first ~30 s after login); Placement's fill order moved to `common/hfplace.py` and leaves those windows to the Workspaces applet (a hidden mark), which places them itself
- [x] The launcher reads the same lists (one source of truth): typed, Favorites, All apps or a group, all the same; terminal apps open as `alacritty --class <id>` so btop is told apart from a plain terminal; `sections.toml`'s `[workspaces]` and group `workspace =` retired
- [x] Tests: 17 new (36 in hypeForge), and 12 pieces of the engine broken on purpose in a copy — each one caught
- [x] Switched on live 11:57 (lists seeded, Alacritty off every list — Javier; launcher keys retired; backups kept); Javier's launcher tests 1–4 passed, and Sim Companies from cold (Steam closed) opened Steam + the game on Gaming
- [x] **F-51 (#57), 12:05:** `supertux2 &` from a terminal set the workspaces switching non-stop; desktop locked, reboot from tty3. Lists taken off live (backup); reproduced on the new hidden bench (`hypeforge/scripts/headless-check.py`: 301 switches in 10 s) → fixed (act on the focused workspace now, never a stale event; safety valve 12 switches / 3 s) → 4 switches, 4 runs of 4 (`d48ce5e`); fixed applets live, lists still off
- [x] Lists back on live; **Javier's retest passed** (~12:40, `supertux2 &` → Gaming once: "this time worked, perfectly"; the safety valve never fired) → #57 and #55 closed

**Phase 1 complete (2026-10-09).** NEXT: Phase 2, the app.
- [ ] Known gaps: WoW (Wine) calls its window `wow.exe` — not matched until its launcher entry says so (StartupWMClass); more than 9 workspaces needs the cell numbering changed (Grid uses `i + 10 × screen`)

## Phase 2 · The app
- [x] Workspaces page: buttons on top; new and edit in place (⚠ note after a rename); delete pop-up moving windows; reorder; on/off
- [x] Apps page: the two tables, ticks, Select All / Deselect All (rows showing), `>>` / `<<`, the open-one-at-a-time workspaces; Find + Category filters; headings sort ▲ ▼
- [x] Sharing page: the grid with an Own / Shared switch per cell, arrows between them, Save / Undo at the bottom
- [x] Review and save: backup (20 kept), open windows carried to their workspace's new name/place, write (read back), the applet reloaded; quit asks to save
- [x] Manual (5 pages), `--hypeforge`, the **Workspaces** page in hypeForge Settings (repo + live) and its Home card
- [x] Tests: 33 (model 18, pages 15), 12 behaviours broken on purpose — 12 caught; 100 × 30 pictures checked by eye (found 3 bugs: a rename counted its apps as changes, sharing planned clashing renames, clipped text — fixed, with tests); text console preview clean; `scripts/bench-save.py` (rename + swap + delete on a hidden Sway) OK twice
- [x] **Javier's first run (2026-10-09 ~13:40):** Workspaces "works well"; Apps "work well", but both tables should be at the same height → one header row across both sides, the tables start and end on the same lines (fixed the same hour)
- [x] Sharing off the menu for now (Javier, D-7); the file's sharing kept on save
- [ ] **Sharing, rethought** — waits on Javier ("have to think better about this section"); SharingView dormant in app.py
- [ ] More than nine workspaces (D-6): the applet's cell naming changes first, with a bench test
- [ ] Not yet tried: one or two screens (a VM), a real tty

## Phase 3 · Release
- [x] 1.0.0 (Javier: "this is workspaceForge v1.0", D-8): version everywhere, changelog, roadmap, matrix + results in `testing/`
- [x] Tag `workspaceforge-v1.0.0` (signed), GitHub Release (Latest) with 4 signed assets
- [x] AUR `workspaceforge` 1.0.0-1: built locally (checksum, signature, 33/33 tests in check()), **Javier installed and tested it**, then pushed (`e4f649c`, 2026-10-09)
- [x] kognogos.org card live (homelab `80c86bb`, server backup first), with every card's "Runs on" line
- [ ] **Only then, the public documentation** (Javier, 2026-10-09: "Documentation is updated only after the app is approved to publish"): the suite README's row, the kognogos.org card (drafted in homelab `fa3496b`, backed out), hypeForge's README and Help pages
