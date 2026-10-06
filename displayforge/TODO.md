# displayForge — the list

**Target: no date set — started 5 Oct 2026.** A Forge Suite app (terminal, forgekit) for screen settings on Sway: arrange, resolution, refresh rate, scale, rotation, on / off, main screen, brightness. Section of the Forge Suite (D-60). Updated after every step.

## Phase 0 · Research and design
- [x] Name: **displayForge** (Javier, 2026-10-05)
- [x] Research: `docs/research/2026-10-05-displayforge.md` — Sway's per-screen settings, brightness via ddcutil without a password, **identical screens can't be told apart by software → an Identify step**, keep-or-revert countdown
- [ ] Screen designs (100-column terminal drawings, the alacrittyForge / grubForge pattern) → **approved by Javier screen by screen before any code** — drawn 2026-10-05: `docs/design/v0.1.0-screens.html` (published privately: https://claude.ai/artifact/NX3YSPKvbcgL7dayRnLoHg), seven screens (Screens, Settings, Keep or go back, Arrange, Brightness, Identify, Save) + seven questions for Javier. **Waiting: Javier's answers**

## Phase 1 · Build (after the design is approved)
- [ ] forgekit app skeleton; read screens (`swaymsg -t get_outputs`)
- [ ] Screens drawing + list; per-screen settings form
- [ ] Apply live with keep-or-revert countdown; save to `~/.config/sway/outputs` with a backup
- [ ] Identify + brightness (ddcutil)
- [ ] Tests (1, 2, 3 screens in a VM; 100 columns; text console)

## Later
- [ ] Profiles (switch layouts when screens are plugged in / out)
- [ ] A page in hypeForge Settings
