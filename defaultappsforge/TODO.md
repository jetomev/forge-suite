# defaultappsForge — the list

**Target: the Default apps page of hypeForge Settings, KognogOS v1.0 (April 2027); started 2026-10-09 (D-1).** Section of the Forge Suite (D-60). Issue #19. Updated after every step.

## 2026-10-11 · What it needs, measured
- [x] **What it needs, measured** (2026-10-11, #91): `docs/PACKAGING.md` + `tests/test_needs.py` (no package yet: the list is its future recipe; xdg-terminal-exec named but not installed here)

## Phase 0 · Design
- [x] Research: `~/.config/mimeapps.list` + `xdg-mime` on the desktop — PDFs in Chrome (a guess), pictures split Pinta/Chrome, 3 old choices for apps that are gone (Typora, Nemo, Brave), Ark and Konsole leave with KDE; 1,129 file types known
- [x] Design page: Kinds, Change (pop-up), File Types, Save (pop-up); 9 questions — `docs/design/v0.1.0-screens.html`, published https://github.com/jetomev/forge-suite/blob/main/defaultappsforge/docs/design/v0.1.0-screens.html
- [x] First review (D-2): his 13 default apps with drop-downs, no status; File Types = two tables with >> / <<; second draft published
- [x] Second review (D-3): Defaults / Selection titles, bullets, drop-downs closer, a gap between rows; File Types' tables aligned from the top; third draft published
- [x] **Approved** (D-4, "WOW APP!!!!"): space under the titles; Office Suite added (14), xdg-terminal-exec for the terminal, Phone Numbers kept

## Phase 1 · Build
- [x] Reading the apps and what each opens (the current app always offered; same-named apps told apart); the system's guess (xdg-mime); mimeapps.list read and written line by line, keeping everything we don't touch; old choices for gone apps tidied; only what changed is written
- [x] Default Apps (14 one-line drop-downs under Defaults / Selection) and File Types (two tables, >> / <<, aligned), Save a pop-up review, quit asks, `--hypeforge`, the manual (3 pages); the terminal through xdg-terminal-exec (installed with nog on save when needed)
- [x] hypeForge: the Default apps page + Home card (links · folders · text), a launcher entry + float rule, Help page 16 rewritten, Win + Enter follows the chosen terminal — repo + live, backups; hypeForge's card tests now find cards by name
- [x] Tests: 19 (model 13, pages 6); 7 deliberate breaks caught (one mutation first hit an unreached branch → re-done, plus a new-user test); pictures checked (glued titles, 3-line drop-downs, cut titles — fixed)
- [x] Found on the way: **displayForge F-6 (#58)** — one-screen computers crash at start (Select.BLANK is False in Textual 8): fixed + test, release 1.1.1 waits on Javier
- [x] **NEXT — Javier's run**
  - **passed 2026-10-28:** web apps (his own Gmail + Google Calendar picks, saved and working) · Find more… · Any app… — all ✅; next: 1.0.0

## Phase 1b · Every job's choices (D-5, Javier 2026-10-27: "all look good")
- [x] Web apps as choices: Gmail, Outlook (email) · Google Calendar, Outlook calendar (calendar) · Google Maps, OpenStreetMap (map) · Google Voice (phone); a launcher written on save; Chrome/Chromium/Brave `--app=`, else a tab — **built 2026-10-27** (`webapps.py`, `webapp-open`; links only, never files; tests 30); hypeForge's day click opens it on that day
  - **his run 2026-10-28:** he picked Gmail (email) and Google Calendar (calendar) himself in Settings → Default apps; a click on a calendar day opened Google Calendar on that day (hypeForge D-125)
- [x] Any app… : every installed app, for any job
  - **built 2026-10-27** (forgekit's FilterPicker; tests 4)
  - **his try 2026-10-28:** Music Player → Any app… showed every app, the list shrank as he typed, Esc changed nothing ✅
- [x] Find more… : nogForge searching for that kind of app (waits on nogForge `--search`) — **built 2026-10-27** (with nogForge's `--search`, same night)
  - **his try 2026-10-28:** Music Player → Find more… opened nogForge searching for music players (*"NICE!!!"*) ✅
- [x] YouTube Music, Google Docs: App Library web apps, not file defaults
  - **built 2026-10-27** (`webapp-open --add youtube-music google-docs`, `--remove`; tests 4; not added on this desktop yet: Javier's call)

## Phase 2 · Release
- [ ] Javier's run → 1.0.0, GitHub, AUR after his local test; README row, kognogos.org, Vault
