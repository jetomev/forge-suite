# Look research 04 · The inventory: everything in hypeForge that has a look

*Research helper 4 of 5 for the look program (D-67, `docs/look-program.md`), 2026-10-10. Read-only: nothing was installed, restarted or changed. Every value below was read from the file named, with its line number, on 2026-10-10. The repo copy is under `~/Programs/forge-suite/hypeforge/`; the live copy is what the desktop actually reads.*

**What this page is for:** a theme (colours) and a style (shapes) must reach every place listed here, and hypeForge Settings will need a control for each. List A (what a theme must touch) and list B (what Settings needs) are at the end.

**Versions on this machine** (`pacman -Q`): sway 1.12, swaybg 1.2.2, waybar 0.15.0, mako 1.11.0, fuzzel 1.15.0, gtklock 4.0.0 (GTK 3, `ldd`), swappy 1.8.0, slurp 1.5.0, adw-gtk-theme 6.5, libadwaita 1.9.4, gtk3 3.24.52, gtk4 4.22.5, candy-icons-git r1369, catppuccin-cursors-mocha 2.0.0, wiremix 0.11.0, bluetui 0.8.1, networkmanager-dmenu 2.6.3.

**Man pages read on this machine:** `sway(5)`, `sway-output(5)`, `swaybg(1)`, `waybar(5)`, `waybar-wlr-taskbar(5)`, `waybar-tray(5)`, `mako(5)`, `fuzzel.ini(5)`, `gtklock(1)`, `swaynag(5)`, `slurp(1)`, `swappy(1)`.

---

## 0 · Surprises first (things the look program should know before it starts)

| # | What | Evidence | Why it matters |
|---|---|---|---|
| S-1 | **The live GTK settings were rewritten on 2026-10-08 18:43**, almost certainly by a Plasma login (THEME.md:134 warned about exactly this). The pointer, the monospace font and the window buttons are back to KDE's. | `~/.config/gtk-3.0/settings.ini` now says `gtk-cursor-theme-name=breeze_cursors`, `gtk-decoration-layout=icon:minimize,maximize,close`, `gtk-modules=colorreload-gtk-module`; `gsettings get org.gnome.desktop.interface cursor-theme` = `'breeze_cursors'`, `monospace-font-name` = `'Hack  10'`, `org.gnome.desktop.wm.preferences button-layout` = `'icon:minimize,maximize,close'`. Both live `gtk.css` files gained a last line `@import 'colors.css';` (KDE's Breeze colour file, 4,998 bytes, same timestamp). The repo (`themes/gtk/settings.ini:5,9`) still says catppuccin pointer and `:close`. | THEME.md's GTK table is no longer true on the desktop. A theme apply step must **write gsettings and both settings.ini files every time**, and must expect Plasma to undo it while Plasma is still installed. Sway's own pointer is still right (`XCURSOR_THEME=catppuccin-mocha-dark-cursors` in Waybar's environment). Not fixed here (read-only). |
| S-2 | **mako *can* include a file.** mako 1.11 has `include=<path>` ("must be absolute or start with ~/"). | `man 5 mako`, GLOBAL CONFIGURATION, `include=config path` | The assumption "mako has no include, so generate it whole" is out of date. A theme file can hold mako's colours; our `config` keeps the rest. *Unproven:* whether `[urgency=…]` sections inside an included file apply — test on the bench. |
| S-3 | **Two pop-up lists lose their prompt and width.** A `# comment` in the middle of the list of arguments swallows `"--prompt", …, "--width", "70"`. | `applets/clipboard/hypeforge-clipboard:48`, `applets/notifications/hypeforge-notifications:93` | The clipboard and notification lists open at fuzzel.ini's width 40 with the default prompt, not width 70 with their own prompt. A look bug to file (F-n), not fixed here. |
| S-4 | **Notification icons named by theme probably never show.** mako only searches `/usr/share/icons/hicolor` and `/usr/share/pixmaps` unless `icon-path` is set; ours is unset. `printer`, `drive-removable-media` and `system-lock-screen` exist only in candy-icons (0 files in hicolor/pixmaps, `find`). | `man 5 mako` `icon-path` ("Default: \"\""); `sway/mako/config` has no `icon-path`; `printers:100` and `drives:54` send `-i printer` / `-i drive-removable-media` | Found by reading, not seen on screen. The icon theme must also be written into mako's `icon-path` (and its parents: candy-icons inherits `breeze-dark,Adwaita,hicolor`). |
| S-5 | **Two dropdowns are placed by arithmetic on the bar's font.** Favorites opens at `x = 44 + 24 + len("Workspaces") * 8 + 8` px; Workspaces at `--x-margin 44`. | `applets/sections/hypeforge-sections:147`, `applets/workspaces/hypeforge-workspaces:187` | Any change to the bar's font, size, padding or the emblem's width moves these lists away from their buttons. A style that changes the bar must recompute them (better: read the button's real position). |
| S-6 | **Sway's tab row has no font set.** `font` is not in `sway/config`, so the tab titles (D-46's stand-in for folder tabs) use Sway's default `monospace 10`. `client.focused_tab_title` is not set either. | `sway(5)` "`font` … monospace 10 is the default"; `grep -n '^font' sway/config` = nothing | The one place where window titles show today is not in our font. |
| S-7 | **The terminal is not on the desktop's base colour.** Alacritty's `KognogOS-theme.toml` background is `#1a1a1a`, the desktop's is `#1e1e2e`; its magenta is pink `#f5c2e7`. Five more colourways sit unused next to it: `hypeforge-black/gray/green/mocha/white.toml` (backgrounds `#0f0f0f`, `#303030`, `#e2efe6`, `#1e1e2e`, `#ececec`). | `~/.config/alacritty/themes/KognogOS-theme.toml:2,19`; `alacritty.toml:55-57` imports only KognogOS-theme | The five colourways match the five wallpaper colours in `/usr/share/wallpapers/kognog/` (Black, Catppuccin Mocha, Gray, Green, White, each in "Arch" and "Semi"). That is a ready-made seed for the theme family. |
| S-8 | **Forge apps take their colours from Python, not from any file.** forgekit's palette is a literal dictionary; its accent is **blue** `#89b4fa`, the desktop's accent is **mauve** `#cba6f7`. | `forgekit/forgekit/theme.py:19-26` (COLORS), `:49` (`accent` = blue), `:50` (`title-accent` = mauve) | Stays as is (Javier: "we are not modifying how our terminal apps work"). Noted so a theme never promises to recolour Settings, Help, or any Forge app. |
| S-9 | **The bar's colours are only half named.** Five `@define-color` names exist, but the shade `#262637` is typed three times, red `#f38ba8` six, blue `#89b4fa` three, yellow `#f9e2af` once. One rule is dead: `#custom-ws.active` (the applet prints class `menu`, never `active`). | `sway/waybar/style.css:5-9` (names), `:43,117,124` (shade), `:111,152,177,181` (red), `:169,174,198` (blue), `:216` (yellow); dead rule `:86-89` vs `workspaces:168` | Before a theme can swap the bar's colours in one place, these literals must become names. |
| S-10 | **Pieces with no hypeForge look at all:** the exit bar (swaynag), the screenshot box (slurp), Qt/KDE apps (Kate, Dolphin…), Waybar's tooltips, and Chrome/Electron apps. | `sway/config:164` (swaynag with defaults); `screenshot:55` (`slurp -d`, no colours); no `QT_QPA_PLATFORMTHEME` in the session, `~/.config/kdeglobals:134,137` (`LookAndFeelPackage=Catppuccin-Mocha-Mauve`, `widgetStyle=Oxygen`); `style.css` has no `tooltip` rule | Each is listed in its own row below with what it can take. |
| S-11 | The accent GNOME apps are told: `gsettings … accent-color` = `'blue'`, while our `gtk.css` says mauve. | `gsettings get org.gnome.desktop.interface accent-color` | *Unproven* which wins in a libadwaita 1.9 app. libadwaita 1.6+ prefers CSS variables over `@define-color` names; check one GTK 4 app before trusting `gtk.css` alone. |

---

## 1 · The palette in use today

Catppuccin Mocha (thank you, catppuccin.com) plus one colour of our own, the **shade** `#262637`. These are the only colours anywhere in hypeForge's files.

| Name | Hex | Where (file:line) |
|---|---|---|
| Crust | `#11111b` | mc skin (`themes/mc/kognogos-mocha.ini:43`), forgekit |
| Mantle — "the bar" | `#181825` | `sway/config:55` ($hf_titlebar), `waybar/style.css:5`, `gtk.css:19,22,24,26`, galculator display, mc |
| Base — "window" | `#1e1e2e` | `gtk.css:13,15` (+ `fg` of accent/destructive/success/warning/error, `:10,44,47,50,53`), `gtklock/style.css:10,34,48` (as rgba 30,30,46 at 0.85), wiremix `:39`, mc, forgekit |
| **Shade** (ours) | `#262637` | `waybar/style.css:43,117,124`, `fuzzel.ini:24`, `mako/config:26`, `gtk.css:30,33,36,38` |
| Surface0 | `#313244` | `mako/config:34,49` (progress, low urgency border), mc, forgekit |
| Surface1 — "hover / inactive" | `#45475a` | `sway/config:54`, `waybar/style.css:9`, `fuzzel.ini:29,32`, `mako/config:28`, `gtklock/style.css:33,47`, `gtk.css:21,54`, wiremix `:27,29,32,37,41` |
| Surface2 | `#585b70` | wiremix `:23,40,43`, galculator inactive, Alacritty bright black, forgekit border |
| Subtext | `#a6adc8` | `sway/config:57`, `waybar/style.css:7`, `fuzzel.ini:26`, `mako/config:50`, wiremix, galculator |
| Text | `#cdd6f4` | `sway/config:53,56`, `waybar/style.css:6,8`, `fuzzel.ini:25,27`, `mako/config:27`, `gtklock/style.css:14,35,49`, `gtk.css:14,16,20,25,31,34,37,39`, wiremix |
| Mauve — accent | `#cba6f7` | `fuzzel.ini:28,31`, `gtklock/style.css:36,42`, `gtk.css:8,9`, wiremix `:17-19,22,36,39`, mc headers, galculator |
| Blue | `#89b4fa` | `waybar/style.css:169,174,198`, wiremix `:28` |
| Green | `#a6e3a1` | `gtk.css:45-46`, wiremix `:30,33` |
| Yellow | `#f9e2af` | `waybar/style.css:216`, `gtk.css:48-49`, Help's inline code (`help/hypeforge-help:54`) |
| Peach | `#fab387` | mc marked files |
| Red | `#f38ba8` | `sway/config:58`, `waybar/style.css:111,152,177,181`, `mako/config:53`, `gtklock/style.css:54`, `gtk.css:42-43,51-52`, wiremix `:31` |
| White | `#ffffff` | `fuzzel.ini:30` (selected row's text) |
| Shadow / see-through | `rgba(0,0,0,0.36)`, `0.5`, `0.6` | `gtk.css:23,27,32,35,55,56`, `gtklock/style.css:15` (text shadow) |

**Fonts in use:** `sans-serif` → Noto Sans (bar 14 px, `style.css:12-13`); Symbols Nerd Font 16 px (bar icons, `style.css:104-105,158-159,187-188,205-206`); Noto Sans 11 (`fuzzel.ini:12`), 10 (drives, printers, network menu: `drives:72`, `printers:91`, `networkmanager-dmenu/config.ini:7`), 9 (clipboard, notifications: `clipboard:48`, `notifications:93`); Noto Sans 10.5 (`mako/config:25`); gtklock 72 pt / 18 pt / 16 pt (`gtklock/style.css:19,24,37`); GTK Noto Sans 10 (`themes/gtk/settings.ini:7`); swappy `sans-serif` 20 (`swappy/config:8-9`); Alacritty JetBrainsMono Nerd Font 12 (`alacritty.toml:24-36`); Sway tab titles: unset → `monospace 10` (S-6).

**Shapes in use:** straight corners everywhere on the desktop (`style.css:15` `border-radius: 0`, `fuzzel.ini:37`, `mako/config:30`), **except** the lock screen (22 px pill, `gtklock/style.css:32,46`) and mc (rounded box lines, `kognogos-mocha.ini:21-24`). Borders: windows 2 px (`sway/config:68-69`), floating tools 3 px (`rules.toml:41,47,53,59,81,98,105`), lists and notifications 1 px, lock box 2 px. Gaps: 10 inner, 0 outer (`sway/config:76-77`). No shadows except GTK's own and the lock screen's text shadow. No see-through except Alacritty 0.97 (`alacritty.toml:9`) and the lock box 85 %.

---

## 2 · Piece by piece

Each piece: **what it is · files (repo → live, and whether they match today) · values today · what the program supports that we don't use · can it follow a generated theme file?**

### 2.1 Windows — Sway's borders, tabs, gaps

- **Files:** `sway/config` → `~/.config/sway/config` (same, `diff`). Screens: `~/.config/sway/outputs` (written by displayForge, included at `sway/config:42`).
- **Values today:**
  - Colour names `sway/config:53-58`: `$hf_active #cdd6f4`, `$hf_inactive #45475a`, `$hf_titlebar #181825`, `$hf_text #cdd6f4`, `$hf_subtext #a6adc8`, `$hf_urgent #f38ba8`.
  - `client.focused / focused_inactive / unfocused / urgent` `:61-64` (border, title background, title text, next-split indicator, window border). The indicator (where the next window opens) is `$hf_active`, so it is invisible against the focused border.
  - `default_border pixel 2`, `default_floating_border pixel 2` `:68-69`; `gaps inner 10`, `gaps outer 0` `:76-77`.
  - Floating tools: `border pixel 3` from Window Rules (`applets/rules/hypeforge-rules:49-50`, `rules.toml` blocks listed above).
- **Supported, not used** (`sway(5)`): `font` (tab/title font, S-6) · `client.focused_tab_title` · colours with alpha `#RRGGBBAA` · `titlebar_border_thickness`, `titlebar_padding`, `title_align left|center|right` (tab row shape) · `hide_edge_borders`, `smart_borders`, `smart_gaps` · per-side gaps (`gaps top|bottom|left|right`) · `default_border normal` (title bars, D-46 chose none). No rounded corners, shadows, blur or dimming in plain Sway; those need SwayFX (helper 01's topic).
- **Follows a theme file?** **Yes.** `include <paths…>` (`sway(5)`, expands `~`, each file once). A generated `~/.config/hypeforge/theme/sway.conf` holding the `set $hf_* …` lines (and `font`, gaps, border width) can be included **above line 61**: Sway replaces `$names` as it reads, so the names must exist before `client.*` uses them. `swaymsg reload` applies it live.

### 2.2 Wallpaper — swaybg

- **Files:** `sway/config:34` → live (same). Pictures in `/usr/share/wallpapers/kognog/` (11 files: Arch and Semi designs × Black, Catppuccin Mocha, Gray, Green, White, plus `default.png`).
- **Values today:** `output * bg "/usr/share/wallpapers/kognog/Kognog OS Semi - Logo Catpuccin Mocha.png" fill` — one picture on every screen.
- **Supported, not used** (`sway-output(5)`, `swaybg(1)`): modes `stretch | fill | fit | center | tile`; a fallback colour after the mode; `output <name> bg <colour> solid_color` (plain colour, no alpha); **one picture per screen** (`output DP-2 bg …`); `swaybg_command` for another wallpaper program.
- **Follows a theme file?** **Yes**, through the same Sway include (an `output * bg …` line in the theme file, read after line 34 so it wins). Live without a reload: `swaymsg 'output * bg <file> fill'`.

### 2.3 Mouse pointer

- **Files:** `sway/config:98` (Sway's own and older X11 apps); `themes/gtk/settings.ini:5-6` → `~/.config/gtk-3.0/` and `gtk-4.0/settings.ini`; gsettings `org.gnome.desktop.interface cursor-theme` / `cursor-size`.
- **Values today:** Sway: `seat * xcursor_theme catppuccin-mocha-dark-cursors 24` (live session env confirms). **GTK side live: `breeze_cursors`** (S-1). Installed choices: 16 Catppuccin Mocha cursor colours (`/usr/share/icons/catppuccin-mocha-*-cursors`: blue, dark, flamingo, green, lavender, light, maroon, mauve, peach, pink, red, rosewater, sapphire, sky, teal, yellow), `breeze_cursors`, `Adwaita`, `~/.icons/Layan-border-cursors`. `/usr/share/icons/default/index.theme` inherits `Adwaita`.
- **Follows a theme file?** Sway: yes (include). GTK: only by writing gsettings + both settings.ini (no include for gsettings).

### 2.4 The top bar — Waybar

- **Files:** `sway/waybar/config.jsonc` and `style.css` → `~/.config/sway/waybar/` (same). Generated by applets: `~/.config/hypeforge/applets/workspaces.waybar.json` (applet 1), `favourites.waybar.json` and `favourites.css` (applet 4, the CSS is an empty placeholder today). Emblem picture: `~/.config/hypeforge/bar/launcher.png` (same bytes as `assets/kognogos-emblem.png`, 256×256). Waybar is a **GTK 3** program, so `~/.config/gtk-3.0/gtk.css` also reaches it (tooltips, tray menus).
- **Values today — layout** (`config.jsonc`): `layer top` `:7`, `position top` `:8`, `height 32` `:9`, `spacing 0` `:10`; left = launcher · workspaces · favourites `:13`; centre = taskbar `:23` (`icon-size 18`, `icon-theme candy-icons` `:29-30`); right = one group `:42` (tray · clipboard · drives · printers · bluetooth · network · volume · clock · bell · power); tray `icon-size 16`, `spacing 10` `:107-108`; clock format `{:%a %d %b   %I:%M %p}` `:131`. Icons as Nerd Font glyphs: network `:48-52`, Bluetooth `:60-63`, volume `:72-73`, power `:100`.
- **Values today — look** (`style.css`): names `:5-9` (bar `#181825`, text and active `#cdd6f4`, subtext `#a6adc8`, inactive `#45475a`); everything `font-family sans-serif`, `14px`, `border none`, `border-radius 0` `:11-17`; emblem 17×17 px inside a 19 px button, margins `0 6px 0 10px` `:26-34`; left area and right group and taskbar on the shade `#262637` `:43,117,124`; workspace number square: background `@hf_active`, text `@hf_bar`, bold, margin `6px 2px 6px 0` `:62-69`; menu titles in subtext, hover grey `:48-57,74-83`; clock with 1 px grey lines either side, padding `0 14px` `:93-99`; power glyph 16 px, red on hover `:102-112`; taskbar buttons 2 px underline for the window in use `:128-139`; tray menu on the bar colour `:146-149`; needs-attention red `:151-153`; indicator icons 16 px Symbols Nerd Font in subtext, hover text `:156-166`, states: drives blue `:168`, printing blue / stopped red `:173-178`, off/muted/disconnected red `:180-182`, clipboard new blue `:197-199`, bell unseen yellow / DND red `:215-221`.
- **Glyph icons drawn by applets** (Symbols Nerd Font): clipboard `\U000f0147` (`clipboard:36`), USB `\U000f0553` (`drives:25`), printer `\U000f042a` (`printers:23`), bell / new / off `\U000f009a`, `\U000f009e`, `\U000f009b` (`notifications:31`). Workspaces title `<u>W</u>orkspaces`, class `menu` (`workspaces:168`); number square class `wsnum` (`:175`); Favorites `<u>F</u>avorites` (`sections:125`).
- **Supported, not used** (`waybar(5)`, Waybar is GTK 3 CSS): `position bottom|left|right` · `margin` / `margin-<side>` (a floating bar with space around it) · `width` · `mode` / `start_hidden` (hide/show bar) · `exclusive`, `passthrough` · `output` (bar on chosen screens only) · `name` (a CSS class per bar, for several bars) · `reload_style_on_change` (reload when the CSS or anything it imports changes) · `fixed-center` · per-module `#` copies. CSS: `border-radius`, `box-shadow`, `background` gradients and `alpha()`/`shade()`/`mix()` colour functions, `opacity`, `transition` (hover fades), `margin` (gaps between "pills"), `tooltip` styling, `:hover`, per-state classes. Taskbar: `markup`, `rewrite`, `app_ids-mapping` (`waybar-wlr-taskbar(5)`); tray: `show-passive-items`, `reverse-direction` (`waybar-tray(5)`).
- **Follows a theme file?** **Yes, already proven:** `style.css:2` has `@import url("../../hypeforge/applets/favourites.css")` (path relative to the CSS file; `@import` must come first). A theme's `@define-color` file imported there works — **but** `style.css` must then stop defining the same names itself (the later definition wins) and the S-9 literals must become names. Layout values (`height`, `position`, icon sizes) live in JSON: the config's own `"include"` list (`config.jsonc:5-6`) can take a generated style fragment ("the first defined value takes precedence: including file → first included file", `waybar(5)`) — so values the theme owns must be **removed** from `config.jsonc`, or they win. Reload: `SIGUSR2` (`hfbar.signal_bar`, used by `sections:134`, `workspaces:160`).

### 2.5 The pop-up lists — fuzzel

The launcher (Win + D), App Sections (Win + Space), Workspaces, Favorites, the power menu, the clipboard, the notification list, drives, printers, and the network menu.

- **Files:** `sway/fuzzel/fuzzel.ini` → `~/.config/sway/fuzzel/fuzzel.ini` (same); `~/.config/fuzzel/fuzzel.ini` is a link to it, so fuzzel's own default also has our look. Named for the launcher by `sections.toml:17` (`fuzzel_config`), and hard-wired in `clipboard:32`, `drives:26`, `printers:24`, `notifications:29`, `workspaces:185`.
- **Values today** (`fuzzel.ini`): `font Noto Sans:size=11` `:12`, `icon-theme candy-icons` `:13`, `prompt "❯  "` `:14`, `width 40`, `lines 12` `:15-16`, padding 14 / 10 / 6 `:17-19`, `layer overlay` `:20`; colours `:24-32`: background `262637ff`, text `cdd6f4ff`, prompt `a6adc8ff`, input `cdd6f4ff`, match `cba6f7ff`, selection `45475aff`, selection-text `ffffffff`, selection-match `cba6f7ff`, border `45475aff`; `border width 1`, `radius 0` `:35,37`.
- **Per-list overrides on the command line** (these beat the file, so a theme font never reaches them):

| List | Anchor, margins | Width | Font | Source |
|---|---|---|---|---|
| App Sections, power | top-left 4/4; power top-right 4/4 | — / 22 | file | `sections:78,159,173` |
| Favorites | top-left, x computed (S-5) | 30 | file | `sections:147-150` |
| Workspaces | top-left, x 44 | 28 | file | `workspaces:187-188` |
| Clipboard | top-right 4/4 | **meant 70, lost (S-3)** | Noto Sans 9 | `clipboard:47-49` |
| Notifications | top-right 4/4 | **meant 70, lost (S-3)** | Noto Sans 9 | `notifications:92-94` |
| Drives | top-right 4/4 | 48 | Noto Sans 10 | `drives:70-72` |
| Printers | top-right 4/4 | 48 | Noto Sans 10 | `printers:89-91` |
| Network menu | top-right 4/4 | 46 | Noto Sans 10 | `themes/networkmanager-dmenu/config.ini:7` |

- **Supported, not used** (`fuzzel.ini(5)`): colours `message`, `placeholder`, `counter` · every colour takes **alpha** (see-through lists) · `border.selection-radius` (rounded highlight) · `radius` (rounded list; default 10) · `line-height`, `letter-spacing`, `use-bold`, `image-size-ratio`, `minimal-lines`, `match-counter`, `placeholder` text, `hide-prompt`, `tabs`, `dpi-aware`, `gamma-correct-blending`.
- **Follows a theme file?** **Yes.** `include=<absolute or ~/ path>` in `[main]`; the included file has its own sections, so it can carry `[colors]` and `[border]`. The per-applet `--font` flags must move into the file (or read the theme) or fonts stay fixed in five places. Read at every open: no reload needed.

### 2.6 Notifications — mako

- **Files:** `sway/mako/config` → `~/.config/mako/config` (same).
- **Values today:** top-right, focused screen, `layer top`, `outer-margin 10`, `margin 6`, `width 420`, `height 200`, `max-visible 5` `:8-15`; 5 s `:20`; `font Noto Sans 10.5` `:25`; background `#262637`, text `#cdd6f4`, border `#45475a`, `border-size 1`, `border-radius 0`, `padding 10` `:26-31`; icons on, `max-icon-size 40` `:32-33`; `progress-color over #313244` `:34`; low urgency border `#313244`, text `#a6adc8` `:48-50`; critical border `#f38ba8`, stays `:52-54`; Do Not Disturb hides `:57-58`.
- **Supported, not used** (`mako(5)`): **alpha** in every colour (`#RRGGBBAA`) · per-corner `border-radius` · `icon-location left|right|top|bottom` · `icon-border-radius` · **`icon-path`** (S-4) · `format` (Pango markup: bold title, colours, sizes per part) · `text-alignment` · `group-by` · per-app criteria (`[app-name=…]`) for per-app colours · `[urgency=normal]` own colours.
- **Follows a theme file?** **Yes** (S-2): `include=~/.config/hypeforge/theme/mako.conf`. Apply with `makoctl reload`.

### 2.7 Lock screen — gtklock (GTK 3)

- **Files:** `sway/gtklock/config.ini`, `style.css` → `~/.config/gtklock/` (style same; config differs only in its first comment line). Background picture `assets/lock/kognogos-mocha-blurred.jpg` (3840×2160) → `~/.config/gtklock/background.jpg`.
- **Values today:** `config.ini:7-10`: time `%I:%M %p`, date `%A, %d %B`, hide the box after 30 s. `style.css`: window background picture, `cover`, fallback `#1e1e2e` `:7-10`; labels `#cdd6f4` with text shadow `0 1px 4px rgba(0,0,0,0.6)` `:14-15`; clock 72 pt bold `:19-20`; date 18 pt, 24 px under `:24-25`; password box 320×44, padding 0 16, **radius 22 px**, 2 px `#45475a` border, background `rgba(30,30,46,0.85)`, text `#cdd6f4`, caret mauve, 16 pt `:29-38`; mauve border while typing `:42`; buttons the same pill `:46-50`; errors red `:54`.
- **Supported, not used** (`gtklock(1)`): `gtk-theme=` (its own GTK theme) · `background=` path in config (CSS can override) · `layout=` (an XML layout file: move the clock, the box) · `modules=` (none installed: `/usr/lib/gtklock` absent — userinfo, powerbar, playerctl exist upstream) · `start-hidden` · `monitor-priority` · lock/unlock commands. All of GTK 3 CSS.
- **Follows a theme file?** **Yes**: GTK 3 CSS supports `@import url(…)` at the top of `style.css`; the blurred picture must be **made per wallpaper** (GTK 3 cannot blur live, `style.css:5-6`) — one blurred copy per theme's wallpaper. Read at every lock.

### 2.8 GTK apps (3 and 4) — and everything GTK draws

Reaches: swappy, galculator, gtklock's widgets, **Waybar's tooltips and tray menus**, file dialogs, GNOME/GTK apps.

- **Files:** `themes/gtk/gtk.css` → `~/.config/gtk-3.0/gtk.css` and `~/.config/gtk-4.0/gtk.css` (**differ live**: `@import 'colors.css';` appended, S-1); `themes/gtk/settings.ini` → both `settings.ini` (**differ live**, S-1); gsettings `org.gnome.desktop.interface` (read by GTK in the Sway session through the settings portal, THEME.md:122).
- **Values today (repo):** `gtk.css:8-56` defines adw-gtk3/libadwaita named colours: accent mauve (`accent_fg` base), window/view `#1e1e2e` on `#cdd6f4`, header bar and sidebar `#181825` (header border `#45475a`), cards / popovers / dialogs / thumbnails the shade `#262637`, destructive/error red, success green, warning yellow (all with base text), borders `#45475a`, shades `rgba(0,0,0,0.36)`, scrollbar outline 0.5. `settings.ini:2-9`: `adw-gtk3-dark`, prefer dark, candy-icons, catppuccin-mocha-dark-cursors 24, Noto Sans 10, animations on, buttons `:close`.
- **Values today (live gsettings):** gtk-theme `adw-gtk3-dark`, icon-theme `candy-icons`, cursor-theme **`breeze_cursors`**, cursor-size 24, font `Noto Sans 10`, monospace **`Hack 10`**, document font `Noto Sans 10`, color-scheme `prefer-dark`, accent-color **`blue`**, text-scaling 1.0, button-layout **`icon:minimize,maximize,close`**.
- **Installed choices:** GTK themes `adw-gtk3`, `adw-gtk3-dark`, `Breeze`, `Breeze-Dark`; icon themes `candy-icons`, `Papirus`, `Papirus-Dark`, `Papirus-Light`, `breeze`, `breeze-dark`, `oxygen`, `Adwaita`, `hicolor`.
- **Supported, not used:** GTK CSS for shapes (corner radius of buttons, entries, menus; no font or radius rules in our `gtk.css`) · libadwaita 1.9 **CSS variables** (`--accent-bg-color`, `--window-radius`…) which newer apps prefer over `@define-color` (S-11, unproven) · gsettings `accent-color` (libadwaita's own accent list), `text-scaling-factor`, `font-antialiasing`/`font-hinting`.
- **Follows a theme file?** **Yes**: `gtk.css` can be one line, `@import url("…/theme/gtk-colors.css");` (GTK 3 and 4). `settings.ini` and gsettings have **no include**: they must be written key by key. GTK 3 apps pick up `gtk.css` only on restart; gsettings changes are live.

### 2.9 swappy (drawing on a screenshot) and galculator

- **swappy** — `sway/swappy/config` → `~/.config/swappy/config` (same): `line_size 5`, `text_size 20`, `text_font sans-serif`, `paint_mode arrow` `:7-10`. Not used (`swappy(1)`): `custom_color` (the default pen colour, e.g. our accent). Its window is GTK 3 (2.8).
- **galculator** — `~/.config/galculator/galculator.conf` (live only, no repo copy; THEME.md:136-138): display background `#181825` `:4`, result `Noto Sans Bold 26` in `#cdd6f4` `:5-6`, history `Noto Sans Bold 11` in `#a6adc8` `:7-8`, labels `Noto Sans Bold 8`, active mauve, inactive `#585b70` `:9-11`, buttons `Sans 10` `:18`. No include: rewrite the keys (galculator writes its file on exit, so only while it is closed). Stopgap until our own calculator (TODO.md:91).

### 2.10 The terminal — Alacritty (set by alacrittyForge)

- **Files:** `~/.config/alacritty/alacritty.toml` (live, owned by alacrittyForge, no hypeForge repo copy) and `~/.config/alacritty/themes/*.toml`.
- **Values today:** no window decorations, `opacity 0.97`, `blur false` `:8-10`; 150×50, padding 15/15 `:13-18`; JetBrainsMono Nerd Font 12, regular/bold/italic `:24-36`; block cursor, blinking `:41-43`; colours from `themes/KognogOS-theme.toml` `:55-57` (S-7).
- **Follows a theme file?** **Yes**: `[general] import = [ … ]`. A theme can ship its own terminal colour file and point the import at it; Alacritty reloads by itself. Terminal apps that use the terminal's colours follow automatically: **bluetui** (`themes/bluetui/config.toml`: no colour settings), **nmtui** (`themes/nmtui/hypeforge-nmtui:8`, colour *names* such as magenta → whatever the terminal theme maps them to), btop, cliamp. The look program should leave the change to alacrittyForge (Settings already has a Terminal page, `settings.toml:36-40`).

### 2.11 Terminal apps with their own colours: mc, wiremix

- **Midnight Commander** — `themes/mc/kognogos-mocha.ini` → `~/.local/share/mc/skins/kognogos-mocha.ini` (same); chosen by `skin=kognogos-mocha` (`~/.config/mc/ini:86`). Built as a palette block (`[aliases]` `:41-66`) then roles (`:68-80`: main Base/Text, selected Surface1, marked Peach, headers Mauve, dialog Surface0…), rounded line set `:18-39`. **Follows a theme?** By generating one skin per theme (only the `[aliases]` block changes) and switching `skin=`. Takes effect when mc next starts.
- **wiremix** (mixer) — `themes/wiremix/wiremix.toml` → `~/.config/wiremix/wiremix.toml` (same): `theme = "kognogos"` `:5`, 27 colour roles `:17-43` (mauve selection, blue volume bars, green/red meters, grey borders), plain borders `:45-48`. No include seen in its file (*unverified* in wiremix's docs): generate the `[themes.kognogos]` block whole.

### 2.12 Forge apps — Settings, Help & Keys, every Forge Suite app

- **How they get colours:** forgekit `theme.py` — `COLORS` (Catppuccin Mocha literals, `:19-26`), `ROLES` (`:32-80`, each role has a truecolour value and a text-console value), `SHAPES` (`:83-92`: rounded borders, 45 % / 30 % backdrops, bold), turned into `$forge-*` CSS variables (`:95-100`). Apps ask for roles (`$forge-accent`, `$forge-border`…): Settings `hypeforge-settings:62-77`, Help `hypeforge-help:118-134` (+ one literal, inline code in yellow `#f9e2af`, `:54`). Settings' page icons are Nerd Font glyphs (`settings/home.py:42-48`).
- **Follows a theme file?** No — and by Javier's rule it **stays that way** for now. Their look is independent of the desktop theme.

### 2.13 Small pieces with no look of ours yet

| Piece | What draws it today | What it can take | Source |
|---|---|---|---|
| **Exit bar** (Win + Shift + E) | swaynag `-t warning`, Sway's built-in yellow/brown | `~/.config/swaynag/config` with `[warning]` sections: `background`, `border`, `border-bottom`, `button-background`, `text`, `button-text`, `font`, sizes, paddings, gaps, `edge top|bottom`, `layer` | `sway/config:164`, `swaynag(5)` |
| **Screenshot box** | `slurp -d`, slurp's defaults | `-b` dim colour, `-c` border colour, `-s` selection fill, `-B` box colour, `-w` border width, `-F` font | `screenshot:55`, `slurp(1)` |
| **Waybar tooltips** | GTK theme (+ KDE's `colors.css` live) | a `tooltip` rule in `style.css` (background, border, radius, font) | no `tooltip` in `style.css` |
| **Qt / KDE apps** (Kate, KDE dialogs…) | nothing from hypeForge: no `QT_QPA_PLATFORMTHEME` in the session; leftover `~/.config/kdeglobals` (`LookAndFeelPackage=Catppuccin-Mocha-Mauve` `:134`, `widgetStyle=Oxygen` `:137`) | *unverified* what they actually show under Sway. KognogOS removes KDE later; qt5ct/qt6ct/Kvantum are not installed | session env, `pacman -Q` |
| **Chrome, Claude Desktop, Electron apps** | follow GTK's dark preference (gsettings `color-scheme prefer-dark`) | Chrome's own theme setting; nothing to write from hypeForge | `sway/chrome/`, `sway/claude/` carry flags only, no look |
| **Text consoles** | Terminus font (FONTS.md) | out of scope (GRUB is grubForge's) | — |

### 2.14 Pieces with no look (checked, nothing to theme)

`sway/cliphist/config` (history size), `themes/udiskie/config.yml` (tray off, `:15`; notifications through mako), `sway/chrome/chrome-flags.conf` and `sway/claude/claude-desktop-flags.conf` (video and password-store flags), `sway/sway-hypeforge.desktop` (the login entry), `applets/placement`, `applets/autostart`. The banner `assets/banner.svg` (1280×400, Mocha gradient `#1e1e2e → #11111b`) is the README's, not the desktop's.

---

## A · What a theme must touch (deduplicated)

One row per file a theme writes. "How" = the cleanest way the program allows.

| # | File the desktop reads | What the theme owns there | How | Applied by |
|---|---|---|---|---|
| A-1 | `~/.config/sway/config` (+ new `…/theme/sway.conf`) | the six `$hf_*` colours, `client.focused_tab_title`, `font` (tab row), border width, gaps, wallpaper line | **include** a generated file above line 61 | `swaymsg reload` |
| A-2 | `~/.config/sway/waybar/style.css` (+ `…/theme/waybar.css`) | every colour (after S-9: shade, red, blue, yellow become names), font family and size, icon font size, radius, margins/padding, shadows | **`@import`** at line 1–2 | `SIGUSR2` or `reload_style_on_change` |
| A-3 | `~/.config/sway/waybar/config.jsonc` | bar `height`, `position`, `margin`, taskbar `icon-size` / `icon-theme`, tray `icon-size` / `spacing` | Waybar **`include`** of a generated JSON fragment, with those keys **removed** from `config.jsonc` | `SIGUSR2` |
| A-4 | `~/.config/sway/fuzzel/fuzzel.ini` (+ `…/theme/fuzzel.ini`) | `[colors]` (9 used + 3 unused), `[border]` width/radius/selection-radius, `font`, `icon-theme`, paddings | **`include=`** | none (read each open) |
| A-5 | applet command lines | the fixed `--font Noto Sans:size=9/10` in clipboard, notifications, drives, printers, network menu; the x positions of Workspaces and Favorites (S-5) | change the applets once to read the theme (or drop the flags) | — |
| A-6 | `~/.config/networkmanager-dmenu/config.ini` | `dmenu_command` font and width (`:7`) | rewrite the line, or let it read the fuzzel file only | none |
| A-7 | `~/.config/mako/config` (+ `…/theme/mako.conf`) | background, text, border, progress, low/critical colours, font, radius, border size, padding, icon size, **`icon-path`** | **`include=`** (S-2; criteria-in-include to verify) | `makoctl reload` |
| A-8 | `~/.config/gtklock/style.css` + `background.jpg` | label/clock colours, box colours, radius, border, fonts, text shadow; the **blurred wallpaper per theme** | **`@import`** + one pre-blurred picture per wallpaper | next lock |
| A-9 | `~/.config/gtk-3.0/gtk.css`, `~/.config/gtk-4.0/gtk.css` | ~40 named colours (and libadwaita variables, S-11) | **`@import`**, and remove KDE's `@import 'colors.css'` | app restart |
| A-10 | `~/.config/gtk-3.0/settings.ini`, `gtk-4.0/settings.ini` | GTK theme, dark preference, icon theme, cursor theme and size, font, button layout; drop `gtk-modules` | **write keys** (no include) | app restart |
| A-11 | gsettings `org.gnome.desktop.interface` (+ `wm.preferences button-layout`) | `gtk-theme`, `color-scheme`, `icon-theme`, `cursor-theme`, `cursor-size`, `font-name`, `monospace-font-name`, `document-font-name`, `accent-color` | **write keys**; rewrite on every apply while Plasma can undo it (S-1) | live |
| A-12 | `seat * xcursor_theme` | pointer theme and size | in the Sway include (A-1) | `swaymsg reload` |
| A-13 | `~/.config/alacritty/alacritty.toml` → `themes/<theme>.toml` | 16 terminal colours, background, cursor, selection (font and opacity stay alacrittyForge's) | **`import`**; leave the switch to alacrittyForge | live |
| A-14 | `~/.local/share/mc/skins/<theme>.ini` + `skin=` in `~/.config/mc/ini` | the `[aliases]` palette | generate one skin per theme | next start |
| A-15 | `~/.config/wiremix/wiremix.toml` | the 27 colour roles | generate the theme block | next start |
| A-16 | `~/.config/galculator/galculator.conf` | 5 display colours, 3 display fonts | write keys while it is closed | next start |
| A-17 | `~/.config/swappy/config` | `custom_color`, `text_font` | write keys | next start |
| A-18 | `~/.config/swaynag/config` (new) | `[warning]` colours, font, sizes | generate whole | next exit prompt |
| A-19 | `applets/screenshot/hypeforge-screenshot:55` | slurp `-b -c -s -B -w` | read the theme in the applet | next screenshot |
| A-20 | `~/.config/hypeforge/bar/launcher.png` | the emblem picture (per colourway, if wanted) | swap the file | `SIGUSR2` |
| A-21 | `~/.config/hypeforge/applets/rules.toml` | floating tools' border width (`border = 3`) | write keys (a style setting, not a colour) | `hypeforge-rules reload` |
| — | forgekit `theme.py` | **not touched** (Javier's rule) | — | — |

Reached for free once A-9/A-10/A-11 and A-13 are right: Waybar tooltips and tray menus, swappy and galculator windows, gtklock's widgets, file dialogs, bluetui, nmtui, btop, cliamp.

---

## B · What hypeForge Settings needs for look and theming

Settings today has nine pages (`applets/settings/settings.toml`); none is about the look except **Terminal** (alacrittyForge) and **Boot Menu** (grubForge). Every page below is a Forge app on forgekit (D-59) — it sets the desktop's look, its own window keeps the forgekit look.

| Page / control | What the person picks | What it writes | Reload |
|---|---|---|---|
| **Look → Theme** (colours) | one of the 23 colour themes; shows a swatch | the theme files of A-1, A-2, A-4, A-7, A-8 (colours), A-9, A-13 import, A-14 `skin=`, A-15, A-16, A-17, A-18, A-19 | each piece's own reload (column above), in one step: `hypeforge-theme apply <style> <colour>` (look-program phase 4) |
| **Look → Style** (shapes) | one of the 6 styles | radius, borders, gaps, shadows, bar layout: A-1 (gaps, border width, tab font/title align), A-2 (radius, margins, shadows), A-3 (height, position, margins), A-4 `[border]`, A-7 radius/border, A-8 radius, A-21 | same |
| **Look → Accent** | one colour (or "the theme's own") | the accent name in every theme file (mauve today: fuzzel match, gtklock caret/focus, GTK accent, wiremix selection, mc headers) + gsettings `accent-color` (nearest of libadwaita's list) | same |
| **Look → Wallpaper** | a picture per screen or one for all; fit mode (fill/fit/center/tile/stretch) or a plain colour | `output <screen|*> bg <file> <mode> [<colour>]` into the Sway theme file (A-1); a new blurred copy for the lock screen (A-8) | `swaymsg output … bg …` (live) |
| **Look → Fonts** | interface font + size; monospace font; bar size | Sway `font`, Waybar `font-family/font-size`, fuzzel `font` (and the five applet flags, A-5), mako `font`, gtklock sizes, settings.ini + gsettings `font-name` / `monospace-font-name`, swaynag `font` | each reload; then recompute the dropdown positions (S-5) |
| **Look → Icons** | icon theme (candy-icons, Papirus…) | Waybar taskbar `icon-theme`, fuzzel `icon-theme`, mako `icon-path`, settings.ini + gsettings `icon-theme` | same |
| **Look → Pointer** | cursor theme + size (16 Catppuccin colours, Adwaita, Breeze…) | `seat * xcursor_theme`, settings.ini + gsettings `cursor-theme` / `cursor-size` | `swaymsg reload` |
| **Look → Dark / light** | follows the theme, or forced | gsettings `color-scheme`, settings.ini `gtk-application-prefer-dark-theme`, GTK theme `adw-gtk3` vs `adw-gtk3-dark` | live / restart |
| **Bar** | position (top/bottom), height, floating margin, which icons show and in what order, clock format | `config.jsonc` (or its include, A-3): `position`, `height`, `margin`, the `group/indicators` list (`:42`), clock `format` (`:131`) | `SIGUSR2` |
| **Windows** | border width (focused / floating tools), gaps inside/outside, tab title alignment | Sway theme file (A-1), `rules.toml` `border` (A-21) | `swaymsg reload` |
| **Notifications** | where (corner), how long, how many, size, Do Not Disturb | mako `anchor`, `default-timeout`, `max-visible`, `width`/`height` | `makoctl reload` |
| **Lock screen** | clock 12/24 h, date format, hide-after seconds, idle times | gtklock `config.ini` (`time-format`, `date-format`, `idle-timeout`), swayidle line `sway/config:90-92` | next lock / `swaymsg reload` |
| **Launcher** (already planned, TODO.md:104) | the launcher's look tied to the theme, sections, favourites | `sections.toml`; the look comes from A-4 | none |
| **Terminal** (exists) | alacrittyForge, unchanged | `alacritty.toml` | live |
| **Undo / backup** | "go back to the last look" | a copy of every file above before each apply (CLAUDE.md: "applied by the app, with a backup and an undo") | — |

**Two things Settings must do that are not a control:** (1) **re-apply after a Plasma login** — while Plasma stays installed it rewrites `settings.ini`, gsettings and `gtk.css` (S-1); a check at login (or a "your look was changed by another desktop — put it back?" note) closes that gap. (2) **show a preview before applying** — the look program's mock-ups (H-2) are driven by the same tokens, so the same swatch can sit on the Theme page.

---

## Commands run (all read-only)

`find` / `cat -n` / `sed -n` over the repo; `diff -q` of every repo file against its live copy; `readlink -f` for the two links; `gsettings get org.gnome.desktop.interface <key>` (11 keys) and `org.gnome.desktop.wm.preferences button-layout`; `pacman -Q`, `pacman -Qo`; `ldd /usr/bin/gtklock`; `ls /usr/share/icons /usr/share/themes /usr/share/wallpapers/kognog`; `find /usr/share/icons/hicolor /usr/share/pixmaps /usr/share/icons/candy-icons -name '<icon>.*'`; `tr '\0' '\n' < /proc/<waybar pid>/environ`; `fc-match sans-serif`, `fc-match monospace`; `man 5 sway`, `man 5 sway-output`, `man 1 swaybg`, `man 5 waybar`, `man 5 waybar-wlr-taskbar`, `man 5 waybar-tray`, `man 5 mako`, `man 5 fuzzel.ini`, `man 1 gtklock`, `man 5 swaynag`, `man 1 slurp`, `man 1 swappy`.
