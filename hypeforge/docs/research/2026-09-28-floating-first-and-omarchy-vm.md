# Research — floating-first windows in Hyprland 0.56, and Omarchy in a VM

*Compiled on 2026-09-28 by a research helper working for Claude. It is based on reading the Hyprland wiki, the Hyprland v0.56.2 source, KDE's source and Omarchy's repositories. **Nothing in it had been run inside Hyprland yet**, so the "Could not verify" list at the end is part of the record. Claude checked one claim before passing it on: skipping encryption with Ctrl+C at the disk-formatting confirmation is in Omarchy's manual (`manual/02-getting-started.md`, "No-encryption installations", `quattro` branch).*

**Events since it was written (2026-09-28, same evening):**

- `/etc/libvirt/qemu.conf` got the NVIDIA device files on its allow-list (`scripts/test-rig/enable-nvidia-vm-3d.sh`).
- `omarchy-ref` was created with the standard "SPICE with OpenGL" display, and QEMU starts with it.
- Whether the picture then shows correctly in Virtual Machine Manager (this report expects trouble on NVIDIA) is the next thing checked. The report's own fallback, egl-headless, is below.

---


*Date: 2026-09-28. Method: read-only. Sources were official docs (the frozen **0.56.0** Hyprland wiki, libvirt, QEMU, ArchWiki), the Hyprland **v0.56.2** source code, the Omarchy source code, GitHub data pulled with `gh api`, and read-only checks on this desktop. Nothing was installed. No VM or system setting was changed. No code was run inside Hyprland.*

> **Important for anyone reading the Hyprland wiki:** the default wiki (`wiki.hypr.land/configuring/...`) is the "latest git" version and was reorganized after 0.56. It may describe newer syntax. The pages that match the Hyprland in Arch (0.56.2) live under **`https://wiki.hypr.land/0.56.0/...`**, and every wiki link below points there.

---

## Floating-first + Win+Arrow snapping — plain summary

**Verdict: Doable with work.** Snapping with the Win+Arrow keys is doable with work. Snapping by *dragging* a window to a screen edge with a Plasma-style preview outline is **Risky**.

1. Making every window float by default is easy. "Floating" means a window opens as a free, movable box, like on Windows or Plasma. It takes one documented configuration rule, and Hyprland's own example configuration uses the same "match every window" pattern.
2. Hyprland has no built-in "snap to half" or "snap to quarter" command. Its new Lua configuration (Lua is a small scripting language Hyprland now reads its settings from) gives us every piece needed to build one: key bindings that run our own small functions, the size and position of the active window, the size of each monitor, and the strip of screen the top bar reserves.
3. Roughly 150–250 lines of Lua can copy Plasma's rules, which we read directly from KDE's source code:
   - Win+Left/Right snaps to the left or right half.
   - Win+Up/Down snaps to the top or bottom half.
   - A second arrow turns a half into a quarter.
   - Pressing the side a window is already on moves it to the next monitor.
   - Win+PageUp maximizes and restores.
4. At least three people have already published small Lua files for Hyprland 0.56 that do much of this, so the approach works in practice. None of them is a maintained product we could simply adopt; they are useful as reference.
5. Remembering a window's size before it was snapped (so "restore" can put it back) works while you are logged in. That memory is erased every time Hyprland reloads its settings, unless we also save it to a file.
6. Drag-to-edge snapping can work, but only as "drop and it jumps into place", without a preview outline while you drag. A preview would need a compiled plugin (a C++ add-on built for one exact Hyprland version), which breaks on every Hyprland update.
7. Two cautions:
   - Hyprland 0.56.2, the version Arch ships, has a known bug. After a quick resize, a window can draw its contents in only part of its frame. The bug is fixed upstream (in Hyprland's main code) but not in any release yet.
   - The Lua system is only a few months old, so we must re-test hypeForge on every Hyprland release.
8. Some things Plasma users expect do not exist in Hyprland at all: minimizing a window, and an Alt+Tab window switcher with previews. Those are separate work items, not part of snapping.

---

## How it would work in Hyprland 0.56 (technical, cited)

Labels used below:
- **[wiki 0.56]** is a quote from the 0.56.0 wiki.
- **[src 0.56.2]** means I read it in the Hyprland source at tag `v0.56.2`.
- **[assembled]** means I combined documented pieces myself; the result is not a quote.
- **[untested]** means nothing was run.

### 1. Float every window

- Rule syntax **[wiki 0.56]** ([Window Rules](https://wiki.hypr.land/0.56.0/Configuring/Basics/Window-Rules/)):
  ```lua
  hl.window_rule({
    name = "apply-something",
    match = {
      class = "my-window"
    },
    border_size = 10
  })
  ```
  The same page adds: "there is at least one prop", and in the effects table: `float | boolean | Floats a window.`
- Matching every window: Hyprland's own default config at v0.56.2 does it with `match = { class = ".*" }` ([example/hyprland.lua L317–322](https://github.com/hyprwm/Hyprland/blob/v0.56.2/example/hyprland.lua)). **[src 0.56.2]**
- The float-everything rule **[assembled]**:
  ```lua
  hl.window_rule({
      name  = "float-everything",
      match = { class = ".*" },
      float = true,
      persistent_size = true,   -- optional, see below
  })
  ```
  The independent floating-only desktop *dimarch* uses exactly this rule on 0.55+ ([rules.lua](https://github.com/dmitrax/dimarch/blob/HEAD/dotfiles/hypr/.config/hypr/modules/rules.lua)).
- This is a *static* effect **[wiki 0.56]**: "Static effects are evaluated once when the window is opened and never again."
- The default config ships a rule that ignores apps' own maximize requests (`suppress-maximize-events`, `suppress_event = "maximize"`). A Plasma-like desktop should **not** copy it, so the maximize button in apps keeps working.
- Other documented effects that help a floating desktop **[wiki 0.56]**:
  - `size`: "Resizes a floating window. E.g. `{800, 600}` or `{"(monitor_w*0.5)", "(monitor_h*0.5)"}`"
  - `move`: "Moves a floating window to a given coordinate, monitor-local."
  - `center`: "If the window is floating, will center it on the monitor."
  - `min_size` and `max_size`.
  - `persistent_size`: "For floating windows, internally store their size. When a new floating window opens with the same class and title, restore the saved size."
- Expression variables **[wiki 0.56]**: `monitor_w`, `monitor_h`, `window_x`, `window_y`, `window_w`, `window_h`, `cursor_x`, `cursor_y`. "All position variables are monitor-local." **These expressions only work inside window rules. The move/resize dispatchers do not accept them (see §3).**
- Useful settings ([Variables](https://wiki.hypr.land/0.56.0/Configuring/Basics/Variables/)) **[wiki 0.56]**:
  - Syntax: `hl.config({ category = { value = ... } })`, with the subcategory written as a nested table.
  - `general.snap.enabled`: "enable snapping for floating windows". These are *magnetic edges while dragging*, not halves or quarters. Related: `window_gap`, `monitor_gap`, `border_overlap`, `respect_gaps`.
  - `general.float_gaps`: "gaps between windows and monitor edges for floating windows".
  - `general.resize_on_border`: "enables resizing windows by clicking and dragging on borders and gaps".
  - `input.follow_mouse`. Mode `2` is "Cursor focus will be detached from keyboard focus. Clicking on a window will move keyboard focus to that window". That is closer to Plasma's click-to-focus than the default mode `1`.

### 2. Key bindings

From [Binds](https://wiki.hypr.land/0.56.0/Configuring/Basics/Binds/) **[wiki 0.56]**:
```lua
hl.bind(keys, dispatcher)
hl.bind("SUPER + SHIFT + X", function()
    -- some logic...
    hl.dispatch(hl.dsp.window.float({ action = "toggle" }))
end)
hl.bind(keys, dispatcher, { flag1 = true, flag2 = true })
```
- Flags include `repeating`, `locked`, `release`, `description`, `drag`, `click`.
- Key names: "The name you should use is the segment after `XKB_KEY_`."
- Arrow keys are written in lower case in the official 0.56.2 config **[src 0.56.2]** ([example/hyprland.lua L254, L268–271](https://github.com/hyprwm/Hyprland/blob/v0.56.2/example/hyprland.lua)):
  ```lua
  local mainMod = "SUPER" -- Sets "Windows" key as main modifier
  hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }))
  ```
  That default config uses SUPER+arrows to *move focus*, so hypeForge must take those keys over.
- PageUp is `XKB_KEY_Page_Up` (alias `XKB_KEY_Prior`) in the xkbcommon key list, so the key name would be `"SUPER + Page_Up"` **[assembled, untested]**.

### 3. Dispatchers that move, resize and maximize

From [Dispatchers](https://wiki.hypr.land/0.56.0/Configuring/Basics/Dispatchers/) **[wiki 0.56]**: "Dispatchers return tables that describe an action... Their purpose is to be fed into `hl.bind()` or `hl.dispatch()`." Inside a Lua function you must call `hl.dispatch(hl.dsp....)`. Relevant `hl.dsp.window.` entries, quoted:

| Dispatcher | Wiki text |
|---|---|
| `float({ action?, window? })` | "set a window's floating state." |
| `move({ x, y, relative?, window? })` | "move a window by / to a coord" |
| `resize({ x, y, relative?, window? })` | "resize a window" |
| `center({ window? })` | "center the current window on screen" |
| `fullscreen({ mode?, action?, layout_aware?, window? })` | "`mode` can be "maximized" and "fullscreen". `action` can be `toggle`/`set`/`unset`." |
| `fullscreen_state({ internal, client, action?, layout_aware?, window? })` | internal/client values: -1 current, 0 none, 1 maximized, 2 fullscreen |
| `move({ monitor, follow?, window? })` | "move a window to a monitor". A monitor can be a "direction", a "name", or "relative: `+1` / `-2`" |
| `alter_zorder({ mode, window? })` | "mode can be "top" or "bottom"" |

What the source code shows (these are traps the wiki does not mention) **[src 0.56.2]**:

- **Plain numbers only.** `move` and `resize` read `x`/`y` with `Internal::tableOptNum(L, 1, "x")`, so there are no `"50%"` strings and no old `exact` keyword ([LuaBindingsDispatchers.cpp ~L848–856, L1082–1090](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/config/lua/bindings/LuaBindingsDispatchers.cpp)). The main branch (the future 0.57) still reads them the same way.
- **Absolute `move` uses whole-desktop coordinates.** It computes `pos - window->position(...)`, so `x`/`y` are in the global space that spans all monitors, not per-monitor ([ConfigActions.cpp L618–631](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/config/shared/actions/ConfigActions.cpp)).
- **Maximized counts as fullscreen.** `move` and `resize` refuse with "Window is fullscreen" when the window is fullscreen **or maximized**, because `isFullscreen(window)` with no mode matches any non-zero state ([FullscreenController.cpp L28–66](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/managers/fullscreen/FullscreenController.cpp)). Snapping code must un-maximize first.
- **Resize before move.** A floating resize keeps the window's centre (`pos.translate(-Δ / 2.F)`, [DefaultFloatingAlgorithm.cpp `resizeTarget`](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/layout/algorithm/floating/default/DefaultFloatingAlgorithm.cpp)), so the working order is resize, then move.
- **No clamping.** `move` does not keep the window inside the monitor. It only shifts the window, so our code must calculate the target rectangle.
- **`center` respects the bar.** It uses `logicalBoxMinusReserved()`.
- **`move({ direction = "left" })` is not a half-snap.** On a floating window it pushes the window flush against that edge of the usable area and keeps its size (`moveTargetInDirection`).
- **Restore after maximize is built in.** Un-maximizing a floating window puts it back in its last floating box (`recenter` → `m_datas.at(t).lastBox`). Win+PageUp maximize/restore needs no memory code of ours.
- **Trap: `action = "set"` does not exist for `float()`.** `parseToggleStr` accepts only `""`/`"toggle"`, `"enable"`/`"on"`, and `"disable"`/`"off"`. Anything else **silently becomes toggle** ([LuaBindingsInternal.cpp L306–314](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/config/lua/bindings/LuaBindingsInternal.cpp)). The wiki's own example `hl.dsp.window.float({ action = "set" })` would therefore *un-float* an already-floating window. Use `"on"`.
- **Undocumented but real.** `hl.dsp.window.bring_to_top()` exists (registered at L1382) even though the dispatcher table omits it. The Binds page uses it.

### 4. Reading window and monitor geometry

- **Functions** (from [Expanding functionality](https://wiki.hypr.land/0.56.0/Configuring/Advanced-and-Cool/Expanding-functionality/)) **[wiki 0.56]**: `hl.get_active_window()`, `hl.get_window(selector)`, `hl.get_windows()`, `hl.get_monitors()`, `hl.get_active_monitor()`, `hl.get_monitor_at({ x = num, y = num })`, `hl.get_monitor_at_cursor()`, `hl.get_cursor_pos()`, `hl.get_config()`, `hl.timer(fn, { timeout = ms, type = "oneshot" | "repeat" })`, and `hl.on(event, fn)`.
- **`hl.get_config`.** The same page shows that `hl.get_config("general.gaps_in")` returns `{ top, left, right, bottom }`.
- **Field names.** The wiki says "Use the LSP for the return values". The LSP (the code-completion helper) type descriptions are generated from source, so these names come from source **[src 0.56.2]**:
  - Window ([LuaWindow.cpp L70–170](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/config/lua/objects/LuaWindow.cpp)): `at.x`, `at.y`, `size.x`, `size.y` (the window box *without* its border), `floating`, `fullscreen` (0 none, 1 maximized, 2 fullscreen), `monitor`, `address`, `stable_id`, `class`, `title`, `xwayland`, `pinned`.
  - Monitor ([LuaMonitor.cpp L83–181](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/config/lua/objects/LuaMonitor.cpp)): `x`, `y`, `position`, `width`, `height`, `size`, `scale`, `transform`, `reserved.top/right/bottom/left`, `name`, `id`.
- **Unit trap.** Monitor `width`/`height` are **raw pixels** (`m_pixelSize`), while monitor `x`/`y`, `reserved`, and window `at`/`size` are in **scaled units**. Divide width and height by `scale`, and swap them on rotated screens. Three independent 0.56 Lua files do exactly this: omarchy-snap, rectangle.lua and aerosnap.lua (see the next section).
- **`monitor.reserved` only exists from 0.56.0 on.** The release notes say "lua/objects: add cm and reserved properties to monitor (#14523)" ([v0.56.0 notes](https://github.com/hyprwm/Hyprland/releases/tag/v0.56.0)). hypeForge's snapping therefore requires Hyprland 0.56 or later.

### 5. Events and callbacks: can we do snap zones and "restore previous size"?

- **The events list** **[wiki 0.56]** includes `window.open` ("fully initialized with window rules applied"), `window.open_early`, `window.close`, `window.destroy`, `window.active`, `window.fullscreen`, `window.move_to_workspace`, `monitor.added`, `monitor.removed`, `monitor.layout_changed`, `config.reloaded`, and `input.keyboard.key`.
- **There is no event for "window moved", "window resized", "drag started/ended" or "floating changed".**
- **Restore previous size: feasible.** Keep a Lua table keyed by `window.address`, fill it before the first snap, clear it on `window.close`.
  - Caveat **[src 0.56.2]**: every config reload calls `reinitLuaState()`, which creates a brand-new Lua state ([ConfigManager.cpp `reload()`](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/config/lua/ConfigManager.cpp)). The table is wiped on reload. To survive reloads, write it to a file; Lua's `io` library is loaded (`luaL_openlibs`).
  - Plasma does the same thing: KWin stores the pre-snap geometry on the first snap with `setGeometryRestore(quickTileGeometryRestore())` ([kwin window.cpp](https://invent.kde.org/plasma/kwin/-/blob/master/src/window.cpp)).
- **Keyboard snap zones: feasible.** The key bindings run Lua functions that do the math.
- **Drag-to-edge zones: feasible without a live preview.** Two working patterns exist:
  - A second `SUPER + mouse:272` bind with `{ drag = true }` that fires on release, reads `hl.get_cursor_pos()`, then places the window a moment later with `hl.timer` (omarchy-snap).
  - A 100 ms repeating timer that watches the active window, because "Hyprland has no drag-end event" (aerosnap.lua).
  - A preview outline while dragging would need a compiled plugin (hitori-chan's hyprsnap does this, but only for their fork).
- **Crash to avoid** (reported by dimarch): moving or resizing a window during `window.open_early` crashed Hyprland ("libpixman 'Invalid rectangle passed'"). Use `window.open` instead ([window-position-memory.lua](https://github.com/dmitrax/dimarch/blob/HEAD/dotfiles/hypr/.config/hypr/modules/window-position-memory.lua)).
- **Why a custom layout does not help.** `hl.layout.register(name, { recalculate, layout_msg? })` custom layouts ([Custom Layouts](https://wiki.hypr.land/0.56.0/Configuring/Layouts/Custom-Layouts/)) only place *tiled* windows. It would be a different design (snapped windows become tiled), so it is not a fit for "floating first".

### 6. Plasma's exact rules, to copy

Read from KWin's current source:
- Default shortcuts: [useractions.cpp L830–897](https://invent.kde.org/plasma/kwin/-/blob/master/src/useractions.cpp).
- Snapping logic: `handleQuickTileShortcut` and `combineQuickTileMode` in [window.cpp](https://invent.kde.org/plasma/kwin/-/blob/master/src/window.cpp).
- The same defaults were introduced in 2018 by [KWin commit f1f97bb](https://invent.kde.org/plasma/kwin/-/commit/f1f97bb3956be03151bb1741cfb44429a0f724d9).

A blog post claiming "Meta+Up = maximize" in Plasma 6.6 is contradicted by that source.

| Key (Meta = Win) | Plasma default |
|---|---|
| Meta+Left / Right / Up / Down | Quick Tile Window to the Left / Right / Top / Bottom |
| Meta+PageUp | Maximize Window (toggle) |
| Meta+PageDown | Minimize Window |

| Window is now… | You press… | Result (KWin logic) |
|---|---|---|
| not snapped | Left | left half; the old size is saved first |
| left half | Up | top-left quarter |
| left half | Right | right half |
| left half | Left | moves to the monitor on the left and becomes its *right* half; if no monitor is there, nothing happens |
| top-left quarter | Right | top half |
| top half | Down | bottom half |

### 7. Sketch of the core [assembled, untested]

Every `hl.*` call below is documented for 0.56 or confirmed in the v0.56.2 source. The logic itself has never been run.

```lua
local mainMod = "SUPER"
local saved = {}                           -- pre-snap box per window; wiped on config reload

local function sides(v, d)                 -- gaps may be a number or {top,right,bottom,left}
  if type(v) == "number" then return { top = v, right = v, bottom = v, left = v } end
  v = type(v) == "table" and v or {}
  return { top = v.top or d, right = v.right or d, bottom = v.bottom or d, left = v.left or d }
end

local function work_area(mon)              -- usable box in global (all-monitor) coordinates
  local s = (mon.scale and mon.scale > 0) and mon.scale or 1
  local w, h = mon.width / s, mon.height / s          -- width/height are raw pixels
  if mon.transform % 2 == 1 then w, h = h, w end      -- rotated screen
  local r = sides(mon.reserved, 0)                    -- the bar's strip
  local g = sides(hl.get_config("general.gaps_out"), 10)
  return { x = mon.x + r.left + g.left, y = mon.y + r.top + g.top,
           w = w - r.left - r.right - g.left - g.right,
           h = h - r.top - r.bottom - g.top - g.bottom }
end

local ZONES = { left = {0,0,.5,1}, right = {.5,0,1,1}, top = {0,0,1,.5}, bottom = {0,.5,1,1},
                topleft = {0,0,.5,.5}, topright = {.5,0,1,.5},
                bottomleft = {0,.5,.5,1}, bottomright = {.5,.5,1,1} }

local function snap(zone)
  local win = hl.get_active_window()
  if not win or not win.floating then return end
  local target = "address:" .. win.address
  if win.fullscreen ~= 0 then                         -- move/resize refuse maximized windows
    hl.dispatch(hl.dsp.window.fullscreen_state({ internal = 0, client = -1, window = target }))
    win = hl.get_window(target)
  end
  saved[win.address] = saved[win.address] or { x = win.at.x, y = win.at.y, w = win.size.x, h = win.size.y }
  local a, z = work_area(win.monitor), ZONES[zone]
  local b = tonumber(hl.get_config("general.border_size")) or 2   -- borders sit outside at/size
  local x, y = a.x + a.w * z[1], a.y + a.h * z[2]
  local w, h = a.w * (z[3] - z[1]), a.h * (z[4] - z[2])
  hl.dispatch(hl.dsp.window.resize({ x = math.floor(w - 2*b), y = math.floor(h - 2*b), window = target }))
  hl.dispatch(hl.dsp.window.move({ x = math.floor(x + b), y = math.floor(y + b), window = target }))
end

hl.bind(mainMod .. " + left", function() snap("left") end, { description = "Snap left half" })
-- ...combination state per window (see the table in §6) decides which zone each arrow picks;
-- the "next monitor" case uses hl.dsp.window.move({ monitor = "l", window = target }) and then re-snaps.
hl.bind(mainMod .. " + Page_Up", hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle" }))
hl.on("window.close", function(w) if w then saved[w.address] = nil end end)
```

The sketch does not yet handle the inner gap between two snapped halves (`gaps_in`), the combination state, or restore on drag. The `fullscreen_state({ internal = 0, client = -1 })` un-maximize call is the one omarchy-snap uses.

---

## Existing projects that do this

Activity comes from `gh api repos/OWNER/REPO --jq '[.stargazers_count, .pushed_at] | @tsv'` on 2026-09-28. "Works on 0.56?" is based on reading the code or README; **none of these were run**.

| Name / link | What it does | Activity (stars · last push) | Works on 0.56? |
|---|---|---|---|
| [georgeantonopoulos/omarchy-snap](https://github.com/georgeantonopoulos/omarchy-snap) | Drag with SUPER+left mouse button and drop on a screen edge: half, quarter or maximize. No preview. By default, edge drops hand the window to the tiling layout (`tile_edges = false` gives floating halves). | 0 · 2026-08-26 (4 commits, all that day) | **Claimed yes:** "Omarchy 4.x, or any Hyprland 0.56+ using the Lua config". It uses only 0.56 Lua APIs (I read `snap.lua`). |
| [yz778/hyprfloat](https://github.com/yz778/hyprfloat) | Outside Lua program: `snap <x0> <x1> <y0> <y1>` to fractions of the screen, float-all toggle, Alt+Tab, overview. | 73 · 2026-08-20 (last code change 2025-10-13) | **No, not with a Lua config.** It sends old strings like `dispatch moveactive exact %d %d`. Under a Lua config, 0.56.2 turns `hyprctl dispatch X` into `hl.dispatch(X)`, which fails with "your syntax might need to be updated" ([HyprCtl.cpp L1126–1140](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/debug/HyprCtl.cpp)). It only works on the deprecated `hyprland.conf`. |
| [mtaimourz/dotfiles · rectangle.lua](https://github.com/mtaimourz/dotfiles/blob/HEAD/omarchy/.config/hypr/rectangle.lua) | Keyboard snapping like the macOS app Rectangle: halves, quarters, full, restore. | 0 · 2026-09-08 | Written for 0.56 Lua (Omarchy 4). A personal dotfile, not a package. |
| [norandom/hyperland-forky-worker-vm · aerosnap.lua](https://github.com/norandom/hyperland-forky-worker-vm/blob/HEAD/files/hypr/aerosnap.lua) | Windows-style drag to the left/right edge = half, top edge = maximized area, via a 100 ms polling timer; dragging again restores the old size. | 0 · 2026-09-28 (repo created 2026-09-26) | Written for 0.56 Lua. A personal VM config; uses the hyprbars plugin. |
| [jdvmi00/hypertile](https://github.com/jdvmi00/hypertile) | Zones like Windows' FancyZones: *tiling* layouts designed in an overlay, scenes, display manager. | 6 · 2026-09-21 | Yes per README (Hyprland 0.56.2 / Omarchy 4.0.3). Heavy (Quickshell, Python). It documents and patches the 0.56.2 sizing bug. |
| [lukejmorrison/omawin](https://github.com/lukejmorrison/omawin) | Windows-style title bars (minimize/maximize/close) on floating windows through official hyprbars; "minimize" = move to a scratchpad. | 0 · 2026-09-01 | Yes per README: "Tested on Omarchy Quattro (4.x) with Hyprland 0.56 Lua config". |
| [hyprwm/hyprland-plugins · hyprbars](https://github.com/hyprwm/hyprland-plugins/tree/main/hyprbars) (official) | Title bars with buttons. | 1463 · 2026-09-22 | Yes: pinned for 0.56.0–0.56.2 in `hyprpm.toml`; the README documents Lua config (`hl.plugin.hyprbars.add_button({...})`). Its own Lua example still uses old syntax (`on_double_click = "hyprctl dispatch fullscreen 1"`). |
| [hitori-chan/hyprland-plugins](https://github.com/hitori-chan/hyprland-plugins) (`hyprsnap`, `hyprmax`, `hyprplace`) | C++ plugins: magnetic plus edge/corner drag snapping **with preview**, per-window maximize that remembers geometry, remembered placement. | 0 · 2026-09-29 UTC | **No:** built "for the exact `hitori-chan/Hyprland` fork ABI" (a personal copy of Hyprland). Design reference only. |
| [elviosak/hyprsnap](https://github.com/elviosak/hyprsnap) | "Aerosnap in Hyprland", C++ plugin. | 0 · 2025-02-07 | Almost certainly no (an early-2025 plugin from before Lua; not checked further). |
| [dmitrax/dimarch](https://github.com/dmitrax/dimarch) | A whole "floating-only" Arch + Hyprland desktop (work in progress). The closest peer to hypeForge. | 1 · 2026-09-19 | Uses 0.55+ Lua (float-all rule, window position memory). **Has no arrow-key snapping.** |
| Hyprland native `general.snap` | Magnetic edges while dragging floating windows. | core | Yes (0.56 Variables page), but not halves or quarters. |
| Upstream requests | [Discussion #13838](https://github.com/hyprwm/Hyprland/discussions/13838) (Aero Snap, 2026-03-24, 0 replies), [#9200](https://github.com/hyprwm/Hyprland/discussions/9200) (2025), [issue #3230](https://github.com/hyprwm/Hyprland/issues/3230) (closed 2024-10-27) | — | Confirms there is no native half/quarter snapping. |

---

## Pitfalls

1. **Three 2560×1440 monitors.**
   - Coordinates are whole-desktop (for example 0–7680 across three screens side by side). Snap on the window's own monitor (`win.monitor`), not the cursor's.
   - Each monitor has its own reserved strip (the bar may exist on one screen or all).
   - "Same side again = next monitor" uses `move({ monitor = "l" })` followed by a re-snap.
   - At scale 1 the math is exact. Any fractional scale needs the divide-by-`scale` step, plus care with rounding.
2. **Maximized or fullscreen windows.**
   - `move`/`resize` refuse them (source); un-maximize first.
   - Un-maximize restores the last floating box by itself.
   - Floating windows go fullscreen through their own handler, so full-screen video in a floating window is fine.
3. **Apps that open tiny, and window placement.**
   - A floating window that asks for no size gets **640×400** (`DEFAULT_SIZE`, [DefaultFloatingAlgorithm.cpp](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/layout/algorithm/floating/default/DefaultFloatingAlgorithm.cpp)).
   - Native Wayland apps cannot choose their position, so every new window opens **centered, stacked on top of the last one**.
   - Fixes: per-app `size` rules, `min_size`, `persistent_size` (it only lasts one session, per dimarch), or a `window.open` handler that enlarges or cascades windows (never `window.open_early`, which crashed dimarch).
4. **Dialogs.**
   - Native Wayland dialogs with a parent open centered over that parent ([WindowTarget.cpp `desiredGeometry`](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/layout/target/WindowTarget.cpp)).
   - `match = { modal = true }` targets "Are you sure" popups.
   - X11 dialogs use their own coordinates.
5. **XWayland apps** (older X11 programs running inside Wayland).
   - An X11 window that asks for a position gets it.
   - They look blurry on fractional scaling ([FAQ](https://wiki.hypr.land/0.56.0/FAQ/)) unless `xwayland.force_zero_scaling`.
   - The default config ships a `fix-xwayland-drags` rule.
   - Forwarding shortcuts to them is "a bit wonky" (Binds page).
6. **The 0.56.2 sizing bug.**
   - After quick resizes, a window can have the right frame while its contents fill only the upper-left part ([hypertile write-up](https://github.com/jdvmi00/hypertile/blob/main/docs/HYPRLAND-SIZING-BUG.md)).
   - Fixed upstream in [af0d014 (2026-08-17)](https://github.com/hyprwm/Hyprland/commit/af0d014cb26f536d8cb7cab2b9d5784f69767c8a), which is **not** in v0.56.2 (checked with `gh api compare`).
   - Arch's `0.56.2-3` is only a rebuild: "Rebuild with plugin manager split", with no patch in its PKGBUILD.
   - Snapping does exactly the resize-then-move that can trigger it. This is unproven for floating windows specifically.
7. **Documentation traps.**
   - `float({ action = "set" })` actually toggles (§3).
   - The wiki's "Combining it all" example has `if ... do` where Lua needs `then`.
   - Community READMEs still show old `hyprctl dispatch` strings.
   - The default wiki is already post-0.56.
8. **Lua memory resets on every config reload** (§5).
9. **No move, resize or drag events**, so there is no live snap preview in pure Lua.
10. **Plasma features Hyprland lacks.**
    - Minimize: Hyprland only reports a taskbar's request as the IPC event `minimized`, with no Lua event ([IPC page source](https://github.com/hyprwm/hyprland-wiki/blob/main/content/ipc/_index.md)). A special workspace is the usual stand-in.
    - Alt+Tab: none built in; the wiki lists [snappy-switcher](https://github.com/OpalAayan/snappy-switcher).
    - Title bars: a plugin, which must be rebuilt through `hyprpm` on every Hyprland update. `hyprpm` became its own Arch package in 0.56.2-3.
11. **API churn.** The wiki warns that dispatcher tables' "contents are not guaranteed to be stable at all". Pin and re-test on every Hyprland release.
12. **Focus feel.** The default `follow_mouse = 1` gives focus to whatever window is under the pointer, which is jarring with overlapping windows. Consider `2`.

---

## Omarchy in a VM — plain summary

**Verdict: Yes, we can run Omarchy 4 in a VM on this machine.**

- **It is a well-trodden path.** Omarchy's own developers boot it in QEMU virtual machines (the same engine behind virt-manager). Their automated tests run the whole desktop with *no* 3D graphics help at all. Omarchy even added a "VM mode" today that turns off animations, because "a VM usually renders on the CPU".
- **The only hard part is graphics speed.** Passing the NVIDIA card's 3D power into a VM by the textbook method ("SPICE with OpenGL") has been broken with NVIDIA's driver for years, and it is still reported broken in 2026. A documented workaround exists and has been reported working on the same RTX 3060 card this spring. It needs one small change to a system settings file (a sudo step, your call). Even then, people describe it as "still slow" when moving windows.
- **Recommended first step (no system changes at all):**
  1. Create the VM with the same plain graphics your other VMs already use.
  2. Install Omarchy 4.0.4 without disk encryption. To do that, press Ctrl+C at the disk-format confirmation; the manual allows this for throw-away installs, and it avoids typing a disk password at every boot.
  3. Then switch off animations and blur inside Omarchy.
  - It will feel a little slow but should just work.
- **Optional upgrade:** try the NVIDIA 3D workaround afterwards. If the VM refuses to start or shows black, switch back.
- **Suggested size:** 8 virtual CPUs, 8 GB of memory, and a 64 GB disk that only grows as it fills. This fits comfortably: the host has 16 threads, 31 GB of RAM and 539 GB free.
- **Nothing new needs installing on the host.** QEMU, libvirt, virt-manager, UEFI firmware and virglrenderer are all present.

---

## Omarchy in a VM — technical notes (cited)

### Host facts (read-only checks today)

- **GPU:** only one, the NVIDIA GA106 RTX 3060 LHR at PCI `01:00.0`. Its render node (the device file programs use to ask the GPU to draw) is `/dev/dri/renderD128`, also reachable as `/dev/dri/by-path/pci-0000:01:00.0-render`, with mode `crw-rw-rw-`.
- **NVIDIA device files:** `/dev/nvidia0`, `/dev/nvidiactl`, `/dev/nvidia-modeset` and `/dev/nvidia-uvm` exist, all mode 0666.
- **Packages:**
  - `nvidia-open-dkms`/`nvidia-utils` 615.71.09, `egl-gbm` 1.1.4, `egl-wayland` 1.1.22
  - `qemu-desktop` 11.1.1, with modules `ui-sdl`, `ui-gtk`, `ui-spice-core`, `ui-egl-headless`, `ui-opengl`, `hw-display-virtio-gpu-gl`, `hw-display-virtio-vga-gl`
  - `libvirt` 12.7.0 (the monolithic `libvirtd.service` is active; the modular `virtqemud` is inactive)
  - `virt-manager` 5.1.0, `virglrenderer` 1.3.0, `edk2-ovmf` 202608, `spice-gtk` 0.42
  - `virt-viewer` is **not** installed; virt-manager's built-in console is enough.
- **CPU and memory:** AMD Ryzen 7 7700 (8 cores / 16 threads, AVX2), 31 GiB RAM (about 23 GiB available). VM images live on btrfs (zstd) with 539 GB free.
- **Session:** KDE Plasma on Wayland.
- **Existing VMs (`kognog-test`, `debian13-grubforge`):**
  - Firmware `OVMF_CODE.secboot.4m.fd` with `enrolled-keys` off. Per libvirt docs, "Firmware with Secure Boot feature but without enrolled keys will successfully boot non-signed binaries as well."
  - SPICE with `<listen type='address'/>`, and `<model type='virtio' .../>` without 3D. This is the no-GL baseline.
- **Integrated graphics:** AMD's spec page lists **"AMD Radeon™ Graphics, Graphics Core Count 2"** for the [Ryzen 7 7700](https://www.amd.com/en/products/processors/desktops/ryzen/7000-series/amd-ryzen-7-7700.html). `lspci` shows no AMD GPU and `amdgpu` is not loaded, so it is most likely disabled in the BIOS. This matters for Plan C.

### What Omarchy says and does about VMs

- **Official statements.**
  - The manual lists VM guides only for Parallels, VirtualBox ("performance probably won't be great") and VMware ([manual/49-omarchy-on.md](https://github.com/basecamp/omarchy/blob/quattro/manual/49-omarchy-on.md)).
  - The ISO README says "The Omarchy ISO is the only supported way to install Omarchy" and gives a **Proxmox VM example** ([omarchy-iso README](https://github.com/omacom-io/omarchy-iso)): `--bios ovmf --machine q35 --cpu host --cores 4 --memory 8192 … efitype=4m,pre-enrolled-keys=0 … --scsi0 …:40,discard=on … --vga virtio`.
  - omarchy.org's "Try it first: All of Omarchy running in a virtual machine" links to official QEMU-based apps for macOS ([try-omarchy](https://github.com/omacom/try-omarchy): "VirGL graphics") and Windows ([try-omarchy-windows](https://github.com/omacom/try-omarchy-windows): "render through VirGL and Venus Vulkan. The launcher falls back to CPU rendering when that path is unavailable"). "On Linux, the ISO is the way in."
- **Developer VM script** ([bin/omarchy-iso-boot](https://github.com/omacom-io/omarchy-iso/blob/HEAD/bin/omarchy-iso-boot)): `-cpu host -enable-kvm -machine q35`, `-smp` = min(host threads, 8), `-m 8192`, `OVMF_CODE.4m.fd` (no Secure Boot), a 40G qcow2 on `virtio-blk-pci`, **`-device virtio-vga-gl -display sdl,gl=on`**, and `usb-tablet`.
- **Automated acceptance tests** ([bin/omarchy-iso-test L201–229](https://github.com/omacom-io/omarchy-iso/blob/HEAD/bin/omarchy-iso-test)): the full desktop runs on **`-device virtio-vga -display none`** plus VNC, which means no 3D at all. The same script warns: "a resize during early boot can wedge virtio-gpu". Don't resize the viewer window while the VM boots.
- **VM mode** ([install/user/hardware/vm-no-animations.sh](https://github.com/basecamp/omarchy/blob/quattro/install/user/hardware/vm-no-animations.sh)): "A VM usually renders on the CPU, where animations and transparency cost every frame, so start it without them."
  - It detects a VM with `systemd-detect-virt --vm --quiet`.
  - It landed in commit `b18ab4952` on **2026-09-28** and is **not in the v4.0.4 tag**.
  - Until it ships, do by hand what its toggle file does ([no-animations.lua](https://github.com/basecamp/omarchy/blob/quattro/default/hypr/toggles/no-animations.lua)): `hl.config({ animations = { enabled = false }, decoration = { blur = { enabled = false }, shadow = { enabled = false } } })`.
- **Scaling in a VM window.** Omarchy 4.0.4 sets `local omarchy_gdk_scale = 2` in `~/.config/hypr/monitors.lua`. The manual says to change it to 1 on a normal-density display ([45-troubleshooting.md](https://github.com/basecamp/omarchy/blob/quattro/manual/45-troubleshooting.md)).

### Installer defaults that matter in a VM

- **ISO:** [`omarchy-4.0.4.iso`](https://iso.omarchy.org/omarchy-4.0.4.iso), 6,185,304,064 bytes (about 6.19 GB), dated 2026-09-15. Its published SHA-256 is `ddeded2758c48318d201dfdac905ecb28f570441883f0c052ea3cd5d05acf92d` (`.sha256` and `.sig` sit alongside it).
- **Offline install.** Packages come from a mirror bundled inside the ISO, so installing needs no internet.
- **Firmware.** "You must turn off Secure Boot" ([02-getting-started.md](https://github.com/basecamp/omarchy/blob/quattro/manual/02-getting-started.md)). Use UEFI without Secure Boot, like Omarchy's own scripts.
- **Encryption.** "the installation defaults to full encryption" (LUKS). "You can hit `Ctrl + C` on the disk formatting confirmation to switch to an encryption-less installation." Encrypted installs get SDDM autologin after the disk password (ISO README).
- **Filesystem.** btrfs with `compress=zstd` and subvolumes `@`, `@home`, `@log`, `@pkg`, plus a 2 GiB FAT32 EFI partition for Unified Kernel Images (single-file boot images) ([configurator](https://github.com/omacom-io/omarchy-iso/blob/HEAD/configs/airootfs/root/configurator)).
- **Bootloader.** "Omarchy installs only support Limine bootloader setup", with Snapper snapshots ([phases_impl.py](https://github.com/omacom-io/omarchy-iso/blob/HEAD/configs/airootfs/usr/share/omarchy-iso/orchestrator/phases_impl.py); [47-system-snapshots.md](https://github.com/basecamp/omarchy/blob/quattro/manual/47-system-snapshots.md)).
- **Hibernation swap file.** The installer runs `omarchy-hibernation-setup --force`, which creates a swap file **equal to the VM's RAM** (`btrfs filesystem mkswapfile -s "$MEM_TOTAL_KB"`, [bin/omarchy-hibernation-setup](https://github.com/basecamp/omarchy/blob/quattro/bin/omarchy-hibernation-setup)). With 8 GiB RAM, 8 GiB of the disk goes to swap.
- **Disk minimum.** A free-space install needs "at least 32GB" (configurator). Omarchy's own VMs use 40 GB. With the RAM-sized swap file, **64 GB** is comfortable, and a thin qcow2 file only grows as it fills.

### Recommended specs, with sources

| Source | vCPU | RAM | Disk | Graphics |
|---|---|---|---|---|
| Omarchy developer VM script | min(threads, 8) | 8 GiB | 40 GB | virtio-vga-gl + SDL GL |
| Omarchy acceptance tests | all threads | 8 GiB | 40 GB | virtio-vga, no GL |
| ISO README Proxmox example | 4, `cpu host` | 8 GB | 40 GB | virtio |
| Try Omarchy for Windows, automatic sizing | "all logical processors but two, between two and eight" | "a third of the machine's RAM between 4 and 8 GiB (6 GiB with GPU rendering)" | — | VirGL/Venus or CPU |
| omarchy.org | — | "Even a 2011 ThinkPad X220 with 2GB of RAM can run Omarchy" | — | — |
| **Proposal for this host** | **8, `host-passthrough`** | **8 GiB** | **64 GB qcow2 on virtio** | see A/B below |

Keep `host-passthrough` (already used by the existing VMs). Try Omarchy's findings note that CPU rendering without AVX2 "hurts llvmpipe badly" ([FINDINGS.md](https://github.com/omacom/try-omarchy-windows/blob/HEAD/docs/FINDINGS.md)). llvmpipe is Mesa's software renderer, the one that draws with the CPU.

### A. Try first: the baseline VM (no host changes; also the fallback)

This is the proven no-3D path (Omarchy's acceptance tests), expressed as libvirt XML fragments **[assembled from libvirt docs and the existing VMs; untested]**. In virt-manager, pick firmware "UEFI x86_64: /usr/share/edk2/x64/OVMF_CODE.4m.fd" (the non-secboot one). The existing secboot-without-keys choice should also boot, per libvirt's docs.

```xml
<memory unit='GiB'>8</memory>
<vcpu placement='static'>8</vcpu>
<os firmware='efi'>
  <type arch='x86_64' machine='q35'>hvm</type>
  <firmware>
    <feature enabled='no' name='secure-boot'/>
  </firmware>
</os>
<cpu mode='host-passthrough' check='none' migratable='on'/>
<!-- disk: qcow2, 64G, bus='virtio'; CD-ROM: omarchy-4.0.4.iso -->
<graphics type='spice' autoport='yes'>
  <listen type='address'/>
</graphics>
<video>
  <model type='virtio' heads='1' primary='yes'/>
</video>
```

After install:
- set `omarchy_gdk_scale = 1`;
- add the `hl.config` block above that turns animations, blur and shadows off.

In the guest, `hyprctl` / Hyprland's log should report a software renderer (llvmpipe).

### B. The 3D upgrade: NVIDIA workaround (one host settings change, sudo, your call)

Source: ArchWiki [Libvirt § "EGL_NOT_INITIALIZED: render node init failed"](https://wiki.archlinux.org/title/Libvirt#EGL_NOT_INITIALIZED:_render_node_init_failed), which states "as of May 11th 2026, it hasn't been fixed yet". It rests on [libvirt #311](https://gitlab.com/libvirt/libvirt/-/issues/311) ("`/etc/libvirt/qemu.conf` needs to have some nvidia specific devices added to `cgroup_device_acl`") and [virt-manager #938](https://github.com/virt-manager/virt-manager/issues/938).

Why the edit is needed: with `qemu:///system`, libvirt only lets QEMU open an allowed list of device files. NVIDIA's EGL (its graphics interface) needs its own `/dev/nvidia*` files, which are not on that list.

1. **Step 1 is already satisfied here.** The wiki's udev rule `SUBSYSTEM=="drm", KERNEL=="renderD*", GROUP="render", MODE="0666"` is in effect; `renderD128` is `crw-rw-rw-`.
2. **Edit `/etc/libvirt/qemu.conf`.** This host's libvirt 12.7 default list (commented out, lines ~618–622) is `/dev/null`, `/dev/full`, `/dev/zero`, `/dev/random`, `/dev/urandom`, `/dev/ptmx`, `/dev/userfaultfd`. Keep those and add the NVIDIA ones:
   ```
   cgroup_device_acl = [
       "/dev/null", "/dev/full", "/dev/zero",
       "/dev/random", "/dev/urandom",
       "/dev/ptmx", "/dev/userfaultfd",
       "/dev/nvidiactl", "/dev/nvidia0", "/dev/nvidia-modeset", "/dev/nvidia-uvm",
       "/dev/dri/renderD128"
   ]
   ```
   Then restart `libvirtd.service`, the unit that is active on this host. The wiki author tested that `seccomp_sandbox = 0` "isn't required" (2026-05-11).
3. **Change the VM's graphics** (the ArchWiki pattern, with this host's PCI path):
   ```xml
   <graphics type='spice'>
     <listen type='none'/>
     <gl enable='no'/>
   </graphics>
   <graphics type='egl-headless'>
     <gl rendernode='/dev/dri/by-path/pci-0000:01:00.0-render'/>
   </graphics>
   <video>
     <model type='virtio' heads='1' primary='yes'>
       <acceleration accel3d='yes'/>
     </model>
   </video>
   ```
   libvirt describes `egl-headless` as "an OpenGL accelerated display accessible both locally and remotely (for comparison, Spice's native OpenGL support only works locally using UNIX sockets at the moment, but has better performance)" ([formatdomain § Graphical framebuffers](https://libvirt.org/formatdomain.html#graphical-framebuffers)).
4. **Check it worked.** In the guest, `dmesg | grep drm` should show `[drm] virgl 3d acceleration enabled` ([ArchWiki QEMU § virtio](https://wiki.archlinux.org/title/QEMU#virtio)). Try Omarchy's notes show Hyprland logging `Renderer: virgl (...)` when this works.
5. **Evidence and expectations.**
   - A user with the **same RTX 3060** reported it working on "Driver 590.48.01. Manjaro / Arch linux … QEMU … 10.2.0, libvirtd … 12.0.0" (virt-manager #938, 2026-01-28). The wiki author ran it on driver 595.71.05.
   - It is **not** confirmed on 615.
   - Expect it to be less smooth than native: "moving windows around still feels slow to me just like it felt when it was using llvmpipe" (2026-05-20). Visual artifacts are possible ("artifacts were visible on renderd128"; [NVIDIA forum: corruption with drivers 570+ vs 535](https://forums.developer.nvidia.com/t/visual-corruption-regression-with-driver-version-570-in-qemu-with-virgl-gpu-acceleration/331730)).
   - One user said it only worked in per-user (session) QEMU, not in system mode ([NVIDIA forum 318750, #17](https://forums.developer.nvidia.com/t/egl-errors-with-qemu-kvm-and-virtio-w-hardware-acceleration/318750)). The cgroup edit in step 2 targets exactly that system-mode failure.

### C. Only as a curiosity: native SPICE GL (the textbook setting)

```xml
<graphics type='spice'><listen type='none'/><gl enable='yes' rendernode='/dev/dri/by-path/pci-0000:01:00.0-render'/></graphics>
```
Use it with `accel3d='yes'`.
- libvirt: "Note that this only works locally, since this requires usage of UNIX sockets, i.e. using listen types 'socket' or 'none'."
- **Expected result on this host:** the VM refuses to start with `egl: eglInitialize failed: EGL_NOT_INITIALIZED` / `egl: render node init failed`. This is reported for NVIDIA drivers from the 500 series through 595.58.03 (April 2026), including an RTX 3060 and an Arch user in May 2026 ([NVIDIA forum 318750](https://forums.developer.nvidia.com/t/egl-errors-with-qemu-kvm-and-virtio-w-hardware-acceleration/318750)).
- Even after the cgroup fix, a black screen is likely ([libvirt #409](https://gitlab.com/libvirt/libvirt/-/issues/409); forum #5: "I've never been able to do Spice with OpenGL with NVIDIA drivers").
- virt-manager's maintainer called SPICE GL and virgl "constantly breaking and unbreaking as packages update" ([virt-manager #396](https://github.com/virt-manager/virt-manager/issues/396)).

### D. Not recommended here

- **Venus (Vulkan inside the VM).**
  - Hyprland 0.56.2 draws with **OpenGL ES 3.2** (`#include <GLES3/gl32.h>`, [OpenGL.cpp](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/render/OpenGL.cpp)), and there is no Vulkan renderer, so Venus does not speed up the desktop.
  - libvirt's domain XML has no Venus option (searched formatdomain), so it would need raw QEMU arguments.
  - An NVIDIA bug distorts Venus images ([NVIDIA forum 364360](https://forums.developer.nvidia.com/t/egl-import-via-egl-ext-image-dma-buf-import-modifiers-ignores-explicit-stride-causes-image-distortion-in-virtio-gpu-venus/364360)).
- **DRM native context** (QEMU 11.0+, a way for the VM to talk to the host GPU's own driver). [QEMU's virtio-gpu docs](https://www.qemu.org/docs/master/system/devices/virtio/virtio-gpu.html) list AMDGPU, Freedreno, Intel i915, Asahi and Panfrost, **not NVIDIA**.
- **GPU passthrough.** The only GPU drives the host desktop. The Hyprland wiki's vGPU route ([Virtual-GPU](https://wiki.hypr.land/0.56.0/Configuring/Advanced-and-Cool/Virtual-GPU/)) needs workstation or partitionable cards. The same page says of virtio-gpu: "You can therefore, and as many have already, use Hyprland normally with it."

### E. Plan C (unverified, changes the host BIOS): use the Ryzen's own graphics

ArchWiki: "If there is a GPU from another brand present (e.g. an iGPU…), it can be used as the render node instead of the Nvidia GPU." Forum users with Intel or AMD integrated graphics confirm it avoids the EGL error.

If the board's BIOS can enable the 7700's 2-core Radeon alongside the RTX 3060, virgl could use its render node through Mesa's AMD driver. It is untested whether the result then displays well through virt-manager running on the NVIDIA desktop.

---

## Could not verify

- **Nothing was run.** No Hyprland 0.56 session was scripted and no VM was created. Every snapping behaviour and every libvirt setting above comes from documentation or source reading.
- **Whether the 0.56.2 sizing bug hits floating-window snapping.** It is documented for tiled layouts in hypertile. Also unknown: when an Arch package will carry the upstream fix (af0d014).
- **The exact return type of `hl.get_config("general.border_size")` and `general.gaps_out`.** The wiki only documents the `gaps_in` table shape; community code handles both a number and a table.
- **The `Page_Up` key name in a bind.** It comes from the xkbcommon naming rule quoted on the Binds page; I did not test it.
- **Whether `fullscreen_state({ internal = 0, client = -1 })` un-maximizes synchronously** enough for a `move`/`resize` in the same function. omarchy-snap does this, but instead places the window a timer tick later.
- **Whether the egl-headless workaround works on NVIDIA driver 615.71.09.** Reports cover 590.48.01 and 595.71.05. Also unknown: whether it works under `qemu:///system` on this exact host, and how smooth Omarchy feels with it.
- **Whether native SPICE GL behaves any differently on driver 615 with a KDE Wayland host.** All the evidence found says it fails.
- **Whether this board's BIOS can enable the Ryzen 7 7700 integrated graphics next to the RTX 3060, and whether Plan C then displays correctly.**
- **Whether Super-key shortcuts reach the Omarchy guest through virt-manager's console on KDE Wayland** instead of being taken by Plasma. Omarchy is keyboard-first, so check this in the first session.
- **Whether the v4.0.4 ISO boots and installs cleanly under libvirt with the settings above,** and whether Omarchy's new VM no-animations mode reaches existing installs through `omarchy update`. It was merged today (2026-09-28), so I don't know which release it ships in.
- **Omarchy has no official hardware or VM requirements page.** The numbers above come from its scripts, examples and try-it apps, not from a stated minimum.
