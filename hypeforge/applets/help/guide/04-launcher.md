# App Sections — the launcher (applet 4)

**What it does:** **Win + Space**, or a click on the **KognogOS emblem** at the left of the bar,
opens the launcher, right under the emblem; press again to close it. Its first screen lists **Favorites**,
the **groups** every desktop uses — Development, Games, Graphics, Internet, Multimedia, Office, Settings,
System, Utilities (and Education, Science or Other once something belongs there) — then **All apps**
and **Help & Keys** — apps only. Lock, log out,
reboot and shut down are on the bar's **⏻** button.

## How to use it

- **Type** to search every app straight away, then **Enter**.
- **Pick a group** to see its apps. Every app is in the group it says it belongs to (its own
  launcher entry carries that), so a new app you install shows up where you'd look for it.
- **Where it opens:** on its own workspace, **however you pick it** — from its group, by typing its
  name, from Favorites or All apps. Each workspace lists its apps (see Workspaces, page 2): Steam
  and the games on Gaming, Chrome on Daily, the system monitors on Monitoring… The screens switch
  there first, then the app opens. An app on no list opens on the screen you are on. Window
  placement then puts it in its spot.
- **Settings** starts with **hypeForge Settings**, the control centre, then every setting:
  displayForge, nogForge, grubForge, alacrittyForge, printers, network, and the rest.
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
- one `[[section]]` per group: `name`, `icon`, `workspace`, `categories` (the standard kinds it
  holds), `apps` (only for apps that declare no kind); `other = true` marks the catch-all
- `claim_order` — when an app says several kinds, the first group here wins (Settings over System,
  Games over Internet)
- `[workspaces]` — an app's own workspace, over its group's
- `[power]` — what the bar's ⏻ menu runs for Lock, Log Out, Reboot and Shut Down

The launcher's look (colours, size, corners): `~/.config/sway/fuzzel/fuzzel.ini`.
