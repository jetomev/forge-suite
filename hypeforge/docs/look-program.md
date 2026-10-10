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
| 2 | **Foundation** — the theme file format (colours separate from shapes), the palette generator and its contrast report, the 23-theme swatch sheet, the wallpaper generator, the SwayFX decision (bench + a separate login session, Sway stays the default) | 10-10 → 10-11 | Claude | Javier reviews the swatches and the SwayFX question |
| 3.1 | **Proposal 1 · Windows 11** — a live mock-up of the three screens (bar, tray, launcher, windows), the 23 themes switchable, its wallpapers | 10-11 → 10-12 | Claude | Javier's review (approve / change) |
| 3.2 | Proposal 2 · Mac OS 9.x | 10-12 → 10-13 | Claude | review |
| 3.3 | Proposal 3 · modern macOS | 10-13 → 10-14 | Claude | review |
| 3.4 | Proposal 4 · a modern Linux rice | 10-14 → 10-15 | Claude | review |
| 3.5 | Proposal 5 · KDE | 10-15 → 10-16 | Claude | review |
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
- **03 · theme system + 23 palettes** — running.
- **04 · inventory** ✅ — 21 places a theme writes; F-52 #59, F-53 #60 (fixed); what Settings needs for Look.
- **05 · wallpapers** — running.

## Questions for Javier (asked on the proposal pages, not before)

- **Q-1 · SwayFX:** D-56 says KognogOS ships with Sway only. Does SwayFX (Sway with eye candy, as a second login) count as Sway? Needed for rounded corners, shadows, blur.
- **Q-2 · graphical pop-ups:** D-57 says terminal apps first. Are small graphical pop-ups from the bar (a KDE-style launcher, Quick Settings, a calendar) OK, while the Forge apps stay in the terminal?
- **Q-3 · wallpapers:** our own generated pictures, or also licensed photos/illustrations?
