# forgekit v0.7.0 — Test Results (6 Oct 2026)

The release is one feature, the shared start-up check (forge-suite #33), so the matrix is the
feature's own: every kind of need fed a known-bad input as well as a good one, the screen checked
by position, the first user (displayForge 1.0.1, #32) run for real, and every shipped app's own
suite run on this forgekit.

| Area | Result |
|---|---|
| Unit + headless tests | **93 PASS** (67 → 93, 0 warnings): `program` missing / too old / version unreadable / installed; `sway_session` on a fake KDE ("KDE Plasma (Wayland)"), a text console, a socket that answers, one that doesn't, a Sway desktop without its socket; `service` active / inactive, the `--user` flag reaching systemctl; `a_file` there / not; a check that raises counts as not met; headings for one, two and only-optional needs; the four lines in order; the terminal record; `start_check` asks nothing when all is met, closes on a required need even when "continue" is answered, continues only for optional ones; the screen shows the four facts, Close starts focused, c / Escape close, a does nothing for a required need, Continue Anyway appears only for optional ones and sits left of Close, the footer sits under the body |
| Console preview (`tools/console-preview.py`) | `examples/needs.py`: every character in the console font, every letter visible against its background — PASS |
| First user, for real | displayForge 1.0.1 on this desktop (Sway): both needs met, the app opens; its own suite 50 → 54 PASS (fake KDE, a dead Sway socket, a live one, `main()` closing without starting the app) |
| Apps on 0.7.0 | alacrittyForge 80, bitlaForge 64, grubForge 53, nogForge 37: PASS |
| Javier, desktop | `examples/needs.py` at 17:57: the screen, Close (c), the terminal record, "the app did not start" — **PASS** |
| Found on the way | A Sway desktop started without `SWAYSOCK` would have been reported as "Sway (Wayland)" under "Needs a Sway session"; now "a Sway desktop, but no way to reach it (SWAYSOCK isn't set)" (`9e65369`) |
| Not run | A real text console (tty) on the VM; the KDE login on Javier's desktop (expect the screen from the launcher). Both belong to displayForge 1.0.1's release check |
