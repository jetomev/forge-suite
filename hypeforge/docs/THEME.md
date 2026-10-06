# hypeForge — the look, piece by piece

*Every place the desktop's look is set: the file, the values in it today, and why. This is the blueprint for the **Theme manager** Forge app (D-59): each row is something it will set. Javier, 2026-10-05: "there is going to be a lot of notes about how we have changed the system. We need to document those, because they are part of the theme management app."*

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
| The pop-up lists | Noto Sans | 11 pt (≈ the bar's 14 px) |
| Notifications | sans | 12 |
| Lock screen clock / date / password box | sans-serif | 72 pt / 18 pt / 16 pt |
| Terminal (Alacritty) and terminal apps | JetBrainsMono Nerd Font | 12 |
| GTK apps (swappy, galculator…) | Noto Sans | 10 |

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
| **Right** — tray · clipboard · bell · ┃ · date and time | the **shade**, straight edges; tray icons 16 px, clipboard and bell 16 px; a 1 px hover-grey line before the clock | "1 px at a time"; "add a separator… paint the date/time area the same colour" |
| Hover on any button | `#45475a` | — |
| Clock | `Mon 05 Oct   08:13 PM` | — |

## The pop-up lists — `sway/fuzzel/fuzzel.ini` → `~/.config/sway/fuzzel/`

The launcher, Workspaces, Favorites, the clipboard list and the notification list. They match the bar they drop from (Javier, 2026-10-05).

| Setting | Value |
|---|---|
| Font | Noto Sans 11 pt |
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
| Look | `sans 12`, background `#1e1e2e` (95 %), text `#cdd6f4`, 2 px border `#45475a`, **10 px rounded corners**, 12 px padding, 48 px icons |
| Low / critical | quieter grey border and text / red border, stays until clicked |
| Timing | 5 seconds |

⚠️ **Not yet matching the bar and the lists** (rounded, darker, a bigger font). Javier's call whether they follow.

## Lock screen — `sway/gtklock/config.ini`, `style.css` → `~/.config/gtklock/`

| Setting | Value |
|---|---|
| Background | the KognogOS wallpaper, blurred once (Gaussian 18, 20 % darker): `assets/lock/kognogos-mocha-blurred.jpg` → `~/.config/gtklock/background.jpg` (GTK3 cannot blur live) |
| Clock / date | 72 pt bold, 12-hour / 18 pt, `%A, %d %B` |
| Password box | 320 × 44 px, rounded (22 px), `#1e1e2e` at 85 %, 2 px border `#45475a`, mauve when typing; dots per key |
| Hide the box | after 30 s idle (`idle-hide`) |

D-58: "it is perfect my friend".

## Midnight Commander — `themes/mc/kognogos-mocha.ini` → `~/.local/share/mc/skins/`

Full colour; Catppuccin Mocha with the emblem's blue folders and peach marked files, mauve headers and menu highlight, red error boxes, rounded corners. Chosen by `skin=kognogos-mocha` in `~/.config/mc/ini`. Preview: `themes/mc/preview.png`.

## Terminal — Alacritty (alacrittyForge)

`~/.config/alacritty/alacritty.toml`: JetBrainsMono Nerd Font 12; colours from `themes/KognogOS-theme.toml`. Set with **alacrittyForge**, which the Theme manager will open.

## GTK apps, icons, mouse pointer — `~/.config/gtk-3.0/settings.ini`

| Setting | Value today | Note |
|---|---|---|
| GTK theme | **Breeze** (KDE's), dark preferred | ⚠️ a KDE leftover (D-56) — swappy, galculator and gtklock's widgets wear it. To change: a non-KDE dark theme + our colours |
| Icon theme | candy-icons | also used by the bar, the lists |
| Mouse pointer | breeze_cursors, 24 | ⚠️ KDE's — and Sway sets no pointer theme of its own yet (no `seat * xcursor_theme`) |
| Font | Noto Sans 10 | |
| Window buttons layout | icon:minimize,maximize,close | hypeForge has no title bars |

---

## For the Theme manager

Everything above in one app: the palette swapped in one place (Sway's `$hf_*` names, the bar's `@define-color`s, the lists, mako, gtklock, mc, Alacritty), fonts and sizes, the shaded areas, corners straight or rounded, the GTK theme, icons and pointer, the wallpaper and the lock screen's blur. Today each lives in its own file; the app will write them together.
