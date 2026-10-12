# forgekit (python-forgekit) — what the package needs

*Measured from the code on 2026-10-11 (Javier: "check all Forge Suite apps for all dependencies needed to build and
run them"), with the Forge Suite's audit, `forge-suite/scripts/needs-audit.py`, and proven by building the
AUR recipe in a clean Arch system (devtools' `makechrootpkg`, tests included). `tests/test_needs.py` reads every import and fails when one isn't listed here, so this page can't fall behind the code.
Arch's `base` packages (bash, coreutils, glibc, sed, grep, util-linux, systemd…) are on every Arch install and
aren't listed.*

## Needs (the recipe's `depends`)

| Package | What uses it | Module / program |
|---|---|---|
| python | everything | — |
| python-textual | the app frame, every screen | textual |
| python-rich | text, tables, colours | rich |
| python-pyte | TerminalPane: a terminal inside the app (nog's runs) | pyte |

## Optional (`optdepends`)

| Package | What uses it | Module / program |
|---|---|---|
| python-gobject | InAppPolkitAgent: the password box for pkexec inside the app (loaded only when used) | gi |
| polkit | the same agent (GI Polkit 1.0, PolkitAgent 1.0) | gi: Polkit, PolkitAgent |

## The AUR recipe

Matches the AUR recipe 0.10.0-1. Nothing to change.
