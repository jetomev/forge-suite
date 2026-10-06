# forgekit v0.5.0: Test Results (2026-10-02)

**Tests: 48, all passing** (v0.4.1: 23). **Warnings: 0** (`python -W default -m unittest discover -s tests`).

0.5.0 adds the pieces for settings forms and save flows (see the README, "Forms and flows").
They were not designed in the abstract: each one was built for grubForge 2.0 and changed
while grubForge used it for real. So most of the testing of 0.5.0 is grubForge 2.0's
testing (`grubforge/testing/20261002 - Test Matrix for grubForge v2-0-0.md`).

| Check | Result | Notes |
|---|---|---|
| Unit + headless tests (`tests/test_v05.py` and the 0.4 tests) | **PASS** | 48 |
| `examples/gallery.py`, every piece on one screen, window and console mode | **PASS** | README picture 05 |
| Console preview (`tools/console-preview.py`) of grubForge 2.0, every screen, 100×30 and 128×48 | **PASS** | only console-font characters; nothing drawn in its own background |
| Fits at 100 columns | **PASS** after fixes | found 10-02 through grubForge: the "● changed" mark (cut at 120, gone at 100; moved to the line under the setting), notices wrapping to the edge (heading and body now separate blocks), presets twice as wide as needed. `dcafa19` |
| Used for real by grubForge 2.0 on Debian 13, Ubuntu 24.04, Fedora 44, openSUSE Tumbleweed (VMs) | **PASS** | |
| Javier's own run of grubForge 2.0 on the KognogOS VM, installed as packages (python-forgekit 0.5.0rc1) | **PASS** | "it works wonders" |
| AUR `check()`: headless mount, window and console mode | **PASS** | in the rc build |

The four 0.4 README pictures changed in 0.5.0 on purpose: fields now have a plain single
border. Checked by eye, not by an identical-file comparison as in 0.4.0.
