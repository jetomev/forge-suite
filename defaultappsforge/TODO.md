# defaultappsForge — the list

**Target: the Default apps page of hypeForge Settings, KognogOS v1.0 (April 2027); started 2026-10-09 (D-1).** Section of the Forge Suite (D-60). Issue #19. Updated after every step.

## Phase 0 · Design
- [x] Research: `~/.config/mimeapps.list` + `xdg-mime` on the desktop — PDFs in Chrome (a guess), pictures split Pinta/Chrome, 3 old choices for apps that are gone (Typora, Nemo, Brave), Ark and Konsole leave with KDE; 1,129 file types known
- [x] Design page: Kinds, Change (pop-up), File Types, Save (pop-up); 9 questions — `docs/design/v0.1.0-screens.html`, published https://claude.ai/artifact/TQfbogzb7BwSq1T4PqVK2A
- [x] First review (D-2): his 13 default apps with drop-downs, no status; File Types = two tables with >> / <<; second draft published
- [x] Second review (D-3): Defaults / Selection titles, bullets, drop-downs closer, a gap between rows; File Types' tables aligned from the top; third draft published
- [x] **Approved** (D-4, "WOW APP!!!!"): space under the titles; Office Suite added (14), xdg-terminal-exec for the terminal, Phone Numbers kept

## Phase 1 · Build
- [x] Reading the apps and what each opens (the current app always offered; same-named apps told apart); the system's guess (xdg-mime); mimeapps.list read and written line by line, keeping everything we don't touch; old choices for gone apps tidied; only what changed is written
- [x] Default Apps (14 one-line drop-downs under Defaults / Selection) and File Types (two tables, >> / <<, aligned), Save a pop-up review, quit asks, `--hypeforge`, the manual (3 pages); the terminal through xdg-terminal-exec (installed with nog on save when needed)
- [x] hypeForge: the Default apps page + Home card (links · folders · text), a launcher entry + float rule, Help page 16 rewritten, Win + Enter follows the chosen terminal — repo + live, backups; hypeForge's card tests now find cards by name
- [x] Tests: 19 (model 13, pages 6); 7 deliberate breaks caught (one mutation first hit an unreached branch → re-done, plus a new-user test); pictures checked (glued titles, 3-line drop-downs, cut titles — fixed)
- [x] Found on the way: **displayForge F-6 (#58)** — one-screen computers crash at start (Select.BLANK is False in Textual 8): fixed + test, release 1.1.1 waits on Javier
- [ ] **NEXT — Javier's run**

## Phase 2 · Release
- [ ] Javier's run → 1.0.0, GitHub, AUR after his local test; README row, kognogos.org, Vault
