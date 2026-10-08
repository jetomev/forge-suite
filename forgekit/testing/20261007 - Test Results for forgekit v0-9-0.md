# forgekit v0.9.0 — Test Results (7 Oct 2026)

Matrix: `20261007 - Test Matrix for forgekit v0-9-0.md`.

| Area | Result |
|---|---|
| 1.1 suite | **110 PASS** (104 + 6 new), run with deprecation warnings as errors: 0 warnings |
| 1.2–1.5 | PASS — `tests/test_menubar.py`: row arithmetic (1 row at 100, 2+ at 40, in order, no overflow; a too-wide title alone), the seven-tab app at 40 columns (every title inside the screen, 2 rows, header 3 high) and at 100 (1 row, header 2), a click on the second-row "About", the active mark kept after growing to 120 columns |
| 1.6 console preview | PASS — `20261007 - console preview 0-9-0 menu bar wrapped at 44 columns.png`: Dashboard · Log · Config · Setup · Help F1 on row one, **Quit on row two**, the page one line lower; every character in the console font, every one visible; exit 0. (A first run showed one cut-off row: it had picked the **installed** 0.8.0 through the demo's path — rerun with `PYTHONPATH=.`) |
| 1.7 makepkg | *(filled in at release)* |
| 2 · The desktop | *(Javier's run, after the AUR update)* |

Found on the way, not a bug in forgekit: `python examples/demo.py` imports the installed package when one exists, because only `examples/` is on the path. The CLAUDE.md line `PYTHONPATH=. python examples/demo.py` is the right one; keep using it.
