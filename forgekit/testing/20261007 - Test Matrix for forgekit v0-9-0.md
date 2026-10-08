# forgekit v0.9.0 — Test Matrix

*One change: the menu bar wraps on a narrow window ([#40](https://github.com/jetomev/forge-suite/issues/40)). Claude's automated checks first, then Javier's run on the desktop after the AUR update. Results in the Test Results file of the same date.*

## 1 · Automated (Claude)

| # | Check | Expected |
|---|---|---|
| 1.1 | `python -W error::DeprecationWarning -m unittest discover -s tests` | 110 pass (104 + 6 new), 0 warnings |
| 1.2 | Row arithmetic: the Help & Keys bar (8 entries) at 100 and at 40 columns; a title wider than the window | 1 row · 2+ rows in order, none lost, no row overflows · its own row |
| 1.3 | Seven-tab app at 40 columns, headless | every title inside the screen, titles on 2+ rows, header 3 rows high |
| 1.4 | Same app at 100 columns | one row, header 2 rows high (as before 0.9.0) |
| 1.5 | Click "About" on the second row; then grow the window to 120 columns | About activates; the bar re-flows to one row; About keeps its active mark |
| 1.6 | Console preview, the demo at 44 columns (`PYTHONPATH=.`, TERM=linux) | the bar on two rows, Quit visible; every character in the console font; exit 0 |
| 1.7 | `makepkg` from the release tarball | sha256 + signature pass; `check()` runs the 110 tests |

## 2 · The desktop (Javier at the screen)

| # | Do | Expected | Done |
|---|---|---|---|
| 2.1 | Install python-forgekit 0.9.0 (nogForge or `nog update`) | 0.9.0 installed; `python -c "import forgekit; print(forgekit.__version__)"` says 0.9.0 | |
| 2.2 | Win + F1 (Help & Keys), then drag the window narrow (under ~70 columns) | the tabs flow onto a second row; the page moves down one line; nothing cut off | |
| 2.3 | Click a tab on the second row | that page opens; the tab is highlighted | |
| 2.4 | Make the window wide again | the tabs return to one row | |
| 2.5 | Open nogForge, alacrittyForge or grubForge at a normal size | looks as before (the bar on one row) | |
