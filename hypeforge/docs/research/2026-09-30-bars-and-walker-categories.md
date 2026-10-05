# Research · App menu with categories (F-6) and top-bar candidates (F-4)

*2026-09-30 · Claude, for Javier · read-only research: nothing was installed, no settings were changed. Sources were cloned into a scratch folder and read. Every claim is marked **[verified]** (read in the source code or official docs today) or **[inferred]** (reasoned from the code, still to be proven in the test VM).*

---

## The short version

**F-6, the Omarchy "categories":**

- **What Javier saw was not Walker, and it was not app categories.** The Omarchy VM runs **Omarchy 4.0.4**, which removed Walker, elephant, Waybar and mako in August 2026 and replaced them with its own panel program (built on Quickshell, a toolkit for drawing desktop panels). In 4.0.4, Win + Space opens the **Omarchy menu**. Its top level lists *Apps, Learn, Trigger, Style, Setup, Install, Remove, Update, About, System*. Clicking **Apps** shows **one alphabetical list of every app**. No Internet, Office or Games grouping exists anywhere in Omarchy. **[verified]**
- Omarchy 3 (the Walker era) worked the same way. A script (`omarchy-menu`) piped that list of words into `walker --dmenu`, and "Apps" opened Walker's normal flat app search. **[verified]**
- **We can still build what Javier wants, and it can be better than Omarchy's.** Walker's helper program, elephant, has a "menus" feature: small files that describe a list, where one entry can open another list. Menus can also be small **Lua** programs that build their list when opened. One such program can read every app's `Categories=` line (the tag each app ships saying what kind of app it is) and show only the matching apps. The recipe is in [Part A](#part-a--f-6-app-menu-with-categories). **[verified that every building block exists; the assembled result is inferred until tried in the VM]**
- **Two warnings.** (1) **elephant's author put development on hold on 2026-09-29, yesterday** ("Development is on hold."). Walker is still active (last change 2026-09-25). (2) Two of the shells in Part B **already have an app launcher with category buttons built in** (Noctalia and DankMaterialShell). If one of them becomes the top bar, the Walker recipe is not needed.

**F-4, top-bar candidates:** seven are worth a VM try. HyprPanel is **out**: its GitHub repository is archived (read-only), confirmed today.

| # | Candidate | Kind | Open-app icons | Tray | Drop-down: sound / network / Bluetooth | App menu with categories | Notifications | Display settings | Package (repo) · version |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Waybar, configured richer** | Bar only | Yes (`wlr/taskbar`) | Yes | **No.** Clicks open other apps; only a simple click-menu | No (opens Walker) | No (mako stays) | No | `waybar` (extra) 0.15.0 · `waybar-git` (chaotic-aur) |
| 2 | **nwg-panel** | Bar + small panels | Yes (`hyprland-taskbar`) | Yes | **Sound yes** (volume, output switch, per-app volume). Network and Bluetooth: status and launch buttons only | **Yes** (its "Menu Start" button opens nwg-menu) | No (mako stays) | No (it uses nwg-displays, which Javier rejected) | `nwg-panel` (extra) 0.12.0 |
| 3 | **ironbar** | Bar + popups | Yes (`launcher`, Windows-style) | Yes | **Sound yes** (mixer, default device), **Bluetooth yes** (device list, connect). Network: status only | **Yes** (`menu` module: click a category, see its apps) | Only as a button for SwayNC | No | `ironbar` (extra) 0.19.1 |
| 4 | **ashell** | Bar + quick-settings panel | **No** (active window title only) | Yes | **All three yes** (audio in/out, Wi-Fi with passwords, VPN, Bluetooth) | No launcher | Optional, can stay off | No | `ashell` (AUR) 0.10.0 |
| 5 | **Noctalia** | Full desktop shell | Yes (`taskbar` widget, pinning) | Yes | **All three yes** (Control Center tabs) | **Yes, built in** (category filter buttons) | Built in, **can be switched off** | Brightness only, no screen layout | `noctalia` (extra) 5.2.0 |
| 6 | **DankMaterialShell (DMS)** | Full desktop shell | Yes (`RunningApps`) | Yes | **All three yes** | **Yes, built in** | Built in, always on (mako must go) | **Yes**: screen layout editor, writes a Hyprland Lua file | `dms-shell` + `dms-shell-hyprland` (extra) 1.6.2 |
| 7 | **Caelestia** | Full desktop shell | **No** | Yes | **All three yes** (as settings pages and popouts) | No category view | Built in, always on (mako must go) | No | `caelestia-shell` (AUR) 2.5.0 |

**Does any of them replace the separate sound, network, Bluetooth and display apps?** Only **DankMaterialShell** covers all four, including a screen-layout editor. **Noctalia** and **ashell** cover sound, network and Bluetooth, but still need a display tool. The others still need separate apps.

**Suggested VM order** (most likely to satisfy Javier first): **Noctalia → DankMaterialShell → ironbar → nwg-panel → Waybar (richer) → ashell → Caelestia.** Details, risks and conflicts are in [Part B](#part-b--f-4-top-bar-candidates).

---

## Part A · F-6: App menu with categories

### A.1 · What Omarchy actually does (verified from source)

**Omarchy 4.0.4 (the version in our VM).** It no longer uses Walker. The 4.0 upgrade script removes it by name, together with the rest of the old stack:

> `"omarchy-walker walker elephant-all elephant elephant-bluetooth … elephant-websearch"`
> `"waybar playerctl"`
> — `bin/omarchy-upgrade-to-quattro`, basecamp/omarchy (MIT)

The key binding, at tag v4.0.4:

```lua
o.bind("SUPER + SPACE", "Omarchy menu", "omarchy-menu toggle")
o.bind("SUPER + ALT + SPACE", "Apps menu", "omarchy-menu toggle apps")
```
— `default/hypr/bindings/utilities.lua` @ v4.0.4, basecamp/omarchy (MIT)

The top level of that menu, which is what looked like "categories":

```jsonc
// Root Menu
"apps": {"icon":"󰀻","label":"Apps","aliases":["app","applications"],"provider":"apps"},
"learn": {"icon":"󰧑","label":"Learn"},
"trigger": {"icon":"󱓞","label":"Trigger"},
"style": {"icon":"","label":"Style"},
"setup": {"icon":"","label":"Setup","aliases":["settings"]},
"install": {"icon":"󰉉","label":"Install"},
"remove": {"icon":"󰭌","label":"Remove","aliases":["uninstall"]},
"update": {"icon":"","label":"Update","aliases":["restart","refresh"]},
"about": {"icon":"","label":"About","action":"omarchy-launch-about"},
"system": {"icon":"","label":"System","aliases":["power-menu"]},
```
— `default/omarchy/omarchy-menu.jsonc`, basecamp/omarchy (MIT)

And what "Apps" shows: every app in one list, kept in alphabetical order on purpose:

```qml
// DesktopEntries can reorder its values when an application starts.
// Keep the Apps menu alphabetical independently of provider refreshes.
```
— `shell/plugins/menu/Menu.qml`, basecamp/omarchy (MIT)

**Omarchy 3.8.4 (the last Walker version).** Same idea, drawn with Walker. The menu is a bash script that pipes lines of text into Walker's "dmenu" mode (a mode where Walker simply shows the lines it is given and prints the one you pick):

```bash
show_main_menu() {
  go_to_menu "$(menu "Go" "󰀻  Apps\n󰧑  Learn\n󱓞  Trigger\n  Style\n  Setup\n󰉉  Install\n󰭌  Remove\n  Update\n  About\n  System")"
}
go_to_menu() {
  case "${1,,}" in
  *apps*) walker -p "Launch…" ;;
```
```bash
echo -e "$options" | omarchy-launch-walker --dmenu --width 295 --minheight 1 --maxheight 630 -p "$prompt…" "${args[@]}"
```
— `bin/omarchy-menu` @ v3.8.4, basecamp/omarchy (MIT)

Omarchy 3's Walker settings had no category feature either. The app list was the plain `desktopapplications` source, with prefixes for the other sources:

```toml
[providers]
max_results = 256
default = ["desktopapplications", "websearch"]

[[providers.prefixes]]
prefix = "/"
provider = "providerlist"
# … "." files, ":" symbols, "=" calc, "@" websearch, "$" clipboard
```
— `config/walker/config.toml` @ v3.8.4, basecamp/omarchy (MIT)

Omarchy 3 did use elephant's **Lua menus**, but only for picture pickers (themes, wallpapers). They lived in `default/elephant/*.lua` and were linked into `~/.config/elephant/menus/`, then opened with `walker -m menus:omarchythemes`. That is the same mechanism our recipe uses. **[verified]**

### A.2 · What elephant and Walker can do (verified from source)

Versions read: **Walker 2.17.1** (`Cargo.toml`), **elephant** at commit `a35b3b5` (2026-09-29), both matching the packages we use.

1. **Menus are files in `menus/` folders**, written in TOML (a plain settings format) or Lua. elephant looks in `~/.config/elephant/menus/`, **and also in `/etc/xdg/elephant/menus/`**, so hypeForge can ship them system-wide with no per-user copy. It searches **every subfolder**, so every `.lua` file under `menus/` is loaded as a menu. A shared helper file must therefore live *outside* that folder. *(`pkg/common/files.go` `ConfigDirs`, `pkg/common/menucfg.go` uses `fastwalk.Walk`.)*
2. **An entry opens another menu** with `submenu = "<menu name>"` in TOML, or `SubMenu = "…"` in Lua. Walker then switches to showing that menu. *(elephant `internal/providers/menus/setup.go`: `if submenu != "" && action == "menus:open"`; Walker `src/data.rs` `listen_menus_loop` calls `set_provider(resp.value)`.)*
3. **A "back" step exists.** A menu with `Parent = "<menu name>"` gets a back action, and Walker binds it to **Escape** by default: `{ action = "menus:parent", label = "back", bind = "Escape" }`. *(Walker `resources/config.toml`, elephant `State()`.)*
4. **Lua menus are dynamic.** elephant calls the menu's `GetEntries()` function. Each entry can carry `Text`, `Subtext`, `Icon`, `Value`, `Keywords`, `Actions` and `SubMenu`. The menu-level settings `Name`, `NamePretty`, `Icon`, `Action`, `Parent`, `FixedOrder`, `HideFromProviderlist`, `Cache` and `RefreshOnChange` are all read from Lua. **`RefreshOnChange`** (a list of folders) caches the list and rebuilds it when those folders change, for example when an app is installed. A menu-wide `Action` may contain `%VALUE%`, which is replaced by the chosen entry's `Value`. Omarchy's own Lua menus prove that `io.open` and `io.popen` (reading files, running a command) work inside elephant. *(`pkg/common/menucfg.go`, `internal/providers/menus/setup.go`, Omarchy 3 `omarchy_themes.lua`.)*
5. **elephant's app source ignores categories for filtering.** It reads the `Categories=` line (`parser.go`), but nothing else in the provider uses it. **There is no setting to show apps by category.** A Lua menu that reads the app files itself is the only way. **[verified: the only uses of `Categories` are in the parser]**
6. **Walker decides what to show when the search box is empty.** `providers.empty` is used when the box is empty, and `providers.default` as soon as you type. Named **sets** (`[providers.sets.<name>]` with both `default` and `empty`, picked with `walker -s <name>`) do the same for one launch only, and the set is cleared when Walker closes. *(`src/data.rs`, `src/config.rs` `ProviderSet`, `src/ui/window.rs`.)*
7. **Walker's settings file only needs the lines you change.** Walker loads its built-in defaults, then merges the first `walker/config.toml` it finds: the user's own first, then `/etc/xdg/walker/`. *(`src/config.rs` `Walker::new`.)*

### A.3 · The recipe (copyable)

**What the user gets:** tap Win and Walker opens showing nine categories. Click one (or press Enter) to see its apps, alphabetical, with icons. Escape goes back. Typing on the first screen searches **all** apps, exactly like today.

Package needed: `elephant-menus` (the menus source; the task says it is already in our list). Launch uses `uwsm app -- <app>.desktop`, which matches our rule that apps are started through uwsm (the program that starts and supervises the Hyprland session).

#### File 1 · the shared helper, NOT inside a `menus/` folder

`/usr/share/hypeforge/elephant/appcats.lua`

```lua
-- hypeForge: shared helper for the category menus. Not a menu itself.
-- Reads every app's .desktop file and returns the ones whose Categories=
-- line contains one of the wanted categories.
local M = {}

local function split(s, sep)
  local out = {}
  if not s then return out end
  for part in string.gmatch(s, "[^" .. sep .. "]+") do table.insert(out, part) end
  return out
end

local function appDirs()
  local home = os.getenv("HOME") or ""
  local dataHome = os.getenv("XDG_DATA_HOME") or (home .. "/.local/share")
  local dirs = { dataHome .. "/applications" }            -- the user's own first
  for d in string.gmatch(os.getenv("XDG_DATA_DIRS") or "/usr/local/share:/usr/share", "[^:]+") do
    table.insert(dirs, d .. "/applications")              -- includes flatpak exports when set
  end
  return dirs
end

local function readEntry(path)
  local f = io.open(path, "r")
  if not f then return nil end
  local e, main = {}, false
  for line in f:lines() do
    local section = line:match("^%[(.+)%]$")
    if section then
      main = (section == "Desktop Entry")
    elseif main then
      local k, v = line:match("^([%w%-]+)%s*=%s*(.*)$")  -- skips translated keys like Name[de]
      if k and e[k] == nil then e[k] = v end
    end
  end
  f:close()
  return e
end

local function visible(e)
  if e.Type ~= "Application" then return false end
  if e.NoDisplay == "true" or e.Hidden == "true" then return false end
  local desks = split(os.getenv("XDG_CURRENT_DESKTOP") or "Hyprland", ":")
  local function onDesk(list)
    for _, d in ipairs(split(list, ";")) do
      for _, cur in ipairs(desks) do if d == cur then return true end end
    end
    return false
  end
  if e.OnlyShowIn and not onDesk(e.OnlyShowIn) then return false end
  if e.NotShowIn and onDesk(e.NotShowIn) then return false end
  return true
end

function M.entries(wanted)
  local want = {}
  for _, c in ipairs(wanted) do want[c] = true end
  local seen, list = {}, {}
  for _, dir in ipairs(appDirs()) do
    local h = io.popen("find -L '" .. dir .. "' -maxdepth 1 -name '*.desktop' 2>/dev/null")
    if h then
      for path in h:lines() do
        local id = path:match("([^/]+)$")
        if id and not seen[id] then
          seen[id] = true                                 -- a user copy hides the system one
          local e = readEntry(path)
          if e and visible(e) then
            local hit = false
            for _, c in ipairs(split(e.Categories, ";")) do if want[c] then hit = true end end
            if hit then
              table.insert(list, {
                Text = e.Name or id,
                Subtext = e.GenericName or e.Comment or "",
                Icon = e.Icon or "application-x-executable",
                Value = id,
                Keywords = split(e.Keywords, ";"),
              })
            end
          end
        end
      end
      h:close()
    end
  end
  table.sort(list, function(a, b) return a.Text:lower() < b.Text:lower() end)
  return list
end

return M
```

#### File 2 · the first screen (the nine categories)

`/etc/xdg/elephant/menus/hf-appmenu.toml`

```toml
name = "hf-appmenu"
name_pretty = "Apps"
icon = "applications-all"
hide_from_providerlist = true
fixed_order = true

[[entries]]
text = "Internet"
icon = "applications-internet"
submenu = "hf-apps-internet"

[[entries]]
text = "Office"
icon = "applications-office"
submenu = "hf-apps-office"

[[entries]]
text = "Graphics"
icon = "applications-graphics"
submenu = "hf-apps-graphics"

[[entries]]
text = "Multimedia"
icon = "applications-multimedia"
submenu = "hf-apps-multimedia"

[[entries]]
text = "Games"
icon = "applications-games"
submenu = "hf-apps-games"

[[entries]]
text = "Development"
icon = "applications-development"
submenu = "hf-apps-development"

[[entries]]
text = "System"
icon = "applications-system"
submenu = "hf-apps-system"

[[entries]]
text = "Settings"
icon = "preferences-system"
submenu = "hf-apps-settings"

[[entries]]
text = "Utilities"
icon = "applications-utilities"
submenu = "hf-apps-utilities"
```

#### Files 3 to 11 · one small Lua menu per category

`/etc/xdg/elephant/menus/hf-apps-internet.lua` (the other eight are identical except for the four marked values):

```lua
Name = "hf-apps-internet"                 -- (1) must match the submenu name above
NamePretty = "Internet"                   -- (2)
Icon = "applications-internet"            -- (3)
Parent = "hf-appmenu"                     -- Escape goes back to the categories
HideFromProviderlist = true
FixedOrder = true                         -- keep the helper's alphabetical order
Action = "uwsm app -- %VALUE%"            -- %VALUE% becomes e.g. firefox.desktop
RefreshOnChange = { "/usr/share/applications",
                    (os.getenv("HOME") or "") .. "/.local/share/applications" }

local AC = dofile("/usr/share/hypeforge/elephant/appcats.lua")
function GetEntries()
  return AC.entries({ "Network" })        -- (4) the freedesktop category names to match
end
```

| File | `NamePretty` | `Icon` | Categories matched (4) |
|---|---|---|---|
| `hf-apps-internet.lua` | Internet | `applications-internet` | `Network` |
| `hf-apps-office.lua` | Office | `applications-office` | `Office` |
| `hf-apps-graphics.lua` | Graphics | `applications-graphics` | `Graphics` |
| `hf-apps-multimedia.lua` | Multimedia | `applications-multimedia` | `AudioVideo`, `Audio`, `Video` |
| `hf-apps-games.lua` | Games | `applications-games` | `Game` |
| `hf-apps-development.lua` | Development | `applications-development` | `Development` |
| `hf-apps-system.lua` | System | `applications-system` | `System` |
| `hf-apps-settings.lua` | Settings | `preferences-system` | `Settings` |
| `hf-apps-utilities.lua` | Utilities | `applications-utilities` | `Utility` |

These are the official freedesktop "main categories", the same list Plasma's menu and DankMaterialShell's launcher use. An app tagged with two of them (many settings tools say both `Settings` and `System`) appears in both lists, as it does in Plasma.

#### File 12 · Walker settings (only the changed lines)

`/etc/xdg/walker/config.toml`, or merged into hypeForge's existing Walker file:

```toml
[providers]
default = ["desktopapplications", "calc"]   # what typing searches (keep our current list here)
empty   = ["menus:hf-appmenu"]              # what an empty box shows: the categories
```

**Alternative, if the categories should appear only on the Win key** and not every time Walker opens:

```toml
[providers.sets.hf-apps]
default = ["desktopapplications", "calc"]
empty   = ["menus:hf-appmenu"]
```
Then the Win binding runs `walker -s hf-apps` instead of `walker`.

#### After shipping

elephant reads menus when it starts, so restart it once: `systemctl --user restart elephant` (or however hypeForge starts it).

### A.4 · What is verified and what is not

| Claim | Status |
|---|---|
| Omarchy 3 and 4 show action groups, and "Apps" is a flat list | **Verified** (source at v3.8.4, v4.0.4 and master) |
| elephant menus support submenus, Parent/back, Lua `GetEntries`, `RefreshOnChange`, `%VALUE%`, `/etc/xdg` location | **Verified** (source) |
| Every `.lua` under `menus/` is loaded as a menu, so the helper must live elsewhere | **Verified** (source) |
| No built-in way to filter apps by category in elephant or Walker | **Verified** (source) |
| `providers.empty = ["menus:…"]` shows a menu on the empty screen | **Inferred.** The code path is the same one `-m menus:…` uses, which Omarchy 3 relied on. Test in the VM. |
| `dofile()` works inside elephant's Lua (gopher-lua) | **Inferred.** It is part of gopher-lua's standard library, but no Omarchy file uses it. **Fallback:** paste the helper into each of the nine files. |
| `uwsm app -- name.desktop` starts terminal apps (`Terminal=true`) correctly | **Inferred** from uwsm's documented desktop-entry launching. Test with one terminal app. |
| **Limitation:** after pressing Escape back to the categories, typing searches only the category names, not all apps | **Inferred** from Walker's code: going back switches to the menu *exclusively*. Closing and reopening Walker restores full search. Confirm in the VM. |
| Empty categories (for example Games with no games) still show and open an empty list | **Inferred.** A Lua root menu could hide them later if Javier minds. |

### A.5 · Risk

- **elephant development is on hold** (README notice added 2026-09-29). The packages still work, but fixes may stop. Walker itself was last changed 2026-09-25.
- Omarchy, which made Walker popular, dropped it in 4.0.
- Worth weighing: if Part B picks **Noctalia** or **DankMaterialShell**, their launchers already filter apps by category, and Walker could leave altogether. Clipboard history would then come from the shell too, since both have one.
- *Note for the caller:* TODO.md's F-6 line says the launcher is now hyprlauncher (D-39), while this task says Walker 2.17.1 is in use. The recipe above assumes Walker stays.

---

## Part B · F-4: Top-bar candidates

### B.1 · Facts table (checked 2026-09-30)

| Candidate | Repo · package · version | Upstream: stars · last push · latest release | Licence | Hyprland Lua dispatch (clicks that switch workspace or focus a window) |
|---|---|---|---|---|
| Waybar | extra `waybar` 0.15.0-3 · chaotic-aur `waybar-git` 0.15.0.r1026 | 12,007 · 2026-09-24 · 0.15.0 (2026-02-06) | MIT | **Broken in 0.15.0** ([#5294](https://github.com/Alexays/Waybar/issues/5294)); fixed on `-git` (D-17). Verified: the 0.15.0 source has no Lua code; current source does. |
| nwg-panel | extra `nwg-panel` 0.12.0-1 | 783 · 2026-09-29 · v0.12.0 (2026-09-29) | MIT | **Handled**: probes `hyprctl dispatch hl.dsp.no_op` and switches to Lua commands (`tools.py`). |
| ironbar | extra `ironbar` 0.19.1-1 | 1,475 · 2026-09-28 · v0.19.1 (2026-09-20) | MIT | **Handled in 0.19.1**: "hyprland: switch workspaces on Lua config providers" (#1554). |
| ashell | AUR `ashell` 0.10.0-1 (19 votes) | 1,127 · 2026-09-30 · 0.10.0 (2026-09-01) | GPL-3.0 | **Handled since 0.9.0**: "support Lua dispatch protocol on 0.55+ with Lua config" (#757). |
| Noctalia | extra `noctalia` 5.2.0-1 | 10,981 · 2026-09-29 · v5.2.0 (2026-09-27) | MIT | **Handled**: `configIsLua()` in its Hyprland code; **its Hyprland docs are written for `hyprland.lua`**. |
| DankMaterialShell | extra `dms-shell` + `dms-shell-hyprland` 1.6.2-1 | 8,278 · 2026-09-30 · v1.6.2 (2026-09-17) | MIT | **Handled at v1.6.2**: sends `hl.dsp.…` commands when Lua is active (checked in the tagged file). |
| Caelestia | AUR `caelestia-shell` 2.5.0-1 (9 votes) | 12,623 · 2026-09-27 · v2.5.0 (2026-09-18) | GPL-3.0 | **Handled at v2.5.0**: `usingLua ? hl.dsp.focus(…) : workspace …` (checked in the tagged file). |
| ~~HyprPanel~~ | AUR `ags-hyprpanel-git` (last update 2025-07-03) | 2,186 · **archived** · none | MIT | **Retired: confirmed.** GitHub shows `archived: true`. The unrelated `pdf/hyprpanel` is archived too. |

Noctalia 5 is **no longer a Quickshell program**. It is now a native program (its package depends on cairo, pipewire, wayland and similar, not on `quickshell`). DMS and Caelestia still run on Quickshell. Omarchy 4's own shell is MIT and well made, but it is tied to Omarchy's own scripts, so it is not a practical candidate. It is useful as a reference.

### B.2 · Each candidate in plain words

#### 1 · Waybar, configured richer (our current bar)
- **Gives:** open-app icons (`wlr/taskbar`, click to focus), tray, workspaces, sound and network icons with tooltips. **Group drawers**, which slide extra icons out on hover. A simple **click menu** (`menu` property: a pop-up list of commands). Sound and brightness **sliders inside the bar** (`pulseaudio-slider`, `backlight-slider`).
- **Does not give:** real drop-down panels. A click can only run another program (for example `pavucontrol`, `nm-connection-editor`, `blueman-manager`). No launcher, no notifications, no settings.
- **Started by:** `waybar.service` (ships with it), or `uwsm app -- waybar`.
- **Colours:** a CSS file (the same style language web pages use). `@import` of a generated `colors.css` works (its own manual shows `@import`).
- **Conflicts:** none. It lives happily with mako, hyprlock, hypridle and Walker.
- **Catch:** we must stay on `waybar-git` until a release after 0.15.0 (D-17). Earlier (D-34) Javier turned the taskbar off; F-4 reopens it.

#### 2 · nwg-panel
- **Gives:** open-app icons (`hyprland-taskbar`), tray, workspaces, clock with calendar, playerctl. A **Controls drop-down** with a volume slider, **output switcher** (choose speakers or headphones), **per-app volume**, brightness, battery, plus your own buttons (for example "Wi-Fi…" opening `nm-connection-editor`, "Bluetooth…" opening `blueman-manager`). A **"Menu Start" button** that opens **nwg-menu**, a classic app menu **with categories** (`nwg-menu` 0.1.9 in extra). It has **its own graphical settings app** (`nwg-panel-config`), no text editing needed.
- **Does not give:** built-in Wi-Fi or Bluetooth lists (current source only has brightness, battery, volume, readme and processes as built-in controls). No notifications. Display settings rely on nwg-displays, which Javier rejected.
- **Started by:** `nwg-panel.service` (in its repo), or `uwsm app -- nwg-panel`.
- **Colours:** a GTK CSS file per panel. A generated colours file can be `@import`ed. **[inferred]**
- **Conflicts:** none. It can show a SwayNC button, but mako is fine.
- **Why try it:** closest to Plasma's "taskbar + start menu with categories" in one package, from the official repo. It would also solve F-6 without Walker.

#### 3 · ironbar
- **Gives:** a **Windows-style taskbar** (`launcher` module: running apps grouped by program, hover shows each window, pinned favourites). Tray. A **Volume** popup (device volume, **default playback device**, per-app volume). A **Bluetooth** popup (device list, connect and disconnect). A **Menu** module: *"Clicking on any application category will open a sub-menu with any installed applications that match."* Clipboard, music, battery.
- **Does not give:** Wi-Fi choosing (the `network_manager` module only *shows* the state). Its notification button needs SwayNC, not mako. No display settings.
- **Started by:** `ironbar.service` (in its repo), or `uwsm app -- ironbar`.
- **Colours:** a GTK4 CSS file, reloaded live. Settings in TOML, JSON, YAML or Corn.
- **Conflicts:** none with our stack (it just skips the notifications module).
- **Why try it:** taskbar + category app menu + sound and Bluetooth drop-downs, all in `extra`, all Rust, small.

#### 4 · ashell
- **Gives:** a **settings panel** that drops down from the bar: audio outputs and inputs (with microphone), brightness, **Wi-Fi scan and password entry**, VPN, **Bluetooth**, power profiles, airplane mode, power menu. Tray, media player, privacy dots, system info, an OS-updates indicator, an on-screen display for volume and brightness.
- **Does not give:** open-app icons (only the active window's title). No launcher. No display settings.
- **Started by:** no service file ships. `uwsm app -- ashell`, or a small user unit hypeForge writes.
- **Colours:** set inside its one TOML config (colours, opacity, fonts). hypeForge would generate that section. It reloads on change.
- **Conflicts:** its notifications module is **optional**. When on, it takes over from mako ("mako … cannot run alongside ashell while this module is enabled"). Keep it off and mako stays.
- **Why try it:** the tidiest "drop-down for sound, network and Bluetooth". Fails the open-apps wish.

#### 5 · Noctalia (full desktop shell)
- **Gives:** bar with **taskbar** (open apps, pinning, middle-click to close), tray, workspaces. A **Control Center** with tabs for **Audio** (devices, streams), **Network** (Wi-Fi, NetworkManager actions), **Bluetooth** (pairing, connect), Notifications, Media, Power, Calendar, Weather. A **launcher with category filter buttons** ("Applications can be filtered by desktop-entry categories such as Internet, Development, Games, Office, System, and Utilities"). A **graphical Settings window**. Notifications, on-screen display, dock, clipboard, lock screen and idle options, wallpaper, desktop widgets.
- **Does not give:** screen layout or resolution settings (the Monitor tab is brightness only).
- **Started by:** the `noctalia` command. Its docs show `hl.exec_cmd("noctalia")` in `hyprland.lua`; for us, `uwsm app -- noctalia` or a user unit.
- **Colours:** a **custom palette JSON file** (`palettes/` in its config folder, 16 named colours) plus a TOML config. hypeForge can generate both. It can also push colours to GTK, Qt, KDE and Firefox through templates.
- **Conflicts, all switchable:** `enable_daemon = false` leaves notifications to mako. Idle actions are **off by default** (hypridle stays). The polkit agent is **off by default** (`polkit_agent = false`, so hyprpolkitagent stays). Its wallpaper has `[wallpaper] enabled`, which interacts with hyprpaper. Its launcher duplicates Walker.
- **Why try it:** meets nearly every wish (taskbar, drop-downs, categories, graphical settings), in `extra`, MIT, Lua-first docs. Its size is the trade-off: it is a whole desktop layer, not just a bar.

#### 6 · DankMaterialShell, "DMS" (full desktop shell)
- **Gives:** bar with **Running Apps**, tray, workspaces, clock, media, system monitors. A **Control Center**. **Settings tabs for Audio, Wi-Fi, Ethernet, VPN, Bluetooth, Keyboard, Mouse and Touchpad, Default Apps, Lock Screen, Notifications**, and a **Display Config tab with a monitor canvas** (drag screens, pick modes). On Hyprland with Lua it writes `~/.config/hypr/dms/outputs.lua`, which `hyprland.lua` must `require`. A **launcher with app categories** (its code maps `Categories=` to Internet, Office, Games and so on). Notifications, on-screen display, lock screen, dock, clipboard, a notepad, plugins.
- **Started by:** `dms.service` (`ExecStart=/usr/bin/dms run --session`, tied to the graphical session, which suits uwsm).
- **Colours:** Material-style themes, generated from the wallpaper (matugen) or from a custom theme file. **[inferred for the file route]**
- **Conflicts:** **its notification server is always on** (no switch found in the code), so **mako must go**. Its own lock and idle overlap hyprlock and hypridle and need care. Its `dms setup` tool writes Hyprland config fragments. **hypeForge must never run it**, because hypeForge owns `hyprland.lua`.
- **Why try it:** the only candidate that also replaces the **display** app. Javier called nwg-displays "a horrible piece of software", so this matters. Newest package in `extra`, very active.

#### 7 · Caelestia (full desktop shell)
- **Gives:** a stylish morphing bar with workspaces, active window, tray and status icons. A dashboard, a sidebar with notifications, a launcher, and a settings window ("Nexus") with **Audio, Network, Bluetooth**, Apps, Wallpaper and Style pages. Lock screen and idle monitors.
- **Does not give:** open-app icons (its "taskbar" setting is just its name for the bar). No category view in the launcher. No display settings.
- **Started by:** `caelestia shell -d`.
- **Colours:** its own colour schemes via the `caelestia` command, usually from the wallpaper. **[inferred]**
- **Conflicts:** notification server always on (mako must go). Its own idle monitors overlap hypridle. **Heavy AUR dependency chain:** `quickshell-git`, `qt6-m3shapes-git`, `caelestia-cli`, and it even pulls in `fish`. Built for its author's own dotfiles.
- **Why last:** it fails two of Javier's wishes (open apps, categories) and would stretch nog's AUR path the most.

### B.3 · Who replaces which separate app

| | Sound (device switch) | Network (Wi-Fi join) | Bluetooth (pair) | Display (layout, resolution) |
|---|---|---|---|---|
| Waybar | ✗ opens an app | ✗ opens an app | ✗ opens an app | ✗ |
| nwg-panel | ✓ | ✗ opens an app | ✗ opens an app | ✗ (nwg-displays) |
| ironbar | ✓ | ✗ status only | ✓ | ✗ |
| ashell | ✓ | ✓ | ✓ | ✗ |
| Noctalia | ✓ | ✓ | ✓ | ✗ brightness only |
| DankMaterialShell | ✓ | ✓ | ✓ | **✓** |
| Caelestia | ✓ | ✓ | ✓ | ✗ |

### B.4 · VM test plan, one at a time

For each candidate, in a fresh snapshot of the hypeForge VM:
1. Install through **nog** (all but ashell and Caelestia are in `extra`; those two are AUR, and each is a nog AUR-path test).
2. Stop Waybar, start the candidate the way the table says.
3. Check, in order: clicking a workspace **switches** (the Lua test); open-app icons appear and click to focus; tray icons; sound drop-down switches output; Wi-Fi join; Bluetooth pair; app menu categories; mako still shows a `notify-send hello`, or the shell's own does; Win + L still locks with hyprlock.
4. Note every gap as a finding; roll back the snapshot.

---

## Commands run (all read-only)

- `git clone --depth 1` into the session scratch folder: `basecamp/omarchy` (master `8b4eae6`, 2026-09-29), `basecamp/omarchy` at tag `v3.8.4`, `abenz1267/elephant` (`a35b3b5`), `abenz1267/walker` (`d885437`, v2.17.1), `Alexays/Waybar`, `nwg-piotr/nwg-panel`, `JakeStanger/ironbar`, `MalpenZibo/ashell`, `noctalia-dev/noctalia`, `AvengeMedia/DankMaterialShell`, `caelestia-dots/shell`. Then `grep`, `sed` and `ls` inside them.
- `curl` of raw files at tags: Omarchy `v4.0.4` (`utilities.lua`, `omarchy-menu.jsonc`), DMS `v1.6.2` `HyprlandService.qml`, Caelestia `v2.5.0` `services/Hypr.qml`, Waybar `0.15.0` `backend.cpp`.
- `pacman -Si` for waybar, waybar-git, nwg-panel, nwg-menu, nwg-look, ironbar, noctalia, dms-shell, dms-shell-hyprland, quickshell, swaync, nwg-drawer; `pacman -Ss noctalia`, `pacman -Ss dms-shell`; `pacman -Q` (Hyprland, Walker and Waybar are not installed on this desktop, as expected).
- AUR RPC `info` and `search` for ashell, caelestia-shell(-git), hyprpanel, ags-hyprpanel-git, ironbar-git, walker-bin, elephant-bin, elephant-menus-bin, waybar-git, nwg-panel-git, noctalia*, dms*.
- GitHub API (`/repos/…` and `/releases/latest`) for all candidates, HyprPanel, pdf/hyprpanel, Quickshell, nwg-drawer, elephant, walker; Waybar issue #5294.

## Sources

- Omarchy (MIT): <https://github.com/basecamp/omarchy>: `default/omarchy/omarchy-menu.jsonc`, `default/hypr/bindings/utilities.lua`, `shell/plugins/menu/Menu.qml`, `bin/omarchy-upgrade-to-quattro`; at v3.8.4 `bin/omarchy-menu`, `bin/omarchy-launch-walker`, `config/walker/config.toml`, `default/elephant/omarchy_themes.lua`, `install/config/walker-elephant.sh`.
- elephant: <https://github.com/abenz1267/elephant>: `README.md` (on-hold notice), `internal/providers/menus/README.md`, `internal/providers/menus/setup.go`, `pkg/common/menucfg.go`, `pkg/common/files.go`, `internal/providers/desktopapplications/parser.go`.
- Walker: <https://github.com/abenz1267/walker>: `resources/config.toml`, `src/config.rs`, `src/data.rs`, `src/main.rs`, `src/ui/window.rs`.
- Waybar: <https://github.com/Alexays/Waybar>: `man/waybar-wlr-taskbar.5.scd`, `man/waybar-menu.5.scd`, `man/waybar.5.scd.in` (group drawers), issue #5294.
- nwg-panel: <https://github.com/nwg-piotr/nwg-panel>: `README.md`, `nwg_panel/modules/controls.py`, `menu_start.py`, `tools.py`; v0.12.0 release notes.
- ironbar: <https://github.com/JakeStanger/ironbar>: `docs/modules/Launcher.md`, `Menu.md`, `Volume.md`, `Bluetooth.md`, `Network-Manager.md`, `Notifications.md`, `CHANGELOG.md`.
- ashell: <https://github.com/MalpenZibo/ashell>: `README.md`, `website/docs/configuration/modules/notifications.md`, `CHANGELOG.md`, `src/services/compositor/hyprland.rs`.
- Noctalia: <https://github.com/noctalia-dev/noctalia>: `docs/user/launcher/index.mdx`, `control-center/index.mdx`, `bar/widgets/taskbar.mdx`, `compositor-settings/hyprland.mdx`, `services/notifications.mdx`, `services/idle.mdx`, `configuration/shell.mdx`, `theming/palette.mdx`.
- DankMaterialShell: <https://github.com/AvengeMedia/DankMaterialShell>: `quickshell/Services/HyprlandService.qml`, `AppSearchService.qml`, `NotificationService.qml`, `Modules/Settings/*`, `core/internal/config/deployer.go`, `assets/systemd/dms.service`.
- Caelestia: <https://github.com/caelestia-dots/shell>: `README.md`, `services/Hypr.qml`, `services/Notifs.qml`, `modules/bar/Bar.qml`, `modules/nexus/pages/`.
- HyprPanel: <https://github.com/Jas-SinghFSU/HyprPanel> (archived).
