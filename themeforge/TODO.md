# themeForge — the list

**Target: the Look page of hypeForge Settings, KognogOS v1.0 (April 2027); started 2026-10-11 (D-1).** Section of the Forge Suite (D-60). Issue #84. Updated after every step.

## 2026-10-11 · What it needs, measured
- [x] **What it needs** checked again by the suite audit (2026-10-11, #91): the list from this morning holds

## Phase 1 · Theme Picker (0.1.0)
- [x] Reading hypeForge's look: the seven styles (with a `summary` each, in hypeForge's `style.toml`), the 25 colour themes with a colour strip, the look in use (`state.toml`); apply and undo through `hypeforge-theme`
- [x] One page: Theme and Color drop-downs, what's in use now, the changes bar (Apply (F10) · Put Back), Undo Last Apply (u); the manual (1 page); `--hypeforge`
- [x] hypeForge: the **Look** page + Home card in Settings, a launcher entry (Settings group), the Forge float rule — repo + live
- [x] Tests: 14 (look 7, page 7); two deliberate breaks caught (F10 doing nothing; a style without its summary); a real apply on the desktop through the same code (Rice · Ember, the bar stayed up) and put back to Rice · KognogOS Mocha
- [x] **Javier's first run (10-11):** "only rice and macos works … colors, only mocha and 'red'. Classic, it's a disaster" → hypeForge F-67 (undo left another layout under the new stylesheet) and F-68 (light themes unreadable) fixed; **the look file** (D-4, hypeForge D-90) and `[elements]`; **the page as a two-column matrix, small buttons** (D-5); a log of every run; `scripts/look-bench.py` 113/113 (27/29 with the old undo); the real app driven by its keys on the desktop (KDE·Blue, F10, then u: back to Rice·Mocha); tests 17
- [ ] **NEXT — Javier's second run**

## Phase 2 · More layers (Javier: "popups, icons, fonts, and other")
- [ ] Corners: straight · rounded · the style's own (`hypeforge-theme corners`, D-81), and the bar's separately from the windows' (idea, 10-10)
- [x] **Wallpaper page (D-6, 10-11):** source (theme's own · KognogOS Tier Aware / Arch Distro · my pictures · solid), fit (fill · fit · stretch · center · tile), folder + Make Folder (n), picture, half-block preview; hypeForge D-93 makes the pictures. **D-7: the preview at full quality** over the terminal (overlay.py, our own, Javier's pick; overlay-bench 13/13). Javier's run (10-11 night): folders should be browsable, every picture visible → D-8
- [x] **The Wallpaper page redesigned (D-8, Javier 2026-10-11 night; built 2026-10-13):** Source = the folder in use + **Browse (b)** (a pop-up: Enter into a folder, Backspace up, a typed path, jumps to Home · Pictures · the KognogOS wallpapers, **Use This Folder (u)**) · **Images** = every picture in it, Enter picks → the preview below (✓ on screen, ● picked) · **Fit Style** in plain names, each explained · **Apply Background (F10)** on the page. **D-9** settles the open points: the theme's own, the KognogOS backgrounds and the solid colour are the first place in Browse, "The theme's pictures"; the changes bar is the Theme Picker's. Tests 42 (two deliberate breaks caught), overlay bench 15/15 (the Browse pop-up and the Fit Style list both hide the sharp preview)
- [x] **Javier's first run (10-13):** Browse "not intuitive" → **D-10, a small file manager**: folders as a tree (The theme's pictures · Home open by default · KognogOS wallpapers · the folder in use's parent when elsewhere), the pictures of the folder under the cursor on the right, Enter on one picks it; **F-71** the Images list came up empty after an apply → the page updates in place (test seen failing on the old code). Fit Style "works perfect!". Tests 44, overlay bench 15/15
- [x] **His second run (10-13, inside Settings, "98% ready"):** the first picture of an opened folder shows by itself; the preview was blurry inside Settings → **D-11**: Settings hands its terminal's cells down (hypeForge D-97), themeForge offsets the sharp preview by the pane's place and hides it on other pages. Tests 47
- [ ] **NEXT — Javier's third run** (#96): from a freshly started Settings, the sharp preview on the Look page; Browse; the first picture
- [ ] Pop-ups, icons, fonts — each its own page
- [ ] The quick-switch tray icon (D-78)

## Phase 3 · Release
- [x] **What the package needs** written down: `docs/PACKAGING.md`, kept honest by `tests/test_needs.py` (seen failing with Pillow left out)
- [ ] Release notes, GitHub Release `themeforge-v1.0.0` (`depends=()` from docs/PACKAGING.md); the AUR only when the full themeForge is done and after Javier's local test (Javier, 2026-10-11)
