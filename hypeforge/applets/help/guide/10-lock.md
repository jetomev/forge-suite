# Lock screen and idle

**What it does:** locks the screen behind your password, with a big clock over the blurred
KognogOS wallpaper.

## How to use it

- **Win + Escape** locks, or **Lock Screen** in the launcher (Win + Space).
- Type your password — a dot appears for each key — and press **Enter**. A wrong password
  shows a red message; just type it again.
- **By itself:** the screen locks after **30 minutes** untouched, and the screens turn off after
  **60** (any key or mouse move wakes them). Nothing ever puts the computer to sleep.

## Settings

The look: `~/.config/gtklock/` (style.css). The timers: the `swayidle` line in Sway's settings.
A Lock screen and an Idle page are planned for hypeForge Settings.
