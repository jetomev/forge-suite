# Test Matrix — nogForge v1.6.0 (open already searching)

*Written 2026-10-28. §1 is Claude's; §2 is Javier's try through defaultappsForge's Find more… (done the same day); §3 is Javier's install of the locally built package, the last step before the AUR.*

## §1 · Claude — tests and checks

| # | Check | Expected | Result | Notes |
|---|---|---|---|---|
| 1.1 | `python -W always -m unittest discover -s tests` | green, no warnings | **PASS** | 70 (67 at 1.5.0), 0 warnings |
| 1.2 | `nogforge --help` | lists `--search WORDS`; says **1-7** and **nog 2.0.0** | **PASS** | F-20: it said 1-6 and nog 1.7.0; the old test pinned "1-6" and now checks "1-7" |
| 1.3 | `man --warnings -l nogforge.1` | no warnings; `--search WORDS` in SYNOPSIS and OPTIONS | **PASS** | |
| 1.4 | `desktop-file-validate nogforge.desktop` | clean | **PASS** | |

## §2 · Javier, this desktop (2026-10-28)

| # | Step | Expected | Result | Notes |
|---|---|---|---|---|
| 2.1 | Settings → Default apps → Music Player → **Find more…** | nogForge opens on Install, already searching for "music player" | **PASS** | "it opened searching for music players..... NICE!!!" |

## §3 · Javier — the locally built package (before the AUR)

| # | Step | Expected | Result | Notes |
|---|---|---|---|---|
| 3.1 | `nog install ./nogforge-1.6.0-1-any.pkg.tar.zst` | installs; `nogforge --version` says 1.6.0 | | |
| 3.2 | `nogforge --search "music player"` | opens on Install with the results showing; q quits | | |
