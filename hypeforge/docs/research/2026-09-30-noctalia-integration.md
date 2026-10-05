# Research · Making Noctalia 5.2.0 shine for hypeForge (D-40)

*2026-09-30 · Claude, for Javier · read-only research. Nothing was installed and no settings were changed. Noctalia's source code was cloned at the exact release tag `v5.2.0` into a scratch folder and read, together with the documentation that ships inside it (the same pages as https://docs.noctalia.dev). Every claim is marked **[verified]** (read in the v5.2.0 source code or docs today) or **[inferred]** (reasoned from them, still to be proven in the test VM).*

*A word on terms used below: a **palette** is Noctalia's name for a colour theme. A **template** is a small text file with blanks in it; Noctalia fills the blanks with the current colours and writes the result into another app's settings. A **hook** is a command Noctalia runs by itself when something happens (for example "the colours changed"). **IPC** means sending a command to the running Noctalia from a terminal or a key, as `noctalia msg <something>`.*

---

## The short version

1. **Settings live in two layers.** Our defaults go in `~/.config/noctalia/*.toml` (Noctalia only ever *reads* this folder). Everything Javier changes in Noctalia's Settings window is saved to `~/.local/state/noctalia/settings.toml`, which is read last and wins. So hypeForge can ship defaults without ever fighting his choices. Both layers reload by themselves the moment they change. Noctalia has **no system-wide folder** (`/etc/xdg` is not read), so a distro ships the defaults through `/etc/skel` or hypeForge's own folder. **[verified]**
2. **Our five themes become five palette files** in `~/.config/noctalia/palettes/`. A palette file has 16 named colours plus the 16 terminal colours. **A palette cannot carry a wallpaper, but a wallpaper can carry a palette.** Noctalia's "favourite wallpapers" can remember a palette and a light/dark choice. Picking that wallpaper, by click or by command, switches the wallpaper, the palette and light/dark in one step. That is how each theme gets its KognogOS wallpaper. **[verified in the source]**
3. **One switch can drive everything.** When the palette changes, Noctalia fills in our templates and then runs our `colors_changed` hook. The hook asks Noctalia which palette is active, writes the theme name for hypeForge, and reloads Hyprland. Our existing `theme.lua` then repaints borders, title bars, Alacritty, GTK apps, Hyprland's own apps and the lock screen, exactly as today. Noctalia's own built-in palettes (Nord, Dracula…) work too: the template gives `theme.lua` their colours. **[verified pieces; the assembled result is inferred until tried in the VM]**
4. **Keys:** Win tapped → `noctalia msg panel-toggle launcher`; Win + V → `panel-toggle clipboard`; Ctrl + Alt + Del → `panel-toggle session`; Win + L → `session lock` (or keep `loginctl lock-session`). Volume, brightness, media and Alt + Tab have commands too. **[verified]**
5. **What it replaces:** Waybar, mako, SwayOSD, hyprpaper, Walker (launcher, clipboard history, power menu), nm-applet and Blueman: **yes**. **udiskie: no** (Noctalia has no removable-drive feature). **Polkit agent: it has one, but it is off by default**, so hyprpolkitagent can stay. **[verified]**
6. **Taskbar with open-app icons:** yes. The `taskbar` widget is **not** in the default bar, so it has to be added. **[verified]**
7. **Lock screen:** Noctalia's and hyprlock **would clash** if both were on. Both answer the same "lock now" signal. Either set `[lockscreen] enabled = false` and keep hyprlock + hypridle, or switch fully to Noctalia's. **[verified switch; the clash is inferred from how both work]**
8. **Anonymous Startup Ping:** off by default in the code (`telemetry_enabled = false`). The welcome window shows it as a switch that starts off. We ship `telemetry_enabled = false` and `setup_wizard_enabled = false` to make sure. **[verified]**
9. **Nothing in the bug tracker is specific to Hyprland's Lua settings.** Noctalia's own docs are written for the Lua format. There are a few open NVIDIA-related reports, none blocking. Details are in §11. **[verified]**

---

## 1 · Configuration

### Where the settings live **[verified: docs `configuration/index.mdx`, `PACKAGING.md`]**

| What | Where | Who writes it |
|---|---|---|
| Our settings (the base layer) | `~/.config/noctalia/*.toml`, every file, read in alphabetical order and merged | us (Noctalia never rewrites these files) |
| Javier's GUI changes | `~/.local/state/noctalia/settings.toml` | Noctalia's Settings window, the welcome window, IPC commands |
| Small UI memory (last-used values) | `~/.local/state/noctalia/state.toml` | Noctalia |
| Custom palettes | `~/.config/noctalia/palettes/<Name>.json` | us |
| Log | `~/.cache/noctalia/noctalia.log` | Noctalia |

Load order: built-in defaults → our `*.toml` files → `settings.toml`. From the docs: *"Because `settings.toml` loads last, it wins when it contains the same setting as your hand-written config layer. When Settings writes a value that matches the parsed value from the lower layers, Noctalia removes that redundant key."*

**Hot reload:** *"Both layers are watched for changes and hot-reloaded."* There is also `noctalia msg config-reload`. **[verified]**

**Checking a file:** `noctalia config validate` checks everything; `noctalia config validate ./file.toml` checks a single file (useful in hypeForge's tests). `noctalia config export full` prints the effective settings. **[verified]**

### How a distro ships defaults **[verified: source code]**

- Noctalia reads **only** the user's folder (`$NOCTALIA_CONFIG_HOME`, `$XDG_CONFIG_HOME` or `~/.config`). A search of the source for `XDG_CONFIG_DIRS` and `/etc/xdg` finds them only in the EasyEffects helper, not in the settings loader. So **there is no `/etc/xdg/noctalia`**.
- Recommended shape: hypeForge ships **`~/.config/noctalia/00-hypeforge.toml`**. The file can live in hypeForge's portable folder, with `~/.config/noctalia` pointing into it like `hypr`, `waybar` and the others today. KognogOS can put the same file in `/etc/skel/.config/noctalia/`. A later file such as `50-mine.toml` can add to or change it, and GUI changes still win over both. **[inferred: follows from the documented merge order]**
- An `[include]` table can pull in other files or folders, with `autoload = false` for switchable profiles. We do not need it now. **[verified]**
- `setup_wizard_enabled = false` stops the welcome window from opening on first start. The welcome window writes its answers to `settings.toml` (for example the telemetry switch: `m_config->setOverride({"shell","telemetry_enabled"}, …)` in `setup_wizard_panel.cpp`). Left on, it could quietly override our defaults on the first login. **[verified that it writes overrides; the "override our defaults" risk is inferred]**

The full annotated example of every setting is `example.toml` in the repo: https://github.com/noctalia-dev/noctalia/blob/v5.2.0/example.toml

### A starting `00-hypeforge.toml` **[keys verified against the docs and example.toml; the file as a whole is untested]**

```toml
# hypeForge defaults for Noctalia (D-40). Javier's changes in Settings win over this file.
[shell]
telemetry_enabled    = false          # the Anonymous Startup Ping: off
setup_wizard_enabled = false          # no welcome window; hypeForge has already set things up
polkit_agent         = false          # hyprpolkitagent stays (see §8)
launch_apps_as_systemd_services = true   # works because Noctalia runs under uwsm (see §7)
app_icon_colorize    = false          # see §9 before turning on

[theme]
mode           = "dark"
source         = "custom"
custom_palette = "hypeForge-Mocha"

[wallpaper]
directory = "/usr/share/wallpapers/kognog"
fill_mode = "crop"

[wallpaper.default]
path = "/usr/share/wallpapers/kognog/Kognog OS Semi - Logo Catpuccin Mocha.png"

# One favourite per theme: picking the wallpaper also picks the palette and light/dark (§2, §4).
[[wallpaper.favorite]]
path = "/usr/share/wallpapers/kognog/Kognog OS Semi - Logo Catpuccin Mocha.png"
theme_mode = "dark"
palette_source = "custom"
custom_palette = "hypeForge-Mocha"
# … four more: Black (dark), Green (light), Gray (dark), White (light)

[bar.default]
start  = ["launcher", "workspaces", "taskbar"]
center = ["clock"]
end    = ["media", "tray", "notifications", "clipboard", "network", "bluetooth",
          "volume", "brightness", "battery", "control-center", "session"]

[lockscreen]
enabled = false                       # only if hyprlock stays (§6)

[hooks]
colors_changed = "bash ~/.config/hypeforge/bin/hypeforge-theme-sync"

[theme.templates]
enable_builtin_templates = false      # our own templates only (§3)

[theme.templates.user.hypeforge_colours]
input_path  = "$XDG_CONFIG_HOME/hypeforge/noctalia/templates/colours.lua"
output_path = "$XDG_CONFIG_HOME/hypeforge/hypr/noctalia-colours.lua"
```

---

## 2 · Themes and palettes

### The palette format **[verified: docs `theming/palette.mdx`, `theming/index.mdx`; code `src/theme/fixed_palette.cpp`]**

- Settings: `[theme] source = "custom"` and `custom_palette = "MyPalette"` load `~/.config/noctalia/palettes/MyPalette.json`. The other sources are `builtin` (Ayu, Catppuccin, Dracula, Eldritch, Gruvbox, Kanagawa, Noctalia, Nord, Rosé Pine, Tokyo-Night), `community` (downloaded from api.noctalia.dev) and `wallpaper` (colours worked out from the picture).
- A palette file has a `"dark"` block and a `"light"` block. *"If `light` is omitted, Noctalia uses the dark variant for both modes."*
- Each block has **16 colour roles** and an optional **`terminal`** block:

| Role | Used for (docs) |
|---|---|
| `mPrimary` / `mOnPrimary` | main accent: buttons, links, active states / text on it |
| `mSecondary` / `mOnSecondary` | second accent / text on it |
| `mTertiary` / `mOnTertiary` | third accent / text on it |
| `mError` / `mOnError` | errors and "danger" buttons / text on it |
| `mSurface` / `mOnSurface` | main background of the shell / main text |
| `mSurfaceVariant` / `mOnSurfaceVariant` | cards, panels, quieter backgrounds / quieter text |
| `mOutline` | borders and separators |
| `mShadow` | shadows |
| `mHover` / `mOnHover` | hover highlight / text on it |
| `terminal` | `background`, `foreground`, `cursor`, `cursorText`, `selectionBg`, `selectionFg`, `normal{black…white}`, `bright{black…white}` |

- From those 16, Noctalia works out 48 "Material" colours for templates (containers, `surface_dim`, `surface_container_low` and so on) with fixed formulas.
- **One adjustment to know about:** `mOutline` is raised to at least 3:1 contrast against `mSurface` (`ensureContrast(outlineRaw, surface, 3.0)`). Our "inactive" colours are deliberately quiet, so **Noctalia's own outlines will look a little brighter than our inactive window border**. Our window borders are not affected, because they keep reading our exact colours (§3).
- A palette file has **no wallpaper field** and no name field. The loader reads only the colour keys. **[verified: `src/theme/custom_palettes.cpp`]**

### Our five as Noctalia palettes (plan)

Five files: `palettes/hypeForge-Mocha.json`, `-Black`, `-Green`, `-Gray`, `-White`. Each file has **the same colours in both the `dark` and `light` blocks**, because each of our themes is one kind. Which kind it is gets decided by the favourite's `theme_mode` (§4): Green and White are `light`, the others `dark`. This keeps Noctalia's light/dark setting and the GNOME "prefer dark" setting truthful. Noctalia sets that GNOME setting itself from the mode (`syncGSettingsColorScheme`). **[verified]**

How our named colours map onto the 16 roles (values copied from `desktop/hypr/themes/*.lua`):

| Noctalia role | from our colour | Mocha | Black | Green | Gray | White |
|---|---|---|---|---|---|---|
| `mPrimary` | accent | `#cba6f7` | `#a3a3a3` | `#1f6e45` | `#d0d0d0` | `#1a1a1a` |
| `mOnPrimary` | btnIcon | `#1e1e2e` | `#0a0a0a` | `#ffffff` | `#262626` | `#ffffff` |
| `mSecondary` | border | `#cba6f7` | `#a3a3a3` | `#2e8b57` | `#bdbdbd` | `#3a3a3a` |
| `mOnSecondary` | btnIcon | `#1e1e2e` | `#0a0a0a` | `#ffffff` | `#262626` | `#ffffff` |
| `mTertiary` | a4 | `#89b4fa` | `#89b4fa` | `#1d4fc4` | `#89b4fa` | `#1d4fc4` |
| `mOnTertiary` | btnIcon | `#1e1e2e` | `#0a0a0a` | `#ffffff` | `#262626` | `#ffffff` |
| `mError` | red | `#f38ba8` | `#f38ba8` | `#c42440` | `#f38ba8` | `#d20f39` |
| `mOnError` | btnIcon | `#1e1e2e` | `#0a0a0a` | `#ffffff` | `#262626` | `#ffffff` |
| `mSurface` | window | `#1e1e2e` | `#0f0f0f` | `#eef7f1` | `#303030` | `#ececec` |
| `mOnSurface` | text | `#cdd6f4` | `#e4e4e4` | `#143d2a` | `#ececec` | `#1c1c1c` |
| `mSurfaceVariant` | selection | `#45475a` | `#2a2a2a` | `#c6e3d0` | `#4a4a4a` | `#c8c8c8` |
| `mOnSurfaceVariant` | subtext | `#a6adc8` | `#9a9a9a` | `#3d6650` | `#b3b3b3` | `#555555` |
| `mOutline` | inactive | `#45475a` | `#262626` | `#b3d4bf` | `#4d4d4d` | `#bdbdbd` |
| `mShadow` | (none; plain shadow) | `#000000` | `#000000` | `#7f9a88` | `#000000` | `#8a8a8a` |
| `mHover` | selection | `#45475a` | `#2a2a2a` | `#c6e3d0` | `#4a4a4a` | `#c8c8c8` |
| `mOnHover` | text | `#cdd6f4` | `#e4e4e4` | `#143d2a` | `#ececec` | `#1c1c1c` |
| `terminal` | `themes/terminal.lua` (F-12) | the hand-picked 16 per theme; cursor = accent, selection = selection | | | | |

`bar`, `barText`, `titlebar` and `green` have no role of their own. Noctalia draws its bar from `mSurface` / `mOnSurface`. Our title bars and window borders keep their exact colours through `theme.lua` (§3). The two shadow colours for the light themes are my suggestion, to be judged by eye. **[the mapping is a proposal]**

Mocha in full, as the pattern for the other four:

```json
{
  "dark": {
    "mPrimary": "#cba6f7", "mOnPrimary": "#1e1e2e",
    "mSecondary": "#cba6f7", "mOnSecondary": "#1e1e2e",
    "mTertiary": "#89b4fa", "mOnTertiary": "#1e1e2e",
    "mError": "#f38ba8", "mOnError": "#1e1e2e",
    "mSurface": "#1e1e2e", "mOnSurface": "#cdd6f4",
    "mSurfaceVariant": "#45475a", "mOnSurfaceVariant": "#a6adc8",
    "mOutline": "#45475a", "mShadow": "#000000",
    "mHover": "#45475a", "mOnHover": "#cdd6f4",
    "terminal": {
      "background": "#1e1e2e", "foreground": "#cdd6f4",
      "cursor": "#cba6f7", "cursorText": "#1e1e2e",
      "selectionBg": "#45475a", "selectionFg": "#cdd6f4",
      "normal": { "black": "#45475a", "red": "#f38ba8", "green": "#a6e3a1", "yellow": "#f9e2af",
                  "blue": "#89b4fa", "magenta": "#f5c2e7", "cyan": "#94e2d5", "white": "#bac2de" },
      "bright": { "black": "#585b70", "red": "#f38ba8", "green": "#a6e3a1", "yellow": "#f9e2af",
                  "blue": "#89b4fa", "magenta": "#f5c2e7", "cyan": "#94e2d5", "white": "#a6adc8" }
    }
  },
  "light": { "…": "the same values again" }
}
```

A small generator script in `scripts/` should write all five from `themes/*.lua` and `themes/terminal.lua`, so the colours have one source. **[proposal]**

### "Palette from a picture" **[verified: docs + `src/cli/schema_theme.h`]**

- **Inside the shell:** `[theme] source = "wallpaper"` works out a palette from the current wallpaper every time it changes. `wallpaper_scheme` picks the method: `m3-tonal-spot`, `m3-content`, `m3-fruit-salad`, `m3-rainbow`, `m3-monochrome`, `vibrant`, `faithful`, `soft`, `dysfunctional`, `muted`.
- **On the command line:** `noctalia theme <image>` is a stand-alone tool. It prints the worked-out colours as JSON (`--scheme`, `--dark`/`--light`/`--both`, `-o file`). It can also fill template files (`-r in:out`, `-c templates.toml`) without the shell running. This is handy for testing our templates.
- The source code also has a "save this picture-made palette as a custom palette" path (`suggestCustomPaletteName`), so a colour set Javier likes can be kept. **[verified that it exists; not tried]**

---

## 3 · Templates: colouring other apps

### How it works **[verified: docs `theming/app-theming.mdx`, `theming/templates.mdx`; `assets/templates/builtin.toml`]**

On every palette change, Noctalia fills each enabled template and writes the result. It only rewrites a file when the content really changed. Then it runs the template's `post_hook` command (in the background by default, at most four at a time). Blanks look like `{{ colors.primary.default.hex }}`: the colour name, then the mode (`default`, `dark`, `light`), then the format (`hex`, `hex_stripped`, `rgb`, `rgba`, `hsl`…). Filters such as `| set_alpha 0.9`, `| darken 10` and `| blend: "#ff0000", 0.5` change a colour. Loops and ifs use `<* for … *>` / `<* if … *>`. `{{ mode }}` is `dark` or `light`. The 22 terminal colours are `colors.terminal_background`, `colors.terminal_normal_red` and so on.

### What ships in the box

- **Built-in (inside the package, 21):** Alacritty, btop, cava, Emacs, foot, Ghostty, **GTK 3**, **GTK 4**, Helix, KDE colours, **kitty**, labwc, Niri, **Hyprland**, Mango, **Qt (qt5ct/qt6ct)**, Scroll, Sway, Umbriel, Starship, WezTerm. They are switched on one by one with `builtin_ids = [...]`; the default is none. **[verified]**
- **Community (downloaded from api.noctalia.dev, 72 today):** includes `hyprtoolkit`, `walker`, `pywalfox` (Firefox), `brave`, `ungoogled-chromium`, `zen-browser`, `rofi`, `fuzzel`, `papirus-icons`, `telegram`, `vscode`, `steam`… There is **no hyprlock template** anywhere. There is no plain "chromium" template. **[verified: catalog fetched today]**
- Firefox works through the Pywalfox browser add-on plus Noctalia's own `firefox-theme` helper, with no Python needed. **[verified: docs]**

### Why we should **not** switch on the built-in Hyprland, GTK and Alacritty templates **[verified behaviour; the conflicts are inferred]**

- **Hyprland:** its `apply.sh` detects the Lua format, writes `~/.config/hypr/noctalia.lua`, and **appends** `require("noctalia").apply_theme()` to `~/.config/hypr/hyprland.lua`. On hypeForge `~/.config/hypr` points into our portable folder, so it would edit our master `hyprland.lua`. It also sets border colours, which fights `theme.lua`. (It had a separate bug with group-bar gradients, #4111, now closed.)
- **GTK 3/4:** its `apply.sh` appends `@import url("noctalia.css");` to `gtk.css` and sets `adw-gtk3`/`adw-gtk3-dark`. Our `theme.lua` writes the whole `gtk.css` on every change, so the two would take turns overwriting each other.
- **Alacritty:** it writes `~/.config/alacritty/themes/noctalia.toml` and edits the `import` list in `alacritty.toml`. We already have `hypeforge-current.toml`, which alacrittyForge understands (F-12).
- **Qt** (qt5ct/qt6ct colour files) and **kitty** are harmless to switch on later if we want them.

### The plan: one switch drives everything **[pieces verified; assembled result inferred]**

```
Javier picks a theme (Noctalia Settings → Colours, a starred wallpaper, or Win + Alt + T)
   │
   ▼
Noctalia repaints itself (bar, panels, launcher, notifications, OSD, its lock screen)
   │ fills our template  →  ~/.config/hypeforge/hypr/noctalia-colours.lua
   │ then fires the colors_changed hook (after the templates, in the background)
   ▼
hypeforge-theme-sync
   1. asks:  noctalia msg color-scheme-get      → "custom hypeForge-Green" (or "builtin Nord")
   2. writes ~/.config/hypeforge/theme          → green   (or "noctalia" for a non-hypeForge palette)
   3. for our five: if the wallpaper is not the matching one, noctalia msg wallpaper-set <it>
   4. hyprctl reload
   ▼
theme.lua (already exists): borders, hyprbars title bars, Alacritty, GTK, hyprtoolkit apps, hyprlock colours
   - for our five: our exact colours from themes/<id>.lua (as today)
   - for any other palette: colours taken from noctalia-colours.lua
```

Why this shape:

- **Verified facts behind it:** `colors_changed` fires *"after the theme palette is resolved and terminal templates are updated"*, and only when the palette really changed (`if (paletteChanged) m_hookManager.fire(HookKind::ColorsChanged)`). Hooks run through `process::runAsync`, so calling `noctalia msg` from inside the hook cannot freeze Noctalia. Step 3 re-applies a favourite whose palette is already active, so the palette does not change and the hook does not fire again. There is no loop.
- `theme.lua` keeps our hand-picked colours exact (including the quiet inactive border that Noctalia would brighten), and Noctalia's own palettes still colour the whole desktop.
- `theme.lua` **drops** its Waybar, mako, Walker and hyprpaper writers. Noctalia replaces those programs. `theme.lua` may also drop its `gsettings color-scheme` line, since Noctalia sets that itself (keeping it is harmless).

The template (`~/.config/hypeforge/noctalia/templates/colours.lua`), which gives `theme.lua` the colours of any palette:

```lua
-- Generated by Noctalia from the active palette (D-40). Do not edit.
return {
    mode      = "{{ mode }}",
    accent    = "{{ colors.primary.default.hex }}",
    border    = "{{ colors.secondary.default.hex }}",
    inactive  = "{{ colors.surface_variant.default.hex }}",
    titlebar  = "{{ colors.surface_dim.default.hex }}",
    bar       = "{{ colors.surface_container_low.default.hex }}",
    barText   = "{{ colors.on_surface.default.hex }}",
    window    = "{{ colors.surface.default.hex }}",
    text      = "{{ colors.on_surface.default.hex }}",
    subtext   = "{{ colors.on_surface_variant.default.hex }}",
    selection = "{{ colors.surface_variant.default.hex }}",
    green     = "{{ colors.terminal_normal_green.default.hex }}",
    red       = "{{ colors.error.default.hex }}",
    btnIcon   = "{{ colors.on_primary.default.hex }}",
    a1 = "{{ colors.terminal_normal_red.default.hex }}",  a2 = "{{ colors.terminal_normal_green.default.hex }}",
    a3 = "{{ colors.terminal_normal_yellow.default.hex }}", a4 = "{{ colors.terminal_normal_blue.default.hex }}",
    a5 = "{{ colors.terminal_normal_magenta.default.hex }}", a6 = "{{ colors.terminal_normal_cyan.default.hex }}",
    terminal = { bg = "{{ colors.terminal_background.default.hex }}", fg = "{{ colors.terminal_foreground.default.hex }}",
        normal = { "{{ colors.terminal_normal_black.default.hex }}", "{{ colors.terminal_normal_red.default.hex }}" --[[ …six more ]] },
        bright = { "{{ colors.terminal_bright_black.default.hex }}", "{{ colors.terminal_bright_red.default.hex }}" --[[ …six more ]] } },
}
```

(The real file lists all 16 terminal colours, in the order black, red, green, yellow, blue, magenta, cyan, white.) The choice of `surface_dim` for title bars and `surface_container_low` for the bar is a guess, to be judged in the VM. **[inferred]**

A second, simpler option exists: template-only, no hook. `theme.lua` would always use `noctalia-colours.lua`, even for our five. It is less code, but our quiet inactive border and exact title-bar colours would be replaced by Noctalia's worked-out ones. **[inferred]**

**Can a theme change run a command?** Yes, in three ways: a template's `pre_hook` / `post_hook`, the `[hooks]` table (`colors_changed`, `theme_mode_changed`, `wallpaper_changed`, and also `started`, `session_locked`, `logging_out`…), and `noctalia msg templates-apply` to re-fill everything by hand. **[verified]**

---

## 4 · Wallpaper **[verified: docs `desktop/wallpaper.mdx`, code `src/shell/wallpaper/wallpaper.cpp`]**

- **Why the picker was empty in the VM:** `[wallpaper] directory` is empty by default, which means *"the standard XDG Pictures directory … falls back to `~/Pictures`"*. Set `directory = "/usr/share/wallpapers/kognog"` and all eleven KognogOS pictures will show (the folder is readable by everyone; checked on this desktop). There are also `directory_light` / `directory_dark` (one folder per mode) and per-monitor folders.
- **Wallpaper that follows the theme:** use `[[wallpaper.favorite]]` entries with `palette_source`, `custom_palette` and `theme_mode`. The code confirms that **`noctalia msg wallpaper-set <path>` applies a favourite's stored palette** (`applyResolvedWallpaper` → `wallpaperFavorite(path)` → `applyWallpaperSelection(…, favorite, …)`). Clicking the starred tile in the picker does the same. Starred wallpapers sit at the top of the picker grid. The other direction (palette picked in Settings → the right wallpaper) is step 3 of the hook in §3.
- Note: favourites declared in our file become part of the list. Starring or un-starring in the picker writes the whole list to `settings.toml`, which then wins. That is expected behaviour, not a bug. **[inferred from the load order]**
- Also available: automatic rotation (`[wallpaper.automation]`), transitions (fade, wipe, disc…), `color:#RRGGBB` solid colours, and a blurred copy for the lock screen.
- **Does it replace hyprpaper?** Yes. Noctalia draws the wallpaper itself (`[wallpaper] enabled = true`, the default). Running both means two programs drawing a background. Stop `hypeforge-hyprpaper.service`. (The reverse setup, where hyprpaper draws and Noctalia only reads colours, is documented in the FAQ, but we do not need it.) **[verified docs; the "two backgrounds" effect is inferred]**

---

## 5 · Taskbar (open-app icons) **[verified: docs `bar/widgets/taskbar.mdx`, `config_types.h`]**

Yes. The `taskbar` widget shows **icons of running apps; left-click focuses the window**, middle-click closes it, and right-click pins it. The focused app gets a small dot. It can also group icons by workspace. A Hyprland bug where clicking did not raise floating windows (#3263) was fixed.

It is **not in the default bar** (`start = launcher, wallpaper, workspaces`). Add it:

```toml
[bar.default]
start = ["launcher", "workspaces", "taskbar"]

[widget.taskbar]
pinned = []                 # desktop-file names to keep even when closed, e.g. ["firefox"]
show_window_title = false   # true shows the title next to each icon, like Plasma
only_active_workspace = false
```

Minimise does not exist on hypeForge (D-34), so a click always focuses. **[inferred]**

---

## 6 · Lock screen and idle **[verified: docs `configuration/shell.mdx` § Lock screen, `services/idle.mdx`, FAQ]**

- **Noctalia's lock screen** is on by default (`[lockscreen] enabled = true`). It answers `loginctl lock-session` (*"`loginctl lock-session` uses the same path when Noctalia is running"*) and locks before suspend (`lock_before_suspend = true`). It is coloured by the palette automatically and can show a blurred picture of the desktop. Passwords go through the `login` PAM service.
- **Noctalia's idle actions** (`[idle.behavior.*]`: `lock`, `screen_off`, `suspend`…) are **all off by default**.
- **The clash:** our `hypridle.conf` runs `hyprlock` when the "lock" signal arrives. Noctalia would react to the same signal. Two lock screens would compete, and only one program can hold the screen lock. **[inferred]**
- **Option A, keep hyprlock:** set `[lockscreen] enabled = false`. The docs say this means *"no `ext-session-lock-v1` engagement, no logind lock/unlock integration, and lock actions are hidden or no-op."* Keep hypridle and hyprlock exactly as today, and `theme.lua` keeps writing `hyprlock-colours.conf`. Noctalia's "Lock" buttons disappear. Its session menu still offers log out, reboot and shut down. **[verified]**
- **Option B, go all-Noctalia:** drop hyprlock and hypridle and add

```toml
[idle.behavior.lock]
timeout = 600
action  = "lock"
enabled = true

[idle.behavior.screen-off]
timeout = 660
action  = "screen_off"
enabled = true
```

  This means fewer programs and no lock-screen template to maintain. Win + L becomes `noctalia msg session lock`. Javier said hyprlock *"looks amazing"*, so this is his call.

---

## 7 · Starting it, and the keys

### Starting under uwsm **[verified: docs `running-the-shell.mdx`, `PACKAGING.md`, `configuration/shell.mdx`]**

- Noctalia **ships no systemd unit** (*"No systemd user unit is shipped"*). The docs suggest Hyprland's start event: `hl.on("hyprland.start", function() hl.exec_cmd("noctalia") end)`.
- `noctalia --daemon` (`-d`) *"returns after the shell has initialized"*. It exists for compositors that wait for start commands to finish. The shipped `.desktop` file uses it.
- **Recommended for hypeForge (D-25 pattern):** our own `hypeforge-noctalia.service`, shaped like the other `hypeforge-*.service` files, with `ExecStart=/usr/bin/noctalia` (no `-d`, so systemd watches it) and `Restart=on-failure`. Two things make this fit well:
  - `launch_apps_as_systemd_services = true`: apps started from the launcher, taskbar or dock each get their own `app-<name>@….service`, so restarting Noctalia never closes Javier's apps. The docs say this *"only applies when Noctalia itself runs under the systemd user manager – as a user unit, or started through uwsm"*. That is our case. **[verified]**
  - If Noctalia is started from Hyprland instead, use `launch_apps_custom_command = "uwsm app -- $CMD"`. The two settings are either/or. **[verified]**
- The services it replaces (mako, hyprpaper, swayosd, walker/elephant, hyprlauncher, nm-applet, blueman) must be **stopped and disabled**, not only paused. Otherwise they come back at the next login. **[inferred]**

### IPC commands for keys (`noctalia msg <command>`) **[verified: docs `ipc/*.mdx`]**

| Group | Commands |
|---|---|
| Panels | `panel-toggle launcher [text]`, `panel-toggle clipboard`, `panel-toggle session`, `panel-toggle wallpaper`, `panel-toggle control-center [tab]`, `panel-open <id>`, `panel-close` |
| Settings | `settings-toggle [section]`, `settings-open [section]`, `config-reload`, `status` |
| Session | `session lock`, `session lock-and-suspend`, `session suspend`, `session logout`, `session reboot`, `session shutdown` |
| Windows | `window-switcher` (Alt + Tab style, with window previews on Hyprland) |
| Theme | `theme-mode-get`, `theme-mode-toggle`, `theme-mode-set dark\|light\|auto`, `color-scheme-get`, `color-scheme-set custom hypeForge-Green`, `templates-apply` |
| Wallpaper | `wallpaper-set <path>`, `wallpaper-get`, `wallpaper-next`, `wallpaper-previous`, `wallpaper-random` |
| Sound | `volume-up [n]`, `volume-down [n]`, `volume-mute`, `volume-set 65`, `mic-mute`, `mic-volume-up/down` |
| Screen | `brightness-up/down`, `nightlight-toggle`, `dpms-on/off`, `osd-toggle` |
| Media | `media toggle`, `media next`, `media previous` |
| Notifications | `notification-dnd-toggle`, `notification-clear-history`, `notification-show "text"` |
| Clipboard | `clipboard-clear`, `clipboard-copy <text>`, `clipboard-text` |
| Screenshots | `screenshot-region`, `screenshot-fullscreen`, `screenshot-annotate`, `annotate` |
| Radios, power | `wifi-toggle`, `bluetooth-toggle`, `caffeine-toggle`, `power-cycle` |
| Bar, dock | `bar-toggle`, `dock-toggle` |

The full list is `noctalia msg --help`.

### Our keys, rewritten (`hyprland.lua`) **[commands verified; the bindings are a proposal]**

```lua
local nm = function(c) return hl.dsp.exec_cmd("noctalia msg " .. c) end
hl.bind("SUPER + SUPER_L", nm("panel-toggle launcher"), { release = true, description = "Launcher" })
hl.bind("SUPER + V",       nm("panel-toggle clipboard"), { description = "Clipboard history" })
hl.bind("CTRL + ALT + DELETE", nm("panel-toggle session"), { description = "Power menu" })
hl.bind("SUPER + L", hl.dsp.exec_cmd("loginctl lock-session"), { description = "Lock the screen" }) -- works for A and B
hl.bind("SUPER + S",     nm("panel-toggle control-center"), { description = "Control centre" })
hl.bind("SUPER + comma", nm("settings-toggle"),              { description = "Noctalia settings" })
hl.bind("XF86AudioRaiseVolume", nm("volume-up"),   { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", nm("volume-down"), { locked = true, repeating = true })
hl.bind("XF86AudioMute",        nm("volume-mute"), { locked = true })
hl.bind("XF86AudioMicMute",     nm("mic-mute"),    { locked = true })
hl.bind("XF86AudioPlay",        nm("media toggle"),   { locked = true })
hl.bind("XF86AudioNext",        nm("media next"),     { locked = true })
hl.bind("XF86AudioPrev",        nm("media previous"), { locked = true })
hl.bind("XF86MonBrightnessUp",   nm("brightness-up"),   { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", nm("brightness-down"), { locked = true, repeating = true })
-- Win + Alt + T: next theme = the next KognogOS wallpaper favourite (it brings its palette)
hl.bind("SUPER + ALT + T", hl.dsp.exec_cmd("bash ~/.config/hypeforge/bin/hypeforge-theme-next"), { description = "Next theme" })
```

Optional: Alt + Tab → `nm("window-switcher")` (today it lives in `snap.lua`), and Print → `nm("screenshot-region")` if Noctalia's screenshot editor replaces grim, slurp and satty. The docs also recommend a floating window rule for Noctalia's Settings window (`class = "dev.noctalia.Noctalia"`) and a blur layer rule. Both are in `compositor-settings/hyprland.mdx`, already written in Lua.

---

## 8 · What it replaces **[verified: `PACKAGING.md` § Session conflicts, service docs, code]**

| Today | Covered? | Notes |
|---|---|---|
| **Waybar** | Yes | the bar and its widgets |
| **mako** | Yes | *"On non-Plasma sessions Noctalia provides and registers `org.freedesktop.Notifications`"* (the standard notification service name). `[notification] enable_daemon = false` gives the name back. **Do not run mako next to it**: whichever starts first gets the notifications. |
| **SwayOSD** | Yes | pop-ups for volume, mic, brightness, caps lock, keyboard layout, Wi-Fi/Bluetooth, media, DND… (`[osd]`) |
| **hyprpaper** | Yes | §4 |
| **Walker / elephant / hyprlauncher** | Yes | launcher with category buttons, calculator, emoji, window search, custom lists (`[shell.launcher.dmenu.entry.*]`), clipboard history (saved encrypted; needs a keyring, otherwise kept for the current session only), and the session menu |
| **nm-applet** | Yes | Control Centre → Network: Wi-Fi with passwords, Enterprise Wi-Fi, VPN status, mobile. Noctalia registers its own NetworkManager password agent, so nm-applet should go to avoid double password prompts. **[agent verified; the double prompt is inferred]** |
| **Blueman** | Yes | Control Centre → Bluetooth: power, pairing, connect. It has its own Bluetooth pairing agent. |
| **udiskie** | **No** | the source has no removable-drive feature (no "udisks" anywhere outside a plugin settings page). Keep udiskie. |
| **Polkit agent** (password pop-up for admin actions) | Has one, **off by default** | `polkit_agent = false`: *"Keep disabled if another desktop agent handles auth prompts."* Only one agent may run. Keep hyprpolkitagent (D-39, Hyprland's own apps), or switch it on and remove hyprpolkitagent to get a palette-coloured prompt. |
| System tray host | Yes | it registers `org.kde.StatusNotifierWatcher`, so Waybar must not run as a tray host at the same time |

---

## 9 · Tray icons in one colour **[verified: docs `bar/widgets/tray.mdx`, `configuration/shell.mdx` § App icon colorization]**

- `[shell] app_icon_colorize = true` (plus `app_icon_color = "on_surface"` or any role) **tints full-colour app icons to the palette**. Icons are turned grey, balanced for contrast, then tinted. Icons that are already one-colour ("symbolic") follow the tray widget's own `color` / `icon_color`.
- **The catch:** this switch is **global**. It also tints the taskbar, dock, launcher results and active-window icons. There is no per-app or tray-only switch in 5.2.0 (the old per-widget keys were removed).
- Tray-only ways out: (1) hide udiskie's icon (`[widget.tray] hidden = ["udiskie"]`) or put it in the tray drawer (`drawer = true`); (2) make udiskie use one-colour ("symbolic") icons through its own `icon_names` setting in `~/.config/udiskie/config.yml`. **[(1) verified; (2) inferred from udiskie's documentation as I remember it, to be checked]**
- Open bug to watch: #4657 "Tray icon right-click does not show menu" (5.2.0, NVIDIA, on the driftwm compositor, not Hyprland). **[verified]**

---

## 10 · Privacy: the Anonymous Startup Ping **[verified: code + docs]**

- Setting: **`[shell] telemetry_enabled`**. Default in the code: `bool telemetryEnabled = false;` (`src/config/config_types.h:1140`). The welcome window's switch starts from that value (off).
- When on, it sends one message at each start to `api.noctalia.dev/ping` with: a random ID (`~/.local/state/noctalia/instance.id`), the version, the compositor, the OS name, RAM, screen sizes and UI scale.
- Other outgoing traffic to know about: community palettes and templates (api.noctalia.dev), weather and location if switched on, exchange rates for the launcher's calculator (`shell.launcher.fetch_exchange_rates`, **on** by default), and the public-IP lookup (`external_ip_enabled`, off). **`[shell] offline_mode = true` blocks all of it.**
- Ship: `telemetry_enabled = false` and `setup_wizard_enabled = false`. Consider `[shell.launcher] fetch_exchange_rates = false`. **[proposal]**

---

## 11 · Known issues (searched 2026-09-30) **[verified: GitHub issues]**

- **Hyprland Lua settings:** no open bug. Noctalia's docs are written for the Lua format (`hl.on`, `hl.bind`, `hl.layer_rule`), and its Hyprland template detects Lua itself. Closed and fixed: #3263 (taskbar click did not raise floating windows), #3563 and #3599 (workspace display did not update), #4111 (group-bar gradients). **Nothing found that names Hyprland 0.56 specifically.**
- **NVIDIA:** #3603 open (system monitor keeps a laptop's NVIDIA card awake; desktops are not affected), #3890 open (freeze when switching workspace from a full-screen game, on Niri), #4657 open (tray right-click, above). The VM does not use NVIDIA. The real desktop does, so test full-screen games there before shipping. **[inferred risk]**
- **General:** #4099 open (Noctalia's main loop sometimes stalls about 20 s; one reporter links it to the weather feature), #4194 open (the launcher is slow the first time after login). #4400 (closed) was a memory limit on the reporter's own system, not a Noctalia leak.
- **nog finding, already logged in TODO:** `nog install noctalia` failed in the VM because the package lists were not refreshed first.

---

## Commands run (all read-only)

```
git clone --depth 50 https://github.com/noctalia-dev/noctalia  (scratchpad) ; git checkout v5.2.0
pacman -Si noctalia                       # extra/noctalia 5.2.0-1, built 2026-09-28
grep / sed / Read over docs/user/**, example.toml, PACKAGING.md, assets/templates/**, src/**
curl https://api.noctalia.dev/templates   # community template catalogue (72 entries)
gh issue list -R noctalia-dev/noctalia --search "hyprland lua" | "nvidia" | "hyprland 0.56" | "uwsm"
gh issue view 4400 2001 4657 3890 4099 3603 4111
ls /usr/share/wallpapers/kognog/          # 11 pictures, readable by everyone
```

## Sources

- Docs: https://docs.noctalia.dev/noctalia/configuration/ · …/theming/ · …/theming/palette/ · …/theming/app-theming/ · …/theming/templates/ · …/desktop/wallpaper/ · …/bar/widgets/taskbar/ · …/bar/widgets/tray/ · …/configuration/shell/ · …/services/idle/ · …/services/notifications/ · …/automation/hooks/ · …/ipc/ · …/compositor-settings/hyprland/ · …/getting-started/running-the-shell/ · …/getting-started/faq/
- Source at v5.2.0: https://github.com/noctalia-dev/noctalia/tree/v5.2.0. Files read: `example.toml`, `PACKAGING.md`, `assets/templates/builtin.toml`, `assets/templates/{hyprland,gtk,alacritty}/*`, `assets/dev.noctalia.Noctalia.desktop`, `src/config/config_types.h`, `src/config/config_overrides.cpp`, `src/config/config_service.cpp`, `src/theme/fixed_palette.cpp`, `src/theme/custom_palettes.cpp`, `src/shell/wallpaper/wallpaper.cpp`, `src/app/application_services.cpp`, `src/app/application_ipc.cpp`, `src/hooks/hook_manager.*`, `src/system/desktop_entry_launch.cpp`, `src/system/telemetry_service.cpp`, `src/shell/setup_wizard/setup_wizard_panel.cpp`, `src/cli/schema_theme.h`
- Community templates: https://api.noctalia.dev/templates
- Issues: #3263 #3563 #3599 #3603 #3890 #4099 #4111 #4194 #4400 #4657
- hypeForge files read: `desktop/hypr/{theme.lua,hyprland.lua,titlebars.lua,hypridle.conf,hyprlock.conf}`, `desktop/hypr/themes/*.lua`, `desktop/systemd/*.service`, `scripts/desktop/install-into.sh`, `docs/DECISIONS.md` (D-40), `TODO.md`

*Noctalia is MIT-licensed. Thanks to the Noctalia team for a shell that documents itself this well; the template and palette formats above are theirs.*
