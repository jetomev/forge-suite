# forgekit v0.5.1: Test Results (2026-10-02)

**Tests: 51, all passing** (v0.5.0: 48). **Warnings: 0** (`python -W default -m unittest discover -s tests`).

A small release for alacrittyForge 1.0, which found both changes while being built:

| Change | Test | Checked in the failing direction |
|---|---|---|
| `NumberPresets(decimals=True)`: accepts 11.25, shows 12.0 as 12 (Alacritty's font size) | `NumberDecimals` (2) | whole-number fields still refuse decimals |
| The number field is as wide as its longest preset, value or limit, plus the cursor (never under 9): a fixed 9 left 3 digits, so "150" filled it and "100000" was cut | `NumberWidth` | yes: fails on 0.5.0's code, with forgekit's real styles |
| The example app's name is bitlaForge (the house name) | — | README pictures regenerated |

Also checked: grubForge 2.0's 53 tests pass against 0.5.1; alacrittyForge 1.0's 80 tests pass on it; built as 0.5.1rc1 with the AUR recipe and installed with nog in the KognogOS VM for Javier's alacrittyForge run ("a beautiful piece of software").
