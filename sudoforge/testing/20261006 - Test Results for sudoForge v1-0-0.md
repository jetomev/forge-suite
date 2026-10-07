# sudoForge v1.0.0 — Test Results (6 Oct 2026)

Every row of the matrix (`20261006 - Test Matrix for sudoForge v1-0-0.md`), on the test desktop (Arch, Sway 1.12, hypeForge, three screens), Javier at the screen.

| Area | Result |
|---|---|
| Automated | **36 PASS**, 0 warnings (stand-in sudo and box; the real box headless; `sudo.conf` on throwaway files). The real-box tests fail 5/5 with F-1 put back |
| Live polkit check | PASS 21:2x with no service running (a real `pkexec` from another program reached the box, cancelled, exit 126). With the real service running it skips: polkit allows one agent per session — which also shows a second sudoForge cannot take over |
| sudo -A | right password ✅ · only `/etc/sudo.conf` set ✅ · two wrong then right (try 2, try 3) ✅ · Esc → "no password was provided" ✅ · two at once: one box, then the next, both exit 0 ✅ · plain `sudo` in a terminal asks in the terminal ✅ (Javier) |
| polkit | `sudoforge setup` in the box ✅ · Print Settings unlock ✅ and Esc (cancelled) ✅ · undo/setup twice, file byte for byte the original plus our two lines ✅ |
| Session | full reboot: the service started by itself 39 s after boot ✅ · the box centred and focused on the screen in use ✅ |
| Found | **F-1 (#36)**: the box crashed on start (forgekit colours not loaded); fixed before any other test |
| Dropped | 2.5 nog from the launcher: nog has no launcher entry; same `sudo -A` path as above. USB mounting asks no password on this system (allowed for the person at the keyboard), so it is not a test |
| Not run | a text console in the KognogOS VM (sudoForge says "no box here" and sudo stops — tested only automatically) |

Javier: *"tested, rebooted, logged back in, tested. All work perfect!"*
