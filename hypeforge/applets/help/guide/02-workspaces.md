# Workspaces Management (applet 1)

**What it does:** gives you six workspaces — **1 Daily · 2 Work · 3 Entertainment · 4 Gaming ·
5 Monitoring · 6 Settings** — that cover **all your screens at once**. Switching workspace
switches every screen together, so each workspace is a whole desk of its own.

## How to use it

- **Win + 1 … 6** switches every screen at once.
- **The workspace button** on the bar (for example **1. Daily ▾**) shows where you are.
  **Click it, or press Win + Tab**, and the list drops down: pick one and every screen
  switches. Press again (or **Esc**) to close it.
- **Win + Shift + 1 … 6**: send the window you are in to another workspace (it stays on the
  same screen).
- The mouse stays where it is when you switch.

## Sharing a screen (the matrix)

A screen can **share one space** between several workspaces: its apps then stay put while the
other screens change. Example: keep your main apps on the middle screen in Daily, Work and
Entertainment. Sharing works down one screen (the same screen across workspaces), never across
screens — a window can only be in one place.

## Settings

`~/.config/hypeforge/applets/workspaces.toml`

- `enabled = true / false` — switch the applet on or off
- `screens` — the screens in order (screen 1 is the main one)
- one `[[workspace]]` block per workspace (up to 9): add, rename, reorder or delete
- `[share]` — which workspaces share a space on each screen

After editing by hand: `hypeforge-workspaces reload`.
