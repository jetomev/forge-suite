# App Sections — the launcher (applet 4)

**What it does:** **Win + Space** opens the launcher. Its first screen lists your workspaces as
**sections**, then **All apps**, then **Lock Screen · Log Out · Reboot · Shutdown**.

## How to use it

- **Type** to search every app straight away, then **Enter**.
- **Pick a section** (for example *2. Work*) to see its apps. An app picked there opens **in
  that workspace**, and window placement puts it in its spot.
- **All apps** lists everything. **Back** returns to the first screen; **Esc** closes.
- Log Out, Reboot and Shutdown ask first, with **No** selected.
- **Win + D** is the plain search, without sections.

Apps you put in a section come first; every other app falls into a section by its own kind
(a game into Gaming, a settings tool into Settings…).

## Settings

`~/.config/hypeforge/applets/sections.toml`

- `enabled = true / false` (off: Win + Space is the plain search)
- `favourites` — apps pinned at the top
- one `[[section]]` per section: `name`, `icon`, `workspace`, `apps`, `categories`
- `[power]` — what Lock Screen, Log Out, Reboot and Shutdown run

The launcher's look (colours, size, corners): `~/.config/sway/fuzzel/fuzzel.ini`.
