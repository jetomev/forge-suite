# grubForge — what the package needs

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
| python-forgekit (>= 0.10.0) | the Forge look and the in-app password box | forgekit |
| python-gobject | forgekit's in-app polkit agent, which grubForge uses | (through forgekit) |
| polkit | saving and rebuilding need pkexec | (program pkexec) |
| grub | the boot menu it manages: grub-mkconfig, grub-script-check | (programs grub-mkconfig, grub-script-check) |

## Optional (`optdepends`)

| Package | What uses it | Module / program |
|---|---|---|
| os-prober | other systems on the boot menu | (program os-prober) |

## At build time only (`checkdepends`)

| Package | What uses it | Module / program |
|---|---|---|
| desktop-file-utils | `check()` validates the launcher entry `grubforge.desktop` (next release, #37) | (program desktop-file-validate) |

## The AUR recipe

Fixed in the AUR's **2.2.1-1**: `depends` carries **grub** (a GRUB manager without GRUB only shows its sample menu) and `optdepends` **os-prober** (checked against the AUR 2026-10-22). Was missing from 2.2.0-1.
