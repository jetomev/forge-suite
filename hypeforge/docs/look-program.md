# hypeForge — the look program (2026-10-10 →)

**Javier, 2026-10-10:** *"Where a beautifully stylised Windows 11 desktop exists, what classic Mac OS 9 functionality offered, and KognogOS identity meets."* Six styles, each with 23 colour themes and five wallpapers per colour, all still **tiling** with our workspaces, placement and snapping; the Forge Suite's terminal apps keep their philosophy and are not restyled (yet). Everything structured and documented so a later theme app (forgekit / Forge Suite / hypeForge Settings) can drive it.

Claude is the graphic design, UI/usability and development team and the critical eye; up to five helpers do research. Every visual step is **proposed, reviewed and approved** by Javier before it is built (Phase 12 rule).

## What Javier asked for

- **Styles (6), one by one, reviewed little by little:** 1 Windows 11 · 2 Mac OS 9.x · 3 modern macOS · 4 a modern Linux rice · 5 KDE · 6 COSMIC.
- **What he loves:** Windows 11's graphics (the bar, the tray, the windows), a launcher more KDE than Windows, and Mac OS 9's bar style above Windows 11's bar location.
- **Shape:** border rounding, shades, shadows, window borders.
- **Colour (23 themes):** White · Light Gray · Gray · Dark Gray · Black · Dark Blue · Blue · Light Blue · Light Purple · Purple (the Kognog colours) · Dark Purple · Light Green · Green · Dark Green · Light Pink · Pink · Dark Pink · Light Red · Red · Dark Red · Light Multicolor · Multicolor · Dark Multicolor. *"Key in design: how to manage colour contrast to make things pop, and create themes."*
- **Wallpapers:** five per colour, not KognogOS-branded, in moods like cyberpunk, anime, nature, technology, buildings.
- **Limits:** inside what Sway and our apps can do; practical, not complicated to use.

## Phases and dates (estimates; the GitHub Project mirrors this as a timeline)

| # | Phase | From → to | Who | Ends with |
|---|---|---|---|---|
| 0 | Ship nightForge 1.0 | 10-10 | Claude, Javier (install test) | GitHub ✅ · AUR after the test · site · Vault |
| 1 | **Research** — compositor (Sway vs SwayFX), bars/trays/launchers/docks, theme system + colour science + 23 palettes, inventory of every themable piece, wallpapers | 10-10 | 5 helpers, Claude reviews | `docs/research/look-2026-10/01…05` |
| 2 ✅ approved (D-73) | **Foundation** — the theme file format (colours separate from shapes), the palette generator and its contrast report, the 23-theme swatch sheet, the wallpaper generator, the SwayFX decision (bench + a separate login session, Sway stays the default) | 10-10 → 10-11 | Claude | Javier reviews the swatches and the SwayFX question |
| 3.1 ✅ approved (D-71) | **Proposal 1 · Windows 11** — a live mock-up of the three screens (bar, tray, launcher, windows), the 23 themes switchable, its wallpapers | 10-11 → 10-12 | Claude | Javier's review (approve / change) |
| 3.2 ✅ approved (D-72) | Proposal 2 · Mac OS 9.x | 10-12 → 10-13 | Claude | review |
| 3.3 ✅ approved (D-74) | Proposal 3 · modern macOS | 10-13 → 10-14 | Claude | review |
| 3.4 ✅ approved (D-75) | Proposal 4 · a modern Linux rice | 10-14 → 10-15 | Claude | review |
| 3.5 ✅ drawn | Proposal 5 · KDE | 10-15 → 10-16 | Claude | review |
| 3.6 | Proposal 6 · COSMIC | 10-16 → 10-17 | Claude | review |
| 4 | **Build** the chosen style(s) as real configs + one `hypeforge-theme apply <style> <colour>` step; bench before live | after the reviews | Claude | Javier lives with it |
| 5 | **Document for the theme apps** — what forgekit, the Forge Suite and hypeForge Settings (a Look page) need | alongside | Claude | `docs/THEME.md`, the Settings catalogue |

Each proposal is published as a page Javier opens in his browser, with what is asked of him written on it. A proposal that needs SwayFX says so.

## How the work is shared

The GitHub Project **"hypeForge · the look"** (jetomev) holds every task above with dates (its Roadmap view is the gantt). Helpers take their task from it and Claude moves items to Done as they finish. Until the Project exists, this file is the plan.

## Decisions on the way

- **H-1 (Claude):** colours and shapes are separate files: a *theme* (23) is colours only; a *style* (6) is shapes, layout and which bar/launcher/dock. Any theme on any style.
- **H-2 (Claude):** mock-ups are HTML/CSS drawings of Javier's real layout (three screens, his bar, his apps), driven by the same tokens the configs will use, so what he approves is what gets built.
- **H-3 (Claude, to confirm with Javier):** wallpapers are made by our own generator (no licences to worry about); photos or illustrations (real anime art) only from sources whose licence allows shipping them.

## Research so far (2026-10-10)

- **01 · compositor** ✅ — SwayFX 0.6 is built on Sway 1.12 (ours); config and applets compatible. Its package replaces Sway, so side by side = our own build in `/opt/swayfx` + a second login "hypeForge FX". Animations stay off (workspaces can vanish moving between screens, #565 #569); shadows only after a 10-reload bench (#566). Plan: every style designed for plain Sway first, the eye candy in one optional `fx.conf`.
- **02 · bar, tray, launcher** ✅ — Waybar 0.15 can do all six styles (top/bottom, several bars, floating centred, drawers, real drop-down menus); one Waybar + a layout and shape file per style + the theme's colour tokens. Not possible on Sway: an app's own File/Edit menus in the top bar, the macOS dock's magnifying wave, minimize, a workspace overview. Our own graphical pop-ups (a KDE-style launcher, Quick Settings, calendar) need **zero new packages** (Python + GTK3 + layer-shell are installed).
- **03 · theme system + 23 palettes** ✅ — 69 colour roles, shapes in a separate `style.toml`; `palette/generate.py` (stdlib, own OKLCH maths) builds all 23: 1794 required contrast pairs, all pass (WCAG 2.2 + APCA). Dark Purple = today's Mocha look. The emblem is **blue #0363ef + orange #d9400e**; the Kognog purple is the OS accent #cba6f7. Every program can include a generated file (checked on the installed versions; Alacritty's live reload of an imported file still to bench).
  - **Critical eye (Claude):** the mid themes (Gray, Blue, Purple, Green, Pink, Red) sit near lightness 0.40, so they read close to their Dark sisters; contrast forces it ("the mid-gray dead zone": at 0.55–0.65 neither black nor white text reaches 7:1). Options for Javier: accept, or let mid themes use 4.5:1 body text and move up to ~0.50.
- **04 · inventory** ✅ — 21 places a theme writes; F-52 #59, F-53 #60 (fixed); what Settings needs for Look.
- **05 · wallpapers** ✅ — our own generator (`wallpapers/generate.py`, Python + Pillow + numpy, already installed): five moods (synthwave, skyline, mountains, circuit, sky-clouds as the anime-style stand-in), any palette, the same picture every time; light themes get calm "paper" versions. Licences read: Unsplash, Pexels and Wallhaven can't be shipped; Wikimedia Commons CC0/CC only, file by file, with credits. Ship the generator and make each wallpaper when a theme is picked (~6 s), or WebP (0.06–0.4 MB each).
  - **Critical eye (Claude):** synthwave, skyline, mountains and circuit look good; sky-clouds was the weak one (clouds low and clipped, dark blobs inside); redone the same day as three cumulus towers over a haze bank, flat cel shading, no blobs — still a little smooth.

## Javier's answers on review 1 (2026-10-10)

Q-1 A · Q-2 A · Q-3 B · Q-4 "middle to darker", with white, black and grays inside every colour theme so none is monotone, more colour combinations the way a graphic designer would, a black/white/dark-gray/orange theme, and "the Kognog colours" are KognogOS Mocha (Catppuccin Mocha), not purple · Q-5 my picks, following those notes. Recorded as D-68, D-69, D-70. Next: palettes v2 (60-30-10), then review 1 again with them. **Done 10-10:** palettes v2 — 25 themes (KognogOS Mocha the default, Ember new), neutral foundation + band + pop, 2,124 contrast pairs pass; review 1 round 2 (F-1…F-4) and both approved styles repainted with it.

## Questions for Javier (asked on the proposal pages, not before)

- **Answered (Javier, 10-10): White and Black are the high-contrast themes** — grayscale styling, not pure: grays only, a near-black / near-white gray accent, stronger text (primary ≥ 7:1 everywhere) and borders; colour only where it means something (status, urgent, the terminal). Done in `palette/generate.py` (`hc=True`).
- **Q-1 · SwayFX:** D-56 says KognogOS ships with Sway only. Does SwayFX (Sway with eye candy, as a second login) count as Sway? Needed for rounded corners, shadows, blur.
- **Q-2 · graphical pop-ups:** D-57 says terminal apps first. Are small graphical pop-ups from the bar (a KDE-style launcher, Quick Settings, a calendar) OK, while the Forge apps stay in the terminal?
- **Q-4 · palette choices:** neutral themes' accent — emblem blue (proposed) or Kognog mauve? Focused window border — the accent (proposed) or white like today? Urgent in red/pink themes — moved to amber/purple (proposed) or one fixed colour? The emblem orange — brand only (proposed) or an accent?
- **Q-3 · wallpapers:** our own generated pictures, or also licensed photos/illustrations?

## Review pages

- **Review 1 · the foundation** — https://claude.ai/artifact/HDF7uAsEJRkMCFaQzLcfLV (`docs/design/look/review-1/`, built by `build.py`): the 23 themes on a live desktop, the wallpapers, Q-1…Q-5. Waiting for Javier's answers.
- **Review 2 · Windows 11** — https://claude.ai/artifact/G4ij4oQ9AEV9n6xLTGT2xP (`docs/design/look/review-2-windows-11/`): bottom taskbar on every screen (centered or left), a KDE-style Start from `sections.toml`, Quick Settings (Wi-Fi, Bluetooth, Night light, Do Not Disturb, Screens, VPN), calendar + notifications, the tray drawer, a Workspaces panel; SwayFX vs plain Sway; W-1…W-5. **Approved 10-10: "A killer proposal. Sold!"** (D-71; W-1 left, W-2…W-5 yes; more contrast inside windows). Its style file: `docs/design/look/styles/windows-11/style.toml`.
- **Review 3 · Mac OS 9** — https://claude.ai/artifact/FRzPE4Y3L9NRpNLFPvQT5D (`docs/design/look/review-3-mac-os-9/`): the menu bar (emblem menu with group submenus · bold app name · Workspaces · Favorites · Window · Special · Help … clock · Application menu), real Sway title bars centred, the Control Strip bottom-left holding the tray and status icons, the crisp shadow on SwayFX; M-1…M-5. Style file `docs/design/look/styles/mac-os-9/style.toml`. Plain Sway draws all of it. **Approved 10-10** (D-72, M-1…M-5 as proposed).
- **Review 4 · modern macOS** — https://claude.ai/artifact/4EuUPYJJZ4Jc9uMJbFZR6w (`docs/design/look/review-4-macos/`): the frosted menu bar keeping Mac OS 9's menus, the Dock (a second Waybar, favourites + running + Downloads + Trash), Spotlight (fuzzel restyled), Launchpad (panel grid), Control Center (shared with Windows 11's Quick Settings), Notification Center; MA-1…MA-5 — **approved 10-10 as proposed (D-74)**. Style file `docs/design/look/styles/macos/style.toml`. Shared builds noted: one pinned+running Waybar part (taskbar and Dock), one panel code (Start/Launchpad, Quick Settings/Control Center, calendar/Notification Center).
- **Review 5 · the Linux rice** — https://claude.ai/artifact/R8dkyJeige2CoRnmDXqpmk (`docs/design/look/review-5-rice/`): three floating islands, numbered workspace pills (the active one named), see-through frosted terminals, a bright frame on the window in use, a big-button power menu, and **every theme with its own generated wallpaper** (`make-wallpapers.py`, 25 pictures, ~4 min); R-1…R-5 — **approved 10-10 (D-75)**: one floating island with three areas; the wallpaper follows the theme, for every theme. Style file `docs/design/look/styles/rice/style.toml`.
- **Review 6 · KDE Plasma** — https://claude.ai/artifact/EsB3L9NUNiUYfs7uAAxZUZ (`docs/design/look/review-6-kde/`): the floating panel (or attached), Kickoff as KDE's list with descriptions, the pager (six little screens), one tray pop-up with pages, KRunner from the top, Breeze-style title bars; no KDE software; K-1…K-5. Style file `docs/design/look/styles/kde/style.toml`.
