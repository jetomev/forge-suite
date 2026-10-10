# hypeForge — the look, piece by piece

*Every place the desktop's look is set: the file, the values in it today, and why. This is the blueprint for the **Theme manager** Forge app (D-59): each row is something it will set. Javier, 2026-10-05: "there is going to be a lot of notes about how we have changed the system. We need to document those, because they are part of the theme management app."*

**Since 2026-10-10 the look is applied by `hypeforge-theme`** (D-78, the look program's step 1): a **style** (`styles/<slug>/style.toml`: shapes and which colour role each part wears) plus a **theme** (`themes/colours/palettes.toml`: 25 colour themes, 60-30-10, D-70/D-73) fill the templates in `themes/templates/` and write `~/.config/hypeforge/theme/{sway.conf, colors.css, fuzzel-colors.ini}`, `~/.config/mako/config`, `~/.config/gtk-3.0|gtk-4.0/{gtk.css, settings.ini}`, the lock screen's blurred wallpaper, and **the terminal** (`~/.config/alacritty/themes/hypeForge-desktop.toml`, first in Alacritty's imports; alacrittyForge shows it locked; a theme picked in alacrittyForge wins — Javier 10-10: the terminals follow the theme); Sway, the bar, the lists and the lock screen *include* those files. **Everything below describes today's look = the "hypeForge Classic" style with the KognogOS Mocha theme**; the only differences from the hand-written values are Mocha's approved tiny changes (D-73 F-4: urgent and Do Not Disturb red `#ff99b5`, subtext `#bac2de`). Commands: `hypeforge-theme list | current | apply <style> <theme> [--dry-run] | wallpaper theme|<file> | undo`. Proven on the hidden bench first: `python3 scripts/theme-bench.py` (every style × theme through Sway's and fuzzel's own checks; three looks running on a screen-less Sway; wallpaper + undo). **Note:** `sway -C` exits 0 even when an *included* file has errors; read its "Error on line" output.

**Rule:** a change to the look updates this page in the same commit, like Help. Values here were read from the files on 2026-10-05, not written from memory. The files under `hypeforge/` are the source; each is copied to the path shown when it is applied.

---

## The palette

Catppuccin Mocha ([catppuccin.com](https://catppuccin.com) — thank you) until the KognogOS brand palette (Phase 12).

| Name | Colour | Where it shows |
|---|---|---|
| Bar | `#181825` | the bar's background |
| **Shade** | `#262637` | the bar's left and right areas, the open-apps area, the pop-up lists |
| Hover / inactive | `#45475a` | hovered buttons, inactive window borders, list borders, the highlighted list row, the line before the clock |
| Text | `#cdd6f4` | text everywhere; the focused window's border |
| Subtext | `#a6adc8` | quieter text (menu titles, list prompts) |
| Mauve | `#cba6f7` | the letters you typed in a list; Midnight Commander's headers |
| Blue | `#89b4fa` | the clipboard icon when something is new; folders in Midnight Commander |
| Yellow | `#f9e2af` | the bell when something is new |
| Red | `#f38ba8` | Do Not Disturb, urgent windows and notifications, errors |
| Peach | `#fab387` | marked files in Midnight Commander |

## Fonts

| Use | Font | Size |
|---|---|---|
| The bar's text | `sans-serif` → Noto Sans | 14 px |
| The bar's icons (clipboard, bell) | Symbols Nerd Font | 16 px |
| The pop-up lists | Noto Sans | 11 pt (≈ the bar's 14 px); the clipboard and notification lists 9 pt |
| Notifications | Noto Sans | 10.5 (≈ the bar's 14 px) |
| Lock screen clock / date / password box | sans-serif | 72 pt / 18 pt / 16 pt |
| Terminal (Alacritty) and terminal apps | JetBrainsMono Nerd Font | 12 |
| GTK apps (swappy, galculator…) | Noto Sans; monospace JetBrainsMono Nerd Font | 10 |

Which package brings each font: [FONTS.md](FONTS.md).

---

## Windows — `sway/config` → `~/.config/sway/config`

| Setting | Value | Why |
|---|---|---|
| Border | 2 px, no title bars (`default_border pixel 2`) | D-46: "border only + tabs works wonders" |
| Focused / unfocused border | `#cdd6f4` / `#45475a` | named once (`$hf_active`, `$hf_inactive`…) so a palette swaps in one place |
| Gaps | 10 px between windows, 0 at the edges | D-46 |
| Several windows in one space | tabs (Win + T) | D-46 |
| Wallpaper | KognogOS Semi — Catppuccin Mocha, `fill`, every screen (swaybg) | Javier, 2026-10-04 |

## The top bar — `sway/waybar/config.jsonc`, `style.css` → `~/.config/sway/waybar/`

| Part | Look | Why |
|---|---|---|
| Bar | 32 px tall, `#181825` | — |
| **Left** — KognogOS emblem · <u>W</u>orkspaces · <u>F</u>avorites | the **shade**, straight edges; menu titles in subtext, key letter underlined | "a visual distinction"; "let's keep it straight for now"; menu titles like a menu bar |
| Emblem | 17 px, drawn as the button's background from `~/.config/hypeforge/bar/launcher.png` (swap the picture to change it) | same size as the other icons; Waybar 0.15's image module stops the bar here |
| **Centre** — open apps | the **shade**; 18 px icons from candy-icons; the window in use underlined in text colour; hover grey | Javier, 2026-10-05 |
| **Right** — tray · clipboard · USB drives · Bluetooth · network · volume ┃ date and time ┃ bell · ⏻ power | the **shade**, straight edges; tray icons 16 px; USB drives (blue with a count when mounted), network, Bluetooth, volume, clipboard and bell 16 px (Symbols Nerd Font, subtext colour, red when off / muted / disconnected); a 1 px hover-grey line on each side of the clock; the ⏻ turns red on hover | "1 px at a time"; "add a separator… paint the date/time area the same colour" |
| Hover on any button | `#45475a` | — |
| Clock | `Mon 05 Oct   08:13 PM` | — |

## The pop-up lists — `sway/fuzzel/fuzzel.ini` → `~/.config/sway/fuzzel/`

The launcher, Workspaces, Favorites, the clipboard list and the notification list. They match the bar they drop from (Javier, 2026-10-05).

| Setting | Value |
|---|---|
| Font | Noto Sans 11 pt; the clipboard and notification lists 9 pt (set in their applets, Javier: "reduce them a couple points") |
| Background / text | the shade `#262637` / `#cdd6f4` |
| Border | 1 px `#45475a`, straight corners |
| Highlighted row | `#45475a`, white text; typed letters mauve |
| Spacing | 14 px sides, 10 px top and bottom, 6 px between the search line and the list |
| Icons | candy-icons |
| Where they open | launcher under the emblem (top left); Workspaces and Favorites under their titles; clipboard and notifications under the bar's right end (top right) — set in each applet |
| Stay open when the mouse moves | `exit-on-keyboard-focus-loss=no` (F-46) |

## Notifications — `sway/mako/config` → `~/.config/mako/config`

| Setting | Value |
|---|---|
| Place | top right of the screen in use, under the bar; 420 × up to 200 px; 5 at a time |
| Look | the bar's: Noto Sans 10.5 (≈ the bar's 14 px), background the shade `#262637`, text `#cdd6f4`, 1 px border `#45475a`, **straight corners**, 10 px padding, 40 px icons |
| Low / critical | quieter grey border and text / red border, stays until clicked |
| Timing | 5 seconds |

Matched to the bar on 2026-10-05 (Javier: "match the notification pop-ups to the bar too"); before: sans 12, `#1e1e2e` at 95 %, 2 px border, 10 px rounded corners.

## Lock screen — `sway/gtklock/config.ini`, `style.css` → `~/.config/gtklock/`

| Setting | Value |
|---|---|
| Background | the KognogOS wallpaper, blurred once (Gaussian 18, 20 % darker): `assets/lock/kognogos-mocha-blurred.jpg` → `~/.config/gtklock/background.jpg` (GTK3 cannot blur live) |
| Clock / date | 72 pt bold, 12-hour / 18 pt, `%A, %d %B` |
| Password box | 320 × 44 px, rounded (22 px), `#1e1e2e` at 85 %, 2 px border `#45475a`, mauve when typing; dots per key |
| Hide the box | after 30 s idle (`idle-hide`) |

D-58: "it is perfect my friend".

## The pop-up apps from the bar

| App | Look | File |
|---|---|---|
| Every fuzzel list (also the network menu) | our list look is **fuzzel's default**: `~/.config/fuzzel/fuzzel.ini` → `sway/fuzzel/fuzzel.ini` | — |
| Network menu (networkmanager_dmenu) | fuzzel, under the bar's right end, Noto Sans 10 pt, ● for the active connection, Wi-Fi signal icons, password as dots | `themes/networkmanager-dmenu/config.ini` → `~/.config/networkmanager-dmenu/` |
| Mixer (wiremix) | KognogOS Mocha theme (mauve selection, blue volume bars, green / red meters), straight borders; full device names (Arctis **Chat** / **Game**); tab row stays at the bottom (no setting) | `themes/wiremix/wiremix.toml` → `~/.config/wiremix/` |
| (all three terminal apps) | float, with a **light 3 px border** (`border = 3` in Window Rules) so they stand out (Javier) | `applets/rules/rules.toml` |
| Bluetooth (bluetui) | no colour settings — it uses the terminal's (Alacritty's KognogOS theme); Esc quits | `themes/bluetui/config.toml` → `~/.config/bluetui/` |
| nmtui | the closest KognogOS colours it can take (the terminal's basic colour names → Alacritty's Mocha shades): dark background, light text, grey borders, **pink** title and highlight (the nearest to mauve), dark text on the highlight; opens floating | `themes/nmtui/hypeforge-nmtui` (linked as `~/.local/bin/hypeforge-nmtui`; used by the bar and the network menu) |

## Midnight Commander — `themes/mc/kognogos-mocha.ini` → `~/.local/share/mc/skins/`

Full colour; Catppuccin Mocha with the emblem's blue folders and peach marked files, mauve headers and menu highlight, red error boxes, rounded corners. Chosen by `skin=kognogos-mocha` in `~/.config/mc/ini`. Preview: `themes/mc/preview.png`.

## Terminal — Alacritty (alacrittyForge)

`~/.config/alacritty/alacritty.toml`: JetBrainsMono Nerd Font 12; colours from `themes/KognogOS-theme.toml`. Set with **alacrittyForge**, which the Theme manager will open.

## GTK apps, icons, mouse pointer — `themes/gtk/` → `~/.config/gtk-3.0/` and `~/.config/gtk-4.0/`

Replaced on 2026-10-05 (Javier: "we will remove KDE eventually, and it will break if not fixed"). In the Sway session GTK apps take their settings from **gsettings** (through the settings portal), and older apps from `settings.ini`; both now say the same thing. Backups of the old files: `logs/20261005-gtk-before.tar.gz`, `logs/20261005-gsettings-interface-before.txt`.

| Setting | Value | Was |
|---|---|---|
| GTK theme | **adw-gtk3-dark** (package adw-gtk-theme — not KDE, not GNOME's desktop) | `settings.ini` said Breeze (KDE); gsettings already said adw-gtk3-dark |
| GTK colours | **KognogOS Mocha** in `gtk.css` (GTK 3 and 4): window `#1e1e2e`, title bars and side panels `#181825` (the bar), cards / menus / pop-ups / dialogs `#262637` (the shade), accent mauve `#cba6f7`, borders `#45475a`, red / green / yellow for errors, success, warnings | a leftover grey `gtk.css` from the Hyprland days (D-36 "Gray") |
| Mouse pointer | **catppuccin-mocha-dark-cursors**, 24 px — gsettings, `settings.ini`, and Sway's own (`seat * xcursor_theme` in `sway/config`) | breeze_cursors (KDE) |
| Icon theme | candy-icons | unchanged |
| Font / monospace font | Noto Sans 10 / **JetBrainsMono Nerd Font 10** | monospace was Hack (KDE's default) |
| Window buttons | close only (`gtk-decoration-layout=:close`) | minimize, maximize, close — hypeForge has no title bars |
| KDE add-ons | `gtk-modules` (colorreload, window-decorations) removed | — |

⚠️ Logging in to **Plasma** (the fallback) may write KDE's choices back into `settings.ini` and `colors.css`; the Sway session reads gsettings first, so it keeps this look. Re-apply from `themes/gtk/` if needed.

### galculator — `~/.config/galculator/galculator.conf`

Its number display has colours of its own: background `#181825`, result `#cdd6f4` (Noto Sans Bold 26), history `#a6adc8`, active labels mauve `#cba6f7`, inactive `#585b70`. Before: white with black numbers (`logs/20261005-galculator-before.conf`).

---

## For the Theme manager

Everything above in one app: the palette swapped in one place (Sway's `$hf_*` names, the bar's `@define-color`s, the lists, mako, gtklock, mc, Alacritty), fonts and sizes, the shaded areas, corners straight or rounded, the GTK theme, icons and pointer, the wallpaper and the lock screen's blur. Today each lives in its own file; the app will write them together.
