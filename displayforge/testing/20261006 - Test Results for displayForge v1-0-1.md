# displayForge v1.0.1 — Test Results (6 Oct 2026, evening)

One job in this release (forge-suite #32): Sway only, said everywhere and checked at launch, on forgekit 0.7.0's shared start-up check (#33). The matrix is that job's.

| Area | Result |
|---|---|
| Unit + headless tests | **54 PASS** (50 → 54, 0 warnings): `needs()` = a Sway session (required) + ddcutil (optional); a fake KDE session reports "KDE Plasma (Wayland)"; a Sway socket that doesn't answer; a live one; `main()` returns 2 and never builds the app when the check says no, with the record in the terminal |
| For real, on the desktop (Sway) | both needs met, the app opens (console preview: every character in the console font, every letter visible) — PASS |
| Javier, the check screen | forgekit's `examples/needs.py` at 17:57 (a fake "KDE Plasma (Wayland)"): the screen, Close (c), the terminal record, "the app did not start" — **PASS** |
| On the installed forgekit | `python-forgekit` 0.7.0-1 installed from the AUR at 18:37 (its check step ran test_v06 + test_v07); the launcher entry back on the installed library |
| "Sway only" said | README (first line + Install), manual page 1, About, launcher entry, suite README, KognogOS README, kognogos.org — checked by grep |
| Not run | The launcher from a KDE login on Javier's desktop (expect the screen, then Close); a real text console. Both stay on the 1.0.x list |
