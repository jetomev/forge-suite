# forgekit v0.6.0 — Test Results (4 Oct 2026)

The full matrix is nogForge's: `nogforge/testing/20261004 - Test Matrix for nogForge v1-1-0.md`
(forgekit 0.6.0 is the shared half of that work).

| Area | Result |
|---|---|
| Unit + headless tests | 67 PASS (52 → 67): real pseudo-terminal with stand-in tools (questions, menus, Ctrl+C, terminal size, alternate screen, scrollback, password asked/cancelled/wrong, steps, a failed run, 80 columns on a console) |
| Apps on 0.6.0 | alacrittyForge 80, bitlaForge 64, grubForge 53, nogForge 37: PASS |
| Polkit spike (KognogOS VM, tty3) | Listener subclass: SIGSEGV after success → not used. D-Bus agent: pkexec ran as root after the app answered → used |
| KognogOS VM, tty3, from source and installed 0.6.0rc1 | nogForge: repo install, AUR install through yay (menus, diff viewer), update with steps, cancelled password, removal; grubForge: wrong password → try again, backup as root — all PASS |
| Javier, desktop + tty3 | install-rc, update, install, cancel, grubForge's box, the text console: all PASS (*"wow! better than expected!"*, *"works wonders"*) |
| Findings | ReviewDialog keys; console "?" in the progress bar; markup ate "[N]one [A]ll"; question bar on a pager's ":" — all fixed before release |
