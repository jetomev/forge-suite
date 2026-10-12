# themeForge — the list

**Target: the Look page of hypeForge Settings, KognogOS v1.0 (April 2027); started 2026-10-11 (D-1).** Section of the Forge Suite (D-60). Issue #84. Updated after every step.

## Phase 1 · Theme Picker (0.1.0)
- [x] Reading hypeForge's look: the seven styles (with a `summary` each, in hypeForge's `style.toml`), the 25 colour themes with a colour strip, the look in use (`state.toml`); apply and undo through `hypeforge-theme`
- [x] One page: Theme and Color drop-downs, what's in use now, the changes bar (Apply (F10) · Put Back), Undo Last Apply (u); the manual (1 page); `--hypeforge`
- [x] hypeForge: the **Look** page + Home card in Settings, a launcher entry (Settings group), the Forge float rule — repo + live
- [x] Tests: 14 (look 7, page 7); two deliberate breaks caught (F10 doing nothing; a style without its summary); a real apply on the desktop through the same code (Rice · Ember, the bar stayed up) and put back to Rice · KognogOS Mocha
- [x] **Javier's first run (10-11):** "only rice and macos works … colors, only mocha and 'red'. Classic, it's a disaster" → hypeForge F-67 (undo left another layout under the new stylesheet) and F-68 (light themes unreadable) fixed; **the look file** (D-4, hypeForge D-90) and `[elements]`; **the page as a two-column matrix, small buttons** (D-5); a log of every run; `scripts/look-bench.py` 113/113 (27/29 with the old undo); the real app driven by its keys on the desktop (KDE·Blue, F10, then u: back to Rice·Mocha); tests 17
- [ ] **NEXT — Javier's second run**

## Phase 2 · More layers (Javier: "popups, icons, fonts, and other")
- [ ] Corners: straight · rounded · the style's own (`hypeforge-theme corners`, D-81), and the bar's separately from the windows' (idea, 10-10)
- [x] **Wallpaper page (D-6, 10-11):** source (theme's own · KognogOS Tier Aware / Arch Distro · my pictures · solid), fit (fill · fit · stretch · center · tile), folder + Make Folder (n), picture, half-block preview; hypeForge D-93 makes the pictures. **D-7: the preview at full quality** over the terminal (overlay.py, our own, Javier's pick; overlay-bench 13/13). ⬜ Javier's run
- [ ] Pop-ups, icons, fonts — each its own page
- [ ] The quick-switch tray icon (D-78)

## Phase 3 · Release
- [x] **What the package needs** written down: `docs/PACKAGING.md`, kept honest by `tests/test_needs.py` (seen failing with Pillow left out)
- [ ] Release notes, GitHub Release `themeforge-v1.0.0` (`depends=()` from docs/PACKAGING.md); the AUR only when the full themeForge is done and after Javier's local test (Javier, 2026-10-11)
