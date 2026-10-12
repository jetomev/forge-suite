# sudoForge — what the package needs

*Measured from the code on 2026-10-11 (Javier: "check all Forge Suite apps for all dependencies needed to build and
run them"), with the Forge Suite's audit, `forge-suite/scripts/needs-audit.py`, and proven by building the
AUR recipe in a clean Arch system (devtools' `makechrootpkg`, tests included). `tests/test_needs.py` reads every import and fails when one isn't listed here, so this page can't fall behind the code.
Arch's `base` packages (bash, coreutils, glibc, sed, grep, util-linux, systemd…) are on every Arch install and
aren't listed.*

## Needs (the recipe's `depends`)

| Package | What uses it | Module / program |
|---|---|---|
| python | everything | — |
| python-textual | the password box | textual |
| python-forgekit (>= 0.8.0) | the Forge look | forgekit |
| python-gobject | the polkit agent | gi |
| polkit | it answers polkit's password requests (pkexec, the agent) | gi: Polkit, PolkitAgent; (program pkexec) |
| sudo | it answers sudo's password requests (sudo -A) | (sudo calls it) |
| alacritty | the password box opens in it | (program alacritty) |

## Optional (`optdepends`)

| Package | What uses it | Module / program |
|---|---|---|
| sway | the desktop it's made for (floats the box) | — |

## The AUR recipe

Matches the AUR recipe 1.0.1-1. Nothing to change.
