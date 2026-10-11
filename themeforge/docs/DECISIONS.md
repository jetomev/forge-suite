# themeForge — decisions

*Newest first. Each one says what was decided, by whom, and why.*

## 2026-10-11

### D-3 · One Apply button, in the bar at the bottom (Claude, from Javier's rule)
The first screenshot had **Apply (F10)** on the page and again in the changes bar. Javier, hypeForge D-85: *"no need to have same buttons in several places."* Apply stays in the bar, which shows only once something new is picked; F10 works any time. The page keeps **Undo Last Apply (u)**.

### D-2 · hypeForge does the switching (Claude)
themeForge reads hypeForge's files and runs `hypeforge-theme apply <style> <theme>` / `undo`: every look file, the backup and the reloads stay in one place (hypeForge D-59: apps read each other's files, never each other's code). Each style now carries a one-line `summary` in its `style.toml`, shown under the Theme drop-down.

### D-1 · Start with the Theme Picker: the theme and its colours, one page (Javier)
*"themeForge is going to be a multilayer, multioptions app. But, I would like you to start with the first 2 options, which already works terminal, Picker (Theme Picker), and Color (Theme Color). The other options … will come later (popups, icons, fonts, and other). … Keep it simple. Maybe both in the same page, just pick and chose options (dropdowns), and when I come back I will see the app open and ready to test."* Built without a design review, at his word; his run is the review. Issue #84.
