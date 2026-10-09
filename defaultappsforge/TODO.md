# defaultappsForge — the list

**Target: the Default apps page of hypeForge Settings, KognogOS v1.0 (April 2027); started 2026-10-09 (D-1).** Section of the Forge Suite (D-60). Issue #19. Updated after every step.

## Phase 0 · Design
- [x] Research: `~/.config/mimeapps.list` + `xdg-mime` on the desktop — PDFs in Chrome (a guess), pictures split Pinta/Chrome, 3 old choices for apps that are gone (Typora, Nemo, Brave), Ark and Konsole leave with KDE; 1,129 file types known
- [x] Design page: Kinds, Change (pop-up), File Types, Save (pop-up); 9 questions — `docs/design/v0.1.0-screens.html`, published https://claude.ai/artifact/TQfbogzb7BwSq1T4PqVK2A
- [x] First review (D-2): his 13 default apps with drop-downs, no status; File Types = two tables with >> / <<; second draft published
- [x] Second review (D-3): Defaults / Selection titles, bullets, drop-downs closer, a gap between rows; File Types' tables aligned from the top; third draft published
- [ ] **Javier's approval**

## Phase 1 · Build
- [ ] Reading the apps and what each opens; the system's guess; mimeapps.list read and written keeping what we don't touch
- [ ] Kinds and File Types pages, Change and Save pop-ups, quit asks, `--hypeforge`, the manual
- [ ] hypeForge: the Default apps page + Home card, a launcher entry + float rule, Help
- [ ] Tests (each seen failing first), pictures

## Phase 2 · Release
- [ ] Javier's run → 1.0.0, GitHub, AUR after his local test; README row, kognogos.org, Vault
