# displayForge — the list

**Target: no date set — started 5 Oct 2026.** A Forge Suite app (terminal, forgekit) for screen settings on Sway: arrange, resolution, refresh rate, scale, rotation, on / off, main screen, brightness. Section of the Forge Suite (D-60). Updated after every step.

## Phase 0 · Research and design
- [x] Name: **displayForge** (Javier, 2026-10-05)
- [x] Research: `docs/research/2026-10-05-displayforge.md` — Sway's per-screen settings, brightness via ddcutil without a password, **identical screens can't be told apart by software → an Identify step**, keep-or-revert countdown
- [x] Screen designs (100-column terminal drawings, the alacrittyForge / grubForge pattern) → **approved by Javier** (D-2: "Wow!!!! I love what you have done! Let's go!" — with any arrangement, sizes 80/90 %, brightness in tens, HDR only where supported, screen names) — drawn 2026-10-05: `docs/design/v0.1.0-screens.html` (published privately: https://claude.ai/artifact/NX3YSPKvbcgL7dayRnLoHg), seven screens (Screens, Settings, Keep or go back, Arrange, Brightness, Identify, Save) + seven questions for Javier.

## Phase 1 · Build (after the design is approved)
- [x] **Engine step 1 — `displayforge/screens.py`** (2026-10-05): read screens from Sway; only real sizes / rates; exact `output …` commands for a change (HDR / adaptive sync only where supported); the saved-file lines; place left / right / above / below with edges snapped and **the others make room**; overlaps found. **20 tests** (`tests/test_screens.py`: Javier's real three Sceptres, serial blanked; 1, 4, 6 screens; a fourth under screen 1; rotated; 80 %)
- [ ] Engine step 2 — trial (apply live, undo by itself), saving (outputs file + backup), brightness (ddcutil in tens) + names / which-screen-is-which
- [ ] forgekit app skeleton
- [ ] Screens drawing + list; per-screen settings form
- [ ] Apply live with keep-or-revert countdown; save to `~/.config/sway/outputs` with a backup
- [ ] Identify + brightness (ddcutil, 10–100 % in tens) + screen names
- [ ] Sizes 80 / 90 % proven in the test VM first (Sway's manual: X11 apps blur at fractional sizes)
- [ ] HDR switch only where Sway reports the screen supports it
- [ ] Tests (1, 2, 3 screens in a VM; 100 columns; text console)

## Later
- [ ] Profiles (switch layouts when screens are plugged in / out)
- [ ] A page in hypeForge Settings
