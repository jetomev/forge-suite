# Look research 01 · What the compositor can draw — Sway 1.12 vs SwayFX 0.6

*Research helper 1 of 5, 2026-10-10. Read-only research: nothing was installed, no Sway setting
was changed, Sway was not reloaded.*

**The compositor** is the program that draws every window on the screen. On hypeForge that is
**Sway 1.12** (checked: `sway --version` → `sway version 1.12`, package `sway 1:1.12-4`, library
`wlroots0.20 0.20.2-1`). Its frames, colours, gaps and corners are what the six styles depend on.
**SwayFX** is a copy of Sway with eye candy added (rounded corners, shadows, blur, dimming,
animations). This file says what each one can draw, what SwayFX costs us, and how to try it
without risking the desktop.

Markings: **[verified]** = checked on this computer or in the source code; **[source]** = from the
linked page; **[unverified]** = reasoned or reported but not tested by us.

---

## The short answer

| Question | Answer |
|---|---|
| Can plain Sway round corners, draw shadows, blur or animate? | **No.** Square corners, solid-colour borders and title bars, gaps, per-window see-through. That is all. |
| Does SwayFX 0.6 add those? | **Yes**: rounded corners, shadows, blur, dimming of unfocused windows, effects on the bar/notifications/launcher, and (new in 0.6) animations. |
| Is SwayFX 0.6 behind our Sway? | **No.** 0.6 (5 Aug 2026) is built on **Sway 1.12.0**, the same Sway we run, on the same wlroots 0.20. [verified] |
| Does our config still work in SwayFX? | **Yes.** Every directive SwayFX documents for Sway is unchanged; SwayFX only *adds* options. [verified by diffing the manuals] |
| Do our applets (Workspaces, Placement, Rules) still talk to it? | **Yes.** Same i3-IPC socket and messages; the only addition is an extra field in `get_outputs`. One catch: it reports its version as `0.6`, not `1.12`. [verified in source] |
| Can Sway and SwayFX be installed side by side? | **Not with the ready-made packages** — `swayfx` *replaces* `sway` (same file names). Side by side needs SwayFX built into its own folder. |
| Can we test it without logging out? | **Yes**, two ways: the hidden bench (no screen, proves it starts and reads the config) and a **SwayFX in a window** on the live desktop (proves the looks). |
| Which styles need SwayFX? | Modern macOS, the Linux rice, KDE and Windows 11 need it to be faithful. **Mac OS 9 does not.** COSMIC has a square option that does not. |
| Recommendation | Build all six on plain-Sway foundations first; offer SwayFX as a **second login entry** ("Sway (hypeForge FX)"), effects in their own file, **animations off**. Details in section 6. |

---

## 1. Plain Sway 1.12 — everything it can draw

Source for this whole section: the Sway 1.12 manual, `sway(5)` and `sway-output(5)`
([sway.5.scd at tag 1.12](https://github.com/swaywm/sway/blob/1.12/sway/sway.5.scd),
[sway-output.5.scd](https://github.com/swaywm/sway/blob/1.12/sway/sway-output.5.scd)),
and `swaybg(1)` on this computer.

### 1.1 Window frames (borders)

| What | Syntax | Notes |
|---|---|---|
| Frame style for new tiled windows | `default_border normal\|none\|pixel [<n>]` | `normal` = frame **plus a title bar**; `pixel n` = frame only, `n` pixels thick. **We use `pixel 2`.** |
| Frame style for new floating windows | `default_floating_border normal\|none\|pixel [<n>]` | We use `pixel 2`. |
| Change one window | `border none\|normal\|csd\|pixel [<n>]`, `border toggle` | `csd` lets the app draw its own frame (Chrome, GTK4 apps). Works in `for_window` rules. |
| Hide frames at the screen edge | `hide_edge_borders [--i3] none\|vertical\|horizontal\|both\|smart\|smart_no_gaps` | `--i3` also hides the title bar of a tab/stack group with one window. |
| Frames only when it matters | `smart_borders on\|no_gaps\|off` | `on` = no frame when a workspace has one window. |

### 1.2 Title bars

| What | Syntax | Notes |
|---|---|---|
| Font | `font [pango:]<font>` e.g. `font pango:Inter Semi-Bold 10` | The `pango:` prefix also turns on **Pango markup** (bold, colour spans) in titles. |
| Text alignment | `title_align left\|center\|right` | **Mac OS 9 / macOS / KDE = `center`; Windows 11 = `left`.** |
| Text content | `title_format <format>` with `%title`, `%app_id`, `%class`, `%instance`, `%shell`, `%sandbox_engine`, `%sandbox_app_id` | Per window via `for_window`. With `pango:` fonts it can carry markup, e.g. `<b>%title</b>`. |
| Height / inner spacing | `titlebar_padding <horizontal> [<vertical>]` | Title bar height = font height + padding. |
| Title bar edge line | `titlebar_border_thickness <n>` | |
| Marks shown in title bar | `show_marks yes\|no` | Marks starting with `_` are never drawn. Our applets use marks — keep them `_`-prefixed or `show_marks no`. |

**What a title bar can NOT have:** buttons (close / minimise / maximise, Mac "traffic lights"),
icons, gradients, stripes (Mac OS 9 pinstripes) or images. It is one solid colour with text.
[source: `client.*` takes only solid colours — below]

### 1.3 Colours per window state — `client.*`

```
client.<class> <border> <background> <text> [<indicator> [<child_border>]]
```

Classes: `client.focused`, `client.focused_inactive` (last-focused window of a group that is not
focused), `client.focused_tab_title` (a tab/stack title that holds the focused window),
`client.unfocused`, `client.urgent` (only for old X11 apps — Wayland apps never become urgent).
`client.background` and `client.placeholder` are ignored (i3 leftovers).

- `border` / `background` / `text` — the **title bar**'s edge, fill and text.
- `child_border` — the **window frame** itself (defaults to `background`).
- `indicator` — the edge where the **next window will open** (a focus/direction hint).
- Colours are `#RRGGBB` **or `#RRGGBBAA`** — frames can be see-through, which lets a thin
  semi-transparent frame *suggest* softness without SwayFX. [source]

We set all four classes from `$hf_*` variables today (`sway/config` lines 61–64). [verified]

### 1.4 Gaps (space between windows)

| What | Syntax |
|---|---|
| Default gaps | `gaps inner\|outer\|horizontal\|vertical\|top\|right\|bottom\|left <amount>` — outer gaps add to inner; negative outer reduces them |
| Change live | `gaps inner\|outer\|… all\|current set\|plus\|minus\|toggle <amount>` |
| Per workspace | `workspace <name> gaps inner\|outer\|… <amount>` |
| Smart gaps | `smart_gaps on\|off\|toggle\|inverse_outer` — `on` = no gaps when a workspace has one window; `inverse_outer` = outer gaps only when it has exactly one |

We use `gaps inner 10`, `gaps outer 0`. [verified]

### 1.5 See-through windows, tabs and stacks

- **Per-window opacity:** `opacity [set|plus|minus] <0..1>` — usually in a rule:
  `for_window [app_id="Alacritty"] opacity 0.92`. This fades **the whole window, text included**;
  terminals that fade only their background (Alacritty's own `opacity`) look better.
- **Tabbed / stacked groups:** `layout tabbed|stacking`, `workspace_layout default|stacking|tabbed`.
  Tab titles use the same `client.*` colours, `font`, `title_align` and `titlebar_padding`;
  `client.focused_tab_title` colours the tab that holds the focus.

### 1.6 Wallpaper (swaybg)

`output <name>|* bg <file> stretch|fill|fit|center|tile [<fallback_color>]` or
`output * bg <#color> solid_color`. One wallpaper per screen is possible. We use
`output * bg "/usr/share/wallpapers/kognog/…png" fill`. [verified; swaybg(1) on this machine]

### 1.7 What plain Sway cannot do

| Effect | Plain Sway 1.12 | Closest honest substitute |
|---|---|---|
| Rounded window corners | **No** | Rounded *bar*, launcher, notifications and lock screen (those are drawn by waybar/fuzzel/mako/gtklock, which can round themselves) |
| Window shadows | **No** | Darker gap colour via wallpaper; a semi-transparent `#RRGGBBAA` frame |
| Blur behind windows/bar | **No** | Pre-blurred wallpaper (as gtklock already does, D-95); see-through without blur |
| Dimming unfocused windows | **No** (no built-in) | An applet that sets `opacity` on unfocused windows over IPC (Sway's contrib `inactive-windows-transparency.py` does this) — fades text too [unverified for us] |
| Animations | **No** | — |
| Title-bar buttons, gradients, textures | **No** | Let apps draw their own (`border csd`), or put buttons in the bar |
| Gradient frames | **No** (also not in SwayFX) | — |

Also new in 1.12 but **irrelevant to looks**: per-window screen capture, HDR10 (Vulkan renderer
only), `ext-workspace-v1`, colour management. ([Sway 1.12 release notes](https://github.com/swaywm/sway/releases/tag/1.12), 25 May 2026)

---

## 2. SwayFX 0.6 — every option

### 2.1 Version and base [verified]

| | |
|---|---|
| Release | **0.6, published 2026-08-05** ([release page](https://github.com/WillPower3309/swayfx/releases/tag/0.6); repo now lives at [wlrfx/swayfx](https://github.com/wlrfx/swayfx)) |
| Based on | **Sway 1.12.0** — release notes: *"Apart from a rebase off of sway 1.12.0, this release contains animations!"*; `meson.build` at tag 0.6: `original_version = '1.12.0'`; the chaotic-aur binary prints `swayfx version 0.6 (based on sway 1.12.0)` [verified with `strings`] |
| Libraries | wlroots 0.20 (`>=0.20.0, <0.21.0`) and **scenefx 0.5** (the effects library) |
| History | 0.4 → Sway 1.9 · 0.5/0.5.1 → Sway 1.10.1 · 0.5.2/0.5.3 → Sway 1.11 · **0.6 → Sway 1.12**. It used to trail Sway by one release; today it does not. |

### 2.2 The options (exact syntax)

All from the SwayFX 0.6 manual ([sway.5.scd at tag 0.6](https://github.com/wlrfx/swayfx/blob/0.6/sway/sway.5.scd))
and [README](https://github.com/wlrfx/swayfx/blob/master/README.md). "Per window" means it works
in a `for_window [criteria] …` rule. [verified in source: `sway/commands/*.c`]

**Corners**

| Option | Values / default | Per window? | Notes |
|---|---|---|---|
| `corner_radius <n>` | 0–99 px | **No** (global; source says `// TODO: handle setting per container`) | Rounds the window, its frame and title bar. **Applies to new windows**; it also **raises `titlebar_padding`** to at least the radius, so title bars get taller. |
| `smart_corner_radius enable\|disable` | | | Round only when there are gaps around the window (matches Windows 11's rule: no rounding when maximised/snapped). |

**Shadows**

| Option | Values / default | Per window? |
|---|---|---|
| `shadows enable\|disable` | off | **Yes** |
| `shadows_on_csd enable\|disable` | | Shadow on apps that draw their own frame — *"The shadow might not fit some windows"* |
| `shadow_blur_radius <n>` | 0–99 (manual says 100), default **20** | |
| `shadow_color <#RRGGBBAA>` | default `#0000007F` | |
| `shadow_inactive_color <#RRGGBBAA>` | default = `shadow_color` | |
| `shadow_offset <x> <y>` | px | Light from above = e.g. `0 4` |

**Blur** (frosted glass behind see-through windows)

| Option | Values / default |
|---|---|
| `blur enable\|disable` | off; **per window** too |
| `blur_xray enable\|disable` | blur shows only the wallpaper, not the windows below (README: *"You probably want to set this to `disable`"* — but see the performance note in §3) |
| `blur_passes <0–10>` | default 2 |
| `blur_radius <0–10>` | default 5 |
| `blur_noise <0–1>` | default 0.02 |
| `blur_brightness <0–2>` | default 0.9 |
| `blur_contrast <0–2>` | default 0.9 |
| `blur_saturation <0–2>` | default 1.1 |

**Blur only shows through a window that is see-through** (an `opacity` below 1, or an app with a
transparent background such as Alacritty's `opacity`). Behind an opaque window it changes
nothing. [source: how blur works; unverified visually]

**Dimming unfocused windows**

| Option | Values |
|---|---|
| `default_dim_inactive <0.0–1.0>` | default 0.0 (off) |
| `for_window [criteria] dim_inactive <0.0–1.0>` | per window only |
| `dim_inactive_colors.unfocused <#RRGGBBAA>` | e.g. `#000000FF` |
| `dim_inactive_colors.urgent <#RRGGBBAA>` | e.g. `#900000FF` |

Open report: dimming strength not always following the value ([#439](https://github.com/wlrfx/swayfx/issues/439), 0.5.2).

**Title bars, scratchpad, animations**

| Option | Notes |
|---|---|
| `titlebar_separator enable\|disable` | Remove the line between title bar and window content (a cleaner, "one piece" window — macOS / KDE / COSMIC feel) |
| `scratchpad_minimize enable\|disable` | Treat minimised windows as scratchpad; **config-time only**; README: *"we recommend keeping this setting off"* |
| `animation_duration_ms <0–5000>` | **New in 0.6.** Open/close, resize/move and workspace-switch animations. **Default 0 = off** (`config.c`: `animation_duration_ms = 0.0f`). Upstream suggests 250. [verified] |

**Effects on the bar, notifications and launcher** (`layer_effects`)

```
layer_effects "waybar" {
    blur enable;
    blur_xray enable;
    blur_ignore_transparent enable;
    shadows enable;
    corner_radius 12;
}
```

- Effects: `blur`, `blur_xray`, `blur_ignore_transparent` (blur only where the bar is not fully
  transparent — needed for "floating island" bars), `shadows`, `corner_radius <int>`, `reset`.
- Live, one effect per call: `swaymsg layer_effects "waybar" "blur enable"`.
- **Surfaces in the _bottom_ layer cannot use these effects.** Ours: waybar `"layer": "top"`,
  mako `layer=top`, fuzzel `layer=overlay` — all fine. [verified in our configs]
- Namespaces: waybar = `waybar` [source: README]; mako = `notifications`, fuzzel = `launcher`
  [unverified — the strings are in the binaries; confirm in SwayFX with
  `swaymsg -r -t get_outputs | jq '.[0].layer_shell_surfaces[].namespace'`].
- Not covered: gtklock (a lock screen, not a layer surface) and the wallpaper's own layer
  (`background`/`bottom`).

**Not in SwayFX either:** gradient frames, title-bar buttons, per-window corner radius,
window "wobble"/fancy shader effects.

### 2.3 Our config against SwayFX 0.6 [verified]

Directives used in `~/.config/sway/config` and `~/Programs/forge-suite/hypeforge/sway/config`
(both identical in directives): `bindsym`, `exec`, `set`, `output` (incl. `mode … @144Hz`,
`adaptive_sync on` in `~/.config/sway/outputs`), `include`, `gaps`, `default_border`,
`default_floating_border`, `client.*`, `seat … xcursor_theme`, `mouse_warping`, `input … xkb_*`,
`floating_modifier`, `mode`. Applets send at runtime: `for_window`, `[con_id=…] mark/unmark/focus/
move container to workspace`, `layout tabbed`, `split v`, `floating enable`, `resize set`,
`move position center`, `workspace "…" output …`.

- **Every one of these exists unchanged in SwayFX 0.6.** The diff between the Sway 1.12 manual and
  the SwayFX 0.6 manual is purely additions (the options above) plus one sentence on
  `titlebar_padding`. `sway-output(5)`, `sway-input(5)`, `sway-bar(5)` are byte-for-byte identical
  in length and content. [verified: `diff` of the `.scd` sources]
- Lost compared with plain Sway: the **Vulkan renderer** (SwayFX always uses its own OpenGL ES
  renderer), so **no HDR10**. We do not use HDR or Vulkan today (no `WLR_RENDERER` set, so plain
  Sway already uses OpenGL ES on our NVIDIA card). [verified: env; source: `server.c` calls
  `fx_renderer_create`]
- Old open report: `primary_selection` "unavailable" ([#308](https://github.com/wlrfx/swayfx/issues/308), 2024). We do not use it.

### 2.4 IPC — our applets [verified in source]

- Same socket (`SWAYSOCK`), same `i3-ipc` message format, same `RUN_COMMAND`, `GET_WORKSPACES`,
  `GET_TREE`, `GET_OUTPUTS`, `SUBSCRIBE` and `workspace`/`window` events that
  `applets/common/hfsway.py` uses. Sway's own `swaymsg` keeps working.
- `get_outputs` gains a `layer_shell_surfaces` list (extra field — harmless).
- **`get_version` reports `major: 0, minor: 6`** (`human_readable: "0.6"`, plus a new
  `sway_original_version: "1.12.0"`). Any tool that checks "Sway ≥ 1.x" would be fooled. Our
  applets never ask for the version (no `GET_VERSION` in `applets/`) [verified by grep]; waybar
  and others unverified.
- SwayFX commands work over IPC too: `swaymsg corner_radius 8`, `swaymsg shadows enable` —
  a future theme app can change effects live. (Note `corner_radius` reaches new windows only;
  existing ones keep theirs — [#93](https://github.com/wlrfx/swayfx/issues/93) comment: *"Windows
  need to be re-opened"*.)

---

## 3. NVIDIA — known issues and cost

Our card: **RTX 3060, 12 GB**, driver **nvidia-open 615.71.09**, three 2560×1440 @ 144 Hz with
adaptive sync, started `sway --unsupported-gpu` from SDDM. [verified]

**Policy.** SwayFX's bug template still says *"Proprietary graphics drivers, including nvidia,
are not supported"* ([bug_report.md](https://github.com/wlrfx/swayfx/blob/master/.github/ISSUE_TEMPLATE/bug_report.md)),
same as Sway. A maintainer: *"Swayfx generally works fine on nvidia's proprietary drivers (with the
`--unsupported-gpu` flag added)"* ([#307](https://github.com/wlrfx/swayfx/issues/307)). It inherits
Sway's explicit sync (needed by NVIDIA) since its 1.11 base ([#328](https://github.com/wlrfx/swayfx/issues/328) closed).

**Reported issues worth knowing** (from the [issue tracker](https://github.com/wlrfx/swayfx/issues), searched 2026-10-10):

| Issue | Version | Status | Matters to us? |
|---|---|---|---|
| [#565](https://github.com/wlrfx/swayfx/issues/565) With animations on and two+ screens, `move workspace to output` leaves the workspace **invisible** on the new screen | 0.6 | **open** (not NVIDIA-specific) | **Yes — high.** Our Workspaces/Placement applets move workspaces between three screens. → **animations off.** |
| [#569](https://github.com/wlrfx/swayfx/issues/569) With animations, a workspace can stay **invisible** after leaving a fullscreen one; setting `animation_duration_ms 0` at runtime makes it permanent | 0.6 | open, fix on master (`663cf66`), not released | **Yes** → animations off; never toggle them live. |
| [#566](https://github.com/wlrfx/swayfx/issues/566) Reloading the config several times **freezes** the desktop when shadows or animations are on (nouveau and nvidia-open) | 0.6 | **open** | **Yes.** Our docs tell people to `swaymsg reload`. A frozen session = leave through a text console. Must be tested before shadows ship. |
| [#574](https://github.com/wlrfx/swayfx/issues/574) / [#458](https://github.com/wlrfx/swayfx/issues/458) Firefox/Zen with `corner_radius`: odd "stars" / scroll lag (apps made of several sub-surfaces) | 0.5.3–0.6 | open | Medium. We use Chrome; Chrome's behaviour unverified. |
| [#585](https://github.com/wlrfx/swayfx/issues/585) Screen sharing breaks when a window moves workspace with blur on | 0.6 | open | Low–medium (video calls). |
| [#393](https://github.com/wlrfx/swayfx/issues/393) NVIDIA: jagged rounded corners depending on window size | 0.5 | **fixed** (June 2025) | No. |
| [#398](https://github.com/wlrfx/swayfx/issues/398) 25 fps cap in games on an NVIDIA build | 0.5 (Sway 1.10) | open, maintainer asked if still true | Unknown — test a game. |
| [#274](https://github.com/wlrfx/swayfx/issues/274) Keeps a second GPU awake | 0.3.2 | open | No (one GPU). |
| [#267](https://github.com/wlrfx/swayfx/issues/267) Blur on floating windows breaks their frames | 2024 | open | Low. |

**Performance — no published measurements found** (searched; none for SwayFX blur/shadows on
NVIDIA or multi-screen). What the source code says, plus estimates:

- SwayFX uses the **same OpenGL ES drawing path** plain Sway already uses on our card; it adds
  shader work, not a new driver path. [verified in source]
- **Blur behind tiled windows is cheap**: windows that cannot overlap use an "optimized blur" —
  the wallpaper is blurred **once per screen** and reused until it changes
  (`output.c`: `should_optimize_blur = config->blur_xray || !could_container_overlap(con)`).
  **Floating windows** (and `blur_xray disable` overlaps) get live blur every frame they change.
  [verified in source]
- Only **changed areas** are redrawn (damage tracking). An idle desktop costs almost nothing; a
  scrolling see-through terminal re-blurs just its own rectangle. [source: scenefx README debug
  options `WLR_SCENE_DEBUG_DAMAGE`]
- Estimate [unverified]: rounded corners and shadows are a light per-window shader — negligible on
  an RTX 3060. Blur at defaults (2 passes, radius 5) on 3 × 2560×1440 should be well within the
  card's means, but **fullscreen games skip compositing** (direct scanout) only when nothing is
  drawn over them — keep effects off fullscreen. Extra video memory for blur buffers: tens to a
  few hundred MB [unverified estimate]. **Measure, don't trust**: `nvidia-smi dmon` before/after,
  and watch for dropped frames at 144 Hz.

---

## 4. Packaging on Arch

| Where | Package | What we found |
|---|---|---|
| Arch official | — | **Not in Arch's repos** ([packages search](https://archlinux.org/packages/?q=swayfx) returns nothing). `extra` has **`scenefx 0.5-1`** (needed by `mangowm`, not by SwayFX). [verified] |
| chaotic-aur | **`swayfx 0.6-0`** | Shown by `nog search swayfx` as **Tier 3 — 7-day hold**. `pacman -Si`: **Provides `sway wayland-compositor`, Conflicts With `sway scenefx`**, depends on `wlroots0.20` (installed). Built 2026-08-11 by Garuda. scenefx is **built in** (no separate library to break on updates — the old pain of [scenefx #123](https://github.com/wlrfx/scenefx/issues/123)). [verified] |
| AUR | `swayfx 0.6-0` | Provides `sway`, conflicts `sway swayfx-git`. **Depends on `scenefx0.5`, a package that does not exist** (AUR and repos: 0 results; `extra` calls it `scenefx`), so it cannot be built as-is. **Flagged out-of-date 2026-10-01.** Source `sha512sums=('SKIP')`, no signature. [verified via AUR RPC + PKGBUILD] |
| AUR | `swayfx-git` | Git snapshot `r7069…`, depends `scenefx-git` (which still targets wlroots 0.19). Not for us. [verified] |

**Side by side? No, not with these packages.** The chaotic package ships the **same file paths**
as `sway`: `/usr/bin/sway`, `swaymsg`, `swaybar`, `swaynag`, `/etc/sway/config`,
`/usr/share/wayland-sessions/sway.desktop` (its session entry is even named "Sway",
`DesktopNames=sway;wlroots;swayfx`). Installing it **removes `sway`**. [verified: file list of the
downloaded package, not installed]

Three ways to offer it:

| Way | How | Sway stays the safe default? | Cost |
|---|---|---|---|
| **A. Replace** | `nog install swayfx` (removes sway); both hypeForge sessions then run SwayFX; effects only in a separate file | Partly — no effects = Sway-like, but SwayFX-only bugs remain (#566 is tied to shadows/animations) | Easiest; rollback = `nog install sway` from a text console |
| **B. Side by side (recommended for a trial)** | Build SwayFX into its **own folder** (`/opt/swayfx`, e.g. `meson setup --prefix=/opt/swayfx`) against `extra/scenefx` + `wlroots0.20`, packaged as our own `hypeforge-swayfx` (no conflicts, nothing in `/usr/bin`) | **Yes** — `sway` untouched | We maintain one small package; rebuild when wlroots moves to 0.21 |
| C. Extract | Unpack chaotic's binary into a folder by hand | Yes | Not managed by the package manager — fine for a **test**, not for shipping. All its libraries exist on this machine [verified with `readelf`]; running it is unverified. |

**The second login entry** (for B — sits next to our `sway-hypeforge.desktop`, which no package
owns today [verified with `pacman -Qo`]):

```
# /usr/share/wayland-sessions/sway-hypeforge-fx.desktop
[Desktop Entry]
Name=Sway (hypeForge FX)
Comment=hypeForge with rounded corners, shadows and blur (SwayFX) — the plain session stays the default
Exec=/opt/swayfx/bin/sway --unsupported-gpu -c /home/…/.config/sway/config-fx
Type=Application
DesktopNames=sway;wlroots;swayfx
```

**Keep the effects out of the shared config.** Both programs read `~/.config/sway/config` by
default. Plain Sway does not stop on an unknown line, but it shows a warning bar
(`swaynag`: *"Error on line … Unknown/invalid command"*) [verified in `sway/config.c`]. So:

```
# ~/.config/sway/config-fx  — read only by the FX session
include ~/.config/sway/config
include ~/.config/sway/fx.conf      # corner_radius, shadows, blur, layer_effects …
```

The `.desktop` path must be absolute or use a wrapper script (`Exec` does not expand `~`)
[unverified for SDDM — use a wrapper to be safe].

---

## 5. Testing it safely first

**What SwayFX can and cannot draw without a GPU [verified in scenefx source]:**
- SwayFX **always** creates its own OpenGL ES renderer (`fx_renderer_create`); it has **no pixman
  (software-only) renderer** and simply **ignores `WLR_RENDERER=pixman`**.
- With the headless backend (`WLR_BACKENDS=headless`) there is no screen, so it opens the first
  GPU render node (`/dev/dri/renderD128` = our NVIDIA) and draws there, invisibly. Upstream bug
  reporters already reproduce SwayFX bugs this way ("reproduced deterministically in a nested
  headless instance", #565, #569).
- Software drawing is possible through Mesa's llvmpipe with `WLR_RENDERER_FORCE_SOFTWARE=1` and
  `WLR_RENDERER_ALLOW_SOFTWARE=1` (scenefx `util.c`, `egl.c`); in that mode **corners, shadows and
  blur are still drawn** (they are shaders, and llvmpipe runs shaders on the CPU). Mesa 26.2.3 is
  installed. [source code read; **not run**]

**Our bench** (`scripts/headless-check.py`) sets `WLR_BACKENDS=headless WLR_RENDERER=pixman`
with three fake 1280×720 screens. Pointed at a SwayFX binary it would **silently use the NVIDIA
card instead of pixman** — still hidden, still safe, but not the same thing it tests today.
[unverified — reasoned from the source]

| Test | Where | Proves | Cannot prove |
|---|---|---|---|
| 1. Config check | `/opt/swayfx/bin/sway -C -c config-fx` (validate only, no screen) | Every line of our config + `fx.conf` is accepted | Anything visual |
| 2. Hidden bench | headless, 3 fake screens (GPU or llvmpipe) | It starts; applets connect; Workspaces/Placement/Rules behave (F-50 loop check); `reload` ×10 does not freeze (#566); screenshots with `grim` show corners/shadows/blur | Real 144 Hz smoothness, NVIDIA scan-out, adaptive sync, three real screens |
| 3. SwayFX in a window | `WLR_BACKENDS=wayland` — SwayFX runs as one window inside today's Sway, own socket, own test config | The **looks** with Javier's eyes, on the real GPU; nothing of the live desktop changes | Multi-screen behaviour, login, real performance |
| 4. Second login entry | "Sway (hypeForge FX)" in SDDM | Everything, for real | — (if it misbehaves: log out, pick plain "Sway (hypeForge)") |

Follow the memory rule *bench before live desktop* (F-51): tests 1–2 pass before 3–4.

---

## 6. Recommendation

### Which styles need SwayFX to be faithful

| Style | Signature shapes | Plain Sway | Needs SwayFX for |
|---|---|---|---|
| **Windows 11** | Windows 8 px radius, Mica/acrylic taskbar, soft shadow. Microsoft: *"Window corners are not rounded when windows are snapped or maximized"* ([Geometry in Windows 11](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/geometry)) | Good: snapped Win11 windows *are* square; left titles, thin accent frame | Rounding with gaps (`corner_radius 8` + `smart_corner_radius`), shadow, taskbar blur — **yes, to feel like Win11** |
| **Mac OS 9** (Platinum) | Square windows, 1 px dark frames, grey title bars with centred titles, menu bar on top | **Faithful** (`title_align center`, `default_border normal 1`, grey `client.*`, waybar as the menu bar). Pinstripes: impossible in either | **No** (`titlebar_separator disable` is a nicety) |
| **modern macOS** | ~10 px radius, large soft shadows, translucent "vibrancy" bar and menus, centred titles | Weak — flat and square | **Yes** (corners, big shadow, blur on the bar/launcher) [radius unverified] |
| **Linux rice** | Gaps, rounded, blurred see-through terminals, floating-island bar | i3-style "flat rice" is a real genre and works | **Yes** for the modern (Hyprland-like) rice |
| **KDE Plasma** (Breeze) | Small rounded corners, strong shadows, blurred translucent panel | Approximation | **Yes** for corners/shadows/panel blur [values unverified] |
| **COSMIC** | Choice of *Round · Slightly round · Square*, coloured "active hint" frame, tiling gaps, shadows ([Debugpoint](https://www.debugpoint.com/cosmic-desktop-first-look/), [Linuxiac](https://linuxiac.com/cosmic-desktop-adds-rounded-corners-and-window-shadows/)) | **"Square" is faithful** (thick accent frame = active hint, gaps) | Round / Slightly round variants, shadows |

### The safe adoption path

1. **Design every style Sway-first.** Each style gets a plain-Sway version (frames, title bars,
   colours, gaps, the bar). That is the default and always works.
2. **Effects as an optional layer, per style**: an `fx.conf` beside each style (corner radius,
   shadow, blur, `layer_effects` for waybar/mako/fuzzel). Same theme colours (H-1).
3. **Animations stay off** (`animation_duration_ms 0`, the default) until #565 and #569 are fixed
   in a release — both hit our three-screen workspace moves.
4. **Shadows wait for the reload test** (#566): ten `swaymsg reload`s on the bench without a
   freeze, or our docs stop telling people to reload under FX.
5. **Install path:** way **B** (our own `/opt/swayfx` package + a second login entry). Plain
   "Sway (hypeForge)" stays first and default in SDDM. If Javier would rather not maintain a
   package, way **A** (chaotic `swayfx`, Tier 3) is acceptable — but then there is no untouched
   Sway to fall back to without reinstalling from a text console.
6. **Order of tests:** config check → hidden bench (incl. reload ×10, applet loop check) →
   SwayFX in a window for Javier's eyes → the second login session for a day of real use, with
   `nvidia-smi` numbers before/after.
7. **Gap to log (nog finding):** SwayFX is not in Arch's repos and the AUR recipe is broken
   (`scenefx0.5`); chaotic-aur is Tier 3. Shipping FX in KognogOS means owning the package.

---

## Sources

- Sway 1.12 manual: <https://github.com/swaywm/sway/blob/1.12/sway/sway.5.scd>, <https://github.com/swaywm/sway/blob/1.12/sway/sway-output.5.scd>; release notes <https://github.com/swaywm/sway/releases/tag/1.12>
- SwayFX 0.6: release <https://github.com/WillPower3309/swayfx/releases/tag/0.6> (via `gh api`), manual <https://github.com/wlrfx/swayfx/blob/0.6/sway/sway.5.scd>, IPC manual <https://github.com/wlrfx/swayfx/blob/0.6/sway/sway-ipc.7.scd>, README <https://github.com/wlrfx/swayfx/blob/master/README.md>, source at tag 0.6 (`meson.build`, `sway/commands/*.c`, `sway/config.c`, `sway/ipc-json.c`, `sway/desktop/output.c`)
- scenefx 0.5 source and README: <https://github.com/wlrfx/scenefx> (`render/fx_renderer/fx_renderer.c`, `util.c`, `egl.c`)
- SwayFX issues: #93, #267, #274, #307, #308, #328, #363, #393, #398, #439, #458, #546, #565, #566, #569, #574, #585 at <https://github.com/wlrfx/swayfx/issues>; scenefx #123
- Packages: `nog search swayfx`, `pacman -Si swayfx scenefx`, chaotic-aur package file list (downloaded to a scratch folder, not installed), AUR RPC + PKGBUILD <https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=swayfx>, <https://archlinux.org/packages/?q=swayfx>
- Windows 11 geometry: <https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/geometry>
- COSMIC roundness: <https://www.debugpoint.com/cosmic-desktop-first-look/>, <https://linuxiac.com/cosmic-desktop-adds-rounded-corners-and-window-shadows/>
- This machine: `sway --version`, `pacman -Q`, `nvidia-smi`, `/proc/driver/nvidia/version`, our Sway/waybar/mako/fuzzel configs, `applets/common/hfsway.py`, `scripts/headless-check.py`
- Prior hypeForge research: `docs/research/2026-10-04-tiling-base-choice.md` (said SwayFX "trails Sway's releases" — **no longer true as of 0.6**)
