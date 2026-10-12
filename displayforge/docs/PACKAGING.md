# displayForge — what the package needs

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
| python-rich | the screen drawing and text | rich |
| python-forgekit (>= 0.10.0) | the Forge look and start check | forgekit |
| sway | it sets up screens by talking to Sway (swaymsg) | (program swaymsg) |

## Optional (`optdepends`)

| Package | What uses it | Module / program |
|---|---|---|
| ddcutil | Brightness and Identify talk to the screens through it | (program ddcutil) |

## The AUR recipe

AUR 1.1.0-1 lacks **python-rich** (imported directly; only arrived through Textual).

## Found by the audit

- **The AUR build of 1.1.0 fails on any machine without ddcutil** (found 2026-10-11 in a clean build): a start-up test expected the one-need message, but with the optional ddcutil missing the app names two. Fixed in the test (ddcutil pinned for that test; a second test covers both missing). Ships as 1.1.1 (F-7, #92), with the one-screen crash fix (F-6, #58).
