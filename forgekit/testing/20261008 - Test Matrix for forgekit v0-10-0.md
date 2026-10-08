# forgekit v0.10.0 — Test Matrix

*Keys for every menu entry, one dropdown at a time, a dialog keeps its keys, `--hypeforge`, the pane for hypeForge Settings ([#49](https://github.com/jetomev/forge-suite/issues/49), [#45](https://github.com/jetomev/forge-suite/issues/45), [#47](https://github.com/jetomev/forge-suite/issues/47), [#48](https://github.com/jetomev/forge-suite/issues/48)). forgekit has no screen of its own: Javier's part runs through the six apps' 1.1.0 / 1.4.0 / 2.2.0 matrices and hypeForge Settings.*

## 1 · Automated (Claude)

| # | Check | Expected | Result |
|---|---|---|---|
| 1.1 | `python -W always -m unittest discover -s tests` | 137 pass, 0 warnings | ✅ 2026-10-08 |
| 1.2 | Each new piece switched off once (menu keys, the Q / Ctrl+Q guard, the SIGUSR1 listener, the hint count, the dropdown toggle, the click switch, the dialog guard) | its tests fail | ✅ 2026-10-08 |
| 1.3 | The six apps' suites on this forgekit | all pass | ✅ displayForge 63 · nogForge 52 · grubForge 75 (+25 script checks; 3 old library notices, unchanged) · bitlaForge 81 · alacrittyForge 103 · hypeForge 8 |
| 1.4 | `makepkg` from the release tarball | sha256 + signature pass; `check()` runs the tests | at release |

## 2 · Javier, inside hypeForge Settings and in each app's own window

| # | Do | Expected | Result |
|---|---|---|---|
| 2.1 | In any app: Ctrl + each underlined letter | goes to that entry (a menu opens its dropdown) | |
| 2.2 | 1 … N | the same, in bar order; Help has the last number | |
| 2.3 | Ctrl+H twice, and Help's number twice | Help opens, then closes (never two); its title lit while open | |
| 2.3b | The letters | the first letter of each name, else the next free one (alacrittyForge: Ctrl+S Settings, Ctrl+R Shortcuts, Ctrl+B Backups) | |
| 2.3c | Help → About, License, Keys, Manual | a page in the work area, not a window; Help lit; Esc goes back | |
| 2.4 | Open a dialog with a text field (grubForge Rename), press Ctrl+E | the cursor goes to the end; the page behind does not change | |
| 2.5 | Inside Settings: Q, Ctrl+Q in an app | nothing; no Quit in its bar | |
| 2.6 | Settings' Quit with an unsaved change in one app | Settings shows that app, which asks its question; Settings closes after the answer | |
| 2.7 | Tab and Enter in a form | still move and choose | |
