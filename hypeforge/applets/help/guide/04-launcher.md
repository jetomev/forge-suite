# App Sections — the launcher (applet 4)

**What it does:** **Win + Space**, or a click on the **KognogOS emblem** at the left of the bar,
opens the launcher, right under the emblem; press again to close it. Its first screen lists **Favorites**,
your workspaces as **sections**, then **All apps** and **Help & Keys** — apps only. Lock, log out,
reboot and shut down are on the bar's **⏻** button.

## How to use it

- **Type** to search every app straight away, then **Enter**.
- **Pick a section** (for example *2. Work*) to see its apps. An app picked there opens **in
  that workspace**, and window placement puts it in its spot.
- **Settings** (*6. Settings*) starts with **hypeForge Settings**, the control centre, then our own
  apps: displayForge, nogForge, grubForge, alacrittyForge, bitlaForge and Help & Keys, then the
  other settings programs. Picked here, they open on the Settings workspace, floating, with a light
  border.
- **All apps** lists everything. **Back** returns to the first screen; **Esc** closes.
- **Win + D** is the plain search, without sections.

## Favorites on the bar

**Favorites** on the top bar (right of **Workspaces**) — or **Win + F** — drops down the same
apps, each with its icon: **click one** to open it; click the button again (or **Esc**) to close the list.
The list follows the `favourites` setting below — after changing it by hand, run
`hypeforge-sections bar` (it also runs at every login).

## Settings

`~/.config/hypeforge/applets/sections.toml`

- `enabled = true / false` (off: Win + Space is the plain search)
- `favourites` — your apps at the top, in your order

The emblem's picture: `~/.config/hypeforge/bar/launcher.png` — put any picture there to change it.
- one `[[section]]` per section: `name`, `icon`, `workspace`, `apps`, `categories`
- `[power]` — what the bar's ⏻ menu runs for Lock, Log Out, Reboot and Shut Down

The launcher's look (colours, size, corners): `~/.config/sway/fuzzel/fuzzel.ini`.
