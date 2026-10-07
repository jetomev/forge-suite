# sudoForge v1.0.1 — Test Results (7 Oct 2026)

Matrix: `20261007 - Test Matrix for sudoForge v1-0-1.md`.

| Area | Result |
|---|---|
| Automated | **38 PASS**, 0 warnings. With the fix removed, `test_a_second_setup_keeps_the_original_backup` fails (13 ran, 1 failure): the guard catches F-2 |
| 1.3 / 1.4 | covered by the two new tests in `tests/test_sudoconf.py` (`AsAdmin`) |
| 1.5 makepkg | PASS 18:46 — sha256 and signature of the published release tarball pass; `check()` ran the 38 tests; `sudoforge 1.0.1-1` built |
| 2.1 install + status | ✅ 19:01 — installed through nogForge (AUR, built by yay, 38 tests in the build); `sudoforge status`: 1.0.1, service running, asks in the box |
| 2.2 undo + setup | ✅ 19:03 — after `undo` the file had no sudoForge line; `setup` took a fresh backup: **4,344 bytes, identical to the live file minus our two lines** — the backup 1.0.0 overwrote on 2026-10-06 is the original again |
| 2.3 setup again | ✅ 19:03 — "Already set up; nothing changed."; the backup's time unchanged (19:03:30) |
| 2.4 sudo -A -k true | ✅ 19:04 — the box, the right password, exit 0 |

Four password boxes, Javier at the screen. Every row passed; nothing dropped.
