# sudoForge v1.0.1 — Test Results (7 Oct 2026)

Matrix: `20261007 - Test Matrix for sudoForge v1-0-1.md`.

| Area | Result |
|---|---|
| Automated | **38 PASS**, 0 warnings. With the fix removed, `test_a_second_setup_keeps_the_original_backup` fails (13 ran, 1 failure): the guard catches F-2 |
| 1.3 / 1.4 | covered by the two new tests in `tests/test_sudoconf.py` (`AsAdmin`) |
| 1.5 makepkg | *(filled in at release)* |
| 2 · The desktop | *(Javier's run, after the AUR update)* |
