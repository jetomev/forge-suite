# App Sections — the launcher (applet 4)

**What it does:** **Win + Space**, or a click on the **KognogOS emblem** at the left of the bar,
opens the launcher; press again to close it. Its first screen lists **Favorites**, your
workspaces as **sections**, then **All apps**, then **Lock Screen · Log Out · Reboot ·
Shutdown**.

## How to use it

- **Type** to search every app straight away, then **Enter**.
- **Pick a section** (for example *2. Work*) to see its apps. An app picked there opens **in
  that workspace**, and window placement puts it in its spot.
- **All apps** lists everything. **Back** returns to the first screen; **Esc** closes.
- Log Out, Reboot and Shutdown ask first, with **No** selected.
- **Win + D** is the plain search, without sections.

## Favorites on the bar

**Favorites ▾** on the top bar (right of the workspace button) drops down the same apps, each
with its icon: **click one** to open it; click the button again (or **Esc**) to close the list.
The list follows the `favourites` setting below — after changing it by hand, run
`hypeforge-sections bar` (it also runs at every login).

## Settings

`~/.config/hypeforge/applets/sections.toml`

- `enabled = true / false` (off: Win + Space is the plain search)
- `favourites` — your apps at the top, in your order

The emblem's picture: `~/.config/hypeforge/bar/launcher.png` — put any picture there to change it.
- one `[[section]]` per section: `name`, `icon`, `workspace`, `apps`, `categories`
- `[power]` — what Lock Screen, Log Out, Reboot and Shutdown run

The launcher's look (colours, size, corners): `~/.config/sway/fuzzel/fuzzel.ini`.
