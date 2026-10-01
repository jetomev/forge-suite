# Test Results — forgekit v0.4.0 console mode, in the apps we already ship

*Matrix: `20261001 - Test Matrix for forgekit v0-4-0-console-apps.md`. Two independent runs, Javier's choice (2026-10-01): Claude first, on the KognogOS VM's real tty3 (keys with `virsh send-key`, every screen read from the kernel, `/dev/vcsa3` colours + `/dev/vcsu3` characters, redrawn with `tools/vcsa-shot.py`); then Javier, by hand, in the same VM.*

**VM:** `kognog-hypeforge` (KognogOS, kernel built-in console font, 160×50), snapshot `before-console-apps` taken first. Installed from the desktop's own builds (same checksums): `python-forgekit 0.4.0-1`, `bitlaforge 0.2.1-1`; `alacrittyforge 0.2.0-1` was already there. `pacman -U` through the guest agent (nobody at the VM's keyboard for nog's prompts).

**Automatic checks on every captured screen:** no letter in its own background colour, no character outside the console font.

| # | Claude (VM) | Javier (VM) | Notes |
|---|---|---|---|
| A.1 | ✅ | | `!  BitlaForge`; "minerd not detected" banner (the VM has no miner) readable |
| A.2 | ✅ | | first letters cyan, the active Dashboard's **D** visible (F-11 fix holds) |
| A.3 | ✅ | | log box frame visible on the real console |
| A.4 | ✅ | | fields black with visible frames (K-1 not reproduced), `▼` on Algorithm |
| A.5 | ⚠ B-1 | | E puts the cursor in Pool URL; **Esc leaves it there**, so later keys type into the field. Same in window mode (headless check) → bitlaForge behaviour, not console mode |
| A.6 | ✅ | | F1 opens Help even with the cursor in a field |
| A.7 | ✅ | | Shortcuts window readable |
| A.8 | ✅ | | Install & Setup readable |
| A.9 | ✅ | | License readable |
| A.10 | ✅ | | About: name pink, tagline grey, links cyan |
| A.11 | ✅ | | from a clean start: `?` opens and closes the shortcuts window |
| A.12 | ✅ | | Ctrl+H: nothing happens (arrives as Backspace, F-10), nothing harmful |
| A.13 | ✅ | | `Q` quits; process gone |
| B.1 | ✅ | | Dashboard readable |
| B.2 | ✅ | | Config table, selected row blue |
| B.3 | ✅ | | E opens the anchored drop-down beside the row; Esc closes it |
| B.4 | ✅ | | Themes list; H opens/closes the install guide (scrollbar drawn as a solid bar) |
| B.5 | ✅ | | Fonts readable |
| B.6 | ✅ | | Bindings table readable |
| B.7 | ✅ | | Shortcuts window |
| B.8 | ✅ | | License window |
| B.9 | ✅ | | About, tagline grey |
| B.10 | ✅ | | `Q` quits; process gone |
| C.1 | ✅ (earlier) | | the README screenshots regenerate identical to 0.3.0 (headless) |
| C.2 | ✅ (headless) | | installed bitlaForge with `TERM=xterm-256color`: unset → off; `FORGE_ASCII=1` → console mode on; `=0` → off |
| D.1 | | | |
| D.2 | | | |

## Findings
- **K-1 (bitlaForge Log/Config frames invisible): not reproduced on a real console.** Only the emulation shows the grey field background; the real console shows black fields with visible frames. Still worth fixing in bitlaForge (its own copy of the form colours, bitlaforge#2), since a terminal that does draw bright backgrounds would hide them.
- **B-1 (bitlaForge, not console mode): Esc does not take the cursor out of a Config field**, so the next shortcut key is typed into the field. Same in a normal terminal. Nothing is saved without `S`. → bitlaForge issue.
- **Tool lesson:** the emulation (pyte) shows bright backgrounds the real console does not. `console-preview.py` should model that too, or it reports problems a real console does not have.
