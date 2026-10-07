# sudoForge v1.0.1 — Test Matrix

*One fix, F-2 ([#37](https://github.com/jetomev/forge-suite/issues/37)): the backup of `/etc/sudo.conf` must be the file from before sudoForge touched it, and a second `sudoforge setup` must keep it. Claude's automated checks, then Javier's one live row on the test desktop (Sway, hypeForge). Results in the Test Results file of the same date.*

## 1 · Automated (Claude)

| # | Check | Expected |
|---|---|---|
| 1.1 | `python -m unittest discover -s tests -t .` | 38 pass (36 + 2 new), 0 warnings |
| 1.2 | `tests.test_sudoconf` with the F-2 fix put back | `test_a_second_setup_keeps_the_original_backup` fails (the guard works) |
| 1.3 | Throwaway files: apply with the repo's helper path, then apply with the package's path | the file names the package's helper; the backup still equals the stock file |
| 1.4 | Throwaway files: apply, undo, edit the file, apply again | the backup is the edited file (no sudoForge mark in it, so it is the new "before") |
| 1.5 | `makepkg` from the release tarball | sha256 + signature pass; `check()` runs the 38 tests |

## 2 · The desktop (Javier at the screen, Claude runs the command)

| # | Do | Expected | Done |
|---|---|---|---|
| 2.1 | Install 1.0.1 (nogForge or `nog install sudoforge`), `sudoforge status` | "asks in sudoForge's box", version 1.0.1 | ✅ 19:01 |
| 2.2 | `sudoforge undo`, then `sudoforge setup` (two boxes) | after undo the file has no sudoForge mark, so setup takes a fresh backup: `/etc/sudo.conf.sudoforge-backup` is now byte for byte sudo's shipped file (4,344 bytes) — this repairs the backup 1.0.0 overwrote on this desktop | ✅ 19:03 |
| 2.3 | `sudoforge setup` once more | "Already set up; nothing changed." — the backup untouched | ✅ 19:03 |
| 2.4 | `sudo -A -k true` | the box as before; exit 0 (nothing else changed) | ✅ 19:04 |
