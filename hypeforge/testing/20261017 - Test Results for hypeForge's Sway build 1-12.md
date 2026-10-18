# Test Results — hypeForge's own Sway build (Sway 1.12 + patches 0001, 0002), clean VM

*2026-10-17 · VM `kognog-hypeforge` (KognogOS, kernel 7.2.7), snapshot `before-sway-hypeforge` taken first · Javier asked: "let's do the VM test".*

## Setup (a clean system)
- No Sway, meson or ninja in the VM. Installed through **nog 2.0.0** (`nog install --yes`, repositories only): sway 1:1.12-4 (wlroots0.20 0.20.2-1, as on the desktop), meson, ninja, wayland-protocols, pkgconf, patch, gnupg, and the bench's needs (python-gobject, gtk3, gtk-layer-shell, python-cairo, python-pillow, grim, alacritty, fonts, librsvg, dbus). Clean install, no errors.
- hypeForge copied in as committed (`git archive HEAD`, 4.7 MB, sha256 checked both sides), as the VM's normal user.

## Results
| # | Test | Result |
|---|---|---|
| 1 | `sway-hypeforge/build.py` from nothing: download, signature (Sway's release key fetched by itself), both patches, build, install | ✅ `~/.local/opt/sway-hypeforge/1.12`, "sway version 1.12" |
| 2 | `scripts/titlebar-bench.py --ours` on that build (hidden screen) | ✅ **29/29** — title bars, the menu, every style switched, hover colours (real pixels), □ and back, ─, ✕, dragging |
| 3 | The login starter, versions match | ✅ our build, `-c` the login's own copy of the button lines, no fallback flag |
| 4 | The login starter, Sway "updated" to 1.13 (a stand-in `sway --version`) | ✅ the system's Sway, `HYPEFORGE_SWAY_FALLBACK=1.12:1.13` |
| 5 | The login starter, our build broken (its link pointing nowhere) | ✅ the system's Sway, `HYPEFORGE_SWAY_FALLBACK=none:1.12` |

Tests 3–5: `sway-hypeforge/login-test.sh` (run as the VM's user). **All pass.** Snapshot after: `sway-hypeforge-tested`.
