# Test Matrix — defaultappsForge v1.0.0 (every job's choices, D-5)

*Written 2026-10-28. §1 is Claude's; §2 is Javier's run in hypeForge Settings → Default apps on this desktop (done the same day, one step at a time); §3 is Javier's install of the locally built package, the last step before the AUR.*

## §1 · Claude — tests and checks

| # | Check | Expected | Result | Notes |
|---|---|---|---|---|
| 1.1 | `python -W always -m unittest discover -s tests` | green, no warnings | **PASS** | 47 (44 after D-5, 19 at 0.1.0; 3 new for the command line, seen failing on the old code), 0 warnings |
| 1.2 | `defaultappsforge --help` / `--version` / `--nope` | usage and exit 0 / `defaultappsForge 1.0.0` / refused, exit 2 — the app never opens | **PASS** | before 1.0.0, `--help` opened the whole app (found preparing the release) |
| 1.3 | `desktop-file-validate defaultappsforge.desktop` | clean | **PASS** | |
| 1.4 | README screenshots from the running app (`scripts/make-screenshots.py`, a copy of the settings file) | the three pages at 1.0.0, Gmail and Google Calendar showing | **PASS** | `docs/images/` |
| 1.5 | The AUR recipe in a clean Arch chroot (the KognogOS VM, `makechrootpkg -c`, forgekit 0.10.0 + nog 2.1.0 built first) | the published file's checksum and signature pass; `check()` green | **PASS** | 47 tests OK, 14 s, 2026-10-28 23:25 UTC; snapshot `before-clean-build-20261028` |

## §2 · Javier, this desktop — Settings → Default apps (2026-10-28)

| # | Step | Expected | Result | Notes |
|---|---|---|---|---|
| 2.1 | Email Client → Gmail, Calendar → Google Calendar, save | both saved; email links and invites open them | **PASS** | his own picks, 17:57 (`mimeapps.list`) |
| 2.2 | On the bar, the calendar pop-up → click a day | Google Calendar opens on that day | **PASS** | "yes it opened on the 30th" |
| 2.3 | Music Player → **Find more…** | nogForge opens already searching for music players; the setting unchanged | **PASS** | "it opened searching for music players..... NICE!!!" |
| 2.4 | Music Player → **Any app…** → type `spo` → Esc | every app listed, the list shrinks as he types, Esc changes nothing | **PASS** | "the list showed and shrank when I typed" |

## §3 · Javier — the locally built package (before the AUR)

| # | Step | Expected | Result | Notes |
|---|---|---|---|---|
| 3.1 | `nog install ./defaultappsforge-1.0.0-1-any.pkg.tar.zst` | installs; `defaultappsforge --version` says 1.0.0 | **PASS** | 20:00: nog → pacman, exit 0, logged; `pacman -Q` defaultappsforge 1.0.0-1; `/usr/bin/webapp-open` → the package's copy |
| 3.2 | `defaultappsforge` in a terminal | the app opens on Default Apps with his choices; Q quits | **PASS** | the installed 1.0.0 opened with his fourteen: Gmail, Google Calendar, Google Maps, Chrome, Pinta, cliamp, VLC, Fresh, Thunar, Alacritty, Ark, ONLYOFFICE |
