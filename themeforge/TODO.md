# themeForge — the list

**Target: the Look page of hypeForge Settings, KognogOS v1.0 (April 2027); started 2026-10-11 (D-1).** Section of the Forge Suite (D-60). Issue #84. Updated after every step.

## Phase 1 · Theme Picker (0.1.0)
- [x] Reading hypeForge's look: the seven styles (with a `summary` each, in hypeForge's `style.toml`), the 25 colour themes with a colour strip, the look in use (`state.toml`); apply and undo through `hypeforge-theme`
- [x] One page: Theme and Color drop-downs, what's in use now, the changes bar (Apply (F10) · Put Back), Undo Last Apply (u); the manual (1 page); `--hypeforge`
- [x] hypeForge: the **Look** page + Home card in Settings, a launcher entry (Settings group), the Forge float rule — repo + live
- [x] Tests: 14 (look 7, page 7); two deliberate breaks caught (F10 doing nothing; a style without its summary); a real apply on the desktop through the same code (Rice · Ember, the bar stayed up) and put back to Rice · KognogOS Mocha
- [ ] **NEXT — Javier's run** (2026-10-11: he comes back to it open on his screen)

## Phase 2 · More layers (Javier: "popups, icons, fonts, and other")
- [ ] Corners: straight · rounded · the style's own (`hypeforge-theme corners`, D-81), and the bar's separately from the windows' (idea, 10-10)
- [ ] Wallpaper: the theme's own or a picture of yours (`hypeforge-theme wallpaper`)
- [ ] Pop-ups, icons, fonts — each its own page
- [ ] The quick-switch tray icon (D-78)

## Phase 3 · Release
- [ ] Release notes, GitHub Release `themeforge-v1.0.0`; the AUR only when the full themeForge is done and after Javier's local test (Javier, 2026-10-11)
