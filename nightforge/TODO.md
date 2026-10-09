# nightForge — the list

**Target: the Night light page of hypeForge Settings, KognogOS v1.0 (April 2027); started 2026-10-09 (D-1).** Section of the Forge Suite (D-60). Issue #44. Updated after every step.

## Phase 0 · Design
- [x] Research: wlsunset 0.4.0 — options only at start (-t/-T warmth, -l/-L place, -S/-s fixed times, -d fade), SIGUSR1 cycles forced day → forced warm → automatic; no status, no settings file
- [x] The sun worked out on the computer (`nightforge/sun.py`, NOAA formulas): Miami today 07:15 / 19:00, checked against June, London, Svalbard
- [x] Design page: Night Light, Preview, Schedule, the bar's moon, Save; 10 questions — `docs/design/v0.1.0-screens.html`, published https://claude.ai/artifact/XuQYKnzCpXp7KPMCiAoa3G
- [x] First review (D-2): Preview and Save both pop-ups; second draft published
- [ ] **Javier's approval**

## Phase 1 · Build
- [ ] Settings + `nightforge start` (login) + restart on save; the preview that goes back by itself
- [ ] The two pages, review and save, quit asks; `--hypeforge`; the manual
- [ ] hypeForge: the login line, the moon on the bar, the Settings page + Home card, Help page 17
- [ ] Tests (each seen failing first), pictures, the hidden bench

## Phase 2 · Release
- [ ] Javier's run → 1.0.0, GitHub, AUR after his local test; then README row, kognogos.org card, Vault
