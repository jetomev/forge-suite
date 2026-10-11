# themeForge — decisions

*Newest first. Each one says what was decided, by whom, and why.*

## 2026-10-11

### D-6 · The Wallpaper page: desktop background 1.0 (Javier, 2026-10-11)
*"Rice uses our KognogOS backgrounds only, the other themes, assign one background topic to each, and uses the color variants when they change, by default."* And for 1.0: *"All screens get the same background · Picker allows to switch a background with the user choice (from a specific folder) · Can we show in terminal a small preview of the images? … Images: centered, stretched, crop, others?"* Javier picked **Tier Aware** for the Rice. The page, the same two-column matrix: **Source** (the theme's own · KognogOS · Tier Aware · KognogOS · Arch Distro · My pictures · Solid colour) and **Fit** (Fill · Fit · Stretch · Center · Tile, Sway's own five), **Folder** (`~/Pictures/Wallpapers` by default; **Make Folder (n)** when it's missing, never made unasked) and **Picture**. Under them a **preview in half blocks** (two pixels a character), laid on a screen-shaped canvas the way Sway lays it; no extra program. The theme's own follows the Theme Picker's picks, so a combination is previewed before it's applied. The choice is written in the look file's `[wallpaper]` (picture, fit, folder) and applied by `hypeforge-theme look` (hypeForge D-93). A picture of yours stays through theme and colour changes.

### D-5 · The page: a matrix of two columns going down, compact, small buttons (Javier)
*"Page should be a matrix of 2xnumber of options going down, all drop down options to choose from. Watch spacing (real state) to make it compact with enough air between things to don't choke. Button sizes, please, not the big ones, they look awful."* The options sit two to a row (**Theme · Colors** for now), each a label and a drop-down, with the theme's line and the colour strip under them; **What this theme brings** lists the theme's elements in the same two-column way (read only until their pages come); buttons are one line, no frame.

### D-4 · themeForge writes the look file; hypeForge applies it (Javier; hypeForge D-90)
*"I believe the way to go should be to have already a config file for theme, and with the config file themeForge call to change it based on the selections on the config files for the different elements … First version theme and colors."* Apply writes the picks into `~/.config/hypeforge/look.toml` (each element's pick is kept) and runs `hypeforge-theme look`. Every run is logged (`~/.local/state/themeforge/themeforge.log`). Replaces D-2's direct `apply`.

### Found on the first run (Javier: "only rice and macos works … colors, only mocha and 'red'. Classic, it's a disaster")
Two hypeForge bugs, fixed there: **F-67** undo only reloaded the bar in place, leaving another theme's layout under the new stylesheet; **F-68** light themes unreadable on the Rice, Classic and macOS's Dock. themeForge's own bench (`scripts/look-bench.py`: a hidden desktop with three screens, 16 steps, undos included, 113 checks) now runs before he sees a change.

### D-3 · One Apply button, in the bar at the bottom (Claude, from Javier's rule)
The first screenshot had **Apply (F10)** on the page and again in the changes bar. Javier, hypeForge D-85: *"no need to have same buttons in several places."* Apply stays in the bar, which shows only once something new is picked; F10 works any time. The page keeps **Undo Last Apply (u)**.

### D-2 · hypeForge does the switching (Claude)
themeForge reads hypeForge's files and runs `hypeforge-theme apply <style> <theme>` / `undo`: every look file, the backup and the reloads stay in one place (hypeForge D-59: apps read each other's files, never each other's code). Each style now carries a one-line `summary` in its `style.toml`, shown under the Theme drop-down.

### D-1 · Start with the Theme Picker: the theme and its colours, one page (Javier)
*"themeForge is going to be a multilayer, multioptions app. But, I would like you to start with the first 2 options, which already works terminal, Picker (Theme Picker), and Color (Theme Color). The other options … will come later (popups, icons, fonts, and other). … Keep it simple. Maybe both in the same page, just pick and chose options (dropdowns), and when I come back I will see the app open and ready to test."* Built without a design review, at his word; his run is the review. Issue #84.
