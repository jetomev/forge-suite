# 03 · The theme system and the colour science

*Research helper 3 of 5 for the look program (D-67, `docs/look-program.md`), 2026-10-10. Read-only research: nothing outside `docs/research/look-2026-10/` was changed, nothing was installed, nothing restarted.*

**What is here:** where the Kognog colours really come from; a list of named colour *roles* that every theme fills in; the readability rules each theme must pass; a generator that builds all 23 themes and checks them; and how each program on the desktop (Sway, Waybar, mako, fuzzel, gtklock, GTK apps, Alacritty, Midnight Commander, pointer and icons) would get its colours from one theme file.

**The files**

| File | What it is |
|---|---|
| `palette/generate.py` | the generator: Python, standard library only. `python3 generate.py` rebuilds everything; `--check` fails if any rule fails |
| `palette/palettes.toml` | all 23 themes in one machine-readable file (69 colours each, plus brand colours and names) |
| `palette/themes/<slug>/theme.toml` | the same, one file per theme: the format proposed for the theme app |
| `palette/contrast-report.md` | every rule, every theme, measured: 1,794 required pairs, the design checks, and every adjustment the generator made |
| `palette/swatches.html` | the 23 themes side by side, each drawn as a tiny desktop (bar, two windows, buttons, status colours, terminal line). One file, opens offline |
| `palette/render/{dark-purple,purple,white}/` | example files for each program, made from a theme, to prove the mapping works |

---

## 1 · The Kognog colours: what the files actually say

**Finding: the KognogOS emblem has no purple in it.** It is blue and orange. The purple that people see as "the Kognog colour" is the operating system's own accent colour, set in `kognog/config/os-release` as `ANSI_COLOR="38;2;203;166;247"`, which is `#cba6f7` (Catppuccin Mocha's *mauve*). That same colour is used by the Plymouth boot ring, kognogos.org, the shell prompt, and today's hypeForge accent.

Sampled with Pillow from `hypeforge/assets/kognogos-emblem.png` (k-means over the solid pixels; the same values appear in `kognog/logo/logo.png`):

| Name in the theme files | Hex | OKLCH (lightness · colourfulness · hue) | Share of the emblem | Where |
|---|---|---|---|---|
| `emblem_blue` | `#0363ef` | 0.544 · 0.225 · 260° | 35 % | the top layers |
| `emblem_blue_deep` | `#0048b6` | 0.440 · 0.185 · 261° | 22 % | their shaded side |
| `emblem_orange` | `#d9400e` | 0.591 · 0.197 · 36° | 28 % | the bottom layer |
| `emblem_orange_deep` | `#b93205` | 0.521 · 0.178 · 36° | 14 % | its shaded side |
| `wordmark_gray` | `#969696` | 0.673 · 0 | — | the "Kognog OS" letters in `logo.png` |
| `kognog_mauve` | `#cba6f7` | 0.787 · 0.119 · 305° | — | os-release, boot ring, website, prompt |

How the generator uses them (Claude's proposal, **for Javier to confirm**):
- **The Purple family is the Kognog theme.** Purple and Dark Purple use mauve `#cba6f7` exactly as their accent. Dark Purple is tuned to land on today's look: base `#1e1e2e`, shade `#262637`, accent `#cba6f7`, the same as Catppuccin Mocha. Switching to it changes almost nothing you can see.
- **The grays (White, Light Gray) and Light Blue use the emblem blue `#0363ef` exactly** as their accent. It already passes the contrast rules on light surfaces, so the logo's main colour gets a home too. On dark grays it is lightened to `#8ab9ff`, the same hue.
- **The emblem orange is not an accent anywhere.** Orange is too close to "warning" and "danger", so it stays a brand colour for the logo. Every theme carries the six brand colours in a `[brand]` table that is **never adjusted and never used for text**.

## 2 · Two kinds of file: a theme is colours, a style is shapes

This follows decision H-1 in the look program: **any of the 23 colour themes works on any of the 6 styles.**

| | A **theme** (23) | A **style** (6) |
|---|---|---|
| Holds | colours only | corners, border widths, gaps, shadow size and blur, bar height, fonts, which bar/launcher/dock, layout |
| Example | Dark Purple, Light Green | Windows 11, Mac OS 9, KDE |
| File | `themes/<slug>/theme.toml` | `styles/<slug>/style.toml` |
| Made by | `generate.py` (never edited by hand) | written by hand, one per style |

The style names *which colour role* goes where ("the focused border uses the accent"). It never names a hex value. The theme fills in the roles. That way a style cannot break a theme's contrast, and a theme cannot change a style's shape.

## 3 · The colour roles (the token list)

A *token* is a named job, like "the main text colour" or "a raised panel". Each theme gives every token a colour. Programs ask for tokens, never for "purple". There are **69 colour tokens** in 12 groups, plus `[brand]` and `[names]`.

### Surfaces: the layers, from deepest to highest

| Token | Job | Today (Mocha) |
|---|---|---|
| `surface.sunken` | wells, the desktop behind windows, inputs that sit "inside" | crust `#11111b` |
| `surface.bar` | the bar, title bars, side panels | mantle `#181825` |
| `surface.base` | window content, the terminal background | base `#1e1e2e` |
| `surface.raised` | cards, pop-up lists, notifications, the bar's shaded areas | the shade `#262637` |
| `surface.overlay` | menus and dialogs above everything | surface0 `#313244` |
| `surface.hover` | a hovered button, a highlighted row | surface1 `#45475a` |

### Text

| Token | Job | Rule |
|---|---|---|
| `text.primary` | everything people read | 7:1 on base and raised |
| `text.secondary` | menu titles, prompts, details | 4.5:1 everywhere |
| `text.muted` | hints, placeholders, disabled text only, **never body text** | 3:1 |
| `accent.on` | words on an accent fill (a button, the active workspace) | 4.5:1 |

### Accent: the colour that pops

| Token | Job |
|---|---|
| `accent.base` | buttons, the active workspace, the focused window's border, the cursor |
| `accent.hover` / `accent.pressed` | the same button when the mouse is over it / held down |
| `accent.text` | the accent used as words: links, the letters you typed in a list (always passes 4.5:1) |
| `accent.ring` | the keyboard focus ring |

### Lines, windows, bar, selection, status

| Group | Tokens |
|---|---|
| `border` | `subtle` (a soft line between panels, decorative), `strong` (a line that must be seen: an input box, a button outline; 3:1) |
| `window` | `focused` (= accent), `unfocused`, `urgent` (Sway's `client.*` colours) |
| `bar` | `bg`, `shade` (the left, centre and right areas), `fg`, `fg_dim`, `hover`, `active_bg`, `active_fg` |
| `selection` | `bg`, `fg`: the highlighted row in a list, selected text |
| `status` | `success`, `warning`, `danger`, `info`, each with `on_<name>` for text on a filled chip |

### Effects, categories, terminal

| Group | Tokens |
|---|---|
| `effects` | `shadow` + `shadow_opacity` (black at 55 % on dark themes; a tinted dark at 18 % on light ones), `blur_tint` + `blur_opacity` (the frosted-glass colour, for SwayFX and the mock-ups) |
| `cat` | eight category colours: red, orange, yellow, green, teal, blue, purple, pink. For workspaces in the Multicolor themes, file types in Midnight Commander, meters, charts. All 3:1 on the base and the bar |
| `term` | the terminal: `bg`, `fg`, `cursor`, `cursor_text`, `selection_*`, and the 16 standard colours (`black` … `bright_white`) tuned to that theme's background |

### Names (things that are not colours)

`[names]` holds `gtk_theme` (`adw-gtk3` or `adw-gtk3-dark`), `color_scheme` (`prefer-light`/`prefer-dark`, for the settings portal), `gnome_accent` (the nearest of the nine named accents libadwaita apps understand), `cursor` (installed `catppuccin-mocha-<colour>-cursors`: blue, mauve, green, pink, red, dark, light, all confirmed in `/usr/share/icons`), `icons` (candy-icons), `icons_symbolic` (Papirus-Dark/Light) and `wallpaper_set`.

## 4 · Shapes: the style file

Shapes are owned by the style. Proposed `styles/<slug>/style.toml`:

```toml
[meta]
name = "Windows 11"
slug = "windows-11"
needs = ["swayfx"]          # or [] when plain Sway can draw it

[shape]                     # pixels
radius_window   = 8         # window corners (SwayFX: corner_radius)
radius_control  = 4         # buttons, inputs, list rows
radius_popup    = 8         # pop-up lists, notifications, menus
border_window   = 1         # window border width (Sway: default_border pixel N)
border_control  = 1
gap_inner       = 10        # between windows (Sway: gaps inner)
gap_outer       = 0
bar_height      = 48
shadow_size     = 24        # blur radius (SwayFX: shadow_blur_radius)
shadow_offset_y = 8
blur            = true      # frosted glass (SwayFX: blur enable)
blur_radius     = 8

[roles]                     # which colour token each part wears (never a hex)
window_focused  = "accent.base"     # today's look uses "text.primary" (a white border)
bar_background  = "surface.bar"
bar_areas       = "bar.shade"
popup_background = "surface.raised"

[fonts]
ui = "Noto Sans"
ui_size = 10.5
mono = "JetBrainsMono Nerd Font"
```

Starting values per style are the bar/launcher and compositor helpers' job (reports 01 and 02). Rough guesses: Windows 11 rounds windows at 8 px and controls at 4; Mac OS 9 is square with 1 px bevels; modern macOS about 10 px; KDE Breeze small rounding; COSMIC offers square / slightly round / round. **Shadows, blur and rounded window corners need SwayFX.** Plain Sway draws square borders only.

## 5 · The readability rules

### Two ways to measure

- **WCAG 2.2 contrast ratio**, the legal and industry standard. It compares how much light two colours give off, from 1:1 (same) to 21:1 (black on white). **4.5:1** is the minimum for reading text, **3:1** for icons, borders and the focus mark (WCAG 1.4.11 and 2.4.13), and **7:1** is the stricter "AAA" level we use for the main text.
- **APCA**, the newer score planned for WCAG 3 (Andrew Somers / Myndex). It follows how eyes really see. It is stricter for light text on dark backgrounds, where WCAG is too generous, and it reads like a grade: **Lc 75** body text, **60** readable text, **45** large text or hints, **30** icons and lines. The generator implements APCA-W3 0.0.98G-4g. It reproduces the reference values exactly (`#888` on white = 63.06; black on white = 106.04; white on black = −107.88), and the OKLab maths reproduces the published `#ff0000` = 0.628 · 0.2577 · 29.23°.

**A pair has to pass both.** WCAG keeps us inside the standard; APCA catches the dark-theme cases WCAG lets through.

### The pairs that must pass (the contract)

| Foreground | On | WCAG | APCA Lc |
|---|---|---|---|
| `text.primary` | base, raised | 7 | 75 |
| `text.primary` | overlay, sunken, hover | 4.5 | 60 |
| `text.secondary` | base, raised, overlay, sunken | 4.5 | 60 |
| `text.muted` (hints only) | base, raised | 3 | 45 |
| `accent.text` | base, raised, overlay | 4.5 | 60 |
| `accent.base` | base, raised, overlay, bar | 3 | 30 |
| `accent.on` | accent, its hover and pressed | 4.5 | 60 |
| `accent.ring`, `border.strong` | base, raised | 3 | 30 |
| `window.focused` | base **and the unfocused border** | 3 | 30 |
| `window.urgent` | base | 3 | 30 |
| `bar.fg` | bar / shade, hover | 7 / 4.5 | 75 / 60 |
| `bar.fg_dim` | bar, shade | 4.5 | 60 |
| `bar.active_fg` on `bar.active_bg`; `bar.active_bg` on bar and shade | — | 4.5; 3 | 60; 30 |
| `selection.fg` on `selection.bg` | — | 4.5 | 60 |
| each `status.*` on base and raised; `status.on_*` on its fill | — | 4.5 | 60 |
| `term.fg` / the 6 normal colours / the 6 bright ones | term.bg | 7 / 4.5 / 3 | 75 / 60 / 45 |
| each `cat.*` | base, bar | 3 | 30 |

78 pairs per theme. The focused-vs-unfocused rule matters most for a tiling desktop: the border is the *only* sign of which window has the keyboard.

### "Make things pop": four design rules on top

Passing contrast makes things readable. It does not make them *pop*. The generator also checks:

1. **A visible ladder.** Neighbouring surfaces (sunken → base → raised → overlay) differ by at least 0.02 in OKLCH lightness, so a pop-up reads as a separate layer: connected, not fused.
2. **A colour budget.** The accent carries at least 1.5× the colourfulness of the surfaces. The eye goes to the most colourful thing, so that has to be the thing you can click.
3. **No look-alikes.** Each status colour stays at least ΔE 0.08 from the accent (ΔE = colour distance; 0.02 is "just noticeable"), and the urgent border at least 0.15 from the focused one. "Error" must never look like "selected".
4. **A press that shows.** The pressed accent is at least ΔE 0.03 from the normal one.

### The mid-gray dead zone (why "Gray" is darker than you might expect)

Around OKLCH lightness 0.55 to 0.65, **neither black nor white text reaches 7:1.** A true middle gray cannot carry readable text. So the seven "mid" themes (Gray, Blue, Purple, Green, Pink, Red, Multicolor) sit at lightness about 0.40 with light text: rich, colourful surfaces, clearly lighter than the Dark ones (0.24) and nowhere near the Light ones (0.92). This is a physical limit, not a taste choice.

## 6 · The generator

### How a theme is made

Each theme is a one-line recipe in `THEMES` (in `generate.py`): its **tone** (white, light, mid, dark, black), the **hue and colourfulness of the surface tint**, and its **accent** (a pinned brand hex, or a lightness · colourfulness · hue). Everything is computed in **OKLCH**, where equal steps of lightness *look* equal (credit: Björn Ottosson's OKLab), so one ladder works for every hue. Colours a screen cannot show lose colourfulness, never lightness or hue.

Then, in order: surfaces → text → accent (and the text on it, hover, pressed) → borders → status colours → window borders → bar → selection → effects → category colours → terminal. After each step the generator **measures the pairs on the final hex values** (what ships). When a pair fails, it **nudges**: it moves the lightness 0.005 at a time away from the background until the pair passes. If the text reaches pure white or black first, it moves the background instead. When a status colour sits too close to the accent (red "danger" in a red theme), it turns the hue first and changes lightness only if hue alone cannot do it. Every move is written into the report.

### The result (run on 2026-10-10)

```
23 themes · 1794 required pairs · 1794 pass · 0 fail · 204 nudges
```

No design-rule warnings remain. The TOML files are read back with Python's own `tomllib` on every run. The generated Sway and fuzzel files pass their programs' own config checks (`sway -C`, `fuzzel --check-config`), and a deliberately broken file fails both, so the checks really are checking.

| Theme | Tone | Bar | Base | Raised | Text | Accent | Urgent | Pointer |
|---|---|---|---|---|---|---|---|---|
| White | white | `#ededed` | `#f1f1f1` | `#f8f8f8` | `#1f1f1f` | `#0363ef` | `#af3c40` | dark |
| Light Gray | light | `#d2d2d2` | `#dedede` | `#e6e6e6` | `#1f1f1f` | `#0363ef` | `#ad3a3e` | dark |
| Gray | mid | `#313131` | `#4a4a4a` | `#525252` | `#f3f3f3` | `#95c0ff` | `#ffbcb8` | dark |
| Dark Gray | dark | `#1a1a1a` | `#202020` | `#282828` | `#d7d7d7` | `#8ab9ff` | `#ffa09c` | dark |
| Black | black | `#000000` | `#040404` | `#101010` | `#d7d7d7` | `#7fb3ff` | `#ffa09c` | light |
| Dark Blue | dark | `#0f192c` | `#172031` | `#1f283a` | `#ccd8ed` | `#8ab9ff` | `#ffa09c` | blue |
| Blue | mid | `#1b2d4f` | `#354666` | `#3d4e6e` | `#e1ecff` | `#8bdeff` | `#ffb9b6` | blue |
| Light Blue | light | `#cdddee` | `#dae8f7` | `#e2f0ff` | `#17202a` | `#0363ef` | `#af3c40` | blue |
| Light Purple | light | `#ddd7eb` | `#e8e3f5` | `#f1ebfd` | `#211d28` | `#793cbb` | `#af3c40` | mauve |
| **Purple** | mid | `#322352` | `#493e69` | `#514672` | `#ece7ff` | **`#cba6f7`** | `#ffbbaa` | mauve |
| **Dark Purple** | dark | `#181729` | **`#1e1e2e`** | **`#262637`** | `#d5d6e9` | **`#cba6f7`** | `#ffa28c` | mauve |
| Light Green | light | `#cee0d1` | `#dbebde` | `#e3f4e6` | `#18221a` | `#007835` | `#af3c40` | green |
| Green | mid | `#013820` | `#28503a` | `#305842` | `#dcf6e6` | `#a5eb7c` | `#ffbcb8` | green |
| Dark Green | dark | `#0b1e13` | `#14241a` | `#1c2d22` | `#caddd0` | `#7bd77f` | `#ffa09c` | green |
| Light Pink | light | `#ebd3dd` | `#f4e0e8` | `#fde8f1` | `#281b21` | `#bf2f77` | `#aa4600` | pink |
| Pink | mid | `#442032` | `#5c3b4a` | `#644352` | `#ffe2ee` | `#ffb9d9` | `#fec348` | pink |
| Dark Pink | dark | `#26131c` | `#2b1a22` | `#34222a` | `#e6d1da` | `#fc9ac9` | `#faab3f` | pink |
| Light Red | light | `#edd4d1` | `#f7e0de` | `#ffe9e6` | `#291b1a` | `#be2323` | `#9a418c` | red |
| Red | mid | `#4c1d1b` | `#643935` | `#6d413d` | `#ffe4e1` | `#ffac96` | `#dbd350` | red |
| Dark Red | dark | `#281311` | `#2d1a19` | `#362221` | `#e9d1cf` | `#ff9089` | `#debb32` | red |
| Light Multicolor | light | `#dbdbdb` | `#e6e6e6` | `#eeeeee` | `#1f1f1f` | `#793cbb` | `#af3c40` | dark |
| Multicolor | mid | `#262626` | `#3e3e3e` | `#464646` | `#dfdfdf` | `#cba6f7` | `#ffb6a4` | dark |
| Dark Multicolor | dark | `#1a1a1a` | `#202020` | `#282828` | `#d7d7d7` | `#cba6f7` | `#ffa28c` | dark |

**Multicolor** = a neutral gray base, the Kognog mauve as the main accent, and `multi = true`. That flag tells the style to paint each workspace number, and optionally each workspace's window border, from the eight `cat` colours (see the swatch sheet).

### Trade-offs the generator found (for Javier's eye)

- **Red themes:** red is the accent, so "danger" turns orange-red and the urgent border turns **yellow** (Red, Dark Red) or **purple** (Light Red). **Pink themes:** the urgent border turns **amber**. The alternative is a danger red that looks like the accent. The generator chose "different". Javier may prefer one fixed urgent colour for every theme, which is one line to change.
- **The White theme's window background is `#f1f1f1`, not pure white.** Pure white is kept for the top layer (menus, dialogs) so the layers still show. This is how Windows 11 light works. Pure-white windows would flatten the ladder.
- **Today's focused border is white (the text colour).** The themes use the accent so the focused window pops in colour. A style can choose `window_focused = "text.primary"` to keep today's look.
- **Text is a little brighter than Mocha's** (`#d5d6e9` vs `#cdd6f4`): a touch less blue, same reading strength.
- **The workspace numbers in the Multicolor sample** use the bar colour on a category colour (3:1, fine for bold numbers). The real build should use each colour's own "on" text.

## 7 · How each program gets its colours

**Proposal:** `hypeforge-theme apply <style> <theme>` (Phase 4) writes small generated files into **`~/.config/hypeforge/theme/`**. Each program's own config `include`s or `@import`s its file **once**, so switching a theme rewrites only the generated files and reloads. The hand-written configs keep their layout, comments and Javier's decisions. Every mechanism below was checked against the version installed on this machine.

| Program (version here) | Generated file | How the config takes it | Reload after a switch |
|---|---|---|---|
| **Sway** 1.12 | `sway-colors.conf`: the `$hf_*` names (the same ones `sway/config` uses today), all four `client.*` lines, `client.background`, the pointer | `include ~/.config/hypeforge/theme/sway-colors.conf` near the top (variables must exist before use); the `client.*` lines move out of `sway/config` | `swaymsg reload` |
| **Waybar** 0.15 | `colors.css`: every token as `@define-color hf_<group>_<name>` (e.g. `@hf_surface_bar`, `@hf_bar_shade`) | `@import url("../../hypeforge/theme/colors.css");` as the first lines of `style.css`, next to the favourites import that already works this way; the hard-coded `#262637` and `#f38ba8` become `@hf_bar_shade` and `@hf_status_danger` | `pkill -SIGUSR2 -x waybar` (restyle without restarting) |
| **mako** 1.11 | `mako-colors.conf`: colours, plus the low/critical sections | `include=~/.config/hypeforge/theme/mako-colors.conf` (`man 5 mako`: absolute or `~/` path) | `makoctl reload` |
| **fuzzel** 1.15 | `fuzzel-colors.ini`: the whole `[colors]` section (8-digit hex, with alpha) | `include=…` in `[main]`; the included file keeps its own section header (`man 5 fuzzel.ini`) | none: read at every launch |
| **gtklock** 4.0 | the same `colors.css` | `@import url("file:///home/…/.config/hypeforge/theme/colors.css");` at the top of `style.css` (GTK 3 CSS) | none: read at every lock |
| **GTK 3 apps** (adw-gtk3 6.5) | `gtk.css`: libadwaita's named colours (`window_bg_color`, `accent_bg_color`, `card_bg_color`, `destructive_color`…), the same names `themes/gtk/gtk.css` sets today | copied to `~/.config/gtk-3.0/gtk.css`; `gsettings … gtk-theme` from `names.gtk_theme` | restart the app |
| **GTK 4 / libadwaita** 1.9.4 | the same `gtk.css`, plus `:root { --window-bg-color: …; }` variables | `~/.config/gtk-4.0/gtk.css`. libadwaita 1.9 reads the `--…-color` variables (confirmed in the library); the old names are still accepted. `gsettings … color-scheme` from `names.color_scheme`, `accent-color` from `names.gnome_accent` | restart the app |
| **Alacritty** 0.17 | `alacritty-colors.toml`: primary, cursor, selection, 16 colours | `[general] import = ["~/.config/hypeforge/theme/alacritty-colors.toml"]`, the same way it imports `KognogOS-theme.toml` today; alacrittyForge stays the editor | live, Alacritty watches its config (that it also watches imported files is not yet tested here: check on the bench) |
| **Midnight Commander** 4.8.33 | `mc-aliases.ini`: only the `[aliases]` block | the skin `themes/mc/kognogos-mocha.ini` already names every colour through aliases (`Base`, `Mauve`, `Peach`…), so the apply step writes a full skin = this block + the fixed rest | next start of mc |
| **wiremix**, nmtui, bluetui | — | wiremix: a `[themes.kognogos]` table written from tokens. nmtui only takes the terminal's basic colour names. bluetui uses Alacritty's colours | next start |
| **Pointer** | `names.cursor` | `seat * xcursor_theme` (in `sway-colors.conf`), gsettings `cursor-theme`, `settings.ini` | Sway reload; apps on restart |
| **Icons** | `names.icons` (candy-icons, colourful, one set for all) and `names.icons_symbolic` (Papirus-Dark/Light, installed) | gsettings `icon-theme`, fuzzel `icon-theme=` (style-owned) | app restart |
| **Wallpaper / lock picture** | `names.wallpaper_set` → the wallpaper helper's folder (report 05) | `swaybg`; gtklock `background.jpg` (blurred once, as today) | Sway reload |

Rules for the apply step (from hypeForge's own rules): back up first and offer an undo; write every file *then* reload, never half; names from `[names]` must exist on the machine or the step stops and says which; `docs/THEME.md` remains the human blueprint and gains a "theme tokens" column when this is built.

**What the theme app needs** (forgekit / Forge Suite / hypeForge Settings): read `palettes.toml` (or the `themes/` folder) to list themes with a preview from `surface.base`, `surface.raised`, `accent.base` and `text.primary`; run the apply step; show the theme's contrast result from the report. It never edits a theme file. A custom theme is a new recipe run through the generator, so it gets checked like the others.

## 8 · Open questions for Javier

1. **Neutral themes' accent:** the emblem blue (proposed) or the Kognog mauve everywhere?
2. **Focused window border:** the accent (proposed, pops) or white like today?
3. **Urgent in red and pink themes:** "different colour" (as generated: yellow / amber / purple) or one fixed urgent colour across all themes?
4. **Emblem orange:** brand-only (proposed), or an accent for a 24th theme?

## Commands run and sources

- Read: `hypeforge/docs/THEME.md`, `docs/look-program.md`, `docs/DECISIONS.md` (D-46), `sway/config`, `sway/waybar/style.css`, `sway/fuzzel/fuzzel.ini`, `sway/mako/config`, `sway/gtklock/style.css`, `themes/gtk/{gtk.css,settings.ini}`, `themes/mc/kognogos-mocha.ini`, `themes/wiremix/wiremix.toml`, `~/.config/alacritty/themes/KognogOS-theme.toml`, `kognog/config/os-release`, `homelab/www/index.html` (CSS variables), both banner SVGs.
- Sampled with Pillow 12.3: `assets/kognogos-emblem.png`, `kognog/logo/logo.png`, two wallpapers.
- Checked on this machine: `pacman -Q` (versions above); `man 5 mako`, `man 5 fuzzel.ini`, `man 5 sway` (include support); `strings /usr/lib/libadwaita-1.so.0` (CSS variables); `/usr/share/icons` (cursor and icon themes); `sway -C` and `fuzzel --check-config` on generated and deliberately broken files; a headless Chrome screenshot of `swatches.html` (into the session scratch folder).
- Colour science: Björn Ottosson, "A perceptual color space for image processing" (OKLab, 2020); W3C WCAG 2.2 (1.4.3, 1.4.6, 1.4.11, 2.4.13); APCA-W3 0.0.98G-4g (Myndex); CSS Color 4 gamut mapping (the idea of reducing chroma at fixed lightness). Catppuccin (catppuccin.com) for today's palette. Thank you to all of them.
