# Test Results — hypeForge's own Sway build, patch 3 (Sway 1.12 + 0001, 0002, 0003), clean VM

*2026-10-20 · VM `kognog-hypeforge` (KognogOS), snapshot `before-sway-patch3` taken first · Javier: "1, patch our Sway" (D-116: pop-ups open under what was clicked).*

## Why patch 3
Measured on a hidden Sway before writing it:
- a new layer surface (the pop-up's see-through backdrop) is **not** told where the pointer is when it appears — only once the pointer moves (probe: no enter event after 1.5 s, on the TOP and the OVERLAY layer; moving the pointer afterwards gave `enter x=496 y=12` at once, so the rig worked);
- `swaymsg -t get_seats` on plain Sway has no pointer position at all (`name, capabilities, focus, devices`).

Patch 3 adds `"cursor": {"x", "y"}` (layout pixels) to every seat in `get_seats` — 12 lines in `sway/ipc-json.c`.

## Setup
- The VM's earlier build and download cache **moved aside** (`*.reset-20261020-…`), so the build starts from nothing.
- hypeForge copied in as committed (`git archive HEAD:hypeforge`, 7.6 MB, sha256 `7e6c13f0…` both sides), unpacked as the VM's normal user.

## Results
| # | Test | Result |
|---|---|---|
| 1 | `sway-hypeforge/build.py` from nothing: download, signature, the three patches, build, install | ✅ downloaded both files, signature good (Sway's release key), 0001 · 0002 · 0003 applied, `~/.local/opt/sway-hypeforge/1.12` "sway version 1.12" |
| 2 | `scripts/titlebar-bench.py --ours` on that build (hidden screen) | ✅ **29/29** — nothing in patches 1–2 broken |
| 3 | The pointer's position, three hidden screens side by side (2560 + 2560 + 1920 = 7040 px), the pointer parked at 496,12 · 3000,700 · 6900,1050 | ✅ `get_seats` answers `{x: 496, y: 12}` · `{3000, 700}` · `{6900, 1050}` — exact, the third screen of another size included |
| 4 | The same on the system's own Sway (the control) | ✅ no `cursor` — the answer the pop-ups fall back from |
| 5 | The login starter, versions match | ✅ our build, `-c` the login's copy of the button lines, no fallback flag |
| 6 | The login starter, Sway "updated" to 1.13 | ✅ the system's Sway, `HYPEFORGE_SWAY_FALLBACK=1.12:1.13` |
| 7 | The login starter, our build broken | ✅ the system's Sway, `HYPEFORGE_SWAY_FALLBACK=none:1.12` |

Tests 5–7: `sway-hypeforge/login-test.sh`. It refused at first — the VM had a Sway config of its own from earlier tests (its guard: never on a desktop). That config was moved aside for the run and put back after (sha256 `82c2481a…` before and after).

The test rig itself, found on the way: `fake-pointer.py` needs `--width/--height` of the whole layout (7040 × 1440 here); without them 496 landed at 1364 (496 × 7040 / 2560).

**All pass.** Snapshot after: `sway-patch3-tested`.

## Also on the desktop (before the VM)
build.py with the three patches installed into `~/.local/opt/sway-hypeforge/1.12` (meson removes a file before it copies, so the running session kept its own copy); `titlebar-bench.py --ours` 29/29 and the pointer test exact on the installed build; the live session untouched (it picks the new build up at the next login).
