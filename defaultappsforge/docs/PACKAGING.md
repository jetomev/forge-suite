# defaultappsForge — what the package needs

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
| python-rich | tables and text | rich |
| python-forgekit (>= 0.10.0) | the Forge look | forgekit |
| nog | installing a missing app from the lists | (program nog) |

## Optional (`optdepends`)

| Package | What uses it | Module / program |
|---|---|---|
| xdg-utils | reading and setting the defaults (xdg-mime); the default browser for web apps (xdg-settings) | (program xdg-mime) |
| xdg-terminal-exec | the default terminal entry, where installed (not on this desktop) | (program xdg-terminal-exec) |

## Check only (`checkdepends`)

| Package | What uses it | Module / program |
|---|---|---|
| desktop-file-utils | `check()` validates the launcher entry `defaultappsforge.desktop` (1.0.0) | (program desktop-file-validate) |

## The AUR recipe

`defaultappsforge` from 1.0.0 (2026-10-28), in `~/Programs/aur-defaultappsforge/`: the source is the signed
release file from `jetomev/forge-suite` (tag `defaultappsforge-vX.Y.Z`, built by `scripts/release-app.sh`).
It installs `defaultappsforge/` and `main.py` under `/usr/lib/defaultappsforge/`, the `defaultappsforge`
launcher and a `webapp-open` link in `/usr/bin` (the App Library's web apps and the launchers a save
writes), the launcher entry, the README and the license. `check()` runs the tests and validates the
launcher entry.
