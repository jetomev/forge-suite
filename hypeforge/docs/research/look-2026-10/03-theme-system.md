# 03 · The theme system and the colour science

*Research helper 3 of 5 for the look program (D-67, `docs/look-program.md`), 2026-10-10. Read-only research: nothing outside `docs/research/look-2026-10/` was changed, nothing was installed, nothing restarted.*

> **v2 (2026-10-10, after Javier's review):** every theme is now built the **60-30-10** way: a neutral foundation, a strong band in the theme colour, a harmony pop. There are two new themes: **KognogOS Mocha** (the default) and **Ember**. The *why* (design rules, harmonies, sources, before/after) is in **[03b-colour-design.md](03b-colour-design.md)**. This page is the format, the roles and the contract.

**What is here:** where the Kognog colours really come from; a list of named colour *roles* that every theme fills in; the readability rules each theme must pass; a generator that builds all 25 themes and checks them; and how each program on the desktop (Sway, Waybar, mako, fuzzel, gtklock, GTK apps, Alacritty, Midnight Commander, pointer and icons) would get its colours from one theme file.

**The files**

| File | What it is |
|---|---|
| `palette/generate.py` | the generator: Python, standard library only. `python3 generate.py` rebuilds everything; `--check` fails if any rule fails |
| `palette/palettes.toml` | all 25 themes in one machine-readable file (78 colours each in 13 groups, plus brand colours and names); `meta.order` lists KognogOS Mocha first |
| `palette/themes/<slug>/theme.toml` | the same, one file per theme: the format proposed for the theme app |
| `palette/contrast-report.md` | every rule, every theme, measured: 2,124 required pairs, the 60-30-10 design checks, Mocha's deviations from Catppuccin, and every adjustment the generator made |
| `palette/swatches.html` | the 25 themes side by side; each card shows its 60-30-10 split and a tiny desktop (the band on the bar, a panel header, the side panel and the selected row; the pop on toggles, typed letters, a badge and buttons). One file, opens offline |
| `palette/render/{kognogos-mocha,purple,white,ember}/` | example files for each program, made from a theme, to prove the mapping works |
| `03b-colour-design.md` | the design research behind v2 |

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

How v2 uses them (Javier's answers, 2026-10-10):
- **Today's colours are their own theme: KognogOS Mocha**, faithful Catppuccin Mocha with mauve `#cba6f7` as its main accent. It is the default and first in the list. Javier: the Purple theme "is actually our KognogOS catppuccin mocha color combinations". The Purple family is now real purples.
- **The gray themes' pop is the emblem blue** `#0363ef` (light) and the same hue lightened on dark grays (`#9dc2ff`). White and Black stay high-contrast grayscale.
- **The emblem orange is brand-only, except in Ember**, where it is the band (`#d43a03`, the emblem orange one small step darker so white text passes 4.5:1).
- Every theme carries the six brand colours in a `[brand]` table that is **never adjusted and never used for text**.

## 2 · Two kinds of file: a theme is colours, a style is shapes

This follows decision H-1 in the look program: **any of the 25 colour themes works on any of the 6 styles.**

| | A **theme** (25) | A **style** (6) |
|---|---|---|
| Holds | colours only | corners, border widths, gaps, shadow size and blur, bar height, fonts, which bar/launcher/dock, layout |
| Example | KognogOS Mocha, Ember, Light Green | Windows 11, Mac OS 9, KDE |
| File | `themes/<slug>/theme.toml` | `styles/<slug>/style.toml` |
| Made by | `generate.py` (never edited by hand) | written by hand, one per style |

The style names *which colour role* goes where ("the focused border uses the accent"). It never names a hex value. The theme fills in the roles. That way a style cannot break a theme's contrast, and a theme cannot change a style's shape.

## 3 · The colour roles (the token list)

A *token* is a named job, like "the main text colour" or "a raised panel". Each theme gives every token a colour. Programs ask for tokens, never for "purple". There are **78 colour tokens** in 13 groups, plus `[brand]` and `[names]`. v2 kept every v1 name and added two groups, `band` and `pop`. The surfaces, the text and the borders are the **foundation** (neutral).

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

### Band: the theme colour at full strength (~30 %)

| Token | Job |
|---|---|
| `band.base` | the bar's areas, panel headers and title strips, the selected row |
| `band.strong` | the bar behind its areas, a pressed band item (deeper, 7:1 with its text) |
| `band.on` | words on the band (white, near-black or cream, whichever passes) |
| `band.soft` | quiet band: side panels (Start's list of places, a settings sidebar), a selection that keeps normal text |
| `band.text` | the band as a line or words on the foundation: **the focused window border**, section titles (4.5:1) |

### Pop: the harmony colour for small important things (~10 %)

| Token | Job |
|---|---|
| `pop.base` | toggles that are on, sliders, badges, buttons |
| `pop.on` | words on the pop |
| `pop.text` | the pop as words: the letters you typed in a list, links (4.5:1) |

### Accent = the pop

`accent.base`, `accent.on`, `accent.text` and `accent.ring` are **the pop**, so every program that already asks for "the accent" (GTK's `accent_bg_color`, fuzzel's `match`, buttons) gets it with no change. `accent.hover` and `accent.pressed` are its two states.

### Who wears what

| Part of the desktop | Token | Layer |
|---|---|---|
| The bar (behind) | `bar.bg` | band.strong (Ember and White: the foundation) |
| The bar's areas (emblem, workspaces, apps, clock) | `bar.shade` | band.base |
| Text on the bar | `bar.fg`, `bar.fg_dim` | band.on |
| The active workspace | `bar.active_bg` / `_fg` | an inverted chip: band.on with band-coloured number. Multicolor: its own category colour |
| The bell's dot, the clipboard's "new" mark | `bar.pop` | pop, lifted to stand out on the band |
| Focused window border | `window.focused` | band.text |
| Unfocused border | `window.unfocused` | border.subtle (foundation) |
| Urgent border | `window.urgent` | status.danger, moved off red in red and pink themes |
| Panel header, title strip | `band.base` / `band.on` | band |
| Side panel | `band.soft` | band, quiet |
| Selected row (lists, the launcher) | `selection.bg` / `.fg` | band.base / band.on |
| Windows, pop-up lists, notifications, terminal | `surface.*`, `term.bg` | foundation |
| Buttons, toggles that are on, sliders | `accent.base` / `accent.on` | pop |
| Links, the letters you typed | `accent.text` | pop |
| Badges, counters | `pop.base` / `pop.on` | pop |
| Keyboard focus ring | `accent.ring` | pop |

### Lines, windows, bar, selection, status

| Group | Tokens |
|---|---|
| `border` | `subtle` (a soft line between panels, decorative), `strong` (a line that must be seen: an input box, a button outline; 3:1) |
| `window` | `focused` (= band.text), `unfocused`, `urgent` (Sway's `client.*` colours) |
| `bar` | `bg`, `shade` (the left, centre and right areas), `fg`, `fg_dim`, `hover`, `active_bg`, `active_fg`, `pop` (the bell's dot); the bar wears the band |
| `selection` | `bg`, `fg`: the highlighted row in a list, selected text (= the band) |
| `status` | `success`, `warning`, `danger`, `info`, each with `on_<name>` for text on a filled chip |

### Effects, categories, terminal

| Group | Tokens |
|---|---|
| `effects` | `shadow` + `shadow_opacity` (black at 55 % on dark themes; a tinted dark at 18 % on light ones), `blur_tint` + `blur_opacity` (the frosted-glass colour, for SwayFX and the mock-ups) |
| `cat` | eight category colours: red, orange, yellow, green, teal, blue, purple, pink. For workspaces in the Multicolor themes, file types in Midnight Commander, meters, charts. All 3:1 on the base and the bar (in Multicolor also on the bar's areas, where the numbers sit) |
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
window_focused  = "band.text"       # the theme's colour (Javier, Q-5); "text.primary" = a white border
bar_background  = "bar.bg"
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
| `text.primary` | band.soft | 4.5 | 60 |
| `band.on` | band.base / band.strong | 4.5 / 7 | 60 / 75 |
| `band.text` | base, raised | 4.5 | 60 |
| `pop.text` (= accent.text) | base, raised, overlay | 4.5 | 60 |
| `pop.base` (= accent.base) | base, raised, overlay | 3 | 30 |
| `pop.on` on the pop; `accent.on` on its hover and pressed | — | 4.5 | 60 |
| `bar.pop` | bar, its areas | 3 | 30 |
| `accent.ring`, `border.strong` | base, raised | 3 | 30 |
| `window.focused` | base **and the unfocused border** | 3 | 30 |
| `window.urgent` | base | 3 | 30 |
| `bar.fg` | bar / shade, hover | 7 / 4.5 | 75 / 60 |
| `bar.fg_dim` | bar, shade | 4.5 | 60 |
| `bar.active_fg` on `bar.active_bg`; `bar.active_bg` on bar and shade | — | 4.5; 3 | 60; 30 |
| `selection.fg` on `selection.bg` | — | 4.5 | 60 |
| each `status.*` on base and raised; `status.on_*` on its fill | — | 4.5 | 60 |
| `term.fg` / the 6 normal colours / the 6 bright ones | term.bg | 7 / 4.5 / 3 | 75 / 60 / 45 |
| each `cat.*` | base, bar (Multicolor: also the bar's areas) | 3 | 30 |

84 pairs per theme, 92 for Multicolor. **One rule moved in v2:** "the accent on the bar" became "`bar.pop` on the bar". The bar is now the band, and the pop that sits on it (the bell's dot) has its own lifted shade. The accent itself is still checked on every surface. The focused-vs-unfocused rule matters most for a tiling desktop: the border is the *only* sign of which window has the keyboard.

### "Make things pop": the 60-30-10 design checks on top

Passing contrast makes things readable. It does not make them *pop*. The generator also checks (reasons and sources in 03b):

1. **A neutral foundation.** Its most colourful level stays at chroma ≤ 0.012 (a whisper of the hue). Neighbouring levels differ by ΔL ≥ 0.02, so a pop-up reads as a separate layer.
2. **Band vs foundation: connected, not fused.** ΔL ≥ 0.10, and in coloured families ΔC ≥ 0.06.
3. **Pop vs band: two colours, not two shades.** ΔE ≥ 0.15 (ΔE = colour distance; 0.02 is "just noticeable").
4. **No look-alikes.** Each status colour stays ΔE ≥ 0.08 from the pop and the band line. The urgent border stays ΔE ≥ 0.15 from the focused one, so "error" never looks like "selected".
5. **A press that shows.** The pressed accent is ΔE ≥ 0.03 from the normal one.
6. **Colour share.** On a typical screen (60 % foundation, 30 % band, 10 % pop by area), where the colour actually lives. A coloured theme whose foundation carries more than 25 % of it reads monotone. v1's Blue: 56 %. v2's Blue: 9 %.

### The mid-gray dead zone (why "Gray" is darker than you might expect)

Around OKLCH lightness 0.55 to 0.65, **neither black nor white text reaches 7:1.** A true middle gray cannot carry readable text. So the seven middle themes (Gray, Blue, Purple, Green, Pink, Red, Multicolor) put their foundation at **graphite, lightness ≈ 0.30**, with light text ("middle to darker", Javier). Their band sits at ≈ 0.47, the brightest a band can be and still carry white text at 4.5:1. The dark themes' foundation is charcoal ≈ 0.185; the light ones are off-white ≈ 0.955. This is a physical limit, not a taste choice.

## 6 · The generator

### How a theme is made

Each theme is a one-line recipe in `THEMES` (in `generate.py`): its **tone** (white, light, mid, dark, black), its **band** (hue and colourfulness, or a pinned brand hex as in Ember), and its **pop** (a harmony family from `POP`, a per-theme harmony, or a pinned hex). KognogOS Mocha is not generated. It is Catppuccin's palette placed by Catppuccin's style guide (03b, section 5). Everything is computed in **OKLCH**, where equal steps of lightness *look* equal (credit: Björn Ottosson's OKLab), so one ladder works for every hue. Colours a screen cannot show lose colourfulness, never lightness or hue.

Then, in order: foundation → text → band (and the text on it) → pop (and the text on it, hover, pressed) → borders → status colours → window borders → bar → selection → effects → category colours → terminal. After each step the generator **measures the pairs on the final hex values** (what ships). When a pair fails, it **nudges**: it moves the lightness 0.005 at a time away from the background until the pair passes. If the text reaches pure white or black first, it moves the background instead. When a status colour sits too close to the pop or the band (red "danger" in a red theme), it turns the hue first. When the pop sits too close to the band, it keeps its hue and changes lightness first, so gold stays gold. When a colour sits between two backgrounds (a category colour on a white window and a deep bar), it searches both ways for the smallest move. Every move is written into the report.

### The result (run on 2026-10-10)

```
25 themes · 2124 required pairs · 2124 pass · 0 fail · 233 nudges
```

(v1: 23 themes · 1,794 pairs, all passing. `--check` exits 0.)

No design-check flags remain. KognogOS Mocha carries one note: it is faithful Catppuccin, so its foundation keeps Mocha's tint and its band is its pane stack, with 5 tiny deviations listed in the report. The TOML files are read back with Python's own `tomllib` on every run. The generated Sway and fuzzel files pass their programs' own config checks (`sway -C`, `fuzzel --check-config`), and a deliberately broken file fails both, so the checks really are checking.

| Theme | Tone | Foundation (window) | Band / strong | Text on band | Pop | Focused border | Urgent | Pointer |
|---|---|---|---|---|---|---|---|---|
| **KognogOS Mocha** | dark | `#1e1e2e` | `#313244` / `#181825` | `#cdd6f4` | `#cba6f7` Catppuccin's many accents | `#b4befe` | `#f9e2af` | mauve |
| White | white · hc | `#f1f1f1` | `#cecece` / `#cccccc` | `#141414` | `#222222` gray | `#2e2e2e` | `#af3c40` | dark |
| Light Gray | light | `#dfdfdf` | `#717171` / `#262626` | `#fafafa` | `#0363ef` emblem blue | `#5d5d5d` | `#ad3a3e` | dark |
| Gray | mid | `#2e2e2e` | `#5b5b5b` / `#424242` | `#fafafa` | `#9dc2ff` emblem blue | `#bebebe` | `#fbc044` | dark |
| Dark Gray | dark | `#131313` | `#3d3d3d` / `#2b2b2b` | `#fafafa` | `#9dc2ff` emblem blue | `#b7b7b7` | `#faab3f` | dark |
| Black | black · hc | `#040404` | `#262626` / `#1b1b1b` | `#fafafa` | `#e4e4e4` gray | `#d7d7d7` | `#ffa65e` | light |
| Ember | dark | `#161110` | `#d43a03` / `#a02900` | `#fff8f7` | `#f7e6c3` cream | `#ff987c` | `#ea9cf7` | peach |
| Light Blue | light | `#edf0f6` | `#276ed2` / `#002356` | `#f7faff` | `#b65400` orange | `#0b58bb` | `#a23d7b` | blue |
| Blue | mid | `#2b2e32` | `#0555b7` / `#003e8b` | `#f7faff` | `#ffae33` amber | `#95c0ff` | `#ffb0ca` | blue |
| Dark Blue | dark | `#101316` | `#003981` / `#00285f` | `#f7faff` | `#ffae33` amber | `#8ab9ff` | `#ff9abd` | blue |
| Light Purple | light | `#f1eff5` | `#8650c7` / `#35005e` | `#fbf9ff` | `#00835e` mint | `#7239b0` | `#af3c40` | mauve |
| Purple | mid | `#2e2d31` | `#6e3aa8` / `#551c8b` | `#fbf9ff` | `#61dbac` mint | `#cfafff` | `#ffb6a4` | mauve |
| Dark Purple | dark | `#131216` | `#4d1e7c` / `#3b0267` | `#fbf9ff` | `#61dbac` mint | `#c7a2ff` | `#ffa09c` | mauve |
| Light Green | light | `#edf2ed` | `#17843f` / `#003011` | `#f6fcf7` | `#c3337a` raspberry | `#007131` | `#aa4600` | green |
| Green | mid | `#2b2f2c` | `#006e30` / `#005121` | `#f6fcf7` | `#edb836` gold | `#7cd591` | `#ffb2bd` | green |
| Dark Green | dark | `#101411` | `#004b1e` / `#003614` | `#f6fcf7` | `#edb836` gold | `#7ccd8e` | `#ff9dac` | green |
| Light Pink | light | `#f5eef1` | `#b73c7c` / `#4b002c` | `#fff8fb` | `#00817c` teal | `#9f2367` | `#9c5300` | pink |
| Pink | mid | `#312c2e` | `#952c63` / `#78094b` | `#fff8fb` | `#4cd9d2` teal | `#ffa1cb` | `#ffbb69` | pink |
| Dark Pink | dark | `#161113` | `#6b1344` / `#530031` | `#fff8fb` | `#4cd9d2` teal | `#f895c2` | `#faab3f` | pink |
| Light Red | light | `#f5eeed` | `#c53634` / `#4f0005` | `#fffaee` | `#008085` deep teal | `#ac191f` | `#9a418c` | red |
| Red | mid | `#322c2c` | `#a22626` / `#81000d` | `#fffaee` | `#ffe5af` gold | `#ffa69c` | `#c5c3ff` | red |
| Dark Red | dark | `#161111` | `#76080f` / `#580006` | `#fffaee` | `#ffd16b` gold | `#ff968c` | `#ea9cf7` | red |
| Light Multicolor | light | `#f0f0f0` | `#2e2e2e` / `#1b1b1b` | `#fafafa` | `#8b57be` mauve | `#5d5d5d` | `#af3c40` | dark |
| Multicolor | mid | `#2e2e2e` | `#121212` / `#070707` | `#fafafa` | `#d3adff` mauve | `#bebebe` | `#fbc044` | dark |
| Dark Multicolor | dark | `#131313` | `#2e2e2e` / `#1f1f1f` | `#fafafa` | `#d3adff` mauve | `#b7b7b7` | `#faab3f` | dark |

**Multicolor** = a neutral foundation, a neutral-dark band, mauve for buttons and toggles, and `multi = true`. That flag tells the style to paint each workspace number from the eight `cat` colours (the active one as a filled chip in its colour), and optionally each workspace's focused border. All eight pass 3:1 on the window, the bar and the bar's areas.

### Trade-offs the generator found (for Javier's eye)

- **Light themes' pops are darker by necessity.** A pop must reach 3:1 on a white window. Dark amber turns brown and dark gold turns olive, so the light themes use a harmony that stays vivid when dark: Light Blue orange, Light Green raspberry, Light Red deep teal (03b, section 3).
- **Urgent moves away from red in red and pink themes** (Javier, Q-5): lavender (Red), purple (Dark Red, Light Red), amber (Pink, Dark Pink). Ember's urgent is purple, away from orange.
- **The pressed state of a dark theme's pop** loses some colour as well as lightness, so a click shows even when contrast leaves no room to darken.
- **The White theme's window is `#f1f1f1`, not pure white.** Pure white is kept for menus and dialogs, so the layers still show.
- **KognogOS Mocha deviates from Catppuccin in 5 colours by a hair** (each misses APCA by 0.5–5 points). Exact Catppuccin is one line per colour if Javier prefers it.

## 7 · How each program gets its colours

**Proposal:** `hypeforge-theme apply <style> <theme>` (Phase 4) writes small generated files into **`~/.config/hypeforge/theme/`**. Each program's own config `include`s or `@import`s its file **once**, so switching a theme rewrites only the generated files and reloads. The hand-written configs keep their layout, comments and Javier's decisions. Every mechanism below was checked against the version installed on this machine.

| Program (version here) | Generated file | How the config takes it | Reload after a switch |
|---|---|---|---|
| **Sway** 1.12 | `sway-colors.conf`: the `$hf_*` names (the same ones `sway/config` uses today), all four `client.*` lines, `client.background`, the pointer | `include ~/.config/hypeforge/theme/sway-colors.conf` near the top (variables must exist before use); the `client.*` lines move out of `sway/config` | `swaymsg reload` |
| **Waybar** 0.15 | `colors.css`: every token as `@define-color hf_<group>_<name>` (e.g. `@hf_surface_bar`, `@hf_bar_shade`) | `@import url("../../hypeforge/theme/colors.css");` as the first lines of `style.css`, next to the favourites import that already works this way; the hard-coded `#262637` and `#f38ba8` become `@hf_bar_shade` and `@hf_status_danger` | `pkill -SIGUSR2 -x waybar` (restyle without restarting) |
| **mako** 1.11 | `mako-colors.conf`: colours, plus the low/critical sections | `include=~/.config/hypeforge/theme/mako-colors.conf` (`man 5 mako`: absolute or `~/` path) | `makoctl reload` |
| **fuzzel** 1.15 | `fuzzel-colors.ini`: the whole `[colors]` section (8-digit hex, with alpha) | `include=…` in `[main]`; the included file keeps its own section header (`man 5 fuzzel.ini`) | none: read at every launch |
| **gtklock** 4.0 | the same `colors.css` | `@import url("file:///home/…/.config/hypeforge/theme/colors.css");` at the top of `style.css` (GTK 3 CSS) | none: read at every lock |
| **GTK 3 apps** (adw-gtk3 6.5) | `gtk.css`: libadwaita's named colours (`window_bg_color`, `accent_bg_color`, `card_bg_color`, `destructive_color`…), the same names `themes/gtk/gtk.css` sets today. v2: title bars wear `band.base` / `band.on`, side panels `band.soft`, content the foundation, buttons the pop | copied to `~/.config/gtk-3.0/gtk.css`; `gsettings … gtk-theme` from `names.gtk_theme` | restart the app |
| **GTK 4 / libadwaita** 1.9.4 | the same `gtk.css`, plus `:root { --window-bg-color: …; }` variables | `~/.config/gtk-4.0/gtk.css`. libadwaita 1.9 reads the `--…-color` variables (confirmed in the library); the old names are still accepted. `gsettings … color-scheme` from `names.color_scheme`, `accent-color` from `names.gnome_accent` | restart the app |
| **Alacritty** 0.17 | `alacritty-colors.toml`: primary, cursor, selection, 16 colours | `[general] import = ["~/.config/hypeforge/theme/alacritty-colors.toml"]`, the same way it imports `KognogOS-theme.toml` today; alacrittyForge stays the editor | live, Alacritty watches its config (that it also watches imported files is not yet tested here: check on the bench) |
| **Midnight Commander** 4.8.33 | `mc-aliases.ini`: only the `[aliases]` block | the skin `themes/mc/kognogos-mocha.ini` already names every colour through aliases (`Base`, `Mauve`, `Peach`…), so the apply step writes a full skin = this block + the fixed rest | next start of mc |
| **wiremix**, nmtui, bluetui | — | wiremix: a `[themes.kognogos]` table written from tokens. nmtui only takes the terminal's basic colour names. bluetui uses Alacritty's colours | next start |
| **Pointer** | `names.cursor` | `seat * xcursor_theme` (in `sway-colors.conf`), gsettings `cursor-theme`, `settings.ini` | Sway reload; apps on restart |
| **Icons** | `names.icons` (candy-icons, colourful, one set for all) and `names.icons_symbolic` (Papirus-Dark/Light, installed) | gsettings `icon-theme`, fuzzel `icon-theme=` (style-owned) | app restart |
| **Wallpaper / lock picture** | `names.wallpaper_set` → the wallpaper helper's folder (report 05) | `swaybg`; gtklock `background.jpg` (blurred once, as today) | Sway reload |

Rules for the apply step (from hypeForge's own rules): back up first and offer an undo; write every file *then* reload, never half; names from `[names]` must exist on the machine or the step stops and says which; `docs/THEME.md` remains the human blueprint and gains a "theme tokens" column when this is built.

**What the theme app needs** (forgekit / Forge Suite / hypeForge Settings): read `palettes.toml` (or the `themes/` folder) to list themes with a preview from `surface.base`, `surface.raised`, `accent.base` and `text.primary`; run the apply step; show the theme's contrast result from the report. It never edits a theme file. A custom theme is a new recipe run through the generator, so it gets checked like the others.

## 8 · Questions: answered and open

**Answered by Javier (Q-5, 2026-10-10):** neutral themes' pop = the emblem blue; focused border = the theme's colour; urgent moves away from red in red and pink themes; emblem orange = brand only, except as Ember's colour. White and Black stay the high-contrast grayscale themes.

**Open (v2):**
1. **The name "Ember"** (a working name).
2. **Ember's pop:** cream (as generated) or white with a gold hover?
3. **Light themes' pops** (orange, mint-green, raspberry, teal): lively enough?
4. **Mocha's 5 tiny deviations:** keep them (all rules pass) or exact Catppuccin?

## Commands run and sources

- Read: `hypeforge/docs/THEME.md`, `docs/look-program.md`, `docs/DECISIONS.md` (D-46), `sway/config`, `sway/waybar/style.css`, `sway/fuzzel/fuzzel.ini`, `sway/mako/config`, `sway/gtklock/style.css`, `themes/gtk/{gtk.css,settings.ini}`, `themes/mc/kognogos-mocha.ini`, `themes/wiremix/wiremix.toml`, `~/.config/alacritty/themes/KognogOS-theme.toml`, `kognog/config/os-release`, `homelab/www/index.html` (CSS variables), both banner SVGs.
- Sampled with Pillow 12.3: `assets/kognogos-emblem.png`, `kognog/logo/logo.png`, two wallpapers.
- v2 (2026-10-10): Catppuccin's style guide and palette.json v1.8.0, Fluent 2 Color, Material Components `Color.md` (sources in 03b); headless Chrome screenshots of the v2 swatches, reviewed and iterated by eye (pink pop on the gray themes, muddy light-theme pops, olive gold, faint Multicolor numbers, White's flat bar: all fixed); v1's colour share measured from the v1 generator.
- Checked on this machine: `pacman -Q` (versions above); `man 5 mako`, `man 5 fuzzel.ini`, `man 5 sway` (include support); `strings /usr/lib/libadwaita-1.so.0` (CSS variables); `/usr/share/icons` (cursor and icon themes); `sway -C` and `fuzzel --check-config` on generated and deliberately broken files; a headless Chrome screenshot of `swatches.html` (into the session scratch folder).
- Colour science: Björn Ottosson, "A perceptual color space for image processing" (OKLab, 2020); W3C WCAG 2.2 (1.4.3, 1.4.6, 1.4.11, 2.4.13); APCA-W3 0.0.98G-4g (Myndex); CSS Color 4 gamut mapping (the idea of reducing chroma at fixed lightness). Catppuccin (catppuccin.com) for today's palette. Thank you to all of them.
