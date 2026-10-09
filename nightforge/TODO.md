# nightForge — the list

**Target: the Night light page of hypeForge Settings, KognogOS v1.0 (April 2027); started 2026-10-09 (D-1).** Section of the Forge Suite (D-60). Issue #44. Updated after every step.

## Phase 0 · Design
- [x] Research: wlsunset 0.4.0 — options only at start (-t/-T warmth, -l/-L place, -S/-s fixed times, -d fade), SIGUSR1 cycles forced day → forced warm → automatic; no status, no settings file
- [x] The sun worked out on the computer (`nightforge/sun.py`, NOAA formulas): Miami today 07:15 / 19:00, checked against June, London, Svalbard
- [x] Design page: Night Light, Preview, Schedule, the bar's moon, Save; 10 questions — `docs/design/v0.1.0-screens.html`, published https://claude.ai/artifact/XuQYKnzCpXp7KPMCiAoa3G
- [x] First review (D-2): Preview and Save both pop-ups; second draft published
- [x] **Approved** (D-3, "perfect"), with a tray icon (D-4)

## Phase 1 · Build
- [x] Settings (`settings.py`, backup + read-back) + `nightforge start` (login) + restart on save; the preview that goes back by itself; the night light started detached (posix_spawn), stopped by its saved number or (hypeForge's old line) its exact name
- [x] The two pages (Night Light, Schedule), Preview and Save both pop-ups (D-2), quit asks; `--hypeforge`; the manual (3 pages); `nightforge status`
- [x] The tray icon (`nightforge tray`, D-4/D-5): muted ☀ by day, mustard ☾ while warm, dim ○ off; its menu; started by `nightforge start`
- [x] hypeForge: the login line (`nightforge start`, fallbacks), the Settings page + Home card, a launcher entry + float rule (and workspaceForge's, which were missing), Help page 17 — repo + live, backups
- [x] Tests: 23 (core 12, tray 4 on a private bus, pages 7); 10 behaviours broken on purpose, 10 caught; pictures checked by eye (lost spaces, a repeated word, narrow time fields — fixed); `scripts/bench-start.py` (real wlsunset on a hidden Sway, private bus): 14/14, the real night light untouched
- [ ] **NEXT — live:** `nightforge start` on the desktop (takes over today's wlsunset, the tray icon appears) → Javier's run

## Phase 2 · Release
- [ ] Javier's run → 1.0.0, GitHub, AUR after his local test; then README row, kognogos.org card, Vault
