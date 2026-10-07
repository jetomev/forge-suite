# sudoForge v1.0.0 — Test Matrix

*Javier's runs on the test desktop (Sway, hypeForge), plus Claude's automated checks. Each row: what to do, what you should see. Results go in the Test Results file of the same date.*

## 1 · Automated (Claude)

| # | Check | Expected |
|---|---|---|
| 1.1 | `python -m unittest discover -s tests -t .` | 36 pass, 0 warnings |
| 1.2 | Live polkit check: `SUDOFORGE_LIVE_POLKIT=1 python -m unittest tests.test_service.LivePolkit` | a real `pkexec` from another program reaches the box; cancelled; exit 126; nothing ran |
| 1.3 | The real-box tests with the F-1 bug put back | all 5 fail (the guard works) |
| 1.4 | `makepkg` from the release tarball | sha256 + signature pass; `check()` runs the tests |

## 2 · sudo (Javier at the screen, Claude runs the command)

| # | Do | Expected | Done |
|---|---|---|---|
| 2.1 | `sudo -A -k true`, type the right password | box: "Claude wants to run as admin", `true` in orange; sudo exits 0 | ✅ 2026-10-06 21:27 |
| 2.2 | Same, with only `/etc/sudo.conf` set (no override) | the same box; exit 0 | ✅ 21:29 |
| 2.3 | Same, two wrong passwords first | yellow "didn't work", "try 2 of 3", "try 3 of 3"; the right one → exit 0 | ✅ 21:30 |
| 2.4 | Same, press Esc | box closes; sudo: "no password was provided"; nothing runs | ✅ 21:48:36 (an earlier try at 21:47 came back "answered", exit 0 — taken as the password typed; Javier to confirm) |
| 2.5 | nog **from the launcher** (no terminal), something small to install | box: "nog wants to run as admin" + the pacman command | |
| 2.6 | `sudo true` typed in a terminal (no -A) | asks **in the terminal**, no box (D-4) | |

## 3 · The admin pop-up (polkit)

| # | Do | Expected | Done |
|---|---|---|---|
| 3.1 | `sudoforge setup` | box: "sudoForge wants to run as admin"; `/etc/sudo.conf` gets the two lines; backup saved | ✅ 21:29 |
| 3.2 | **Print Settings** → change something small (e.g. the default printer) | box: "Printers wants admin rights", the system's sentence, "Asked by system-config-printer" | ✅ 21:46 (Unlock; `cupspkhelper.mechanism.all-edit`; Javier: "password success!!!") |
| 3.3 | Same, press Esc | the change is not made; Print Settings says so | |
| 3.4 | `sudoforge undo`, then `sudoforge setup` again | the two lines go, then come back; nothing else in the file changes | |

## 4 · The session

| # | Do | Expected | Done |
|---|---|---|---|
| 4.1 | Log out of Sway and back in | `sudoforge status`: "running in this session"; the record shows it started | |
| 4.2 | The box opens on the screen you are using (try with the mouse on each screen) | centred on that screen, typing goes straight in | |
| 4.3 | Two requests at once (Claude starts two `sudo -A` together) | one box, then the next; both work | ✅ 21:49 (both asked 21:49:20, answered :27 and :34, both exit 0; at most 1 box on screen, counted every second) |
