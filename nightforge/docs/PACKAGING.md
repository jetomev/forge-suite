# nightForge — what the package needs

*Measured from the code on 2026-10-11 (Javier: "check all Forge Suite apps for all dependencies needed to build and
run them"), with the Forge Suite's audit, `forge-suite/scripts/needs-audit.py`, and proven by building the
AUR recipe in a clean Arch system (devtools' `makechrootpkg`, tests included). `tests/test_needs.py` reads every import and fails when one isn't listed here, so this page can't fall behind the code.
Arch's `base` packages (bash, coreutils, glibc, sed, grep, util-linux, systemd…) are on every Arch install and
aren't listed.*

## Needs (the recipe's `depends`)

| Package | What uses it | Module / program |
|---|---|---|
| python | everything | — |
| python-textual | the app's screens | textual |
| python-rich | text and the schedule drawing | rich |
| python-forgekit (>= 0.10.0) | the Forge look | forgekit |
| python-gobject | the tray icon (D-Bus) | gi |
| glib2 | the tray icon's Gio (D-Bus, watching the bar's file) | gi: Gio |
| wlsunset | the night light itself | (program wlsunset) |

## Optional (`optdepends`)

| Package | What uses it | Module / program |
|---|---|---|
| sway | the desktop it's made for; hypeForge runs `nightforge start` at login | — |
| alacritty | the tray menu's Open nightForge… | (program alacritty) |
| libnotify | a message when the night light can't start | (program notify-send) |

## For the tests the recipe runs (`checkdepends`)

| Package | Why |
|---|---|
| dbus | the tray test runs on a private session bus (dbus-run-session) |

## The AUR recipe

AUR 1.0.0-1 lacks **python-rich** and **glib2** (both used directly).

## Found by the audit

- **The AUR build of 1.0.0 fails on a machine whose clock isn't on Miami time** (found 2026-10-11: clean build machines run on UTC). A test built "8:30 in the evening" in the machine's zone for the default place, Miami; on UTC that's 4:30 p.m. in Miami, before sunset. Fixed in the test (Miami's own zone); passes on New York, UTC and Tokyo time. Ships in 1.1.0 with the tray fix (D-7).
